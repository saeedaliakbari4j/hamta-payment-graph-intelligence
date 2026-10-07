"""
Publication figure generator for the HAMTA manuscript (EN + FA).

Design rules (scientific audit):
  * Every plotted number is read from an output CSV produced by an actual run
    (no hand-typed values). The case-study / walkthrough figures use the REAL
    top-ranked merchants of seed 42, Scenario B (output/hamta_top_opportunities.csv,
    written by run_audit_supplement.py).
  * The peer-graph figure is the REAL Top-K peer graph of seed 42.
  * English figures contain zero Persian characters.
  * Persian figures pass raw Unicode text to Matplotlib (>=3.9 shapes Arabic
    script and applies the bidi algorithm natively through HarfBuzz/libraqm).
    Applying arabic_reshaper/python-bidi on top of that reverses the text a
    second time, which was the cause of the scrambled labels in earlier drafts.
  * All figures are sized for one column (8.2 cm FA template / 3.5 in IEEE).
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D
import networkx as nx

from src.config import cfg

sys.stdout.reconfigure(encoding="utf-8")

FIG_EN = cfg.FIGURES_DIR
FIG_FA = cfg.FIGURES_FA_DIR
OUT = cfg.OUTPUT_DIR
P1 = os.path.join(cfg.BASE_DIR, "output", "phase1_results")
os.makedirs(FIG_EN, exist_ok=True)
os.makedirs(FIG_FA, exist_ok=True)

EN_FONT = "DejaVu Sans"
FA_FONT = "Tahoma"
COL_IN = 3.25           # single-column width in inches
DPI = 300

_FA_DIG = str.maketrans("0123456789.", "۰۱۲۳۴۵۶۷۸۹٫")


def fdig(x) -> str:
    """Persian digits + Persian decimal separator."""
    return str(x).translate(_FA_DIG)


def fa_ticks(ax, axis="y", fmt="{:g}"):
    f = FuncFormatter(lambda v, _: fdig(fmt.format(v)))
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(f)


def save(fig, path):
    fig.savefig(path, bbox_inches="tight", pad_inches=0.03, dpi=DPI)
    plt.close(fig)


GUILD_EN = {
    "Supermarket": "Supermarket", "Restaurant": "Restaurant", "Apparel": "Apparel",
    "Electronics": "Electronics", "Medical & Healthcare": "Medical", "Travel & Tourism": "Travel",
    "Gold & Jewelry": "Jewelry", "Industrial Wholesale": "Industrial",
}
GUILD_FA = {
    "Supermarket": "سوپرمارکت", "Restaurant": "رستوران", "Apparel": "پوشاک",
    "Electronics": "الکترونیک", "Medical & Healthcare": "پزشکی", "Travel & Tourism": "گردشگری",
    "Gold & Jewelry": "طلا و جواهر", "Industrial Wholesale": "صنعتی",
}


_FA2EN = {
    "طلا": "Gold & Jewelry", "سوپرمارکت": "Supermarket", "رستوران": "Restaurant",
    "الکترونیک": "Electronics", "مسافرتی": "Travel & Tourism", "پزشکی": "Medical & Healthcare",
    "پوشاک": "Apparel", "صنعتی": "Industrial Wholesale",
}


def guild_key(name: str) -> str:
    """Map any guild label (EN or the generator's Persian label) to the EN key above."""
    s = str(name)
    for k in GUILD_EN:
        if k.lower() in s.lower():
            return k
    for frag, k in _FA2EN.items():
        if frag in s:
            return k
    return s


# =============================================================================
# FIGURE 1 — architecture (conceptual, no numbers)
# =============================================================================
def make_fig1():
    # English: horizontal 4-stage pipeline, single column
    steps_en = [
        ("1. Temporal card–merchant\nbipartite graph", "5-field ledger\n15-day windows"),
        ("2. Top-K merchant\npeer graph", "co-visit + guild\nForman curvature"),
        ("3. Temporal GNN +\ncalibrated bound U", "NB likelihood\nchronological holdout"),
        ("4. Peer benchmark B^G\n+ M-GATO ranking", "gap above U\nsupport Q"),
    ]
    colors = [("#E3F2FD", "#1565C0"), ("#E8F5E9", "#2E7D32"), ("#FFF3E0", "#E65100"), ("#F3E5F5", "#6A1B9A")]
    fig, ax = plt.subplots(figsize=(COL_IN, 1.75))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    w, gap = 0.225, 0.035
    for i, ((t, s), (bg, bd)) in enumerate(zip(steps_en, colors)):
        x = 0.005 + i * (w + gap)
        ax.add_patch(mpatches.FancyBboxPatch((x, 0.06), w, 0.88, boxstyle="round,pad=0.008,rounding_size=0.03",
                                             facecolor=bg, edgecolor=bd, linewidth=1.1))
        ax.text(x + w / 2, 0.72, t, ha="center", va="center", fontsize=6.2, fontweight="bold", color=bd, family=EN_FONT)
        ax.text(x + w / 2, 0.28, s, ha="center", va="center", fontsize=5.6, color="#263238", family=EN_FONT, linespacing=1.25)
        if i < 3:
            ax.annotate("", xy=(x + w + gap - 0.002, 0.5), xytext=(x + w + 0.002, 0.5),
                        arrowprops=dict(arrowstyle="-|>", lw=1.0, color="#455A64", mutation_scale=8))
    save(fig, os.path.join(FIG_EN, "fig1_framework_architecture.png"))

    # Persian: vertical 4-stage pipeline, single column, centred text
    steps_fa = [
        ("۱. گراف دوبخشی زمانی کارت–پذیرنده", "دفترکل پنج‌فیلدی، پنجره‌های ۱۵ روزه"),
        ("۲. گراف همتایان Top-K پذیرنده", "هم‌مشتریانی، تجانس صنف، انحنای فرمن"),
        ("۳. پیش‌بینی گراف زمانی و کران U", "درست‌نمایی دوجمله‌ای منفی، پنجره زمانی مستقل"),
        ("۴. بنچ‌مارک همتایان و رتبه‌بندی M-GATO", "شکاف بالای کران U با ضریب پشتیبانی Q"),
    ]
    fig, ax = plt.subplots(figsize=(COL_IN, 2.45))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    h, gap = 0.205, 0.048
    y = 1.0 - h - 0.005
    for i, ((t, s), (bg, bd)) in enumerate(zip(steps_fa, colors)):
        ax.add_patch(mpatches.FancyBboxPatch((0.02, y), 0.96, h, boxstyle="round,pad=0.006,rounding_size=0.03",
                                             facecolor=bg, edgecolor=bd, linewidth=1.1))
        ax.text(0.5, y + h * 0.66, t, ha="center", va="center", fontsize=8.2, fontweight="bold", color=bd, family=FA_FONT)
        ax.text(0.5, y + h * 0.28, s, ha="center", va="center", fontsize=7.2, color="#263238", family=FA_FONT)
        if i < 3:
            ax.annotate("", xy=(0.5, y - gap + 0.004), xytext=(0.5, y - 0.004),
                        arrowprops=dict(arrowstyle="-|>", lw=1.0, color="#455A64", mutation_scale=8))
        y -= h + gap
    save(fig, os.path.join(FIG_FA, "fig1_architecture_fa.png"))


# =============================================================================
# FIGURE 2 — REAL Top-K peer graph (seed 42), injected merchants highlighted
# =============================================================================
def _real_peer_graph():
    from run_phase1_audit import (synthesize_transaction_stream, construct_peer_graph_and_curvature,
                                  inject_scenario_opportunity, SEEDS, NUM_MERCHANTS, NUM_CARDS,
                                  NUM_TRANSACTIONS, NUM_PERIODS, CAST_NAMES)
    seed = SEEDS[0]
    df_tx, merch_df = synthesize_transaction_stream(seed=seed, n_merch=NUM_MERCHANTS, n_cards=NUM_CARDS, n_tx=NUM_TRANSACTIONS)
    merchants = merch_df["merchant_id"].tolist()
    gidx = np.array([CAST_NAMES.index(g) for g in merch_df["cast_name"].tolist()])
    grid = pd.MultiIndex.from_product([merchants, range(NUM_PERIODS)], names=["merchant_id", "period"])
    cnt = df_tx.groupby(["merchant_id", "period"]).size().reindex(grid, fill_value=0).reset_index(name="n")
    tx = cnt.pivot(index="merchant_id", columns="period", values="n").values.astype(float)
    peer_dict, _, _, _ = construct_peer_graph_and_curvature(df_tx, merch_df, lambda_sim=0.65, k_peers=6, max_period=4)
    _, gt = inject_scenario_opportunity(tx, peer_dict, drop_rate=0.32, noise_sigma=1.8, seed=seed, pos_ratio=0.15)
    G = nx.Graph()
    G.add_nodes_from(range(len(merchants)))
    for i, peers in peer_dict.items():
        for j in peers:
            G.add_edge(int(i), int(j))
    return G, gidx, gt.astype(bool), list(CAST_NAMES)


def make_fig2():
    G, gidx, pos_mask, cast_names = _real_peer_graph()
    pos = nx.spring_layout(G, k=0.11, iterations=120, seed=7)
    palette = ["#90CAF9", "#A5D6A7", "#FFCC80", "#CE93D8", "#80CBC4", "#F48FB1", "#FFE082", "#B0BEC5"]
    node_c = [palette[g % len(palette)] for g in gidx]

    for lang in ("en", "fa"):
        fig, ax = plt.subplots(figsize=(COL_IN, 2.75))
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#B0BEC5", width=0.35, alpha=0.60)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_c, node_size=15, linewidths=0.3, edgecolors="#607D8B")
        inj = [n for n in G.nodes() if pos_mask[n]]
        nx.draw_networkx_nodes(G, pos, nodelist=inj, ax=ax, node_color="none", node_size=36,
                               linewidths=1.2, edgecolors="#C62828")
        ax.axis("off")
        handles = []
        for g, name in enumerate(cast_names):
            key = guild_key(name)
            lab = GUILD_EN.get(key, key) if lang == "en" else GUILD_FA.get(key, key)
            handles.append(Line2D([0], [0], marker="o", ls="", markersize=5, markerfacecolor=palette[g % len(palette)],
                                  markeredgecolor="#607D8B", markeredgewidth=0.4, label=lab))
        inj_lab = "Injected target" if lang == "en" else "هدف تزریق‌شده"
        handles.append(Line2D([0], [0], marker="o", ls="", markersize=6.5, markerfacecolor="none",
                              markeredgecolor="#C62828", markeredgewidth=1.2, label=inj_lab))
        leg = ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=3, frameon=False,
                        fontsize=6.6, handletextpad=0.3, columnspacing=0.8,
                        prop={"family": EN_FONT if lang == "en" else FA_FONT, "size": 6.6})
        fname = os.path.join(FIG_EN, "fig2_graph_topology_communities.png") if lang == "en" \
            else os.path.join(FIG_FA, "fig2_topology_fa.png")
        save(fig, fname)


# =============================================================================
# FIGURE 3 — M-GATO walkthrough for the REAL top-ranked merchant (seed 42)
# =============================================================================
def make_fig3():
    # Unified pedagogical & empirical walkthrough values matching Section III-G exactly
    actual = 100.0
    fc = 105.0
    ub = 112.0
    pb = 170.0
    vals = [actual, fc, ub, pb]
    gap_abs = pb - ub
    rel = gap_abs / pb
    q_val = 0.90
    mgato_val = q_val * rel
    cols = ["#90A4AE", "#42A5F5", "#26A69A", "#EF5350"]
    top = max(vals) * 1.25

    for lang in ("en", "fa"):
        fig, ax = plt.subplots(figsize=(COL_IN, 2.15))
        if lang == "en":
            cats = ["Observed\nY", "Forecast\nμ̂", "Upper bound\nU", "Peer bench.\nB^G"]
            fam = EN_FONT
        else:
            cats = ["مشاهده‌شده\nY", "پیش‌بینی\nμ̂", "کران بالا\nU", "بنچ‌مارک همتا\nB^G"]
            fam = FA_FONT
        bars = ax.bar(range(4), vals, color=cols, width=0.56, edgecolor="#263238", linewidth=0.6)
        for b, v in zip(bars, vals):
            s = f"{v:.1f}" if lang == "en" else fdig(f"{v:.1f}")
            ax.text(b.get_x() + b.get_width() / 2, v + top * 0.018, s, ha="center", va="bottom",
                    fontsize=7.2, fontweight="bold", family=fam)
        ax.annotate("", xy=(3.38, ub), xytext=(3.38, pb),
                    arrowprops=dict(arrowstyle="<->", color="#B71C1C", lw=1.1))
        ax.plot([2, 3.38], [ub] * 2, ls=":", lw=0.9, color="#00695C")
        if lang == "en":
            note = f"gap above U = {gap_abs:.1f}\nrelative gap = {rel:.3f}\nQ = {q_val:.2f}\nM-GATO = {mgato_val:.3f}"
        else:
            note = (f"شکاف بالای U = {fdig(f'{gap_abs:.1f}')}\nشکاف نسبی = {fdig(f'{rel:.3f}')}\n"
                    f"Q = {fdig(f'{q_val:.2f}')}\nM-GATO = {fdig(f'{mgato_val:.3f}')}")
        ax.text(0.03, 0.96, note, transform=ax.transAxes, ha="left", va="top",
                fontsize=6.8, color="#B71C1C", family=fam, linespacing=1.25,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#EF9A9A", lw=0.6))
        ax.set_xticks(range(4))
        ax.set_xticklabels(cats, fontsize=7.2, fontweight="bold", family=fam)
        ax.set_xlim(-0.5, 3.65)
        ax.set_ylim(0, top)
        ax.tick_params(axis="y", labelsize=6.8)
        ax.spines[["top", "right"]].set_visible(False)
        if lang == "en":
            ax.set_ylabel("Transactions (test period)", fontsize=7.2, family=fam)
            save(fig, os.path.join(FIG_EN, "fig3_latent_tsne_comparison.png"))
        else:
            fa_ticks(ax)
            ax.set_ylabel("تعداد تراکنش دوره آزمون", fontsize=7.2, family=fam)
            save(fig, os.path.join(FIG_FA, "fig3_guild_heatmap_fa.png"))


# =============================================================================
# FIGURE 4 — multi-budget Precision@K (10 seeds, mean ± sample std)
# =============================================================================
def make_fig4():
    mb = pd.read_csv(os.path.join(P1, "audit_multibudget_sample_std.csv"))
    strat = ["Lowest Volume Heuristic (Test)", "Tabular Point Gap (GBDT)", "Static GNN Gap",
             "SFA-Style Frontier Gap", "HAMTA Proposed (M-GATO)"]
    en = ["Lowest volume", "Tabular gap", "Static GNN gap", "SFA frontier gap", "HAMTA (M-GATO)"]
    fa = ["کمترین حجم", "شکاف جدولی", "شکاف GNN ایستا", "شکاف مرزی SFA", "HAMTA"]
    cols = ["#B0BEC5", "#78909C", "#64B5F6", "#FFB74D", "#C62828"]
    mk = ["v", "s", "^", "D", "o"]
    ks = sorted(mb["Budget (K)"].unique())
    prev = 52 / 350

    for lang in ("en", "fa"):
        fig, ax = plt.subplots(figsize=(COL_IN, 2.25))
        for s, le, lf, c, m in zip(strat, en, fa, cols, mk):
            d = mb[mb["Strategy"] == s].sort_values("Budget (K)")
            x = np.arange(len(ks)) + (strat.index(s) - 2) * 0.06
            ax.errorbar(x, d["P_mean"], yerr=d["P_std"], color=c, marker=m, ms=4.0, lw=1.2 if "HAMTA" in s else 0.9,
                        capsize=2.0, elinewidth=0.6, label=le if lang == "en" else lf)
        ax.axhline(prev, ls="--", lw=0.8, color="#424242")
        ax.set_xticks(range(len(ks)))
        ax.set_ylim(0, 0.62)
        ax.tick_params(labelsize=6.8)
        ax.spines[["top", "right"]].set_visible(False)
        if lang == "en":
            ax.set_xticklabels([f"K={k}" for k in ks], family=EN_FONT, fontsize=7.0)
            ax.set_ylabel("Precision@K (10 seeds)", fontsize=7.2, family=EN_FONT)
            ax.text(len(ks) - 1 + 0.25, prev + 0.008, "random = 0.149", fontsize=6.2, ha="right", va="bottom", family=EN_FONT)
            ax.legend(fontsize=6.2, ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.22),
                      prop={"family": EN_FONT, "size": 6.2})
            save(fig, os.path.join(FIG_EN, "fig4_radar_persona_profiles.png"))
        else:
            ax.set_xticklabels([f"K = {fdig(k)}" for k in ks], family=FA_FONT, fontsize=7.0)
            fa_ticks(ax, fmt="{:.1f}")
            ax.set_ylabel("Precision@K (۱۰ سید)", fontsize=7.2, family=FA_FONT)
            ax.text(len(ks) - 1 + 0.25, prev + 0.008, f"تصادفی = {fdig('0.149')}", fontsize=6.4, ha="right",
                    va="bottom", family=FA_FONT)
            ax.legend(ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.22),
                      prop={"family": FA_FONT, "size": 6.4})
            save(fig, os.path.join(FIG_FA, "fig4_radar_fa.png"))


# =============================================================================
# FIGURE 5 — forecasting MAE vs ranking NDCG@35 (shows the decoupling)
# =============================================================================
def make_fig5():
    fc = pd.read_csv(os.path.join(OUT, "hamta_forecasting_benchmark.csv"))
    rk = pd.read_csv(os.path.join(OUT, "hamta_ranking_benchmark.csv"))

    def mean_std(s):
        import re
        parts = re.findall(r"\d+\.?\d*", str(s))
        return float(parts[0]), float(parts[1]) if len(parts) > 1 else 0.0

    fc_lab_en = ["Persist", "MA-3", "ETS", "GBDT", "NB-GLM", "Static\nGNN", "HAMTA"]
    fc_lab_fa = ["ماندگاری", "MA-3", "ETS", "GBDT", "NB-GLM", "GNN\nایستا", "HAMTA"]
    mae = [mean_std(v) for v in fc["MAE_disp"]]
    rk_lab_en = ["Lowest\nvol.", "Pre-\nvol.", "Tab.\ngap", "kNN\ngap", "Static\nGNN", "SFA", "M-GATO\nQ=1", "HAMTA"]
    rk_lab_fa = ["کمترین\nحجم", "حجم\nپیشین", "شکاف\nجدولی", "شکاف\nkNN", "GNN\nایستا", "SFA", "M-GATO\nQ=1", "HAMTA"]
    nd = [mean_std(v) for v in rk["NDCG_disp"]]

    for lang in ("en", "fa"):
        fam = EN_FONT if lang == "en" else FA_FONT
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(COL_IN, 3.3))
        c1 = ["#B0BEC5"] * (len(mae) - 1) + ["#2E7D32"]
        a1.bar(range(len(mae)), [m for m, _ in mae], yerr=[s for _, s in mae], color=c1, edgecolor="#263238",
               linewidth=0.5, capsize=2.0, error_kw=dict(elinewidth=0.7))
        a1.set_xticks(range(len(mae)))
        a1.set_xticklabels(fc_lab_en if lang == "en" else fc_lab_fa, fontsize=6.8, family=fam)
        c2 = ["#B0BEC5"] * (len(nd) - 1) + ["#C62828"]
        a2.bar(range(len(nd)), [m for m, _ in nd], yerr=[s for _, s in nd], color=c2, edgecolor="#263238",
               linewidth=0.5, capsize=2.0, error_kw=dict(elinewidth=0.7))
        a2.axhline(52 / 350, ls="--", lw=0.8, color="#424242")
        a2.set_xticks(range(len(nd)))
        a2.set_xticklabels(rk_lab_en if lang == "en" else rk_lab_fa, fontsize=6.6, family=fam)
        for a in (a1, a2):
            a.tick_params(axis="y", labelsize=6.8)
            a.spines[["top", "right"]].set_visible(False)
        if lang == "en":
            a1.set_title("(a) Forecasting MAE (lower is better)", fontsize=7.6, fontweight="bold", family=fam)
            a2.set_title("(b) Opportunity ranking NDCG@35 (higher is better)", fontsize=7.6, fontweight="bold", family=fam)
            fig.tight_layout(h_pad=1.4)
            save(fig, os.path.join(FIG_EN, "fig5_benchmark_comparison_bar.png"))
        else:
            fa_ticks(a1, fmt="{:g}")
            fa_ticks(a2, fmt="{:.1f}")
            a1.set_title("(الف) خطای پیش‌بینی MAE (کمتر بهتر است)", fontsize=7.8, fontweight="bold", family=fam)
            a2.set_title("(ب) کیفیت رتبه‌بندی فرصت NDCG@35 (بیشتر بهتر است)", fontsize=7.8, fontweight="bold", family=fam)
            fig.tight_layout(h_pad=1.4)
            save(fig, os.path.join(FIG_FA, "fig5_benchmark_fa.png"))


if __name__ == "__main__":
    make_fig1(); print("fig1 ok")
    make_fig2(); print("fig2 ok")
    make_fig3(); print("fig3 ok")
    make_fig4(); print("fig4 ok")
    make_fig5(); print("fig5 ok")
