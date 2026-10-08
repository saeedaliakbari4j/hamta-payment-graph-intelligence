import sys, docx

sys.stdout.reconfigure(encoding='utf-8')
doc = docx.Document('FA_From_Transactional_Data_to_Organizational_Intelligence.docx')

print('=== SCANNING INLINE MATH RUNS ===')
math_terms = ['η =', 'λ =', 'K =', 'p =', 'α =', 'κ =', 'TP =', 'Q =', 'Coverage =', 'Y ≥']
found = 0
for i, p in enumerate(doc.paragraphs):
    for r in p.runs:
        for term in math_terms:
            if term in r.text:
                found += 1
                has_lrm = r.text.startswith('\u200E') and r.text.endswith('\u200E')
                print(f'P{i:02d} [{term}]: run_text="{r.text}" | has_lrm={has_lrm} | font={r.font.name}')

print(f'Total verified math runs: {found}')
