with open('d:/project/hamta/generate_perfect_figures.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if 'fc_lab_en =' in line and '["Persist"' in line:
        skip = True
        new_lines.append('    fc_lab_en = ["Persist", "MA-3", "GBDT", "Static\\nGNN", "HAMTA"]\n')
        new_lines.append('    fc_lab_fa = ["ماندگاری", "MA-3", "GBDT", "GNN\\nایستا", "HAMTA"]\n')
        new_lines.append('    mae = [mean_std(v) for v in fc.get("MAE")]\n')
        new_lines.append('    rk_lab_en = ["Lowest\\nvol.", "Tab.\\ngap", "Static\\nGNN", "M-GATO\\nQ=1", "HAMTA"]\n')
        new_lines.append('    rk_lab_fa = ["کمترین\\nحجم", "شکاف\\nجدولی", "GNN\\nایستا", "M-GATO\\nQ=1", "HAMTA"]\n')
    elif 'nd =' in line:
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

with open('d:/project/hamta/generate_perfect_figures.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed")
