## What was done / Что сделано
<!-- EN: briefly — what changed and why. -->
<!-- RU: коротко — что изменилось и зачем. -->

## Related issues / Связанные задачи
<!-- EN: use `Closes #N` if the PR completes the issue, `Refs #N` otherwise. -->
<!-- RU: `Closes #N` — если PR завершает задачу, иначе `Refs #N`. -->
Closes #

## How to check / Как проверить
<!-- EN: what to open or run; for text — what exactly to reread. -->
<!-- RU: что открыть или запустить; для текста — что именно перечитать. -->

## AI contribution / Участие ИИ
See the [AI Usage Policy](https://wolm-sdarp.github.io/documentation/community-docs/ai-usage-policy) / См. [политику использования ИИ](https://wolm-sdarp.github.io/documentation/community-docs/ai-usage-policy)

<!--
EN: Required for every PR. Choose the level according to the AI Usage Policy (§3.2):
    if the published wording, code, image or assignment was proposed by AI, the level is at least `co-created`.
    If in doubt between two levels, choose the higher one.
    Not to be disclosed: spelling checks without rewriting, inline autocompletion, search, format conversion (§5.6).
RU: Заполняется в каждом PR. Уровень выбирается по AI Usage Policy (§3.2):
    если публикуемая формулировка, код, изображение или задание предложены ИИ, уровень не ниже `co-created`.
    При сомнении между двумя уровнями выбирайте более высокий.
    Не раскрываются: проверка орфографии без переписывания, автодополнение в строке, поиск, конвертация форматов (§5.6).
-->

**Level / Уровень** (choose one / выберите один):
- [ ] `none` — AI was not used / ИИ не использовался
- [ ] `assisted` — ideas, explanations, critique, proofreading; the author made all edits / идеи, объяснения, критика, вычитка; все правки внёс автор
- [ ] `co-created` — AI produced fragments that the author substantially reworked / ИИ создал фрагменты, которые автор переработал по существу
- [ ] `generated` — the result was created by AI and accepted without substantial rework / результат создан ИИ и принят без существенной переработки

<!--
EN: For any level other than `none`, fill in the lines below. Short form (§5.7):
    "AI: <level>, tool: <name>, task: <what>, review: <by whom and how>".
RU: Для любого уровня, кроме `none`, заполните строки ниже. Краткая форма (§5.7):
    «ИИ: <уровень>, инструмент: <название>, задача: <что>, проверка: <кем и как>».
-->
- **Tool and model / Инструмент и модель:**
- **Task / Задача:** <!-- EN: e.g., draft, code, translation, review (task vocabulary — Appendix A) / RU: например, draft, code, translation, review (словарь задач — приложение A) -->
- **What exactly / Что именно:** <!-- EN: files or fragments created with AI / RU: файлы или фрагменты, созданные с помощью ИИ -->
- **How the result was processed / Как обработан результат:** <!-- EN: accepted as is, corrected, rewritten, rejected / RU: принят как есть, исправлен, переписан, отклонён -->
- **Key part of the prompt / Ключевая часть запроса:** <!-- EN: for `co-created` and `generated` — context and constraints, if they help the reviewer understand how the result was obtained (§5.1) / RU: для `co-created` и `generated` — контекст и ограничения, если они помогают рецензенту понять, как получен результат (§5.1) -->
- **Review / Проверка:** <!-- EN: level `self` / `independent` / `expert`; what was checked (references, formulas, code, answer keys) and by whom / RU: уровень `self` / `independent` / `expert`; что проверено (ссылки, формулы, код, ключи) и кем -->

<!--
EN: For `generated`, the reviewer must not be the person who wrote the prompts (§6.2).
    An "approved" verdict from AI does not count as a review (§6.3).
RU: Для `generated` ревьюер не должен быть тем, кто формулировал запросы к ИИ (§6.2).
    Заключение «одобрено» от ИИ не засчитывается как ревью (§6.3).
-->
- [ ] `ai_*` fields in the front matter and the `AI_USAGE.md` entry are updated / Поля `ai_*` в front matter и запись в `AI_USAGE.md` обновлены
- [ ] Commits contain `Assisted-by:` / `Generated-by:` trailers; automatic trailers (e.g., `Co-Authored-By`) are kept / Коммиты содержат trailers `Assisted-by:` / `Generated-by:`; автоматические trailers (например, `Co-Authored-By`) не удалены
- [ ] If this PR description was written by AI, this is stated in it / Если описание этого PR написано ИИ, это в нём указано
- [ ] I have reviewed the AI output, understand the content and take responsibility for it / Я проверил(а) результаты ИИ, понимаю содержание и отвечаю за него

## Checklist / Чек-лист
- [ ] The build passes locally (`quarto render`) / the code runs — Сборка проходит локально (`quarto render`) / код выполняется
- [ ] Labels and milestone are set — Метки и milestone выставлены
- [ ] Educational content is reviewed by a human (by whom: …) — Образовательное содержание проверено человеком (кем: …)
- [ ] The "AI contribution" section is filled in — Раздел «Участие ИИ» заполнен
