"""
Scientific-audit supplement for the HAMTA manuscript (EN + FA).

Everything reported here is computed by actually running the pipeline from
run_phase1_audit.py over the same 10 logged seeds. Outputs:

  output/phase1_results/audit_multibudget_sample_std.csv
      Precision/Recall/NDCG/MAP @ K in {10,20,35,50} with SAMPLE std (ddof=1),
      matching the convention used in Tables I-V.
  output/phase1_results/audit_significance_tests.csv
      Paired two-sided Wilcoxon signed-rank + paired t-test, HAMTA vs each
      baseline, per budget and metric, with Holm correction across the 4
      baselines inside each (budget, metric) family.
  output/phase1_results/audit_coverage_diagnostics.csv
      Empirical test-period coverage of the calibrated upper bound U, split by
      injected (positive) vs non-injected merchants, plus calibrated margin q.
  output/hamta_top_opportunities.csv
      REAL top-5 M-GATO merchants for seed 42 / Scenario B (replaces the former
      hand-typed illustrative table), including the synthetic ground-truth label.
"""

import os
import sys
import numpy as np
import pandas as pd
import scipy.stats as stats

from run_phase1_audit import (
    synthesize_transaction_stream,
    construct_peer_graph_and_curvature,
    train_and_predict_hamta,
    forecast_baselines,
    compute_mgato_pipeline,
    inject_scenario_opportunity,
    evaluate_ranking,
    SEEDS, NUM_MERCHANTS, NUM_CARDS, NUM_TRANSACTIONS, NUM_PERIODS, CAST_NAMES,
)
from src.config import cfg

sys.stdout.reconfigure(encoding="utf-8")

P1 = os.path.join(cfg.BASE_DIR, "output", "phase1_results")
os.makedirs(P1, exist_ok=True)

KS = [10, 20, 35, 50]
STRATS = [
    "Lowest Volume Heuristic (Test)",
    "Tabular Point Gap (GBDT)",
    "Static GNN Gap",
    "SFA-Style Frontier Gap",
    "HAMTA Proposed (M-GATO)",
]
SCENARIOS = [
    ("Negative Control", 0.00, 2.0),
    ("Scenario A", 0.18, 3.0),
    ("Scenario B", 0.32, 1.8),
    ("Scenario C", 0.48, 0.9),
]

rec = {k: {s: {"P": [], "R": [], "NDCG": [], "MAP": []} for s in STRATS} for k in KS}
cov_rows = []
case_rows = []

for si, seed in enumerate(SEEDS):
    print(f"seed {si + 1}/{len(SEEDS)} = {seed}", flush=True)
    df_tx, merch_df = synthesize_transaction_stream(seed=seed, n_merch=NUM_MERCHANTS, n_cards=NUM_CARDS, n_tx=NUM_TRANSACTIONS)
    merchants = merch_df["merchant_id"].tolist()
    guild_idx = np.array([CAST_NAMES.index(g) for g in merch_df["cast_name"].tolist()])
    grid = pd.MultiIndex.from_product([merchants, range(NUM_PERIODS)], names=["merchant_id", "period"])
    cnt = df_tx.groupby(["merchant_id", "period"]).size().reindex(grid, fill_value=0).reset_index(name="n")
    tx_clean = cnt.pivot(index="merchant_id", columns="period", values="n").values.astype(float)
    peer_dict, sim, curv, shared = construct_peer_graph_and_curvature(df_tx, merch_df, lambda_sim=0.65, k_peers=6, max_period=4)

    for sc_name, drop, noise in SCENARIOS:
        tx_sc, gt = inject_scenario_opportunity(tx_clean, peer_dict, drop_rate=drop, noise_sigma=noise, seed=seed, pos_ratio=0.15)
        y_pred, _ = train_and_predict_hamta(tx_sc, guild_idx, peer_dict, curv, 0.25, seed, 70)
        mg, U, B, Q, cov_cal, width = compute_mgato_pipeline(
            y_pred, tx_sc, peer_dict, sim, curv, shared, guild_idx,
            q_level=0.85, kappa_q=18.0, eta_curv=0.25, cal_period=4)
        covered = tx_sc[:, 5] <= U
        # injected set (same RNG draw as inject_scenario_opportunity even when drop=0)
        _, gt_b = inject_scenario_opportunity(tx_clean, peer_dict, drop_rate=0.32, noise_sigma=noise, seed=seed, pos_ratio=0.15)
        inj = gt_b.astype(bool)
        cov_rows.append({
            "seed": seed, "scenario": sc_name, "margin_q": width,
            "coverage_all": covered.mean(),
            "coverage_injected": covered[inj].mean(),
            "coverage_non_injected": covered[~inj].mean(),
            "calibration_coverage_p4": cov_cal,
        })

        if sc_name != "Scenario B":
            continue

        base = forecast_baselines(tx_sc, guild_idx, peer_dict, seed=seed)
        s_low = 1.0 / (tx_sc[:, 5] + 1.0)
        gm = {g: np.mean(tx_sc[guild_idx == g, 4]) for g in range(len(CAST_NAMES))}
        bg = np.array([gm[guild_idx[i]] for i in range(NUM_MERCHANTS)])
        s_tab = np.maximum(0.0, (bg - base["Tabular GBDT (RFM + Guild)"]) / (bg + 1.0))
        s_sta = np.maximum(0.0, (B - base["Static GNN (Static Bipartite)"]) / (B + 1.0))
        fr = np.array([np.quantile(tx_sc[peer_dict[i], 4], 0.90) for i in range(NUM_MERCHANTS)])
        s_sfa = np.maximum(0.0, (fr - y_pred) / (fr + 1.0))
        scores = dict(zip(STRATS, [s_low, s_tab, s_sta, s_sfa, mg]))
        for k in KS:
            for s, sc in scores.items():
                r = evaluate_ranking(sc, gt, top_k=k)
                rec[k][s]["P"].append(r["Precision@35"])
                rec[k][s]["R"].append(r["Recall@35"])
                rec[k][s]["NDCG"].append(r["NDCG@35"])
                rec[k][s]["MAP"].append(r["MAP@35"])

        if seed == SEEDS[0]:
            order = np.argsort(-mg)[:5]
            for i in order:
                case_rows.append({
                    "merchant_id": merchants[i], "guild": CAST_NAMES[guild_idx[i]],
                    "current_tx": int(tx_sc[i, 5]), "forecast_tx": round(float(y_pred[i]), 1),
                    "upper_bound": round(float(U[i]), 1), "peer_benchmark": round(float(B[i]), 1),
                    "graph_support": round(float(Q[i]), 2), "mgato_score": round(float(mg[i]), 3),
                    "synthetic_label": int(gt[i]),
                })

# ---------------------------------------------------------------- multibudget (ddof=1)
rows = []
for k in KS:
    for s in STRATS:
        d = {"Budget (K)": k, "Strategy": s}
        for m in ("P", "R", "NDCG", "MAP"):
            v = np.array(rec[k][s][m])
            d[f"{m}_mean"] = v.mean()
            d[f"{m}_std"] = v.std(ddof=1)
            d[f"{m}_disp"] = f"{v.mean():.3f} ± {v.std(ddof=1):.3f}"
        rows.append(d)
pd.DataFrame(rows).to_csv(os.path.join(P1, "audit_multibudget_sample_std.csv"), index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- significance + Holm
sig = []
for k in KS:
    for m in ("P", "NDCG"):
        h = np.array(rec[k]["HAMTA Proposed (M-GATO)"][m])
        fam = []
        for s in STRATS[:-1]:
            b = np.array(rec[k][s][m])
            diff = h - b
            t_p = stats.ttest_rel(h, b).pvalue if np.any(diff != 0) else 1.0
            w_p = stats.wilcoxon(h, b).pvalue if np.any(diff != 0) else 1.0
            fam.append({"Budget (K)": k, "Metric": "Precision" if m == "P" else "NDCG", "Baseline": s,
                        "HAMTA_mean": h.mean(), "Baseline_mean": b.mean(), "Mean_diff": diff.mean(),
                        "Wins": int((diff > 0).sum()), "Ties": int((diff == 0).sum()), "Losses": int((diff < 0).sum()),
                        "t_p": t_p, "wilcoxon_p": w_p})
        # Holm on Wilcoxon p within family of 4 baselines
        ps = np.array([f["wilcoxon_p"] for f in fam])
        idx = np.argsort(ps)
        adj = np.empty_like(ps)
        running = 0.0
        for rank, j in enumerate(idx):
            val = min(1.0, (len(ps) - rank) * ps[j])
            running = max(running, val)
            adj[j] = running
        for f, a in zip(fam, adj):
            f["wilcoxon_p_holm"] = a
            f["significant_0.05_holm"] = bool(a < 0.05)
        sig.extend(fam)
df_sig = pd.DataFrame(sig)
df_sig.to_csv(os.path.join(P1, "audit_significance_tests.csv"), index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- coverage
df_cov = pd.DataFrame(cov_rows)
df_cov.to_csv(os.path.join(P1, "audit_coverage_per_seed.csv"), index=False, encoding="utf-8-sig")
agg = df_cov.groupby("scenario", sort=False).agg(["mean", lambda x: x.std(ddof=1)])
agg.columns = [f"{a}_{'mean' if b == 'mean' else 'std'}" for a, b in agg.columns]
agg = agg.drop(columns=[c for c in agg.columns if c.startswith("seed")]).reset_index()
agg.to_csv(os.path.join(P1, "audit_coverage_diagnostics.csv"), index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- case study
pd.DataFrame(case_rows).to_csv(os.path.join(cfg.OUTPUT_DIR, "hamta_top_opportunities.csv"), index=False, encoding="utf-8-sig")

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
print(pd.DataFrame(rows)[["Budget (K)", "Strategy", "P_disp", "R_disp", "NDCG_disp"]].to_string(index=False))
print(df_sig.round(4).to_string(index=False))
print(agg.round(4).to_string(index=False))
print(pd.DataFrame(case_rows).to_string(index=False))
