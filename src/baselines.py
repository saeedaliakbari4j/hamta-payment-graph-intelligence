"""
Baseline Models Module
Implements classical customer discovery and segmentation approaches in the payment industry:
1. Classical Tabular RFM (Recency, Frequency, Monetary) + K-Means
2. Matrix Factorization / Truncated SVD on Transaction Co-occurrence
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from typing import Dict, Tuple, List
from src.config import cfg

class BaselineCustomerDiscovery:
    def __init__(self, config=cfg):
        self.cfg = config

    def extract_tabular_rfm_features(self, df_tx: pd.DataFrame, cust_list: List[str]) -> np.ndarray:
        """
        Extracts classical Tabular RFM features:
        - Recency (days since last transaction)
        - Frequency (total number of transactions)
        - Monetary (total spend volume)
        - Average Order Value (AOV)
        """
        df_tx_copy = df_tx.copy()
        df_tx_copy["create_date"] = pd.to_datetime(df_tx_copy["create_date"])
        max_time = df_tx_copy["create_date"].max()

        cust_stats = df_tx_copy.groupby("pan").agg(
            last_tx=("create_date", "max"),
            frequency=("amount", "count"),
            monetary=("amount", "sum"),
            mean_amount=("amount", "mean")
        ).reset_index()

        cust_stats["recency"] = (max_time - cust_stats["last_tx"]).dt.total_seconds() / 86400.0

        cust_map = {row["pan"]: row for _, row in cust_stats.iterrows()}
        rfm_matrix = []
        for c in cust_list:
            if c in cust_map:
                r = cust_map[c]
                rfm_matrix.append([
                    np.log1p(max(0.0, r["recency"])),
                    np.log1p(r["frequency"]),
                    np.log1p(r["monetary"]),
                    np.log1p(r["mean_amount"])
                ])
            else:
                rfm_matrix.append([0.0, 0.0, 0.0, 0.0])

        X_rfm = np.array(rfm_matrix, dtype=np.float32)
        scaler = StandardScaler()
        return scaler.fit_transform(X_rfm)

    def evaluate_rfm_baseline(self, df_tx: pd.DataFrame, cust_list: List[str]) -> Tuple[np.ndarray, Dict[str, float], np.ndarray]:
        """
        Runs Classical RFM + K-Means baseline.
        """
        X_rfm = self.extract_tabular_rfm_features(df_tx, cust_list)
        km = KMeans(n_clusters=self.cfg.OPTIMAL_CLUSTERS, random_state=self.cfg.SEED, n_init=10)
        labels = km.fit_predict(X_rfm)

        metrics = {
            "silhouette_score": float(silhouette_score(X_rfm, labels)),
            "davies_bouldin_score": float(davies_bouldin_score(X_rfm, labels)),
            "calinski_harabasz_score": float(calinski_harabasz_score(X_rfm, labels))
        }
        return labels, metrics, X_rfm

    def evaluate_svd_baseline(self, B_matrix: np.ndarray) -> Tuple[np.ndarray, Dict[str, float], np.ndarray]:
        """
        Runs Matrix Factorization (Truncated SVD) on Bipartite Customer-Guild Co-occurrence.
        """
        svd = TruncatedSVD(n_components=min(self.cfg.EMBEDDING_DIM, B_matrix.shape[1] - 1), random_state=self.cfg.SEED)
        X_svd = svd.fit_transform(B_matrix)

        km = KMeans(n_clusters=self.cfg.OPTIMAL_CLUSTERS, random_state=self.cfg.SEED, n_init=10)
        labels = km.fit_predict(X_svd)

        metrics = {
            "silhouette_score": float(silhouette_score(X_svd, labels)),
            "davies_bouldin_score": float(davies_bouldin_score(X_svd, labels)),
            "calinski_harabasz_score": float(calinski_harabasz_score(X_svd, labels))
        }
        return labels, metrics, X_svd

if __name__ == "__main__":
    from src.graph_builder import PaymentGraphBuilder
    df_tx = pd.read_csv(cfg.DATA_PATH)
    builder = PaymentGraphBuilder()
    B, cust_list, _ = builder.build_bipartite_customer_guild_matrix(df_tx)

    baseline = BaselineCustomerDiscovery()
    labels_rfm, metrics_rfm, _ = baseline.evaluate_rfm_baseline(df_tx, cust_list)
    labels_svd, metrics_svd, _ = baseline.evaluate_svd_baseline(B)

    print("RFM Baseline Metrics:", metrics_rfm)
    print("SVD Baseline Metrics:", metrics_svd)
