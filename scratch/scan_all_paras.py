import re
import ast
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('create_paper_fa.py', 'r', encoding='utf-8') as f:
    code = f.read()

tree = ast.parse(code)

TOKEN_PROPOSED = re.compile(
    r'(?P<cite>\[\d+(?:[,\-\s]\d+)*\])'
    r'|(?P<bigo>O\((?:[^()]|\((?:[^()]|\([^()]*\))*\))*\))'
    r'|(?P<bracket_eq>\[[^\]]+\]_?\+?\s*=\s*[A-Za-z0-9_\u0300-\u036f\(\),\s]+)'
    r'|(?P<topk>Top-K(?:\s*\([^\)]+\))?)'
    r'|(?P<set_in>[A-Za-z\u03b1-\u03c9\u0391-\u03a9]\s*∈\s*(?:\[[^\]]+\]|\{[^\}]+\}))'
    r'|(?P<var_eq>(?:\()?Var\([^\)]+\)\s*/\s*E\[[^\]]+\]\s*≈\s*[\d\.]+(?:\))?)'
    r'|(?P<sub>[A-Za-z\u03b1-\u03c9\u0391-\u03a9\u0300-\u036f]_\{[^}]+\})'
    r'|(?P<func>[A-Za-z\u03b1-\u03c9\u0391-\u03a9\u0300-\u036fΔ]+(?:\([A-Za-z0-9_\u03b1-\u03c9\u0391-\u03a9\u0300-\u036f,\s\(\)]+\))+)'
    r'|(?P<lat>[A-Za-z0-9\u03b1-\u03c9\u0391-\u03a9\u0300-\u036f@Δ]'
    r'[A-Za-z0-9_\.\+/\-\u03b1-\u03c9\u0391-\u03a9\u0300-\u036f@:=<>≤≥≈±∈∪∩×·\^\|~\\\'\*\[\]Δ]*'
    r'(?:\s+[A-Za-z0-9_\.\+/\-\u03b1-\u03c9\u0391-\u03a9\u0300-\u036f@:=<>≤≥≈±∈∪∩×·\^\|~\\\'\*\[\]Δ]+)*)'
)

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

# Find all B.para calls
para_calls = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func = getattr(node.func, 'attr', '')
        if func == 'para' and len(node.args) >= 2:
            arg = node.args[1]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                para_calls.append(arg.value)
            elif isinstance(arg, ast.JoinedStr):
                # reconstruct f-string approximately
                parts = []
                for v in arg.values:
                    if isinstance(v, ast.Constant):
                        parts.append(str(v.value))
                    else:
                        parts.append("X")
                para_calls.append("".join(parts))

print(f"Total B.para calls: {len(para_calls)}")

# Check every para for any remaining issues:
# e.g., if there are dangling parentheses or pipes in 'fa' runs next to 'lat' runs
suspects = []
for idx, p in enumerate(para_calls):
    tks = tokenize(p)
    for ti in range(len(tks) - 1):
        t1, t2 = tks[ti], tks[ti+1]
        # Check if a fa run ends with '(' and next is lat, and next fa starts with ')'
        if t1[0] == 'fa' and t1[1].rstrip().endswith('(') and t2[0] == 'lat':
            if ti + 2 < len(tks) and tks[ti+2][0] == 'fa' and tks[ti+2][1].lstrip().startswith(')'):
                suspects.append((idx, f"Lat in parens: '({t2[1]})' in: {p[:60]}..."))
        # Check if any fa run contains | or math operators
        if t1[0] == 'fa' and any(c in t1[1] for c in ['|', '√', '≈', '≤', '≥', '±']):
            suspects.append((idx, f"Math in FA run: '{t1[1]}' in: {p[:60]}..."))

print(f"Suspects found: {len(suspects)}")
for s in suspects:
    print(s)
