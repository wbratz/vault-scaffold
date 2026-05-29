#!/usr/bin/env python3
"""Build a distributable .skill package for vault-scaffold.

Pipeline:
  1. Run the test suite. Bail on failure.
  2. Zip the necessary files into dist/vault-scaffold-v<VERSION>.skill.
  3. Verify the resulting zip contains the required entries.

The .skill file is a zip with SKILL.md at the root; other paths are
preserved relative to the project root. Development-only files (tests/,
caches, dist itself, VCS metadata) are excluded.
"""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
VERSION = "0.1.0"


# Files / directories that go into the package (paths are relative to ROOT).
# Order doesn't matter; everything is dedup'd into a set of files.
INCLUDE: list[str] = [
    "SKILL.md",
    "README.md",
    "CHANGELOG.md",
    "assets",          # all templates
    "references",      # domain-templates.md (+ stubs)
    "scripts/scaffold.py",
    "scripts/schema.json",
]

# Anything matching one of these path-parts is excluded.
EXCLUDE_PARTS: set[str] = {
    "__pycache__", ".pytest_cache", ".git", ".github",
    "dist", "tests", "node_modules", ".venv", "venv", ".idea", ".vscode",
}

# Required files inside the final zip — verification fails if any are missing.
REQUIRED_IN_PACKAGE: list[str] = [
    "SKILL.md",
    "scripts/scaffold.py",
    "scripts/schema.json",
    "references/domain-templates.md",
    "assets/CLAUDE.md.template",
    "assets/skills/ingest.skill.template.md",
    "assets/skills/query.skill.template.md",
    "assets/skills/lint.skill.template.md",
    "assets/skills/capture-decision.skill.template.md",
    "assets/skills/file-back.skill.template.md",
]


def should_include(path: Path) -> bool:
    return not any(part in EXCLUDE_PARTS or part.endswith(".pyc") for part in path.parts)


def run_tests() -> None:
    print("== running tests ==")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(ROOT / "tests"), "-q", "--tb=short"],
        cwd=ROOT,
    )
    if result.returncode != 0:
        sys.stderr.write("\nERROR: tests failed; aborting package build.\n")
        sys.exit(1)
    print()


def collect_files() -> list[Path]:
    files: list[Path] = []
    for item in INCLUDE:
        src = ROOT / item
        if not src.exists():
            sys.stderr.write(f"warning: INCLUDE entry not found, skipping: {item}\n")
            continue
        if src.is_file():
            if should_include(src):
                files.append(src)
        else:
            for f in src.rglob("*"):
                if f.is_file() and should_include(f):
                    files.append(f)
    # Dedup while preserving order
    seen: set[Path] = set()
    deduped: list[Path] = []
    for f in files:
        if f not in seen:
            seen.add(f)
            deduped.append(f)
    return sorted(deduped)


def build_skill() -> Path:
    DIST.mkdir(exist_ok=True)
    out = DIST / f"vault-scaffold-v{VERSION}.skill"
    if out.exists():
        out.unlink()

    files = collect_files()
    print(f"== packaging {len(files)} files into {out.name} ==")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            arcname = f.relative_to(ROOT).as_posix()
            zf.write(f, arcname)
    return out


def verify(pkg: Path) -> None:
    print(f"\n== verifying {pkg.name} ==")
    with zipfile.ZipFile(pkg) as zf:
        names = sorted(zf.namelist())
        # Smoke-test the zip itself
        bad = zf.testzip()
        if bad is not None:
            sys.stderr.write(f"ERROR: corrupt entry in package: {bad}\n")
            sys.exit(1)

    missing = [r for r in REQUIRED_IN_PACKAGE if r not in names]
    if missing:
        sys.stderr.write("ERROR: package missing required files:\n")
        for m in missing:
            sys.stderr.write(f"  - {m}\n")
        sys.exit(1)

    print(f"  entries: {len(names)}")
    print(f"  size:    {pkg.stat().st_size:,} bytes")
    print(f"  path:    {pkg}")
    print("\n[OK] package valid.")


def main() -> int:
    run_tests()
    pkg = build_skill()
    verify(pkg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
