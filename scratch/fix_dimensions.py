import re

with open('d:/project/hamta/generate_perfect_figures.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Make the figure sizes wider to prevent overlapping
c = c.replace('COL_IN = 3.25', 'COL_IN = 6.5')

# Increase font sizes slightly since we doubled the width
c = re.sub(r'fontsize=6\.2', 'fontsize=8.5', c)
c = re.sub(r'fontsize=5\.6', 'fontsize=7.5', c)
c = re.sub(r'fontsize=6\.6', 'fontsize=9.0', c)
c = re.sub(r'fontsize=7\.2', 'fontsize=10.0', c)
c = re.sub(r'fontsize=6\.8', 'fontsize=9.5', c)
c = re.sub(r'fontsize=7\.6', 'fontsize=10.5', c)
c = re.sub(r'fontsize=7\.0', 'fontsize=9.5', c)

# Adjust w and gap in make_fig1 to ensure it fits perfectly within 1.0
c = c.replace('w, gap = 0.225, 0.035', 'w, gap = 0.22, 0.04')

with open('d:/project/hamta/generate_perfect_figures.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("Fixed dimensions and fonts")
