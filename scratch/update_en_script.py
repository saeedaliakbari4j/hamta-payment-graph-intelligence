def update_create_paper_en():
    with open('create_paper.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Abstract lift
    content = content.replace(
        "achieving a 2.51-fold improvement over random expectation",
        "achieving a 2.46-fold improvement over portfolio random expectation (and 2.10-fold over candidate pool baseline)"
    )

    # 2. Section 4 ground truth
    old_s4 = (
        'Exactly 51 out of 350 merchants (~14.6%) across all 8 business categories are selected via stratified random sampling from candidates with active peer baselines. Target-peer overlap is low: on average only 11.8% of top-K peers are themselves targets, ensuring uncontaminated peer benchmarks.'
    )
    new_s4 = (
        'Exactly 52 out of 350 merchants (~14.9%) across all 8 business categories are selected via stratified random sampling from candidates with active peer baselines (average candidate pool 299 merchants across 10 seeds, yielding 17.4% in-pool random expectation). Target-peer overlap is low: on average only 11.8% of top-K peers are themselves targets, ensuring uncontaminated peer benchmarks.'
    )
    content = content.replace(old_s4, new_s4)

    # 3. Section 5.2 Ranking text
    old_s52 = (
        'Under synthetic opportunity prevalence of 51/350 (random expectation = 0.146, 14.6%), Table II confirms that HAMTA achieves Precision@35 = 0.366 ± 0.120, '
        'Recall@35 = 0.246 ± 0.081, R-Precision = 0.342 ± 0.077, NDCG@35 = 0.382 ± 0.116, and MAP@35 = 0.180 ± 0.088. '
        'This represents a 2.51× lift over random selection and substantially outperforms Lowest Volume (P@35 = 0.197 ± 0.053) and Pre-Campaign Volume (P@35 = 0.220 ± 0.054). '
        'Recall@35 reaches 0.246 ± 0.081, noting that maximum possible Recall@35 under 35 slots for 51 targets is bounded by 35/51 = 0.686.'
    )
    new_s52 = (
        'Under synthetic opportunity prevalence of 52/350 (portfolio random expectation = 0.1486, ~14.9%; candidate pool random expectation = 52/299 = 0.174, 17.4%), Table II confirms that HAMTA achieves Precision@35 = 0.366 ± 0.120, '
        'Recall@35 = 0.246 ± 0.081, R-Precision = 0.342 ± 0.077, NDCG@35 = 0.382 ± 0.116, and MAP@35 = 0.180 ± 0.088. '
        'This represents a 2.46× lift over portfolio random selection (and 2.10× lift over the candidate pool baseline) and substantially outperforms Lowest Volume (P@35 = 0.197 ± 0.053) and Pre-Campaign Volume (P@35 = 0.220 ± 0.054). '
        'Recall@35 reaches 0.246 ± 0.081, noting that maximum possible Recall@35 under 35 slots for 52 targets is bounded by 35/52 = 0.673 (67.3%).'
    )
    content = content.replace(old_s52, new_s52)

    # 4. Multi-Budget Holm-Bonferroni text
    old_mb = (
        'Under Holm-Bonferroni adjustment across evaluated baselines, HAMTA maintains statistically significant superiority (p_adj < 0.05) over conventional baselines: '
        'at K = 10 against Lowest Volume (p = 0.015) and Tabular GBDT (p = 0.039); at K = 20 against Lowest Volume (p = 0.005) and Tabular GBDT (p = 0.005); '
        'and at K = 35 against Static GNN (p = 0.0488).'
    )
    new_mb = (
        'Under Holm-Bonferroni adjustment across evaluated baselines, HAMTA maintains statistically significant superiority (p_adj < 0.05) over conventional baselines: '
        'at K = 10 against Lowest Volume (p_adj = 0.0156) and Tabular GBDT (p_adj = 0.0293); at K = 20 against Lowest Volume (p_adj = 0.0156) and Tabular GBDT (p_adj = 0.0176); '
        'and at K = 35 against Lowest Volume (p_adj = 0.0176) and Tabular GBDT (p_adj = 0.0078). Against Static GNN at K = 35, the raw paired Wilcoxon test is significant (p = 0.0488), '
        'adjusting to p_adj = 0.0977 under Holm-Bonferroni. Differences between HAMTA and SFA across budgets do not reach statistical significance, establishing SFA as a competitive non-parametric frontier benchmark.'
    )
    content = content.replace(old_mb, new_mb)

    # 5. Equation 4 formatting to prevent column overflow
    old_eq4 = 'add_equation("L_NB = -∑_m [ ln Γ(Y_m + φ) - ln Γ(φ) - ln Γ(Y_m + 1) + φ ln(φ / (φ + μ̂_m)) + Y_m ln(μ̂_m / (φ + μ̂_m)) ]", 4)'
    new_eq4 = 'add_equation("L_NB = - ∑_m [ ln Γ(Y_m + φ) - ln Γ(φ) - ln Γ(Y_m + 1)\\n              + φ ln(φ / (φ + μ̂_m)) + Y_m ln(μ̂_m / (φ + μ̂_m)) ]", 4, font_size=6.8)'
    content = content.replace(old_eq4, new_eq4)

    # Equation 8 font size
    old_eq8 = 'add_equation("M-GATO_{m, t} = Q_{m, t} · [ (B^G_{m, t+1} - U_{m, t+1}) / (B^G_{m, t+1} + ε) ]_+", 8)'
    new_eq8 = 'add_equation("M-GATO_{m, t} = Q_{m, t} · [ (B^G_{m, t+1} - U_{m, t+1}) / (B^G_{m, t+1} + ε) ]_+", 8, font_size=7.0)'
    content = content.replace(old_eq8, new_eq8)

    # add_equation definition font_size parameter
    old_def_eq = 'def add_equation(eq_text, eq_num):'
    new_def_eq = 'def add_equation(eq_text, eq_num, font_size=7.5):'
    content = content.replace(old_def_eq, new_def_eq)
    content = content.replace('r0.font.size = Pt(7.8)', 'r0.font.size = Pt(font_size)')

    # 6. References [9], [15], [19], [23]
    old_r9 = '[9] Z. Liu, C. Chen, X. Yang, J. Zhou, X. Li, and L. Song, "Graph representation learning for merchant incentive optimization in mobile payment marketing," in Proc. 28th ACM Int. Conf. Inf. Knowl. Manage. (CIKM), 2019, pp. 2577–2584.'
    new_r9 = '[9] Z. Liu, D. Wang, Q. Yu, Z. Zhang, Y. Shen, J. Ma, W. Zhong, J. Gu, J. Zhou, S. Yang, and Y. Qi, "Graph representation learning for merchant incentive optimization in mobile payment marketing," in Proc. 28th ACM Int. Conf. Inf. Knowl. Manage. (CIKM), 2019, pp. 2577–2584.'
    content = content.replace(old_r9, new_r9)

    old_r15 = '[15] M. Tare, C. Rattasits, Y. Wu, and E. Wielewski, "Harnessing GraphSAGE for Learning Representations of Massive Transactional Networks," in Proc. IAPR Workshop Graph-Based Representations in Pattern Recognition (GbRPR), Springer, 2025, pp. 179–188.'
    new_r15 = '[15] M. Tare, C. Rattasits, Y. Wu, and E. Wielewski, "Harnessing GraphSAGE for learning representations of massive transactional networks," in Graph-Based Representations in Pattern Recognition (GbRPR), Lecture Notes in Computer Science, vol. 14782, Springer, Cham, 2025, pp. 179–188.'
    content = content.replace(old_r15, new_r15)

    old_r19 = '[19] J. Zhang et al., "A survey on dynamic graph neural networks," Front. Comput. Sci., vol. 19, no. 1, p. 191301, 2025.'
    new_r19 = '[19] Y. Zheng, L. Yi, and Z. Wei, "A survey of dynamic graph neural networks," Front. Comput. Sci., vol. 19, no. 6, Article 196323, 2025.'
    content = content.replace(old_r19, new_r19)

    old_r23 = "[23] T. Wang, J. Kang, Y. Yan, A. Kulkarni, and D. Zhou, 'Non-exchangeable Conformal Prediction for Temporal Graph Neural Networks,' in Proc. 31st ACM SIGKDD Conf. Knowl. Discov. Data Min. (KDD), 2025, pp. 3031–3042."
    new_r23 = '[23] T. Wang, J. Kang, Y. Yan, A. Kulkarni, and D. Zhou, "Non-exchangeable conformal prediction for temporal graph neural networks," in Proc. 31st ACM SIGKDD Conf. Knowl. Discov. Data Min. (KDD), vol. 2, 2025, pp. 3031–3042.'
    content = content.replace(old_r23, new_r23)

    with open('create_paper.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated create_paper.py successfully!')

update_create_paper_en()
