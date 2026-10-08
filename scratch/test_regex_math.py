import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

TOKEN_NEW = re.compile(
    r'(?P<cite>\[\d+(?:[,\-]\d+)*\])'
    r'|(?P<bigo>O\([^\)]*\([^\)]*\)[^\)]*\)|O\([^\)]+\))'
    r'|(?P<topk>Top-K\s*\([^\)]+\)|Top-K)'
    r'|(?P<bracket_eq>\[[^\]]+\]_?\+?\s*=\s*[A-Za-z0-9_\(\),\s]+)'
    r'|(?P<interval>[A-Za-z\u03b1-\u03c9\u0391-\u03a9]\s*∈\s*\[[^\]]+\])'
    r'|(?P<var_eq>Var\([^\)]+\)\s*/\s*E\[[^\]]+\]\s*≈\s*[\d\.]+)'
    r'|(?P<sub>[A-Za-z\u03b1-\u03c9\u0391-\u03a9]_\{[^}]+\})'
    r'|(?P<func>[A-Za-z\u03b1-\u03c9\u0391-\u03a9]\([A-Za-z0-9_\u03b1-\u03c9\u0391-\u03a9]+\))'
    r'|(?P<lat>[A-Za-z0-9\u03b1-\u03c9\u0391-\u03a9@]'
    r'[A-Za-z0-9_\.\+/\-\u03b1-\u03c9\u0391-\u03a9@:=<>≤≥≈±∈∪∩×·\^\|~\\\'\*\[\]]*'
    r'(?:\s+[A-Za-z0-9_\.\+/\-\u03b1-\u03c9\u0391-\u03a9@:=<>≤≥≈±∈∪∩×·\^\|~\\\'\*\[\]]+)*)'
)

test_strings = [
    "یک هیپ بیشینه همتایان Top-K (K=6) را در مرتبه O(|C(m)| log K) با پیچیدگی کاندیدایابی محدود به O(|M| · K · d_avg) استخراج می‌نماید.",
    "به منظور پرهیز از مقایسه‌های متراکم و پرهزینه O(|M|^2)، چارچوب HAMTA از ایندکس معکوس کارت به پذیرنده جهت تولید کاندیداها استفاده می‌نماید.",
    "نمایه معکوس I(c) تمامی پذیرندگان مشاهده‌شده توسط کارت c در پنجره‌های گذشته را بازمی‌یابد و برای هر پذیرنده m، همسایگی ۲-گامه در زمان O(|C_m| · d_card) استخراج می‌شود:",
    "که در آن S_covisit شباهت کسینوسی بردار دودویی وقوع مشتریان مشترک و S_category تطابق صنف تجاری است. ضریب λ = 0.65 در پنجره اعتبارسنجی گذشته تنظیم شده است.",
    "با ضریب مقیاس η = 0.25 به عنوان تنظیم‌کننده ساختاری و پالایش‌گر روابط همتایان عمل می‌نماید.",
    "داده‌های تراکنشی بیش‌پراکندگی شدید نشان می‌دهند (Var(Y)/E[Y] ≈ 3.24) که استفاده از توزیع دوجمله‌ای منفی را نسبت به مدل پواسون توجیه می‌کند.",
    "که در آن [x]_+ = max(0, x)، O_{m, t} مجموع کارت‌های مشترک با همتایان Top-K و κ = 18 پارامتر اشباع شواهد است. M-GATO بیانگر شکاف کران-پیش‌بینی همتایان (Forecast-Bound Peer Gap معادل B^G - U) است، نه صرفاً افت لحظه‌ای مشاهده‌شده کنونی (B^G - Y).",
    "تغییرات همسایگی K ∈ [3, 10]، وزن انحنا η ∈ [0.0, 0.5] و پارامتر اشباع κ ∈ [10, 30] پایداری مناسبی دارد.",
    "کاندیدایابی با اندیس معکوس کارت‌ها پیچیدگی را به O(|M| · K · d_avg) محدود نموده و مقیاس‌پذیری عملیاتی روش را تأیید می‌کند."
]

def tokenize(text):
    pos = 0
    tokens = []
    for m in TOKEN_NEW.finditer(text):
        s, e = m.span()
        # If lat group, trim trailing Persian punctuation
        if m.group('lat'):
            while text[s:e] and text[e - 1] in ".-:,،؛)(":
                e -= 1
        if s > pos:
            tokens.append(('fa', text[pos:s]))
        matched_group = m.lastgroup
        tokens.append(('lat', text[s:e], matched_group))
        pos = e
    if pos < len(text):
        tokens.append(('fa', text[pos:]))
    return tokens

for i, ts in enumerate(test_strings):
    print(f"\n=== Test {i+1} ===")
    tokens = tokenize(ts)
    for t in tokens:
        if t[0] == 'lat':
            print(f"  [LAT/{t[2]}]: '{t[1]}'")
