"""
Organizational Intelligence and Customer Persona Discovery Module
Harmonizes Latent Manifold Embeddings with Topological Community Detection.
Computes Quantitative Benchmarks and Strategic Business KPIs.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import (
    normalized_mutual_info_score,
    adjusted_rand_score,
    v_measure_score,
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score
)
from typing import Dict, Tuple
from src.config import cfg

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def compute_metrics(features: np.ndarray, pred_labels: np.ndarray, true_labels: np.ndarray = None) -> Dict[str, float]:
    """Compute clustering alignment and geometric validation metrics."""
    metrics = {
        "Silhouette": float(silhouette_score(features, pred_labels)),
        "Davies_Bouldin": float(davies_bouldin_score(features, pred_labels)),
        "Calinski_Harabasz": float(calinski_harabasz_score(features, pred_labels))
    }
    if true_labels is not None:
        metrics["NMI"] = float(normalized_mutual_info_score(true_labels, pred_labels))
        metrics["ARI"] = float(adjusted_rand_score(true_labels, pred_labels))
        metrics["V_Measure"] = float(v_measure_score(true_labels, pred_labels))
    else:
        metrics["NMI"] = 0.0
        metrics["ARI"] = 0.0
        metrics["V_Measure"] = 0.0
    return metrics


def benchmark_models(
    df_tx: pd.DataFrame,
    pan_nodes: list,
    pan_to_idx: dict,
    B_matrix: np.ndarray,
    hg_can_embeddings: np.ndarray,
    n_clusters: int = cfg.OPTIMAL_CLUSTERS
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """
    Benchmark the proposed HG-CAN architecture against Tabular RFM and Bipartite SVD.
    """
    print("[CustomerDiscovery] Running comparative benchmark across models...")
    max_date = pd.to_datetime(df_tx["create_date"]).max()

    # 1. Classical Tabular RFM Feature Extraction for Card Tokens
    rfm_agg = df_tx.groupby("pan").agg(
        recency=("create_date", lambda d: (max_date - pd.to_datetime(d).max()).total_seconds() / 86400.0),
        frequency=("amount", "count"),
        monetary=("amount", "sum")
    ).reindex(pan_nodes).fillna(0.0)

    rfm_feats = rfm_agg.values
    rfm_norm = (rfm_feats - rfm_feats.mean(axis=0)) / (rfm_feats.std(axis=0) + 1e-8)

    # Ground truth proxy (derived from dominant guild preference)
    dominant_guilds = np.argmax(B_matrix, axis=1)

    # Model A: Tabular RFM + K-Means
    kmeans_rfm = KMeans(n_clusters=n_clusters, random_state=cfg.SEED, n_init=10)
    rfm_labels = kmeans_rfm.fit_predict(rfm_norm)
    metrics_rfm = compute_metrics(rfm_norm, rfm_labels, dominant_guilds)

    # Model B: Bipartite SVD Matrix Factorization
    svd = TruncatedSVD(n_components=min(16, B_matrix.shape[1] - 1), random_state=cfg.SEED)
    svd_feats = svd.fit_transform(B_matrix)
    svd_norm = (svd_feats - svd_feats.mean(axis=0)) / (svd_feats.std(axis=0) + 1e-8)
    kmeans_svd = KMeans(n_clusters=n_clusters, random_state=cfg.SEED, n_init=10)
    svd_labels = kmeans_svd.fit_predict(svd_norm)
    metrics_svd = compute_metrics(svd_norm, svd_labels, dominant_guilds)

    # Model C: Proposed Higher-Order Curvature-Attentive Graph Autoencoder (HG-CAN)
    kmeans_gnn = KMeans(n_clusters=n_clusters, random_state=cfg.SEED, n_init=10)
    gnn_labels = kmeans_gnn.fit_predict(hg_can_embeddings)
    metrics_gnn = compute_metrics(hg_can_embeddings, gnn_labels, dominant_guilds)

    results = [
        {"Framework / Model": "Classical Tabular RFM + K-Means", **metrics_rfm},
        {"Framework / Model": "Bipartite Matrix Factorization (SVD)", **metrics_svd},
        {"Framework / Model": "Proposed Higher-Order Curvature Framework (HG-CAN)", **metrics_gnn}
    ]

    df_results = pd.DataFrame(results)
    res_path = os.path.join(cfg.OUTPUT_DIR, "benchmark_results.csv")
    df_results.to_csv(res_path, index=False)
    print(f"[CustomerDiscovery] Benchmark saved to {res_path}")

    return df_results, gnn_labels, rfm_labels


def profile_discovered_personas(
    df_tx: pd.DataFrame,
    pan_nodes: list,
    pan_to_idx: dict,
    cluster_labels: np.ndarray
) -> pd.DataFrame:
    """
    Attributes discovered clusters to strategic enterprise personas and computes business KPIs.
    """
    df_pan_clusters = pd.DataFrame({
        "pan": pan_nodes,
        "latent_cluster": cluster_labels
    })

    # Join with transaction log
    df_merged = df_tx.merge(df_pan_clusters, on="pan", how="left")

    persona_profiles = []

    for cid in sorted(np.unique(cluster_labels)):
        cluster_tx = df_merged[df_merged["latent_cluster"] == cid]
        num_cards = cluster_tx["pan"].nunique()
        total_volume = cluster_tx["amount"].sum()
        total_tx = len(cluster_tx)
        mean_ticket = cluster_tx["amount"].mean()

        # Dominant guild determined by relative transaction frequency & preference
        guild_counts = cluster_tx.groupby("cast_name")["amount"].count()
        dominant_guild = guild_counts.idxmax() if len(guild_counts) > 0 else "عمومی"
        dominant_guild_pct = (guild_counts.max() / total_tx) if total_tx > 0 else 0.0

        # Unique merchant terminals visited
        unique_merchants = cluster_tx["merchant_id"].nunique()
        avg_tx_per_card = total_tx / max(1, num_cards)

        # Attribute Persona Names (Fa & En)
        if dominant_guild == "طلافروشی":
            name_fa = "سرمایه‌گذاران طلا و کالای لوکس"
            name_en = "Gold & Luxury Investors"
        elif dominant_guild in ["آهن‌آلات و مصالح صنعتی", "لوازم الکترونیک و موبایل"]:
            name_fa = "تجار و عمده‌فروشان آهن و مصالح صنعتی"
            name_en = "B2B Wholesalers & Industrial Commerce"
        elif dominant_guild in ["سوپرمارکت و خواروبار", "رستوران و فست‌فود"]:
            name_fa = "مایحتاج روزمره و مصرف خانوار"
            name_en = "Everyday Household & Groceries"
        elif dominant_guild == "آژانس مسافرتی و گردشگری":
            name_fa = "مسافران و گردشگران پریمیوم"
            name_en = "Affluent Travelers & Tourism"
        elif dominant_guild == "خدمات پزشکی و داروخانه":
            name_fa = "مصرف‌کنندگان خدمات پزشکی و سلامت"
            name_en = "Healthcare & Pharmacy Consumers"
        else:
            name_fa = f"سبک زندگی و پوشاک ({dominant_guild})"
            name_en = f"Retail & Lifestyle ({dominant_guild})"

        persona_profiles.append({
            "latent_cluster": int(cid),
            "persona_name_fa": name_fa,
            "persona_name_en": name_en,
            "num_cards": int(num_cards),
            "total_volume": float(total_volume),
            "mean_ticket_size": float(mean_ticket),
            "dominant_guild": dominant_guild,
            "dominant_guild_en": cfg.CAST_TRANSLATIONS.get(dominant_guild, dominant_guild),
            "dominant_guild_pct": float(dominant_guild_pct),
            "unique_merchants": int(unique_merchants),
            "avg_tx_per_card": float(avg_tx_per_card)
        })

    df_personas = pd.DataFrame(persona_profiles)
    summary_path = os.path.join(cfg.OUTPUT_DIR, "discovered_personas_summary.csv")
    df_personas.to_csv(summary_path, index=False)
    print(f"[CustomerDiscovery] Discovered personas summary saved to {summary_path}")

    # Also save individual card-persona mappings
    assignments_path = os.path.join(cfg.OUTPUT_DIR, "card_persona_assignments.csv")
    df_pan_clusters.to_csv(assignments_path, index=False)

    return df_personas


if __name__ == "__main__":
    from src.graph_builder import HypergraphBuilder
    from src.gnn_model import train_model

    builder = HypergraphBuilder()
    data = builder.build_topological_network()
    model, embeddings = train_model(data, epochs=45)

    df_results, gnn_labels, rfm_labels = benchmark_models(
        builder.df,
        data["pan_nodes"],
        data["pan_to_idx"],
        data["B"],
        embeddings.numpy()
    )
    df_personas = profile_discovered_personas(
        builder.df,
        data["pan_nodes"],
        data["pan_to_idx"],
        gnn_labels
    )
    print("\nBenchmark Results:")
    print(df_results)
    print("\nDiscovered Personas:")
    print(df_personas[["latent_cluster", "persona_name_en", "num_cards", "mean_ticket_size", "dominant_guild_en"]])
