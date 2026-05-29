#!/usr/bin/env python3
"""vault-scaffold: generate and upgrade LLM-maintained knowledge vaults.

Two modes:

* **scaffold** (default): validate a config, render templates, lay out a new
  vault tree, git-init it.
* **upgrade** (``--upgrade``): re-render the meta files against current
  templates and apply user-approved changes to an existing vault. User
  content pages and the log body are never replaced; the log gets one
  appended entry recording the upgrade.

Exit codes:
  0  success
  1  config / domain-template / missing-input / unsupported-Python error
  2  target conflict (existing vault without --force; target is a file;
     --upgrade against a non-vault directory)
  3  file-write / permission / template-render error
"""

from __future__ import annotations

import sys

# Version guard: scaffold.py uses `from __future__ import annotations`, so
# PEP 604 (`X | Y`) and PEP 585 (`list[X]`) type hints are lazy strings at
# runtime and don't actually require 3.10/3.9. 3.9 is the practical floor
# (`dict[...]` subscript at type-hint position is fine via `__future__`).
# Bail with a clear message if we're on something older.
if sys.version_info < (3, 9):
    sys.stderr.write(
        f"error: vault-scaffold requires Python 3.9 or newer; got "
        f"{sys.version.split()[0]} at {sys.executable}.\n"
        "Re-invoke with `python3`, `py -3`, or a newer python binary.\n"
    )
    raise SystemExit(1)

import argparse
import difflib
import json
import os
import re
import subprocess
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft7Validator
except ImportError as exc:
    sys.stderr.write(
        "error: 'jsonschema' is required. Install with: pip install 'jsonschema>=4.0'\n"
    )
    raise SystemExit(1) from exc

try:
    from jinja2 import Environment, FileSystemLoader, StrictUndefined, UndefinedError
except ImportError as exc:
    sys.stderr.write(
        "error: 'jinja2' is required. Install with: pip install 'jinja2>=3.0'\n"
    )
    raise SystemExit(1) from exc


HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE / "schema.json"
ASSETS_DIR = HERE.parent / "assets"
DOMAIN_TEMPLATES_PATH = HERE.parent / "references" / "domain-templates.md"

MAX_REASONABLE_CATEGORIES = 12


DEFAULT_CATEGORY_DESCRIPTIONS: dict[str, str] = {
    "entities":  "People, projects, systems, organizations",
    "concepts":  "Ideas, patterns, technical concepts",
    "decisions": "Architectural decisions, conventions, corrections",
    "syntheses": "Cross-cutting analyses, comparisons",
    "sources":   "Summaries of ingested source documents",
    "runbooks":  "Step-by-step procedures and on-call playbooks",
}

DEFAULT_TRIGGER_EXAMPLES: dict[str, list[str]] = {
    "ingest": ["ingest <path>", "add this source", "process this article"],
    "query": ["query <question>", "what do we know about X", "explain X"],
    "lint": ["lint", "audit the vault", "find contradictions"],
    "capture-decision": [
        "let's go with X", "we'll do Y", "decided", "going with the second option",
    ],
    "file-back": ["file this", "save this to the vault", "add this as a page"],
}

SKILL_TEMPLATES: dict[str, str] = {
    "ingest": "skills/ingest.skill.template.md",
    "query": "skills/query.skill.template.md",
    "lint": "skills/lint.skill.template.md",
    "capture-decision": "skills/capture-decision.skill.template.md",
    "file-back": "skills/file-back.skill.template.md",
}

# Files the upgrade flow may rewrite. Anything not in this list is left alone.
UPGRADE_META_FILES: list[tuple[str, str]] = [
    ("CLAUDE.md.template", "CLAUDE.md"),
    ("README.md.template", "README.md"),
    ("gitignore.template", ".gitignore"),
]
for _skill_name, _template_rel in SKILL_TEMPLATES.items():
    UPGRADE_META_FILES.append(
        (_template_rel, f".claude/skills/{_skill_name}/SKILL.md")
    )

REQUIRED_DOMAIN_SUBSECTIONS = (
    "default_categories",
    "category_descriptions",
    "trigger_examples",
    "capture_decision_examples",
    "custom_claude_additions",
    "custom_default_behavior_rules",
)


class ScaffoldError(Exception):
    """User-facing error that maps to a process exit code."""

    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code


# ---------------------------------------------------------------------------
# Domain-templates parser
# ---------------------------------------------------------------------------


def parse_domain_templates(text: str) -> dict[str, dict[str, Any]]:
    """Parse references/domain-templates.md into a structured dict.

    See the file's own header for the authoring rules.
    """
    domains: dict[str, dict[str, Any]] = {}
    h2_split = re.split(r"^## (.+?)$", text, flags=re.MULTILINE)
    for i in range(1, len(h2_split), 2):
        name = h2_split[i].strip().lower()
        domains[name] = _parse_domain_section(h2_split[i + 1])
    return domains


def _parse_domain_section(text: str) -> dict[str, Any]:
    h3_split = re.split(r"^### (.+?)$", text, flags=re.MULTILINE)
    raw: dict[str, str] = {}
    for i in range(1, len(h3_split), 2):
        raw[h3_split[i].strip()] = h3_split[i + 1].strip()
    return {
        "default_categories": _parse_bullet_list(raw.get("Default categories", "")),
        "category_descriptions": _parse_category_descriptions(
            raw.get("Category descriptions", "")
        ),
        "trigger_examples": _parse_trigger_examples(
            raw.get("Trigger phrase examples", "")
        ),
        "capture_decision_examples": _parse_bullet_list(
            raw.get("Capture-decision examples", "")
        ),
        "custom_claude_additions": raw.get("Custom CLAUDE.md additions", "").strip(),
        "custom_default_behavior_rules": _parse_bullet_list(
            raw.get("Custom default-behavior rules", "")
        ),
    }


def _parse_bullet_list(text: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^- (.+?)$", text, flags=re.MULTILINE)]


def _parse_category_descriptions(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    pattern = re.compile(r"^- `?([a-z][a-z0-9_-]*)`?\s*[—–\-]\s*(.+)$")
    for line in text.splitlines():
        m = pattern.match(line.strip())
        if m:
            result[m.group(1)] = m.group(2).strip()
    return result


def _parse_trigger_examples(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    h4_split = re.split(r"^#### (.+?)$", text, flags=re.MULTILINE)
    for i in range(1, len(h4_split), 2):
        skill = h4_split[i].strip()
        phrases = [p.strip().strip('"').strip("'") for p in _parse_bullet_list(h4_split[i + 1])]
        result[skill] = phrases
    return result


# ---------------------------------------------------------------------------
# Config sanitization (slugify, dedupe, length warning) — runs BEFORE schema validation
# ---------------------------------------------------------------------------


def slugify_category(name: str) -> str:
    """Convert 'ML Models' -> 'ml-models', 'foo bar!' -> 'foo-bar'.

    Schema requires categories to match ``^[a-z][a-z0-9_-]*$``. Slugify
    ensures any reasonable user input lands inside that.
    """
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


def sanitize_config(config: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Pre-validation: slugify category names, dedupe, warn on excess.

    Returns ``(maybe-modified-config, warnings)``.
    """
    cfg = deepcopy(config)
    warnings: list[str] = []
    cats = cfg.get("categories", []) or []

    sanitized: list[str] = []
    seen: set[str] = set()
    for original in cats:
        if not isinstance(original, str):
            continue
        slug = slugify_category(original)
        if not slug:
            warnings.append(
                f"Category {original!r} could not be slugified — dropped."
            )
            continue
        if slug != original:
            warnings.append(
                f"Category {original!r} sanitized to {slug!r}."
            )
        if slug in seen:
            warnings.append(
                f"Duplicate category {slug!r} (from {original!r}) — deduped."
            )
            continue
        seen.add(slug)
        sanitized.append(slug)

    cfg["categories"] = sanitized

    if len(sanitized) > MAX_REASONABLE_CATEGORIES:
        warnings.append(
            f"You picked {len(sanitized)} categories — vaults with more than "
            f"{MAX_REASONABLE_CATEGORIES} categories tend to be hard to navigate; "
            "consider consolidating."
        )

    return cfg, warnings


# ---------------------------------------------------------------------------
# Loading & validation
# ---------------------------------------------------------------------------


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_config(config: dict[str, Any], schema: dict[str, Any]) -> None:
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(config), key=lambda e: list(e.absolute_path))
    if not errors:
        return
    lines = ["Config invalid:"]
    for err in errors:
        field = "/".join(str(p) for p in err.absolute_path) or "<root>"
        lines.append(f"  - {field}: {err.message}")
    raise ScaffoldError("\n".join(lines), exit_code=1)


def load_domain_templates() -> dict[str, dict[str, Any]]:
    if not DOMAIN_TEMPLATES_PATH.is_file():
        raise ScaffoldError(
            f"domain templates not found: {DOMAIN_TEMPLATES_PATH}", exit_code=1
        )
    return parse_domain_templates(DOMAIN_TEMPLATES_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Context building
# ---------------------------------------------------------------------------


def build_context(
    config: dict[str, Any],
    domain_templates: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[str]]:
    ctx: dict[str, Any] = deepcopy(config)
    warnings: list[str] = []

    domain = config["domain"]
    domain_data = domain_templates.get(domain, {})
    domain_cat_desc: dict[str, str] = domain_data.get("category_descriptions", {})
    domain_triggers: dict[str, list[str]] = domain_data.get("trigger_examples", {})

    cat_descriptions: dict[str, str] = {}
    for cat in config["categories"]:
        if cat in domain_cat_desc:
            cat_descriptions[cat] = domain_cat_desc[cat]
        elif cat in DEFAULT_CATEGORY_DESCRIPTIONS:
            cat_descriptions[cat] = DEFAULT_CATEGORY_DESCRIPTIONS[cat]
            warnings.append(
                f"No domain-specific description for category {cat!r} — using generic default."
            )
        else:
            cat_descriptions[cat] = (
                f"User-defined category: {cat.replace('-', ' ').replace('_', ' ')}"
            )
            warnings.append(
                f"No domain-specific description for category {cat!r} — using user-defined fallback."
            )
    ctx["category_descriptions"] = cat_descriptions

    triggers = deepcopy(DEFAULT_TRIGGER_EXAMPLES)
    for skill, phrases in domain_triggers.items():
        if phrases:
            triggers[skill] = phrases
    ctx["trigger_examples"] = triggers

    ctx["domain_custom_additions"] = domain_data.get("custom_claude_additions", "")
    ctx["domain_default_behavior_rules"] = domain_data.get(
        "custom_default_behavior_rules", []
    )

    return ctx, warnings


# ---------------------------------------------------------------------------
# Target safety
# ---------------------------------------------------------------------------


def check_target(target: Path, force: bool) -> None:
    """Refuse unsafe targets for fresh scaffolding."""
    if target.exists():
        if target.is_file():
            raise ScaffoldError(
                f"target is a file, not a directory: {target}",
                exit_code=2,
            )
        has_vault = (target / "CLAUDE.md").exists() and (target / "vault").is_dir()
        if has_vault and not force:
            raise ScaffoldError(
                f"target already contains a vault: {target}\n"
                f"  found: {target / 'CLAUDE.md'}\n"
                f"  found: {target / 'vault'}/\n"
                "Re-run with --force to overlay files (does NOT delete the existing\n"
                "tree), or with --upgrade to interactively update meta files only.",
                exit_code=2,
            )


def check_upgrade_target(target: Path) -> None:
    """For --upgrade: the target MUST already be a vault."""
    if not target.exists():
        raise ScaffoldError(
            f"--upgrade target does not exist: {target}", exit_code=2
        )
    if target.is_file():
        raise ScaffoldError(
            f"--upgrade target is a file, not a directory: {target}", exit_code=2
        )
    if not (target / "CLAUDE.md").exists() or not (target / "vault").is_dir():
        raise ScaffoldError(
            f"--upgrade target does not look like a vault (missing CLAUDE.md or vault/): {target}",
            exit_code=2,
        )


# ---------------------------------------------------------------------------
# Rendering & writing
# ---------------------------------------------------------------------------


def make_jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(ASSETS_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
        autoescape=False,
    )


def render_template(env: Environment, template_rel: str, ctx: dict[str, Any]) -> str:
    try:
        return env.get_template(template_rel).render(**ctx)
    except UndefinedError as exc:
        raise ScaffoldError(
            f"template {template_rel!r} references an undefined variable: {exc.message}",
            exit_code=3,
        ) from exc


def write_text(path: Path, content: str, *, dry_run: bool, verbose: bool) -> None:
    if dry_run:
        print(f"  [dry-run] write {path} ({len(content)} bytes)")
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except PermissionError as exc:
        raise ScaffoldError(
            f"permission denied writing {path}: {exc}", exit_code=3
        ) from exc
    except OSError as exc:
        raise ScaffoldError(f"failed to write {path}: {exc}", exit_code=3) from exc
    if verbose:
        print(f"  wrote {path} ({len(content)} bytes)")


def write_gitkeep(path: Path, *, dry_run: bool, verbose: bool) -> None:
    write_text(path, "", dry_run=dry_run, verbose=verbose)


# ---------------------------------------------------------------------------
# Fresh scaffold
# ---------------------------------------------------------------------------


def scaffold(
    config: dict[str, Any],
    target: Path,
    ctx: dict[str, Any],
    *,
    dry_run: bool,
    verbose: bool,
) -> list[Path]:
    env = make_jinja_env()
    written: list[Path] = []

    def _write(p: Path, content: str) -> None:
        write_text(p, content, dry_run=dry_run, verbose=verbose)
        written.append(p)

    def _gitkeep(p: Path) -> None:
        write_gitkeep(p, dry_run=dry_run, verbose=verbose)
        written.append(p)

    _write(target / "CLAUDE.md", render_template(env, "CLAUDE.md.template", ctx))
    _write(target / "README.md", render_template(env, "README.md.template", ctx))
    _write(target / ".gitignore", render_template(env, "gitignore.template", ctx))

    _gitkeep(target / "raw" / ".gitkeep")

    _write(target / "vault" / "index.md", render_template(env, "index.md.template", ctx))
    _write(target / "vault" / "log.md", render_template(env, "log.md.template", ctx))
    _write(
        target / "vault" / ".scaffold-config.json",
        json.dumps(config, indent=2, sort_keys=True) + "\n",
    )

    for cat in config["categories"]:
        _gitkeep(target / "vault" / cat / ".gitkeep")

    for skill_name, template_rel in SKILL_TEMPLATES.items():
        _write(
            target / ".claude" / "skills" / skill_name / "SKILL.md",
            render_template(env, template_rel, ctx),
        )

    return written


# ---------------------------------------------------------------------------
# Upgrade mode
# ---------------------------------------------------------------------------


def _ask_yes_no(prompt: str) -> bool:
    """Ask y/N via stdin. Default no on EOF or empty input."""
    try:
        ans = input(f"  {prompt} [y/N] ").strip().lower()
    except EOFError:
        return False
    return ans in ("y", "yes")


def _prepend_log_entry(log_path: Path, entry: str) -> None:
    """Insert a log entry before the most recent existing entry (or at the end if none)."""
    old = log_path.read_text(encoding="utf-8")
    m = re.search(r"^## \[", old, flags=re.MULTILINE)
    if m:
        new = old[: m.start()] + entry + old[m.start() :]
    else:
        new = old.rstrip() + "\n\n" + entry + "\n"
    log_path.write_text(new, encoding="utf-8")


def upgrade(
    target: Path,
    ctx: dict[str, Any],
    *,
    yes: bool,
    dry_run: bool,
    verbose: bool,
) -> list[Path]:
    """Re-render meta files; apply user-approved changes to existing vault.

    Never touches vault/<category>/, raw/, or the body of vault/index.md and
    vault/log.md. Appends one upgrade entry to vault/log.md.
    """
    env = make_jinja_env()
    updated: list[Path] = []
    summary_lines: list[str] = []

    print(f"\nUpgrade plan for {target}:")
    for template_rel, rel_out in UPGRADE_META_FILES:
        new_content = render_template(env, template_rel, ctx)
        target_file = target / rel_out

        if not target_file.exists():
            print(f"\n[NEW] {rel_out}")
            if yes or _ask_yes_no(f"Create {rel_out}?"):
                write_text(target_file, new_content, dry_run=dry_run, verbose=verbose)
                updated.append(target_file)
                summary_lines.append(f"created {rel_out}")
            continue

        old_content = target_file.read_text(encoding="utf-8")
        if old_content == new_content:
            if verbose:
                print(f"[unchanged] {rel_out}")
            continue

        print(f"\n[CHANGED] {rel_out}")
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"{rel_out} (existing)",
            tofile=f"{rel_out} (upgraded)",
            n=2,
        )
        sys.stdout.writelines(diff)

        if yes or _ask_yes_no(f"Apply this change to {rel_out}?"):
            write_text(target_file, new_content, dry_run=dry_run, verbose=verbose)
            updated.append(target_file)
            summary_lines.append(f"updated {rel_out}")

    # Append a log entry recording the upgrade
    log_path = target / "vault" / "log.md"
    if updated and not dry_run and log_path.exists():
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        version = ctx.get("scaffold_version", "?")
        entry = (
            f"## [{now}] upgrade | vault-scaffold v{version} ({len(updated)} files)\n\n"
            f"{', '.join(summary_lines)}.\n"
        )
        _prepend_log_entry(log_path, entry)
        if verbose:
            print(f"  appended log entry to {log_path}")

    print()
    if updated:
        print(f"Upgrade applied {len(updated)} file(s):")
        for p in updated:
            print(f"  - {p.relative_to(target)}")
    else:
        print("No changes applied — vault is already in sync with current templates.")
    return updated


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------


def init_git(
    target: Path,
    scaffold_version: str,
    *,
    dry_run: bool,
    verbose: bool,
) -> None:
    msg = f"vault: initial scaffold via vault-scaffold v{scaffold_version}"
    if dry_run:
        print(f"  [dry-run] git init {target}")
        print(f'  [dry-run] git commit -m "{msg}"')
        return
    try:
        if not (target / ".git").is_dir():
            subprocess.run(["git", "init", "-q"], cwd=target, check=True)
            if verbose:
                print(f"  git init {target}")
        subprocess.run(["git", "add", "."], cwd=target, check=True)
        result = subprocess.run(
            ["git", "commit", "-q", "-m", msg],
            cwd=target, capture_output=True, text=True,
        )
        if result.returncode != 0:
            sys.stderr.write(
                "warning: git commit failed (the scaffold was created successfully).\n"
                f"  git stderr: {result.stderr.strip() or '(empty)'}\n"
                "  If this is a missing user.name/user.email, set those and run:\n"
                f'    cd {target} && git commit -m "{msg}"\n'
            )
            return
        if verbose:
            print(f'  git commit -m "{msg}"')
    except FileNotFoundError:
        sys.stderr.write("warning: 'git' not found in PATH; skipping git init/commit\n")
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(f"warning: git operation failed: {exc}\n")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def print_summary(target: Path, ctx: dict[str, Any], files: list[Path], *, dry_run: bool) -> None:
    verb = "Would create" if dry_run else "Created"
    print()
    print(f"{verb} vault: {ctx['vault_name']}")
    print(f"  target:     {target}")
    print(f"  domain:     {ctx['domain']}")
    print(f"  scope:      {ctx['scope']}")
    print(f"  categories: {', '.join(ctx['categories'])}")
    print(f"  files:      {len(files)}")
    print()
    print("Next steps:")
    print(f"  cd {target}")
    print("  cat CLAUDE.md                 # read the schema")
    print('  # then in Claude: "ingest <path-or-url>" to add your first source')


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="vault-scaffold",
        description="Scaffold or upgrade an LLM-maintained vault.",
    )
    p.add_argument("--config", type=Path, required=False,
                   help="Path to a JSON config. Required for fresh scaffold; "
                        "optional for --upgrade (defaults to <target>/vault/.scaffold-config.json).")
    p.add_argument("--target", required=True, type=Path)
    p.add_argument("--force", action="store_true",
                   help="Overlay files onto an existing vault (fresh scaffold).")
    p.add_argument("--upgrade", action="store_true",
                   help="Re-render meta files against current templates and "
                        "apply user-approved changes to an existing vault.")
    p.add_argument("--yes", action="store_true",
                   help="With --upgrade: auto-accept every proposed change.")
    p.add_argument("--dry-run", action="store_true",
                   help="Print actions without writing.")
    p.add_argument("--no-git", action="store_true",
                   help="Skip git init / initial commit (fresh scaffold only).")
    p.add_argument("--verbose", action="store_true",
                   help="Print every file written.")
    args = p.parse_args(argv)

    if not args.upgrade and args.config is None:
        p.error("--config is required (unless --upgrade is set)")
    if args.force and args.upgrade:
        p.error("--force and --upgrade are mutually exclusive")

    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if not SCHEMA_PATH.is_file():
            raise ScaffoldError(f"schema not found: {SCHEMA_PATH}", exit_code=1)

        # ---- Upgrade flow ----
        if args.upgrade:
            check_upgrade_target(args.target)
            config_path = (
                args.config
                if args.config is not None
                else args.target / "vault" / ".scaffold-config.json"
            )
            if not config_path.is_file():
                raise ScaffoldError(
                    f"upgrade config not found: {config_path}", exit_code=1
                )

            schema = load_json(SCHEMA_PATH)
            raw_config = load_json(config_path)
            config, sanitize_warnings = sanitize_config(raw_config)
            for w in sanitize_warnings:
                sys.stderr.write(f"warning: {w}\n")
            validate_config(config, schema)

            domain_templates = load_domain_templates()
            if config["domain"] not in domain_templates:
                raise ScaffoldError(
                    f"no domain template for {config['domain']!r}. "
                    f"Available: {sorted(domain_templates.keys())}",
                    exit_code=1,
                )

            if args.verbose:
                d = domain_templates[config["domain"]]
                print(
                    f"  loaded domain template: {config['domain']!r} "
                    f"({len(d['default_categories'])} default categories, "
                    f"{len(d['category_descriptions'])} category descriptions, "
                    f"{len(d['trigger_examples'])} skill trigger sets, "
                    f"{len(d['custom_default_behavior_rules'])} behavior rules)"
                )

            ctx, warnings = build_context(config, domain_templates)
            for w in warnings:
                sys.stderr.write(f"warning: {w}\n")

            upgrade(args.target, ctx,
                    yes=args.yes, dry_run=args.dry_run, verbose=args.verbose)
            return 0

        # ---- Fresh scaffold flow ----
        if not args.config.is_file():
            raise ScaffoldError(f"config not found: {args.config}", exit_code=1)

        schema = load_json(SCHEMA_PATH)
        raw_config = load_json(args.config)
        config, sanitize_warnings = sanitize_config(raw_config)
        for w in sanitize_warnings:
            sys.stderr.write(f"warning: {w}\n")
        validate_config(config, schema)

        domain_templates = load_domain_templates()
        if config["domain"] not in domain_templates:
            raise ScaffoldError(
                f"no domain template for {config['domain']!r}. "
                f"Available: {sorted(domain_templates.keys())}",
                exit_code=1,
            )

        if args.verbose:
            d = domain_templates[config["domain"]]
            print(
                f"  loaded domain template: {config['domain']!r} "
                f"({len(d['default_categories'])} default categories, "
                f"{len(d['category_descriptions'])} category descriptions, "
                f"{len(d['trigger_examples'])} skill trigger sets, "
                f"{len(d['custom_default_behavior_rules'])} behavior rules)"
            )

        check_target(args.target, args.force)
        if args.force and (args.target / "CLAUDE.md").exists():
            sys.stderr.write(
                f"warning: --force given; overlaying files at {args.target}\n"
            )

        ctx, warnings = build_context(config, domain_templates)
        for w in warnings:
            sys.stderr.write(f"warning: {w}\n")

        if args.dry_run:
            print("DRY RUN — no files will be written.")

        files = scaffold(
            config, args.target, ctx,
            dry_run=args.dry_run, verbose=args.verbose,
        )

        if not args.no_git:
            init_git(
                args.target,
                config["scaffold_version"],
                dry_run=args.dry_run, verbose=args.verbose,
            )
        elif args.verbose:
            print("  [skip] git init/commit (--no-git)")

        print_summary(args.target, ctx, files, dry_run=args.dry_run)
        return 0

    except ScaffoldError as exc:
        sys.stderr.write(f"{exc}\n")
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
