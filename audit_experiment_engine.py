"""
Audit Experiment Engine:
Verifies and validates the revised experimental methodology for HAMTA.
Includes:
- Data generation with seed control
- Leakage-free temporal forecasting (Train: 0-3, Cal: 4, Test: 5)
- Standard IR ranking metrics (Precision@K, Recall@K, NDCG@K, standard MAP@K, R-Precision)
- Discrete Negative Binomial NLL
- 4 Scenarios (Negative Control, A, B, C)
- Component Ablations
- Conformal Coverage & Interval Width
- Sensitivity & Scalability
"""

import os
import sys
import time
import math
import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.special import gammaln
import networkx as nx
from typing import Dict, List, Tuple
from sklearn.ensemble import HistGradientBoostingRegressor
import torch
import torch.nn as nn
import torch.nn.functional as F

# Fix random seed utility
def set_all_seeds(seed: int):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

# Compute Discrete Negative Binomial NLL (Strictly Non-Negative)
def compute_nb_nll(y_true: np.ndarray, y_pred_mean: np.ndarray, phi: float = 5.0) -> float:
    """
    Computes average Negative Log-Likelihood under a discrete Negative Binomial distribution.
    p = phi / (phi + mu), n = phi.
    y ~ NB(n, p)
    Since P(y) in [0, 1], -ln P(y) >= 0.
    """
    y_true = np.asarray(y_true, dtype=float)
    mu = np.maximum(1e-4, np.asarray(y_pred_mean, dtype=float))
    phi = max(1e-2, float(phi))
    
    # log P(Y=y) = gammaln(y + phi) - gammaln(phi) - gammaln(y + 1)
    #              + phi * ln(phi / (phi + mu)) + y * ln(mu / (phi + mu))
    log_probs = (
        gammaln(y_true + phi)
        - gammaln(phi)
        - gammaln(y_true + 1.0)
        + phi * np.log(phi / (phi + mu))
        + y_true * np.log(mu / (phi + mu))
    )
    nll = -np.mean(log_probs)
    return float(max(0.0, nll))

# Compute Discrete Poisson NLL (Strictly Non-Negative)
def compute_poisson_nll(y_true: np.ndarray, y_pred_mean: np.ndarray) -> float:
    """
    Computes average Poisson NLL including the factorial term ln(y!).
    log P(y) = y * ln(mu) - mu - ln(y!)
    """
    y_true = np.asarray(y_true, dtype=float)
    mu = np.maximum(1e-4, np.asarray(y_pred_mean, dtype=float))
    log_probs = y_true * np.log(mu) - mu - gammaln(y_true + 1.0)
    return float(max(0.0, -np.mean(log_probs)))

# Standard IR Ranking Metrics
def compute_ranking_metrics_strict(
    scores: np.ndarray,
    ground_truth: np.ndarray,
    top_k: int = 35
) -> Dict[str, float]:
    """
    Computes IR metrics with standard definitions:
    - Precision@K: hits / K
    - Recall@K: hits / R (where R is total positives)
    - R-Precision: Precision at K = R
    - NDCG@K: DCG@K / IDCG@K
    - MAP@K: (1 / min(K, R)) * sum_{k=1}^K P@k * hit_k (Standard IR definition)
    - FPR@K: false_positives_in_top_k / total_negatives
    """
    scores = np.asarray(scores)
    ground_truth = np.asarray(ground_truth)
    total_positives = int(np.sum(ground_truth))
    total_negatives = int(len(ground_truth) - total_positives)
    
    order = np.argsort(scores)[::-1]
    top_idx = order[:top_k]
    
    hits = int(np.sum(ground_truth[top_idx]))
    prec_k = float(hits / top_k)
    rec_k = float(hits / max(1, total_positives))
    
    # False Positive Rate in Top-K
    fp = top_k - hits
    fpr_k = float(fp / max(1, total_negatives))
    
    # R-Precision (at K = total_positives)
    r_k = min(len(scores), max(1, total_positives))
    r_top_idx = order[:r_k]
    r_hits = int(np.sum(ground_truth[r_top_idx]))
    r_prec = float(r_hits / r_k)
    
    # NDCG@K
    if total_positives == 0:
        ndcg_k = 0.0
        map_k = 0.0
    else:
        dcg = sum([ground_truth[top_idx[i]] / math.log2(i + 2) for i in range(top_k)])
        ideal_order = np.argsort(ground_truth)[::-1][:top_k]
        idcg = sum([ground_truth[ideal_order[i]] / math.log2(i + 2) for i in range(top_k)])
        ndcg_k = float(dcg / max(1e-12, idcg))
        
        # Standard MAP@K normalized by min(K, total_positives)
        cum_hits = 0
        ap_sum = 0.0
        for i in range(top_k):
            if ground_truth[top_idx[i]] == 1:
                cum_hits += 1
                ap_sum += cum_hits / (i + 1)
        map_k = float(ap_sum / min(top_k, total_positives))
        
    return {
        "Precision@K": round(prec_k, 4),
        "Recall@K": round(rec_k, 4),
        "R_Precision": round(r_prec, 4),
        "NDCG@K": round(ndcg_k, 4),
        "MAP@K": round(map_k, 4),
        "FPR@K": round(fpr_k, 4)
    }

print("Engine test setup successfully imported.")
