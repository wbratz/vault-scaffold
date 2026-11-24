"""Exercise a generated vault and its local-only Git defaults."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from scaffold import build_context, init_git, load_domain_templates, scaffold, upgrade  # noqa: E402


def make_vault(target: Path) -> tuple[dict, dict]:
    config = json.loads((ROOT / "tests" / "fixtures" / "sample-config.json").read_text(encoding="utf-8"))
    config["target_path"] = str(target)
    config["custom_notes"] = "Do not ingest private-client/ or send it to a model."
    context, _warnings = build_context(config, load_domain_templates())
    scaffold(config, target, context, dry_run=False, verbose=False)
    return config, context


def test_fresh_vault_keeps_notes_local_and_includes_full_answer_loop(tmp_path: Path) -> None:
    target = tmp_path / "new-vault"
    make_vault(target)

    assert "private-client/" in (target / "LOCAL-NOTES.md").read_text(encoding="utf-8")
    assert "private-client/" not in (target / "CLAUDE.md").read_text(encoding="utf-8")
    assert "private-client/" in (target / "vault" / ".scaffold-config.json").read_text(encoding="utf-8")
    assert (target / ".claude" / "skills" / "review-answer" / "SKILL.md").is_file()
    assert "known wrong answer" in (target / "evaluation" / "README.md").read_text(encoding="utf-8")
    assert "one bounded domain" in (target / "ADOPTION.md").read_text(encoding="utf-8")
    assert "Derived graph" in (target / "SEMANTIC-LAYER.md").read_text(encoding="utf-8")


@pytest.mark.skipif(shutil.which("git") is None, reason="git unavailable")
def test_git_init_never_stages_existing_or_generated_content(tmp_path: Path) -> None:
    target = tmp_path / "existing-files"
    target.mkdir()
    (target / "unrelated.txt").write_text("leave me alone", encoding="utf-8")
    make_vault(target)
    init_git(target, dry_run=False, verbose=False)

    staged = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=target, capture_output=True, text=True, check=True)
    assert staged.stdout.strip() == ""
    head = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=target, capture_output=True, text=True)
    assert head.returncode != 0
    ignored = subprocess.run(
        ["git", "check-ignore", "raw/", "vault/.scaffold-config.json", "LOCAL-NOTES.md", "evaluation/cases/example.md"],
        cwd=target, capture_output=True, text=True, check=True,
    )
    assert len(ignored.stdout.splitlines()) == 4
    assert (target / "unrelated.txt").read_text(encoding="utf-8") == "leave me alone"


@pytest.mark.skipif(shutil.which("git") is None, reason="git unavailable")
def test_git_init_preserves_existing_staging(tmp_path: Path) -> None:
    target = tmp_path / "existing-repo"
    target.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    (target / "other.txt").write_text("already staged", encoding="utf-8")
    subprocess.run(["git", "add", "other.txt"], cwd=target, check=True)
    make_vault(target)
    init_git(target, dry_run=False, verbose=False)

    staged = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=target, capture_output=True, text=True, check=True)
    assert staged.stdout.splitlines() == ["other.txt"]


def test_upgrade_moves_legacy_notes_without_rewriting_existing_local_notes(tmp_path: Path) -> None:
    target = tmp_path / "upgrade"
    _, context = make_vault(target)
    notes = target / "LOCAL-NOTES.md"
    notes.unlink()
    (target / "CLAUDE.md").write_text("# Legacy schema\n\nDo not ingest private-client/ or send it to a model.\n", encoding="utf-8")
    (target / "ADOPTION.md").unlink()
    (target / "SEMANTIC-LAYER.md").unlink()
    (target / "evaluation" / "README.md").unlink()
    (target / ".claude" / "skills" / "review-answer" / "SKILL.md").unlink()
    raw = target / "raw" / "existing.md"
    raw.write_text("immutable evidence", encoding="utf-8")

    upgrade(target, context, yes=True, dry_run=False, verbose=False)
    assert "private-client/" in notes.read_text(encoding="utf-8")
    assert "private-client/" not in (target / "CLAUDE.md").read_text(encoding="utf-8")
    assert (target / "ADOPTION.md").is_file()
    assert (target / "SEMANTIC-LAYER.md").is_file()
    assert (target / "evaluation" / "README.md").is_file()
    assert (target / ".claude" / "skills" / "review-answer" / "SKILL.md").is_file()
    assert raw.read_text(encoding="utf-8") == "immutable evidence"

    notes.write_text("My later edit", encoding="utf-8")
    upgrade(target, context, yes=True, dry_run=False, verbose=False)
    assert notes.read_text(encoding="utf-8") == "My later edit"
