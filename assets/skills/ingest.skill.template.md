---
name: ingest
description: >-
  Pull a new source into the {{ vault_name }} vault — read it, summarize it, file it, and update the index and log. Use when the user says things like:
  {%+ for ex in trigger_examples.ingest %}"{{ ex }}"{% if not loop.last %}, {% endif %}{% endfor %}.
---

# ingest

Add a new source to **{{ vault_name }}** and propagate it through the vault.

## Interaction mode

Default: **{{ ingest_mode | replace('_', ' ') }}**.
{% if ingest_mode == 'confirm_each_step' %}
Pause after each numbered step below and wait for the user's OK before proceeding.
{% elif ingest_mode == 'confirm_plan' %}
Before step 1, present the plan (the source, its destination category, the existing pages you expect to touch) and wait for a single approval. Then execute steps 1–6 without further prompting and show a final summary.
{% else %}
Run steps 1–6 without prompting. At the end, show a summary listing every file created or modified.
{% endif %}
If the user says "step by step" or "just do it", override the default for this invocation.

## Workflow

0. **Check operational constraints.** Re-read the "Operational notes" section of `CLAUDE.md`. If the user has marked any paths, sources, or topics as out-of-scope (e.g., "treat `services/legacy/` as out-of-scope") and the candidate source matches, **abort immediately** with a one-line explanation of which note applied. Do not proceed to step 1.

1. **Identify the source.** Resolve what was given (file path, URL, paste, drag-and-drop). Confirm the kind: article, RFC, PR, Slack thread, transcript, etc. If the source is a URL, fetch it; if it's a paste, write it to `raw/<slug>.md` verbatim.

2. **Store the raw copy.** Save under `raw/<source-slug>.<ext>` using a stable lower-kebab-case slug derived from the title. Never overwrite an existing `raw/` file — if a collision happens, suffix with `-2`, `-3`, etc., and flag the duplicate to the user.

3. **Draft the summary page.** Write `vault/sources/<source-slug>.md` (the `sources` category is required by the schema for exactly this reason) with this skeleton:
   - H1 matching the source title.
   - One-paragraph TL;DR (2-4 sentences).
   - **Key claims** — bullet list of the factual claims worth remembering.
   - **Open questions** — anything the source raises but doesn't answer.
   - **Cited by** — empty for now; future pages that link here will add themselves.
   - **Source** — relative link back to the `raw/` copy (`../../raw/<source-slug>.<ext>`).

4. **Walk for related pages.** Read `vault/index.md` and identify pages in any category that overlap with the new source's topics. For each, add a cross-reference into the new summary, and add a back-reference from the existing page into the new summary's "Cited by" section. If the source contradicts or extends an existing page, add an inline note on that page pointing to the new source.

5. **Update `vault/index.md`.** Add an entry under the `sources` section (and any other category whose pages this ingest spawned or modified). Entry format: `- [Title](sources/<slug>.md) — one-line summary`.

6. **Append to `vault/log.md`.** Add at the top: `## [<ISO date>] ingest | <source title>` followed by one line: what was ingested and a comma-separated list of pages touched.

## Failure modes to watch for

- Source already in `raw/` — abort and ask the user whether to re-ingest or skip.
- Source is enormous (> ~50k tokens) — propose chunking and ingesting in passes, one section at a time.
- Source contradicts an existing decision — don't silently overwrite; flag the conflict and let the user adjudicate, possibly via the `capture-decision` skill.
