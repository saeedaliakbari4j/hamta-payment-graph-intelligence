import re

def fix(path, is_fa=False):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    c = c.replace('row["Weak-Support %"]', 'row.get("Weak-Support %", row.get("FPR@35", 0))')
    
    if is_fa:
        c = c.replace('row["MAE_disp"]', 'row.get("MAE_disp", str(row.get("MAE", 0)))')
        c = c.replace('row["RMSE_disp"]', 'row.get("RMSE_disp", str(row.get("RMSE", 0)))')
        c = c.replace('row["sMAPE_disp"]', 'row.get("sMAPE_disp", str(row.get("sMAPE", 0)))')
        c = c.replace('row["NBNLL_disp"]', 'row.get("NBNLL_disp", str(row.get("NB_NLL", 0)))')
        c = c.replace('row["NDCG_disp"]', 'row.get("NDCG_disp", str(row.get("NDCG@35", 0)))')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

fix('create_paper.py', False)
fix('create_paper_fa.py', True)
