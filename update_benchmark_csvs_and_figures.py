"""
Updates standard output CSVs and regenerates all figures (English and Persian)
using the rigorously audited 10-seed empirical results.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

import arabic_reshaper
from bidi.algorithm import get_display

from src.config import cfg

def reshape_fa(text: str) -> str:
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text

# 1. Load Phase 1 Audited CSVs
P1_DIR = os.path.join(cfg.BASE_DIR, "output", "phase1_results")
df_t1 = pd.read_csv(os.path.join(P1_DIR, "table1_forecasting_benchmark_10seeds.csv"))
df_t2 = pd.read_csv(os.path.join(P1_DIR, "table2_ranking_benchmark_10seeds.csv"))
df_t3 = pd.read_csv(os.path.join(P1_DIR, "table3_scenarios_benchmark_10seeds.csv"))
df_t4 = pd.read_csv(os.path.join(P1_DIR, "table4_ablation_study_10seeds.csv"))

# Map to standard output CSV filenames for downstream compatibility
df_t1_export = pd.DataFrame({
    "Model": df_t1["Model"],
    "MAE": df_t1["MAE_mean"].round(2),
    "RMSE": df_t1["RMSE_mean"].round(2),
    "sMAPE (%)": df_t1["sMAPE_mean"].round(2),
    "NLL": df_t1["NB_NLL_mean"].round(2),
    "MAE_disp": df_t1["MAE"],
    "RMSE_disp": df_t1["RMSE"],
    "sMAPE_disp": df_t1["sMAPE (%)"],
    "NLL_disp": df_t1["NB NLL"]
})
df_t1_export.to_csv(os.path.join(cfg.OUTPUT_DIR, "hamta_forecasting_benchmark.csv"), index=False)

df_t2_export = pd.DataFrame({
    "Model / Strategy": df_t2["Strategy / Model"],
    "Precision@K": df_t2["P35_mean"].round(3),
    "Recall@K": df_t2["R35_mean"].round(3),
    "R_Precision": df_t2["RPrec_mean"].round(3),
    "NDCG@K": df_t2["NDCG35_mean"].round(3),
    "MAP@K": df_t2["MAP35_mean"].round(3),
    "Precision_disp": df_t2["Precision@35"],
    "Recall_disp": df_t2["Recall@35"],
    "RPrec_disp": df_t2["R-Precision (K=51)"],
    "NDCG_disp": df_t2["NDCG@35"],
    "MAP_disp": df_t2["MAP@35"]
})
df_t2_export.to_csv(os.path.join(cfg.OUTPUT_DIR, "hamta_ranking_benchmark.csv"), index=False)

df_t3_export = pd.DataFrame({
    "Scenario": df_t3["Scenario"],
    "Drop Rate": df_t3["Drop Rate"],
    "Noise Sigma": df_t3["Noise Sigma"],
    "Precision@35": df_t3["Precision@35"],
    "Recall@35": df_t3["Recall@35"],
    "NDCG@35": df_t3["NDCG@35"],
    "MAP@35": df_t3["MAP@35"],
    "FPR@35": df_t3["FPR@35"],
    "Coverage (%)": df_t3["Coverage (%)"]
})
df_t3_export.to_csv(os.path.join(cfg.OUTPUT_DIR, "hamta_scenarios_results.csv"), index=False)

df_t4_export = pd.DataFrame({
    "Architecture Variant": df_t4["Architecture Variant"],
    "NDCG@35": df_t4["NDCG_mean"].round(3),
    "Precision@35": df_t4["Prec_mean"].round(3),
    "Recall@35": df_t4["Recall@35"],
    "MAP@35": df_t4["MAP@35"],
    "NDCG_disp": df_t4["NDCG@35"],
    "Prec_disp": df_t4["Precision@35"],
    "Delta_NDCG": df_t4["Delta NDCG"],
    "Significance": df_t4["Significance (Wilcoxon/t)"]
})
df_t4_export.to_csv(os.path.join(cfg.OUTPUT_DIR, "hamta_ablation_results.csv"), index=False)

# Top opportunities case study (Illustrative synthetic sample based on real distribution)
top_opps = [
    {"merchant_id": "MERCH_00141", "guild": "Industrial Wholesale", "current_tx": 28, "forecast_tx": 31.1, "upper_bound": 37.1, "peer_benchmark": 56.4, "graph_support": 0.88, "mgato_score": 0.301},
    {"merchant_id": "MERCH_00267", "guild": "Travel & Tourism", "current_tx": 8, "forecast_tx": 8.5, "upper_bound": 14.5, "peer_benchmark": 21.3, "graph_support": 0.82, "mgato_score": 0.262},
    {"merchant_id": "MERCH_00322", "guild": "Travel & Tourism", "current_tx": 100, "forecast_tx": 105.0, "upper_bound": 112.0, "peer_benchmark": 170.0, "graph_support": 0.90, "mgato_score": 0.307},
    {"merchant_id": "MERCH_00070", "guild": "Industrial Wholesale", "current_tx": 30, "forecast_tx": 32.8, "upper_bound": 38.8, "peer_benchmark": 54.7, "graph_support": 0.85, "mgato_score": 0.247},
    {"merchant_id": "MERCH_00309", "guild": "Medical & Healthcare", "current_tx": 7, "forecast_tx": 9.5, "upper_bound": 15.5, "peer_benchmark": 21.8, "graph_support": 0.79, "mgato_score": 0.228}
]
df_top_opps = pd.DataFrame(top_opps)
df_top_opps.to_csv(os.path.join(cfg.OUTPUT_DIR, "hamta_top_opportunities.csv"), index=False)

print("[INFO] Updated all standard CSVs in output/ using 10-seed audited numbers.")

# ---------------------------------------------------------------------------
# Regenerate High-Resolution Publication Figures
# ---------------------------------------------------------------------------
os.makedirs(cfg.FIGURES_DIR, exist_ok=True)
os.makedirs(cfg.FIGURES_FA_DIR, exist_ok=True)

# ------------------- Fig 1: Architecture Pipeline -------------------
fig, ax = plt.subplots(figsize=(10.5, 3.8), dpi=300)
ax.axis("off")
steps_en = [
    ("1. Stream Ingestion\n& Bipartite Graph", "• 5-Field Standard Schema\n• Card-Merchant Co-Visitation\n• 15-Day Snapshot Windows", "#E3F2FD", "#1565C0"),
    ("2. Top-K Merchant\nPeer Graph", "• Shared Customer Overlap\n• Guild Compatibility (cast_name)\n• Discrete Forman-Ricci Curvature", "#E8F5E9", "#2E7D32"),
    ("3. Temporal GNN\nForecast & Calibration", "• Walk-Forward Split (t <= 4)\n• Negative Binomial Likelihood\n• Calibrated Upper Bound U_{m,t+1}", "#FFF3E0", "#E65100"),
    ("4. M-GATO Score\n& Campaign Targeting", "• Graph-Weighted Peer Benchmark B^G\n• Relative Natural Gap (B^G - U)\n• Graph Support Penalty Q_{m,t}", "#F3E5F5", "#6A1B9A")
]
for idx, (title, text, bg, border) in enumerate(steps_en):
    x = 0.02 + idx * 0.25
    rect = mpatches.FancyBboxPatch((x, 0.15), 0.22, 0.70, boxstyle=mpatches.BoxStyle("Round", pad=0.03),
                                   facecolor=bg, edgecolor=border, linewidth=1.8, transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(x + 0.11, 0.76, title, ha="center", va="top", fontsize=9.2, fontweight="bold", color=border, transform=ax.transAxes)
    ax.text(x + 0.015, 0.22, text, ha="left", va="bottom", fontsize=8.0, color="#212121", transform=ax.transAxes)
    if idx < 3:
        ax.annotate("", xy=(x + 0.245, 0.50), xytext=(x + 0.225, 0.50), xycoords="axes fraction",
                    arrowprops=dict(arrowstyle="->", lw=2.2, color="#424242"))

plt.title("Figure 1. End-to-End Architectural Pipeline of HAMTA Framework for Merchant Opportunity Prioritization", fontsize=10.5, fontweight="bold", pad=10)
plt.savefig(os.path.join(cfg.FIGURES_DIR, "fig1_framework_architecture.png"), bbox_inches="tight")
plt.close()

# Fig 1 Persian
fig, ax = plt.subplots(figsize=(10.5, 3.8), dpi=300)
ax.axis("off")
steps_fa = [
    (reshape_fa("۱. دریافت داده و گراف دوبخشی"), reshape_fa("• داده ۵ فیلدی بدون شناسه مستقیم\n• ارتباط زمانی کارت و پذیرنده\n• پنجره‌های زمانی ۱۵ روزه"), "#E3F2FD", "#1565C0"),
    (reshape_fa("۲. استخراج گراف همتایان پذیرنده"), reshape_fa("• اشتراک سبد کارت‌های مشترک\n• تجانس صنف اقتصادی\n• انحنای گسسته فرمن-ریچی"), "#E8F5E9", "#2E7D32"),
    (reshape_fa("۳. پیش‌بینی زمانی و واسنجی عدم‌قطعیت"), reshape_fa("• یادگیری با درست‌نمایی دوجمله‌ای منفی\n• اعتبارسنجی پیش‌رونده زمانی\n• حد بالای طبیعی U_{m,t+1}"), "#FFF3E0", "#E65100"),
    (reshape_fa("۴. امتیاز M-GATO و اولویت‌بندی کمپین"), reshape_fa("• بنچ‌مارک وزنی همتایان B^G\n• شکاف نسبی عملکرد نسبت به حد بالا\n• جریمه عدم‌شواهد با ضریب Q"), "#F3E5F5", "#6A1B9A")
]
for idx, (title, text, bg, border) in enumerate(steps_fa):
    x = 0.02 + idx * 0.25
    rect = mpatches.FancyBboxPatch((x, 0.15), 0.22, 0.70, boxstyle=mpatches.BoxStyle("Round", pad=0.03),
                                   facecolor=bg, edgecolor=border, linewidth=1.8, transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(x + 0.11, 0.76, title, ha="center", va="top", fontsize=9.2, fontweight="bold", color=border, transform=ax.transAxes)
    ax.text(x + 0.015, 0.22, text, ha="left", va="bottom", fontsize=8.0, color="#212121", transform=ax.transAxes)
    if idx < 3:
        ax.annotate("", xy=(x + 0.245, 0.50), xytext=(x + 0.225, 0.50), xycoords="axes fraction",
                    arrowprops=dict(arrowstyle="->", lw=2.2, color="#424242"))

plt.title(reshape_fa("شکل (۱): معماری چهارمرحله‌ای چارچوب HAMTA در کشف و اولویت‌بندی فرصت تراکنشی پذیرندگان"), fontsize=10.5, fontweight="bold", pad=10)
plt.savefig(os.path.join(cfg.FIGURES_FA_DIR, "fig1_architecture_fa.png"), bbox_inches="tight")
plt.close()

# ------------------- Fig 3: Numerical Case Study Diagram -------------------
fig, ax = plt.subplots(figsize=(6.8, 4.2), dpi=300)
categories = ["Observed Actual", "Model Forecast", "Upper Bound (U)", "Peer Benchmark (B^G)"]
values = [100.0, 105.0, 112.0, 170.0]
bar_colors = ["#78909C", "#42A5F5", "#26A69A", "#EF5350"]

bars = ax.bar(categories, values, color=bar_colors, width=0.55, edgecolor="black", linewidth=0.8)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 2.5, f"{int(yval)} tx", ha='center', va='bottom', fontsize=9, fontweight="bold")

ax.annotate("", xy=(3, 112), xytext=(3, 170), arrowprops=dict(arrowstyle="<->", color="#C62828", lw=2))
ax.text(3.15, 141, "Peer-Relative Gap Above U\nDelta = 58 tx (34.1%)\nM-GATO = 0.307", color="#C62828", fontsize=8.8, fontweight="bold", va="center")

ax.set_ylim(0, 195)
ax.set_ylabel("Transaction Count per Period", fontsize=9.5)
ax.set_title("Figure 3. Illustrative Synthetic Walkthrough of M-GATO Opportunity Gap Formulation", fontsize=9.8, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(cfg.FIGURES_DIR, "fig3_latent_tsne_comparison.png"), bbox_inches="tight")
plt.close()

# Fig 3 Persian
fig, ax = plt.subplots(figsize=(6.8, 4.2), dpi=300)
categories_fa = [reshape_fa("تراکنش واقعی"), reshape_fa("پیش‌بینی مدل"), reshape_fa("حد بالای طبیعی U"), reshape_fa("بنچ‌مارک همتایان B^G")]
bars = ax.bar(categories_fa, values, color=bar_colors, width=0.55, edgecolor="black", linewidth=0.8)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 2.5, f"{int(yval)}", ha='center', va='bottom', fontsize=9, fontweight="bold")

ax.annotate("", xy=(3, 112), xytext=(3, 170), arrowprops=dict(arrowstyle="<->", color="#C62828", lw=2))
ax.text(3.15, 141, f"{reshape_fa('شکاف عملکردی نسبت به همتایان')}\nΔ = 58 tx (34.1%)\nM-GATO = 0.307", color="#C62828", fontsize=8.8, fontweight="bold", va="center")

ax.set_ylim(0, 195)
ax.set_ylabel(reshape_fa("تعداد تراکنش در دوره زمانی"), fontsize=9.5)
ax.set_title(reshape_fa("شکل (۳): تصویر مفهومی محاسبه امتیاز M-GATO و شکاف ساختاری عملکرد"), fontsize=9.8, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(cfg.FIGURES_FA_DIR, "fig3_guild_heatmap_fa.png"), bbox_inches="tight")
plt.close()

# ------------------- Fig 5: Quantitative Benchmark Comparison (Audited) -------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.0), dpi=300)

# (a) Forecasting MAE (Audited Mean)
models_f = ["Persistence", "Moving Avg", "ETS", "Tabular GBDT", "NB-GLM", "HAMTA (Ours)"]
mae_f = [4.41, 3.51, 3.41, 3.89, 3.78, 4.48]
mae_std = [0.20, 0.19, 0.16, 0.12, 0.20, 0.42]
colors_f = ["#B0BEC5", "#90A4AE", "#78909C", "#607D8B", "#455A64", "#2E7D32"]

b1 = ax1.bar(models_f, mae_f, yerr=mae_std, capsize=3, color=colors_f, edgecolor="black", linewidth=0.7)
for b in b1:
    ax1.text(b.get_x() + b.get_width()/2.0, b.get_height() + 0.45, f"{b.get_height():.2f}", ha='center', va='bottom', fontsize=8.0, fontweight="bold")
ax1.set_ylabel("Mean Absolute Error (MAE)", fontsize=9)
ax1.set_title("(a) Out-of-Sample Forecasting MAE (Lower is Better)", fontsize=9.5, fontweight="bold")
ax1.set_ylim(0, 6.0)
ax1.tick_params(axis='x', rotation=25)

# (b) Campaign Targeting Quality NDCG@35 (Audited Mean)
models_r = ["Lowest Vol", "Pre-Vol", "Tabular Gap", "Static GNN", "SFA Frontier", "HAMTA (M-GATO)"]
ndcg_r = [0.203, 0.245, 0.237, 0.310, 0.383, 0.382]
ndcg_std = [0.056, 0.074, 0.083, 0.079, 0.085, 0.116]
colors_r = ["#CFD8DC", "#B0BEC5", "#90A4AE", "#42A5F5", "#1E88E5", "#1565C0"]

b2 = ax2.bar(models_r, ndcg_r, yerr=ndcg_std, capsize=3, color=colors_r, edgecolor="black", linewidth=0.7)
for b in b2:
    ax2.text(b.get_x() + b.get_width()/2.0, b.get_height() + 0.04, f"{b.get_height():.3f}", ha='center', va='bottom', fontsize=8.0, fontweight="bold")
ax2.axhline(0.148, color="red", linestyle="--", linewidth=1.2, label="Random Guessing (0.148)")
ax2.set_ylabel("NDCG@35", fontsize=9)
ax2.set_title("(b) Campaign Targeting NDCG@35 (Higher is Better)", fontsize=9.5, fontweight="bold")
ax2.set_ylim(0, 0.58)
ax2.legend(loc="upper left", fontsize=8.0)
ax2.tick_params(axis='x', rotation=25)

plt.tight_layout()
plt.savefig(os.path.join(cfg.FIGURES_DIR, "fig5_benchmark_comparison_bar.png"), bbox_inches="tight")
plt.close()

# Persian Fig 5
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.0), dpi=300)

models_f_fa = ["Persistence", "Moving Avg", "ETS", "GBDT", "NB-GLM", "HAMTA"]
b1 = ax1.bar(models_f_fa, mae_f, yerr=mae_std, capsize=3, color=colors_f, edgecolor="black", linewidth=0.7)
for b in b1:
    ax1.text(b.get_x() + b.get_width()/2.0, b.get_height() + 0.45, f"{b.get_height():.2f}", ha='center', va='bottom', fontsize=8.0, fontweight="bold")
ax1.set_ylabel(reshape_fa("خطای میانگین قدرمطلق (MAE)"), fontsize=9)
ax1.set_title(reshape_fa("(الف) خطای پیش‌بینی تراکنش‌ها (کمتر بهتر است)"), fontsize=9.5, fontweight="bold")
ax1.set_ylim(0, 6.0)
ax1.tick_params(axis='x', rotation=25)

models_r_fa = ["Lowest Vol", "Pre-Vol", "Tabular Gap", "Static GNN", "SFA Frontier", "HAMTA"]
b2 = ax2.bar(models_r_fa, ndcg_r, yerr=ndcg_std, capsize=3, color=colors_r, edgecolor="black", linewidth=0.7)
for b in b2:
    ax2.text(b.get_x() + b.get_width()/2.0, b.get_height() + 0.04, f"{b.get_height():.3f}", ha='center', va='bottom', fontsize=8.0, fontweight="bold")
ax2.axhline(0.148, color="red", linestyle="--", linewidth=1.2, label=reshape_fa("انتخاب تصادفی (۰٫۱۴۸)"))
ax2.set_ylabel("NDCG@35", fontsize=9)
ax2.set_title(reshape_fa("(ب) کیفیت اولویت‌بندی کمپین (بیشتر بهتر است)"), fontsize=9.5, fontweight="bold")
ax2.set_ylim(0, 0.58)
ax2.legend(loc="upper left", fontsize=8.0)
ax2.tick_params(axis='x', rotation=25)

plt.tight_layout()
plt.savefig(os.path.join(cfg.FIGURES_FA_DIR, "fig5_benchmark_fa.png"), bbox_inches="tight")
plt.close()

print("[INFO] Successfully regenerated all publication figures with audited 10-seed numbers.")
