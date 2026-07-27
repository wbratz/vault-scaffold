# Changelog

All notable changes to `vault-scaffold` are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the project uses [semantic versioning](https://semver.org/).

Iteration markers in parentheses refer to the development session that produced each change set.

---

## [Unreleased]

### Fixed

- README install section corrected. `claude skills install <pkg>.skill` is not a real Claude Code CLI subcommand. Direct clone and `.skill` extraction remain supported; marketplace installation is documented in the 0.1.1 release notes.

- **Python invocation portability.** SKILL.md previously hardcoded `python` for invoking `scripts/scaffold.py`, which fails on systems where the binary is `python3` (modern macOS) or `py` (Windows-only py launcher). SKILL.md now probes for `python3`, `py -3`, then `python` in order, using the first that reports Python 3.9+. `scripts/scaffold.py` gained a top-level version guard so an unsupported interpreter exits 1 with a clear actionable message instead of a cryptic `SyntaxError` or `ImportError`. Added a `#!/usr/bin/env python3` shebang.

### Documented

- New "Where this runs" section in README clarifying that `vault-scaffold` is CLI-first: generated vaults live on the user's real filesystem and are meant to be opened in subsequent CLI sessions. The desktop app installs the skill fine but scaffolds into its sandboxed VM, so vaults created there don't persist between sessions — useful for demos, not for vaults the user wants to keep.

- README dependency floor corrected from Python 3.10 to Python 3.9 (the actual minimum, thanks to `from __future__ import annotations` deferring all type-hint syntax to strings). Added explicit `python3 -m pip install` vs `py -3 -m pip install` guidance for macOS/Linux vs Windows.

---

## [0.1.1] — 2026-07-27

### Fixed

- Added a root `.claude-plugin/marketplace.json`, making the public GitHub repository installable through Claude Code's supported two-step marketplace flow.
- Replaced the invalid `/plugin install <owner>/<repo>` documentation with `/plugin marketplace add wbratz/vault-scaffold` followed by `/plugin install vault-scaffold@wbratz-vault-tools`.
- Documented the non-plugin path explicitly: `SKILL.md` remains a portable interview and execution contract for any local file-reading agent that can run the scaffolder.
- Removed domain-example placeholders from generated query-skill metadata so stricter cross-agent skill validators accept every scaffolded skill.
- Confirmed the scaffold and git initialization flow on macOS.

---

## [0.1.0] — 2026-05-28

First public release. Six iterations of build + harden.

### Added

- **Project skeleton and config contract** (Iter 1)
  - JSON Schema (draft-07) defining the 11 required config fields: `vault_name`, `target_path`, `domain`, `scope`, `audience`, `categories`, `seed_artifacts`, `ingest_mode`, `custom_notes`, `created_at`, `scaffold_version`.
  - Stub `scaffold.py` (argparse + validation only).
  - Sample fixture for testing.
- **Template content** (Iter 2)
  - `CLAUDE.md` template with default-behavior section, read order, folder map, page categories, conventions, ingest mode.
  - Five companion skill templates (`ingest`, `query`, `lint`, `capture-decision`, `file-back`) with full workflows and YAML frontmatter.
  - `index.md`, `log.md`, `README.md`, `.gitignore` templates.
- **Schema hardening** (Iter 2.5)
  - Schema now requires `sources` in `categories` (the `ingest` skill writes there; missing it caused silent breakage).
  - Enum values are humanized in rendered prose (`single_repo` → "single repo") via Jinja `replace` filter.
  - "Common invocations" section added to `CLAUDE.md` rendering each skill's trigger phrases.
  - `User notes` renamed to `Operational notes`, elevated to right after `Default behavior`, and given explicit "honor on every write" weight.
  - `ingest` skill gained a Step 0 that re-reads `Operational notes` for scope exclusions before any write.
- **Real scaffolding logic** (Iter 3)
  - Jinja2 rendering with `keep_trailing_newline=True`, `trim_blocks=True`, `lstrip_blocks=True`, `StrictUndefined` (unfilled placeholders raise at render time, not silently render as empty).
  - Target safety: refuses to overwrite an existing vault without `--force`.
  - CLI: `--config`, `--target`, `--force`, `--dry-run`, `--no-git`, `--verbose`.
  - Git init and initial commit (warning, not fatal, if git is unavailable).
  - Per-domain default category descriptions and trigger examples merged with user config.
  - Fixed two Jinja whitespace bugs caught during validation: skill-frontmatter YAML was being broken by `lstrip_blocks` (fixed with `{%+ for %}`); CLAUDE.md "Common invocations" bullets ran together because `trim_blocks` ate the inner newline (fixed with `{% endfor +%}`).
- **Pushy SKILL.md** (Iter 4)
  - Skill entry point with a "PROACTIVELY" description and ~9 trigger phrases.
  - Three-phase interview (7 questions, target <2 min).
  - Confirmation gates before every disk write (target creation, vault overwrite, config approval).
  - Post-scaffold "test the flow now" path that spawns a child `claude -p "ingest <artifact>"` session in the new vault.
- **End-to-end validation** (Iter 5)
  - Three scenarios (engineering, product, research) scaffolded and verified for structure, categories, sub-skill content, config-snapshot fidelity, git log.
  - Found and documented issue I5-1: fallback category description was tautological ("User-defined category: features" provided no info).
- **Domain templates** (Iter 6)
  - `references/domain-templates.md` with six domains × six subsections each: default categories, category descriptions, trigger phrase examples (per sub-skill, in domain vernacular), capture-decision examples, custom CLAUDE.md additions, custom default-behavior rules.
  - Parser in `scaffold.py` (`parse_domain_templates`).
  - Build-context layering: domain → generic → user-defined fallback (with stderr warning).
  - Pytest suite (`tests/test_domain_templates.py`) covering presence, completeness, and cross-skill coverage — 26 parametrized tests.
  - `--verbose` now logs which domain template was loaded and how many entries it contains.
  - Fixed I5-1: per-domain templates now provide concrete category descriptions instead of tautological fallbacks.

### Added (Iter 7 — hardening and packaging)

- **Edge case handling in `scaffold.py`:**
  - Target-is-a-file detected before any write (exit 2).
  - Permission errors during writes surface as exit 3 with a clear message.
  - Categories sanitized to slugs pre-validation ("ML Models" → "ml-models", warning).
  - Duplicate categories deduped with a warning.
  - More than 12 categories produces a navigation-difficulty warning.
- **Interview-handling behaviors in `SKILL.md`:**
  - Abort recognition ("stop", "cancel", "never mind").
  - Invalid-path re-ask flow.
  - "Modify Q3" / "change the categories" jump-back support.
  - Confirmation when slugification changes a category name.
  - Dedupe and >12-category nudge surfaced in Step 3 review.
- **Upgrade mode** (`--upgrade`):
  - Re-renders only meta files (`CLAUDE.md`, `README.md`, `.gitignore`, 5× `SKILL.md`).
  - Per-file unified-diff display with y/N confirmation (`--yes` to auto-accept).
  - User content (`vault/<category>/`, `raw/`, body of `vault/index.md` and `vault/log.md`) is never touched.
  - A single entry is prepended to `vault/log.md` recording the upgrade.
- **Packaging:** `scripts/package.py` runs the tests, zips the project into `dist/vault-scaffold-v<VERSION>.skill`, and verifies required files are present.
- **Edge-case test suite:** `tests/test_edge_cases.py` covers slugification, dedupe, and the navigation warning.
- **README rewrite** with three install methods, full usage example, customization map, and a versioning policy.
- **Ship checklist** (`SHIP_CHECKLIST.md`) documenting what to verify before each public release.

### Known limitations

- **Interactive UX of the SKILL.md flow has only been validated structurally** (configs constructed manually and run through `scaffold.py`). No end-to-end interactive test of the trigger-phrase firing or interview flow has been recorded yet. See `tests/issues-iteration-5.md` for the human-driven test checklist.
- **Post-scaffold `claude -p "ingest <artifact>"` spawn path** is described in the SKILL.md but has never been exercised because every test scenario had empty `seed_artifacts`.
- **Tested only on Windows** (developer's environment). macOS and Linux behavior is not yet confirmed — `pathlib` and `subprocess` usage should be portable, but no actual run on those platforms has been done.
