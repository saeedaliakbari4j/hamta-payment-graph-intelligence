import re
import ast
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('create_paper_fa.py', 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)

# Extract all string constants
all_strings = []
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        all_strings.append(node.value)

keywords = ['O(', 'Var', 'Top-K', 'log', '∈', '≈', 'B^G', 'M-GATO', 'η =', 'λ =', 'κ =', 'd_avg', 'd_card', '[x]_+', 'S_covisit', 'S_category']
found = []
for s in all_strings:
    if any(k in s for k in keywords):
        found.append(s)

print(f"Total matching strings: {len(found)}")
for i, s in enumerate(found):
    print(f"\n--- String {i+1} ---")
    print(s[:200] + ("..." if len(s) > 200 else ""))
