# vault-scaffold

**A Claude Code skill that scaffolds LLM-maintained "vault" knowledge bases.**

Based on [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern: a persistent, markdown-based knowledge directory that an LLM curates, queries, and grows over time. Instead of re-deriving answers from raw sources on every query (RAG-style), the vault is a compounding artifact where summaries, decisions, entity pages, and syntheses accumulate.

`vault-scaffold` runs a short interview (~7 questions), validates the answers, and lays out a ready-to-use vault: schema (`CLAUDE.md`), seed indices, five companion skills (`ingest`, `query`, `lint`, `capture-decision`, `file-back`), and an initial git commit. Six built-in domain templates (engineering, product, research, personal, team, mixed) customize the vault's vocabulary and rules.

---

## Install

`vault-scaffold` is a Claude Code skill — install it where Claude Code will discover it. Three current options, listed in the order you should reach for them.

### a) Via `/plugin install` from a public GitHub repo (canonical, once published)

In any Claude Code session:

```
/plugin install <owner>/vault-scaffold
```

This is the path most users will expect — Claude Code's plugin/skill ecosystem standardizes on `/plugin install` from a GitHub repo or marketplace. Use this once your fork or our official repo is public.

### b) Direct git clone (works today, no marketplace dependency)

User-global — skill becomes available in every Claude Code session on your machine:

```bash
git clone https://github.com/<owner>/vault-scaffold.git ~/.claude/skills/vault-scaffold
```

Project-scoped — only loads when Claude Code starts in this project's root:

```bash
git clone https://github.com/<owner>/vault-scaffold.git .claude/skills/vault-scaffold
```

Update later with `git -C <path> pull`.

### c) From a built `.skill` package

Build one with `python scripts/package.py` (output lands in `dist/`), or download a release. The `.skill` file is just a zip:

```bash
unzip vault-scaffold-v0.1.0.skill -d ~/.claude/skills/
# verify SKILL.md ends up one level deep, not nested:
ls ~/.claude/skills/vault-scaffold/SKILL.md
```

### After install

**Restart Claude Code** so the skill loader picks up the new skill. Then test it in a fresh session by saying something like *"set up a vault for my Python project"* — the trigger phrase should fire the interview.

### Runtime dependencies

The scaffold script needs Python 3.9 or newer plus two libraries:

```bash
# macOS / Linux:
python3 -m pip install 'jsonschema>=4.0' 'jinja2>=3.0'

# Windows (via the py launcher):
py -3 -m pip install 'jsonschema>=4.0' 'jinja2>=3.0'
```

The skill auto-detects whether your system's Python is invoked as `python3`, `py -3`, or `python` and picks the first one that reports a supported version. Install the dependencies into whichever interpreter that probe selects.

## Where this runs

`vault-scaffold` is built for **Claude Code CLI**, where the generated vault lives on your actual local filesystem and is opened in subsequent Claude Code sessions started from the vault's directory.

The skill also installs in the **Claude desktop app**, but desktop sessions run in a sandboxed VM that resets between turns — a vault scaffolded inside the app exists only for that session and isn't accessible from your CLI afterward. Use the app for demos and to inspect what the scaffolder produces; use the CLI for vaults you actually want to keep.

---

## Usage

Open Claude Code in any directory and trigger the skill:

> *"Set up a vault for my Python web app project."*

Other triggers that work: *"create a knowledge base for our product team"*, *"scaffold an LLM wiki"*, *"I want a knowledge directory my AI can maintain"*. You don't need to say the word "vault" — anything that implies a fresh persistent LLM-maintained knowledge directory should fire the skill.

The interview is three phases, ~7 questions, under two minutes:

```
You:    Set up a vault for my Python web app project.
Claude: I can set up an LLM-maintained vault — should I walk you through it?
You:    Yes
Claude: Where should I scaffold it, and what should I call the vault?
You:    ./acme-payments, "Acme Payments Vault"
Claude: [Phase 1] Domain, scope, audience? ...
You:    engineering / single repo / small team
Claude: [Phase 2] Categories (defaults: concepts, decisions, runbooks, systems, incidents, syntheses)?
        Seed artifacts?
You:    defaults are fine; no seeds
Claude: [Phase 3] Ingest interaction style? Anything custom?
You:    confirm the plan; no custom notes
Claude: [shows the JSON config] Look right?
You:    yes
Claude: [runs scripts/scaffold.py, streams output]
        Created vault: Acme Payments Vault
          target:     /abs/path/acme-payments
          domain:     engineering
          ...
          files:      17
```

After scaffolding, open Claude Code in the new vault directory and ask it anything. It reads `vault/index.md` first per the schema, drills into relevant pages, and proposes filing your synthesis back when worthwhile.

---

## Customization

The skill is intentionally easy to fork. After install, edit:

| File | Customize |
|---|---|
| `references/domain-templates.md` | Add a new domain, edit category descriptions, trigger phrases, default-behavior rules, or domain-specific CLAUDE.md additions. Read the file's own header for the authoring rules. |
| `assets/CLAUDE.md.template` | Change the structure of the generated `CLAUDE.md` (folder map, section order, conventions). |
| `assets/skills/*.template.md` | Edit the workflow of any companion skill. Uses Jinja2; placeholders like `{{ vault_name }}`, `{{ trigger_examples.ingest }}` are documented at the top of each template. |
| `scripts/schema.json` | Tighten or loosen the config contract. Tests in `tests/test_domain_templates.py` enforce that every domain section is complete. |

After edits, run `python scripts/package.py` to rebuild the `.skill` (it runs the test suite first and fails the build if anything regresses).

### Updating an already-scaffolded vault

```bash
python scripts/scaffold.py --upgrade --target /path/to/existing/vault
```

`--upgrade` re-renders the *meta* files (`CLAUDE.md`, `README.md`, `.gitignore`, the five `.claude/skills/*/SKILL.md`) against current templates and shows a per-file diff. Confirm or reject each change. **User content under `vault/<category>/`, `raw/`, the body of `vault/index.md`, and the body of `vault/log.md` are never touched.** A single entry is appended to `vault/log.md` recording the upgrade.

Add `--yes` to auto-accept all proposed changes (useful in CI or for batch updates).

---

## Versioning

Semantic versioning. The version is recorded in:

- `scripts/package.py` (`VERSION`)
- Every scaffolded vault's `vault/.scaffold-config.json` (under `scaffold_version`)
- The initial git commit message in the scaffolded vault
- Filename of the built `.skill` package

**Bump rules:**

| Change | Bump |
|---|---|
| New trigger phrases, additional categories in defaults, new domain section, new optional config field, anything that doesn't break existing vaults | minor |
| Schema-breaking changes (renamed/removed config fields, removed domain, renamed category), changes that require an `--upgrade` to be applied | major |
| Bug fixes, doc-only changes, template content tweaks that don't change rendered shape | patch |

`--upgrade` migrations should always be safe across patches and minors; majors may require manual intervention (the upgrade output makes the diff visible so the user can adjudicate).

---

## Project layout

```
vault-scaffold/
├── SKILL.md                          # skill entrypoint (drives the interview)
├── README.md                         # this file
├── CHANGELOG.md
├── references/
│   ├── domain-templates.md           # per-domain content the scaffolder layers in
│   ├── schema-template.md            # (stub — for future expansion)
│   └── skill-templates.md            # (stub — for future expansion)
├── assets/
│   ├── CLAUDE.md.template            # generated vault's schema
│   ├── README.md.template            # generated vault's human entry point
│   ├── index.md.template
│   ├── log.md.template
│   ├── gitignore.template
│   └── skills/
│       ├── ingest.skill.template.md
│       ├── query.skill.template.md
│       ├── lint.skill.template.md
│       ├── capture-decision.skill.template.md
│       └── file-back.skill.template.md
├── scripts/
│   ├── scaffold.py                   # validates config, renders templates, scaffolds, or upgrades
│   ├── package.py                    # tests + builds dist/*.skill
│   └── schema.json                   # JSON Schema (draft-07) for the config
└── tests/
    ├── fixtures/
    │   └── sample-config.json
    ├── test_domain_templates.py
    └── test_edge_cases.py
```

---

## License

MIT. See `LICENSE` (or add one before publishing — see `SHIP_CHECKLIST.md`).
