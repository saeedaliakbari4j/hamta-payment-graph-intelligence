import re

with open('d:/project/hamta/generate_perfect_figures.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'fc_lab_en = ["Persist", "MA-3", "ETS", "GBDT", "NB-GLM", "Static\\nGNN", "HAMTA"]',
    'fc_lab_en = ["Persist", "MA-3", "GBDT", "Static\\nGNN", "HAMTA"]'
)
c = c.replace(
    'fc_lab_fa = ["ماندگاری", "MA-3", "ETS", "GBDT", "NB-GLM", "GNN\\nایستا", "HAMTA"]',
    'fc_lab_fa = ["ماندگاری", "MA-3", "GBDT", "GNN\\nایستا", "HAMTA"]'
)
c = c.replace(
    'rk_lab_en = ["Lowest\\nvol.", "Pre-\\nvol.", "Tab.\\ngap", "kNN\\ngap", "Static\\nGNN", "SFA", "M-GATO\\nQ=1", "HAMTA"]',
    'rk_lab_en = ["Lowest\\nvol.", "Tab.\\ngap", "Static\\nGNN", "M-GATO\\nQ=1", "HAMTA"]'
)
c = c.replace(
    'rk_lab_fa = ["کمترین\\نحجم", "حجم\\نپیشین", "شکاف\\نجدولی", "شکاف\\nkNN", "GNN\\nایستا", "SFA", "M-GATO\\nQ=1", "HAMTA"]',
    'rk_lab_fa = ["کمترین\\nحجم", "شکاف\\nجدولی", "GNN\\nایستا", "M-GATO\\nQ=1", "HAMTA"]'
)

# Fix for the Persian typo where `\ن` was used incorrectly in my regex matching above:
# Let's just use regex substitute to be safer
c = re.sub(r'fc_lab_fa = \[.*?"HAMTA"\]', 'fc_lab_fa = ["ماندگاری", "MA-3", "GBDT", "GNN\\nایستا", "HAMTA"]', c)
c = re.sub(r'rk_lab_en = \[.*?"HAMTA"\]', 'rk_lab_en = ["Lowest\\nvol.", "Tab.\\ngap", "Static\\nGNN", "M-GATO\\nQ=1", "HAMTA"]', c)
c = re.sub(r'rk_lab_fa = \[.*?"HAMTA"\]', 'rk_lab_fa = ["کمترین\\nحجم", "شکاف\\nجدولی", "GNN\\nایستا", "M-GATO\\nQ=1", "HAMTA"]', c)

with open('d:/project/hamta/generate_perfect_figures.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("Fixed labels")
