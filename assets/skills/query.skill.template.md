---
name: query
description: >-
  Answer questions from the {{ vault_name }} vault with citations and propose
  filing valuable syntheses back into the vault. Use when the user asks what
  the vault knows, requests a grounded lookup, or asks a substantive question
  about this vault's domain.
---

# query

Answer a question grounded in the **{{ vault_name }}** vault and, when the answer is worth keeping, propose promoting it into a vault page.

## Workflow

1. **Route the question.** Read `vault/index.md`, then search the vault for the user's terms, source names, and likely synonyms. Build a shortlist of 1-5 relevant pages. An index entry or search hit is a route, not evidence.

2. **Read the candidates.** Follow cross-references one hop deep if a candidate points to another page that's clearly relevant. Do NOT load the whole vault — index + targeted reads is the whole point.

3. **Verify the source for substantive claims.** Open the cited `raw/` passage behind the central conclusion. Check what it actually asserts, who said it, when it applies, and whether the page adds an inference. A matching phrase or valid link is not enough. If the pages are silent, search `raw/` and the surrounding repo within the user's access constraints before declaring a gap. If source evidence is unavailable, mark the conclusion unverified.

4. **Serve focused context.** Answer the question first. Explain the relevant meaning, relationship, or decision rule; cite the page and Raw support near the claim; give scope, exceptions, and uncertainty when material. Distinguish a `source claim`, `local observation`, `inference`, `proposal`, and `owner decision`. For an agent doing work, use the context-card shape in `ADOPTION.md`: task, current terms, applicable rule, evidence, boundary, next action. Keep it small enough to inspect.

5. **Propose filing back.** If your answer synthesizes information that isn't already a standalone page — a new concept, a comparison, a decision rationale, a worked example, a debugging finding — propose promoting it via the `file-back` skill. Be specific: name the proposed page slug, the category, and a one-sentence draft. Default to opt-in; do not file back silently. Skip this step for trivial lookups ("what's the timeout value?") where filing back would just be noise.

6. **Keep useful feedback.** For a recurring question, a miss, or a corrected answer, use `review-answer` to record a local case. Do not log trivial lookups or private question text merely because a query occurred. If filing back was accepted, that skill records its own change.

## Quality bar

- A citation is a trail to inspect, not proof. Check that the source supports the **meaning** of a substantive conclusion.
- "I don't see it in the vault" is acceptable after a targeted search and source check. Name what was searched and what remains unknown.
- If two pages contradict each other on the question, surface the contradiction explicitly and recommend running `lint`.
