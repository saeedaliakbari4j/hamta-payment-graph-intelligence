import re

def fix(path):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Fix quote syntax error
    c = c.replace('"Representation Learning on Large Non-Bipartite Transaction Networks using GraphSAGE,"', "'Representation Learning on Large Non-Bipartite Transaction Networks using GraphSAGE,'")
    c = c.replace('"Non-exchangeable Conformal Prediction for Temporal Graph Neural Networks,"', "'Non-exchangeable Conformal Prediction for Temporal Graph Neural Networks,'")
    c = c.replace('"A survey of dynamic graph neural networks,"', "'A survey of dynamic graph neural networks,'")

    # Fix unclosed parenthesis/quotes in fa version where I inserted the EA text
    # The text was inserted before "کلمات کلیدی"
    # "کلمات کلیدی" was previously inside a string. I must ensure the string matches.
    c = c.replace('سازمانی متصل می‌شود.\\n\\nکلمات کلیدی', 'سازمانی متصل می‌شود.")\n\n    B.para("Heading 0", "کلمات کلیدی')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

fix('d:/project/hamta/create_paper.py')
fix('d:/project/hamta/create_paper_fa.py')
