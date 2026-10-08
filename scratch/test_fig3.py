import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

COL_IN = 7.0
FA_FONT = 'Tahoma'

actual = 100.0
fc = 105.0
ub = 112.0
pb = 170.0
vals = [actual, fc, ub, pb]
gap_abs = pb - ub
rel = gap_abs / pb
q_val = 0.90
mgato_val = q_val * rel
cols = ['#90A4AE', '#42A5F5', '#26A69A', '#EF5350']
top = max(vals) * 1.25

_FA_DIG = str.maketrans('0123456789.', '۰۱۲۳۴۵۶۷۸۹٫')
def fdig(x):
    return str(x).translate(_FA_DIG)

cats_fa = [
    'مشاهده‌شده\nY',
    'پیش‌بینی مدل\nμ̂',
    'کران بالای محتاطانه\nU',
    'بنچ‌مارک همتایان\nB^G'
]

# Order from Right to Left:
# Rightmost (3): Observed
# Next (2): Forecast
# Next (1): Upper Bound U
# Leftmost (0): Peer Benchmark B^G
x_pos = [3, 2, 1, 0]

fig, ax = plt.subplots(figsize=(COL_IN, 2.5))
bars = ax.bar(x_pos, vals, color=cols, width=0.55, edgecolor='#263238', linewidth=0.7)

for xp, v in zip(x_pos, vals):
    s = fdig(f'{v:.1f}')
    ax.text(xp, v + top * 0.02, s, ha='center', va='bottom', fontsize=9.5, fontweight='bold', family=FA_FONT)

# Arrow between U (x=1) and B^G (x=0)
ax.annotate('', xy=(-0.35, ub), xytext=(-0.35, pb),
            arrowprops=dict(arrowstyle='<->', color='#B71C1C', lw=1.2))
ax.plot([-0.35, 1], [ub, ub], ls=':', lw=1.0, color='#00695C')
ax.plot([-0.35, 0], [pb, pb], ls=':', lw=1.0, color='#B71C1C')

RLM = '\u200F'
lines = [
    f'{RLM}شکاف بالای کران: {fdig(round(gap_abs, 1))}',
    f'{RLM}شکاف نسبی: {fdig(round(rel, 3))}',
    f'{RLM}ضریب اطمینان (Q): {fdig(round(q_val, 2))}',
    f'{RLM}شاخص M-GATO: {fdig(round(mgato_val, 3))}'
]
note = '\n'.join(lines)
ax.text(0.98, 0.95, note, transform=ax.transAxes, ha='right', va='top',
        fontsize=9.0, color='#B71C1C', family=FA_FONT, linespacing=1.4,
        bbox=dict(boxstyle='round,pad=0.4', fc='#FFF8F8', ec='#EF9A9A', lw=0.8))

ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels([cats_fa[3], cats_fa[2], cats_fa[1], cats_fa[0]], fontsize=9.2, fontweight='bold', family=FA_FONT)
ax.set_xlim(-0.6, 3.8)
ax.set_ylim(0, top)
ax.spines[['top', 'right']].set_visible(False)
ax.set_ylabel('تعداد تراکنش دوره آزمون', fontsize=9.5, family=FA_FONT)

ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fdig(f'{v:g}')))
ax.tick_params(axis='both', labelsize=8.5)

plt.savefig('test_fig3_rtl.png', bbox_inches='tight', pad_inches=0.04, dpi=300)
print('saved test_fig3_rtl.png')
