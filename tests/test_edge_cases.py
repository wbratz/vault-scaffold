"""Edge-case tests for the scaffolder.

Covers category slugification, dedupe, navigation-difficulty warning, and
the target-is-a-file refusal in check_target. Permission tests are
deliberately omitted — they're flaky cross-platform.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from scaffold import (  # noqa: E402
    MAX_REASONABLE_CATEGORIES,
    ScaffoldError,
    check_target,
    sanitize_config,
    slugify_category,
)


# ---------------------------------------------------------------------------
# slugify_category
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("concepts", "concepts"),                  # already-slug, untouched
        ("ML Models", "ml-models"),                # spaces + capitals
        ("Architecture & Design", "architecture-design"),  # ampersand
        ("foo bar!", "foo-bar"),                   # punctuation
        ("  hello  ", "hello"),                    # surrounding whitespace
        ("foo___bar", "foo-bar"),                  # underscores collapsed
        ("FOO-BAR", "foo-bar"),                    # case lowered, hyphens kept
        ("Décisions", "d-cisions"),                # non-ASCII -> hyphen (lossy but slug-safe)
        ("---", ""),                               # pure-separator input -> empty
        ("", ""),                                  # empty input -> empty
    ],
)
def test_slugify_category(raw: str, expected: str) -> None:
    assert slugify_category(raw) == expected


# ---------------------------------------------------------------------------
# sanitize_config
# ---------------------------------------------------------------------------


def _make_config(categories: list[str]) -> dict:
    return {
        "vault_name": "Test",
        "target_path": "/tmp/test",
        "domain": "engineering",
        "scope": "single_repo",
        "audience": "solo",
        "categories": categories,
        "seed_artifacts": [],
        "ingest_mode": "autonomous",
        "custom_notes": "",
        "created_at": "2026-05-28T00:00:00-04:00",
        "scaffold_version": "0.1.0",
    }


def test_sanitize_slugifies_with_warning() -> None:
    cfg, warns = sanitize_config(_make_config(["ML Models", "sources"]))
    assert cfg["categories"] == ["ml-models", "sources"]
    assert any("'ML Models'" in w and "'ml-models'" in w for w in warns)


def test_sanitize_dedupes_with_warning() -> None:
    cfg, warns = sanitize_config(_make_config(["decisions", "Decisions", "sources"]))
    # 'decisions' and 'Decisions' both slug to 'decisions' -> dedup'd
    assert cfg["categories"] == ["decisions", "sources"]
    assert any("Duplicate category" in w for w in warns)


def test_sanitize_dedupes_after_slugify() -> None:
    cfg, warns = sanitize_config(_make_config(["ML Models", "ml models", "sources"]))
    assert cfg["categories"] == ["ml-models", "sources"]
    assert any("Duplicate category" in w for w in warns)


def test_sanitize_drops_empty_slugs() -> None:
    cfg, warns = sanitize_config(_make_config(["---", "sources"]))
    assert cfg["categories"] == ["sources"]
    assert any("could not be slugified" in w for w in warns)


def test_sanitize_no_warnings_for_clean_input() -> None:
    cfg, warns = sanitize_config(_make_config(["concepts", "decisions", "sources"]))
    assert cfg["categories"] == ["concepts", "decisions", "sources"]
    assert warns == []


def test_sanitize_warns_on_excess_categories() -> None:
    many = [f"cat{i}" for i in range(MAX_REASONABLE_CATEGORIES + 1)]
    cfg, warns = sanitize_config(_make_config(many + ["sources"]))
    assert any("hard to navigate" in w for w in warns)


def test_sanitize_does_not_warn_at_exactly_max() -> None:
    cats = [f"cat{i}" for i in range(MAX_REASONABLE_CATEGORIES)]
    _, warns = sanitize_config(_make_config(cats))
    assert not any("hard to navigate" in w for w in warns)


# ---------------------------------------------------------------------------
# check_target
# ---------------------------------------------------------------------------


def test_check_target_refuses_file(tmp_path: Path) -> None:
    f = tmp_path / "not-a-dir"
    f.write_text("hi", encoding="utf-8")
    with pytest.raises(ScaffoldError) as exc:
        check_target(f, force=False)
    assert exc.value.exit_code == 2
    assert "file, not a directory" in str(exc.value)


def test_check_target_allows_missing_directory(tmp_path: Path) -> None:
    # Should NOT raise — the scaffold creates parents on write.
    check_target(tmp_path / "does-not-exist", force=False)


def test_check_target_allows_empty_directory(tmp_path: Path) -> None:
    # Empty dir is fine for fresh scaffold.
    check_target(tmp_path, force=False)


def test_check_target_refuses_existing_vault_without_force(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# vault", encoding="utf-8")
    (tmp_path / "vault").mkdir()
    with pytest.raises(ScaffoldError) as exc:
        check_target(tmp_path, force=False)
    assert exc.value.exit_code == 2
    assert "already contains a vault" in str(exc.value)


def test_check_target_allows_existing_vault_with_force(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# vault", encoding="utf-8")
    (tmp_path / "vault").mkdir()
    check_target(tmp_path, force=True)  # should not raise


def test_check_target_allows_dir_with_unrelated_files(tmp_path: Path) -> None:
    (tmp_path / "some-other-file.txt").write_text("hi", encoding="utf-8")
    check_target(tmp_path, force=False)  # should not raise
