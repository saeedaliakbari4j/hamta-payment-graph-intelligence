"""
Persian (RTL) publication figures for the Persian version of the paper.
Built only from saved artifacts in output/ so numbers are identical to the English paper.
Schema: [pan, amount, merchant_id, create_date, cast_name]
"""
import os
import sys
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from src.config import cfg
from src.graph_builder import HypergraphBuilder

FIG_DIR = os.path.join(cfg.BASE_DIR, "figures_fa")
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams.update({
    "font.family": "Tahoma",
    "axes.unicode_minus": False,
    "font.size": 7,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]


def fa(text: str) -> str:
    # Matplotlib >= 3.11 performs complex text layout natively
    return str(text)


def short_persona(name: str) -> str:
    mapping = {
        "سرمایه‌گذاران طلا و کالای لوکس": "سرمایه‌گذاران طلا",
        "تجار و عمده‌فروشان آهن و مصالح صنعتی": "عمده‌فروشان آهن و مصالح",
        "مایحتاج روزمره و مصرف خانوار": "مایحتاج روزمره",
        "مسافران و گردشگران پریمیوم": "مسافران پریمیوم",
        "مصرف‌کنندگان خدمات پزشکی و سلامت": "سلامت و پزشکی",
    }
    return mapping.get(name, name)


def fig_architecture():
    fig, ax = plt.subplots(figsize=(3.3, 4.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    layers = [
        ("لایه ۱: دریافت و نرمال‌سازی تراکنش", "pan, amount, merchant_id,\ncreate_date, cast_name", "#E3F2FD", "#1565C0"),
        ("لایه ۲: مدل‌سازی انحنای هایپرگراف", "انحنای فورمن-ریچی، انتروپی صنف،\nشبکه هم‌دیدار کارت و پذیرنده", "#E8F5E9", "#2E7D32"),
        ("لایه ۳: یادگیری هندسی HG-CAN", "توجه گراف با انحنای ریچی\nیادگیری خود‌نظارتی منیفولد دوگانه", "#FFF3E0", "#E65100"),
        ("لایه ۴: موتور هوشمندی سازمانی", "کشف پرسونا، شاخص تمول،\nچسبندگی و اتصال شبکه", "#F3E5F5", "#6A1B9A"),
    ]
    h, gap = 0.18, 0.07
    y = 0.98 - h
    for i, (title, body, bg, ec) in enumerate(layers):
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.04, y), 0.92, h, boxstyle=mpatches.BoxStyle("Round", pad=0.01),
            facecolor=bg, edgecolor=ec, linewidth=1.3))
        ax.text(0.5, y + h - 0.045, fa(title), ha="center", va="center",
                fontsize=8, fontweight="bold", color=ec)
        lines = body.split("\n")
        rendered = "\n".join(fa(l) if any("\u0600" <= c <= "\u06ff" for c in l) else l for l in lines)
        ax.text(0.5, y + 0.055, rendered, ha="center", va="center", fontsize=7, color="#212121", linespacing=1.4)
        if i < len(layers) - 1:
            ax.annotate("", xy=(0.5, y - gap + 0.012), xytext=(0.5, y - 0.004),
                        arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#424242"))
        y -= h + gap
    fig.savefig(os.path.join(FIG_DIR, "fig1_architecture_fa.png"))
    plt.close(fig)


def fig_topology(df_tx, disc):
    builder = HypergraphBuilder()
    data = builder.build_topological_network()
    num_sub = min(260, data["num_cards"])
    G = nx.Graph()
    for u in range(num_sub):
        G.add_node(u)
    src, dst = data["edge_index"][0].numpy(), data["edge_index"][1].numpy()
    weights = data["edge_weight"].numpy()
    for s, d, w in zip(src, dst, weights):
        if s < num_sub and d < num_sub and s < d:
            G.add_edge(s, d, weight=w)

    pos = nx.spring_layout(G, k=0.18, iterations=50, seed=cfg.SEED)
    cl = disc.set_index("pan").loc[[data["pan_nodes"][i] for i in range(num_sub)], "latent_cluster"].values

    fig, ax = plt.subplots(figsize=(3.3, 3.0))
    nx.draw_networkx_edges(G, pos, alpha=0.15, edge_color="gray", width=0.5, ax=ax)
    nx.draw_networkx_nodes(G, pos, node_color=[PALETTE[c % 5] for c in cl], node_size=22,
                           alpha=0.9, edgecolors="white", linewidths=0.3, ax=ax)
    ax.axis("off")
    fig.savefig(os.path.join(FIG_DIR, "fig2_topology_fa.png"))
    plt.close(fig)


def fig_heatmap(df_tx, disc):
    merged = df_tx.merge(disc[["pan", "latent_cluster"]], on="pan")
    ct = pd.crosstab(merged["latent_cluster"], merged["cast_name"], normalize="index") * 100
    guilds = list(ct.columns)
    fig, ax = plt.subplots(figsize=(3.3, 3.1))
    im = ax.imshow(ct.values, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(guilds)))
    ax.set_xticklabels([fa(g) for g in guilds], rotation=55, ha="right", fontsize=6)
    ax.set_yticks(range(len(ct)))
    ax.set_yticklabels([fa(f"خوشه {c}") for c in ct.index], fontsize=6)
    for i in range(ct.shape[0]):
        for j in range(ct.shape[1]):
            v = ct.values[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=5.5,
                    color="white" if v > 45 else "black")
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cb.set_label(fa("سهم تراکنش‌ها (٪)"), fontsize=6)
    cb.ax.tick_params(labelsize=5.5)
    fig.savefig(os.path.join(FIG_DIR, "fig3_guild_heatmap_fa.png"))
    plt.close(fig)


def fig_radar(summ):
    cats = ["ارزش تراکنش", "بسامد تراکنش", "تنوع پذیرنده", "تمرکز صنف", "امتیاز تمول"]
    N = len(cats)
    ang = [n / N * 2 * np.pi for n in range(N)] + [0]
    fig, ax = plt.subplots(figsize=(3.3, 3.5), subplot_kw=dict(polar=True))
    ax.set_xticks(ang[:-1])
    ax.set_xticklabels([fa(c) for c in cats], fontsize=6.5)
    ax.tick_params(axis="y", labelsize=5)
    for i, row in summ.iterrows():
        t_val = min(1.0, row["mean_ticket_size"] / 25000000.0)
        f_val = min(1.0, row["avg_tx_per_card"] / 40.0)
        m_val = min(1.0, row["unique_merchants"] / 100.0)
        g_val = float(row["dominant_guild_pct"])
        a_val = t_val * 0.7 + f_val * 0.3
        vals = [t_val, f_val, m_val, g_val, a_val]
        vals += vals[:1]
        c = PALETTE[int(row["latent_cluster"]) % 5]
        name = short_persona(str(row.get("persona_name_fa", f"خوشه {row['latent_cluster']}")))
        ax.plot(ang, vals, color=c, lw=1.3, label=fa(name))
        ax.fill(ang, vals, color=c, alpha=0.12)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, fontsize=6, frameon=False)
    fig.savefig(os.path.join(FIG_DIR, "fig4_radar_fa.png"))
    plt.close(fig)


def fig_benchmark(bench):
    names = ["RFM + K-Means", "SVD", fa("HG-CAN (پیشنهادی)")]
    metrics = ["NMI", "ARI", "Silhouette"]
    x = np.arange(len(metrics))
    w = 0.26
    colors = ["#90CAF9", "#80CBC4", "#EF5350"]
    fig, ax = plt.subplots(figsize=(3.3, 2.6))
    for i, (_, r) in enumerate(bench.iterrows()):
        vals = [r["NMI"], r["ARI"], r["Silhouette"]]
        rects = ax.bar(x + (i - 1) * w, vals, w, label=names[i], color=colors[i], edgecolor="#333", linewidth=0.5)
        ax.bar_label(rects, fmt="%.2f", padding=1.5, fontsize=5.5)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=7)
    ax.set_ylabel(fa("مقدار شاخص"), fontsize=7)
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(fontsize=6, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.13))
    fig.savefig(os.path.join(FIG_DIR, "fig5_benchmark_fa.png"))
    plt.close(fig)


if __name__ == "__main__":
    fig_architecture()
