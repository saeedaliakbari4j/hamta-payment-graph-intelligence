import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

from src.config import cfg

COL_IN = 7.0
FA_FONT = 'Tahoma'
P1 = os.path.join(cfg.BASE_DIR, "output", "phase1_results")

_FA_DIG = str.maketrans('0123456789.', '۰۱۲۳۴۵۶۷۸۹٫')
def fdig(x):
    return str(x).translate(_FA_DIG)

mb = pd.read_csv(os.path.join(P1, "audit_multibudget_sample_std.csv"))
strat = ["Lowest Volume Heuristic (Test)", "Tabular Point Gap (GBDT)", "Static GNN Gap",
         "SFA-Style Frontier Gap", "HAMTA Proposed (M-GATO)"]
fa_labels = ["کمترین حجم", "شکاف جدولی", "شکاف GNN ایستا", "شکاف مرزی SFA", "HAMTA (پیشنهادی)"]
cols = ["#B0BEC5", "#78909C", "#64B5F6", "#FFB74D", "#C62828"]
mk = ["v", "s", "^", "D", "o"]
ks = sorted(mb["Budget (K)"].unique())
prev = 52 / 350

fig, ax = plt.subplots(figsize=(COL_IN, 2.6))
for s, lf, c, m in zip(strat, fa_labels, cols, mk):
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

ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fdig(f"{v:.1f}")))
ax.set_ylabel("دقت اولویت‌بندی Precision@K (۱۰ سید)", fontsize=9.5, family=FA_FONT)
ax.text(len(ks) - 1 + 0.25, prev + 0.012, f"شانس تصادفی = {fdig('0.149')}", fontsize=8.0,
        ha="right", va="bottom", family=FA_FONT, color="#424242")

ax.legend(ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.25),
          prop={"family": FA_FONT, "size": 8.0})

plt.savefig("test_fig4_fa.png", bbox_inches="tight", pad_inches=0.04, dpi=300)
print("saved test_fig4_fa.png")
