import re

def update_create_paper_fa():
    with open('create_paper_fa.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Abstract lift
    content = content.replace(
        "به بهبود {to_fa_num('2.51')} برابری نسبت به شانس تصادفی دست یافته",
        "به بهبود {to_fa_num('2.46')} برابری نسبت به شانس تصادفی کل سبد (و {to_fa_num('2.10')} برابری نسبت به جامعه کاندیداها) دست یافته"
    )

    # 2. Section 4 ground truth 51 -> 52 and candidate pool
    old_s4 = "دقیقاً تعداد {to_fa_num('51')} پذیرنده از ۳۵۰ پذیرنده ({to_fa_num('14.6')}٪) با نمونه‌گیری طبقه‌بندی‌شده از میان کاندیداهای دارای بنچ‌مارک فعال همتایان در تمامی اصناف به عنوان هدف تعیین شدند."
    new_s4 = "دقیقاً تعداد {to_fa_num('52')} پذیرنده از ۳۵۰ پذیرنده ({to_fa_num('14.9')}٪) با نمونه‌گیری طبقه‌بندی‌شده از میان کاندیداهای دارای بنچ‌مارک فعال همتایان (میانگین ۲۹۹ پذیرنده در ۱۰ سید با شانس تصادفی درون‌جامعه‌ای ۱۷٫۴٪) در تمامی اصناف به عنوان هدف تعیین شدند."
    content = content.replace(old_s4, new_s4)

    # 3. Section 5.2 ranking text
    old_s52 = (
        'f"با توجه به شیوع فرصت‌های واقعی در سطح {to_fa_num(\'51\')} پذیرنده از ۳۵۰ پذیرنده (شانس تصادفی معادل {to_fa_num(\'0.146\')} یا {to_fa_num(\'14.6\')}٪)، نتایج جدول (2) نشان می‌دهد که "\n'
        '           f"مدل پیشنهادی HAMTA با Precision@35 معادل {to_fa_num(\'0.366 ± 0.120\')}، Recall@35 معادل {to_fa_num(\'0.246 ± 0.081\')} (با سقف نظری {to_fa_num(\'0.686\')} برای ۳۵ جایگاه از ۵۱ هدف)، "\n'
        '           f"NDCG@35 معادل {to_fa_num(\'0.382 ± 0.116\')} و R-Precision معادل {to_fa_num(\'0.342 ± 0.077\')}، "\n'
        '           f"به ضریب برتری {to_fa_num(\'2.51\')} برابری نسبت به انتخاب تصادفی دست می‌یابد."'
    )
    new_s52 = (
        'f"با توجه به شیوع فرصت‌های واقعی در سطح {to_fa_num(\'52\')} پذیرنده از ۳۵۰ پذیرنده (شانس تصادفی کل سبد معادل {to_fa_num(\'0.1486\')} یا {to_fa_num(\'14.9\')}٪، و شانس تصادفی جامعه کاندیداها معادل {to_fa_num(\'17.4\')}٪)، نتایج جدول (2) نشان می‌دهد که "\n'
        '           f"مدل پیشنهادی HAMTA با Precision@35 معادل {to_fa_num(\'0.366 ± 0.120\')}، Recall@35 معادل {to_fa_num(\'0.246 ± 0.081\')} (با سقف نظری {to_fa_num(\'0.673\')} برای ۳۵ جایگاه از ۵۲ هدف: ۳۵/۵۲ = ۰٫۶۷۳)، "\n'
        '           f"NDCG@35 معادل {to_fa_num(\'0.382 ± 0.116\')} و R-Precision معادل {to_fa_num(\'0.342 ± 0.077\')}، "\n'
        '           f"به ضریب برتری {to_fa_num(\'2.46\')} برابری نسبت به انتخاب تصادفی کل سبد (و {to_fa_num(\'2.10\')} برابری نسبت به خط‌مبنای تصادفی درون‌جامعه کاندیداها) دست می‌یابد."'
    )
    content = content.replace(old_s52, new_s52)

    # 4. Multi-budget Holm-Bonferroni text
    old_mb = (
        '"تحت تصحیح هولم-بونفرونی برای مقایسه‌های چندگانه، برتری‌های HAMTA نسبت به خط‌مبناهای سنتی معناداری آماری خود را حفظ می‌نمایند (p_adj < 0.05): "\n'
        '           "در بودجه K = 10 نسبت به کمترین حجم (p = 0.015) و مدل جدولی (p = 0.039)؛ در بودجه K = 20 نسبت به کمترین حجم (p = 0.005) و مدل جدولی (p = 0.005)؛ و در K = 35 نسبت به گراف ایستا (p = 0.0488)."'
    )
    new_mb = (
        '"تحت تصحیح هولم-بونفرونی برای مقایسه‌های چندگانه، برتری‌های HAMTA نسبت به خط‌مبناهای سنتی کمترین حجم و مدل جدولی در تمامی بودجه‌ها کاملاً معنادار باقی می‌ماند (p_adj < 0.05): "\n'
        '           "در بودجه K = 10 نسبت به کمترین حجم (p_adj = 0.0156) و مدل جدولی (p_adj = 0.0293)؛ در بودجه K = 20 نسبت به کمترین حجم (p_adj = 0.0156) و مدل جدولی (p_adj = 0.0176)؛ "\n'
        '           "و در K = 35 نسبت به کمترین حجم (p_adj = 0.0176) و مدل جدولی (p_adj = 0.0078). نسبت به گراف ایستا در K = 35، آزمون خام ویلکاکسون معنادار است (p = 0.0488) که پس از تصحیح هولم-بونفرونی به p_adj = 0.0977 تعدیل می‌شود. "\n'
        '           "تفاوت‌های HAMTA با خط‌مبنای SFA به سطح معناداری آماری نمی‌رسد و SFA به عنوان یک بنچ‌مارک مرزی ناپارامتریک قدرتمند عمل می‌نماید."'
    )
    content = content.replace(old_mb, new_mb)

    # 5. References [9], [15], [19], [23]
    old_r9 = '[("Z. Liu, C. Chen, X. Yang, J. Zhou, X. Li, L. Song, \\"Graph representation learning for merchant incentive optimization in mobile payment marketing\\", ", 0),'
    new_r9 = '[("Z. Liu, D. Wang, Q. Yu, Z. Zhang, Y. Shen, J. Ma, W. Zhong, J. Gu, J. Zhou, S. Yang, Y. Qi, \\"Graph representation learning for merchant incentive optimization in mobile payment marketing\\", ", 0),'
    content = content.replace(old_r9, new_r9)

    old_r15 = (
        '[("M. Tare, C. Rattasits, Y. Wu, E. Wielewski, \\"Representation learning on large transaction networks using inductive architectures\\", ", 0),\n'
        '         ("Expert Systems with Applications", 1), (", Vol. 248, p. 123480, 2024.", 0)],'
    )
    new_r15 = (
        '[("M. Tare, C. Rattasits, Y. Wu, E. Wielewski, \\"Harnessing GraphSAGE for learning representations of massive transactional networks\\", ", 0),\n'
        '         ("Graph-Based Representations in Pattern Recognition (GbRPR), Lecture Notes in Computer Science", 1), (", Vol. 14782, pp. 179-188, Springer, 2025.", 0)],'
    )
    content = content.replace(old_r15, new_r15)

    old_r19 = (
        '[("J. Zhang et al., \\"A survey on dynamic graph neural networks\\", ", 0),\n'
        '         ("Frontiers of Computer Science", 1), (", Vol. 19, No. 1, p. 191301, 2025.", 0)],'
    )
    new_r19 = (
        '[("Y. Zheng, L. Yi, Z. Wei, \\"A survey of dynamic graph neural networks\\", ", 0),\n'
        '         ("Frontiers of Computer Science", 1), (", Vol. 19, No. 6, Art. 196323, 2025.", 0)],'
    )
    content = content.replace(old_r19, new_r19)

    old_r23 = (
        '[("S. Zargarbashi, S. Antonelli, K. Borgwardt, \\"Non-exchangeable conformal prediction for temporal graph neural networks\\", ", 0),\n'
        '         ("Proc. 31st ACM SIGKDD Conf. on Knowledge Discovery and Data Mining (KDD)", 1), (", 2025.", 0)],'
    )
    new_r23 = (
        '[("T. Wang, J. Kang, Y. Yan, A. Kulkarni, D. Zhou, \\"Non-exchangeable conformal prediction for temporal graph neural networks\\", ", 0),\n'
        '         ("Proc. 31st ACM SIGKDD Conf. on Knowledge Discovery and Data Mining (KDD)", 1), (", Vol. 2, pp. 3031-3042, 2025.", 0)],'
    )
    content = content.replace(old_r23, new_r23)

    with open('create_paper_fa.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated create_paper_fa.py successfully!')

update_create_paper_fa()
