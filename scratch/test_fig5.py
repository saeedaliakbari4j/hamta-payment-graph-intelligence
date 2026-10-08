import os
import re
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

from src.config import cfg

COL_IN = 7.0
FA_FONT = 'Tahoma'
OUT = cfg.OUTPUT_DIR

_FA_DIG = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
def fdig(x):
    return str(x).translate(_FA_DIG)

fc = pd.read_csv(os.path.join(OUT, "hamta_forecasting_benchmark.csv"))
rk = pd.read_csv(os.path.join(OUT, "hamta_ranking_benchmark.csv"))

def mean_std(s):
    parts = re.findall(r"\d+\.?\d*", str(s))
    return float(parts[0]), float(parts[1]) if len(parts) > 1 else 0.0

fc_lab_fa = ["ماندگاری", "MA-3", "GBDT", "GNN ایستا", "HAMTA"]
mae = [mean_std(v) for v in fc.get("MAE")]

rk_lab_fa = ["کمترین حجم", "شکاف جدولی", "GNN ایستا", "M-GATO (Q=1)", "HAMTA"]
nd = [mean_std(v) for v in rk.get("NDCG@K")]

fig, (a1, a2) = plt.subplots(2, 1, figsize=(COL_IN, 3.8))

# Subplot 1: Forecasting MAE
c1 = ["#B0BEC5"] * (len(mae) - 1) + ["#2E7D32"]
a1.bar(range(len(mae)), [m for m, _ in mae], yerr=[s for _, s in mae], color=c1, edgecolor="#263238",
       linewidth=0.6, capsize=2.5, error_kw=dict(elinewidth=0.8))
a1.set_xticks(range(len(mae)))
a1.set_xticklabels(fc_lab_fa, fontsize=9.0, family=FA_FONT)
a1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fdig(f"{v:g}")))
a1.set_ylabel("خطای پیش‌بینی MAE", fontsize=9.0, family=FA_FONT)
a1.set_title("(الف) خطای پیش‌بینی آینده (کمتر بهتر است)", fontsize=9.5, fontweight="bold", family=FA_FONT)

# Subplot 2: Ranking NDCG@35
c2 = ["#B0BEC5"] * (len(nd) - 1) + ["#C62828"]
a2.bar(range(len(nd)), [m for m, _ in nd], yerr=[s for _, s in nd], color=c2, edgecolor="#263238",
       linewidth=0.6, capsize=2.5, error_kw=dict(elinewidth=0.8))
a2.axhline(52 / 350, ls="--", lw=0.9, color="#424242")
a2.set_xticks(range(len(nd)))
a2.set_xticklabels(rk_lab_fa, fontsize=9.0, family=FA_FONT)
a2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fdig(f"{v:.1f}")))
a2.set_ylabel("کیفیت رتبه‌بندی NDCG@35", fontsize=9.0, family=FA_FONT)
a2.set_title("(ب) کیفیت اولویت‌بندی کمپین (بیشتر بهتر است)", fontsize=9.5, fontweight="bold", family=FA_FONT)

for a in (a1, a2):
    a.tick_params(axis="both", labelsize=8.0)
    a.spines[["top", "right"]].set_visible(False)

fig.tight_layout(h_pad=1.8)
plt.savefig("test_fig5_fa.png", bbox_inches="tight", pad_inches=0.04, dpi=300)
print("saved test_fig5_fa.png")
