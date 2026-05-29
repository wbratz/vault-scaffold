---
name: vault-scaffold
description: >-
  Use this skill PROACTIVELY whenever the user wants to set up, create, or
  initialize a new LLM-maintained knowledge base or "vault" — based on
  Karpathy's LLM Wiki pattern: a markdown-based, LLM-curated knowledge
  directory that compounds over time. Trigger phrases include "set up a
  vault", "create a knowledge base", "scaffold an LLM wiki", "build a
  knowledge base for my codebase", "I want to build a personal knowledge
  base", "make a vault for this project", "start a vault", "set up a
  knowledge base for my codebase", "I want a knowledge directory my AI can
  maintain". The user does NOT need to say "vault" for this to fire — any
  paraphrase implying a fresh persistent LLM-maintained knowledge directory
  should activate it.
---

# vault-scaffold

Run a short interview, build a validated config, and scaffold a new LLM-maintained vault into a directory of the user's choice. Based on Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern.

## When to use this skill

The user wants to start a new vault — a directory of markdown that Claude (or another LLM) will curate, query, and grow over time. Fire on the first turn that describes this need; don't wait for them to ask by name.

## What you'll create

A self-contained directory with a `CLAUDE.md` schema (read first by any agent), a `raw/` folder for source documents, a `vault/` folder of LLM-generated pages with one subfolder per category, an `index.md` catalog, an append-only `log.md`, and five companion skills (`ingest`, `query`, `lint`, `capture-decision`, `file-back`) under `.claude/skills/`. The whole tree is git-initialized with an initial commit.

## Workflow

### Step 1: Confirm intent and target

1. **Confirm.** One line: *"I can set up an LLM-maintained vault here — should I walk you through it? About 7 short questions, under 2 minutes."*

2. **Offer a preview.** If they hesitate, ask *"want to see the directory layout first?"* and if yes, print this tree:

   ```
   <target>/
   ├── CLAUDE.md       ← schema Claude reads first
   ├── README.md       ← human-facing entry point
   ├── raw/            ← source documents (immutable)
   ├── vault/          ← LLM-curated wiki
   │   ├── index.md, log.md
   │   └── <category>/ ← one folder per category you choose
   └── .claude/skills/ ← ingest, query, lint, capture-decision, file-back
   ```

3. **Get target path and vault name (one message, two questions).** *"Where should I scaffold it (absolute or relative path), and what should I call the vault?"*
   - Resolve any relative path to absolute before continuing.
   - If they give only a path, derive a default name from the directory basename (`acme-payments` → *"Acme Payments Vault"*) and confirm it during the Step 3 config review.

4. **Check the target before going further:**
   - **Doesn't exist** → *"Create `<absolute-path>` and scaffold into it?"* (yes/no).
   - **Exists, empty (or only `.git`)** → proceed silently.
   - **Exists, has unrelated files, no vault** → *"That directory has existing files. I'll add the vault alongside them and won't overwrite anything by default — OK?"*
   - **Already contains a vault** (both `CLAUDE.md` and `vault/` present) → require explicit overlay consent: *"There's already a vault here. Re-running will overlay the schema, README, and skills (your `raw/` and existing pages are untouched). Type 'force' to confirm."* Accept any case-insensitive match (`force`, `FORCE`, `Force`) or any unambiguous yes like `confirm`, `overwrite`, `go ahead`. Only then pass `--force` to the script in Step 4.

### Step 2: Conduct the interview

Three phases. **Ask every question in a given phase in a single turn** — don't fire them one at a time. Use `AskUserQuestion` when a question has 2–4 options; use prose when it has more options or accepts a free-form list. The whole interview should feel under 2 minutes.

**Combine mechanisms in the same turn.** Prose questions go in your response text, `AskUserQuestion` calls go in the same response. Don't split a phase across turns just because some questions are prose and others are structured.

**Phase 1 — Purpose** (Q1 + Q2 + Q3 in one turn):

- **Q1 — Primary domain.** *Engineering codebase / Product knowledge / Research / Personal knowledge / Team or org wiki / Mixed.* Maps to `domain`: `engineering | product | research | personal | team | mixed`. (Six options → prose.)
- **Q2 — Scope.** *Single repository / Single project (multi-repo) / Cross-project domain / Personal scratchpad.* Maps to `scope`: `single_repo | single_project | cross_project | personal`.
- **Q3 — Audience.** *Just me / Small team (≤5) / Larger team (>5) / Mixed.* Maps to `audience`: `solo | small_team | large_team | mixed`.

**Phase 2 — Content structure** (Q4 + Q5 in one turn):

- **Q4 — Categories.** Multi-select. Show domain-appropriate defaults based on Q1:

  | domain | suggested defaults |
  |---|---|
  | engineering | `concepts, decisions, runbooks, systems, incidents, syntheses` |
  | product | `features, personas, decisions, experiments, competitors, syntheses` |
  | research | `entities, concepts, papers, methods, syntheses` |
  | personal | `entities, concepts, decisions, syntheses` |
  | team | `entities, concepts, decisions, processes, syntheses` |
  | mixed | `concepts, decisions, entities, syntheses` |

  Accept any of: a comma-separated list (*"concepts, decisions, runbooks"*), *"all of the above"*, *"the defaults are fine"*, *"keep them all"*, or *"custom — let me specify"* followed by their own list. Use prose, not `AskUserQuestion` — the option count and paraphrase tolerance make multi-select UI a worse fit here.

  **Important — auto-include `sources`.** The scaffolder's schema requires `sources` in the category list (the `ingest` skill always writes summaries there). If the user didn't pick it, add it to the final list silently and mention it explicitly during the Step 3 config review so it's not a surprise.

- **Q5 — Seed artifacts.** *Yes — local files I'll provide paths to / Yes — URLs to fetch / No — start empty.* If they pick a "Yes", follow up in the same phase: *"Paste the paths or URLs, comma-separated."* Otherwise `seed_artifacts: []`.

**Phase 3 — Operating style** (Q6 + Q7 in one turn):

- **Q6 — Ingest interaction style.** *Confirm every write step / Confirm only the plan / Run autonomously.* Maps to `ingest_mode`: `confirm_each_step | confirm_plan | autonomous`.
- **Q7 — Custom notes** (optional, free text). *"Anything about how your team works that should be baked into the schema? Scope exclusions, naming conventions, things to never auto-ingest. Press enter to skip."* Goes into `custom_notes`; empty string is allowed.

### Step 2.5: Interview-handling behaviors

Beyond the per-phase rules above, the interview must handle these mid-flow cases gracefully:

- **Abort.** If the user says "stop", "cancel", "never mind", "actually no" (or similar) at any point before Step 4, exit cleanly: *"OK — no vault created. Run the trigger phrase again whenever you're ready."* Do not write any files.

- **Invalid target path.** If the path is malformed, points to an existing *file* (not a directory), already contains a vault, or can't be created due to permissions — explain the problem in one sentence and re-ask. Example: *"`/usr/lib/secret` looks like a file, not a directory. Where else should I scaffold?"*

- **Modify a previous answer.** If the user says "wait, change Q3", "let me redo the categories", "actually make the scope cross-project", or similar at any time before Step 4, jump back to *just that question* without re-asking the ones before it. Re-display only the affected question(s), then continue forward.

- **Custom category names with spaces or special characters.** If a Q4 answer contains spaces, capitals, ampersands, or punctuation (e.g., *"ML Models"*, *"Architecture & Design"*), the scaffolder will slugify them automatically (*"ML Models"* → `ml-models`). Show the slugified versions in the Step 3 config review explicitly: *"I'll create `ml-models/` and `architecture-design/` — sound right?"* If the user pushes back, ask them to give slug-friendly names directly.

- **Duplicate categories.** If Q4 returns duplicates (e.g., from a paraphrase like *"decisions, decisions, runbooks"*), dedupe silently and continue — the scaffolder also dedupes defensively.

- **Too many categories.** If Q4 returns more than 12 categories, flag it before Step 3: *"That's {{N}} categories — vaults with more than ~12 categories tend to be hard to navigate. Want to consolidate?"* Don't block; just nudge.

### Step 3: Build and review the config

1. Construct the JSON. Required shape (matches `scripts/schema.json`):

   ```json
   {
     "vault_name":       "<from Step 1>",
     "target_path":      "<absolute path from Step 1>",
     "domain":           "<Q1>",
     "scope":            "<Q2>",
     "audience":         "<Q3>",
     "categories":       ["<Q4 + 'sources' guaranteed present>"],
     "seed_artifacts":   ["<Q5 paths/URLs, or []>"],
     "ingest_mode":      "<Q6>",
     "custom_notes":     "<Q7 or empty string>",
     "created_at":       "<ISO 8601 with timezone, e.g. 2026-05-28T14:00:00-04:00>",
     "scaffold_version": "0.1.0"
   }
   ```

2. **Show the JSON in a fenced code block.** Call out:
   - That `sources` was added if the user didn't list it.
   - The full resolved `target_path` (so the user catches typos before any disk write).

3. Ask: *"Look right? Anything to tweak?"* If they tweak, regenerate and re-show. Only proceed when they say yes.

### Step 4: Run the scaffold script

1. **Write the config to system temp.** Filename: `vault-scaffold-config-<YYYYMMDD-HHMMSS>.json` (no colons in the timestamp — colons are invalid in Windows filenames). On Linux/macOS use `/tmp/`; on Windows use the value of `$env:TEMP` (or whatever your shell exposes).

2. **Pick the right Python command first.** The command literally named `python` doesn't exist on every system (e.g., modern macOS has `python3` only). Probe in order, taking the first whose `--version` reports 3.9 or newer:

   - `python3` (macOS, most Linux distros)
   - `py -3` (Windows, via the py launcher)
   - `python` (Windows native install, some Linux distros)

   One-liner probe:

   ```bash
   PY=""
   for cmd in "python3" "py -3" "python"; do
     if $cmd -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
       PY="$cmd"; break
     fi
   done
   ```

   If `$PY` is still empty after the probe, stop and tell the user: *"I need Python 3.9 or newer to run the scaffolder, but I couldn't find one — install Python (or add it to PATH) and re-run the trigger phrase."*

3. **Invoke the scaffolder.** The script lives at `scripts/scaffold.py` relative to this `SKILL.md` — i.e., the parent directory of this file. Claude Code exposes that path in your runtime context; if for any reason you can't find it there, locate it with `find ~/.claude ~ -path '*/vault-scaffold/scripts/scaffold.py' 2>/dev/null | head -1` (or the Windows equivalent). Use the absolute path. Pass `--verbose` always; add `--force` only if Step 1 established overlay consent:

   ```bash
   $PY "<absolute-path-to-skill-dir>/scripts/scaffold.py" \
     --config "<temp-config-path>" \
     --target "<target-path>" \
     --verbose [--force]
   ```

4. **Stream the script's output to the user as it runs** (each `wrote …` line is one file). Don't summarize until the script exits.

5. **If exit code ≠ 0:** show the stderr verbatim, do NOT try to silently repair the config. Go back to Step 3 with the user, fix the offending field, and re-run.

### Step 5: Post-scaffold

1. **Show what got created.** Run a tree listing rooted at `<target>`. Prefer `tree -L 3` if available; otherwise `find <target> -not -path '*/.git/*' | sort` (Linux/macOS) or an equivalent recursive listing on Windows. Render it in a code block.

2. **Offer to ingest a seed artifact.** If Q5 produced any paths/URLs, ask: *"Want to test the flow by ingesting `<first artifact>` now? I'll spawn a one-shot Claude Code session inside the new vault to run it."*

   If yes, run via Bash with a long timeout (ingests can take a couple of minutes):

   ```bash
   cd "<target>" && claude -p "ingest <first-artifact>"
   ```

   The child session loads the new vault's `CLAUDE.md` and `.claude/skills/ingest/SKILL.md` automatically (because its CWD is the new vault). Stream the output verbatim. When the child exits, summarize what landed: which file appeared under `raw/`, which page under `vault/sources/`, and what got appended to `vault/index.md` and `vault/log.md`.

   **Caveats — mention only if they actually bite:**
   - The child runs non-interactively (`-p`), so if the user picked `confirm_each_step` for `ingest_mode`, the child cannot pause for confirmations. It will either plow ahead or report that it can't proceed. For a test ingest this is usually fine; if the user wants the full interactive experience, suggest they re-run interactively (`cd "<target>" && claude` then say *"ingest <artifact>"*).
   - If `claude` isn't on the user's `PATH` or the `-p` flag isn't supported by their version, Bash will fail. Surface the stderr and fall back: tell the user to open a new terminal in `<target>` and run `claude` interactively.

   If no, skip and move to the closing message.

3. **Closing.** Keep it short:

   > Open Claude Code in `<target>` and try saying *"what does this project know about X?"* — Claude will read `vault/index.md` automatically and answer (or admit the vault is silent and offer to ingest something). The five skills under `.claude/skills/` activate on their own triggers; `capture-decision` will fire proactively whenever a decision surfaces in conversation.

## Behavior rules

- **Group questions per phase.** Never fire phase questions one at a time. The interview must feel under 2 minutes.
- **Accept paraphrases on multi-select.** For Q4 (categories), accept *"all of the above"*, *"defaults are fine"*, *"keep them all"*, or a comma-separated list — don't force the user back into a structured picker.
- **Resolve paths.** Convert any relative target to absolute before showing it in the config.
- **Never silently overwrite.** Always confirm before running, and re-confirm with an explicit "force" (or unambiguous equivalent) before overlaying an existing vault.
- **Don't invent schema fields.** The config shape is fixed by `scripts/schema.json`. If the user wants something that doesn't fit, put it in `custom_notes` rather than inventing keys — extra fields fail validation.
- **Tone is conversational, not bureaucratic.** Short questions, plain English.

## Failure modes to watch for

- **`jsonschema` or `jinja2` not installed.** The script will exit during import. Surface the install hint: `pip install 'jsonschema>=4.0' 'jinja2>=3.0'`.
- **`git` not in PATH.** The scaffold still succeeds and the script prints a warning. Tell the user how to commit manually: `cd <target> && git init && git add . && git commit -m "initial scaffold"`.
- **User picks zero categories.** The schema requires at least one. Push back: *"You need at least one category — usually 3-4 to start. Want the defaults for `<domain>`?"*
- **Target on a read-only filesystem or permission-denied path.** The script exits with code 3 and a clear error; relay it and ask for a writable target.
- **User's `target_path` has a typo and resolves to an unexpected place.** This is exactly why Step 3 shows the resolved absolute path. If you skip that step, the user can wipe the wrong directory with `--force`. Don't skip it.
