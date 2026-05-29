# Domain templates

Per-domain content the scaffolder layers over its generic defaults. Each H2 below is a domain name (matching the `domain` enum in `scripts/schema.json`); each H3 is one of the six fixed subsections the parser reads. Authoring conventions:

- **`### Default categories`** — flat bullet list of category slugs.
- **`### Category descriptions`** — bullets in the form ``- `<cat>` — <one-line description>``.
- **`### Trigger phrase examples`** — one H4 per skill (`ingest`, `query`, `lint`, `capture-decision`, `file-back`), each with bulleted phrases in double quotes.
- **`### Capture-decision examples`** — flat bullet list of *kinds of statements* (not literal trigger phrases) that should make the `capture-decision` skill fire in this domain.
- **`### Custom CLAUDE.md additions`** — free prose appended to `CLAUDE.md` as a new "Domain-specific conventions" section. Do not use H1/H2 inside this prose (they'd confuse the parser); H3+ is fine.
- **`### Custom default-behavior rules`** — bullet list of rules appended under the "Default behavior" section of `CLAUDE.md`.

---

## engineering

### Default categories

- concepts
- decisions
- runbooks
- systems
- incidents
- syntheses

### Category descriptions

- `concepts` — Architectural concepts, language idioms, infrastructure primitives, core abstractions used across the codebase
- `decisions` — ADRs, RFC outcomes, tradeoff conversations turned into commitments
- `runbooks` — Step-by-step procedures for deploys, incidents, on-call scenarios, recurring chores
- `systems` — Canonical descriptions of services, modules, libraries, and their boundaries
- `incidents` — Postmortems with timeline, root cause, contributing factors, action items
- `syntheses` — Cross-cutting analyses spanning multiple services, comparisons, migration writeups
- `sources` — Summaries of ingested source documents (RFCs, PRs, articles, talks)

### Trigger phrase examples

#### ingest
- "ingest this PR"
- "summarize this RFC"
- "add this commit to the vault"
- "pull in this oncall report"
- "ingest this design doc"

#### query
- "what do we know about <module>?"
- "how does <component> handle <case>?"
- "what was the decision around <topic>?"
- "explain how <subsystem> works"
- "find the runbook for <scenario>"

#### lint
- "audit the vault"
- "find contradictions"
- "lint"
- "find stale runbooks"
- "check for broken cross-references"

#### capture-decision
- "let's go with PostgreSQL"
- "we'll skip caching for now"
- "decided to ship synchronously"
- "going with the Redis approach"
- "we're not doing the rewrite"

#### file-back
- "save this debugging session"
- "file this gotcha"
- "add this finding to the vault"
- "promote this to a page"
- "this is worth keeping"

### Capture-decision examples

- A PR review concludes with a chosen approach
- The team picks a library, framework, or vendor
- Architecture or schema is changed to handle a constraint
- A bug fix reveals a permanent rule ("we'll always validate X")
- An incident postmortem assigns a new operating procedure
- A migration plan is finalized
- A deprecation is announced

### Custom CLAUDE.md additions

When referencing code, always include file paths and line numbers in `path/to/file.ext:line` form so the reader can navigate directly.

When citing decisions, link to the PR, commit, or ticket when one exists. A decision without a link to its source can't be re-litigated.

When summarizing a service or module under `vault/systems/`, name its primary repo, language, runtime, and on-call owner (when known). These are the questions every new contributor asks.

When recording an incident under `vault/incidents/`, include the timeline as UTC ISO timestamps and separate observed facts from inferred causes.

Treat code in `raw/` (when committed there) as authoritative; treat documentation summaries as approximations of code, not substitutes.

### Custom default-behavior rules

- Before answering implementation questions, check `vault/systems/` for the canonical description of the service in question. Do not infer from the code path alone if a system page exists.
- When an answer requires shell commands, suggest the command. Do not execute production-touching commands (`kubectl`, `psql -c`, deploy scripts) without explicit user confirmation in the same turn.
- When a runbook exists for the situation, link to it rather than retyping the steps inline.

---

## product

### Default categories

- features
- personas
- decisions
- experiments
- competitors
- syntheses

### Category descriptions

- `features` — Feature specs, user stories, currently-shipped capabilities and their states
- `personas` — User and customer segments with goals, pain points, jobs-to-be-done
- `decisions` — Product decisions — what we're building, what we're not, and why
- `experiments` — A/B tests, feature flags, hypotheses with metrics and verdicts
- `competitors` — Competitor capabilities, pricing, positioning, our differentiation
- `syntheses` — Cross-cutting analyses combining customer feedback, metrics, and roadmap
- `sources` — Summaries of ingested source documents (interviews, decks, articles, releases)

### Trigger phrase examples

#### ingest
- "ingest this customer interview"
- "summarize this PR"
- "add this Linear ticket to the vault"
- "pull in this competitor announcement"
- "ingest this user research summary"

#### query
- "what do we know about <segment>?"
- "what experiments have we run on <feature>?"
- "why did we ship <thing>?"
- "who's our main competitor for X?"
- "what did customers say about <feature>?"

#### lint
- "audit the vault"
- "find stale assumptions"
- "lint"
- "find personas without backing research"
- "find features without owners"

#### capture-decision
- "let's deprioritize X"
- "we'll ship the small version first"
- "going with the freemium model"
- "decided not to compete on price"
- "we'll cut this feature from the launch"

#### file-back
- "save this customer quote"
- "file this observation"
- "add this experiment result"
- "promote this to the vault"
- "this insight is worth keeping"

### Capture-decision examples

- Roadmap prioritization is set or changed
- A feature is descoped, deferred, or killed
- Pricing or packaging is decided
- A persona definition is agreed upon
- A response to a competitor move is chosen
- A launch is delayed or accelerated
- A metric becomes (or stops being) a North Star

### Custom CLAUDE.md additions

When citing customer evidence, name the customer (or persona) and the date or source. Anonymize if needed, but keep enough detail to re-find the source.

When referencing experiments, include the hypothesis, the metric watched, the sample size if known, and the verdict (shipped / killed / extended).

When summarizing competitors, separate observable facts (their pricing page, their public roadmap) from inference (likely strategy, internal motivations).

Tickets, decks, and customer artifacts should be cited by their canonical ID or URL when filed (e.g., `LIN-1234`, `pitch://deck-id`, `gong://call-id`).

Personas under `vault/personas/` should each link to at least one piece of backing evidence (interview, survey, behavioral data). Personas without evidence rot.

### Custom default-behavior rules

- Before answering "should we build X?", check `vault/experiments/` and `vault/decisions/` for prior attempts. Surface any prior verdict explicitly.
- For any claim about a persona's behavior, check `vault/personas/` first; do not invent or generalize persona traits from memory.
- When summarizing customer feedback, distinguish what the customer literally said from what we infer they meant.

---

## research

### Default categories

- entities
- concepts
- papers
- methods
- syntheses

### Category descriptions

- `entities` — People, labs, organizations, datasets, tools referenced across the literature
- `concepts` — Theoretical concepts, definitions, frameworks, taxonomies
- `papers` — Per-paper summaries: contributions, methods, results, critiques
- `methods` — Reusable techniques, experimental designs, evaluation protocols
- `syntheses` — Cross-paper analyses, literature reviews, comparison tables
- `sources` — Summaries of ingested source documents (papers, talks, datasets, code releases)

### Trigger phrase examples

#### ingest
- "ingest this paper"
- "summarize this arxiv preprint"
- "add this talk to the vault"
- "pull in this dataset description"
- "ingest this blog post"

#### query
- "what does the literature say about X?"
- "who has worked on Y?"
- "what methods have been used for Z?"
- "summarize the debate around <topic>"
- "what's the state of the art for <task>?"

#### lint
- "audit the vault"
- "find contradicting claims"
- "lint"
- "find papers without summaries"
- "find concepts without canonical definitions"

#### capture-decision
- "let's focus the review on X"
- "we'll exclude pre-2020 work"
- "decided on this evaluation metric"
- "going with this taxonomy"
- "we're treating these two terms as synonyms"

#### file-back
- "save this comparison"
- "file this insight"
- "add this critique to the vault"
- "promote this to a synthesis"
- "this is worth keeping"

### Capture-decision examples

- A scope decision for a literature review or research project
- A choice of methodology, evaluation, or dataset
- An adopted taxonomy or definition
- A judgment about a paper's validity or relevance
- A decision to follow up (or not) on a particular thread
- An acknowledged limitation that will shape the rest of the work

### Custom CLAUDE.md additions

When citing a paper, use a canonical citation (authors, year, venue) and link to the `raw/` copy when available.

When discussing claims, distinguish what the paper *demonstrates* (its evidence) from what it *argues* (its claim). The distinction is where most contradictions hide.

When summarizing methods, capture the assumptions and limitations explicitly. A method page that omits limitations becomes harmful when reused.

For any extracted dataset or benchmark, record the source, license, version, and any preprocessing steps. Datasets evolve silently; pin what you used.

Definitions under `vault/concepts/` should call out conflicting usages in the literature rather than picking one silently.

### Custom default-behavior rules

- Before answering "what's the state of the art for X?", check `vault/syntheses/` and `vault/papers/`. Do not synthesize across papers from memory — the vault exists precisely to make this kind of question grounded.
- When a claim conflicts across papers, surface the conflict explicitly with citations rather than picking a side silently.
- When recommending a method, cite the paper(s) it came from and any vault page that records prior experience with it.

---

## personal

### Default categories

- entities
- concepts
- decisions
- syntheses

### Category descriptions

- `entities` — People, places, projects, tools, books — the named things you reference repeatedly
- `concepts` — Ideas, frameworks, mental models you're working with
- `decisions` — Personal decisions and their context (what you chose, why, what you'd revisit)
- `syntheses` — Cross-cutting reflections, summaries of phases or periods
- `sources` — Summaries of ingested source documents (articles, books, podcasts, talks)

### Trigger phrase examples

#### ingest
- "ingest this article"
- "add this book to my notes"
- "summarize this podcast"
- "save this for later"
- "ingest this talk"

#### query
- "what did I think about X?"
- "what have I read about Y?"
- "remind me what I decided about Z"
- "what's in my notes on <topic>?"
- "did I capture anything about <person>?"

#### lint
- "tidy up"
- "check for stale notes"
- "lint my vault"
- "find decisions I haven't revisited"

#### capture-decision
- "I'm going to stop X"
- "I'll commit to Y"
- "decided to switch to Z"
- "going to drop this hobby"
- "I'm changing my mind about W"

#### file-back
- "save this"
- "remember this"
- "add this to my notes"
- "keep this thought"

### Capture-decision examples

- A commitment to start, stop, or change something (habit, project, tool)
- A revisit of a previous decision with new information
- A boundary set ("I won't take on more side projects this quarter")
- A choice about what to read, study, or learn next
- An acknowledged change of mind worth dating

### Custom CLAUDE.md additions

This vault is private. Speak naturally; don't write for an audience that isn't here.

When referencing past notes or decisions, link rather than restate. Restating loses the original framing.

Reflection-style pages (under `vault/syntheses/`) are encouraged — they're what makes the vault useful when you look back six months later.

When recording a decision, note your state of mind or the trigger if relevant. Future-you reads not just the choice but the context that shaped it.

### Custom default-behavior rules

- Before answering "what did I decide about X?", check `vault/decisions/`. Do not infer from chat history alone.
- When the vault contradicts a more recent stated view, surface the contradiction rather than silently siding with the newer one — the decision page might be the load-bearing one.
- For any claim about a person, place, or tool, prefer linking to the relevant `vault/entities/` page rather than restating from chat.

---

## team

### Default categories

- entities
- concepts
- decisions
- processes
- syntheses

### Category descriptions

- `entities` — People, teams, projects, tools, vendors — anything referenced in team context
- `concepts` — Shared ideas, methodologies, frameworks the team operates with
- `decisions` — Team decisions: charters, processes, technology choices, organizational changes
- `processes` — How the team works: rituals, workflows, conventions, expectations
- `syntheses` — Retrospectives, quarterly reviews, cross-cutting analyses
- `sources` — Summaries of ingested source documents (charters, retros, 1:1 notes, all-hands)

### Trigger phrase examples

#### ingest
- "ingest this retrospective"
- "summarize this all-hands"
- "add this charter doc to the vault"
- "pull in this 1:1 note"
- "ingest this team agreement"

#### query
- "what's our policy on X?"
- "who owns Y?"
- "what did we agree about Z?"
- "how do we handle <situation>?"
- "what's our process for <event>?"

#### lint
- "audit the vault"
- "find stale processes"
- "lint"
- "find owners without entities"
- "find decisions without follow-through"

#### capture-decision
- "let's adopt this ritual"
- "we'll move standups to async"
- "decided to split the team"
- "going with this on-call rotation"
- "we're sunsetting that meeting"

#### file-back
- "save this retro outcome"
- "file this convention"
- "add this to the team vault"
- "promote this to a process page"

### Capture-decision examples

- A team charter, mission, or scope is set or changed
- A process change is agreed upon (meetings, on-call, code review, planning cadence)
- An ownership boundary is drawn or moved
- A hiring or staffing decision (within what's appropriate to record)
- A vendor or tool is adopted or sunset
- A team norm is articulated for the first time

### Custom CLAUDE.md additions

When referencing a person, prefer role + name (e.g., "tech lead, Alex") rather than first-name-only. Roles persist; people move.

When citing a process, link to its canonical doc and note when it was last reviewed. Processes that haven't been reviewed in 12 months are usually wrong.

When summarizing a retrospective, separate observations (what happened) from action items (what we'll change). Action items belong in `vault/decisions/` when they're commitments.

For any decision that names an owner, include the role; the role outlives any individual.

The vault is shared across the team — write for the reader who joins next quarter, not just the current group.

### Custom default-behavior rules

- Before answering "what's our policy on X?", check `vault/processes/` and `vault/decisions/`. Do not invent or generalize from external best practices.
- When advising on a team practice, ground the recommendation in what this team's vault actually says, not industry norms.
- When a process page conflicts with a recent decision, the decision wins and the process page needs updating — flag this rather than silently following one.

---

## mixed

### Default categories

- concepts
- decisions
- entities
- syntheses

### Category descriptions

- `concepts` — Core ideas and topics this vault tracks across whatever domains it spans
- `decisions` — Decisions and their context, across all domains the vault covers
- `entities` — People, projects, organizations, systems — the named things referenced often
- `syntheses` — Cross-cutting analyses that combine multiple categories or domains
- `sources` — Summaries of ingested source documents (any kind)

### Trigger phrase examples

#### ingest
- "ingest this"
- "add this source"
- "summarize this document"
- "pull this into the vault"

#### query
- "what do we know about X?"
- "what was decided about Y?"
- "tell me about Z"
- "find pages on <topic>"

#### lint
- "audit the vault"
- "find contradictions"
- "lint"

#### capture-decision
- "let's go with X"
- "we'll do Y"
- "decided"
- "going with this approach"

#### file-back
- "save this"
- "file this back"
- "add this as a page"

### Capture-decision examples

- An explicit conclusion to a discussion
- A change of direction
- A tradeoff acknowledged and accepted
- A choice between two named options
- A scope or boundary set

### Custom CLAUDE.md additions

This vault spans multiple domains. When a page could fit under multiple framings, file it under the most natural primary domain and cross-link from the others.

When the audience for a page differs (e.g., a decision page that matters to both engineers and product), say so explicitly at the top of the page. Hidden audience mismatches are a frequent source of confusion in mixed-domain vaults.

### Custom default-behavior rules

- When answering a question, identify which "side" of the vault the question is about (engineering / product / personal / etc.) and prioritize pages from that area before crossing over.
- For decisions that affect multiple areas, surface both perspectives when relevant rather than answering only from one.
