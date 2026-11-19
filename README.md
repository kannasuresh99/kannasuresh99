<picture>
  <source media="(max-width: 1011px)" srcset="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/hero-narrow.svg">
  <img src="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/hero.svg" width="100%" alt="Kannappan Suresh, Backend & AI Engineer, Chennai, India. Diagram: raw input (documents, code, requests) flows into a glowing LLM core whose particles drift at random, labeled probabilistic. The core sits inside four still, concentric rings labeled grounded retrieval, validation rules, human-in-the-loop and audit trail, together labeled deterministic. One clean, straight line leaves the rings, tagged cited, validated and audit-ready. Below, four results: large-document extraction accuracy from ~70% to ~90% (gold-set harness); a new agent in ~1 day instead of weeks; Venmo's migration ~30% faster; 60M+ records migrated with zero data loss.">
</picture>

## Models are probabilistic. The systems I build around them aren't.

I build production LLM and agentic systems, and the secure multi-tenant backends under them, for regulated domains: legal, life sciences, fintech. Currently Senior Software Engineer, AI/ML at **ValGenesis**. Shipping production software since 2021.

The LLM extracts. Deterministic checks validate. A human approves. Every output leaves a trail an auditor can follow.

**Measure it. Control it. Prove it.**

[LinkedIn](https://www.linkedin.com/in/kannappan-suresh-kannan99) · [GitHub](https://github.com/kannasuresh99)

### Not if-else. Intelligence.

I don't wire workflows out of if-else branches that break on the case nobody wrote. I put a model in the loop that reads each case, decides what to do, checks its own work, and hands off to a person when it isn't sure.

<picture>
  <source media="(max-width: 1011px)" srcset="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/agentic-narrow.svg">
  <img src="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/agentic.svg" width="100%" alt="Two panels compare a hard-coded workflow with intelligence in the workflow. Left, in grey: four incoming documents, a clean one, a scanned one, a new format and an amended one, enter an if, elif, else decision tree. The clean one takes its branch; the new format falls through to a dead end, no rule matched, manual. Every new case is another branch, and it breaks on the case nobody wrote. Right: the same four documents enter a loop around a violet model core: understand what this is and what is being asked, plan the steps and tools, act by extracting, looking up and comparing, and check against the source. All four are handled; a low-confidence case goes to an azure human-review gate and comes back approved. It reasons about each case, and rules become guardrails, not the logic. Footer: deterministic where it must be, validation, permissions and audit; intelligent everywhere else.">
</picture>

### Intelligence inside large-document workflows

Long, regulated documents. At every step the model makes a judgment, and every judgment is verified, cited to its page, and measured.

<picture>
  <source media="(max-width: 1011px)" srcset="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/docflow-narrow.svg">
  <img src="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/docflow.svg" width="100%" alt="A large-document workflow and where the intelligence sits in it. A thick stack of long regulated documents enters from the left and moves through five steps on one lane, each with a violet callout giving the question the model answers there. Read: what is this document, which parts matter? Find: where is the evidence for this field? Extract: what does it actually say? Each value stays tied to its page. Verify: does it agree with the rest of the document? Rules act as guardrails. Decide: sure enough to ship? If yes, a structured, page-cited result; if not sure, a human reviewer checks it and the correction flows back. Underneath, a mint measurement loop: every change is measured against a gold set, and a gauge shows extraction accuracy rising from ~70% to ~90%.">
</picture>

### Use cases I've solved

What the agents do, and what changed.

<picture>
  <source media="(max-width: 1011px)" srcset="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/usecases-narrow.svg">
  <img src="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/usecases.svg" width="100%" alt="Six use cases solved with agents, each tile read top to bottom as where, problem, what the agent does and result. 1. Shipping new agents at Enegma: every new agent was built from scratch; a reusable agent framework with memory, tools and multi-agent orchestration built in; weeks to ~1 day per new agent. 2. Changing agent behaviour at Enegma: every behaviour change meant a code change; written procedures (SOPs) become agent execution flows on a canvas, so core code stays untouched; ~60% faster workflow iteration. 3. Real-time agents at Enegma: slow first token; one big prompt split into small, focused prompts (micro-prompting); ~5× faster first token and ~90% fewer prompt tokens. 4. Understanding a large codebase at PayPal: engineers mapped services and dependencies by hand; agents read the code and draw service maps and call graphs; architectural-analysis time down 60% and dependency discovery down 70%. 5. Breaking up a monolith at PayPal (Venmo): a 9-month manual service-decomposition process; an agentic workflow does the decomposition; ~30% faster monolith-to-microservices migration. 6. Turning a long spec into working artifacts, a pattern I build with: forms, specs and mappings hand-built from a long document; the document becomes a structured, computable model, agents draft each artifact, amendments propagate to everything that depends on them, and every answer cites its section; AI drafts, humans approve.">
</picture>

### How I work a problem

Measure first. Find the constraint. Change the system. Prove the result.

<picture>
  <source media="(max-width: 1011px)" srcset="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/cases-narrow.svg">
  <img src="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/cases.svg" width="100%" alt="Three problem-solving cases, each read in order as problem, diagnose, move, result: a grey problem tile, a mint diagnosis tile, a move tile in its colour and an ivory result tile with the biggest type, each stage marked by a small staircase that gains a step. 1. Accuracy at ValGenesis: extraction stuck at ~70% on long regulated documents; a gold-set regression harness, measure before tuning; rebuilt evidence retrieval plus targeted model tuning; ~90% extraction accuracy. 2. Data at Kissflow: 60M+ records to move from GCS to MongoDB; two hard constraints, zero loss and faster reads; batch processing and optimized indexing; zero data loss, 15% ahead of schedule, retrieval time down 40%. 3. Backend at Saama: slow REST APIs on two clinical SaaS products; profiled the hot paths in queries and the data model; query optimization and data modeling; +20% API efficiency.">
</picture>

### Where I've shipped

Each role added a layer: backend and data first, then retrieval and agents, and now the controls that let AI run in regulated work.

<picture>
  <source media="(max-width: 1011px)" srcset="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/journey-narrow.svg">
  <img src="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/journey.svg" width="100%" alt="Career staircase from 2021 to now: five evenly spaced steps, oldest to newest, each a tower of glass layers that grows by one layer per role, capped in the colour of the layer that role built most and carrying a small scene of what that role built. One line joins the steps and shifts colour from rose to tangerine, orchid, violet and azure, with a phrase at each stop: backend, data at scale, agentic RAG, agent platforms, regulated AI. Saama, Software Engineer, 2021–2023, clinical SaaS, API efficiency +20%. Kissflow, Software Engineer, 2024, no-code platform, 60M+ records, zero loss, flagged where LLMs enter. PayPal, Software Engineer 2, 2024–2025, code intelligence, migration ~30% faster. Enegma, Founding team, 2025–2026, agent platform, weeks to ~1 day. ValGenesis, Senior SWE, AI/ML, 2026 to now, GxP document AI, ~70% to ~90%, ringed as now.">
</picture>

<details>
<summary><b>ValGenesis</b> · Senior Software Engineer, AI/ML · Apr 2026 – present</summary>

Agentic document-intelligence services for a GxP-regulated validation platform (pharma / life sciences).

- Pair LLM extraction with deterministic validation and human-in-the-loop gates on multi-tenant, permission-aware processing, so every AI output stays traceable and audit-ready (21 CFR Part 11).
- Raised extraction accuracy of a large-document pipeline from ~70% to ~90%, measured against a gold-set regression harness.
- Built an organization-wide knowledge layer that gives every AI service shared, grounded context.
- Brought tenant fairness to shared AI workloads across multi-tenant systems, with per-tenant throughput and latency metrics.
- Cut LLM inference cost and latency with context caching, batch processing and thinking-budget tuning, tracked by token-level cost and latency observability.
- Wrote engineering guidelines for using AI coding tools responsibly (review discipline, test coverage, and keeping design judgment with the engineer) and ran the internal rollout to other teams.

</details>

<details>
<summary><b>Enegma</b> (Tangerine Ventures) · Senior Software Engineer, Founding Team · Jul 2025 – Feb 2026</summary>

- Built a reusable agentic framework on LangGraph that standardizes lifecycle, memory persistence, tool integration and multi-agent orchestration, cutting new-agent development from weeks to ~1 day.
- ~5× faster time-to-first-token and ~90% prompt-token reduction for real-time agents, via micro-prompting (200 to 800-token decomposed prompts).
- Cut workflow iteration time ~60% with a DSL that expresses agent behavior as SOP-to-AOP execution flows behind an agent-canvas abstraction, so behavior changes without touching core code.
- Stood up CI/CD and engineering practice as founding engineer.

</details>

<details>
<summary><b>PayPal</b> · Software Engineer 2 · Dec 2024 – Jul 2025</summary>

- Conceived and built CodexMap, an agentic RAG code-intelligence platform (AST parsing, semantic embeddings, LLM reasoning agents) that generates service maps and call graphs, cutting architectural analysis ~60% and dependency discovery ~70%.
- Accelerated Venmo's monolith-to-microservices migration ~30% by turning a 9-month manual service-decomposition process into an automated agentic workflow.
- Shipped a refactoring tool adopted across multiple PayPal teams.

</details>

<details>
<summary><b>Kissflow</b> · Software Engineer · Jan 2024 – Dec 2024</summary>

- Migrated 60M+ records from GCS to MongoDB 15% ahead of schedule with zero data loss, cutting retrieval time 40% through optimized indexing and batch processing.
- Shipped a platform feature in 4 weeks, now used daily by 10,000+ business clients (engagement +25%, task time −30%).
- Built LLM prompt templates powering AI-assisted automation in the no-code engine. This is where LLMs enter the story.

</details>

<details>
<summary><b>Saama Technologies</b> · Software Engineer · Jul 2021 – Dec 2023</summary>

- Improved backend REST API efficiency 20% for two large-scale clinical SaaS products through query optimization and data modeling (Python, Flask, PostgreSQL, Redis, Celery, Kubernetes).
- Boosted app performance 12% and ingestion throughput 10% with Kubernetes pod auto-scaling and Kafka data pipelines on AWS.
- 4× Shining Star Award (monthly best performer).

</details>

### Toolkit

| Layer | Tools and patterns |
|---|---|
| `TRUST & CONTROLS` | deterministic validation · human-in-the-loop gates · provenance / audit trails · multi-tenant isolation · permission-aware access · 21 CFR Part 11 / GxP |
| `AGENTS` | LangGraph · LangChain · Pipecat · multi-agent orchestration · prompt engineering · micro-prompting · context caching · thinking-budget tuning |
| `RETRIEVAL` | RAG and graph-RAG · hybrid search · re-ranking · embeddings · OCR / long-document chunking · batch inference · content-hash caching |
| `EVALS & OBSERVABILITY` | eval-driven development (gold-set harnesses, LLM-as-judge) · token-level cost / latency observability · metrics · structured logging · tracing |
| `SERVICES & APIs` | FastAPI · Flask · Django · gRPC / REST API design · event-driven microservices |
| `MESSAGING & QUEUES` | Azure Service Bus · Kafka · Celery · outbox · idempotent consumers · tenant fairness (shuffle-sharding) |
| `DATA STORES` | PostgreSQL · MongoDB · Redis · Neo4j · LanceDB |
| `INFRASTRUCTURE` | GCP (Vertex AI, Gemini) · Azure (Service Bus, AKS, OpenAI) · AWS (EC2, S3, Lambda, SQS, ECS) · Docker · Kubernetes · Terraform |
| `LANGUAGES` | Python (expert) · SQL · TypeScript · Bash |

**Education** · B.Tech, Chemical Engineering, Anna University (ACT Campus), Chennai · 2016–2020 · CGPA 8.19/10<br>
**Awards** · 4× Shining Star Award (monthly best performer), Saama Technologies · INSPIRE Science Camp, Govt. of India (top 200 nationally)

[LinkedIn](https://www.linkedin.com/in/kannappan-suresh-kannan99) · [GitHub](https://github.com/kannasuresh99)
