# Iteration 5 — Test findings

Tested 2026-05-28. Three scenarios scaffolded by directly constructing the config each one's interview would produce, then running `scripts/scaffold.py` with that config and inspecting the output.

## What was tested

| Scenario | Domain / Scope / Audience | Categories | ingest_mode | custom_notes | Target |
|---|---|---|---|---|---|
| A | engineering / single_repo / small_team | concepts, decisions, runbooks, systems, **sources** | confirm_plan | *(none)* | `/tmp/vault-test-eng` |
| B | product / cross_project / large_team | features, personas, decisions, experiments, **sources** | confirm_each_step | "We use Linear for tickets and Pitch for decks" | `/tmp/vault-test-product` |
| C | research / personal / solo | entities, concepts, papers, syntheses, **sources** | autonomous | *(none)* | `/tmp/vault-test-research` |

`sources` was silently added in every scenario per the SKILL.md rule (the user's interview answers did not include it).

## What passed (all 3 scenarios)

- Structure (17 expected files per scenario).
- `CLAUDE.md` lists every chosen category as `` `vault/<cat>/` ``.
- All 5 sub-skills present, >500 bytes each, YAML frontmatter parses cleanly under PyYAML.
- `vault/.scaffold-config.json` snapshot equals the input config.
- `git log` shows a single commit: `vault: initial scaffold via vault-scaffold v0.1.0`.
- Enum prose displays cleanly (`single repo`, `cross project`, `confirm plan`, `confirm each step`, `autonomous`).
- Scenario B's `custom_notes` lands in the Operational notes section verbatim.
- Scenario A's empty `custom_notes` produces the friendly italic placeholder.
- ingest-skill interaction-mode adapter selects the correct paragraph for each of the three `ingest_mode` values.

**Net: 0 structural failures across 3 scenarios.**

## Issues found

### I5-1 — Fallback category description is tautological (severity: high)

**Where:** rendered `CLAUDE.md` "Page categories" section AND `vault/index.md` per-category heading, in every scenario where the user picked a non-default category.

**Observed (Scenario B):**
```
- **`vault/features/`** — User-defined category: features
- **`vault/personas/`** — User-defined category: personas
- **`vault/experiments/`** — User-defined category: experiments
```

**Expected:** something that tells the reader what these pages *are*. The current fallback echoes the category name back, which is informationally empty.

**Impact:** This fires for every domain that picks a category outside the small built-in set (`entities`, `concepts`, `decisions`, `syntheses`, `sources`, `runbooks`). In practice that's most product/research/team vaults — meaning most generated vaults will ship with this dead-weight wording.

**Suggested fix (one of):**
- **(a) Expand `DEFAULT_CATEGORY_DESCRIPTIONS` in `scripts/scaffold.py`** to cover the per-domain default categories called out in `SKILL.md`'s Phase 2 table — `systems`, `incidents`, `features`, `personas`, `experiments`, `competitors`, `papers`, `methods`, `processes`. Roughly 9 one-liners. Cheapest fix, biggest gain. Iteration 6 should do this regardless because per-domain template files are on the roadmap.
- **(b) Have the `vault-scaffold` SKILL.md ask** for a one-line description when the user picks a custom category not in defaults. Adds a question to the interview (bad for the "under 2 minutes" goal).
- **(c) Drop the description line entirely** when no real description exists. Cleaner than the tautology but loses the index-as-catalog readability.

**Recommendation:** (a). Low-cost; aligns with Iteration 6's planned per-domain templates work.

### I5-2 — `custom_notes` is rendered verbatim, no trailing punctuation normalization (severity: low)

**Where:** Scenario B's Operational notes section.

**Observed:**
```
We use Linear for tickets and Pitch for decks
```

(No period.)

**Expected/Acceptable:** the user typed it that way. But rendered alongside the surrounding prose ("These are user-imposed constraints..."), the missing terminal punctuation looks abrupt.

**Suggested fix:** In `scripts/scaffold.py`'s `build_context`, if `custom_notes` is non-empty and doesn't end with `.`, `!`, or `?`, append a period. Trivial; cosmetic.

**Recommendation:** defer to Iteration 7+ unless trivially folded into another `build_context` change.

### I5-3 — All three scenarios had empty `seed_artifacts`, so option (b) ingest-spawn was not exercised (severity: untested, not a bug)

**What:** The post-scaffold "offer to ingest a seed artifact" branch added in Iteration 4 (option b — spawn `claude -p "ingest <artifact>"` in the new vault) was never triggered by these scenarios because every scenario's `seed_artifacts` was `[]`.

**Risk:** That code path is currently 100% untested. Plausible failure modes:
- `claude` not on PATH on a fresh machine.
- `claude -p` flag may not behave the way SKILL.md assumes (semantics differ across Claude Code versions).
- Non-interactive child session can't honor `confirm_each_step` mode (acknowledged in SKILL.md but unverified).
- Output streaming from a child session back to the parent may not display cleanly.

**Suggested fix:** Add a 4th simulation scenario with non-empty `seed_artifacts` (e.g., a local README path), have the parent skill spawn the child via Bash, capture the result. Or test interactively (see "What was NOT tested" below).

## What was NOT tested (require interactive Claude Code session — out of scope for this simulation)

These represent real gaps. They need a human-driven test before Iteration 6.

- **Trigger phrase firing.** Whether Claude Code actually invokes `vault-scaffold` on phrases like *"Set up a vault for my Python web app project"*, *"Create a knowledge base for our product team"*, *"I want to start an LLM Wiki for my reading list on AI safety"*. Description was written to be "pushy" but real-world fire-rate is unknown.
- **Interview flow UX.** Whether Claude actually asks all 7 questions in 3 grouped turns, whether the prose + AskUserQuestion mix lands cleanly in a single turn, whether users can paraphrase ("defaults are fine") and have Claude understand.
- **Confirmation gate behavior.** Whether the "type 'force' to confirm" gate actually blocks accidental overwrites, and whether case-insensitive variants are accepted as instructed.
- **Skill-directory path discovery.** Whether Claude finds `scripts/scaffold.py` from the runtime context or has to fall back to the `find` command suggested in SKILL.md.
- **Post-scaffold ingest spawn (option b).** See I5-3.
- **Generated-vault session behavior.** Whether opening Claude Code in `/tmp/vault-test-eng` and asking *"what does this project know about authentication?"* actually causes Claude to read `vault/index.md` first per the "Default behavior" section. The rendered `index.md` is correct (5 categories, all "No entries yet."), so the right answer would be something like: *"This vault doesn't have anything on authentication yet — want to ingest a source?"*

## Recommendations for Iteration 6

In priority order:

1. **Fix I5-1 by expanding `DEFAULT_CATEGORY_DESCRIPTIONS`.** Add the 9 per-domain default category names from `SKILL.md` Phase 2 to the dict. This is the only "real" bug; it would land in almost every generated vault.
2. **Run the three scenarios interactively.** A fresh Claude Code session in `/tmp`, trigger phrase, full interview, scaffold, then open Claude Code in the generated vault and try the authentication question. The structural sim says the scaffolder is correct for these inputs; what's untested is whether `vault-scaffold` *as a skill* drives this flow as written.
3. **Add a 4th scenario or extend an existing one with non-empty `seed_artifacts`** to exercise the option (b) ingest-spawn path. Verify what happens when `claude` isn't on PATH (likely on CI) so the fallback messaging actually shows up in someone's transcript.
4. **(Optional, low priority) I5-2 punctuation normalization** if you touch `build_context` for anything else.

The scaffolder itself is solid. The risks now are all in the SKILL.md → Claude Code → user-flow layer, which the structural sim cannot validate.
