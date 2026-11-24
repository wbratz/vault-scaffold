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

0. **Gate the source.** Read `CLAUDE.md` and `LOCAL-NOTES.md`. Check source exclusions, secrets, and whether this agent/model may process the material before fetching, pasting, or writing Raw. If access is unclear or a restriction applies, stop. This starter has no automated privacy scanner; an agent's ability to read a file is not publication consent.

1. **Identify the source.** Resolve what was given (file path, URL, paste, or an already filtered file in `raw/`). Confirm its kind and provenance: article, design document, change discussion, transcript, etc. Fetch or paste only after step 0. If the source already lives in `raw/`, check its allowed status and proceed to summarizing without duplicating it.

2. **Store the allowed Raw copy.** Apply exclusions and secret removal first. Save under `raw/<source-slug>.<ext>` using a stable lower-kebab-case slug derived from the title. Preserve source type, date, creator, and access limits in a short header when known. Never overwrite an existing `raw/` file — if a collision happens, suffix with `-2`, `-3`, etc., and flag the duplicate to the user.

3. **Draft the summary page.** Write `vault/sources/<source-slug>.md` (the `sources` category is required by the schema for exactly this reason) with this skeleton:
   - H1 matching the source title.
   - One-paragraph TL;DR (2-4 sentences).
   - **Key claims** — each important assertion with its role (`source claim`, `local observation`, `inference`, or `proposal`), supporting Raw passage, and material scope. Attribute an author's recommendation to that author; do not record it as an owner decision.
   - **Open questions** — anything the source raises but doesn't answer.
   - **Cited by** — empty for now; future pages that link here will add themselves.
   - **Source** — relative link back to the `raw/` copy (`../../raw/<source-slug>.<ext>`).

4. **Walk for related pages.** Read `vault/index.md` and identify overlapping pages. Add useful cross-references. If the source contradicts or extends an existing page, record the conflict and source beside the relevant claim; do not silently replace an owner decision or an opinion page. Propose an edit when that page's authority is unclear.

5. **Update `vault/index.md`.** Add an entry under the `sources` section (and any other category whose pages this ingest spawned or modified). Entry format: `- [Title](sources/<slug>.md) — one-line summary`.

6. **Append to `vault/log.md`.** Add at the top: `## [<ISO date>] ingest | <source title>` followed by one line: what was ingested and a comma-separated list of pages touched.

## Failure modes to watch for

- Source already in `raw/` — verify that it is an allowed, filtered copy and summarize it without making a duplicate. If its status is unclear, stop and ask before reading further.
- Source is enormous (> ~50k tokens) — propose chunking and ingesting in passes, one section at a time.
- Source contradicts an existing decision — don't silently overwrite; flag the conflict and let the user adjudicate, possibly via the `capture-decision` skill.
- A clean citation accompanies an overbroad summary — compare the *meaning* of each important claim with the supporting Raw passage before filing.
