import re

with open('d:/project/hamta/generate_perfect_figures.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('fc.get("MAE_disp", fc.get("MAE"))', 'fc.get("MAE")')
c = c.replace('rk.get("NDCG_disp", rk.get("NDCG@35"))', 'rk.get("NDCG@K")')

with open('d:/project/hamta/generate_perfect_figures.py', 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed generate_perfect_figures.py")
