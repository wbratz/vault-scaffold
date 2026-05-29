---
name: query
description: >-
  Answer a question using the {{ vault_name }} vault, citing sources, and propose filing the answer back when it would compound. Use when the user says things like:
  {%+ for ex in trigger_examples.query %}"{{ ex }}"{% if not loop.last %}, {% endif %}{% endfor %}.
---

# query

Answer a question grounded in the **{{ vault_name }}** vault and, when the answer is worth keeping, propose promoting it into a vault page.

## Workflow

1. **Read `vault/index.md` first.** Identify candidate pages by category and one-line summary. Build a shortlist of 1-5 pages most likely to hold the answer.

2. **Read the candidates.** Follow cross-references one hop deep if a candidate points to another page that's clearly relevant. Do NOT load the whole vault — index + targeted reads is the whole point.

3. **Reach for `raw/` only if needed.** If a wiki page summarizes a source but you need a detail the summary skipped, open the cited `raw/` file. If the vault is silent on the topic entirely, stop and ask the user whether to ingest something new instead of guessing.

4. **Compose the answer.** Cite every claim with a relative link to the page (or `raw/` file) it came from. Make the citation inline (e.g., *"as documented in [retry policy](vault/decisions/payment-retry-policy.md)"*), not a footnote — the user is reading in chat, not in a journal.

5. **Propose filing back.** If your answer synthesizes information that isn't already a standalone page — a new concept, a comparison, a decision rationale, a worked example, a debugging finding — propose promoting it via the `file-back` skill. Be specific: name the proposed page slug, the category, and a one-sentence draft. Default to opt-in; do not file back silently. Skip this step for trivial lookups ("what's the timeout value?") where filing back would just be noise.

6. **Log the query.** If the user accepted filing back, the `file-back` skill writes its own log entry — you're done. If they declined or the question was a trivial lookup, append a one-line entry to `vault/log.md`: `## [<ISO date>] query | <one-line question>` with no body.

## Quality bar

- An answer with no citations is a guess. Either find the citation or admit the vault doesn't know.
- "I don't see it in the vault" is a complete and acceptable answer. It is also a signal to ingest something — say so.
- If two pages contradict each other on the question, surface the contradiction explicitly and recommend running `lint`.
