import re

def fix(path, is_fa=False):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    c = c.replace('row["Delta_NDCG"]', 'row.get("Delta_NDCG", row.get("Delta NDCG", 0.0))')
    
    if is_fa:
        c = c.replace('row["Precision_disp"]', 'row.get("Precision_disp", str(row.get("Precision@35", 0.0)))')
        c = c.replace('row["NDCG_disp"]', 'row.get("NDCG_disp", str(row.get("NDCG@35", 0.0)))')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

fix('d:/project/hamta/create_paper.py', False)
fix('d:/project/hamta/create_paper_fa.py', True)
print("Fixes applied successfully")
