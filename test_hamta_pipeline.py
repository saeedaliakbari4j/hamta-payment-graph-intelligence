import time
import math
import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.special import gammaln
import networkx as nx
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

def test_single_seed():
    seed = 42
    df_tx, merch_df = synthesize_transaction_stream(seed=seed, n_merch=350, n_cards=1500, n_tx=35000)
    merchants = merch_df["merchant_id"].tolist()
    guild_list = merch_df["cast_name"].tolist()
    guild_idx = np.array([CAST_NAMES.index(g) for g in guild_list])
    
    # Grid transaction matrix
    grid = pd.MultiIndex.from_product([merchants, range(6)], names=["merchant_id", "period"])
    counts = df_tx.groupby(["merchant_id", "period"]).size().reindex(grid, fill_value=0).reset_index(name="tx_count")
    tx_matrix = counts.pivot(index="merchant_id", columns="period", values="tx_count").values.astype(float)
    
    # Construct peer graph on historical periods <= 4
    peer_dict, combined_sim, curvatures, shared_cards = construct_peer_graph_and_curvature(
        df_tx, merch_df, lambda_sim=0.65, k_peers=6, max_period=4
    )
    
    # Inject opportunity starting in period 4 (calibration / pre-campaign window)
    # Candidate pool: merchants with >= 4 peers and peer historical average >= 12
    rng = np.random.RandomState(seed + 777)
    peer_means_p3 = np.array([np.mean(tx_matrix[peer_dict[i], 3]) for i in range(350)])
    candidate_indices = np.where(peer_means_p3 >= 12.0)[0]
    opp_indices = rng.choice(candidate_indices, size=52, replace=False)
    
    # Scenario B: 32% drop in Period 4 and 5
    drop_rate = 0.32
    noise_sigma = 1.8
    tx_matrix_sc = tx_matrix.copy()
    for idx in opp_indices:
        tx_matrix_sc[idx, 4] = max(1.0, round(tx_matrix_sc[idx, 4] * (1.0 - drop_rate) + rng.normal(0, noise_sigma)))
        tx_matrix_sc[idx, 5] = max(1.0, round(tx_matrix_sc[idx, 5] * (1.0 - drop_rate) + rng.normal(0, noise_sigma)))
    gt_labels = np.isin(np.arange(350), opp_indices).astype(int)
    
    print(f"Ground truth positives: {gt_labels.sum()}")
    
    # Let's test a refined HAMTA forecaster:
    # Uses lag features + spatial attention + residual connection
    class RefinedHAMTAForecaster(nn.Module):
        def __init__(self, num_merch: int, in_dim: int = 12, hidden_dim: int = 32):
            super().__init__()
            self.feat_fc = nn.Linear(in_dim, hidden_dim)
            self.spatial_Wq = nn.Linear(hidden_dim, hidden_dim)
            self.spatial_Wk = nn.Linear(hidden_dim, hidden_dim)
            self.spatial_Wv = nn.Linear(hidden_dim, hidden_dim)
            self.gamma_curv = nn.Parameter(torch.tensor(0.25))
            
            # Autoregressive skip
            self.lag_weight = nn.Parameter(torch.tensor(0.85))
            self.lag_bias = nn.Parameter(torch.tensor(0.0))
            
            self.out_mu = nn.Sequential(
                nn.Linear(hidden_dim, 16),
                nn.ReLU(),
                nn.Linear(16, 1),
                nn.Softplus()
            )
            self.out_phi = nn.Sequential(
                nn.Linear(hidden_dim, 1),
                nn.Softplus()
            )
            
        def forward(self, x_feat, last_lag, peer_idx, peer_curv, eta=0.25):
            h = F.relu(self.feat_fc(x_feat))
            Q = self.spatial_Wq(h).unsqueeze(1)
            h_peers = h[peer_idx]
            K = self.spatial_Wk(h_peers)
            V = self.spatial_Wv(h_peers)
            
            raw = (Q * K).sum(dim=-1) / math.sqrt(h.shape[-1])
            raw = raw + eta * torch.tanh(peer_curv)
            alpha = F.softmax(raw, dim=-1).unsqueeze(-1)
            agg = (alpha * V).sum(dim=1)
            
            h_comb = h + agg
            delta_mu = self.out_mu(h_comb).squeeze(-1)
            phi = self.out_phi(h_comb).squeeze(-1) + 1.0
            
            # Autoregressive skip connection
            mu = F.softplus(self.lag_weight * last_lag + self.lag_bias) + delta_mu + 0.1
            return mu, phi
            
    # Train model
    M = 350
    guild_eye = np.eye(len(CAST_NAMES))
    p_idx = torch.tensor([peer_dict[i] for i in range(M)], dtype=torch.long)
    p_curv = torch.tensor([[curvatures[i, k] for k in peer_dict[i]] for i in range(M)], dtype=torch.float32)
    
    # Feature builder for time t: [log1p(Y_t-1), log1p(Y_t-2), log1p(Y_t-3), guild_onehot (8), peer_mean_log]
    def make_feat(t: int):
        f_list = []
        for i in range(M):
            l1 = np.log1p(tx_matrix_sc[i, t-1])
            l2 = np.log1p(tx_matrix_sc[i, t-2])
            l3 = np.log1p(tx_matrix_sc[i, t-3])
            pm = np.log1p(np.mean(tx_matrix_sc[peer_dict[i], t-1]))
            g = guild_eye[guild_idx[i]]
            f_list.append(np.concatenate([[l1, l2, l3, pm], g]))
        return np.array(f_list, dtype=np.float32)
        
    model = RefinedHAMTAForecaster(M, in_dim=12, hidden_dim=32)
    opt = torch.optim.AdamW(model.parameters(), lr=0.01, weight_decay=1e-4)
    
    # Train on transition: predicting period 4 using periods 1,2,3
    X_tr = torch.tensor(make_feat(4), dtype=torch.float32)
    lag_tr = torch.tensor(tx_matrix_sc[:, 3], dtype=torch.float32)
    y_tr = torch.tensor(tx_matrix_sc[:, 4], dtype=torch.float32)
    
    model.train()
    for ep in range(80):
        opt.zero_grad()
        mu, phi = model(X_tr, lag_tr, p_idx, p_curv)
        p = phi / (phi + mu)
        loss = -(torch.lgamma(y_tr + phi) - torch.lgamma(phi) - torch.lgamma(y_tr + 1.0)
                 + phi * torch.log(p.clamp(min=1e-6)) + y_tr * torch.log((1.0 - p).clamp(min=1e-6))).mean()
        loss.backward()
        opt.step()
        
    # Predict period 5 using periods 2,3,4
    model.eval()
    with torch.no_grad():
        X_te = torch.tensor(make_feat(5), dtype=torch.float32)
        lag_te = torch.tensor(tx_matrix_sc[:, 4], dtype=torch.float32)
        mu_te, phi_te = model(X_te, lag_te, p_idx, p_curv)
        y_pred = mu_te.numpy()
        phi_val = float(phi_te.mean().numpy())
        
    actual_t5 = tx_matrix_sc[:, 5]
    mae = np.mean(np.abs(actual_t5 - y_pred))
    rmse = np.sqrt(np.mean((actual_t5 - y_pred)**2))
    print(f"HAMTA Out-of-sample Forecast Period 5: MAE={mae:.2f}, RMSE={rmse:.2f}, phi={phi_val:.2f}")
    
    # Now evaluate M-GATO:
    # 1. Conformal quantile from calibration on Period 4
    # Residuals on period 4:
    with torch.no_grad():
        mu_cal, _ = model(X_tr, lag_tr, p_idx, p_curv)
        cal_pred = mu_cal.numpy()
    cal_res = np.maximum(0.0, tx_matrix_sc[:, 4] - cal_pred) / (np.sqrt(np.maximum(1.0, cal_pred)) + 1e-4)
    q_conformal = float(np.quantile(cal_res, 0.85))
    
    # Upper bound for period 5:
    U_bounds = y_pred + q_conformal * (np.sqrt(np.maximum(1.0, y_pred)) + 1e-4)
    peer_lower = np.maximum(0.0, y_pred - q_conformal * (np.sqrt(np.maximum(1.0, y_pred)) + 1e-4))
    
    # Peer benchmark B^G:
    B_graph = np.zeros(M)
    graph_support = np.zeros(M)
    for i in range(M):
        peers = peer_dict[i]
        base_w = combined_sim[i, peers]
        curv_mod = 1.0 + 0.25 * np.tanh(curvatures[i, peers])
        adj_w = base_w * curv_mod
        weights = adj_w / (np.sum(adj_w) + 1e-8)
        # Peer benchmark from peers' expected capability:
        # Note: peers who are operating normally achieve their expected performance
        B_graph[i] = np.sum(weights * y_pred[peers])
        
        tot_ov = np.sum(shared_cards[i, peers])
        graph_support[i] = 1.0 - math.exp(-tot_ov / 18.0)
        
    relative_gap = np.maximum(0.0, (B_graph - U_bounds) / (B_graph + 1e-6))
    mgato_scores = graph_support * relative_gap
    
    res = evaluate_ranking(mgato_scores, gt_labels, top_k=35)
    print(f"HAMTA Ranking on Scenario B: P@35={res['Precision@35']:.3f}, Rec@35={res['Recall@35']:.3f}, NDCG@35={res['NDCG@35']:.3f}, MAP@35={res['MAP@35']:.3f}")
    
    # Baselines for comparison:
    # 1. Lowest Volume (Period 5)
    rk_low = evaluate_ranking(1.0 / (actual_t5 + 1.0), gt_labels, 35)
    print(f"Lowest Volume (Test): P@35={rk_low['Precision@35']:.3f}, NDCG@35={rk_low['NDCG@35']:.3f}")
    
    # 2. Pre-campaign volume (Period 4)
    rk_pre = evaluate_ranking(1.0 / (tx_matrix_sc[:, 4] + 1.0), gt_labels, 35)
    print(f"Pre-Campaign Volume (Period 4): P@35={rk_pre['Precision@35']:.3f}, NDCG@35={rk_pre['NDCG@35']:.3f}")

if __name__ == "__main__":
    test_single_seed()
