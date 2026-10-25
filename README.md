# .github

Organization-wide defaults and settings for **[wolm-sdarp](https://github.com/wolm-sdarp)** — *World of Linear Models: Statistics & Data Analysis in R for Psychologists* (WoLM SDARP).

This repository holds no educational content. It contains:

- the organization profile shown at [github.com/wolm-sdarp](https://github.com/wolm-sdarp);
- default issue forms and the pull request template shared by all repositories of the organization;
- the source of truth for labels and a script that applies them.

## Contents

| Path | Purpose |
| --- | --- |
| `profile/README.md` | Organization profile page |
| `.github/ISSUE_TEMPLATE/*.yml` | Issue forms for all repositories; each form sets the issue type |
| `.github/ISSUE_TEMPLATE/config.yml` | Template chooser settings: blank issues are disabled, questions go to Discussions |
| `.github/pull_request_template.md` | Pull request template, including the AI contribution disclosure block |
| `settings/labels.yml` | Source of truth for labels: names, colors, descriptions, repository sets, deprecated labels |
| `settings/apply-labels.py` | Syncs labels in the organization's repositories with `labels.yml` |
| `settings/comm-health.yml` | Where the canonical versions of community health files are maintained |

## How defaults work

GitHub uses files from this repository as defaults for every repository of the organization that **does not have its own file of the same kind**. A repository-level file (for example, its own `.github/ISSUE_TEMPLATE/` folder) overrides the default completely, not partially.

Default files are not copied into other repositories, so the "Community Standards" checklist of a repository may not show them as present.

## Issue forms

| File | Form | Issue type |
| --- | --- | --- |
| `01-content-mistake.yml` | Content mistake | Mistake |
| `02-edit-proposal.yml` | Edit proposal | Editing |
| `10-writing-task.yml` | Writing task | Writing |
| `11-learning-design.yml` | Learning design task | Learning Design |
| `12-assessment-task.yml` | Assessment task | Assessment |
| `13-localization-task.yml` | Translation and localization task | Localization |
| `20-technical-problem.yml` | Technical problem | Bug |
| `21-feature-request.yml` | Technical feature | Feature |
| `22-maintenance.yml` | Maintenance | Maintenance |
| `23-release.yml` | Release (reserved) | Release |
| `30-research-task.yml` | Research question | Research |
| `31-epic.yml` | Epic | Epic |
| `32-review-task.yml` | Review task | Review |
| `99-other.yml` | Other | Task |

Numeric prefixes set the order in the chooser: 01–02 for readers and reviewers, 10–13 for content and learning design, 20–23 for technical work, 30–32 for research, epics and reviews, 99 for everything else.

Before relying on the forms, check that:

- every issue type used in `type:` exists in the organization settings — otherwise the form cannot assign it;
- the labels used by the forms exist in the repositories (see [Labels](#labels));
- the Discussions link in `config.yml` points to an enabled Discussions page.

## Labels

Requirements: [GitHub CLI](https://cli.github.com/) (`gh`) authenticated with `gh auth login`, write access to the organization's repositories, Python 3 (standard library only).

```bash
python3 settings/apply-labels.py --check              # validate labels.yml (no GitHub access needed)
python3 settings/apply-labels.py                      # dry run for all repositories
python3 settings/apply-labels.py --repo book1         # dry run for one repository
python3 settings/apply-labels.py --apply              # create, update and rename labels
python3 settings/apply-labels.py --apply --delete     # same, plus delete deprecated labels
```

The script:

- **creates** missing labels and **updates** colors and descriptions of existing ones;
- **renames** labels listed in `aliases`, so issues stay attached to them;
- **deletes** labels from the `delete` list only with `--apply --delete`; before deleting it shows how many issues and pull requests use each label and asks for confirmation (`--yes` skips the prompt);
- **leaves untouched** labels from the `ignore` list (created by Dependabot) and any other labels not described in the file — it only lists them;
- skips repositories that do not exist in the organization yet;
- is idempotent: a second run on an up-to-date repository changes nothing.

Recommended first run: dry run → review the plan → `--apply` → move issues off deprecated labels → `--apply --delete`.

### Changing labels

1. Edit `settings/labels.yml` (the format is described in the comments at the top of the file) and run `--check`.
2. When renaming a label, add its previous name to `aliases`.
3. When retiring a label, move it to the `delete` list after its issues have been relabeled.
4. Record the change in the change history of the issues documentation.
5. Run a dry run, then `--apply`.

To add a new repository, put its name into the right set in `repo_sets`.

## Community health files

Canonical texts of the code of conduct, contributing guide, security policy and other community documents are maintained in the [`documentation`](https://github.com/wolm-sdarp/documentation) repository (see `settings/comm-health.yml`). Their default copies for the organization are to be added to this repository. *TBA.*

## Documentation

- [Issue types and labels](https://wolm-sdarp.github.io/documentation/git-gh-docs/gh-issues-docs)
- [Git workflow](https://wolm-sdarp.github.io/documentation/git-gh-docs/git-workflow): branches, commits, pull requests, releases
- [AI Usage Policy](https://wolm-sdarp.github.io/documentation/community-docs/ai-usage-policy)
- [Project board](https://github.com/orgs/wolm-sdarp/projects/1)

## Contributing

Changes to this repository affect every repository of the organization, so they go through a pull request like any other change: a branch from `dev`, a Conventional Commits title, and the pull request template filled in, including the AI contribution section. See the [Git workflow](https://wolm-sdarp.github.io/documentation/git-gh-docs/git-workflow).

## License

Unless otherwise noted:

- **content** of the WoLM SDARP project (texts, illustrations, assignments and other educational materials, documentation) is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/);
- **code** of the project is licensed under the [MIT License](https://opensource.org/license/mit). This covers both technical code (build and publishing scripts, workflows, configurations, and utilities) and code examples in the books and other materials, including code embedded in the text.

Some materials may be distributed under a different license; in that case, the license is stated in the material itself or in the repository where it is published.

Datasets and other third-party materials are distributed under their own licenses, which are stated separately for each of them.
