import re

def fix(path, is_fa=False):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Create Paper EN
    if not is_fa:
        c = c.replace('row["Coverage (%)"]', 'row.get("Coverage (%)", row.get("Coverage", 0.0))')
    
    # Create Paper FA
    if is_fa:
        c = c.replace('row["NLL_disp"]', 'row.get("NLL_disp", row.get("NB_NLL", 0.0))')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

fix('d:/project/hamta/create_paper.py', False)
fix('d:/project/hamta/create_paper_fa.py', True)
print("Fixes applied successfully")
