import re

def fix():
    with open('d:/project/hamta/generate_perfect_figures.py', 'r', encoding='utf-8') as f:
        c = f.read()

    # Import statements
    c = c.replace('import networkx as nx', 'import networkx as nx\nimport arabic_reshaper\nfrom bidi.algorithm import get_display')
    
    # Helper for Persian text
    c = c.replace('def fdig(x) -> str:', 'def fa_text(text):\n    return get_display(arabic_reshaper.reshape(str(text)))\n\ndef fdig(x) -> str:')
    
    # Wrap Persian strings with fa_text()
    # For fa_ticks:
    c = c.replace('f = FuncFormatter(lambda v, _: fdig(fmt.format(v)))', 'f = FuncFormatter(lambda v, _: fa_text(fdig(fmt.format(v))))')
    
    # For Fig 1 Persian
    c = c.replace('ax.text(0.5, y + h * 0.66, t', 'ax.text(0.5, y + h * 0.66, fa_text(t)')
    c = c.replace('ax.text(0.5, y + h * 0.28, s', 'ax.text(0.5, y + h * 0.28, fa_text(s)')
    
    # For Fig 1 styling (Simple)
    c = c.replace('colors = [("#E3F2FD", "#1565C0"), ("#E8F5E9", "#2E7D32"), ("#FFF3E0", "#E65100"), ("#F3E5F5", "#6A1B9A")]',
                  'colors = [("#FFFFFF", "#000000"), ("#FFFFFF", "#000000"), ("#FFFFFF", "#000000"), ("#FFFFFF", "#000000")]')
    c = c.replace('linewidth=1.1', 'linewidth=1.0')
    c = c.replace('boxstyle="round,pad=0.008,rounding_size=0.03"', 'boxstyle="square,pad=0.02"')
    c = c.replace('boxstyle="round,pad=0.006,rounding_size=0.03"', 'boxstyle="square,pad=0.02"')
    
    # For Fig 2 labels
    c = c.replace('lab = GUILD_EN.get(key, key) if lang == "en" else GUILD_FA.get(key, key)',
                  'lab = GUILD_EN.get(key, key) if lang == "en" else fa_text(GUILD_FA.get(key, key))')
    c = c.replace('inj_lab = "Injected target" if lang == "en" else "هدف تزریق‌شده"',
                  'inj_lab = "Injected target" if lang == "en" else fa_text("هدف تزریق‌شده")')
                  
    # For Fig 3
    c = c.replace('ax.set_xticklabels(cats,', 'ax.set_xticklabels([fa_text(c) if lang=="fa" else c for c in cats],')
    c = c.replace('ax.text(b.get_x() + b.get_width() / 2, v + top * 0.018, s', 'ax.text(b.get_x() + b.get_width() / 2, v + top * 0.018, fa_text(s) if lang=="fa" else s')
    c = c.replace('ax.text(0.03, 0.96, note', 'ax.text(0.03, 0.96, fa_text(note) if lang=="fa" else note')
    c = c.replace('ax.set_ylabel("تعداد تراکنش دوره آزمون"', 'ax.set_ylabel(fa_text("تعداد تراکنش دوره آزمون")')
    
    # For Fig 4
    c = c.replace('label=le if lang == "en" else lf', 'label=le if lang == "en" else fa_text(lf)')
    c = c.replace('ax.set_xticklabels([f"K = {fdig(k)}" for k in ks]', 'ax.set_xticklabels([fa_text(f"K = {fdig(k)}") for k in ks]')
    c = c.replace('ax.set_ylabel("Precision@K (۱۰ سید)"', 'ax.set_ylabel(fa_text("Precision@K (۱۰ سید)")')
    c = c.replace('fa_text(f"تصادفی = {fdig(\'0.149\')}")', 'fa_text(f"تصادفی = {fdig(\'0.149\')}")') # we will do it differently
    c = c.replace('f"تصادفی = {fdig(\'0.149\')}"', 'fa_text(f"تصادفی = {fdig(\'0.149\')}")')
    
    # For Fig 5
    c = c.replace('a1.set_xticklabels(fc_lab_en if lang == "en" else fc_lab_fa', 'a1.set_xticklabels(fc_lab_en if lang == "en" else [fa_text(x) for x in fc_lab_fa]')
    c = c.replace('a2.set_xticklabels(rk_lab_en if lang == "en" else rk_lab_fa', 'a2.set_xticklabels(rk_lab_en if lang == "en" else [fa_text(x) for x in rk_lab_fa]')
    c = c.replace('a1.set_title("(الف) خطای پیش‌بینی MAE (کمتر بهتر است)"', 'a1.set_title(fa_text("(الف) خطای پیش‌بینی MAE (کمتر بهتر است)")')
    c = c.replace('a2.set_title("(ب) کیفیت رتبه‌بندی فرصت NDCG@35 (بیشتر بهتر است)"', 'a2.set_title(fa_text("(ب) کیفیت رتبه‌بندی فرصت NDCG@35 (بیشتر بهتر است)")')

    with open('d:/project/hamta/generate_perfect_figures.py', 'w', encoding='utf-8') as f:
        f.write(c)

fix()
print("generate_perfect_figures.py fixed")
