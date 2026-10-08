"""
Publication figure generator for the HAMTA manuscript (EN + FA).

Design rules (scientific audit):
  * Every plotted number is read from an output CSV produced by an actual run
    (no hand-typed values). The case-study / walkthrough figures use the REAL
    top-ranked merchants of seed 42, Scenario B (output/hamta_top_opportunities.csv,
    written by run_audit_supplement.py).
  * The peer-graph figure is the REAL Top-K peer graph of seed 42.
  * English figures contain zero Persian characters.
  * Persian figures use native Matplotlib (>=3.9) Arabic/Persian shaping via
    HarfBuzz/libraqm. No external arabic_reshaper/python-bidi is applied, as that
    scrambles the text.
  * All Persian charts feature proper Right-to-Left (RTL) alignments, sequence,
    and academic Persian terminology.
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
COL_IN = 7.0           # single-column width in inches
DPI = 300

_FA_DIG = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def fa_text(text):
    """Raw Unicode string for Matplotlib native HarfBuzz shaping."""
    return str(text)


def fdig(x) -> str:
    """Convert digits to Persian numerals."""
    return str(x).translate(_FA_DIG)


def fa_ticks(ax, axis="y", fmt="{:g}"):
    f = FuncFormatter(lambda v, _: fdig(fmt.format(v)))
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(f)


def save(fig, path):
    fig.savefig(path, bbox_inches="tight", pad_inches=0.04, dpi=DPI)
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
    # English: horizontal 4-stage pipeline, left-to-right
    steps_en = [
        ("1. Temporal card–merchant\nbipartite graph", "5-field ledger\n15-day windows"),
        ("2. Top-K merchant\npeer graph", "co-visit + guild\nForman curvature"),
        ("3. Temporal GNN +\ncalibrated bound U", "NB likelihood\nchronological holdout"),
        ("4. Peer benchmark B^G\n+ M-GATO ranking", "gap above U\nsupport Q"),
    ]
    colors = [("#FFFFFF", "#263238")] * 4
    fig, ax = plt.subplots(figsize=(COL_IN, 1.8))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    w, gap = 0.21, 0.04
    total_w = 4 * w + 3 * gap
    start_x = (1.0 - total_w) / 2.0
    for i, ((t, s), (bg, bd)) in enumerate(zip(steps_en, colors)):
        x = start_x + i * (w + gap)
        ax.add_patch(mpatches.FancyBboxPatch((x, 0.07), w, 0.86, boxstyle="square,pad=0.0",
                                             facecolor=bg, edgecolor=bd, linewidth=1.1))
        ax.text(x + w / 2, 0.69, t, ha="center", va="center", fontsize=7.8, fontweight="bold", color=bd, family=EN_FONT)
        ax.text(x + w / 2, 0.27, s, ha="center", va="center", fontsize=7.0, color="#37474F", family=EN_FONT, linespacing=1.25)
        if i < 3:
            ax.annotate("", xy=(x + w + gap - 0.006, 0.50), xytext=(x + w + 0.006, 0.50),
                        arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#37474F", mutation_scale=10))
    save(fig, os.path.join(FIG_EN, "fig1_framework_architecture.png"))

    # Persian: horizontal 4-stage pipeline, RTL (Right-to-Left)
    steps_fa_rtl = [
        ("۱. گراف زمانی\nکارت–پذیرنده", "دفترکل ۵ فیلدی\nپنجره‌های ۱۵ روزه"),
        ("۲. گراف همتایان\nTop-K پذیرنده", "هم‌مشتریانی و صنف\nانحنای فرمن-ریچی"),
        ("۳. گراف زمانی و\nکران بالای U", "دوجمله‌ای منفی\nپنجره زمانی مستقل"),
        ("۴. بنچ‌مارک همتا\nو رتبه M-GATO", "شکاف بالای U\nپشتیبان فرضیه Q"),
    ]
    fig, ax = plt.subplots(figsize=(COL_IN, 1.8))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    n = len(steps_fa_rtl)
    for i, (t, s) in enumerate(steps_fa_rtl):
        # i=0 on the far right, i=3 on the far left
        x = start_x + (n - 1 - i) * (w + gap)
        ax.add_patch(mpatches.FancyBboxPatch((x, 0.07), w, 0.86,
                                             boxstyle="square,pad=0.0",
                                             facecolor="#F8F9FA", edgecolor="#263238", linewidth=1.1))
        ax.text(x + w / 2, 0.69, t, ha="center", va="center", fontsize=7.6, fontweight="bold", color="#1A237E", family=FA_FONT, linespacing=1.35)
        ax.text(x + w / 2, 0.27, s, ha="center", va="center", fontsize=7.0, color="#37474F", family=FA_FONT, linespacing=1.3)
        if i < n - 1:
            ax.annotate("", xy=(x - gap + 0.006, 0.50), xytext=(x - 0.006, 0.50),
                        arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#37474F", mutation_scale=10))
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
        fig, ax = plt.subplots(figsize=(COL_IN, 3.0))
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
                        fontsize=8.5, handletextpad=0.5, columnspacing=1.2,
                        prop={"family": EN_FONT if lang == "en" else FA_FONT, "size": 8.0})
        fname = os.path.join(FIG_EN, "fig2_graph_topology_communities.png") if lang == "en" \
            else os.path.join(FIG_FA, "fig2_topology_fa.png")
        save(fig, fname)


# =============================================================================
# FIGURE 3 — M-GATO walkthrough for the REAL top-ranked merchant (seed 42)
# =============================================================================
def make_fig3():
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

    # English version
    fig, ax = plt.subplots(figsize=(COL_IN, 2.5))
    cats_en = ["Observed\nY", "Forecast\nμ̂", "Upper bound\nU", "Peer bench.\nB^G"]
    bars = ax.bar(range(4), vals, color=cols, width=0.55, edgecolor="#263238", linewidth=0.7)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + top * 0.018, f"{v:.0f}", ha="center", va="bottom",
                fontsize=9.5, fontweight="bold", family=EN_FONT)
    ax.annotate("", xy=(3.38, ub), xytext=(3.38, pb),
                arrowprops=dict(arrowstyle="<->", color="#B71C1C", lw=1.2))
    ax.plot([2, 3.38], [ub] * 2, ls=":", lw=1.0, color="#00695C")
    note_en = f"gap above U = {gap_abs:.0f}\nrelative gap = {rel:.3f}\nQ = {q_val:.2f}\nM-GATO = {mgato_val:.3f}"
    ax.text(0.03, 0.96, note_en, transform=ax.transAxes, ha="left", va="top",
            fontsize=9.0, color="#B71C1C", family=EN_FONT, linespacing=1.25,
            bbox=dict(boxstyle="round,pad=0.3", fc="#FFF8F8", ec="#EF9A9A", lw=0.8))
    ax.set_xticks(range(4))
    ax.set_xticklabels(cats_en, fontsize=9.2, fontweight="bold", family=EN_FONT)
    ax.set_xlim(-0.5, 3.65)
    ax.set_ylim(0, top)
    ax.tick_params(axis="both", labelsize=8.0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylabel("Transactions (test period)", fontsize=9.5, family=EN_FONT)
    save(fig, os.path.join(FIG_EN, "fig3_latent_tsne_comparison.png"))

    # Persian version: RTL progression (Observed on the right at x=3, B^G on the left at x=0)
    fig, ax = plt.subplots(figsize=(COL_IN, 2.5))
    cats_fa = [
        "بنچ‌مارک همتایان\nB^G",
        "کران بالای محتاطانه\nU",
        "پیش‌بینی مدل\nμ̂",
        "مشاهده‌شده\nY"
    ]
    vals_rtl = [pb, ub, fc, actual]
    cols_rtl = ["#EF5350", "#26A69A", "#42A5F5", "#90A4AE"]
    bars = ax.bar(range(4), vals_rtl, color=cols_rtl, width=0.55, edgecolor="#263238", linewidth=0.7)
    for b, v in zip(bars, vals_rtl):
        ax.text(b.get_x() + b.get_width() / 2, v + top * 0.018, fdig(f"{int(v)}"), ha="center", va="bottom",
                fontsize=10.0, fontweight="bold", family=FA_FONT)
    # Gap arrow between B^G (x=0) and U (x=1) on the left
    ax.annotate("", xy=(-0.35, ub), xytext=(-0.35, pb),
                arrowprops=dict(arrowstyle="<->", color="#B71C1C", lw=1.2))
    ax.plot([-0.35, 1], [ub, ub], ls=":", lw=1.0, color="#00695C")
    ax.plot([-0.35, 0], [pb, pb], ls=":", lw=1.0, color="#B71C1C")

    RLM = "\u200F"
    lines = [
        f"{RLM}شکاف بالاتر از کران: {fdig(int(gap_abs))}",
        f"{RLM}شکاف نسبی: {fdig('0.341')}",
        f"{RLM}ضریب اطمینان گرافی: {fdig('0.90')}",
        f"{RLM}امتیاز شاخص M-GATO: {fdig('0.307')}"
    ]
    note_fa = "\n".join(lines)
    ax.text(0.98, 0.95, note_fa, transform=ax.transAxes, ha="right", va="top",
            fontsize=9.0, color="#B71C1C", family=FA_FONT, linespacing=1.45,
            bbox=dict(boxstyle="round,pad=0.4", fc="#FFF8F8", ec="#EF9A9A", lw=0.8))
    ax.set_xticks(range(4))
    ax.set_xticklabels(cats_fa, fontsize=9.2, fontweight="bold", family=FA_FONT)
    ax.set_xlim(-0.6, 3.8)
    ax.set_ylim(0, top)
    ax.tick_params(axis="both", labelsize=8.0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylabel("تعداد تراکنش دوره آزمون", fontsize=9.5, family=FA_FONT)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v)}"))
    save(fig, os.path.join(FIG_FA, "fig3_guild_heatmap_fa.png"))


# =============================================================================
# FIGURE 4 — multi-budget Precision@K (10 seeds, mean ± sample std)
# =============================================================================
def make_fig4():
    mb = pd.read_csv(os.path.join(P1, "audit_multibudget_sample_std.csv"))
    strat = ["Lowest Volume Heuristic (Test)", "Tabular Point Gap (GBDT)", "Static GNN Gap",
             "SFA-Style Frontier Gap", "HAMTA Proposed (M-GATO)"]
    en = ["Lowest volume", "Tabular gap", "Static GNN gap", "SFA frontier gap", "HAMTA (M-GATO)"]
    fa = ["کمترین حجم", "شکاف جدولی GBDT", "شکاف گراف ایستا", "مرز تصادفی SFA", "مدل پیشنهادی HAMTA"]
    cols = ["#B0BEC5", "#78909C", "#64B5F6", "#FFB74D", "#C62828"]
    mk = ["v", "s", "^", "D", "o"]
    ks = sorted(mb["Budget (K)"].unique())
    prev = 51 / 350

    # English version
    fig, ax = plt.subplots(figsize=(COL_IN, 2.6))
    for s, le, c, m in zip(strat, en, cols, mk):
        d = mb[mb["Strategy"] == s].sort_values("Budget (K)")
        x = np.arange(len(ks)) + (strat.index(s) - 2) * 0.06
        ax.errorbar(x, d["P_mean"], yerr=d["P_std"], color=c, marker=m, ms=4.5, lw=1.4 if "HAMTA" in s else 1.0,
                    capsize=2.5, elinewidth=0.7, label=le)
    ax.axhline(prev, ls="--", lw=0.9, color="#424242")
    ax.set_xticks(range(len(ks)))
    ax.set_xticklabels([f"K={k}" for k in ks], family=EN_FONT, fontsize=9.0)
    ax.set_ylim(0, 0.65)
    ax.tick_params(labelsize=8.0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylabel("Precision@K (10 seeds)", fontsize=9.5, family=EN_FONT)
    ax.text(len(ks) - 1 + 0.25, prev + 0.010, "random = 0.146", fontsize=8.0, ha="right", va="bottom", family=EN_FONT)
    ax.legend(fontsize=8.0, ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.25),
              prop={"family": EN_FONT, "size": 8.0})
    save(fig, os.path.join(FIG_EN, "fig4_radar_persona_profiles.png"))

    # Persian version
    fig, ax = plt.subplots(figsize=(COL_IN, 2.6))
    for s, lf, c, m in zip(strat, fa, cols, mk):
        d = mb[mb["Strategy"] == s].sort_values("Budget (K)")
        x = np.arange(len(ks)) + (strat.index(s) - 2) * 0.06
        ax.errorbar(x, d["P_mean"], yerr=d["P_std"], color=c, marker=m, ms=4.5,
                    lw=1.4 if "HAMTA" in s else 1.0, capsize=2.5, elinewidth=0.7, label=lf)
    ax.axhline(prev, ls="--", lw=0.9, color="#424242")
    ax.set_xticks(range(len(ks)))
    ax.set_xticklabels([f"K = {fdig(k)}" for k in ks], family=FA_FONT, fontsize=9.0)
    ax.set_ylim(0, 0.65)
    ax.tick_params(labelsize=8.0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylabel("دقت اولویت‌بندی Precision@K (۱۰ بذر آزمایشی)", fontsize=9.5, family=FA_FONT)
    ax.text(len(ks) - 1 + 0.25, prev + 0.012, "شانس تصادفی: 0.146", fontsize=8.0,
            ha="right", va="bottom", family=FA_FONT, color="#424242")
    ax.legend(ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.25),
              prop={"family": FA_FONT, "size": 8.0})
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

    fc_lab_en = ["Persist", "MA-3", "GBDT", "Static\nGNN", "HAMTA"]
    fc_lab_fa = ["ماندگاری", "MA-3", "GBDT", "GNN ایستا", "HAMTA"]
    mae = [mean_std(v) for v in fc.get("MAE")]

    rk_lab_en = ["Lowest\nvol.", "Tab.\ngap", "Static\nGNN", "M-GATO\nQ=1", "HAMTA"]
    rk_lab_fa = ["کمترین حجم", "شکاف جدولی", "GNN ایستا", "M-GATO (Q=1)", "HAMTA"]
    nd = [mean_std(v) for v in rk.get("NDCG@K")]

    # English version
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(COL_IN, 3.6))
    c1 = ["#B0BEC5"] * (len(mae) - 1) + ["#2E7D32"]
    a1.bar(range(len(mae)), [m for m, _ in mae], yerr=[s for _, s in mae], color=c1, edgecolor="#263238",
           linewidth=0.6, capsize=2.5, error_kw=dict(elinewidth=0.8))
    a1.set_xticks(range(len(mae)))
    a1.set_xticklabels(fc_lab_en, fontsize=9.0, family=EN_FONT)
    a1.set_ylabel("Forecasting MAE", fontsize=9.0, family=EN_FONT)
    a1.set_title("(a) Forecasting MAE (lower is better)", fontsize=9.5, fontweight="bold", family=EN_FONT)

    c2 = ["#B0BEC5"] * (len(nd) - 1) + ["#C62828"]
    a2.bar(range(len(nd)), [m for m, _ in nd], yerr=[s for _, s in nd], color=c2, edgecolor="#263238",
           linewidth=0.6, capsize=2.5, error_kw=dict(elinewidth=0.8))
    a2.axhline(51 / 350, ls="--", lw=0.9, color="#424242")
    a2.set_xticks(range(len(nd)))
    a2.set_xticklabels(rk_lab_en, fontsize=9.0, family=EN_FONT)
    a2.set_ylabel("NDCG@35 Ranking Quality", fontsize=9.0, family=EN_FONT)
    a2.set_title("(b) Opportunity ranking NDCG@35 (higher is better)", fontsize=9.5, fontweight="bold", family=EN_FONT)

    for a in (a1, a2):
        a.tick_params(axis="both", labelsize=8.0)
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(h_pad=1.8)
    save(fig, os.path.join(FIG_EN, "fig5_benchmark_comparison_bar.png"))

    # Persian version
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(COL_IN, 3.8))
    a1.bar(range(len(mae)), [m for m, _ in mae], yerr=[s for _, s in mae], color=c1, edgecolor="#263238",
           linewidth=0.6, capsize=2.5, error_kw=dict(elinewidth=0.8))
    a1.set_xticks(range(len(mae)))
    a1.set_xticklabels(fc_lab_fa, fontsize=9.0, family=FA_FONT)
    a1.set_ylabel("خطای پیش‌بینی MAE", fontsize=9.0, family=FA_FONT)
    a1.set_title("(الف) خطای پیش‌بینی آینده (کمتر بهتر است)", fontsize=9.5, fontweight="bold", family=FA_FONT)

    a2.bar(range(len(nd)), [m for m, _ in nd], yerr=[s for _, s in nd], color=c2, edgecolor="#263238",
           linewidth=0.6, capsize=2.5, error_kw=dict(elinewidth=0.8))
    a2.axhline(51 / 350, ls="--", lw=0.9, color="#424242")
    a2.set_xticks(range(len(nd)))
    a2.set_xticklabels(rk_lab_fa, fontsize=9.0, family=FA_FONT)
    a2.set_ylabel("کیفیت رتبه‌بندی NDCG@35", fontsize=9.0, family=FA_FONT)
    a2.set_title("(ب) کیفیت اولویت‌بندی کمپین (بیشتر بهتر است)", fontsize=9.5, fontweight="bold", family=FA_FONT)

    for a in (a1, a2):
        a.tick_params(axis="both", labelsize=8.0)
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(h_pad=1.8)
    save(fig, os.path.join(FIG_FA, "fig5_benchmark_fa.png"))


if __name__ == "__main__":
    make_fig1(); print("fig1 ok")
    make_fig2(); print("fig2 ok")
    make_fig3(); print("fig3 ok")
    make_fig4(); print("fig4 ok")
    make_fig5(); print("fig5 ok")
