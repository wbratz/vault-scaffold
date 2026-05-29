---
name: capture-decision
description: >-
  Use this skill PROACTIVELY whenever a decision is being made in conversation about the {{ vault_name }} project — an architecture choice, a tradeoff, a policy, a "let's go with X" moment — and file it as a decision page before the context is lost. Triggers include:
  {%+ for ex in trigger_examples['capture-decision'] %}"{{ ex }}"{% if not loop.last %}, {% endif %}{% endfor %}.
---

# capture-decision

Decisions are the most valuable and the most quickly forgotten artifact in any project. **Use this skill proactively** — do not wait to be asked. The moment a decision surfaces in conversation, capture it.

## When to fire (without being asked)

Look for any of these signals:

- Explicit conclusion: "let's go with X", "we'll do Y", "decided", "going with the second option".
- Implicit conclusion: the user weighed options and is now describing what they'll build as if it's settled.
- Course correction: a user direction that changes a previously chosen approach.
- Tradeoff acknowledged: "yeah, X is slower but Y has the failure mode we can't accept".
- Reversal: "scratch that, we're not doing X anymore".

If you see any of these and the conclusion isn't already in `vault/decisions/`, fire.

## Workflow

1. **Interrupt briefly.** One line, no derail: *"I'm going to capture this as a decision page — sound right?"* If the user says no, drop it. If they say yes (or nothing within the same turn and the decision is clear), proceed.

2. **Draft the page in memory** before writing anything. Required sections:
   - **Decision** — one sentence stating what was chosen. Plain English, no hedging.
   - **Context** — what problem prompted it. 2-3 sentences. Include the trigger (incident, PR review, planning session, customer ask).
   - **Options considered** — bullet list. For each rejected option, one line on *why* it was rejected.
   - **Tradeoffs accepted** — what we gave up by choosing this. Be honest; this is the section future-you will thank present-you for.
   - **Reversibility** — easy to back out / hard / one-way. Helps the next person judge how much to argue.
   - **Source** — link to the conversation, PR, ticket, or "verbal, {{ created_at }} session" if it was pure chat.

3. **Choose a slug.** Format: `vault/decisions/<short-kebab-summary>.md`. The slug should be a noun phrase that describes the decision itself ("payment-retry-policy", "drop-redis-cache"), not the discussion ("retry-discussion-with-bob"). Show the slug to the user before writing.

4. **Check for supersession.** Scan `vault/decisions/` (via `vault/index.md`) for any prior decision this one overrides. If found, edit the prior decision: add a "Superseded by" line at the top linking forward, and leave the original body intact (decisions are history, not state).

5. **Write the file.** Use the skeleton from step 2.

6. **Update `vault/index.md`.** Add the entry under the `decisions` section: `- [Decision title](decisions/<slug>.md) — one-line summary`.

7. **Append to `vault/log.md`.** Top of file: `## [<ISO date>] decision | <title>`. One line on what was decided and what (if anything) it superseded.

8. **Propagate.** If this decision changes how something is built or operated, the affected `concepts`, `runbooks`, or `entities` pages need an inline pointer to the new decision. Don't rewrite those pages — just add a line: *"As of [date], see [decision title](../decisions/<slug>.md) for current policy."*

## Failure modes to watch for

- **Overcapture.** Not every preference is a decision. "Let's use 2-space indent" is a convention, not a decision. Decisions involve tradeoffs the user could imagine regretting.
- **Premature capture.** If the user is still actively weighing options, wait. Capture when there's a conclusion, not while there's a debate.
- **Silent capture.** Always show the slug and a one-line summary of what you're about to file. Never write a decision page without confirmation.
