# vault-scaffold

**Turn sources into context an agent can verify and use.**

`vault-scaffold` is an interview-driven skill for creating an LLM-maintained knowledge base and the habits that make its answers dependable.

Based on [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern: a persistent Markdown knowledge directory that an LLM curates, queries, and grows over time. The starter now asks the agent to check evidence, serve bounded context, review real answers, and improve the pages or vocabulary that caused a miss.

`vault-scaffold` runs a short interview (~7 questions), validates the answers, and lays out a ready-to-use vault: schema (`CLAUDE.md`), Raw evidence and cited pages, a first-domain walkthrough, an answer review protocol, an optional semantic-layer guide, and six companion skills (`ingest`, `query`, `lint`, `capture-decision`, `file-back`, `review-answer`). Six domain templates (engineering, product, research, personal, team, mixed) customize the vault's vocabulary and rules. Git is initialized locally when available, with no automatic staging or commit.

## The first useful loop

`allowed source → immutable Raw → cited page → focused context → answer → evidence review → correction`

Start with one domain, a few approved sources, and a question you will really ask. The generated `ADOPTION.md` walks through the loop; `evaluation/README.md` gives each question an expected distinction, supporting passages, scope, and a plausible wrong answer. The agent checks whether its answer preserved those conditions. Finding a page or producing a valid citation is only a partial result.

The optional `SEMANTIC-LAYER.md` starts with stable terms and aliases, then adds relationships when real questions need them. Taxonomy, formal ontology, and a derived graph have explicit adoption gates. No graph database or automated entailment claim is bundled with the starter.

Source-derived files, local operating notes, and evaluation cases are ignored by Git by default. The scaffold has no automatic privacy scanner: check exclusions and model access before ingest, and review the exact files before any remote export.

---

## Install

The workflow is plain Markdown plus a Python scaffolder. The marketplace is the easiest installation path for Claude Code, but the skill can also be cloned directly or read as standalone agent instructions.

### a) Claude Code marketplace

Add the personal marketplace once:

```
/plugin marketplace add wbratz/vault-scaffold
```

Then install the plugin:

```
/plugin install vault-scaffold@wbratz-vault-tools
```

Run `/reload-plugins` to make it available in the current session.

### b) Direct git clone

User-global — skill becomes available in every Claude Code session on your machine:

```bash
git clone https://github.com/wbratz/vault-scaffold.git ~/.claude/skills/vault-scaffold
```

Project-scoped — only loads when Claude Code starts in this project's root:

```bash
git clone https://github.com/wbratz/vault-scaffold.git .claude/skills/vault-scaffold
```

Update later with `git -C <path> pull`.

### c) From a built `.skill` package

Build one with `python scripts/package.py` (output lands in `dist/`), or download a release. The `.skill` file is just a zip:

```bash
unzip vault-scaffold-v0.2.0.skill -d ~/.claude/skills/
# verify SKILL.md ends up one level deep, not nested:
ls ~/.claude/skills/vault-scaffold/SKILL.md
```

### After install

If you used the marketplace, run `/reload-plugins`. For a direct clone or `.skill` extraction, restart Claude Code. Then say something like *"set up a vault for my Python project"* — the trigger phrase should fire the interview.

### Other agents

`SKILL.md` is the complete interview and execution contract. Agents that can read local instructions and run Python can follow it without the Claude plugin system. The generated `CLAUDE.md` explicitly addresses any file-reading agent; the `.claude/skills/` directory adds automatic operation detection when Claude Code is the client.

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
          files:      24
```

After scaffolding, open `ADOPTION.md` in the new vault. Ingest one allowed source, ask a real question, and use `review-answer` to inspect the answer against Raw. The index routes the agent to pages; it checks the source behind substantive conclusions and proposes filing back reusable synthesis.

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

`--upgrade` re-renders the *meta* files (`CLAUDE.md`, `README.md`, `ADOPTION.md`, `SEMANTIC-LAYER.md`, `evaluation/README.md`, `.gitignore`, and six `.claude/skills/*/SKILL.md`) against current templates and shows a per-file diff. Confirm or reject each change. **User content under `vault/<category>/`, `raw/`, the body of `vault/index.md`, and the body of `vault/log.md` are never touched.** Older custom notes are copied into ignored `LOCAL-NOTES.md` if it does not exist; an existing local-notes file is never overwritten. A single entry is appended to `vault/log.md` recording the upgrade. After upgrading, inspect tracked files: `.gitignore` does not untrack content already committed.

Add `--yes` to auto-accept all proposed changes (useful in CI or for batch updates).

---

## Versioning

Semantic versioning. The version is recorded in:

- `scripts/package.py` (`VERSION`)
- Every scaffolded vault's `vault/.scaffold-config.json` (under `scaffold_version`)
- Filename of the built `.skill` package

**Bump rules:**

| Change | Bump |
|---|---|
| New trigger phrases, additional categories in defaults, new domain section, new optional config field, anything that doesn't break existing vaults | minor |
| Schema-breaking changes (renamed/removed config fields, removed domain, renamed category), changes that require an `--upgrade` to be applied | major |
| Bug fixes, doc-only changes, template content tweaks that don't change rendered shape | patch |

During the `0.x` series, a minor release may also change generation defaults. Version `0.2.0` removes the automatic initial Git commit and adds privacy, evidence, evaluation, and semantic-layer contracts. `--upgrade` migrations show each proposed meta-file change; review them against local edits.

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
│   ├── ADOPTION.md.template           # first-domain walkthrough
│   ├── SEMANTIC-LAYER.md.template     # optional modeling guide
│   ├── evaluation-README.md.template # answer review contract
│   ├── local-notes.md.template        # ignored local constraints
│   ├── README.md.template            # generated vault's human entry point
│   ├── index.md.template
│   ├── log.md.template
│   ├── gitignore.template
│   └── skills/
│       ├── ingest.skill.template.md
│       ├── query.skill.template.md
│       ├── lint.skill.template.md
│       ├── capture-decision.skill.template.md
│       ├── file-back.skill.template.md
│       └── review-answer.skill.template.md
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
