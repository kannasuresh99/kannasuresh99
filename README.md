<picture>
  <source media="(max-width: 1011px)" srcset="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/hero-narrow.svg">
  <img src="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/hero.svg" width="100%" alt="Kannappan Suresh, Backend & AI Engineer, Chennai, India. Diagram: raw input (documents, code, requests) flows into a glowing LLM core whose particles drift at random, labeled probabilistic. The core sits inside four still, concentric rings labeled grounded retrieval, validation rules, human-in-the-loop and audit trail, together labeled deterministic. One clean, straight line leaves the rings, tagged cited, validated and audit-ready. Below, four results: large-document extraction accuracy from ~70% to ~90% (gold-set harness); a new agent in ~1 day instead of weeks; Venmo's migration ~30% faster; 60M+ records migrated with zero data loss.">
</picture>

## Models are probabilistic. The systems I build around them aren't.

I build production LLM and agentic systems, and the secure multi-tenant backends under them, for regulated domains: legal, life sciences, fintech. Currently Senior Software Engineer, AI/ML at **ValGenesis**. Shipping production software since 2021.

The LLM extracts. Deterministic checks validate. A human approves. Every output leaves a trail an auditor can follow.

**Measure it. Control it. Prove it.**

[LinkedIn](https://www.linkedin.com/in/kannappan-suresh-kannan99) · [GitHub](https://github.com/kannasuresh99)

### Built from the base up

I design the whole system, not only the prompt: from the cluster at the bottom to the controls at the top that make AI output trustworthy. Each color is one layer, and it keeps that meaning in every diagram on this page.

<picture>
  <source media="(max-width: 1011px)" srcset="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/stack-narrow.svg">
  <img src="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/stack.svg" width="100%" alt="Layered architecture stack, built from the bottom up. 1 Infrastructure: Azure AKS, GCP Vertex AI, AWS, Kubernetes, Docker, Terraform; pattern: pod auto-scaling. 2 Data stores: PostgreSQL, MongoDB, Redis, Neo4j, LanceDB; patterns: knowledge graph, optimized indexing. 3 Messaging and queues: Azure Service Bus, Kafka, Celery; patterns: shuffle-sharding, outbox, idempotent consumers. 4 Services and APIs: FastAPI, Flask, Django, gRPC and REST; patterns: event-driven microservices, multi-tenant isolation, permission-aware access. 5 Retrieval: embeddings, hybrid search, re-ranking, OCR chunking; patterns: graph-RAG, content-hash cache. 6 Agents: LangGraph, LangChain, Pipecat, Gemini, Azure OpenAI; patterns: multi-agent orchestration, micro-prompting, context caching, thinking budgets. 7 Trust and controls: deterministic validation, human-in-the-loop, audit trails, provenance, 21 CFR Part 11 / GxP. Two rails run alongside: observability (metrics, structured logs, tracing, token cost and latency) across every layer, and evals (gold-set harness, LLM-as-judge) across retrieval, agents, and trust and controls.">
</picture>

### How I build large-document pipelines

The LLM is one stage. Everything around it exists to give it the right context, check its work, and show where each answer came from.

<picture>
  <source media="(max-width: 1011px)" srcset="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/pipeline-narrow.svg">
  <img src="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/pipeline.svg" width="100%" alt="Large-document pipeline in three lanes plus an eval loop. Ingest path: long PDFs enter an ingest service (FastAPI), wait in a tenant-fair queue, pass a content-hash cache where seen content is reused and skips ahead, then go through OCR and long-document chunking, then embedding and graph linking into a shared knowledge graph and vector layer. Answer path: hybrid and graph search over that knowledge, re-ranking, LLM extraction by agents with batch inference, deterministic validation, a human review and approval gate, and finally cited, page-anchored output written to an audit trail (source page, extracted, validated, approved; 21 CFR Part 11). Eval loop: a gold-set harness and an LLM-as-judge score the output and feed back to tune retrieval and the model; a gauge shows extraction accuracy rising from ~70% to ~90%.">
</picture>

### Agentic systems I've built

How they work, and what they changed.

<picture>
  <source media="(max-width: 1011px)" srcset="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/agents-narrow.svg">
  <img src="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/agents.svg" width="100%" alt="Five agentic systems as diagram cards. 1. Agent framework (Enegma, LangGraph): one framework core with lifecycle, memory, tools and orchestration modules produces new agents that work together; new-agent development went from weeks to ~1 day. 2. Micro-prompting (Enegma, real-time agents): one big prompt split into 200 to 800-token decomposed prompts; ~5× faster time-to-first-token and ~90% fewer prompt tokens. 3. SOP to AOP (Enegma): a DSL turns a standard operating procedure into an agent execution flow on an agent canvas while core code stays untouched; workflow iteration time cut ~60%. 4. Agents that read code (PayPal, CodexMap): a codebase goes through AST parsing, semantic embeddings and LLM reasoning agents to produce service maps and call graphs; architectural analysis cut ~60% and dependency discovery cut ~70%. Alongside it, Venmo's 9-month manual service-decomposition process became an agentic workflow, and the monolith-to-microservices migration ran ~30% faster. 5. Document to computable model (side-project pattern): a long spec document becomes a structured, computable model; drafting agents generate forms, specs and mappings; a human approves before anything goes live; amendments are detected and propagated to every dependent artifact; questions to the document are answered with section citations. AI drafts, humans approve.">
</picture>

### How I work a problem

Measure first. Find the constraint. Change the system. Prove the result.

<picture>
  <source media="(max-width: 1011px)" srcset="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/cases-narrow.svg">
  <img src="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/cases.svg" width="100%" alt="Four problem-solving cases, each read in order as problem, diagnose, move, result: a grey problem tile, a mint diagnosis tile, a move tile in its layer colour and an ivory result tile with the biggest type, each stage marked by a small staircase that gains a step. 1. Retrieval at ValGenesis: extraction at ~70% in a large-document pipeline; a gold-set regression harness, measure before tuning; retrieval over a trace graph with hybrid and graph search plus model optimizations; ~90% extraction accuracy. 2. Messaging at ValGenesis: noisy neighbours, tenants share AI queues; no tenant fairness, one queue for many tenants; a shuffle-sharded queue with idempotent consumers and an outbox on Azure Service Bus; tenant fairness with per-tenant metrics. 3. Agents at Enegma: slow first token for real-time agents; oversized prompts, tokens drive latency; micro-prompting with 200 to 800-token prompts; ~5× faster first token and ~90% fewer prompt tokens. 4. Data at Kissflow: 60M+ records to move from GCS to MongoDB; two hard constraints, zero loss and faster reads; batch processing and optimized indexing; zero data loss, 15% ahead of schedule, retrieval time down 40%.">
</picture>

### Where I've shipped

Each role added a layer: backend and data first, then retrieval and agents, and now the controls that let AI run in regulated work.

<picture>
  <source media="(max-width: 1011px)" srcset="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/journey-narrow.svg">
  <img src="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/journey.svg" width="100%" alt="Career staircase from 2021 to now: five evenly spaced steps, oldest to newest, each a tower of glass layers that grows by one layer per role, capped in the colour of the layer that role built most and carrying that layer's small scene from the stack. One line joins the steps and shifts colour from rose to tangerine, orchid, violet and azure, with a phrase at each stop: backend, data at scale, agentic RAG, agent platforms, regulated AI. Saama, Software Engineer, 2021–2023, clinical SaaS, API efficiency +20%. Kissflow, Software Engineer, 2024, no-code platform, 60M+ records, zero loss, flagged where LLMs enter. PayPal, Software Engineer 2, 2024–2025, code intelligence, migration ~30% faster. Enegma, Founding team, 2025–2026, agent platform, weeks to ~1 day. ValGenesis, Senior SWE, AI/ML, 2026 to now, GxP document AI, ~70% to ~90%, ringed as now.">
</picture>

<details>
<summary><b>ValGenesis</b> · Senior Software Engineer, AI/ML · Apr 2026 – present</summary>

Agentic document-intelligence services for a GxP-regulated validation platform (pharma / life sciences).

- Pair LLM extraction with deterministic validation and human-in-the-loop gates on multi-tenant, permission-aware processing, so every AI output stays traceable and audit-ready (21 CFR Part 11).
- Raised extraction accuracy of a large-document pipeline from ~70% to ~90%, measured against a gold-set regression harness, by re-architecting retrieval over a trace graph with hybrid and graph-based search plus targeted model optimizations.
- Designed and built an organization-wide knowledge-graph system on Neo4j that unifies entity and dependency context to power graph-RAG retrieval across AI services.
- Designed a shared queuing service on Azure Service Bus for AI workloads (shuffle-sharding, idempotent consumers, outbox pattern) that brought tenant fairness to multi-tenant systems, instrumented with per-tenant throughput and latency metrics.
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

<picture>
  <source media="(max-width: 1011px)" srcset="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/footer-narrow.svg">
  <img src="https://raw.githubusercontent.com/kannasuresh99/kannasuresh99/main/assets/footer.svg" width="100%" alt="Two systems mirrored across three shared verbs. Left: a chemical reactor with a gauge (measure), a valve (control) and a chart recorder (prove), captioned Chemical Engineering, 2016–2020. Right: an LLM core with an eval harness (measure), validation and a human gate (control) and an audit trail (prove), captioned Production AI, today.">
</picture>

<p align="right"><i>Same discipline. New reactor.</i></p>
