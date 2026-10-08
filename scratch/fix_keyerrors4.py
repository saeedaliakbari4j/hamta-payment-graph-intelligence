import re

def fix(path, is_fa=False):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # English fixes
    c = c.replace("row['Delta_NDCG']", "row.get('Delta_NDCG', row.get('Delta NDCG', 0.0))")
    c = c.replace('row["Delta_NDCG"]', 'row.get("Delta_NDCG", row.get("Delta NDCG", 0.0))')
    
    # Persian fixes
    if is_fa:
        c = c.replace('row["Recall_disp"]', 'row.get("Recall_disp", str(row.get("Recall@35", 0.0)))')
        c = c.replace('row["MAP_disp"]', 'row.get("MAP_disp", str(row.get("MAP@35", 0.0)))')
        c = c.replace('row["FPR_disp"]', 'row.get("FPR_disp", str(row.get("FPR@35", 0.0)))')
        c = c.replace('row["RPrec_disp"]', 'row.get("RPrec_disp", str(row.get("R-Prec", 0.0)))')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

fix('d:/project/hamta/create_paper.py', False)
fix('d:/project/hamta/create_paper_fa.py', True)
print("Fixes applied successfully")
