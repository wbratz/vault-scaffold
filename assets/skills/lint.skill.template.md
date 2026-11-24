---
name: lint
description: >-
  Run a health check on the {{ vault_name }} vault — find contradictions, stale claims, orphans, broken links, missing cross-references, and data gaps. Use when the user says things like:
  {%+ for ex in trigger_examples.lint %}"{{ ex }}"{% if not loop.last %}, {% endif %}{% endfor %}.
---

# lint

Periodic health check across the **{{ vault_name }}** vault. Run weekly, after a burst of ingests, or any time the user feels the vault has drifted.

## Workflow

1. **Build the page set.** Read `vault/index.md` and record every page it lists. Walk `vault/` recursively and record every `*.md` file on disk (excluding `index.md`, `log.md`, and dotfiles like `.scaffold-config.json`). The symmetric difference is your first finding set:
   - On disk but not in index → **orphans**.
   - In index but not on disk → **broken index entries**.

2. **Check cross-references.** For each page, parse markdown links of the form `(<category>/...)` or `(../...)`. Resolve each target. Links to nonexistent pages → **broken links**.

3. **Check raw citations.** For each page, parse links into `raw/`. Missing files → **broken source citations**. Bonus: if a page cites a `raw/` file that has no corresponding summary in `vault/sources/`, flag it as **un-summarized source**.

   For a small sample of high-impact claims, open the cited passages and ask whether they support the *meaning*, attribution, and scope of the claims. Report this as a review finding, never as an automated entailment verdict. Flag a proposal described as an owner decision.

4. **Scan for contradictions.** When two pages make claims about the same entity, decision, or concept, surface the conflict. Heuristic: pages that mention the same proper noun or decision title and contain words like "always", "never", "must", "should not" deserve a closer look. Don't try to be exhaustive — surface the candidates and let the user adjudicate.

5. **Scan for stale claims.** A page is potentially stale if any of these are true: its `updated` frontmatter (when present) predates a source it cites; a source it cites has a newer version in `raw/`; the page hasn't been touched in over 6 months and lives in a fast-moving category (e.g., `runbooks`, `decisions`).

6. **Find missing cross-references.** Identify the top ~10 entities or concepts mentioned across many pages. For each, flag pages that mention the term but don't link to its canonical page.

7. **Find data gaps.** Two signals: (a) categories with very few pages relative to the others; (b) recurring queries in `vault/log.md` that don't map to any page. Both suggest the vault should grow in that direction.

   Read `evaluation/cases/` when it exists. Treat repeated answer misses as stronger evidence of a gap than category size alone. Check that any changed page has not broken a previously passing distinction.

8. **Produce a report.** Group findings by severity:
   - **Broken** — broken links, broken index entries, missing files. Fix immediately.
   - **Stale** — contradictions, stale claims. User must adjudicate.
   - **Gaps** — orphans, missing cross-refs, thin categories. Lower priority.
   For each finding, propose a concrete fix (e.g., "add `[retry policy](../decisions/payment-retry-policy.md)` to line 14 of `vault/concepts/idempotency.md`"). Wait for user approval before writing.

9. **Apply approved fixes and log.** Make the edits the user signed off on. Append a single log entry to `vault/log.md`: `## [<ISO date>] lint | <N findings, M applied, K deferred>` with a one-line summary.

## What lint is NOT

- It is not a rewrite pass. Don't rephrase or "improve" pages while linting; that's a separate, explicit ask.
- It is not a deletion pass. Orphans get flagged, not deleted. The user might want to keep an unlisted page on purpose (drafts, scratch).
