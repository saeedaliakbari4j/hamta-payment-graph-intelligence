"""
Test scenario drop timing consistency and ranking metrics across Scenarios.
"""
import time
import math
import numpy as np
import pandas as pd
import scipy.stats as stats
import torch
import torch.nn as nn
import torch.nn.functional as F

from run_phase1_audit import (
    synthesize_transaction_stream,
    construct_peer_graph_and_curvature,
    compute_discrete_nb_nll,
    compute_discrete_poisson_nll,
    evaluate_ranking,
    CAST_NAMES
)

def test_scenarios():
    seed = 42
    df_tx, merch_df = synthesize_transaction_stream(seed=seed, n_merch=350, n_cards=1500, n_tx=35000)
    merchants = merch_df["merchant_id"].tolist()
    guild_list = merch_df["cast_name"].tolist()
    guild_idx = np.array([CAST_NAMES.index(g) for g in guild_list])
    
    grid = pd.MultiIndex.from_product([merchants, range(6)], names=["merchant_id", "period"])
    counts = df_tx.groupby(["merchant_id", "period"]).size().reindex(grid, fill_value=0).reset_index(name="tx_count")
    tx_matrix = counts.pivot(index="merchant_id", columns="period", values="tx_count").values.astype(float)
    
    peer_dict, combined_sim, curvatures, shared_cards = construct_peer_graph_and_curvature(
        df_tx, merch_df, lambda_sim=0.65, k_peers=6, max_period=4
    )
    
    # Candidate pool: merchants with >= 4 peers and peer historical average >= 12
    rng = np.random.RandomState(seed + 777)
    peer_means_p3 = np.array([np.mean(tx_matrix[peer_dict[i], 3]) for i in range(350)])
    candidate_indices = np.where(peer_means_p3 >= 12.0)[0]
    opp_indices = rng.choice(candidate_indices, size=52, replace=False)
    
    scenarios = [
        {"name": "Negative Control", "drop": 0.0, "noise": 2.0},
        {"name": "Scenario A (Weak)", "drop": 0.18, "noise": 3.0},
        {"name": "Scenario B (Medium)", "drop": 0.32, "noise": 1.8},
        {"name": "Scenario C (Strong)", "drop": 0.48, "noise": 0.9}
    ]
    
    for sc in scenarios:
        drop_rate = sc["drop"]
        noise_sigma = sc["noise"]
        tx_mat_sc = tx_matrix.copy()
        
        if drop_rate > 0.0:
            for idx in opp_indices:
                tx_mat_sc[idx, 4] = max(1.0, round(tx_mat_sc[idx, 4] * (1.0 - drop_rate) + rng.normal(0, noise_sigma)))
                tx_mat_sc[idx, 5] = max(1.0, round(tx_mat_sc[idx, 5] * (1.0 - drop_rate) + rng.normal(0, noise_sigma)))
            gt = np.isin(np.arange(350), opp_indices).astype(int)
        else:
            gt = np.zeros(350, dtype=int)
            
        # Predict Period 5 using GBDT or HAMTA on periods 1,2,3,4
        # GBDT baseline on historical lags:
        X_train = np.column_stack([
            tx_mat_sc[:, 1], tx_mat_sc[:, 2], tx_mat_sc[:, 3],
            np.mean(tx_mat_sc[:, 1:4], axis=1), guild_idx
        ])
        y_train = tx_mat_sc[:, 4]
        
        X_test = np.column_stack([
            tx_mat_sc[:, 2], tx_mat_sc[:, 3], tx_mat_sc[:, 4],
            np.mean(tx_mat_sc[:, 2:5], axis=1), guild_idx
        ])
        
        from sklearn.ensemble import HistGradientBoostingRegressor
        gbdt = HistGradientBoostingRegressor(max_iter=50, random_state=42)
        gbdt.fit(X_train, y_train)
        pred_p5 = np.maximum(1.0, gbdt.predict(X_test))
        
        # Conformal calibration on Period 4:
        cal_pred = gbdt.predict(X_train)
        cal_res = np.maximum(0.0, tx_mat_sc[:, 4] - cal_pred)
        q_conf = float(np.quantile(cal_res, 0.85))
        
        U = pred_p5 + q_conf
        
        # Peer benchmark B^G:
        B_graph = np.zeros(350)
        graph_support = np.zeros(350)
        for i in range(350):
            peers = peer_dict[i]
            base_w = combined_sim[i, peers]
            curv_mod = 1.0 + 0.25 * np.tanh(curvatures[i, peers])
            adj_w = base_w * curv_mod
            weights = adj_w / (np.sum(adj_w) + 1e-8)
            # Benchmark from peers' natural predictions:
            B_graph[i] = np.sum(weights * pred_p5[peers])
            tot_ov = np.sum(shared_cards[i, peers])
            graph_support[i] = 1.0 - math.exp(-tot_ov / 18.0)
            
        rel_gap = np.maximum(0.0, (B_graph - U) / (B_graph + 1e-6))
        mgato = graph_support * rel_gap
        
        res = evaluate_ranking(mgato, gt, 35)
        print(f"[{sc['name']}] P@35: {res['Precision@35']:.3f}, Rec@35: {res['Recall@35']:.3f}, NDCG@35: {res['NDCG@35']:.3f}, MAP@35: {res['MAP@35']:.3f}, FPR@35: {res['FPR@35']:.3f}")

if __name__ == "__main__":
    test_scenarios()
