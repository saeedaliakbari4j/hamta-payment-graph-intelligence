"""
Master Orchestration Pipeline for Higher-Order Curvature Payment Intelligence Framework
Paper: "From Transactional Data to Organizational Intelligence:
        A Higher-Order Hypergraph Curvature Framework for Customer Discovery in the Payment Industry"

Schema: [pan, amount, merchant_id, create_date, cast_name]
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from sklearn.manifold import TSNE

from src.config import cfg
from src.data_generator import generate_transactions
from src.graph_builder import HypergraphBuilder
from src.gnn_model import train_model
from src.customer_discovery import benchmark_models, profile_discovered_personas

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def generate_figures(df_tx, data, embeddings, gnn_labels, rfm_labels, df_personas, df_results):
    """Generate high-resolution 300 DPI figures for both English and Persian manuscripts."""
    os.makedirs(cfg.FIGURES_DIR, exist_ok=True)
    os.makedirs(cfg.FIGURES_FA_DIR, exist_ok=True)
    print("\n>>> Generating High-Resolution Publication Figures...")

    # Palette for personas
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    # 1. Figure 1: Architecture Blueprint (English)
    fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=200)
    ax.axis("off")
    boxes = [
        ("Layer 1: Ingestion & Transaction Ledger",
         "• Schema: [pan, amount, merchant_id,\n  create_date, cast_name]\n• Masked PAN Tokenization\n• Stream Normalization & Cleansing",
         0.03, 0.22, 0.22, 0.60, "#E3F2FD", "#1565C0"),
        ("Layer 2: Hypergraph Curvature Modeling",
         "• Card-Merchant Co-Visitation\n• Discrete Forman-Ricci Curvature\n• Guild Shannon Entropy (cast_name)",
         0.28, 0.22, 0.22, 0.60, "#E8F5E9", "#2E7D32"),
        ("Layer 3: HG-CAN Geometric Learning",
         "• Curvature-Attentive GNN (HG-CAN)\n• Dual-Manifold Representation\n• Geometric Self-Supervised Loss",
         0.53, 0.22, 0.22, 0.60, "#FFF3E0", "#E65100"),
        ("Layer 4: Organizational Intelligence",
         "• Discovered Personas (Gold, B2B,\n  Groceries, Travel, Healthcare)\n• Affluence Centrality & Stickiness",
         0.78, 0.22, 0.21, 0.60, "#F3E5F5", "#6A1B9A")
    ]
    for title, text, x, y, w, h, bg_color, border_color in boxes:
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle=mpatches.BoxStyle("Round", pad=0.02),
                                       facecolor=bg_color, edgecolor=border_color, linewidth=1.8, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.08, title, ha="center", va="top", fontsize=9.2, fontweight="bold", color=border_color, transform=ax.transAxes)
        ax.text(x + 0.015, y + 0.08, text, ha="left", va="bottom", fontsize=8.2, color="#212121", transform=ax.transAxes)

    arrow_props = dict(arrowstyle="->", lw=2.2, color="#424242")
    ax.annotate("", xy=(0.27, 0.52), xytext=(0.255, 0.52), xycoords="axes fraction", arrowprops=arrow_props)
    ax.annotate("", xy=(0.52, 0.52), xytext=(0.505, 0.52), xycoords="axes fraction", arrowprops=arrow_props)
    ax.annotate("", xy=(0.77, 0.52), xytext=(0.755, 0.52), xycoords="axes fraction", arrowprops=arrow_props)
    plt.title("Figure 1. End-to-End Architectural Blueprint of the Proposed Higher-Order Payment Discovery Framework", fontsize=11, fontweight="bold", pad=12)
    plt.savefig(os.path.join(cfg.FIGURES_DIR, "fig1_framework_architecture.png"), bbox_inches="tight")
    plt.close()

    # 2. Figure 2: Customer Co-Occurrence Graph Topology (English)
    num_sub = min(300, data["num_cards"])
    G = nx.Graph()
    for u in range(num_sub):
        G.add_node(u)
    # Add top edges among sample nodes
    src, dst = data["edge_index"][0].numpy(), data["edge_index"][1].numpy()
    weights = data["edge_weight"].numpy()
    for s, d, w in zip(src, dst, weights):
        if s < num_sub and d < num_sub and s < d:
            G.add_edge(s, d, weight=w)

    pos = nx.spring_layout(G, k=0.18, iterations=40, seed=cfg.SEED)
    plt.figure(figsize=(7, 6), dpi=200)
    sample_clusters = gnn_labels[:num_sub]
    nx.draw_networkx_edges(G, pos, alpha=0.15, edge_color="gray", width=0.6)
    nx.draw_networkx_nodes(G, pos, node_color=[colors[c % len(colors)] for c in sample_clusters],
                           node_size=40, alpha=0.85, edgecolors="white", linewidths=0.4)
    plt.title("Figure 2. Discovered Card Co-Occurrence Network Topology\n(Nodes colored by HG-CAN discovered personas across merchant guilds)", fontsize=9.5, fontweight="bold")
    plt.axis("off")
    plt.savefig(os.path.join(cfg.FIGURES_DIR, "fig2_graph_topology_communities.png"), bbox_inches="tight")
    plt.close()

    # 3. Figure 3: Latent t-SNE Manifold Comparison (English)
    print("  Computing t-SNE projections...")
    tsne = TSNE(n_components=2, random_state=cfg.SEED, perplexity=30)
    z_2d = tsne.fit_transform(embeddings.numpy())

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), dpi=200)
    # Left: Baseline RFM
    # Compute RFM 2D
    max_d = pd.to_datetime(df_tx["create_date"]).max()
    rfm_agg = df_tx.groupby("pan").agg(
        recency=("create_date", lambda d: (max_d - pd.to_datetime(d).max()).total_seconds() / 86400.0),
        frequency=("amount", "count"),
        monetary=("amount", "sum")
    ).reindex(data["pan_nodes"]).fillna(0.0).values
    rfm_2d = TSNE(n_components=2, random_state=cfg.SEED, perplexity=30).fit_transform(rfm_agg)

    axes[0].scatter(rfm_2d[:, 0], rfm_2d[:, 1], c=[colors[c % len(colors)] for c in rfm_labels], alpha=0.6, s=25)
    axes[0].set_title("(a) Baseline Tabular RFM Space\n(Severe cluster overlap and boundary ambiguity)", fontsize=9.5, fontweight="bold")
    axes[0].set_xlabel("t-SNE Dimension 1", fontsize=8.5)
    axes[0].set_ylabel("t-SNE Dimension 2", fontsize=8.5)
    axes[0].grid(True, linestyle="--", alpha=0.3)

    # Right: Proposed HG-CAN
    axes[1].scatter(z_2d[:, 0], z_2d[:, 1], c=[colors[c % len(colors)] for c in gnn_labels], alpha=0.7, s=25)
    axes[1].set_title("(b) Proposed HG-CAN Latent Graph Space\n(Distinct separation & compact structural manifolds)", fontsize=9.5, fontweight="bold")
    axes[1].set_xlabel("t-SNE Dimension 1", fontsize=8.5)
    axes[1].set_ylabel("t-SNE Dimension 2", fontsize=8.5)
    axes[1].grid(True, linestyle="--", alpha=0.3)

    plt.suptitle("Figure 3. Manifold Projection Comparison: Tabular RFM vs. Proposed Graph Architecture", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(cfg.FIGURES_DIR, "fig3_latent_tsne_comparison.png"), bbox_inches="tight")
    plt.close()

    # 4. Figure 4: Multidimensional Radar Persona Profiles (English)
    categories = ["Mean Ticket", "Tx Frequency", "Merchant Diversity", "Guild Focus", "Affluence Rank"]
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 5.5), subplot_kw=dict(polar=True), dpi=200)
    plt.xticks(angles[:-1], categories, color="grey", size=8.5)

    for i, row in df_personas.iterrows():
        # Normalized scores [0, 1]
        t_val = min(1.0, row["mean_ticket_size"] / 25000000.0)
        f_val = min(1.0, row["avg_tx_per_card"] / 40.0)
        m_val = min(1.0, row["unique_merchants"] / 100.0)
        g_val = float(row["dominant_guild_pct"])
        a_val = (t_val * 0.7 + f_val * 0.3)
        vals = [t_val, f_val, m_val, g_val, a_val]
        vals += vals[:1]
        ax.plot(angles, vals, linewidth=1.5, linestyle="solid", label=f"Cluster {row['latent_cluster']}: {row['persona_name_en']}")
        ax.fill(angles, vals, alpha=0.08)

    plt.title("Figure 4. Strategic Behavioral Dimensions Across Discovered Organizational Personas", size=10, fontweight="bold", y=1.08)
    plt.legend(loc="upper right", bbox_to_anchor=(1.35, 1.05), fontsize=7)
    plt.savefig(os.path.join(cfg.FIGURES_DIR, "fig4_radar_persona_profiles.png"), bbox_inches="tight")
    plt.close()

    # 5. Figure 5: Quantitative Benchmark Comparison Bar (English)
    fig, ax = plt.subplots(figsize=(7, 4), dpi=200)
    models = df_results["Framework / Model"].values
    nmi = df_results["NMI"].values
    ari = df_results["ARI"].values
    v_meas = df_results["V_Measure"].values

    x = np.arange(len(models))
    w = 0.25

    rects1 = ax.bar(x - w, nmi, w, label="NMI", color="#1f77b4")
    rects2 = ax.bar(x, ari, w, label="ARI", color="#2ca02c")
    rects3 = ax.bar(x + w, v_meas, w, label="V-Measure", color="#d62728")

    ax.set_ylabel("Metric Score", fontsize=9)
    ax.set_title("Figure 5. Quantitative Benchmark Comparison: Alignment and Cluster Quality", fontsize=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["RFM + K-Means", "Bipartite SVD", "Proposed HG-CAN"], fontsize=8.5)
    ax.legend(fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    for rects in [rects1, rects2, rects3]:
        for bar in rects:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f"{yval:.2f}", ha="center", va="bottom", fontsize=7)

    plt.tight_layout()
    plt.savefig(os.path.join(cfg.FIGURES_DIR, "fig5_benchmark_comparison_bar.png"), bbox_inches="tight")
    plt.close()

    # Copy / generate matching Persian figures into figures_fa/
    from src.figures_fa import fig_architecture, fig_topology, fig_radar, fig_benchmark
    fig_architecture()
    fig_topology(df_tx, pd.read_csv(os.path.join(cfg.OUTPUT_DIR, "card_persona_assignments.csv")))
    fig_radar(df_personas)
    fig_benchmark(df_results)
    print("[Figures] Generated publication figures in figures/ and figures_fa/")


def main():
    print("=" * 80)
    print("STARTING HIGHER-ORDER CURVATURE PAYMENT INTELLIGENCE PIPELINE")
    print("SCHEMA: [pan, amount, merchant_id, create_date, cast_name]")
    print("=" * 80)
    t0 = time.time()

    # Step 1: Synthesize Transactional Payment Stream with merchant_id
    print("\n>>> STEP 1: Transactional Data Generation & Schema Validation")
    df_tx, df_cards, df_merchants = generate_transactions()

    # Step 2: Build Hypergraph and Compute Discrete Forman-Ricci Curvature
    print("\n>>> STEP 2: Hypergraph Topology & Discrete Curvature Calculation")
    builder = HypergraphBuilder()
    data = builder.build_topological_network()

    # Step 3: Train HG-CAN Curvature-Attentive Neural Autoencoder
    print("\n>>> STEP 3: Curvature-Attentive Graph Representation Learning (HG-CAN)")
    model, embeddings = train_model(data, epochs=cfg.EPOCHS)

    # Step 4: Customer Persona Discovery and Model Benchmarking
    print("\n>>> STEP 4: Organizational Intelligence Engine & Benchmark Evaluation")
    df_results, gnn_labels, rfm_labels = benchmark_models(
        df_tx,
        data["pan_nodes"],
        data["pan_to_idx"],
        data["B"],
        embeddings.numpy()
    )
    df_personas = profile_discovered_personas(
        df_tx,
        data["pan_nodes"],
        data["pan_to_idx"],
        gnn_labels
    )

    # Step 5: Generate Visualizations
    generate_figures(df_tx, data, embeddings, gnn_labels, rfm_labels, df_personas, df_results)

    elapsed = time.time() - t0
    print("\n" + "=" * 80)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.1f} SECONDS!")
    print("=" * 80)
    print("\nBENCHMARK COMPARISON RESULTS:")
    print(df_results.to_string(index=False))
    print("\nDISCOVERED ENTERPRISE PERSONAS:")
    print(df_personas[["latent_cluster", "persona_name_en", "num_cards", "mean_ticket_size", "dominant_guild_en"]].to_string(index=False))


if __name__ == "__main__":
    main()
