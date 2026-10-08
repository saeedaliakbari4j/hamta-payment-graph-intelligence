import os
import pandas as pd
import numpy as np

# Load tables
fc_path = "output/phase1_results/table1_forecasting_benchmark_10seeds.csv"
rk_path = "output/phase1_results/table2_ranking_benchmark_10seeds.csv"
mb_path = "output/phase1_results/table2b_multibudget_10seeds.csv"
sc_path = "output/phase1_results/table3_scenarios_benchmark_10seeds.csv"
ab_path = "output/phase1_results/table4_ablation_study_10seeds.csv"
sig_path = "output/phase1_results/audit_significance_tests.csv"

df_fc = pd.read_csv(fc_path)
df_rk = pd.read_csv(rk_path)
df_mb = pd.read_csv(mb_path)
df_sc = pd.read_csv(sc_path)
df_ab = pd.read_csv(ab_path)
df_sig = pd.read_csv(sig_path)

print("="*60)
print("AUDIT: TABLES DATA INTEGRITY")
print("="*60)

with open("create_paper.py", "r", encoding="utf-8") as f:
    text_en = f.read()

with open("create_paper_fa.py", "r", encoding="utf-8") as f:
    text_fa = f.read()

checks_en = [
    ("Forecasting HAMTA MAE", "4.48", "4.48" in text_en),
    ("Forecasting HAMTA RMSE", "5.86", "5.86" in text_en),
    ("Forecasting ETS MAE", "3.41", "3.41" in text_en),
    ("Forecasting Moving Average MAE", "3.51", "3.51" in text_en),
    ("Forecasting Static GNN MAE", "5.98", "5.98" in text_en),
    ("Ranking Target Count", "52/350", "52 out of 350" in text_en and "52/350" in text_en),
    ("Ranking Portfolio Expectation", "0.1486", "0.1486" in text_en),
    ("Ranking Candidate Pool Expectation", "0.174", "0.174" in text_en),
    ("Ranking HAMTA P@35", "0.366", "0.366" in text_en),
    ("Ranking HAMTA Recall@35", "0.246", "0.246" in text_en),
    ("Ranking Recall Ceiling", "35/52 = 0.673", "35/52 = 0.673" in text_en),
    ("Ranking Lift", "2.46", "2.46" in text_en),
    ("Multi-Budget K=10 SFA", "0.430", "0.430" in text_en),
    ("Multi-Budget K=10 HAMTA", "0.400", "0.400" in text_en),
    ("Multi-Budget K=20 SFA", "0.345", "0.345" in text_en),
    ("Multi-Budget K=20 HAMTA", "0.410", "0.410" in text_en),
    ("Multi-Budget K=35 SFA", "0.357", "0.357" in text_en),
    ("Multi-Budget K=35 HAMTA", "0.366", "0.366" in text_en),
    ("Multi-Budget K=50 SFA", "0.322", "0.322" in text_en),
    ("Multi-Budget K=50 HAMTA", "0.340", "0.340" in text_en),
    ("Holm p-value K=10 Lowest Vol", "0.0156", "0.0156" in text_en),
    ("Holm p-value K=35 GBDT", "0.0078", "0.0078" in text_en),
    ("Holm p-value K=35 Static GNN", "0.0977", "0.0977" in text_en),
    ("Ref 9 Ant Financial Authors", "Z. Liu, D. Wang", "Z. Liu, D. Wang" in text_en),
    ("Ref 15 GbRPR LNCS", "vol. 14782", "vol. 14782" in text_en),
    ("Ref 19 Zheng FCS", "Y. Zheng, L. Yi", "Y. Zheng, L. Yi" in text_en),
    ("Ref 23 Wang KDD", "T. Wang, J. Kang", "T. Wang, J. Kang" in text_en)
]

print("\n--- English Paper (create_paper.py) ---")
for label, val, passed in checks_en:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {label}: {val}")

checks_fa = [
    ("Persian Target Count", "52", "52" in text_fa),
    ("Persian Portfolio Expectation", "0.1486", "0.1486" in text_fa),
    ("Persian Candidate Pool Expectation", "17.4", "17.4" in text_fa),
    ("Persian HAMTA P@35", "0.366", "0.366" in text_fa),
    ("Persian HAMTA NDCG@35", "0.382", "0.382" in text_fa),
    ("Persian HAMTA R-Prec", "0.342", "0.342" in text_fa),
    ("Persian Recall Ceiling", "35/52 = 0.673", "0.673" in text_fa),
    ("Persian Lift", "2.46", "2.46" in text_fa),
    ("Persian Multi-Budget K=10 SFA", "0.430", "0.430" in text_fa),
    ("Persian Multi-Budget K=10 HAMTA", "0.400", "0.400" in text_fa),
    ("Persian Multi-Budget K=20 SFA", "0.345", "0.345" in text_fa),
    ("Persian Multi-Budget K=20 HAMTA", "0.410", "0.410" in text_fa),
    ("Persian Multi-Budget K=35 SFA", "0.357", "0.357" in text_fa),
    ("Persian Multi-Budget K=35 HAMTA", "0.366", "0.366" in text_fa),
    ("Persian Multi-Budget K=50 SFA", "0.322", "0.322" in text_fa),
    ("Persian Multi-Budget K=50 HAMTA", "0.340", "0.340" in text_fa),
    ("Persian Holm p-value K=10 Lowest Vol", "0.0156", "0.0156" in text_fa),
    ("Persian Holm p-value K=35 GBDT", "0.0078", "0.0078" in text_fa),
    ("Persian Holm p-value K=35 Static GNN", "0.0977", "0.0977" in text_fa),
    ("Persian Ref 9 Ant Financial Authors", "Z. Liu, D. Wang", "Z. Liu, D. Wang" in text_fa),
    ("Persian Ref 15 GbRPR LNCS", "14782", "14782" in text_fa),
    ("Persian Ref 19 Zheng FCS", "Y. Zheng, L. Yi", "Y. Zheng, L. Yi" in text_fa),
    ("Persian Ref 23 Wang KDD", "T. Wang, J. Kang", "T. Wang, J. Kang" in text_fa)
]

print("\n--- Persian Paper (create_paper_fa.py) ---")
for label, val, passed in checks_fa:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {label}: {val}")
