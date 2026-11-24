---
name: review-answer
description: >-
  Review a real {{ vault_name }} answer against its question, cited Raw evidence,
  scope, and known wrong answers. Use when the user asks to grade an answer,
  correct a misleading answer, or investigate a retrieval miss.
---

# review-answer

Find out whether the Vault served usable, supported context for a real question. Follow `evaluation/README.md`. Keep private questions and excerpts in ignored `evaluation/cases/`.

## Workflow

1. **Capture the case.** Record the user's question, the answer being reviewed, date, and relevant agent or context version. Use the user's wording; do not substitute a convenient benchmark question.
2. **Read the evidence.** Locate the cited page and its supporting Raw passages. If the answer cited no source, search for the best available evidence. Record source type, authority, date, and access limits. If a passage is unavailable, mark support unverified.
3. **Write the expected distinction.** State the condition, relationship, or decision rule a good answer must preserve. Write one plausible wrong answer that loses a crucial condition. Distinguish owner decisions from source recommendations and agent proposals.
4. **Grade separate dimensions.** Mark retrieval, claim support, meaning and relationships, scope and uncertainty, and citation accuracy as `pass`, `partial`, or `miss`. Explain each `partial` or `miss` with a specific passage or gap. A top search result is not an answer-quality pass.
5. **Find the cause.** Choose the smallest cause that explains the miss: absent source, weak page synthesis, ambiguous term, wrong routing, unsupported inference, stale decision, or answer composition. Draft a concrete correction. Preserve Raw and respect page edit authority.
6. **Save and re-ask.** Write the case under `evaluation/cases/<short-slug>.md` using the template in `evaluation/README.md`. Apply authorized corrections, then ask the same question again and compare against the expected distinction and known wrong answer. Keep the earlier result as a regression record.

This review is a reasoned judgment with visible evidence. Do not claim automated entailment checking or a general performance gain from one case.
