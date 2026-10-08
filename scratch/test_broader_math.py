import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Regex with improved func and set patterns
TOKEN_TEST = re.compile(
    r'(?P<cite>\[\d+(?:[,\-]\d+)*\])'
    r'|(?P<bigo>O\([^\)]*\([^\)]*\)[^\)]*\)|O\([^\)]+\))'
    r'|(?P<topk>Top-K\s*\([^\)]+\)|Top-K)'
    r'|(?P<bracket_eq>\[[^\]]+\]_?\+?\s*=\s*[A-Za-z0-9_\(\),\s]+)'
    r'|(?P<set_in>[A-Za-z\u03b1-\u03c9\u0391-\u03a9]\s*∈\s*(?:\[[^\]]+\]|\{[^\}]+\}))'
    r'|(?P<var_eq>Var\([^\)]+\)\s*/\s*E\[[^\]]+\]\s*≈\s*[\d\.]+)'
    r'|(?P<sub>[A-Za-z\u03b1-\u03c9\u0391-\u03a9]_\{[^}]+\})'
    r'|(?P<func>[A-Za-z\u03b1-\u03c9\u0391-\u03a9]+(?:\([A-Za-z0-9_\u03b1-\u03c9\u0391-\u03a9,\s\(\)]+\))+)'
    r'|(?P<lat>[A-Za-z0-9\u03b1-\u03c9\u0391-\u03a9@]'
    r'[A-Za-z0-9_\.\+/\-\u03b1-\u03c9\u0391-\u03a9@:=<>≤≥≈±∈∪∩×·\^\|~\\\'\*\[\]]*'
    r'(?:\s+[A-Za-z0-9_\.\+/\-\u03b1-\u03c9\u0391-\u03a9@:=<>≤≥≈±∈∪∩×·\^\|~\\\'\*\[\]]+)*)'
)

samples = [
    "که d(m) درجه گره، Δ(m, j) تعداد مثلث‌های مشترک",
    "انحنا وزن همتایان را طبق رابطه ( 1 + η · tanh(F(m, j)) ) تعدیل می‌کند",
    "تغییرات همسایگی K ∈ {10, 20, 35, 50} بررسی شد",
    "تغییرات همسایگی K ∈ [3, 10] و η ∈ [0.0, 0.5] است",
    "آستانه‌های تراکنش Y ≥ 5، 10 و 20 اعمال شد",
    "یک هیپ بیشینه همتایان Top-K (K=6) را در مرتبه O(|C(m)| log K) با پیچیدگی کاندیدایابی محدود به O(|M| · K · d_avg) استخراج می‌نماید.",
    "که در آن [x]_+ = max(0, x)، O_{m, t} مجموع کارت‌های مشترک",
    "داده‌های تراکنشی بیش‌پراکندگی شدید نشان می‌دهند (Var(Y)/E[Y] ≈ 3.24) که استفاده",
    "در زمان O(|C_m| · d_card) استخراج می‌شود",
    "پرهیز از مقایسه‌های متراکم و پرهزینه O(|M|^2) است",
    "همتایان Top-K و مقادیر Precision@K و Recall@K و NDCG@10",
    "شکاف کران-پیش‌بینی همتایان (Forecast-Bound Peer Gap معادل B^G - U) است، نه B^G - Y",
    "ضریب λ = 0.65 و η = 0.25 و κ = 18 است"
]

def tokenize(text):
    pos = 0
    tokens = []
    for m in TOKEN_TEST.finditer(text):
        s, e = m.span()
        if m.group('lat'):
            while text[s:e] and text[e - 1] in ".-:,،؛)(":
                e -= 1
        if s > pos:
            tokens.append(('fa', text[pos:s]))
        tokens.append(('lat', text[s:e], m.lastgroup))
        pos = e
    if pos < len(text):
        tokens.append(('fa', text[pos:]))
    return tokens

for i, s in enumerate(samples):
    print(f"\n--- Sample {i+1} ---")
    print(f"Original: {s}")
    tks = tokenize(s)
    for t in tks:
        if t[0] == 'lat':
            print(f"   [{t[2]}]: '{t[1]}'")
        else:
            # show persian snippet
            p = t[1].strip()
            if p:
                print(f"   [FA]: '{p}'")
