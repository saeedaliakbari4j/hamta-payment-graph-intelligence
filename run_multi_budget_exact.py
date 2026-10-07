import sys
import os
import math
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import scipy.stats as stats

# Import from run_phase1_audit
from run_phase1_audit import (
    synthesize_transaction_stream,
    construct_peer_graph_and_curvature,
    train_and_predict_hamta,
    forecast_baselines,
    compute_mgato_pipeline,
    inject_scenario_opportunity,
    evaluate_ranking,
    SEEDS,
    NUM_MERCHANTS,
    NUM_CARDS,
    NUM_TRANSACTIONS,
    NUM_PERIODS,
    CAST_NAMES,
    OUTPUT_DIR
)

ks = [10, 20, 35, 50]
strat_names = [
    "Lowest Volume Heuristic (Test)",
    "Tabular Point Gap (GBDT)",
    "Static GNN Gap",
    "SFA-Style Frontier Gap",
    "HAMTA Proposed (M-GATO)"
]

records = {k: {s: {"P": [], "R": [], "NDCG": [], "MAP": []} for s in strat_names} for k in ks}

print(f"[Multi-Budget] Evaluating across budgets {ks} and {len(SEEDS)} seeds...")

for seed_idx, seed in enumerate(SEEDS):
    print(f"  Seed {seed_idx+1}/{len(SEEDS)}: {seed}...")
    df_tx, merch_df = synthesize_transaction_stream(seed=seed, n_merch=NUM_MERCHANTS, n_cards=NUM_CARDS, n_tx=NUM_TRANSACTIONS)
    merchants = merch_df["merchant_id"].tolist()
    guild_list = merch_df["cast_name"].tolist()
    guild_idx = np.array([CAST_NAMES.index(g) for g in guild_list])
    
    grid = pd.MultiIndex.from_product([merchants, range(NUM_PERIODS)], names=["merchant_id", "period"])
    tx_counts = df_tx.groupby(["merchant_id", "period"]).size().reindex(grid, fill_value=0).reset_index(name="tx_count")
    tx_matrix_clean = tx_counts.pivot(index="merchant_id", columns="period", values="tx_count").values.astype(float)
    
    peer_dict, combined_sim, curvatures, shared_cards = construct_peer_graph_and_curvature(
        df_tx, merch_df, lambda_sim=0.65, k_peers=6, max_period=4
    )
    
    # Inject Scenario B (Default medium: drop=0.32, noise=1.8)
    tx_mat_b, gt_labels_b = inject_scenario_opportunity(
        tx_matrix_clean, peer_dict, drop_rate=0.32, noise_sigma=1.8, seed=seed, pos_ratio=0.15
    )
    
    y_pred_b, _ = train_and_predict_hamta(tx_mat_b, guild_idx, peer_dict, curvatures, 0.25, seed, 70)
    baseline_preds_b = forecast_baselines(tx_mat_b, guild_idx, peer_dict, seed=seed)
    
    mgato_b, U_b, B_graph_b, Q_b, _, _ = compute_mgato_pipeline(
        y_pred_b, tx_mat_b, peer_dict, combined_sim, curvatures, shared_cards, guild_idx,
        q_level=0.85, kappa_q=18.0, eta_curv=0.25, cal_period=4
    )
    
    # Scores
    score_lowest_vol = 1.0 / (tx_mat_b[:, 5] + 1.0)
    guild_means_hist = {g_id: np.mean(tx_mat_b[guild_idx == g_id, 4]) for g_id in range(len(CAST_NAMES))}
    b_guild_hist = np.array([guild_means_hist[guild_idx[i]] for i in range(NUM_MERCHANTS)])
    score_tab_gap = np.maximum(0.0, (b_guild_hist - baseline_preds_b["Tabular GBDT (RFM + Guild)"]) / (b_guild_hist + 1.0))
    score_static_gap = np.maximum(0.0, (B_graph_b - baseline_preds_b["Static GNN (Static Bipartite)"]) / (B_graph_b + 1.0))
    sfa_frontier = np.array([np.quantile(tx_mat_b[peer_dict[i], 4], 0.90) for i in range(NUM_MERCHANTS)])
    score_sfa_gap = np.maximum(0.0, (sfa_frontier - y_pred_b) / (sfa_frontier + 1.0))
    score_mgato = mgato_b
    
    scores_dict = {
        "Lowest Volume Heuristic (Test)": score_lowest_vol,
        "Tabular Point Gap (GBDT)": score_tab_gap,
        "Static GNN Gap": score_static_gap,
        "SFA-Style Frontier Gap": score_sfa_gap,
        "HAMTA Proposed (M-GATO)": score_mgato
    }
    
    for k in ks:
        for s_name, sc in scores_dict.items():
            r = evaluate_ranking(sc, gt_labels_b, top_k=k)
            records[k][s_name]["P"].append(r["Precision@35"])
            records[k][s_name]["R"].append(r["Recall@35"])
            records[k][s_name]["NDCG"].append(r["NDCG@35"])
            records[k][s_name]["MAP"].append(r["MAP@35"])

rows = []
for k in ks:
    for s_name in strat_names:
        p_mean = np.mean(records[k][s_name]["P"])
        p_std = np.std(records[k][s_name]["P"])
        r_mean = np.mean(records[k][s_name]["R"])
        r_std = np.std(records[k][s_name]["R"])
        n_mean = np.mean(records[k][s_name]["NDCG"])
        n_std = np.std(records[k][s_name]["NDCG"])
        m_mean = np.mean(records[k][s_name]["MAP"])
        m_std = np.std(records[k][s_name]["MAP"])
        rows.append({
            "Budget (K)": k,
            "Strategy": s_name,
            "Precision@K": f"{p_mean:.3f} ± {p_std:.3f}",
            "Recall@K": f"{r_mean:.3f} ± {r_std:.3f}",
            "NDCG@K": f"{n_mean:.3f} ± {n_std:.3f}",
            "MAP@K": f"{m_mean:.3f} ± {m_std:.3f}",
            "P_mean": p_mean, "P_std": p_std,
            "NDCG_mean": n_mean, "NDCG_std": n_std
        })

df_out = pd.DataFrame(rows)
csv_path = os.path.join(OUTPUT_DIR, "table2b_multibudget_10seeds.csv")
df_out.to_csv(csv_path, index=False)
print(f"[Done] Saved multi-budget benchmark to {csv_path}")

for k in ks:
    print(f"\n==================== BUDGET @{k} ====================")
    sub = df_out[df_out["Budget (K)"] == k]
    for _, r in sub.iterrows():
        print(f"{r['Strategy']:<32} | P@{k}: {r['Precision@K']} | NDCG@{k}: {r['NDCG@K']} | Rec@{k}: {r['Recall@K']}")
