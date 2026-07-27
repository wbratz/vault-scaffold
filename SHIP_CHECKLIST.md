# Ship checklist

Run through this before tagging a public release. Items are grouped roughly by *what would embarrass you most if you skipped it*.

## Correctness

- [ ] `python scripts/package.py` exits 0 (this runs the test suite).
- [ ] All three example scenarios (engineering / product / research) scaffold cleanly from the SKILL.md interview AND from a manual `scaffold.py --config` invocation. Spot-check the rendered `CLAUDE.md` per domain for vocabulary differences.
- [ ] `scaffold.py --upgrade --yes` on an existing vault either reports "no changes" (when templates haven't moved) or applies a sensible diff and records one log entry.
- [ ] `scaffold.py --dry-run` lists files and writes none.
- [ ] Re-running `scaffold.py` without `--force` against an existing vault exits 2 with a clear message that names both conflicting paths.
- [ ] Invalid config (missing required field, bad enum, empty `categories`) exits 1 with a multi-error report; the error includes the field path.
- [ ] Bizarre but legal category names (`"ML Models"`, `"Architecture & Design"`) are slugified, a warning is printed to stderr, and the vault validates.

## Cross-platform

- [x] Tested on **macOS**. Confirmed `pathlib`, `subprocess`, template rendering, and git initialization behave correctly.
- [ ] Tested on **Linux** (likely CI / cloud machines).
- [ ] Any path comparison in tests uses `Path` not string equality so trailing slashes / case sensitivity don't trip you.
- [ ] No use of `/tmp` in code or default configs — system temp via `os.environ['TEMP']` / `tempfile.gettempdir()` only.
- [ ] No use of `\` in path literals; only `/` and `Path()`.

## Hardcoded paths and assumptions

- [ ] No hardcoded user home directory (`/Users/...`, `C:\Users\...`).
- [ ] No assumption that `python3` is on `PATH` — scripts use `sys.executable` when re-invoking Python.
- [ ] `SCAFFOLD_VERSION` in `scripts/package.py` matches what's in `CHANGELOG.md`, `README.md`, and the sample fixture's `scaffold_version` field.
- [ ] Generated `CLAUDE.md` doesn't leak any path from the developer's machine into its rendered output. (`scaffold-config.json` will contain the user's `target_path` — that's expected and theirs.)

## SKILL.md triggering

- [ ] In a clean Claude Code session (no prior context about vaults), each of these prompts fires the skill within one turn:
  - *"Set up a vault for my Python web app project."*
  - *"I want to build a personal knowledge base."*
  - *"Make a vault for this project."*
  - *"Create a knowledge base for our product team."*
- [ ] In a clean Claude Code session, an *adjacent but unrelated* prompt does NOT fire the skill (e.g., *"Tell me about vaults in cryptography"*, *"Show me my Obsidian vault config"*).
- [ ] When the skill fires, Claude actually executes the interview as written (3 phases, 7 questions, grouped per turn) instead of paraphrasing or skipping steps.
- [ ] The interview interruption handling (abort / re-ask / modify-Q3) works in practice.

## Documentation

- [ ] `README.md` install methods all work for a user who doesn't know what Claude Code is. Run through them on a fresh shell.
- [ ] `README.md` correctly explains Karpathy's LLM Wiki pattern in the first paragraph for someone who hasn't read the gist.
- [ ] Every command in `README.md` has been copy-pasted into a real shell and verified to do what the docs claim.
- [ ] `CHANGELOG.md` includes the release date and matches the version everywhere else.
- [ ] `SKILL.md` description is under ~150 words and lists the trigger phrases explicitly.
- [ ] No `TODO`, `FIXME`, `XXX`, or placeholder text in any user-visible file.

## Repository hygiene

- [ ] `LICENSE` file present (MIT or whatever you've chosen).
- [ ] `.gitignore` excludes `dist/`, `__pycache__/`, `.pytest_cache/`, `.venv/`, `.env`.
- [ ] No secrets, tokens, or personal data in any file or git history.
- [ ] Repo description on the hosting platform (GitHub etc.) matches the README opening paragraph.
- [ ] Tag the release commit: `git tag -a v0.1.1 -m "vault-scaffold v0.1.1"`.

## Package

- [ ] `dist/vault-scaffold-v<VERSION>.skill` exists and is under a reasonable size (< 200 KB at v0.1.0).
- [ ] Extracting the `.skill` zip locally and pointing Claude Code at the extracted dir loads the skill successfully (sanity check on the package structure).
- [ ] The package does NOT contain `tests/`, `.git/`, `.pytest_cache/`, `__pycache__/`, or `dist/` itself.
- [ ] The package DOES contain `SKILL.md` at the root, plus `scripts/scaffold.py`, `scripts/schema.json`, `references/domain-templates.md`, and the full `assets/` tree.

## Post-publish

- [ ] First-issue template / contribution guide (optional but appreciated by would-be contributors).
- [ ] At least one screenshot or GIF in the README showing the interview running.
- [ ] An announcement post / tweet links to the LLM Wiki gist and to the install command.
