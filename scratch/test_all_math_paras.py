import re
import ast
import sys

sys.stdout.reconfigure(encoding='utf-8')

TOKEN_PROPOSED = re.compile(
    r'(?P<cite>\[\d+(?:[,\-\s]\d+)*\])'
    r'|(?P<bigo>O\((?:[^()]|\((?:[^()]|\([^()]*\))*\))*\))'
    r'|(?P<bracket_eq>\[[^\]]+\]_?\+?\s*=\s*[A-Za-z0-9_\u0300-\u036f\(\),\s]+)'
    r'|(?P<topk>Top-K(?:\s*\([^\)]+\))?)'
    r'|(?P<set_in>[A-Za-z\u03b1-\u03c9\u0391-\u03a9]\s*∈\s*(?:\[[^\]]+\]|\{[^\}]+\}))'
    r'|(?P<var_eq>Var\([^\)]+\)\s*/\s*E\[[^\]]+\]\s*≈\s*[\d\.]+)'
    r'|(?P<sub>[A-Za-z\u03b1-\u03c9\u0391-\u03a9\u0300-\u036f]_\{[^}]+\})'
    r'|(?P<func>[A-Za-z\u03b1-\u03c9\u0391-\u03a9\u0300-\u036fΔ]+(?:\([A-Za-z0-9_\u03b1-\u03c9\u0391-\u03a9\u0300-\u036f,\s\(\)]+\))+)'
    r'|(?P<lat>[A-Za-z0-9\u03b1-\u03c9\u0391-\u03a9\u0300-\u036f@Δ]'
    r'[A-Za-z0-9_\.\+/\-\u03b1-\u03c9\u0391-\u03a9\u0300-\u036f@:=<>≤≥≈±∈∪∩×·\^\|~\\\'\*\[\]Δ]*'
    r'(?:\s+[A-Za-z0-9_\.\+/\-\u03b1-\u03c9\u0391-\u03a9\u0300-\u036f@:=<>≤≥≈±∈∪∩×·\^\|~\\\'\*\[\]Δ]+)*)'
)

# Read all strings from create_paper_fa.py
with open('create_paper_fa.py', 'r', encoding='utf-8') as f:
    code = f.read()

tree = ast.parse(code)
strings = []
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        strings.append(node.value)

def tokenize(text):
    pos = 0
    runs = []
    for m in TOKEN_PROPOSED.finditer(text):
        s, e = m.span()
        if m.group('lat'):
            while text[s:e] and text[e - 1] in ".-:,،؛)(":
                e -= 1
        if s > pos:
            runs.append(('fa', text[pos:s]))
        grp = m.lastgroup
        matched = text[s:e]
        runs.append(('lat', matched, grp))
        pos = e
    if pos < len(text):
        runs.append(('fa', text[pos:]))
    return runs

# Find paragraphs that contain math
math_paras = []
for s in strings:
    if any(k in s for k in ['O(', 'Top-K', 'log K', 'd_avg', 'd_card', '[x]_+', 'Var(Y)', 'λ =', 'η =', 'κ =', 'Δ(m', 'd(m)', 'I(c)', 'μ̂']):
        math_paras.append(s)

print(f"Total math strings to test: {len(math_paras)}\n")
for idx, p in enumerate(math_paras):
    print(f"================ Paragraph {idx+1} ================")
    runs = tokenize(p)
    for r in runs:
        if r[0] == 'lat':
            print(f"  [LAT/{r[2]}]: '{r[1]}'")
        else:
            txt = r[1].strip()
            if txt:
                print(f"  [FA]: '{txt[:40]}...'")
