import os
import sys
import re
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load CSV Ground Truths
df_fc = pd.read_csv('output/hamta_forecasting_benchmark.csv')
df_rk = pd.read_csv('output/hamta_ranking_benchmark.csv')
df_mb = pd.read_csv('output/table2b_multibudget_10seeds.csv')
df_sc = pd.read_csv('output/hamta_scenarios_results.csv')
df_ab = pd.read_csv('output/hamta_ablation_results.csv')

print("="*60)
print("AUDIT: TABLES DATA INTEGRITY")
print("="*60)

print("\n--- TABLE I: Forecasting Benchmark ---")
for _, r in df_fc.iterrows():
    print(f"{r['Model'][:28]:<30} | MAE={r['MAE']:<5} | RMSE={r['RMSE']:<5} | sMAPE={r['sMAPE (%)']:<5} | NLL={r['NLL']}")

print("\n--- TABLE II: Campaign Ranking Benchmark (K=35) ---")
for _, r in df_rk.iterrows():
    print(f"{r['Model / Strategy'][:30]:<32} | P@35={r['Precision@K']:<6} | R@35={r['Recall@K']:<6} | R-Prec={r['R_Precision']:<6} | NDCG={r['NDCG@K']:<6} | MAP={r['MAP@K']}")

print("\n--- TABLE III: Multi-Budget (SFA vs HAMTA) ---")
for b in [10, 20, 35, 50]:
    sub = df_mb[df_mb['Budget (K)'] == b]
    sfa = sub[sub['Strategy'].str.contains('SFA')]['Precision@K'].values[0]
    hamta = sub[sub['Strategy'].str.contains('HAMTA')]['Precision@K'].values[0]
    print(f"Budget K={b:<2} | SFA={sfa} | HAMTA={hamta}")

print("\n--- TABLE IV: Scenarios ---")
for _, r in df_sc.iterrows():
    print(f"{r['Scenario'][:30]:<32} | Drop={r['Drop Rate']:<5} | P@35={r['Precision@35']:<15} | NDCG={r['NDCG@35']:<15} | Cov={r['Coverage (%)']}")

print("\n--- TABLE V: Ablation Study ---")
for _, r in df_ab.iterrows():
    print(f"{r['Architecture Variant'][:32]:<34} | NDCG={r['NDCG@35']:<15} | Prec={r['Precision@35']:<15} | Delta={r.get('Delta_NDCG', 'N/A'):<7} | Sig={r.get('Significance', 'N/A')}")

# 2. Check text files
print("\n" + "="*60)
print("AUDIT: TEXT VS CSV CONSISTENCY")
print("="*60)

with open('create_paper.py', encoding='utf-8') as f:
    text_en = f.read()

with open('create_paper_fa.py', encoding='utf-8') as f:
    text_fa = f.read()

# Check key metrics in English
checks_en = [
    ("Forecasting HAMTA MAE", "4.48", "4.48" in text_en),
    ("Forecasting HAMTA RMSE", "5.86", "5.86" in text_en),
    ("Forecasting ETS MAE", "3.41", "3.41" in text_en),
    ("Forecasting Moving Average MAE", "3.51", "3.51" in text_en),
    ("Forecasting Static GNN MAE", "5.98", "5.98" in text_en),
    ("Ranking Target Count", "51/350", "51/350" in text_en),
    ("Ranking Random Expectation", "0.146", "0.146" in text_en),
    ("Ranking HAMTA P@35", "0.366", "0.366" in text_en),
    ("Ranking HAMTA Recall@35", "0.246", "0.246" in text_en),
    ("Ranking Recall Ceiling", "35/51 = 0.686", "35/51 = 0.686" in text_en),
    ("Ranking Lift", "2.51", "2.51" in text_en),
    ("Multi-Budget K=10 SFA", "0.430", "0.430" in text_en),
    ("Multi-Budget K=10 HAMTA", "0.400", "0.400" in text_en),
    ("Multi-Budget K=20 SFA", "0.345", "0.345" in text_en),
    ("Multi-Budget K=20 HAMTA", "0.410", "0.410" in text_en),
    ("Multi-Budget K=35 SFA", "0.357", "0.357" in text_en),
    ("Multi-Budget K=35 HAMTA", "0.366", "0.366" in text_en),
    ("Multi-Budget K=50 SFA", "0.322", "0.322" in text_en),
    ("Multi-Budget K=50 HAMTA", "0.340", "0.340" in text_en),
    ("Scenario Coverage", "86.2%", "86.2%" in text_en),
    ("Scenario Width", "4.6", "4.6" in text_en),
    ("Ablation Tabular Delta", "+0.145", "+0.145" in text_en),
    ("Ablation Static Delta", "+0.072", "+0.072" in text_en),
    ("Ablation Curvature Delta", "-0.002", "-0.002" in text_en),
    ("Ablation Curvature p-value", "0.8457", "0.8457" in text_en),
    ("Ablation No-Bounds p-value", "0.0273", "0.0273" in text_en),
    ("Old target count 52 check", "52", "35/52" not in text_en and "52/350" not in text_en)
]

print("\n--- English Paper (create_paper.py) ---")
for label, val, passed in checks_en:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {label}: {val}")

# Check key metrics in Persian
checks_fa = [
    ("Persian Target Count", "51", "51" in text_fa),
    ("Persian Random Expectation", "0.146", "0.146" in text_fa),
    ("Persian HAMTA P@35", "0.366", "0.366" in text_fa),
    ("Persian HAMTA NDCG@35", "0.382", "0.382" in text_fa),
    ("Persian HAMTA R-Prec", "0.342", "0.342" in text_fa),
    ("Persian Lift", "2.51", "2.51" in text_fa),
    ("Persian Multi-Budget K=10 SFA", "0.430", "0.430" in text_fa),
    ("Persian Multi-Budget K=10 HAMTA", "0.400", "0.400" in text_fa),
    ("Persian Multi-Budget K=20 SFA", "0.345", "0.345" in text_fa),
    ("Persian Multi-Budget K=20 HAMTA", "0.410", "0.410" in text_fa),
    ("Persian Multi-Budget K=35 SFA", "0.357", "0.357" in text_fa),
    ("Persian Multi-Budget K=35 HAMTA", "0.366", "0.366" in text_fa),
    ("Persian Multi-Budget K=50 SFA", "0.322", "0.322" in text_fa),
    ("Persian Multi-Budget K=50 HAMTA", "0.340", "0.340" in text_fa),
    ("Persian Scenario Coverage", "86.2", "86.2" in text_fa),
    ("Persian Scenario Width", "4.6", "4.6" in text_fa),
    ("Persian Ablation Curvature Delta", "-0.002", "-0.002" in text_fa),
    ("Persian Ablation Curvature p-value", "0.8457", "0.8457" in text_fa),
    ("Persian Ablation No-Bounds p-value", "0.0273", "0.0273" in text_fa),
    ("Old target count 52 check", "52", "35/52" not in text_fa and "52/350" not in text_fa)
]

print("\n--- Persian Paper (create_paper_fa.py) ---")
for label, val, passed in checks_fa:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {label}: {val}")
