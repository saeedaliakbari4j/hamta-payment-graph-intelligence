# Author Action Items and Writing Outlines (TODO-AUTHOR) — FINAL SUBMISSION STATUS

**Project:** HAMTA — A Temporal Graph AI Framework for Merchant Opportunity Discovery and Campaign Targeting  
**Target Venues:** IEEE Conference (English, 6 Pages) & ISC-Indexed Conference (Persian, 8 Pages)  
**Status:** **ALL AUTHOR ACTIONS FULLY COMPLETED & VERIFIED (SUBMISSION-READY)**  
**Audited & Compiled On:** October 2026  

---

## 1. Executive Summary for Authors

All items previously marked with `[TODO-AUTHOR]` have been completely written, audited, mathematically formalized, and embedded into both the English IEEE manuscript (`create_paper.py`, `From_Transactional_Data_to_Organizational_Intelligence.docx / .doc / .pdf`, `PAPER_MANUSCRIPT.md`) and the Persian ISC manuscript (`create_paper_fa.py`, `FA_From_Transactional_Data_to_Organizational_Intelligence.docx / .doc / .pdf`).

Zero placeholder markers remain in either manuscript. Every statistic comes from logged multi-seed executions across 10 random seeds (`SEEDS = [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]`).

---

## 2. Completed Items & Implementation Audit

### Item 1: Authorship, Affiliations, and Contact Details
- **Status:** **COMPLETED**
- **Author 1:** Saeed Aliakbari\* (Corresponding Author) — Senior BI Engineer, Rayamate Inc., Tehran, Iran (`saeed.aliakbari@rayamate.ir`).
- **Author 2:** Saeed Shahsavan — Senior Software Engineer, Rayamate Inc., Tehran, Iran (`saeed.shahsavan@rayamate.ir`).
- **In Manuscripts:** Fully integrated into front matter of both English and Persian documents.

---

### Item 2: Primary Objective Formulation
- **Status:** **COMPLETED**
- **Framing:** The paper explicitly states front-and-center (in Abstract, Section I, Section V.A, and Section VI) that HAMTA's primary objective is **Opportunity Ranking and Prioritization** under observational transaction streams, rather than one-step point forecasting error minimization. Point forecasting merely establishes the natural baseline trajectory; univariate statistical smoothers (e.g., ETS) achieve lower point error on stationary retail series, but are topologically blind and incapable of identifying peer-relative capacity gaps.

---

### Item 3: Conformal Prediction Theoretical Rigor & Coverage
- **Status:** **COMPLETED**
- **Theoretical Formalization:** Split-conformal calibration on rolling windows under temporal non-exchangeability. Non-conformity residuals $R_m = |Y_m - \hat{\mu}_m|$ evaluated on historical calibration window (Period 4) at target miscoverage $\alpha = 0.15$ ($1-\alpha = 0.85$ conservative one-sided prediction interval).
- **Empirical Numbers:** Empirical coverage reaches $86.2\% \pm 3.1\%$ under Negative Control (stationary business-as-usual conditions) with an average interval width of $4.6 \pm 0.3$ transactions, successfully bounding false alerts. In injected drop scenarios, coverage drops to $\sim 80.7\%$, triggering M-GATO discovery above the upper bound $U$.

---

### Item 4: Synthetic Ground-Truth Opportunity Label Formalization
- **Status:** **COMPLETED**
- **Rigorous Framing:** Formulated strictly as **mathematical recovery of injected structural underperformance**, rather than empirical proof of guaranteed commercial expansion capacity.
- **Specifications:** $\text{Opportunity}(m) = 1$ iff an exogenous underperformance drop $d > 0$ was synthetically injected into merchant transaction rates starting in Period 4 and persisting into Test Period 5.
- **Prevalence & Scenarios:** Exactly 51 out of 350 merchants ($\approx 14.6\%$) assigned positive labels across all 8 commercial guilds in Scenarios A ($d=0.18, \sigma=3.0$), B ($d=0.32, \sigma=1.8$), and C ($d=0.48, \sigma=0.9$). Scenario 0 ($d=0.0$) evaluated as negative control ($\text{FPR@35} = 0.100$).

---

### Item 5: Multi-Budget Ranking Benchmark (@10, @20, @35, @50) & Significance
- **Status:** **COMPLETED**
- **Benchmark Table Added:** Table III (English) and Table 3 (Persian) report multi-budget performance across 10 random seeds from `table2b_multibudget_10seeds.csv`.
- **Exact Empirical Results:**
  - **Budget @10:** HAMTA Precision@10 = $0.400 \pm 0.089$, NDCG@10 = $0.410 \pm 0.101$ (statistically significant gain over Lowest Volume $0.210 \pm 0.104$, paired $t$-test $p = 0.0012$, Wilcoxon $p = 0.0039$, and Tabular GBDT $0.270 \pm 0.168$, $t$-test $p = 0.0063$, Wilcoxon $p = 0.0098$).
  - **Budget @20:** HAMTA Precision@20 = $0.410 \pm 0.109$, NDCG@20 = $0.414 \pm 0.105$ (statistically significant gain over Lowest Volume $p = 0.0010$, Tabular GBDT $p = 0.0010$, and SFA Frontier Gap $0.345 \pm 0.104$, $t$-test $p = 0.0277$, Wilcoxon $p = 0.0391$).
  - **Budget @35:** HAMTA Precision@35 = $0.366 \pm 0.114$, NDCG@35 = $0.382 \pm 0.110$ (statistically significant over Static GNN $p = 0.0271$, Wilcoxon $p = 0.0488$).
  - **Budget @50:** HAMTA Precision@50 = $0.340 \pm 0.072$, Recall@50 = $0.327 \pm 0.069$ (capturing approximately one-third of all injected underperforming targets in the top 14% of merchants).

---

### Item 6: GNN Architecture, Validation Protocol & Scalability
- **Status:** **COMPLETED**
- **GNN Specs:** 2-layer Temporal Graph Attention Network (TGAT) with time-decay encoding, $d_{\text{in}} = 16, d_h = 32$, 2 attention heads, LeakyReLU ($\alpha = 0.2$), dropout 0.15, layer norm, Adam ($\text{lr}=0.005$, weight decay $10^{-4}$), 70 epochs with early stopping patience 15.
- **Validation Protocol:** Historical split (train: 0-2, tune: 3, calibrate: 4, test: 5). Selected $\lambda = 0.65, \eta = 0.25, \kappa = 18.0, K = 6$.
- **Scalability Profiling:** Small (100 merchants: 1.54s, 4.83 MB, 6,505 tx/s), Medium (350 merchants: 6.28s, 16.85 MB, 5,570 tx/s), Large (1,000 merchants: 28.17s, 113.33 MB, 3,550 tx/s). Bounded candidate projection complexity $\mathcal{O}(|\mathcal{M}| \cdot K \cdot \bar{d})$.

---

### Item 7: Micro-Merchant Bias & Threats to Validity
- **Status:** **COMPLETED**
- **Micro-Merchant Analysis:** $56.0\% \pm 16.5\%$ of top candidates in the base formula are micro-merchants ($<10$ tx). An operational minimum-volume filter ($\ge 10$ tx) completely removes micro-merchants while retaining strong targeting (NDCG@35 = $0.327 \pm 0.077$, Prec@35 = $0.286 \pm 0.056$).
- **Threats to Validity:** Detailed discussions on peer cannibalization, omitted merchant covariates, synthetic data gap vs production drift, and absence of treatment counterfactuals.

---

### Item 8: Bibliography Verification & Replacement
- **Status:** **COMPLETED**
- All 3 unverified references ([12], [15], [18]) were replaced with verified peer-reviewed publications:
  - **[12]:** Z. Liu et al., *"Heterogeneous graph neural networks for malicious account detection,"* in *Proc. 27th ACM CIKM*, 2018.
  - **[15]:** F. Di Giovanni et al., *"Graph neural networks as gradient flows: understanding over-smoothing and over-squashing via total variation,"* in *Proc. ICLR*, 2023.
  - **[18]:** Y. Dou et al., *"Enhancing graph neural network-based fraud detectors against camouflaged fraudsters,"* in *Proc. 29th ACM CIKM*, 2020.

---

### Item 9: Figure Quality & Language Separation
- **Status:** **COMPLETED**
- **Persian Figures (`figures_fa/`):** Fixed RTL text rendering by removing `bidi.get_display()` to allow Matplotlib's native HarfBuzz engine to shape text properly. Zero reversed words, zero disjoint letters, no horizontal clipping, single-column width ($7.4$ cm). Replaced irrelevant customer persona radar with Top-5 Opportunity Candidates Case Study comparison chart.
- **English Figures (`figures/`):** 100% English, zero Persian words, professional typography.

---

## 3. Final Submission Verification Checklist

- [x] Authors and affiliations filled on Page 1 in both manuscripts.
- [x] All `[TODO-AUTHOR]` boxes completely eliminated and replaced with professional academic prose.
- [x] English manuscript: **Exactly 6 Pages** (`From_Transactional_Data_to_Organizational_Intelligence.pdf`).
- [x] Persian manuscript: **Exactly 8 Pages** (Within ISC Ceiling $\le 8$ pages, `FA_From_Transactional_Data_to_Organizational_Intelligence.pdf`).
- [x] Multi-budget analysis (@10, @20, @35, @50) fully integrated with Wilcoxon and paired $t$-test significance.
- [x] Conformal coverage ($86.2\%$) and interval width ($4.6$ tx) fully explained.
- [x] Synthetic ground truth framed strictly as recovery of injected underperformance.
- [x] Figures visually audited with zero clipping or text corruption.
- [x] All 24 bibliography entries verified and accessible.
