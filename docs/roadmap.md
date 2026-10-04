# Hamta — Roadmap

Each phase ends with something usable. The first two phases are enough for a conference paper.

## Phase 0 — Foundations (data access & governance)

- Agreement on data access and what may be published (aggregates only).
- Anonymization inside the company: keyed hash (HMAC) of card numbers, no raw PAN anywhere.
- Data dictionary, exploratory analysis: merchants / cards / transactions per category, degree
  distributions (find hub merchants and hub cards), seasonality.
- Define the target metric (count vs amount vs active customers) and time windows.

**Deliverable:** clean Parquet dataset + EDA notebook + data governance note.

## Phase 1 — Baselines and the evaluation harness

The most important asset of the project: a **temporal backtest** that every method is judged by.

- Split time: history window `T` (e.g. 6 months) → outcome window `T+1` (e.g. next 3 months).
- Baselines: rank by current volume; category z-score (gap vs category median); own-history dip.
- Metrics: precision@k / lift@k of "merchants that grew most in T+1", NDCG, Spearman correlation.
- Explicitly check regression-to-the-mean effects.

**Deliverable:** reproducible backtest script + baseline numbers.

## Phase 2 — Graph peer score (the core idea, v1)

- Bipartite card–merchant graph per window; trim hubs.
- Merchant–merchant similarity: Jaccard / cosine on shared cards (same category), plus temporal
  profile similarity (hour × weekday vector).
- Peer set = top-k similar merchants; expected volume = similarity-weighted peer volume.
- Growth-gap score + confidence; **share-of-wallet among shared customers**.
- Leiden communities to describe "markets" (e.g. a bazaar, a neighborhood cluster).
- Per-merchant explanation: list of peers and their numbers.

**Deliverable:** ranked target list + backtest comparison against Phase 1 baselines.
→ **Enough for the ICAEA 2026 paper** (deadline 1405/07/17).

## Phase 3 — AI model (v2)

- Merchant embeddings: node2vec / DeepTrax-style skip-gram on card co-visits.
- Expected-performance model: LightGBM on graph + temporal + category features (quantile
  regression for "achievable" level, close to a frontier).
- Forecast of next-period volume; score = predicted achievable − predicted actual.
- SHAP explanations; conformal intervals for confidence.
- Optional: heterogeneous GNN (GraphSAGE / RGCN in PyTorch Geometric) and compare.

**Deliverable:** model v2 with measured lift over v1.

## Phase 4 — Architecture and decision-support system

- Scheduled pipeline (monthly), model registry (MLflow), dashboard for the marketing team.
- Integration point with the campaign / CRM system.
- Document as an enterprise capability: data layer → governance → analytics → decision → action.

**Deliverable:** working internal tool; strong material for an EA-oriented journal paper.

## Phase 5 — Pilot campaign (causal evidence)

- Randomized pilot: among high-score merchants, treat a random half, keep half as control.
- Measure incremental transactions. This is the first real proof that the score finds *responsive*
  merchants.

**Deliverable:** A/B results; treatment data for uplift modeling.

## Phase 6 — Uplift and edge methods

- Uplift models (causal forests, DR-learner; CausalML / EconML): target merchants whose growth is
  *caused* by the campaign, not those who would grow anyway.
- Temporal GNNs (TGN), relational foundation models (KumoRFM-style), transaction foundation
  model embeddings.
- LLM-generated campaign suggestions and explanations per merchant.

**Deliverable:** journal paper (method + causal validation).

## Publication path

| When | Output | Content |
|---|---|---|
| ICAEA 2026 (deadline 1405/07/17) | Conference paper | Problem, architecture, Phase 1–2 method, backtest |
| After Phase 3–4 | Journal / special issue | AI model, system architecture, larger evaluation |
| After Phase 5–6 | Journal | Causal (uplift) validation from a real pilot |
