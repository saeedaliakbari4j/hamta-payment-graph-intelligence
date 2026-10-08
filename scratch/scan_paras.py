import sys, re

sys.stdout.reconfigure(encoding='utf-8')

TOKEN = re.compile(
    r'(?P<sub>[A-Za-z\u03b1-\u03c9\u0391-\u03a9]_\{[^}]+\})'
    r'|(?P<cite>\[\d+(?:[,\-]\d+)*\])'
    r'|(?P<lat>[A-Za-z0-9\u03b1-\u03c9\u0391-\u03a9@]'
    r'[A-Za-z0-9_\.\+/\-\u03b1-\u03c9\u0391-\u03a9@:=<>≤≥≈±∈∪∩×·\^\[\]\(\)\{\}\|%,~\\\'\*]*'
    r'(?:\s+[A-Za-z0-9_\.\+/\-\u03b1-\u03c9\u0391-\u03a9@:=<>≤≥≈±∈∪∩×·\^\[\]\(\)\{\}\|%,~\\\'\*]+)*)'
)

with open('create_paper_fa.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== SCANNING ALL LINES FOR LATIN/MATH TOKENS ===')
for line_no, line in enumerate(lines, 1):
    # Only check lines with Persian characters
    if any(c in line for c in 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'):
        # Check if line contains math/Latin terms with parentheses, big-O, or operators
        if any(term in line for term in ['O(', 'Top-K', '∈', '≤', '≥', 'Var(', 'Precision@', 'NDCG@', 'log', 'p =', 'K =', 'η =', 'λ =', 'α =', 'κ =', '|M|', '|C']):
            print(f"\nLine {line_no}:")
            # tokenize line as add_text would
            # extract string literal
            # Find tokens
            clean_line = line.strip()
            print("  Raw:", clean_line[:90])
            for m in TOKEN.finditer(clean_line):
                txt = m.group()
                if any(k in txt for k in ['O(', 'Top-K', '∈', '≤', '≥', 'Var(', 'log', '=', '|']):
                    print(f"    Token matched: '{txt}'")
