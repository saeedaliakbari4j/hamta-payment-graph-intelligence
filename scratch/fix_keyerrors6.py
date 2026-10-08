import re

with open('d:/project/hamta/create_paper_fa.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('row["Prec_disp"]', 'row.get("Prec_disp", str(row.get("Precision@35", 0.0)))')

with open('d:/project/hamta/create_paper_fa.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("Fix applied successfully")
