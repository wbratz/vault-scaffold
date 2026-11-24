---
name: file-back
description: >-
  Promote useful conversation content into a {{ vault_name }} vault page — typically invoked at the end of a query, a debugging session, or an exploration where the synthesis is worth keeping. Triggers include:
  {%+ for ex in trigger_examples['file-back'] %}"{{ ex }}"{% if not loop.last %}, {% endif %}{% endfor %}.
---

# file-back

Convert conversation content into a durable vault page. Most often invoked by the `query` skill after a non-trivial answer, but can be triggered any time the user (or you) recognizes that what just got said is worth keeping.

## What's worth filing back

| Worth filing | Not worth filing |
|---|---|
| A synthesis that pulled together 3+ existing pages into something new | A one-shot lookup ("what's the timeout?") |
| A debugging finding that explains *why* something fails | A passing comment or aside |
| A comparison between two approaches with tradeoffs | A restatement of something already on a page |
| A new entity description (system, component, person, vendor) | Chitchat or scheduling |
| A worked example users will copy from | A question that didn't get answered |

When in doubt, ask the user one line: *"Worth filing this back?"*

## Workflow

1. **Identify the keepable content.** Read back the conversation segment you intend to capture. State in one sentence what the page will *be about* (not the title — the topic).

2. **Propose a category.** Show the user: *"I'd file this under `<category>` — sound right?"* If two categories could fit, offer both and let the user pick. Decisions go via the `capture-decision` skill instead; if the content is a decision, hand off there.

3. **Propose a slug.** Lower-kebab-case, noun-phrase, descriptive. *"`vault/<category>/<slug>.md` — OK?"* Show before writing.

4. **Draft the page.** Skeleton:
   - **H1 title** matching the index entry.
   - **TL;DR** — one paragraph (2-4 sentences). Future-you reads this and decides whether to open the rest.
   - **Body** — the actual content. Use H2 sections for anything longer than ~10 lines.
   - **Claim roles and limits** — label source claims, local observations, inferences, proposals, and owner decisions where they matter. State applicability and unresolved uncertainty instead of polishing it away.
   - **Sources** — links into `raw/` for the claims they support. Read the passages before filing. A conversation date is provenance for the draft, not evidence that an external claim is true; if no durable source exists, mark the page provisional and say what evidence is missing.
   - **Related** — bullet list of links to other pages in this vault that touch the topic. If you can't think of any, note that too — it's a signal of an isolated page that may want more context later.

5. **Write the file.** Path: `vault/<category>/<slug>.md`.

6. **Update `vault/index.md`.** Add `- [Title](<category>/<slug>.md) — <one-line TL;DR>` under the relevant category, in alphabetical order by title within the section.

7. **Append to `vault/log.md`.** Top of file: `## [<ISO date>] file-back | <title>` followed by one line noting what conversation it came from (e.g., "filed from query about idempotency keys").

8. **Suggest back-links.** Walk the "Related" list from step 4. For each related page, propose adding a one-line back-reference to the new page. Don't write the back-references silently — show them as a list and let the user approve in bulk: *"Want me to add back-links to these 3 pages?"*

## Failure modes to watch for

- **Filing back duplicates.** Before drafting, check `vault/index.md` under the proposed category. If a similar title or topic already exists, ask whether to update the existing page instead of creating a new one.
- **Filing too broad.** A page titled "Notes on the system" will rot. Push for a narrower topic — what specifically did this conversation teach? If you can't narrow it, don't file.
- **Filing too narrow.** A page that exists only to record one log line belongs in `vault/log.md`, not in a `vault/<category>/` page. Filing back is for content with reuse value.
