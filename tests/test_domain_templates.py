"""Tests for references/domain-templates.md and its parser in scaffold.py.

Asserts every required domain section is present, each section has all six
required subsections, no subsection is empty, and every domain's trigger
examples cover all five sub-skills with at least one phrase each.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make scripts/ importable without packaging the project.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from scaffold import (  # noqa: E402  (sys.path tweak above is intentional)
    DOMAIN_TEMPLATES_PATH,
    REQUIRED_DOMAIN_SUBSECTIONS,
    parse_domain_templates,
)


REQUIRED_DOMAINS = ("engineering", "product", "research", "personal", "team", "mixed")
REQUIRED_SKILLS = ("ingest", "query", "lint", "capture-decision", "file-back")


@pytest.fixture(scope="module")
def domains() -> dict:
    assert DOMAIN_TEMPLATES_PATH.is_file(), (
        f"domain-templates.md not found at {DOMAIN_TEMPLATES_PATH}"
    )
    return parse_domain_templates(DOMAIN_TEMPLATES_PATH.read_text(encoding="utf-8"))


def test_domain_templates_file_exists() -> None:
    assert DOMAIN_TEMPLATES_PATH.is_file()


def test_all_required_domains_present(domains: dict) -> None:
    missing = [d for d in REQUIRED_DOMAINS if d not in domains]
    assert not missing, f"missing domain sections: {missing}"


@pytest.mark.parametrize("domain", REQUIRED_DOMAINS)
def test_each_domain_has_all_subsections(domains: dict, domain: str) -> None:
    section = domains[domain]
    missing = [sub for sub in REQUIRED_DOMAIN_SUBSECTIONS if sub not in section]
    assert not missing, f"{domain}: missing subsections {missing}"


@pytest.mark.parametrize("domain", REQUIRED_DOMAINS)
def test_no_subsection_is_empty(domains: dict, domain: str) -> None:
    section = domains[domain]

    assert section["default_categories"], (
        f"{domain}: default_categories is empty"
    )
    assert section["category_descriptions"], (
        f"{domain}: category_descriptions is empty"
    )
    assert section["trigger_examples"], (
        f"{domain}: trigger_examples is empty"
    )
    assert section["capture_decision_examples"], (
        f"{domain}: capture_decision_examples is empty"
    )
    assert section["custom_claude_additions"].strip(), (
        f"{domain}: custom_claude_additions is empty"
    )
    assert section["custom_default_behavior_rules"], (
        f"{domain}: custom_default_behavior_rules is empty"
    )


@pytest.mark.parametrize("domain", REQUIRED_DOMAINS)
def test_trigger_examples_cover_all_skills(domains: dict, domain: str) -> None:
    triggers = domains[domain]["trigger_examples"]
    missing_skills = [s for s in REQUIRED_SKILLS if s not in triggers]
    assert not missing_skills, (
        f"{domain}: trigger_examples missing skills {missing_skills}"
    )
    empty_skills = [s for s in REQUIRED_SKILLS if not triggers[s]]
    assert not empty_skills, (
        f"{domain}: trigger_examples for {empty_skills} are empty"
    )


@pytest.mark.parametrize("domain", REQUIRED_DOMAINS)
def test_category_descriptions_cover_default_categories(
    domains: dict, domain: str
) -> None:
    """Every category listed in 'Default categories' should also have a
    description. Catches author drift where a category gets added but no
    matching description is written."""
    section = domains[domain]
    default_cats = section["default_categories"]
    described = set(section["category_descriptions"].keys())
    missing = [c for c in default_cats if c not in described]
    assert not missing, (
        f"{domain}: categories without descriptions: {missing}"
    )
