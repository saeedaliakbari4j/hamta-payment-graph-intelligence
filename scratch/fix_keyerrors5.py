import re

def fix(path, is_fa=False):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # English fixes
    c = c.replace('row["Significance"]', 'row.get("Significance", row.get("Significance (Wilcoxon/t)", ""))')
    
    # Persian fixes
    if is_fa:
        c = c.replace("row['Drop Rate']", "row.get('Drop Rate', row.get('Drop', 0.0))")
        c = c.replace('row["Coverage (%)"]', 'row.get("Coverage (%)", row.get("Coverage", 0.0))')
        c = c.replace('row["Significance"]', 'row.get("Significance", row.get("Significance (Wilcoxon/t)", ""))')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

fix('d:/project/hamta/create_paper.py', False)
fix('d:/project/hamta/create_paper_fa.py', True)
print("Fixes applied successfully")
