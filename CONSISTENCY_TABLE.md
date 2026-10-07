# Consistency Audit Table: English (IEEE) vs. Persian (ISC)

**Document:** HAMTA Manuscript Consistency Verification  
**English Version:** `From_Transactional_Data_to_Organizational_Intelligence.docx` (Generated via `create_paper.py`)  
**Persian Version:** `FA_From_Transactional_Data_to_Organizational_Intelligence.docx` (Generated via `create_paper_fa.py`)  
**Status:** **100% Numerically, Conceptually, and Terminologically Aligned (Submission-Ready)**  

---

## 1. Document Metadata and Structural Alignment

| Dimension | English Manuscript (IEEE) | Persian Manuscript (ISC) | Alignment Status |
| :--- | :--- | :--- | :---: |
| **Title** | A Temporal Graph AI Framework for Peer-Relative Merchant Opportunity Ranking in Payment Networks | از داده‌های تراکنشی تا هوشمندی سازمانی: چارچوب هوش مصنوعی گراف زمانی برای کشف فرصت‌های پذیرندگان و اولویت‌بندی کمپین‌های بازاریابی (HAMTA) | **Semantically Aligned** |
| **Acronym Expansion** | HAMTA: Holistic Architecture for Merchant Transaction Analytics | HAMTA: معماری سلسله‌مراتبی و جامع برای تحلیل تراکنشی پذیرندگان | **Consistent** |
| **Score Formulation** | M-GATO: Merchant Graph-Aware Transaction Opportunity (Peer-Relative Opportunity Score) | M-GATO: شاخص رتبه‌بندی فرصت همتا-محور آگاه از گراف | **Consistent** |
| **Document Length** | Exactly 6 Pages (Strict IEEE 6-Page Limit) | Exactly 6 Pages (Strict ISC 6-Page Limit) | **100% Compliant (6 / 6)** |
| **Column Layout** | Two-Column, LTR (A4: 210 × 297 mm, Margin: 19 mm top, 25.4 mm bottom) | Two-Column, RTL (A4: 210 × 297 mm, Margin: 52 mm P1 top, 25 mm all bottom) | **Compliant** |
| **Authors** | Saeed Aliakbari\*¹ (Business Intelligence Specialist) & Saeed Shahsavan² (Software Architect), Rayamate Inc., Tehran, Iran | سعید علی اکبری\*¹ (کارشناس هوش تجاری) و سعید شاهسون² (معمار نرم‌افزار)، شرکت رایامیت، تهران، ایران | **Identical** |
| **Author Emails** | saeed.aliakbari@rayamate.ir / saeed.shahsavan@rayamate.ir (Explicit LTR run) | saeed.aliakbari@rayamate.ir / saeed.shahsavan@rayamate.ir (w:bidi val="0") | **Non-Inverted LTR** |
| **Total References** | 27 References (All Verified, Consecutively Numbered 1..27) | 27 References (All Verified, Consecutively Numbered 1..27) | **1:1 Match (27/27)** |

---

## 2. Mathematical Formalism and Symbolic Consistency

| Mathematical Concept | English Symbol / Formula | Persian Symbol / Formula | Status |
| :--- | :--- | :--- | :---: |
| **Ledger Event** | $e_k = (\text{pan}_k, \text{amount}_k, \text{merchant\_id}_k, \text{create\_date}_k, \text{cast\_name}_k)$ | $e_k = (\text{pan}_k, \text{amount}_k, \text{merchant\_id}_k, \text{create\_date}_k, \text{cast\_name}_k)$ | **Identical** |
| **Bipartite Graph** | $G^{(B)}_t = (C_t, M_t, E_t)$ (binary interaction edge) | $G^{(B)}_t = (C_t, M_t, E_t)$ (یال تراکنش دودویی) | **Identical** |
| **Peer Similarity** | $S(m, j) = \lambda S_{\text{covisit}}(m, j) + (1 - \lambda) S_{\text{category}}(m, j)$ | $S(m, j) = \lambda \cdot S_{\text{covisit}}(m, j) + (1 - \lambda) \cdot S_{\text{category}}(m, j)$ | **Identical** |
| **Similarity Weight** | $\lambda = 0.65$ | $\lambda = 0.65$ (۰٫۶۵) | **Identical** |
| **Peer Symmetrization** | $G_{\text{peer}} = \text{Top-}K \cup \text{Top-}K^T$ | $G_{\text{peer}} = \text{Top-}K \cup \text{Top-}K^T$ | **Identical** |
| **Normalized Forman Curvature** | $F(m, j) = \frac{4 - d(m) - d(j) + 3\Delta(m, j)}{\sqrt{d(m)d(j)}}$ | $F(m, j) = \frac{4 - d(m) - d(j) + 3\Delta(m, j)}{\sqrt{d(m)d(j)}}$ | **Identical** |
| **Curvature Modulation** | $\tilde{w}_{mj} \propto w_{mj}(1 + \eta \tanh(F(m, j))), \eta = 0.25$ | $\tilde{w}_{mj} \propto w_{mj}(1 + \eta \tanh(F(m, j))), \eta = 0.25$ (۰٫۲۵) | **Identical** |
| **Forecast Likelihood** | Negative Binomial PMF ($L_{\text{NB}}$) with dispersion $\phi$ | Negative Binomial PMF ($L_{\text{NB}}$) with dispersion $\phi$ | **Identical** |
| **Overdispersion Ratio** | $\text{Var}(Y) / \mathbb{E}[Y] \approx 3.24$ | $\text{Var}(Y) / \mathbb{E}[Y] \approx 3.24$ (۳٫۲۴) | **Identical** |
| **Upper Natural Bound** | $U_{m, t+1} = \hat{\mu}_{m, t+1} + q_{0.85}$ (P4 clean calibration) | $U_{m, t+1} = \hat{\mu}_{m, t+1} + q_{0.85}$ (دوره ۴ واسنجی تمیز) | **Identical** |
| **Peer Benchmark** | $B^G_{m, t+1} = \frac{\sum_{j \in N_K(m)} \tilde{w}_{mj} L_{j, t+1}}{\sum_{j \in N_K(m)} \tilde{w}_{mj}}$ | $B^G_{m, t+1} = \frac{\sum_{j \in N_K(m)} \tilde{w}_{mj} L_{j, t+1}}{\sum_{j \in N_K(m)} \tilde{w}_{mj}}$ | **Identical** |
| **Forecast-Bound Peer Gap** | $B^G_{m, t+1} - U_{m, t+1}$ | $B^G_{m, t+1} - U_{m, t+1}$ | **Identical** |
| **Graph Support** | $Q_{m, t} = 1 - \exp(-O_{m, t} / \kappa), \kappa = 18.0$ | $Q_{m, t} = 1 - \exp(-O_{m, t} / \kappa), \kappa = 18.0$ (۱۸٫۰) | **Identical** |
| **M-GATO Score** | $\text{M-GATO}_{m, t} = Q_{m, t} \cdot \left[ \frac{B^G_{m, t+1} - U_{m, t+1}}{B^G_{m, t+1} + \epsilon} \right]_+$ | $\text{M-GATO}_{m, t} = Q_{m, t} \cdot \left[ \frac{B^G_{m, t+1} - U_{m, t+1}}{B^G_{m, t+1} + \epsilon} \right]_+$ | **Identical** |

---

## 3. Empirical Benchmark Consistency Across Tables (10 Seeds)

### Table I: Natural Forecasting Accuracy Benchmark (Period 5, Unperturbed Series)
| Model | English Value (MAE / RMSE / sMAPE / NB NLL) | Persian Value (MAE / RMSE / sMAPE / NB NLL) | Consistent? |
| :--- | :--- | :--- | :---: |
| **Naive Persistence** | 4.41 ± 0.20 / 5.78 ± 0.37 / 32.40% ± 1.49% / — | ۴٫۴۱ ± ۰٫۲۰ / ۵٫۷۸ ± ۰٫۳۷ / ۳۲٫۴۰٪ ± ۱٫۴۹٪ / — | **Yes** |
| **Moving Average (3P)**| 3.51 ± 0.19 / 4.58 ± 0.28 / 26.05% ± 1.03% / — | ۳٫۵۱ ± ۰٫۱۹ / ۴٫۵۸ ± ۰٫۲۸ / ۲۶٫۰۵٪ ± ۱٫۰۳٪ / — | **Yes** |
| **Exponential Smoothing**| 3.41 ± 0.16 / 4.46 ± 0.28 / 25.42% ± 0.92% / — | ۳٫۴۱ ± ۰٫۱۶ / ۴٫۴۶ ± ۰٫۲۸ / ۲۵٫۴۲٪ ± ۰٫۹۲٪ / — | **Yes** |
| **Tabular GBDT** | 3.89 ± 0.12 / 5.31 ± 0.42 / 27.68% ± 0.79% / — | ۳٫۸۹ ± ۰٫۱۲ / ۵٫۳۱ ± ۰٫۴۲ / ۲۷٫۶۸٪ ± ۰٫۷۹٪ / — | **Yes** |
| **NB-GLM (Category)** | 3.78 ± 0.20 / 4.96 ± 0.38 / 27.55% ± 1.06% / 3.17 ± 0.02 | ۳٫۷۸ ± ۰٫۲۰ / ۴٫۹۶ ± ۰٫۳۸ / ۲۷٫۵۵٪ ± ۱٫۰۶٪ / ۳٫۱۷ ± ۰٫۰۲ | **Yes** |
| **Static GNN (Bipartite)**| 5.98 ± 0.54 / 7.56 ± 0.77 / 38.67% ± 2.13% / 3.31 ± 0.03 | ۵٫۹۸ ± ۰٫۵۴ / ۷٫۵۶ ± ۰٫۷۷ / ۳۸٫۶۷٪ ± ۲٫۱۳٪ / ۳٫۳۱ ± ۰٫۰۳ | **Yes** |
| **HAMTA Temporal (Ours)**| **4.48 ± 0.42 / 5.86 ± 0.58 / 31.37% ± 2.11% / 3.51 ± 0.31** | **۴٫۴۸ ± ۰٫۴۲ / ۵٫۸۶ ± ۰٫۵۸ / ۳۱٫۳۷٪ ± ۲٫۱۱٪ / ۳٫۵۱ ± ۰٫۳۱** | **Yes** |

---

### Table II: Campaign Prioritization Benchmark (Top-35 Budget)
| Strategy / Model | English Value (P@35 / Rec@35 / R-Prec / NDCG@35 / MAP@35) | Persian Value (P@35 / Rec@35 / R-Prec / NDCG@35 / MAP@35) | Consistent? |
| :--- | :--- | :--- | :---: |
| **Lowest Volume Heuristic** | 0.197 ± 0.050 / 0.133 ± 0.034 / 0.194 ± 0.052 / 0.203 ± 0.053 / 0.059 ± 0.028 | ۰٫۱۹۷ ± ۰٫۰۵۰ / ۰٫۱۳۳ ± ۰٫۰۳۴ / ۰٫۱۹۴ ± ۰٫۰۵۲ / ۰٫۲۰۳ ± ۰٫۰۵۳ / ۰٫۰۵۹ ± ۰٫۰۲۸ | **Yes** |
| **Recent Volume (P4)** | 0.220 ± 0.054 / 0.148 ± 0.036 / 0.202 ± 0.032 / 0.245 ± 0.074 / 0.082 ± 0.039 | ۰٫۲۲۰ ± ۰٫۰۵۴ / ۰٫۱۴۸ ± ۰٫۰۳۶ / ۰٫۲۰۲ ± ۰٫۰۳۲ / ۰٫۲۴۵ ± ۰٫۰۷۴ / ۰٫۰۸۲ ± ۰٫۰۳۹ | **Yes** |
| **Tabular Point Gap (GBDT)**| 0.214 ± 0.060 / 0.144 ± 0.041 / 0.188 ± 0.042 / 0.237 ± 0.078 / 0.082 ± 0.046 | ۰٫۲۱۴ ± ۰٫۰۶۰ / ۰٫۱۴۴ ± ۰٫۰۴۱ / ۰٫۱۸۸ ± ۰٫۰۴۲ / ۰٫۲۳۷ ± ۰٫۰۷۸ / ۰٫۰۸۲ ± ۰٫۰۴۶ | **Yes** |
| **kNN Peer Benchmark Gap** | 0.231 ± 0.053 / 0.156 ± 0.036 / 0.221 ± 0.035 / 0.241 ± 0.071 / 0.080 ± 0.039 | ۰٫۲۳۱ ± ۰٫۰۵۳ / ۰٫۱۵۶ ± ۰٫۰۳۶ / ۰٫۲۲۱ ± ۰٫۰۳۵ / ۰٫۲۴۱ ± ۰٫۰۷۱ / ۰٫۰۸۰ ± ۰٫۰۳۹ | **Yes** |
| **Static GNN Gap** | 0.286 ± 0.068 / 0.192 ± 0.046 / 0.287 ± 0.056 / 0.310 ± 0.075 / 0.124 ± 0.052 | ۰٫۲۸۶ ± ۰٫۰۶۸ / ۰٫۱۹۲ ± ۰٫۰۴۶ / ۰٫۲۸۷ ± ۰٫۰۵۶ / ۰٫۳۱۰ ± ۰٫۰۷۵ / ۰٫۱۲۴ ± ۰٫۰۵۲ | **Yes** |
| **SFA-Style Frontier Gap** | 0.357 ± 0.079 / 0.240 ± 0.053 / 0.323 ± 0.075 / 0.383 ± 0.081 / 0.171 ± 0.055 | ۰٫۳۵۷ ± ۰٫۰۷۹ / ۰٫۲۴۰ ± ۰٫۰۵۳ / ۰٫۳۲۳ ± ۰٫۰۷۵ / ۰٫۳۸۳ ± ۰٫۰۸۱ / ۰٫۱۷۱ ± ۰٫۰۵۵ | **Yes** |
| **M-GATO w/o Support (Q=1)** | 0.374 ± 0.117 / 0.252 ± 0.079 / 0.342 ± 0.069 / 0.396 ± 0.102 / 0.184 ± 0.083 | ۰٫۳۷۴ ± ۰٫۱۱۷ / ۰٫۲۵۲ ± ۰٫۰۷۹ / ۰٫۳۴۲ ± ۰٫۰۶۹ / ۰٫۳۹۶ ± ۰٫۱۰۲ / ۰٫۱۸۴ ± ۰٫۰۸۳ | **Yes** |
| **HAMTA Proposed (M-GATO)** | **0.366 ± 0.120 / 0.246 ± 0.081 / 0.342 ± 0.077 / 0.382 ± 0.116 / 0.180 ± 0.092** | **۰٫۳۶۶ ± ۰٫۱۲۰ / ۰٫۲۴۶ ± ۰٫۰۸۱ / ۰٫۳۴۲ ± ۰٫۰۷۷ / ۰٫۳۸۲ ± ۰٫۱۱۶ / ۰٫۱۸۰ ± ۰٫۰۹۲** | **Yes** |

---

### Table III: Multi-Budget Benchmark Evaluation (10 Seeds)
| Budget ($K$) | Strategy | English Metrics (Prec@K / Recall@K / NDCG@K) | Persian Metrics (Prec@K / Recall@K / NDCG@K) | Consistent? |
| :---: | :--- | :--- | :--- | :---: |
| **10** | Lowest Volume Heuristic | 0.210 ± 0.104 / 0.040 ± 0.020 / 0.217 ± 0.145 | ۰٫۲۱۰ ± ۰٫۱۰۴ / ۰٫۰۴۰ ± ۰٫۰۲۰ / ۰٫۲۱۷ ± ۰٫۱۴۵ | **Yes** |
| **10** | Tabular GBDT Gap | 0.270 ± 0.168 / 0.052 ± 0.032 / 0.285 ± 0.183 | ۰٫۲۷۰ ± ۰٫۱۶۸ / ۰٫۰۵۲ ± ۰٫۰۳۲ / ۰٫۲۸۵ ± ۰٫۱۸۳ | **Yes** |
| **10** | Static GNN Gap | 0.370 ± 0.110 / 0.071 ± 0.021 / 0.376 ± 0.127 | ۰٫۳۷۰ ± ۰٫۱۱۰ / ۰٫۰۷۱ ± ۰٫۰۲۱ / ۰٫۳۷۶ ± ۰٫۱۲۷ | **Yes** |
| **10** | SFA Frontier Gap | 0.430 ± 0.127 / 0.083 ± 0.024 / 0.453 ± 0.154 | ۰٫۴۳۰ ± ۰٫۱۲۷ / ۰٫۰۸۳ ± ۰٫۰۲۴ / ۰٫۴۵۳ ± ۰٫۱۵۴ | **Yes** |
| **10** | **HAMTA Proposed (M-GATO)** | **0.400 ± 0.089 / 0.077 ± 0.017 / 0.410 ± 0.101** | **۰٫۴۰۰ ± ۰٫۰۸۹ / ۰٫۰۷۷ ± ۰٫۰۱۷ / ۰٫۴۱۰ ± ۰٫۱۰۱** | **Yes** |
| **20** | Lowest Volume Heuristic | 0.200 ± 0.074 / 0.077 ± 0.029 / 0.207 ± 0.091 | ۰٫۲۰۰ ± ۰٫۰۷۴ / ۰٫۰۷۷ ± ۰٫۰۲۹ / ۰٫۲۰۷ ± ۰٫۰۹۱ | **Yes** |
| **20** | Tabular GBDT Gap | 0.265 ± 0.125 / 0.102 ± 0.048 / 0.275 ± 0.128 | ۰٫۲۶۵ ± ۰٫۱۲۵ / ۰٫۱۰۲ ± ۰٫۰۴۸ / ۰٫۲۷۵ ± ۰٫۱۲۸ | **Yes** |
| **20** | Static GNN Gap | 0.335 ± 0.110 / 0.129 ± 0.042 / 0.349 ± 0.102 | ۰٫۳۳۵ ± ۰٫۱۱۰ / ۰٫۱۲۹ ± ۰٫۰۴۲ / ۰٫۳۴۹ ± ۰٫۱۰۲ | **Yes** |
| **20** | SFA Frontier Gap | 0.345 ± 0.104 / 0.133 ± 0.040 / 0.385 ± 0.111 | ۰٫۳۴۵ ± ۰٫۱۰۴ / ۰٫۱۳۳ ± ۰٫۰۴۰ / ۰٫۳۸۵ ± ۰٫۱۱۱ | **Yes** |
| **20** | **HAMTA Proposed (M-GATO)** | **0.410 ± 0.109 / 0.158 ± 0.042 / 0.414 ± 0.105** | **۰٫۴۱۰ ± ۰٫۱۰۹ / ۰٫۱۵۸ ± ۰٫۰۴۲ / ۰٫۴۱۴ ± ۰٫۱۰۵** | **Yes** |
| **35** | Lowest Volume Heuristic | 0.197 ± 0.050 / 0.133 ± 0.034 / 0.203 ± 0.053 | ۰٫۱۹۷ ± ۰٫۰۵۰ / ۰٫۱۳۳ ± ۰٫۰۳۴ / ۰٫۲۰۳ ± ۰٫۰۵۳ | **Yes** |
| **35** | Tabular GBDT Gap | 0.214 ± 0.060 / 0.144 ± 0.041 / 0.237 ± 0.078 | ۰٫۲۱۴ ± ۰٫۰۶۰ / ۰٫۱۴۴ ± ۰٫۰۴۱ / ۰٫۲۳۷ ± ۰٫۰۷۸ | **Yes** |
| **35** | Static GNN Gap | 0.286 ± 0.068 / 0.192 ± 0.046 / 0.310 ± 0.075 | ۰٫۲۸۶ ± ۰٫۰۶۸ / ۰٫۱۹۲ ± ۰٫۰۴۶ / ۰٫۳۱۰ ± ۰٫۰۷۵ | **Yes** |
| **35** | SFA Frontier Gap | 0.357 ± 0.079 / 0.240 ± 0.053 / 0.383 ± 0.081 | ۰٫۳۵۷ ± ۰٫۰۷۹ / ۰٫۲۴۰ ± ۰٫۰۵۳ / ۰٫۳۸۳ ± ۰٫۰۸۱ | **Yes** |
| **35** | **HAMTA Proposed (M-GATO)** | **0.366 ± 0.114 / 0.246 ± 0.077 / 0.382 ± 0.110** | **۰٫۳۶۶ ± ۰٫۱۱۴ / ۰٫۲۴۶ ± ۰٫۰۷۷ / ۰٫۳۸۲ ± ۰٫۱۱۰** | **Yes** |
| **50** | Lowest Volume Heuristic | 0.192 ± 0.048 / 0.185 ± 0.046 / 0.198 ± 0.044 | ۰٫۱۹۲ ± ۰٫۰۴۸ / ۰٫۱۸۵ ± ۰٫۰۴۶ / ۰٫۱۹۸ ± ۰٫۰۴۴ | **Yes** |
| **50** | Tabular GBDT Gap | 0.188 ± 0.046 / 0.181 ± 0.044 / 0.214 ± 0.063 | ۰٫۱۸۸ ± ۰٫۰۴۶ / ۰٫۱۸۱ ± ۰٫۰۴۴ / ۰٫۲۱۴ ± ۰٫۰۶۳ | **Yes** |
| **50** | Static GNN Gap | 0.288 ± 0.060 / 0.277 ± 0.058 / 0.307 ± 0.065 | ۰٫۲۸۸ ± ۰٫۰۶۰ / ۰٫۲۷۷ ± ۰٫۰۵۸ / ۰٫۳۰۷ ± ۰٫۰۶۵ | **Yes** |
| **50** | SFA Frontier Gap | 0.322 ± 0.079 / 0.310 ± 0.076 / 0.352 ± 0.081 | ۰٫۳۲۲ ± ۰٫۰۷۹ / ۰٫۳۱۰ ± ۰٫۰۷۶ / ۰٫۳۵۲ ± ۰٫۰۸۱ | **Yes** |
| **50** | **HAMTA Proposed (M-GATO)** | **0.340 ± 0.072 / 0.327 ± 0.069 / 0.360 ± 0.080** | **۰٫۳۴۰ ± ۰٫۰۷۲ / ۰٫۳۲۷ ± ۰٫۰۶۹ / ۰٫۳۶۰ ± ۰٫۰۸۰** | **Yes** |

---

### Table IV: Multi-Scenario Benchmark Evaluation (10 Seeds)
| Scenario | English Metrics (Drop / Prec@35 / NDCG@35 / FPR@35 / Coverage) | Persian Metrics (Drop / Prec@35 / NDCG@35 / FPR@35 / Coverage) | Consistent? |
| :--- | :--- | :--- | :---: |
| **Scenario 0 (Negative Control)** | 0.00 / 0.000 ± 0.000 / 0.000 ± 0.000 / 0.100 ± 0.000 / 86.2% ± 3.1% | ۰٫۰۰ / ۰٫۰۰۰ ± ۰٫۰۰۰ / ۰٫۰۰۰ ± ۰٫۰۰۰ / ۰٫۱۰۰ ± ۰٫۰۰۰ / ۸۶٫۲٪ ± ۳٫۱٪ | **Yes** |
| **Scenario A (Weak Drop, d=0.18)** | 0.18 / 0.229 ± 0.084 / 0.264 ± 0.075 / 0.077 ± 0.012 / 81.9% ± 2.8% | ۰٫۱۸ / ۰٫۲۲۹ ± ۰٫۰۸۴ / ۰٫۲۶۴ ± ۰٫۰۷۵ / ۰٫۰۷۷ ± ۰٫۰۱۲ / ۸۱٫۹٪ ± ۲٫۸٪ | **Yes** |
| **Scenario B (Medium Drop, d=0.32)**| 0.32 / 0.366 ± 0.120 / 0.382 ± 0.116 / 0.063 ± 0.017 / 80.7% ± 3.3% | ۰٫۳۲ / ۰٫۳۶۶ ± ۰٫۱۲۰ / ۰٫۳۸۲ ± ۰٫۱۱۶ / ۰٫۰۶۳ ± ۰٫۰۱۷ / ۸۰٫۷٪ ± ۳٫۳٪ | **Yes** |
| **Scenario C (Strong Drop, d=0.48)**| 0.48 / 0.480 ± 0.108 / 0.505 ± 0.098 / 0.052 ± 0.015 / 80.3% ± 3.5% | ۰٫۴۸ / ۰٫۴۸۰ ± ۰٫۱۰۸ / ۰٫۵۰۵ ± ۰٫۰۹۸ / ۰٫۰۵۲ ± ۰٫۰۱۵ / ۸۰٫۳٪ ± ۳٫۵٪ | **Yes** |

---

### Table V: Systematic Component Ablation Study (10 Seeds)
| Architecture Variant | English Value (NDCG@35 / Prec@35 / Δ NDCG / Significance) | Persian Value (NDCG@35 / Prec@35 / Δ NDCG / Significance) | Consistent? |
| :--- | :--- | :--- | :---: |
| **Full HAMTA Proposed** | **0.382 ± 0.116 / 0.366 ± 0.120 / Reference / Baseline** | **۰٫۳۸۲ ± ۰٫۱۱۶ / ۰٫۳۶۶ ± ۰٫۱۲۰ / مبنا / رفرنس** | **Yes** |
| **w/o Curvature Mod. (η=0)** | 0.384 ± 0.118 / 0.369 ± 0.122 / -0.002 / p = 0.8457 | ۰٫۳۸۴ ± ۰٫۱۱۸ / ۰٫۳۶۹ ± ۰٫۱۲۲ / -۰٫۰۰۲ / p = ۰٫۸۴۵۷ | **Yes** |
| **w/o Graph Support (Q=1)** | 0.396 ± 0.102 / 0.374 ± 0.117 / -0.014 / p = 0.4922 | ۰٫۳۹۶ ± ۰٫۱۰۲ / ۰٫۳۷۴ ± ۰٫۱۱۷ / -۰٫۰۱۴ / p = ۰٫۴۹۲۲ | **Yes** |
| **w/o Uncertainty Bounds (U)**| 0.415 ± 0.095 / 0.386 ± 0.105 / -0.033 / p = 0.0273 | ۰٫۴۱۵ ± ۰٫۰۹۵ / ۰٫۳۸۶ ± ۰٫۱۰۵ / -۰٫۰۳۳ / p = ۰٫۰۲۷۳ | **Yes** |
| **w/o Graph Benchmark (B_guild)**| 0.334 ± 0.089 / 0.311 ± 0.094 / +0.048 / p = 0.0371 | ۰٫۳۳۴ ± ۰٫۰۸۹ / ۰٫۳۱۱ ± ۰٫۰۹۴ / +۰٫۰۴۸ / p = ۰٫۰۳۷۱ | **Yes** |
| **w/o Temporal Dynamic (Static)**| 0.310 ± 0.075 / 0.286 ± 0.068 / +0.072 / p = 0.0840 | ۰٫۳۱۰ ± ۰٫۰۷۵ / ۰٫۲۸۶ ± ۰٫۰۶۸ / +۰٫۰۷۲ / p = ۰٫۰۸۴۰ | **Yes** |
| **w/o Graph (Tabular GBDT)** | 0.237 ± 0.078 / 0.214 ± 0.060 / +0.145 / p = 0.0020 | ۰٫۲۳۷ ± ۰٫۰۷۸ / ۰٫۲۱۴ ± ۰٫۰۶۰ / +۰٫۱۴۵ / p = ۰٫۰۰۲۰ | **Yes** |

---

## 4. Submission Verification Checklist

- [x] **Strict 6-Page Limit:** Both English (IEEE) and Persian (ISC) compile to exactly 6 pages (`PAGES=6`).
- [x] **Clean Calibration Protocol:** Clean historical calibration on Period 4 decoupled from injected synthetic drops in Period 5.
- [x] **Page Margins (25 mm):** Persian bottom margin set strictly to 25 mm (`Cm(2.5)`) on all pages; blue `25 mm` guide arrows removed.
- [x] **Single-Page Header Banner:** Repeating conference banner on pages 2–6 removed in Persian; present strictly on Page 1.
- [x] **Author Affiliations:** "کارشناس هوش تجاری" (Business Intelligence Specialist) and "معمار نرم‌افزار" (Software Architect) applied.
- [x] **BiDi Email Alignment:** Email runs wrapped in `<w:bidi w:val="0"/>` and Times New Roman font to prevent reversed punctuation.
- [x] **Readable Figures:** Figures enlarged to 5.8–6.0 cm width with clear captions (7.6–8.0 pt) and crisp resolution.
- [x] **IEEE Abstract Compliant:** Zero math symbols, `@`, `±`, or citations in English Abstract per IEEE requirements.
- [x] **ISC Persian Abstract Compliant:** Under 200 words (185 words) per ISC conference requirements.
- [x] **Consecutive Bibliography:** 27 references consecutively numbered 1..27 in strict order of appearance in text.
- [x] **2025/2026 Literature:** Integrated recent Dynamic GNN survey (2025) and Non-exchangeable Conformal Prediction for Temporal GNNs (KDD 2025).
