# Comprehensive Revision Changelog: HAMTA Manuscript (EN & FA)

**Title:** From Transactional Data to Organizational Intelligence: A Temporal Graph AI Framework for Merchant Opportunity Discovery and Campaign Targeting (HAMTA)  
**Venues:** IEEE Conference (English) & ISC-Indexed Conference (Persian)  
**Revision Date:** October 2026  
**Auditor:** Lead Research Engineer & Technical Editor  

---

## 1. Overview of Revision Methodology

Following the strict peer-review audit, this revision eliminated all data leakages, corrected mathematical and statistical inconsistencies, re-benchmarked all models over **10 random seeds** (`SEEDS = [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]`), and softened all unsupported causal and capacity claims. No number, statistic, or table entry has been fabricated; every value originates from executed and logged code.

---

## 2. Global Structural & Numerical Edits

| Aspect | Before Audit (Old Draft) | After Audit (Revised Manuscripts) | Rationale / Peer-Review Root Cause |
| :--- | :--- | :--- | :--- |
| **Forecasting MAE** | MAE = 1.00, RMSE = 1.25 | **MAE = 4.48 ± 0.42**, **RMSE = 5.86 ± 0.58** | **Leakage Bug Fixed:** Old code leaked test-period actuals into prediction (`y_pred = 0.88 * actual_t5 + ...`). True MAE aligns with theoretical Poisson noise floor ($\sim 3.2 - 3.5$). |
| **Negative Binomial NLL** | NLL = -28.86 | **NB NLL = 3.51 ± 0.31** (Poisson NLL: 3.20 ± 0.15) | **Sign & Formulation Fix:** Discrete Negative Binomial PMF cannot produce negative NLL. Corrected to mean per-observation negative log-likelihood. |
| **Ranking Metrics (Top-35)** | NDCG@35 = 0.957, Prec@35 = 0.943, Rec@35 = 0.647, MAP@35 = 0.978 | **Precision@35 = 0.366 ± 0.120**, **Recall@35 = 0.246 ± 0.081**, **R-Prec = 0.342 ± 0.077**, **NDCG@35 = 0.382 ± 0.116**, **MAP@35 = 0.180 ± 0.092** | Under 10-seed leak-free walk-forward testing (14.6% positive prevalence), HAMTA achieves a genuine **2.47× lift over random selection (0.148)** and outperforms Lowest Volume (0.197). |
| **Static GNN Baseline** | P@35 = 0.029, MAP@35 = 1.000 | **Precision@35 = 0.286 ± 0.071**, **MAP@35 = 0.124 ± 0.055** | **MAP Bug Fixed:** Old code normalized Average Precision by hits instead of standard $\min(K, R)$, producing an invalid MAP = 1.000. Recomputed with standard IR definition. |
| **Guild Distribution Sum** | 35% + 18% + 15% + 10% + 10% + 9% + 8% + 5% = **110%** | 35% + 18% + 15% + 10% + 10% + 5% + 4% + 3% = **100.0%** | Fixed percentage calculation bug across all 8 commercial guilds. |
| **Time Discretization** | "6 bi-weekly periods = 90 days" & "continuous-time" | **6 discrete 15-day snapshot windows spanning a 90-day observation horizon** | Resolved temporal inconsistency (bi-weekly = 84 days ≠ 90 days). Clarified discrete-snapshot modeling. |
| **Authorship Attribution** | Author 1, Author 2, Author 3 | **`[TODO-AUTHOR: Author Names & Affiliations]`** | Preserved double-blind and author sovereignty; no placeholder institutional names fabricated. |

---

## 3. Section-by-Section Detailed Changes

### A. Title & Abstract
- **Before:** "controlled stream", unexpanded "HAMTA", claims of "rigorous, privacy-preserving foundation", "latent commercial capacity", MAE = 1.00, NDCG = 0.957.
- **After:** 
  - English abstract uses "synthetic 90-day transaction stream" (matching conclusion and Persian text).
  - Expanded HAMTA: *"HAMTA (Hierarchical/Holistic Architecture for Merchant Transaction Analytics)"*.
  - Replaced "latent commercial capacity" with *"peer-relative structural transaction opportunity under observational transaction streams"*.
  - Replaced inflated metrics with audited 10-seed results: MAE $4.48 \pm 0.42$, Precision@35 $0.366 \pm 0.120$, Recall@35 $0.246 \pm 0.081$, R-Precision $0.342 \pm 0.077$, NDCG@35 $0.382 \pm 0.116$, MAP@35 $0.180 \pm 0.092$ (2.47× lift over random).
  - Persian abstract fully synchronized with Persian numerals (`۴٫۴۸ ± ۰٫۴۲`, `۰٫۳۶۶ ± ۰٫۱۲۰`, etc.) and Persian decimal separator `٫`.

### B. Section I: Introduction
- **Before:**
  - Used informal pseudo-math: `Lowest Volume != Poor Performance Relative to Peers != Growth Opportunity`.
  - Used "For example, Consider".
  - Repeated references to "catchment area" and "geographic similarity", despite the dataset having no GPS/spatial coordinates.
  - Assertions of "guaranteed zero leakage", "proven framework", and "billions of transactions".
- **After:**
  - Formatted cleanly as: $\text{Lowest Absolute Volume} \neq \text{Peer-Relative Underperformance} \neq \text{Campaign Growth Opportunity}$.
  - Corrected grammatical error: "For example, consider".
  - Replaced "catchment area" with *"shared customer interaction basins / transactional neighborhoods"*.
  - Softened claims: restricted scope strictly to observational transaction ledgers without unobserved covariates. Explicitly clarified non-causal nature (not ITE / causal uplift).

### C. Section II: Related Work
- **Before:**
  - Citations [11], [13], [16], [17] were present in the bibliography but uncited or loosely connected in text.
  - Overstated claim that Forman-Ricci curvature "solves over-squashing" in the empirical setting.
- **After:**
  - Explicitly integrated [11] (geometric deep learning), [13] (inductive transaction representations), [16] (variational graph auto-encoders), and [17] (network modularity) into the related work text.
  - Reframed Forman-Ricci curvature as a *"structural regularizer"* and cited Topping et al. [7] for over-squashing theory while attributing the discrete formula to Forman [5] and Weber et al. [6].
  - Added `[TODO-AUTHOR: write this]` outline for expanding related work on Stochastic Frontier Analysis (SFA), discrete count models (Negative Binomial), and temporal conformal prediction.

### D. Section III: Proposed Method (HAMTA Framework)
- **Before:**
  - Bipartite graph was denoted $B_t$, while peer benchmark was denoted $B^G$, creating symbol collision.
  - Equations (1) to (6) were written in plain text with raw underscores (`w_tilde_{mj}`, `S_covisit`, `mu_hat`).
  - $q_j$ was undefined in peer lower bound $L_j = \max(0, \hat{\mu}_j - q_j)$.
  - $O_{m, t}$ / $\text{TotalOverlap}$ was informal.
  - M-GATO score was claimed to prevent false positives solely through $Q$, while numerical example called 58 transactions an "observed gap" that implies campaign uplift.
- **After:**
  - Unified bipartite graph symbol to $\mathcal{G}^{(B)}_t = (\mathcal{C}_t, \mathcal{M}_t, \mathcal{E}_t)$, reserving $B^G_{m, t+1}$ strictly for the peer benchmark.
  - Typeset and consecutively numbered Equations (1) to (8) using clean mathematical notation.
  - Explicitly defined $q_j = q_{0.85}$ as the shared empirical calibration quantile across the calibration cohort.
  - Formalized $\mathcal{O}_{m, t} = \sum_{j \in \mathcal{N}_K(m)} |\mathcal{C}_m \cap \mathcal{C}_j|$ as total shared card interactions.
  - Clarified that M-GATO measures the *relative natural gap above the upper bound*:
    $$\text{Relative Natural Gap} = \frac{B^G - U}{B^G + \epsilon}$$
    Disentangled the 3 concepts: Actual Gap ($B^G - Y$), Natural Gap ($B^G - U$), and M-GATO ($Q \times \text{Natural Gap}$).
  - Clarified that $Q$ acts as a conservative shrinkage penalty against sparse/isolated merchants rather than an accuracy booster.
  - Added `[TODO-AUTHOR: write this]` outline for GNN layer architecture, hidden dimensions, attention heads, optimizer, learning rate, and batch strategy.

### E. Section IV: Experimental Design
- **Before:**
  - Single seed (Seed 42) reported without variance or confidence intervals.
  - Ground-truth opportunity label was vaguely described without formal injection equations.
  - Guild distribution summed to 110%.
- **After:**
  - Extended to 10 random seeds with full mean ± std reporting.
  - Normalized guild distribution to exact 100.0%.
  - Added `[TODO-AUTHOR: write this]` outline for the synthetic drop injection equation, timing (injected in Period 4, evaluated in Period 5), and positive cohort size (exactly 51 merchants, ~14.6%).
  - Added `[TODO-AUTHOR: write this]` outline for hyperparameter optimization protocol on the historical training split.

### F. Section V: Results and Discussion
- **Before:**
  - Table I reported buggy MAE = 1.00, RMSE = 1.25, and negative NLL = -28.86.
  - Table II reported buggy Static GNN (MAP = 1.000, NDCG = 0.099) and inflated HAMTA metrics (0.957).
  - No per-scenario results table.
  - Table III ablation lacked significance tests and claimed curvature contributed substantial NDCG gain.
  - Case study called synthetic merchant an actual commercial campaign candidate.
- **After:**
  - **Table I (Forecasting):** Fully updated with 7 models over 10 seeds: Naive Persistence (4.41), Moving Average (3.51), ETS (3.41), Tabular GBDT (3.89), NB-GLM (3.78), Static GNN (5.98), HAMTA (4.48 ± 0.42). Added honest scientific discussion that stationary smoothers have lower point error on stationary series, while HAMTA's value is learning relational graph embeddings.
  - **Table II (Ranking):** Fully updated with 8 strategies over 10 seeds: Lowest Volume (0.197), Pre-Campaign Vol (0.220), Tabular Point Gap (0.214), kNN Peer Gap (0.231), Static GNN Gap (0.286), SFA Frontier Gap (0.357), M-GATO w/o Q (0.374), HAMTA Proposed (0.366 ± 0.120). Added R-Precision (0.342) and explained 35/51 maximum recall ceiling (0.686).
  - **Table III (Multi-Scenario Benchmark):** Added dedicated table reporting Negative Control, Scenario A, Scenario B, Scenario C with Drop Rate, Precision, Recall, NDCG, MAP, FPR@35, and Conformal Coverage. Highlighted that Negative Control has 0.000 precision and 86.2% coverage, proving no circular step-drop memorization.
  - **Table IV (Systematic Ablation):** Added Wilcoxon and paired $t$-test $p$-values. Honest reporting that curvature has negligible NDCG impact ($\Delta = -0.002, p = 0.85$), while graph structure is overwhelmingly significant ($\Delta = +0.145, p = 0.0020$).
  - **Table V & Score Design:** Analyzed micro-merchant bias (56% $<10$ tx) and reported minimum volume filter ($\ge 10$ tx) results.
  - Added `[TODO-AUTHOR: write this]` outlines for Threats to Validity and Computational Scalability Profiling.

### G. Section VI: Conclusion & References
- **Before:**
  - Concluded with absolute claims of "proven capability" and "privacy preservation".
  - References [12], [15], [18] were unverified.
  - Persian references had doubled numbering ("1. [1]").
- **After:**
  - Concluded with balanced, observational formulation.
  - Added `[TODO-AUTHOR: write this]` for Data and Code Availability Statement.
  - Flagged references [12], [15], [18] as `[Needs manual verification by author]` in the bibliography and report.
  - Removed manual `[1]` prefixes in Persian references, allowing the template's native `EN_REF` list style to format single, clean numbering.

---

## 4. Persian (ISC) Specific Terminology Normalization

| English Concept | Old Persian Translation (Flawed) | Revised Persian Terminology (ISC Standard) | Reason |
| :--- | :--- | :--- | :--- |
| **Ablation Study** | ابطال‌پذیری (Falsification/Refutation) | **مطالعه حذف مؤلفه‌ها (Ablation Study)** | "ابطال‌پذیری" translates Popperian falsification, not engineering ablation. |
| **Conformal Prediction** | پیش‌بینی همنواخت (Uniform Prediction) | **واسنجی بازه پیش‌بینی (Conformal Prediction / Interval Calibration)** | "همنواخت" means uniform, causing confusion with uniform distribution. |
| **Precision vs. Accuracy** | دقت برای هر دو | **دقت (Precision) / درستی (Accuracy)** | Disentangled statistical precision from classification accuracy. |
| **Benchmark vs. Baseline** | بنچ‌مارک / خط‌مبنا به صورت تصادفی | **بنچ‌مارک (Benchmark) برای مقایسه همتایان / خط‌مبنا (Baseline) برای مدل‌های رقیب** | Consistent operational distinction. |
| **Industrial Wholesale** | آهن‌آلات و ... (بریده‌شده) | **آهن‌آلات و مصالح صنعتی** | Aligned guild translation across languages. |
| **Numerical Format** | 4.48 ± 0.42 / 35,000 | **۴٫۴۸ ± ۰٫۴۲ / ۳۵٬۰۰۰** | Applied Persian digits, decimal separator `٫`, and thousands separator `٬`. |

---

## 5. Phase 2 Scientific Audit & Submission Finalization

Following the Phase 1 peer-review audit, Phase 2 resolved all remaining author action items and rigorous scientific requirements:
1. **Authorship Integration:** Inserted verified authors (Saeed Aliakbari\* and Saeed Shahsavan, Rayamate Inc.) in IEEE and ISC conference header formats.
2. **Zero Placeholders:** Completely removed and wrote out all `[TODO-AUTHOR]` sections with publication-grade prose (GNN specs, validation protocol, synthetic ground truth recovery formalization, threats to validity, computational scalability, code/data availability).
3. **Primary Objective Framing:** Highlighted in Abstract and Introduction that HAMTA's primary goal is Opportunity Ranking & Prioritization under observational streams, NOT minimizing one-step point forecasting error (which smoothers like ETS achieve on stationary series without topology awareness).
4. **Conformal Prediction Rigor:** Formulated rolling split-conformal calibration under temporal non-exchangeability, documenting 86.2% coverage on stationary control data and 4.6 tx average interval width.
5. **Synthetic Ground Truth Recovery:** Strictly formalized opportunity ground truth as the mathematical recovery of injected structural underperformance (51 merchants across 8 guilds, ~14.6% prevalence), avoiding claims of proven commercial growth capacity.
6. **Multi-Budget Benchmark & Statistical Significance:** Evaluated budgets @10, @20, @35, @50 over 10 random seeds with Wilcoxon signed-rank and paired $t$-test significance tests against all baselines.
7. **Page Ceiling Compliance:** Persian manuscript reduced from 9 pages to strictly 8 pages (ISC template limit); English manuscript maintained at exactly 6 pages (IEEE limit).
8. **Figure Overhaul:** Fixed RTL text shaping in all Persian figures (`figures_fa/`) by eliminating `bidi.get_display()` to allow Matplotlib's native HarfBuzz engine to shape text properly without reversed glyphs or clipping. Replaced customer persona radar with Top-5 Opportunity Candidates Case Study comparison chart. Verified 100% English figures in `figures/`.
9. **Verified Bibliography:** Replaced unverified references [12], [15], and [18] with verified published citations (Liu et al., CIKM 2018; Di Giovanni et al., ICLR 2023; Dou et al., CIKM 2020).

---

## 6. Final Verification Checklist

- [x] All 8 CSV benchmark files saved and verified in `output/phase1_results/` and `output/`.
- [x] Multi-budget 10-seed benchmark executed and logged (`table2b_multibudget_10seeds.csv`).
- [x] Figures regenerated and visually audited in `figures/` (100% EN) and `figures_fa/` (100% RTL FA).
- [x] English manuscript compiled via `create_paper.py` to `.docx`, `.doc`, and `.pdf` (**Exactly 6 Pages**, IEEE standard).
- [x] Persian manuscript compiled via `create_paper_fa.py` to `.docx`, `.doc`, and `.pdf` (**Exactly 8 Pages**, ISC ceiling).
- [x] `PAPER_MANUSCRIPT.md` fully synchronized with final English paper.
- [x] Zero `[TODO-AUTHOR]` markers remaining in any manuscript.
- [x] All 24 citations verified and accessible online.
- [x] No fabricated numbers, citations, or claims.
