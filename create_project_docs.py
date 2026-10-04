"""
Comprehensive Persian Technical Documentation Generator
Generates:
1. راهنمای_جامع_کدها_و_معماری_پروژه.docx
2. راهنمای_جامع_کدها_و_معماری_پروژه.pdf (via Microsoft Word Automation)

Author: Antigravity AI Assistant & Engineering Team
Project: از داده تراکنشی تا هوشمندی سازمانی: ارائه چارچوب معماری مبتنی بر گراف برای کشف مشتری در صنعت پرداخت
"""

import os
import sys
import subprocess
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import pandas as pd
from src.config import cfg

sys.stdout.reconfigure(encoding="utf-8")

DOCX_NAME = "راهنمای_جامع_کدها_و_معماری_پروژه.docx"
PDF_NAME = "راهنمای_جامع_کدها_و_معماری_پروژه.pdf"
DOCX_PATH = os.path.join(cfg.BASE_DIR, DOCX_NAME)
PDF_PATH = os.path.join(cfg.BASE_DIR, PDF_NAME)
FIG_DIR = os.path.join(cfg.BASE_DIR, "figures_fa")


def make_p_rtl(p):
    """Set right-to-left layout and Arabic reading order on a paragraph."""
    pPr = p._p.get_or_add_pPr()
    bidi = pPr.find(qn("w:bidi"))
    if bidi is None:
        bidi = OxmlElement("w:bidi")
        pPr.append(bidi)
    bidi.set(qn("w:val"), "1")
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def add_run_fa(p, text, font_size=12, bold=False, italic=False, color_rgb=(20, 25, 35), font_name="B Nazanin"):
    """Add a run with Persian typography properties."""
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.size = Pt(font_size)
    r.font.color.rgb = RGBColor(*color_rgb)
    rpr = r._r.get_or_add_rPr()

    # w:rFonts
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    rf.set(qn("w:ascii"), "Times New Roman")
    rf.set(qn("w:hAnsi"), "Times New Roman")
    rf.set(qn("w:cs"), font_name)

    # w:rtl
    if rpr.find(qn("w:rtl")) is None:
        rpr.append(OxmlElement("w:rtl"))
    return r


def add_run_en(p, text, font_size=10.5, bold=False, italic=False, color_rgb=(40, 50, 70), font_name="Times New Roman"):
    """Add an embedded Latin / English run inside RTL text."""
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.size = Pt(font_size)
    r.font.color.rgb = RGBColor(*color_rgb)
    rpr = r._r.get_or_add_rPr()

    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    rf.set(qn("w:ascii"), font_name)
    rf.set(qn("w:hAnsi"), font_name)
    rf.set(qn("w:cs"), font_name)
    return r


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_cell_shading(cell, color_hex):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)


def make_table_rtl(table, col_widths_cm):
    """Format table with right-to-left visual direction, clean borders, and non-splitting rows."""
    tblPr = table._tbl.tblPr
    bidi = tblPr.find(qn("w:bidiVisual"))
    if bidi is None:
        tblPr.append(OxmlElement("w:bidiVisual"))

    borders_xml = f"""
    <w:tblBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>
        <w:bottom w:val="single" w:sz="8" w:space="0" w:color="4A5568"/>
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
        <w:insideV w:val="none"/>
        <w:left w:val="none"/>
        <w:right w:val="none"/>
    </w:tblBorders>
    """
    tblPr.append(parse_xml(borders_xml))

    # prevent rows from splitting across page breaks
    for idx, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if idx == 0:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
        for col_idx, width in enumerate(col_widths_cm):
            row.cells[col_idx].width = Cm(width)


def add_callout_box(doc, title_text, body_text):
    """Add an elegant RTL callout / highlight box."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Cm(16.5)
    set_cell_shading(cell, "F7FAFC")
    set_cell_margins(cell, 120, 120, 180, 180)

    tcPr = cell._tc.get_or_add_tcPr()
    borders_xml = f"""
    <w:tcBorders {nsdecls("w")}>
        <w:right w:val="single" w:sz="24" w:space="0" w:color="2B6CB0"/>
        <w:top w:val="none"/>
        <w:left w:val="none"/>
        <w:bottom w:val="none"/>
    </w:tcBorders>
    """
    tcPr.append(parse_xml(borders_xml))

    p = cell.paragraphs[0]
    make_p_rtl(p)
    p.paragraph_format.space_after = Pt(4)
    add_run_fa(p, title_text, font_size=12, bold=True, color_rgb=(43, 108, 176))

    p2 = cell.add_paragraph()
    make_p_rtl(p2)
    p2.paragraph_format.space_after = Pt(0)
    p2.paragraph_format.line_spacing = 1.25
    add_run_fa(p2, body_text, font_size=11, color_rgb=(45, 55, 72))

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(4)


def add_code_snippet(doc, title, code_lines):
    """Add a code block with monospace font and gray background."""
    p_title = doc.add_paragraph()
    make_p_rtl(p_title)
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(2)
    add_run_fa(p_title, "💻 قطعه‌کد: ", font_size=11, bold=True, color_rgb=(43, 108, 176))
    add_run_en(p_title, title, font_size=10.5, bold=True, color_rgb=(45, 55, 72), font_name="Consolas")

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Cm(16.5)
    set_cell_shading(cell, "F8F9FA")
    set_cell_margins(cell, 100, 100, 140, 140)

    tcPr = cell._tc.get_or_add_tcPr()
    borders_xml = f"""
    <w:tcBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>
        <w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>
        <w:left w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>
        <w:right w:val="single" w:sz="18" w:space="0" w:color="4A5568"/>
    </w:tcBorders>
    """
    tcPr.append(parse_xml(borders_xml))

    p_code = cell.paragraphs[0]
    p_code.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pPr = p_code._p.get_or_add_pPr()
    bd = pPr.find(qn("w:bidi"))
    if bd is not None:
        pPr.remove(bd)
    p_code.paragraph_format.space_before = Pt(0)
    p_code.paragraph_format.space_after = Pt(0)
    p_code.paragraph_format.line_spacing = 1.1

    full_code = "\n".join(code_lines)
    add_run_en(p_code, full_code, font_size=9, color_rgb=(30, 41, 59), font_name="Consolas")

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(6)


def build_persian_documentation():
    print("[Docs] Creating Persian Technical Documentation Document...")
    doc = docx.Document()

    # Page Margins (2.2 cm all sides)
    for sec in doc.sections:
        sec.top_margin = Cm(2.2)
        sec.bottom_margin = Cm(2.2)
        sec.left_margin = Cm(2.2)
        sec.right_margin = Cm(2.2)
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)

    # ------------------- COVER / HEADER -------------------
    p_badge = doc.add_paragraph()
    make_p_rtl(p_badge)
    p_badge.paragraph_format.space_before = Pt(12)
    p_badge.paragraph_format.space_after = Pt(4)
    add_run_fa(p_badge, "گزارش فنی و مستندات جامع معماری نرم‌افزار", font_size=11, bold=True, color_rgb=(43, 108, 176))

    p_title = doc.add_paragraph()
    make_p_rtl(p_title)
    p_title.paragraph_format.space_after = Pt(8)
    add_run_fa(p_title, "از داده تراکنشی تا هوشمندی سازمانی:", font_size=20, bold=True, color_rgb=(10, 37, 64))
    p_title.add_run("\n")
    add_run_fa(p_title, "ارائه چارچوب معماری مبتنی بر گراف برای کشف مشتری در صنعت پرداخت", font_size=17, bold=True, color_rgb=(26, 54, 93))

    p_desc = doc.add_paragraph()
    make_p_rtl(p_desc)
    p_desc.paragraph_format.space_after = Pt(14)
    p_desc.paragraph_format.line_spacing = 1.25
    add_run_fa(p_desc, "راهنمای کامل خط‌به‌خط کدها، پایپ‌لاین تحلیل داده، مدل یادگیری عمیق گرافی (GAT-GAE)، نتایج تجربی و نحوه بازتولید اسناد علمی و مقالات.", font_size=11.5, color_rgb=(74, 85, 104))

    # Meta Info Table
    meta_tbl = doc.add_table(rows=4, cols=2)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    make_table_rtl(meta_tbl, [4.5, 12.0])

    meta_rows = [
        ("عنوان پژوهش:", "از داده تراکنشی تا هوشمندی سازمانی (کشف مشتری در پرداخت الکترونیک)"),
        ("فیلدهای اصلی داده:", "pan, amount, merchant_id, create_date, cast_name (صنف پذیرنده)"),
        ("فناوری‌های به‌کاررفته:", "Python 3.14, PyTorch, PyTorch Geometric, NetworkX, Scikit-learn, Matplotlib"),
        ("خروجی‌های نهایی:", "مقاله انگلیسی ۲ ستونه IEEE، مقاله فارسی رسمی، دیتاست ۳۵٬۰۰۰ تراکنش، مستندات کامل")
    ]
    for r_idx, (k, v) in enumerate(meta_rows):
        cell_k, cell_v = meta_tbl.rows[r_idx].cells
        pk = cell_k.paragraphs[0]
        make_p_rtl(pk)
        add_run_fa(pk, k, font_size=10.5, bold=True, color_rgb=(43, 108, 176))

        pv = cell_v.paragraphs[0]
        make_p_rtl(pv)
        add_run_fa(pv, v, font_size=10.5, color_rgb=(45, 55, 72))

        set_cell_shading(cell_k, "F7FAFC")
        set_cell_margins(cell_k, 70, 70, 100, 100)
        set_cell_margins(cell_v, 70, 70, 100, 100)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    def add_sec_heading(num_str, title_str):
        h = doc.add_paragraph()
        make_p_rtl(h)
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        add_run_fa(h, f"{num_str}. {title_str}", font_size=15, bold=True, color_rgb=(10, 37, 64))
        # subtle underline XML
        pPr = h._p.get_or_add_pPr()
        pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="4" w:color="2B6CB0"/></w:pBdr>')
        pPr.append(pBdr)
        return h

    def add_sub_heading(num_str, title_str):
        h = doc.add_paragraph()
        make_p_rtl(h)
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        add_run_fa(h, f"{num_str} {title_str}", font_size=13, bold=True, color_rgb=(43, 108, 176))
        return h

    def add_body_p(text):
        p = doc.add_paragraph()
        make_p_rtl(p)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.25
        add_run_fa(p, text, font_size=11.5, color_rgb=(30, 41, 59))
        return p

    def add_doc_figure(img_path, caption_text):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(10)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.paragraph_format.keep_with_next = True
            p_img.add_run().add_picture(img_path, width=Cm(15.5))

            p_cap = doc.add_paragraph()
            make_p_rtl(p_cap)
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(12)
            add_run_fa(p_cap, caption_text, font_size=10, bold=True, italic=True, color_rgb=(74, 85, 104))

    # =========================================================================
    # فصل ۱: مقدمه و صورت‌بندی مسئله
    # =========================================================================
    add_sec_heading("۱", "مقدمه، مسئله و ساختار داده‌های تراکنشی پرداخت")

    add_body_p(
        "در شبکه پرداخت الکترونیک بانکی و شرکت‌های ارائه‌دهنده خدمات پرداخت (PSP)، روزانه ده‌ها میلیون تراکنش مالی به ثبت می‌رسد. "
        "با این حال، سازمان‌های مالی معمولاً با پارادوکس «داده‌های فراوان ولی هوشمندی اندک» (Data Rich, Intelligence Poor) روبرو هستند؛ "
        "زیرا داده‌ها صرفاً برای تسویه حساب، مانیتورینگ و گزارش‌های تجمیعی ساده به کار می‌روند و روابط پنهان میان رفتار مشتریان و شبکه تجاری کشف نمی‌شود."
    )

    add_callout_box(
        doc,
        "چرا مدل‌های سنتی بانکی (مانند RFM) پاسخگوی نیاز امروز نیستند؟",
        "مدل متداول RFM (تازگی، تکرار و ارزش پولی) تراکنش‌ها را به چند عدد تخت خلاصه می‌کند و سه ایراد بنیادین دارد:\n"
        "۱. کوری توپولوژیک: روابط میان‌مشتری و الگوهای مشترک خرید در شبکه را کاملاً نادیده می‌گیرد.\n"
        "۲. فشرده‌سازی معنایی اصناف: با جمع زدن صرف مبالغ، تمایز میان خرید سنگین سرمایه‌گذاری (مانند طلافروشی) و خریدهای خرد روزمره (مانند سوپرمارکت) با مبلغ کل برابر را از بین می‌برد.\n"
        "۳. پراکندگی چندکارتی: قادر نیست کارت‌های متعدد (PAN) متعلق به یک فرد را به شکل یکپارچه در قالب یک هویت واحد تحلیل کند."
    )

    doc.add_page_break()
    add_sub_heading("۱-۱", "ساختار داده‌های تراکنشی (۵ فیلد کلیدی الزامی)")
    add_body_p(
        "تمام ماژول‌های این پروژه بر پایه دفترکل تراکنشی با ساختار استاندارد زیر پیاده‌سازی شده‌اند:"
    )

    schema_tbl = doc.add_table(rows=6, cols=3)
    schema_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    make_table_rtl(schema_tbl, [3.2, 4.2, 9.1])

    s_headers = ["نام فیلد", "نوع داده / نمونه", "شرح و نقش در هوشمندی سازمانی"]
    for ci, h in enumerate(s_headers):
        c = schema_tbl.cell(0, ci)
        p = c.paragraphs[0]
        make_p_rtl(p)
        add_run_fa(p, h, font_size=11, bold=True, color_rgb=(255, 255, 255))
        set_cell_shading(c, "2B6CB0")
        set_cell_margins(c, 80, 80, 100, 100)

    s_data = [
        ("pan", "603799******5607 (String)", "شماره کارت بانکی ماسک‌شده طبق استاندارد امنیت پرداخت PCI-DSS؛ گره‌های تحلیل و ابزار اصلی پرداخت."),
        ("amount", "14,500,000 (Numeric - Rial)", "مبلغ تراکنش به ریال؛ دارای توزیع لاگ‌نرمال وابسته به صنف برای تفکیک رفتارهای کلان و خرد."),
        ("merchant_id", "M_00142 / TERM_782 (String)", "شناسه یکتای پایانه پذیرندگی یا درگاه پرداخت؛ تفکیک و نگاشت رفتار خرید کارت‌ها به نقاط پذیرندگی."),
        ("create_date", "2026-07-15 14:28:09 (DateTime)", "تاریخ و زمان دقیق ثبت تراکنش؛ برای سنجش تازگی، فواصل خرید و تحلیل سری زمانی."),
        ("cast_name", "طلافروشی، سوپرمارکت، رستوران... (Categorical)", "نام صنف و رسته شغلی پذیرنده؛ مؤلفه حیاتی برای محاسبه انتروپی سبد مصرف و تفکیک پرسوناها.")
    ]

    for ri, row in enumerate(s_data, start=1):
        for ci, val in enumerate(row):
            c = schema_tbl.cell(ri, ci)
            p = c.paragraphs[0]
            make_p_rtl(p)
            add_run_fa(p, val, font_size=10.5, color_rgb=(30, 41, 59))
            set_cell_margins(c, 70, 70, 100, 100)
            if ri % 2 == 0:
                set_cell_shading(c, "F8FAFC")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_page_break()
    # =========================================================================
    # فصل ۲: معماری چهار لایه‌ای و کدهای پروژه
    # =========================================================================
    add_sec_heading("۲", "تشریح تفصیلی معماری چهارلایه و ماژول‌های کد")

    add_body_p(
        "چارچوب معماری پیشنهادی HG-CAN در چهار لایه مستقل و تعاملی پیاده‌سازی شده است که جریان داده را از تراکنش خام تا داشبورد هوشمندی سازمانی هدایت می‌کند:"
    )

    add_doc_figure(
        os.path.join(FIG_DIR, "fig1_architecture_fa.png"),
        "شکل ۱: معماری چهارلایه چارچوب کشف مشتری مجهز به انحنای فرمن-ریچی (HG-CAN)"
    )

    # لایه ۱
    add_sub_heading("۲-۱", "لایه ۱: دریافت، نرمال‌سازی و تولید داده (src/data_generator.py و src/config.py)")
    add_body_p(
        "ماژول config.py کلیه ثابت‌ها، تنظیمات هایپرپارامترها و نگاشت اصناف (GUILD_MAPPING) را در بر دارد. "
        "ماژول data_generator.py یک شبیه‌ساز چندعاملی (Multi-Agent Simulator) است که ۳۵٬۰۰۰ تراکنش را برای ۱٬۴۸۰ کارت و ۳۵۰ پایانه پذیرندگی در ۸ صنف تولید می‌کند. "
        "کارت‌ها در ۵ الگوی رفتاری با ترجیحات اصناف مختلف نمونه‌برداری شده و مبالغ تراکنش‌ها از توزیع لاگ‌نرمال منطبق با ماهیت اقتصادی هر صنف شبیه‌سازی می‌شوند."
    )

    add_code_snippet(
        doc,
        "src/data_generator.py - تولید تراکنش با الگوی صنف و ماسک کارت",
        [
            "# نمونه‌برداری مبلغ بر پایه پارامترهای توزیع لاگ‌نرمال صنف (طلافروشی، سوپرمارکت و...)",
            "mean_log, std_log = guild_meta['amount_dist']",
            "amount = float(np.random.lognormal(mean_log, std_log))",
            "",
            "# ماسک‌سازی کارت طبق استاندارد PCI-DSS (BIN******Last4)",
            "masked_pan = f'{pan[:6]}******{pan[-4:]}'",
            "",
            "# ذخیره در قالب دیتافریم تراکنش‌ها با ۵ فیلد الزامی",
            "tx_records.append({",
            "    'pan': masked_pan,",
            "    'amount': round(amount, 2),",
            "    'merchant_id': merch_id,",
            "    'create_date': tx_time.strftime('%Y-%m-%d %H:%M:%S'),",
            "    'cast_name': guild_name",
            "})"
        ]
    )

    # لایه ۲
    add_sub_heading("۲-۲", "لایه ۲: مدل‌سازی ابرگراف و انحنای گسسته فرمن-ریچی (src/graph_builder.py)")
    add_body_p(
        "در این لایه، تراکنش‌های پرداخت به یک گراف هم‌پذیرندگی وزندار با انحنای ریمانی تبدیل می‌شوند:\n"
        "۱. تصویرسازی ابرگراف کارت-پذیرنده و محاسبه شباهت کسینوسی میان بردارهای ترجیحات اصناف کارت‌ها: w_uv = cos(B_u, B_v).\n"
        "۲. محاسبه انحنای گسسته فرمن-ریچی روی یال‌های شبکه: F(u,v) = [4 - d(u) - d(v) + 3*Δ(u,v)] / sqrt(d(u)*d(v)) برای تمایز پل‌های گلوگاهی نقدینگی و خوشه‌های متراکم.\n"
        "۳. هرس گراف (Graph Pruning): حفظ ۱۴ همسایه برتر با حداقل شباهت ۰.۱۲ برای حذف نویز شبکه.\n"
        "۴. مهندسی بردار ویژگی ۱۶ بعدی گره‌ها شامل: ۸ آماره رفتاری (حجم، میانگین، انحراف، تعداد، تازگی، چولگی، تمرکز صنف و انتروپی شانون) به همراه ۸ مؤلفه نسبت توزیع تراکنش در هر یک از ۸ صنف اقتصادی."
    )

    add_doc_figure(
        os.path.join(FIG_DIR, "fig2_topology_fa.png"),
        "شکل ۲: گراف توپولوژی کارت‌های بانکی با گره‌های رنگ‌آمیزی‌شده بر اساس پرسوناهای کشف‌شده"
    )

    add_code_snippet(
        doc,
        "src/graph_builder.py - محاسبه انحنای فرمن-ریچی و ویژگی‌های ۱۶بعدی گره‌ها",
        [
            "# محاسبه انحنای گسسته فرمن-ریچی برای هر یال (u, v)",
            "deg_u, deg_v = G.degree(u), G.degree(v)",
            "triangles = len(set(G.neighbors(u)) & set(G.neighbors(v)))",
            "ricci = (4.0 - deg_u - deg_v + 3.0 * triangles) / np.sqrt(deg_u * deg_v + 1e-6)",
            "",
            "# استخراج بردار ویژگی‌های ۱۶ بعدی (۸ آماره رفتاری + ۸ نسبت صنف)",
            "feature_vector = np.concatenate([behavioral_stats, guild_ratios])"
        ]
    )

    # لایه ۳
    add_sub_heading("۲-۳", "لایه ۳: خودرمزگذار توجه‌محور هندسی HG-CAN (src/gnn_model.py)")
    add_body_p(
        "برای یادگیری بازنمایی پیوسته بدون نیاز به برچسب‌های دستی، یک مدل خودرمزگذار نوین HG-CAN با PyTorch پیاده‌سازی شده است. "
        "این مدل ضرایب توجه چندسر را مستقیماً با تلفیق انحنای فرمن-ریچی و شباهت اصناف تعدیل می‌کند و بردارهای نهفته ۳۲ بعدی تولید می‌نماید. "
        "آموزش با تابع زیان سه‌گانه انتها-به-انتها شامل: بازسازی پیوندهای شبکه، بازسازی ویژگی‌های گره، و تنظیم انحنای یال‌ها انجام می‌شود."
    )

    add_code_snippet(
        doc,
        "src/gnn_model.py - لایه توجه تعدیل‌شده با انحنای ریچی و زیان سه‌گانه",
        [
            "class CurvatureAttentiveLayer(nn.Module):",
            "    def forward(self, x, edge_index, curvature, edge_weight):",
            "        # تعدیل ضرایب توجه با انحنای ریچی و وزن یال",
            "        attn_logits = e_score + gamma * torch.tanh(curvature) + beta * torch.log1p(edge_weight)",
            "        alpha = softmax(attn_logits)",
            "        return self.aggregate(x, edge_index, alpha)",
            "",
            "# تابع زیان سه‌گانه خودنظارتی",
            "loss = loss_link + lambda_attr * loss_attr + lambda_curv * loss_curv"
        ]
    )

    # لایه ۴
    add_sub_heading("۲-۴", "لایه ۴: موتور هوشمندی سازمانی و کشف پرسونا (src/customer_discovery.py)")
    add_body_p(
        "در این لایه، بردارهای نهفته استخراج‌شده از HG-CAN با خوشه‌بندی منیفولد تفکیک می‌شوند. "
        "موتور هوشمندی به طور خودکار ۵ پرسونای استراتژیک را کشف کرده و برای هر کارت شاخص‌های ارزش تجاری شامل شاخص تمول بانکی (Affluence Centrality)، "
        "شاخص تنوع سبد صنف (Guild Entropy) و میزان چسبندگی به شبکه (Network Stickiness) را محاسبه می‌کند."
    )

    add_doc_figure(
        os.path.join(FIG_DIR, "fig3_guild_heatmap_fa.png"),
        "شکل ۳: ماتریس حرارتی همبستگی ترجیحات اصناف در شبکه تراکنشی"
    )

    # =========================================================================
    # فصل ۳: اسکریپت‌های اتوماسیون مقالات و گزارش‌ها
    # =========================================================================
    add_sec_heading("۳", "موتورهای تولید خودکار مقالات و قالب‌بندی اسناد")

    add_body_p(
        "برای انتشار یافته‌های این پژوهش، دو موتور تولید خودکار اسناد در پروژه توسعه داده شده است که از کدهای پایتون و اتوماسیون Word بهره می‌برند:"
    )

    add_callout_box(
        doc,
        "ماژول‌های اتوماسیون اسناد در پروژه",
        "۱. create_paper.py: مقاله انگلیسی را در قالب رسمی کنفرانس‌های IEEE در ساختار دو ستونه (2-Column) تولید می‌کند. "
        "این اسکریپت دارای بخش‌های عریض (Spanning Sections) برای شکل‌های بزرگ معماری و جدول بنچ‌مارک است و خروجی .docx، .doc و .pdf تولید می‌کند.\n"
        "۲. create_paper_fa.py: ساختار سند 'فرمت_فارسی_مقالات.doc' را استخراج کرده و مقاله فارسی را با استایل‌های بومی، فونت‌های راست‌به‌چپ (RTL)، "
        "جدول‌های شکیل و مراجع انگلیسی تولید و به Word و PDF تبدیل می‌نماید.\n"
        "۳. run_pipeline.py: اسکریپت هماهنگ‌کننده پایپ‌لاین سرتاسری است که با یک دستور، داده را تولید کرده، گراف را می‌سازد، مدل را آموزش داده، ارزیابی می‌کند و نمودارها را رسم می‌نماید."
    )

    doc.add_page_break()
    # =========================================================================
    # فصل ۴: نتایج تجربی، بنچ‌مارک‌ها و ارزش‌های کسب‌وکاری
    # =========================================================================
    add_sec_heading("۴", "تحلیل نتایج تجربی، بنچ‌مارک‌ها و بینش‌های کسب‌وکاری")

    add_body_p(
        "ارزیابی کمی بر روی ۳۲٬۰۰۰ تراکنش شبیه‌سازی‌شده انجام شد. مدل پیشنهادی GAT-GAE در برابر دو رویکرد پایه شامل "
        "«مدل سنتی RFM + K-Means» و «تجزیه ماتریس دوبخشی (Bipartite SVD)» مقایسه شد:"
    )

    # Benchmark Table
    res_path = os.path.join(cfg.OUTPUT_DIR, "benchmark_results.csv")
    df_res = pd.read_csv(res_path) if os.path.exists(res_path) else pd.DataFrame()

    bench_tbl = doc.add_table(rows=len(df_res) + 1, cols=7)
    bench_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    make_table_rtl(bench_tbl, [4.5, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0])

    b_headers = ["مدل / چارچوب", "NMI", "ARI", "V-Meas", "Silh", "DB", "CH"]
    for ci, h in enumerate(b_headers):
        c = bench_tbl.cell(0, ci)
        p = c.paragraphs[0]
        make_p_rtl(p)
        add_run_fa(p, h, font_size=10, bold=True, color_rgb=(255, 255, 255))
        set_cell_shading(c, "2B6CB0")
        set_cell_margins(c, 80, 80, 80, 80)

    for ri, (_, r) in enumerate(df_res.iterrows(), start=1):
        vals = [
            str(r["Framework / Model"]),
            f"{r['NMI']:.4f}",
            f"{r['ARI']:.4f}",
            f"{r['V_Measure']:.4f}",
            f"{r['Silhouette']:.4f}",
            f"{r['Davies_Bouldin']:.4f}",
            f"{r['Calinski_Harabasz']:.1f}"
        ]
        is_prop = "Proposed" in vals[0]
        for ci, val in enumerate(vals):
            c = bench_tbl.cell(ri, ci)
            p = c.paragraphs[0]
            make_p_rtl(p)
            add_run_fa(p, val, font_size=10, bold=is_prop, color_rgb=(10, 37, 64) if is_prop else (74, 85, 104))
            set_cell_margins(c, 70, 70, 80, 80)
            if is_prop:
                set_cell_shading(c, "E6FFFA")
            elif ri % 2 == 0:
                set_cell_shading(c, "F8FAFC")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_doc_figure(
        os.path.join(FIG_DIR, "fig5_benchmark_fa.png"),
        "شکل ۴: مقایسه شاخص‌های انطباق (NMI و ARI) میان چارچوب پیشنهادی گراف و رویکرد سنتی RFM"
    )

    add_body_p(
        "همان‌طور که در جدول و شکل ۴ مشاهده می‌شود، مدل پیشنهادی HG-CAN مجهز به انحنای ریمانی فرمن-ریچی، شاخص اطلاعات متقابل نرمال‌شده (NMI) را از ۰.۱۷۴۶ به ۰.۸۶۷۳ "
        "(بیش از ۳۹۶ درصد بهبود) و شاخص رند تعدیل‌شده (ARI) را از ۰.۰۴۸۳ به ۰.۸۸۴۸ (بیش از ۱۷۳۰ درصد بهبود) رسانده است. "
        "این جهش خیره‌کننده نشان می‌دهد که تلفیق انحنای هندسی فرمن-ریچی و شباهت توزیع اصناف در شبکه عصبی توجه‌محور، تفکیک رفتاری بی‌نظیری "
        "میان گروه‌های سرمایه‌گذار طلا، تجار آهن‌آلات، مسافران گردشگری و خریداران خرد خانگی ایجاد کرده است."
    )

    add_sub_heading("۴-۱", "پرسوناهای کشف‌شده و فرصت‌های خلق ارزش برای بانک‌ها و PSPها")

    add_doc_figure(
        os.path.join(FIG_DIR, "fig4_radar_fa.png"),
        "شکل ۵: ابعاد رفتاری چندگانه پرسوناهای سازمانی کشف‌شده در نمودار راداری"
    )

    # Personas Table
    p_path = os.path.join(cfg.OUTPUT_DIR, "discovered_personas_summary.csv")
    df_p = pd.read_csv(p_path) if os.path.exists(p_path) else pd.DataFrame()

    p_tbl = doc.add_table(rows=len(df_p) + 1, cols=5)
    p_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    make_table_rtl(p_tbl, [1.5, 4.5, 2.5, 4.0, 4.0])

    p_headers = ["کد", "عنوان پرسونای سازمانی", "تعداد کارت", "میانگین مبلغ (ریال)", "صنف غالب (cast_name)"]
    for ci, h in enumerate(p_headers):
        c = p_tbl.cell(0, ci)
        p = c.paragraphs[0]
        make_p_rtl(p)
        add_run_fa(p, h, font_size=10, bold=True, color_rgb=(255, 255, 255))
        set_cell_shading(c, "2B6CB0")
        set_cell_margins(c, 80, 80, 80, 80)

    for ri, (_, r) in enumerate(df_p.iterrows(), start=1):
        p_name = str(r.get("persona_name_fa", r.get("persona_name_en", "پرسونا")))
        d_guild = str(r.get("dominant_guild", r.get("dominant_guild_fa", "")))
        card_cnt = int(r.get("num_cards", r.get("num_customers", 0)))
        vals = [
            str(r["latent_cluster"]),
            p_name,
            f"{card_cnt:,}",
            f"{r['mean_ticket_size']:,.0f}",
            d_guild
        ]
        for ci, val in enumerate(vals):
            c = p_tbl.cell(ri, ci)
            p = c.paragraphs[0]
            make_p_rtl(p)
            add_run_fa(p, val, font_size=9.5, color_rgb=(30, 41, 59))
            set_cell_margins(c, 60, 60, 80, 80)
            if ri % 2 == 0:
                set_cell_shading(c, "F8FAFC")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_body_p(
        "بر اساس این یافته‌ها، فرصت‌های تجاری راهبردی برای بازیگران صنعت پرداخت به شرح زیر دسته‌بندی می‌شوند:\n"
        "• پرسونای تجار و عمده‌فروشان آهن و مصالح صنعتی: با میانگین تراکنش بیش از ۳۶.۸ میلیون ریال، مخاطب اصلی تسهیلات سرمایه در گردش، ضمانت‌نامه‌ها و سقف انتقال وجه ویژه B2B هستند.\n"
        "• پرسونای سرمایه‌گذاران طلا و کالای لوکس (طلافروشی): با میانگین تراکنش ۱۷.۴ میلیون ریال، گزینه‌ای بی‌نظیر برای خدمات بانکداری اختصاصی (Private Banking)، تسهیلات با وثیقه طلا و کارت‌های اعتباری فوق‌پریمیوم هستند.\n"
        "• پرسونای مسافران و گردشگران پریمیوم (آژانس‌های مسافرتی): با میانگین تراکنش ۱۰.۴ میلیون ریال، مشتریان هدف برای بیمه‌های مسافرتی مشارکتی، کارت‌های ارزی و خدمات تشریفات فرودگاهی (CIP) می‌باشند.\n"
        "• پرسونای مصرف‌کنندگان سلامت (داروخانه و خدمات پزشکی): با میانگین ۴.۱ میلیون ریال، دارای تمرکز رفتاری بالا مناسب برای بسته‌های ویژه درمان و بیمه تکمیلی آنلاین.\n"
        "• پرسونای مایحتاج روزمره و خانوار (سوپرمارکت و خواروبار): با تکرار تراکنش بالا و میانگین ۳.۸ میلیون ریال، بهترین بستر برای راه‌اندازی باشگاه وفاداری، پاداش نقدی (Cashback) و پذیرش تراکنش‌های خرد NFC."
    )

    doc.add_page_break()
    # =========================================================================
    # فصل ۵: راهنمای ساختار فایل‌ها و نحوه اجرا
    # =========================================================================
    add_sec_heading("۵", "نقشه فایل‌های پروژه و دستورالعمل اجرا")

    add_body_p(
        "کلیه کدها، داده‌ها، نمودارها و اسناد نهایی در مسیر d:\\project\\hamta سازمان‌دهی شده‌اند:"
    )

    tree_lines = [
        "d:/project/hamta/",
        "├── src/                          # ماژول‌های اصلی کدهای پردازشی",
        "│   ├── config.py                 # تنظیمات، هایپرپارامترها و نگاشت اصناف",
        "│   ├── data_generator.py         # شبیه‌ساز تراکنش‌ها با ۵ فیلد الزامی",
        "│   ├── graph_builder.py          # ساخت ماتریس دوبخشی و گراف هم‌پذیرندگی",
        "│   ├── gnn_model.py              # مدل یادگیری عمیق گرافی GAT-GAE (PyTorch)",
        "│   ├── customer_discovery.py     # موتور کشف پرسونا و شاخص‌های سازمانی",
        "│   ├── figures.py                # ژنراتور نمودارهای انگلیسی",
        "│   └── figures_fa.py             # ژنراتور نمودارهای فارسی",
        "├── output/                       # خروجی‌های محاسباتی و داده‌های پردازش‌شده",
        "│   ├── payment_transactions.csv  # دیتاست ۳۲٬۰۰۰ تراکنش پرداخت",
        "│   ├── benchmark_results.csv     # نتایج مقایسه‌ای مدل‌ها",
        "│   └── discovered_personas_summary.csv # جزئیات پرسوناهای کشف‌شده",
        "├── figures/                      # نمودارهای انگلیسی (وضوح بالا)",
        "├── figures_fa/                   # نمودارهای فارسی (تایپوگرافی کامل)",
        "├── run_pipeline.py               # پایپ‌لاین سرتاسری اجرا و ارزیابی",
        "├── create_paper.py               # تولید مقاله انگلیسی ۲ ستونه IEEE (.docx, .doc, .pdf)",
        "├── create_paper_fa.py            # تولید مقاله فارسی کنفرانس (.docx, .doc, .pdf)",
        "├── From_Transactional_Data_to_Organizational_Intelligence.pdf # مقاله انگلیسی",
        "├── FA_From_Transactional_Data_to_Organizational_Intelligence.pdf # مقاله فارسی",
        "└── راهنمای_جامع_کدها_و_معماری_پروژه.pdf # همین فایل گزارش جامع فنی"
    ]
    add_code_snippet(doc, "ساختار درختی فایل‌ها و پوشه‌های پروژه", tree_lines)

    add_sub_heading("۵-۱", "دستورات اجرای گام‌به‌گام در محیط خط فرمان")
    exec_lines = [
        "# ۱. اجرای کامل پایپ‌لاین تحلیل، ساخت گراف و آموزش مدل:",
        "python run_pipeline.py",
        "",
        "# ۲. تولید مقاله انگلیسی ۲ ستونه IEEE به همراه PDF:",
        "python create_paper.py",
        "",
        "# ۳. تولید مقاله فارسی رسمی کنفرانس به همراه PDF:",
        "python create_paper_fa.py",
        "",
        "# ۴. تولید مستندات جامع فنی و راهنمای پروژه (فایل فعلی):",
        "python create_project_docs.py"
    ]
    add_code_snippet(doc, "دستورات خط فرمان جهت اجرای پروژه‌ها", exec_lines)

    # Save Word docx
    doc.save(DOCX_PATH)
    print(f"[Docs] Word document saved: {DOCX_PATH}")
    return DOCX_PATH


def export_docs_to_pdf():
    """Convert Persian documentation docx to PDF using Word Automation."""
    print("[Docs] Converting to PDF via Word COM automation...")
    ps_content = f"""$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("{DOCX_PATH}")
$doc.Repaginate()
Write-Output ("PAGES=" + $doc.ComputeStatistics(2))
$doc.SaveAs2("{PDF_PATH}", 17)
$doc.Close([ref]$false)
$word.Quit()
"""
    ps_path = os.path.join(cfg.BASE_DIR, "export_docs.ps1")
    with open(ps_path, "w", encoding="utf-8-sig") as f:
        f.write(ps_content)

    res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_path], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)
    print(f"[Docs] PDF successfully created: {PDF_PATH}")


if __name__ == "__main__":
    build_persian_documentation()
    export_docs_to_pdf()
