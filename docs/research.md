# Hamta — Research Notes

Understanding of the proposal, its hidden assumptions, related work and the technology landscape.

## 1. What the proposal really says (formalized)

Data: one row per transaction — `card_hash, merchant_id, amount, timestamp, cast_name`.

1. Build a **bipartite graph** cards ↔ merchants (edge weight = number/amount of transactions).
2. For each merchant `m`, find its **peer set** `P(m)`: merchants that
   - share customers with it (graph overlap),
   - are in the same or a related category (CastName),
   - have a similar temporal pattern (hour-of-day, day-of-week, trend).
3. Estimate the merchant's **expected performance** `ŷ_m` from its peers (and, later, an AI model
   that also forecasts the future).
4. **Growth-gap score**: roughly `g_m = (ŷ_m − y_m) / ŷ_m`, weighted by how strongly `m` is tied to
   its peers (confidence).
5. Rank merchants by score → campaign target list.

In one line: *a peer-relative under-performance detector where "peer" is defined by the
customer graph rather than by category alone.*

## 2. Strengths

- Simple, explainable intuition that a marketing team can trust ("your peers do 170, you do 100").
- Uses information that classical rankings ignore: who the customers are and where else they shop.
- Shared customers implicitly encode **geography and customer segment** even when location data is
  missing — two gold shops that share customers are probably in the same bazaar or serve the same
  clientele.
- Output is directly actionable (a ranked list) and cheap to validate historically.

## 3. Hidden assumptions and pitfalls (what reviewers will attack)

| # | Issue | Why it matters | Mitigation |
|---|---|---|---|
| 1 | **Gap ≠ potential** | A merchant may be small because of size, opening hours, number of terminals, location — not lack of effort. | Control for available structural factors; describe the score as an *opportunity signal*, not proof. Frontier/benchmarking literature (SFA) formalizes exactly this. |
| 2 | **Hub merchants** | Supermarkets, fuel stations, telecom top-ups share customers with everyone and dominate raw overlap counts. | Normalized similarity (Jaccard, cosine, PMI, Adamic–Adar / resource allocation), down-weight high-degree nodes, or exclude hub categories from peer sets. |
| 3 | **Substitutes vs complements** | Shared customers within the same category = competitors; across categories = co-visit complements. They mean different things. | Use same-category overlap for peer benchmarking; use cross-category overlap as context features. |
| 4 | **Regression to the mean** | Merchants that had a bad period tend to bounce back naturally. A naive backtest will make any "low performer" score look predictive. | Backtest against baselines that also benefit from it (e.g., category z-score, own-history low point). Report lift *over* those baselines. |
| 5 | **No ground truth for "potential"** | Potential is not observed. | Proxy labels: future growth (backtest); later, real campaign response (uplift). |
| 6 | **Correlation, not causation** | High gap does not mean a campaign will *cause* growth. | Run a randomized pilot campaign → collect treatment data → uplift modeling (Phase 5 of roadmap). |
| 7 | **Scale** | Bipartite projection cost grows with Σ(degree²); national networks have tens of millions of cards. | Trim hub cards/merchants, time-window the graph, sparse matrix ops, or learn embeddings with neighbor sampling instead of full projection. |
| 8 | **Privacy & governance** | Card numbers are regulated data (PCI DSS + local regulator rules). | Keyed hashing (HMAC with secret salt) inside the company, aggregate outputs only, no raw data leaves the company or enters this repo. This is also a natural "data governance" angle for the paper. |

### A sharper metric worth adding: share of wallet among shared customers

For gold shop A, take the customers it shares with its peers and measure what fraction of *their*
gold-category spending goes to A versus B and C. A low share means customers already come to A but
spend most of their money elsewhere — a much more direct "capacity" signal than a raw count gap,
and it is naturally robust to merchant size.

## 4. Related work (to position the novelty)

- **Internal benchmarking / frontier analysis** — measuring the gap between actual and best-practice
  performance of comparable units. Stochastic Frontier Analysis (SFA) and DEA in retail; *Identifying
  Sales Performance Gaps with Internal Benchmarking* (Journal of Retailing); ML-based SFA (DNN-SFA).
  → Hamta can be described as *graph-defined peer benchmarking*: the peer group comes from the
  customer network instead of manual segmentation.
- **Merchant embeddings from card co-visits** — DeepTrax (embedding graphs of financial
  transactions; merchants linked when the same card visits both within a time window, then
  skip-gram). Shows that similar merchants cluster in embedding space — exactly Hamta's peer notion.
- **Transaction foundation models** — TransactionGPT (Visa, 2025) and pretrained generative
  autoregressive models on transaction sequences: large models of payment behaviour that produce
  merchant/cardholder representations.
- **GNNs on payment graphs** — heterogeneous cardholder–merchant graphs (RGCN, GraphSAGE), mostly used
  for fraud detection; Hamta reuses the same graph for a *marketing* task, which is less explored.
- **Relational deep learning** — RelBench (benchmark for learning directly on relational databases),
  TGB 2.0 (temporal heterogeneous graphs), KumoRFM / KumoRFM-2 (foundation models doing in-context
  prediction over relational databases).
- **Uplift modeling** — estimating who changes behaviour *because of* a campaign (meta-learners
  T/S/X/DR, causal forests, multi-treatment uplift). The end goal of campaign targeting.

**Positioning of the novelty:** combining (a) customer-graph-defined peer groups, (b) category,
(c) temporal behaviour into a peer-relative opportunity score for **merchant-side** (acquiring)
campaign targeting. Most published graph work in payments targets fraud, and most uplift work
targets consumers, not merchants.

## 5. Technology landscape (from baseline to cutting edge)

| Layer | Baseline | Strong / modern | Edge (2025–2026) |
|---|---|---|---|
| Data & ETL | pandas | **DuckDB / Polars**, Parquet, Spark for national scale | Lakehouse (Iceberg/Delta) |
| Graph construction | NetworkX | sparse matrices (SciPy), igraph, Neo4j GDS, RAPIDS cuGraph | — |
| Peer similarity | Jaccard / cosine on shared cards | PMI, Adamic–Adar, Personalized PageRank, **Leiden** communities | — |
| Representations | category + RFM features | **node2vec / DeepTrax-style** skip-gram merchant embeddings | Heterogeneous / temporal GNNs (GraphSAGE, RGCN, TGN) via PyTorch Geometric |
| Expected performance | peer mean / median | **LightGBM** on graph + temporal features, quantile regression | Relational foundation models (KumoRFM), tabular FMs (TabPFN), ML-SFA |
| Forecasting | moving average | gradient boosting with lags, Prophet-style seasonality | temporal GNNs, transaction foundation models |
| Uncertainty | — | bootstrap intervals | **conformal prediction** for calibrated intervals |
| Targeting / causality | rank by gap | A/B-tested campaigns | **uplift modeling** (CausalML, EconML: causal forests, DR-learner) |
| Explainability | peer table | **SHAP**, peer examples | GNNExplainer; LLM-written per-merchant explanation for the marketing team |
| Serving | CSV report | Streamlit / dashboard, scheduled pipeline, MLflow | campaign system integration via API (EA "capability" view) |

**Recommended stack for v1:** Python, DuckDB/Polars, SciPy sparse, igraph (Leiden), node2vec or
PyG, LightGBM, SHAP, Streamlit. Everything runs on one machine for a city- or category-sized pilot.

## 6. Open questions for the idea owner

1. Is there access to **real data**, and is publishing aggregate results permitted?
2. Time span of the data? (Backtesting needs at least two windows, e.g. 6 months + 3 months.)
3. Are merchant **location** (city/region), **terminal count**, or **terminal type** (POS / IPG) available?
4. Has the company run **past campaigns**, and is it recorded which merchants were targeted? (Unlocks uplift modeling.)
5. Rough scale: number of merchants, cards, transactions per month?
6. What is the business definition of success: transaction **count**, **amount**, or active customers?

## Sources

- DeepTrax: https://arxiv.org/abs/1907.07225
- TransactionGPT: https://arxiv.org/abs/2511.08939
- Foundation purchasing model on transaction sequences: https://arxiv.org/abs/2401.01641
- RelBench: https://github.com/snap-stanford/relbench · https://arxiv.org/abs/2407.20060
- TGB 2.0: https://arxiv.org/abs/2406.09639
- KumoRFM-2: https://arxiv.org/abs/2604.12596
- Internal benchmarking of sales gaps: https://www.sciencedirect.com/science/article/abs/pii/S0022435917300672
- ML approach to stochastic frontier modeling: https://link.springer.com/article/10.1007/s11123-026-00800-x
- Multi-treatment uplift with ranking & calibration: https://arxiv.org/abs/2408.13628
- GNN in credit-card workflow: https://arxiv.org/abs/2504.02275
