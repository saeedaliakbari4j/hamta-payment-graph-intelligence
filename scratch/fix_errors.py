import re

# Fix 1: KeyError R_Precision in create_paper.py
with open('d:/project/hamta/create_paper.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace("rprec_s = str(row[\"RPrec_disp\"]).replace(\" \", \"\\u00A0\") if \"RPrec_disp\" in row else f\"{row['R_Precision']:.3f}\"", 
              "rprec_s = str(row[\"RPrec_disp\"]).replace(\" \", \"\\u00A0\") if \"RPrec_disp\" in row else f\"{row.get('R-Prec', row.get('R_Precision', 0)):.3f}\"")
c = c.replace("rprec_s = str(row[\"RPrec_disp\"]).replace(\" \", \"\\u00A0\") if \"RPrec_disp\" in row else f\"{row['R-Prec']:.3f}\"", 
              "rprec_s = str(row[\"RPrec_disp\"]).replace(\" \", \"\\u00A0\") if \"RPrec_disp\" in row else f\"{row.get('R-Prec', row.get('R_Precision', 0)):.3f}\"")

with open('d:/project/hamta/create_paper.py', 'w', encoding='utf-8') as f:
    f.write(c)

# Fix 2: Syntax error in create_paper_fa.py
with open('d:/project/hamta/create_paper_fa.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'سازمانی متصل می‌شود' in line and 'کلمات کلیدی' not in line and not line.strip().endswith(')'):
        lines[i] = line.rstrip() + '")\n'
    if 'B.para("Heading 0", "کلمات کلیدی' in line and not line.strip().endswith(')'):
        lines[i] = line.rstrip() + '")\n'

with open('d:/project/hamta/create_paper_fa.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
