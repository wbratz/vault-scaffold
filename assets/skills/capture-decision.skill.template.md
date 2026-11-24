---
name: capture-decision
description: >-
  Notice explicit owner decisions about the {{ vault_name }} project and offer to record them with their source and scope. Triggers include:
  {%+ for ex in trigger_examples['capture-decision'] %}"{{ ex }}"{% if not loop.last %}, {% endif %}{% endfor %}.
---

# capture-decision

Decisions are easy to lose. Notice them proactively, then verify **whose decision** it is before recording one. A source's recommendation, an agent proposal, or silence after a question is not an owner decision.

## When to fire (without being asked)

Look for any of these signals:

- Explicit conclusion: "let's go with X", "we'll do Y", "decided", "going with the second option".
- Likely conclusion: the user weighed options and now describes one as settled. Ask whether it is a decision if the wording leaves room for doubt.
- Course correction: a user direction that changes a previously chosen approach.
- Tradeoff acknowledged: "yeah, X is slower but Y has the failure mode we can't accept".
- Reversal: "scratch that, we're not doing X anymore".

If you see any of these and the conclusion isn't already in `vault/decisions/`, fire.

## Workflow

1. **Verify authority.** Quote or paraphrase the owner's explicit choice and show a proposed slug and one-line summary. An explicit request to record it is authorization. Otherwise ask whether to capture it and wait for an affirmative answer. Silence is never confirmation. If the source is an article, meeting note, or assistant suggestion, attribute it as a source claim or proposal until the owner adopts it.

2. **Draft the page in memory** before writing anything. Required sections:
   - **Decision** — one sentence stating what was chosen. Plain English, no hedging.
   - **Context** — what problem prompted it. 2-3 sentences. Include the trigger (incident, PR review, planning session, customer ask).
   - **Options considered** — bullet list. For each rejected option, one line on *why* it was rejected.
   - **Tradeoffs accepted** — what we gave up by choosing this. Be honest; this is the section future-you will thank present-you for.
   - **Reversibility** — easy to back out / hard / one-way. Helps the next person judge how much to argue.
   - **Source and authority** — link to the conversation, change, or Raw record if available; identify the owner statement and date. If no durable record exists, say `owner statement in live conversation; no Raw record` rather than inventing a citation.
   - **Scope and status** — where this choice applies, effective date if known, and whether it is current, provisional, or superseded.

3. **Choose a slug.** Format: `vault/decisions/<short-kebab-summary>.md`. The slug should describe the decision itself ("payment-retry-policy", "drop-redis-cache"), not the discussion. If this vault has no `decisions` category, ask to add it or choose an existing authorized category before writing.

4. **Check for supersession.** Scan `vault/decisions/` (via `vault/index.md`) for any prior decision this one overrides. If found, edit the prior decision: add a "Superseded by" line at the top linking forward, and leave the original body intact (decisions are history, not state).

5. **Write the file.** Use the skeleton from step 2.

6. **Update `vault/index.md`.** Add the entry under the `decisions` section: `- [Decision title](decisions/<slug>.md) — one-line summary`.

7. **Append to `vault/log.md`.** Top of file: `## [<ISO date>] decision | <title>`. One line on what was decided and what (if anything) it superseded.

8. **Propagate.** If this decision changes how something is built or operated, the affected `concepts`, `runbooks`, or `entities` pages need an inline pointer to the new decision. Don't rewrite those pages — just add a line: *"As of [date], see [decision title](../decisions/<slug>.md) for current policy."*

## Failure modes to watch for

- **Overcapture.** Not every preference is a decision. "Let's use 2-space indent" is a convention, not a decision. Decisions involve tradeoffs the user could imagine regretting.
- **Premature capture.** If the user is still actively weighing options, wait. Capture when there's a conclusion, not while there's a debate.
- **Silent capture.** Always show the slug and a one-line summary. Never treat a missing reply as confirmation.
