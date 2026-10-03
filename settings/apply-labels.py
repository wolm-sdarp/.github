#!/usr/bin/env python3
"""Синхронизация меток репозиториев организации с settings/labels.yml.

По умолчанию ничего не меняет, а только показывает план (dry-run).

    python3 settings/apply-labels.py --check                 # проверить labels.yml, GitHub не нужен
    python3 settings/apply-labels.py                         # показать план для всех репозиториев
    python3 settings/apply-labels.py --repo book1            # план для одного репозитория
    python3 settings/apply-labels.py --apply                 # создать, обновить и переименовать метки
    python3 settings/apply-labels.py --apply --delete        # то же + удалить устаревшие метки

Требуется GitHub CLI (`gh`), выполненный `gh auth login` и право записи в репозитории.
Спецификация: documentation/content/gh-issues-docs.md.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HEX = re.compile(r"^[0-9a-fA-F]{6}$")


# --------------------------------------------------------------------------------------
# Чтение labels.yml (подмножество YAML; сторонние библиотеки не нужны)
# --------------------------------------------------------------------------------------
def _split_inline(s):
    items, buf, quote = [], "", None
    for ch in s:
        if quote:
            buf += ch
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf += ch
        elif ch == ",":
            items.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        items.append(buf.strip())
    return items


def _scalar(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    if s == "true":
        return True
    if s == "false":
        return False
    if s.startswith("[") and s.endswith("]"):
        return [_scalar(x) for x in _split_inline(s[1:-1])]
    return s


def _key_value(line, lineno):
    key, sep, value = line.partition(":")
    if not sep:
        raise ValueError(f"строка {lineno}: ожидалось «ключ: значение»")
    return key.strip(), value.strip()


def load_config(path):
    root, cur_key, cur_item = {}, None, None
    for lineno, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent == 0:
            key, value = _key_value(line, lineno)
            cur_key, cur_item = key, None
            root[key] = _scalar(value) if value else None
        elif cur_key is None:
            raise ValueError(f"строка {lineno}: значение вне ключа верхнего уровня")
        elif line.startswith("- "):
            if root[cur_key] is None:
                root[cur_key] = []
            if not isinstance(root[cur_key], list):
                raise ValueError(f"строка {lineno}: элемент списка внутри «{cur_key}», который не список")
            cur_item = {}
            root[cur_key].append(cur_item)
            key, value = _key_value(line[2:], lineno)
            cur_item[key] = _scalar(value)
        elif cur_item is not None and isinstance(root[cur_key], list):
            key, value = _key_value(line, lineno)
            cur_item[key] = _scalar(value)
        else:
            if root[cur_key] is None:
                root[cur_key] = {}
            key, value = _key_value(line, lineno)
            root[cur_key][key] = _scalar(value)
    return root


# --------------------------------------------------------------------------------------
# Проверка labels.yml
# --------------------------------------------------------------------------------------
def validate(cfg):
    errors = []
    if not isinstance(cfg.get("org"), str) or not cfg["org"]:
        errors.append("org: не задана организация")
    sets = cfg.get("repo_sets")
    if not isinstance(sets, dict) or not sets:
        errors.append("repo_sets: не задан")
        sets = {}
    seen_repo = {}
    for set_name, repos in sets.items():
        if not isinstance(repos, list):
            errors.append(f"repo_sets.{set_name}: должен быть списком")
            continue
        for repo in repos:
            if repo in seen_repo:
                errors.append(f"репозиторий {repo} входит в два набора: {seen_repo[repo]} и {set_name}")
            seen_repo[repo] = set_name

    names, alias_owner = {}, {}
    labels = cfg.get("labels")
    if not isinstance(labels, list) or not labels:
        errors.append("labels: пустой или не список")
        labels = []
    for i, lab in enumerate(labels, 1):
        where = f"labels[{i}] {lab.get('name', '?')}"
        name = lab.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"{where}: нет name")
            continue
        if len(name) > 50:
            errors.append(f"{where}: имя длиннее 50 символов")
        if name.lower() in names:
            errors.append(f"{where}: дубликат имени (без учёта регистра)")
        names[name.lower()] = name
        if not isinstance(lab.get("color"), str) or not HEX.match(lab["color"]):
            errors.append(f"{where}: color должен быть hex из 6 символов в кавычках")
        desc = lab.get("description")
        if not isinstance(desc, str) or not desc:
            errors.append(f"{where}: нет description")
        elif len(desc) > 100:
            errors.append(f"{where}: description длиннее 100 символов ({len(desc)})")
        lab_sets = lab.get("sets")
        if not isinstance(lab_sets, list) or not lab_sets:
            errors.append(f"{where}: sets должен быть непустым списком")
        else:
            for s in lab_sets:
                if s not in sets:
                    errors.append(f"{where}: неизвестный набор «{s}»")
        if not isinstance(lab.get("reserve"), bool):
            errors.append(f"{where}: reserve должен быть true или false")
        aliases = lab.get("aliases", [])
        if not isinstance(aliases, list):
            errors.append(f"{where}: aliases должен быть списком")
            aliases = []
        for a in aliases:
            alias_owner[a.lower()] = name
    for alias, owner in alias_owner.items():
        if alias in names:
            errors.append(f"алиас «{alias}» (для {owner}) совпадает с именем другой метки")
    for key in ("delete", "ignore"):
        lst = cfg.get(key, [])
        if not isinstance(lst, list):
            errors.append(f"{key}: должен быть списком")
            continue
        for n in lst:
            if n.lower() in names:
                errors.append(f"{key}: «{n}» одновременно описана в labels")
    return errors


# --------------------------------------------------------------------------------------
# Работа с GitHub CLI
# --------------------------------------------------------------------------------------
def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def repo_exists(full):
    return gh("repo", "view", full, "--json", "name").returncode == 0


def list_labels(full):
    r = gh("label", "list", "-R", full, "--limit", "1000", "--json", "name,color,description")
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "gh label list завершился с ошибкой")
    return json.loads(r.stdout or "[]")


def usage(full, name):
    """Сколько issues и PR ссылаются на метку; None, если посчитать не удалось."""
    total = 0
    for kind in ("issue", "pr"):
        r = gh(kind, "list", "-R", full, "--label", name, "--state", "all", "--limit", "1000", "--json", "number")
        if r.returncode != 0:
            return None
        total += len(json.loads(r.stdout or "[]"))
    return total


def confirm(question):
    if not sys.stdin.isatty():
        return False
    return input(f"{question} [y/N] ").strip().lower() in ("y", "yes", "д", "да")


# --------------------------------------------------------------------------------------
# Синхронизация одного репозитория
# --------------------------------------------------------------------------------------
class Stats:
    def __init__(self):
        self.counts = {"create": 0, "rename": 0, "update": 0, "delete": 0, "ok": 0, "errors": 0}

    def add(self, key):
        self.counts[key] += 1


def run_op(args, apply, stats, kind):
    if not apply:
        stats.add(kind)
        return
    r = gh(*args)
    if r.returncode == 0:
        stats.add(kind)
    else:
        stats.add("errors")
        print(f"      ОШИБКА: {r.stderr.strip()}")


def sync_repo(cfg, repo, set_name, opts):
    full = f"{cfg['org']}/{repo}"
    print(f"\n== {full}  (набор: {set_name})")
    stats = Stats()
    if not repo_exists(full):
        print("   репозиторий не найден или недоступен — пропущен")
        return stats, False
    try:
        existing_list = list_labels(full)
    except RuntimeError as e:
        print(f"   не удалось получить список меток: {e}")
        stats.add("errors")
        return stats, False

    existing = {l["name"].lower(): l for l in existing_list}
    ignore = {n.lower() for n in cfg.get("ignore", [])}
    delete = {n.lower() for n in cfg.get("delete", [])}
    desired = [
        l for l in cfg["labels"]
        if set_name in l["sets"] and not (opts.no_reserve and l["reserve"])
    ]
    all_names = {l["name"].lower() for l in cfg["labels"]}
    claimed = set()

    for lab in desired:
        name, color, desc = lab["name"], lab["color"].lower(), lab["description"]
        key = name.lower()
        cur = existing.get(key)
        if cur:
            claimed.add(key)
            changes = []
            if cur["name"] != name:
                changes.append("имя (регистр)")
            if cur["color"].lower() != color:
                changes.append("цвет")
            if (cur.get("description") or "") != desc:
                changes.append("описание")
            if not changes:
                stats.add("ok")
                continue
            print(f"   ~ обновить   {cur['name']}  ({', '.join(changes)})")
            run_op(["label", "edit", cur["name"], "--name", name, "--color", color,
                    "--description", desc, "-R", full], opts.apply, stats, "update")
            continue
        old = next((existing[a.lower()] for a in lab.get("aliases", [])
                    if a.lower() in existing and a.lower() not in claimed), None)
        if old:
            claimed.add(old["name"].lower())
            print(f"   > переименовать {old['name']} -> {name}")
            run_op(["label", "edit", old["name"], "--name", name, "--color", color,
                    "--description", desc, "-R", full], opts.apply, stats, "rename")
            continue
        print(f"   + создать    {name}{'  (резерв)' if lab['reserve'] else ''}")
        run_op(["label", "create", name, "--color", color, "--description", desc, "-R", full],
               opts.apply, stats, "create")

    # Устаревшие метки
    for key in sorted(delete & set(existing)):
        cur = existing[key]
        used = usage(full, cur["name"])
        used_txt = "не удалось посчитать задачи" if used is None else f"используется в {used} issues/PR"
        if not (opts.apply and opts.delete):
            print(f"   - удалить    {cur['name']}  ({used_txt}; удаление выполняется с --apply --delete)")
            continue
        if used != 0 and not opts.yes and not confirm(f"   Удалить «{cur['name']}» ({used_txt})?"):
            print(f"   - пропущено  {cur['name']}  ({used_txt})")
            continue
        print(f"   - удалить    {cur['name']}  ({used_txt})")
        run_op(["label", "delete", cur["name"], "--yes", "-R", full], True, stats, "delete")

    # Остальное — только сообщаем
    desired_names = {l["name"].lower() for l in desired}
    unmanaged = sorted(
        l["name"] for k, l in existing.items()
        if k not in claimed and k not in delete and k not in ignore
        and k not in desired_names and k not in all_names
    )
    elsewhere = sorted(
        l["name"] for k, l in existing.items()
        if k in all_names and k not in desired_names
    )
    if unmanaged:
        print(f"   ? вне системы (не тронуты): {', '.join(unmanaged)}")
    if elsewhere:
        print(f"   ? метки из других наборов (не тронуты): {', '.join(elsewhere)}")
    c = stats.counts
    print(f"   итого: создать {c['create']}, переименовать {c['rename']}, обновить {c['update']}, "
          f"удалить {c['delete']}, без изменений {c['ok']}, ошибок {c['errors']}")
    return stats, True


# --------------------------------------------------------------------------------------
def main():
    default_cfg = Path(__file__).resolve().with_name("labels.yml")
    p = argparse.ArgumentParser(description="Синхронизация меток организации с labels.yml (по умолчанию — dry-run).")
    p.add_argument("--config", default=str(default_cfg), help="путь к labels.yml")
    p.add_argument("--repo", action="append", metavar="NAME", help="только этот репозиторий (можно несколько раз)")
    p.add_argument("--apply", action="store_true", help="выполнить изменения (иначе только план)")
    p.add_argument("--delete", action="store_true", help="вместе с --apply: удалить устаревшие метки из списка delete")
    p.add_argument("--yes", action="store_true", help="не спрашивать подтверждение перед удалением используемых меток")
    p.add_argument("--no-reserve", action="store_true", help="не создавать резервные метки")
    p.add_argument("--check", action="store_true", help="только проверить labels.yml")
    opts = p.parse_args()

    try:
        cfg = load_config(opts.config)
    except (OSError, ValueError) as e:
        print(f"Не удалось прочитать {opts.config}: {e}")
        return 1
    errors = validate(cfg)
    if errors:
        print("labels.yml содержит ошибки:")
        for e in errors:
            print(f"  - {e}")
        return 1

    per_set = {s: sum(1 for l in cfg["labels"] if s in l["sets"]) for s in cfg["repo_sets"]}
    reserve = sum(1 for l in cfg["labels"] if l["reserve"])
    print(f"labels.yml: {len(cfg['labels'])} меток (из них резерв: {reserve}); по наборам: "
          + ", ".join(f"{s} — {n}" for s, n in per_set.items()))
    if opts.check:
        print("Проверка пройдена.")
        return 0

    if not shutil.which("gh"):
        print("Не найден GitHub CLI (gh). Установка: https://cli.github.com/")
        return 1
    if gh("auth", "status").returncode != 0:
        print("gh не авторизован. Выполните: gh auth login")
        return 1
    if opts.delete and not opts.apply:
        print("Флаг --delete действует только вместе с --apply; сейчас выполняется план.")

    repo_to_set = {r: s for s, repos in cfg["repo_sets"].items() for r in repos}
    targets = opts.repo or list(repo_to_set)
    unknown = [r for r in targets if r not in repo_to_set]
    if unknown:
        print(f"Неизвестные репозитории (нет в repo_sets): {', '.join(unknown)}")
        return 1

    print("Режим: " + ("ПРИМЕНЕНИЕ ИЗМЕНЕНИЙ" if opts.apply else "dry-run (ничего не меняется)"))
    failed = False
    for repo in targets:
        stats, ok = sync_repo(cfg, repo, repo_to_set[repo], opts)
        failed = failed or stats.counts["errors"] > 0
    if not opts.apply:
        print("\nЭто был dry-run. Чтобы применить изменения, добавьте --apply (и --delete для удаления устаревших меток).")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
