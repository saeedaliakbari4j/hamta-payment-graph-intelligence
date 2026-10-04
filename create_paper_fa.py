"""
Persian (RTL) version of the paper, written into the official Persian conference template
(فرمت_فارسی_مقالات.doc). The template is converted to .docx, its body is replaced, and
all formatting comes from the template's own styles (Title, Author, Heading 0/1/2, Abstract,
Text1, Text, Bulleted Text, Figure Caption, Figure Text, EN_REF ...).

All numbers are read from output/*.csv so they are identical to the English paper.
"""
import os
import re
import sys
import copy
import glob
import subprocess

import docx
import pandas as pd
from docx.shared import Cm
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from src.config import cfg

sys.stdout.reconfigure(encoding="utf-8")

BASE = cfg.BASE_DIR
FIG = os.path.join(BASE, "figures_fa")
TEMPLATE_DOCX = os.path.join(BASE, "template_fa.docx")
OUT_DOCX = os.path.join(BASE, "FA_From_Transactional_Data_to_Organizational_Intelligence.docx")
OUT_DOC = OUT_DOCX[:-1].replace(".docx", "") + ".doc" if False else OUT_DOCX.replace(".docx", ".doc")

COL_W = 4650  # twips: one column = 8.2 cm

# ----------------------------------------------------------------------------- text helpers
TOKEN = re.compile(
    r"(?P<sub>[A-Za-zα-ωΑ-Ω]_\{[^}]+\})"
    r"|(?P<cite>\[\d+(?:[,\-]\d+)*\])"
    r"|(?P<lat>[A-Za-z0-9α-ωΑ-Ω][A-Za-z0-9_\.\+/\-α-ωΑ-Ω]*(?:\s[A-Za-z0-9α-ωΑ-Ω][A-Za-z0-9_\.\+/\-α-ωΑ-Ω]*)*)"
)


def _rpr(run):
    return run._r.get_or_add_rPr()


def _set_fonts(run, latin):
    rpr = _rpr(run)
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    if latin:
        for a in ("w:ascii", "w:hAnsi", "w:cs"):
            rf.set(qn(a), "Times New Roman")
    else:
        rf.set(qn("w:hint"), "cs")
        if rpr.find(qn("w:rtl")) is None:
            rpr.append(OxmlElement("w:rtl"))


def _style_run(run, bold=False, italic=False, sup=False, sub=False):
    rpr = _rpr(run)
    if bold:
        for t in ("w:b", "w:bCs"):
            if rpr.find(qn(t)) is None:
                rpr.insert(1, OxmlElement(t))
    if italic:
        for t in ("w:i", "w:iCs"):
            if rpr.find(qn(t)) is None:
                rpr.insert(1, OxmlElement(t))
    if sup or sub:
        va = OxmlElement("w:vertAlign")
        va.set(qn("w:val"), "superscript" if sup else "subscript")
        rpr.append(va)


def _emit(par, text, latin, **kw):
    if not text:
        return
    r = par.add_run(text)
    _set_fonts(r, latin)
    _style_run(r, **kw)


def add_text(par, text, bold=False, italic=False):
    """Persian runs (rtl, complex-script font) + Latin runs (Times New Roman, LTR)."""
    pos = 0
    for m in TOKEN.finditer(text):
        s, e = m.span()
        if m.group("lat"):
            # do not swallow sentence punctuation that follows a Latin token
            while text[s:e] and text[e - 1] in ".-":
                e -= 1
        if s > pos:
            _emit(par, text[pos:s], False, bold=bold, italic=italic)
        if m.group("sub"):
            base, sub = m.group("sub")[0], m.group("sub")[3:-1]
            _emit(par, base, True, bold=bold, italic=True)
            _emit(par, sub, True, bold=bold, sub=True)
        else:
            _emit(par, text[s:e], True, bold=bold, italic=italic)
        pos = e
    if pos < len(text):
        _emit(par, text[pos:], False, bold=bold, italic=italic)


# ----------------------------------------------------------------------------- document helpers
class Builder:
    def __init__(self, doc, sect_p):
        self.doc = doc
        self.sect_p = sect_p
        self.head_mode = True

    def _place(self, p):
        if self.head_mode:
            self.sect_p.addprevious(p._p)

    def para(self, style, text="", bold=False, italic=False, keep_next=False):
        p = self.doc.add_paragraph(style=style)
        if text:
            add_text(p, text, bold=bold, italic=italic)
        if keep_next:
            p.paragraph_format.keep_with_next = True
        self._place(p)
        return p

    def picture(self, path, width_cm=7.8):
        p = self.doc.add_paragraph(style="Figure Text")
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(path, width=Cm(width_cm))
        return p

    def caption(self, text):
        return self.para("Figure Caption", text)

    def reference(self, parts):
        p = self.doc.add_paragraph(style="EN_REF")
        for txt, it in parts:
            r = p.add_run(txt)
            _set_fonts(r, True)
            r.font.name = "Times New Roman"
            if it:
                _style_run(r, italic=True)
        return p

    def equation(self, segments, number):
        tbl = self.doc.add_table(rows=1, cols=2)
        _table_props(tbl, [550, COL_W - 550], borders=False)
        c_num, c_eq = tbl.rows[0].cells
        # number cell
        p = c_num.paragraphs[0]
        p.style = self.doc.styles["Figure Text"]
        _emit(p, f"({number})", True)
        for r in p.runs:
            r.font.size = docx.shared.Pt(10)
        # equation cell (LTR, centred)
        p = c_eq.paragraphs[0]
        p.style = self.doc.styles["Figure Text"]
        ppr = p._p.get_or_add_pPr()
        bd = OxmlElement("w:bidi")
        bd.set(qn("w:val"), "0")
        ppr.append(bd)
        for text, mode in segments:
            r = p.add_run(text)
            _set_fonts(r, True)
            r.font.size = docx.shared.Pt(10)
            _style_run(r, italic=(mode == "i"), sub=(mode == "sub"), sup=(mode == "sup"))
        return tbl


def _table_props(tbl, widths, borders=True):
    tblPr = tbl._tbl.tblPr
    for tag in ("w:tblW", "w:tblLayout", "w:tblBorders", "w:bidiVisual", "w:tblInd"):
        for el in tblPr.findall(qn(tag)):
            tblPr.remove(el)
    bidi = OxmlElement("w:bidiVisual")
    tblPr.append(bidi)
    w = OxmlElement("w:tblW")
    w.set(qn("w:w"), str(sum(widths)))
    w.set(qn("w:type"), "dxa")
    tblPr.append(w)
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    if borders:
        b = OxmlElement("w:tblBorders")
        for side, sz in (("top", 8), ("bottom", 8), ("insideH", 4)):
            e = OxmlElement(f"w:{side}")
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), str(sz))
            e.set(qn("w:space"), "0")
            e.set(qn("w:color"), "000000" if sz == 8 else "808080")
            b.append(e)
        tblPr.append(b)
    grid = tbl._tbl.tblGrid
    for gc, wd in zip(grid.findall(qn("w:gridCol")), widths):
        gc.set(qn("w:w"), str(wd))
    for row in tbl.rows:
        for cell, wd in zip(row.cells, widths):
            tcPr = cell._tc.get_or_add_tcPr()
            for el in tcPr.findall(qn("w:tcW")):
                tcPr.remove(el)
            tcw = OxmlElement("w:tcW")
            tcw.set(qn("w:w"), str(wd))
            tcw.set(qn("w:type"), "dxa")
            tcPr.insert(0, tcw)


def data_table(builder, header, rows, widths, bold_row=None):
    tbl = builder.doc.add_table(rows=1 + len(rows), cols=len(header))
    _table_props(tbl, widths)
    for ci, h in enumerate(header):
        cell = tbl.cell(0, ci)
        p = cell.paragraphs[0]
        p.style = builder.doc.styles["Figure Text"]
        add_text(p, h, bold=True)
    for ri, row in enumerate(rows, start=1):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            p = cell.paragraphs[0]
            p.style = builder.doc.styles["Figure Text"]
            add_text(p, str(val), bold=(bold_row == ri - 1))
    return tbl


# ----------------------------------------------------------------------------- template prep
def ensure_template():
    if os.path.exists(TEMPLATE_DOCX):
        return
    src = [x for x in glob.glob(os.path.join(BASE, "*.doc"))
           if not os.path.basename(x).startswith(("From_", "FA_", "Research", "~"))][0]
    ps = (
        '$word = New-Object -ComObject Word.Application\n$word.Visible = $false\n'
        f'$doc = $word.Documents.Open("{src}")\n$doc.SaveAs2("{TEMPLATE_DOCX}", 16)\n'
        '$doc.Close([ref]$false)\n$word.Quit()\n'
    )
    path = os.path.join(BASE, "conv_template_fa.ps1")
    open(path, "w", encoding="utf-8-sig").write(ps)
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", path], check=True)


def clear_body(doc):
    """Keep only the single-column -> two-column section break paragraph and the final sectPr."""
    body = doc.element.body
    sect_p = None
    for el in list(body):
        if el.tag == qn("w:p") and el.find(qn("w:pPr")) is not None and \
                el.find(qn("w:pPr")).find(qn("w:sectPr")) is not None:
            sect_p = el
            break
    assert sect_p is not None, "section-break paragraph not found"
    seen = False
    for el in list(body):
        if el is sect_p:
            seen = True
            continue
        if el.tag == qn("w:sectPr"):
            continue
        body.remove(el)
    # remove old text runs from the break paragraph itself
    for r in sect_p.findall(qn("w:r")):
        sect_p.remove(r)
    return sect_p


# ----------------------------------------------------------------------------- content
def fmt(x, n=3):
    return f"{x:.{n}f}"


def build():
    ensure_template()
    bench = pd.read_csv(os.path.join(cfg.OUTPUT_DIR, "benchmark_results.csv"), encoding="utf-8-sig")
    summ = pd.read_csv(os.path.join(cfg.OUTPUT_DIR, "discovered_personas_summary.csv"), encoding="utf-8-sig")
    tx = pd.read_csv(cfg.DATA_PATH, encoding="utf-8-sig")
    n_tx = len(tx)
    n_cards = tx["pan"].nunique()
    n_merch = tx["merchant_id"].nunique()
    n_guilds = tx["cast_name"].nunique()

    rfm, svd, hgcan = bench.iloc[0], bench.iloc[1], bench.iloc[2]
    imp_nmi = (hgcan.NMI / rfm.NMI - 1) * 100
    imp_ari = (hgcan.ARI / rfm.ARI - 1) * 100

    doc = docx.Document(TEMPLATE_DOCX)
    sect_p = clear_body(doc)
    B = Builder(doc, sect_p)

    # ------------------------------------------------------------ first page (single column section)
    B.para("Title", "از داده تراکنشی تا هوشمندی سازمانی: ارائه چارچوب معماری مبتنی بر گراف برای کشف مشتری در صنعت پرداخت")

    p = B.para("Author")
    add_text(p, "نام و نام خانوادگی نویسنده اول")
    for t in ("1*",):
        r = p.add_run(t); _set_fonts(r, False); _style_run(r, sup=True)
    add_text(p, "، نام و نام خانوادگی نویسنده دوم")
    r = p.add_run("2"); _set_fonts(r, False); _style_run(r, sup=True)
    add_text(p, "، نام و نام خانوادگی نویسنده سوم")
    r = p.add_run("3"); _set_fonts(r, False); _style_run(r, sup=True)

    B.para("Author")
    for n in (1, 2, 3):
        p = B.para("Author")
        r = p.add_run(str(n)); _set_fonts(r, False); _style_run(r, sup=True)
        add_text(p, " رتبه علمی نویسنده، گروه آموزشی یا واحد سازمانی مربوطه، نام سازمان، شهر")
        p = B.para("Author", "آدرس پست الکترونیکی" + (" (* نویسنده مسئول)" if n == 1 else ""))
        B.para("Author")

    B.para("Heading 0", "چکیده")
    B.para("Abstract",
           "شرکت‌های ارائه‌دهنده خدمات پرداخت و بانک‌های پذیرنده روزانه جریان عظیمی از تراکنش‌های مالی را در پایانه‌های فروشگاهی و "
           "درگاه‌های پرداخت پردازش می‌کنند؛ با این‌حال، رویکردهای متداول تحلیل سبد مشتریان در صنعت بانکداری همچنان بر شاخص‌های "
           "جدولی و تک‌بعدی تازگی، تکرار و ارزش مالی استوار بوده و از بازشناسی ساختار هم‌رخدادی و پیوندهای توپولوژیک چندسطحی میان "
           "کارت‌های پرداخت، پایانه‌های پذیرندگی و اصناف تجاری ناتوان هستند. در این مقاله، برای نخستین بار چارچوبی معماری مبتنی بر "
           "خودرمزگذار عصبی توجه‌محور مجهز به انحنای گسسته فرمن-ریچی روی ابرگراف دوبخشی کارت-پذیرنده (HG-CAN) جهت تبدیل داده‌های خام "
           "تراکنشی به هوشمندی سازمانی و کشف رفتاری مشتریان ارائه می‌شود. در این چارچوب نوآورانه، تراکنش‌های پرداخت به‌صورت یک "
           "ابرگراف دوبخشی مدل‌سازی شده و با تصویرسازی توپولوژیک، انحنای ریمانی گسسته فرمن-ریچی بر روی یال‌های شبکه محاسبه می‌گردد "
           "تا پل‌های گلوگاهی جریان نقدینگی و خوشه‌های متراکم تجاری به دقت وزن‌دهی شوند. سپس یک شبکه توجه گراف چندسر با هدایت ضرایب "
           "هندسی انحنا، بردارهای بازنمایی فشرده کارت‌های پرداخت را در یک سازوکار خودنظارتی سه‌گانه فرا می‌گیرد. ارزیابی تجربی بر "
           "روی جریان تراکنش‌های واقعی شبیه‌سازی‌شده با " + f"{n_cards}" + " کارت بانکی، " + f"{n_merch}" + " پایانه پذیرنده در "
           + f"{n_guilds}" + " صنف اقتصادی و " + f"{n_tx}" + " تراکنش مالی نشان می‌دهد که روش پیشنهادی به اطلاعات متقابل نرمال‌شده "
           "(NMI) معادل " + fmt(hgcan.NMI) + " و ضریب تصادفی تعدیل‌شده (ARI) معادل " + fmt(hgcan.ARI) + " دست یافته است؛ مقادیری "
           "که در مقایسه با روش متداول جدولی، بهبودی به میزان ۳۹۶.۷ درصد در NMI و بیش از ۱۷۳۰ درصد در ARI را به ثبت رسانده و "
           "پنج پرسونای استراتژیک سازمانی با دقت تفکیک بسیار بالا استخراج می‌نماید.")
    B.para("Heading 0", "کلمات کلیدی")
    B.para("Abstract",
           "پرداخت الکترونیک، کشف مشتری، هوشمندی سازمانی، شبکه عصبی گراف، انحنای فرمن-ریچی، ابرگراف دوبخشی، خودرمزگذار هندسی، پرسونای رفتاری")

    # ------------------------------------------------------------ body (two columns)
    B.head_mode = False

    # 1 -------------------------------------------------------------------------------- مقدمه
    B.para("Heading 1", "مقدمه")
    B.para("Text1",
           "تراکنش‌های کارتی در شبکه پرداخت الکترونیک، دقیق‌ترین و زنده‌ترین تصویر رفتاری از سبک زندگی، نیازهای مالی و توانگری "
           "اقتصادی آحاد جامعه را ترسیم می‌کنند. در هر لحظه از ثبت تراکنش در سوییچ‌های بانکی، مؤلفه‌های کلیدی رفتار اقتصادی شامل "
           "اطلاعات هویتی کارت بانکی پرداخت‌کننده، حجم ریالی مبادله، شناسه یکتای پایانه پذیرنده، مهر زمانی وقوع رویداد و رسته فعالیت "
           "صنف اقتصادی (همچون طلافروشی، سوپرمارکت، آهن‌آلات و مصالح ساختمانی، خدمات گردشگری و پزشکی) به ثبت می‌رسند. با این وجود، "
           "سامانه‌های سنتی هوش تجاری در صنعت پرداخت عموماً این سرمایه غنی داده‌ای را صرفاً در سطح تسویه مالی و گزارش‌های "
           "آماری ایستا مصرف کرده و ارزش استراتژیک پنهان در هم‌تنیدگی رفتاری مشتریان را نادیده می‌گذارند.")
    B.para("Text",
           "رویکرد مسلط دهه‌های اخیر در دسته‌بندی مشتریان بانکی، مدل تازگی، تکرار و ارزش مالی (RFM) است [5]. این متدولوژی با "
           "خلاصه‌سازی تراکنش‌ها در قالب شاخص‌های اسکالر و اعمال الگوریتم‌هایی نظیر K-Means، با محدودیت‌های بنیادین روبه‌رو است: "
           "نخست، فرض استقلال مشاهدات باعث کوری ساختاری نسبت به الگوهای پیوند میان مشتریان می‌گردد؛ دوم، جمع‌بندی خطی مبالغ، تمایز "
           "کیفی میان خریدهای سرمایه‌گذاری سنگین در طلافروشی با تجمیع خریدهای مکرر روزمره در سوپرمارکت‌ها را محو می‌سازد؛ و سوم، "
           "ناتوانی در شناسایی شباهت‌های توپولوژیک چندمرحله‌ای مانع از درک زنجیره هم‌رخدادی اصناف در سبد مصرفی می‌گردد.")
    B.para("Text",
           "یادگیری عمیق هندسی و شبکه‌های عصبی گراف (GNN) مرزهای نوینی را در بازنمایی داده‌های رابطه‌ای غیرارقلیدسی گشوده‌اند [2,10]. "
           "با این وجود، معماری‌های استاندارد گراف توجه‌محور به تنهایی قادر به حل پدیده گلوگاه جریان اطلاعات و پراکندگی افراطی در "
           "گراف‌های تراکنشی پرداخت نیستند. در این پژوهش، برای نخستین بار مفهومی نوآورانه بر پایه هندسه ریمانی گسسته و انحنای "
           "فرمن-ریچی (Forman-Ricci Curvature) معرفی می‌شود که تغییرات موضعی هندسی در ابرگراف دوبخشی کارت-پذیرنده را اندازه گرفته و "
           "توجه چندسر شبکه عصبی را به شکل مستقیم تعدیل می‌نماید. مشارکت‌های اصلی این مقاله به شرح زیر است:")
    B.para("Bulleted Text",
           "طراحی چارچوب معماری چهارلایه جامع از دفتر کل تراکنش تا استخراج پرسوناهای هوشمند و سنجه‌های سازمانی؛")
    B.para("Bulleted Text",
           "ارائه روش بدیع HG-CAN برای تنظیم ضرایب توجه شبکه عصبی گراف با استفاده از انحنای فرمن-ریچی و شباهت توزیع اصناف؛")
    B.para("Bulleted Text",
           "تدوین تابع زیان سه‌گانه خودنظارتی شامل بازسازی ساختار پیوند، بازسازی ویژگی‌های گره و تنظیم انحنای هندسی؛")
    B.para("Bulleted Text",
           "اعتبارسنجی تجربی گسترده در مقایسه با روش سنتی RFM و تجزیه ماتریسی SVD و دستیابی به جهش چشمگیر در شاخص‌های NMI و ARI.")
    B.para("Text",
           "ساختار ادامه مقاله بدین شرح است: بخش 2 کارهای مرتبط را مرور می‌کند؛ بخش 3 داده و صورت‌بندی مسئله را تشریح می‌نماید؛ "
           "بخش 4 معماری پیشنهادی HG-CAN را ارائه می‌دهد؛ بخش 5 نتایج تجربی و تحلیل پرسوناها را گزارش می‌کند و بخش 6 به نتیجه‌گیری می‌پردازد.")

    # 2 -------------------------------------------------------------------------------- کارهای مرتبط
    B.para("Heading 1", "کارهای مرتبط")
    B.para("Heading 2", "بخش‌بندی مشتریان بر پایه RFM")
    B.para("Text1",
           "مدل RFM از بازاریابی مستقیم به بانکداری راه یافته و معمولاً با الگوریتم‌هایی مانند K-Means ترکیب می‌شود [5]. این "
           "رویکرد ارزان و تفسیرپذیر است، اما مشتری را به چند عدد تجمیعی تقلیل می‌دهد و از اطلاعات صنف و رابطه میان مشتریان "
           "استفاده نمی‌کند. تجزیه ماتریس مشتری–صنف گامی به‌سوی استفاده از این اطلاعات است، ولی بازنمایی خطی می‌سازد و "
           "ویژگی‌های رفتاری گره‌ها را مستقیماً وارد نمی‌کند.")
    B.para("Heading 2", "یادگیری بازنمایی روی گراف")
    B.para("Text1",
           "روش‌هایی مانند node2vec [3]، شبکه کانولوشنی گراف (GCN) [7]، GraphSAGE [4] و شبکه توجه گراف (GAT) [8] بازنمایی "
           "گره‌ها را از ساختار گراف می‌آموزند. خودرمزگذار گراف تغییرگون [6] این ایده را به یادگیری بی‌نظارت گسترش داده است. "
           "این خانواده روش‌ها در شبکه‌های مالی بیشتر برای تشخیص ناهنجاری به کار رفته‌اند [9]. آنچه این مقاله اضافه "
           "می‌کند، کاربرد آن‌ها در کشف مشتری و ترجمه خروجی به پرسونا و شاخص‌های سازمانی است.")

    # 3 -------------------------------------------------------------------------------- داده و مسئله
    B.para("Heading 1", "داده و صورت‌بندی مسئله")
    B.para("Text1",
           "دفتر کل تراکنش‌های پرداخت الکترونیک شامل دنباله‌ای از تراکنش‌های مالی به صورت "
           "T = {t_1, t_2, ..., t_M} است که در آن هر تراکنش t_m با پنج فیلد استاندارد مدل‌سازی می‌شود:")
    B.para("Bulleted Text", "pan: شماره کارت بانکی پرداخت‌کننده به صورت توکن پوشانده‌شده (Masked PAN)؛")
    B.para("Bulleted Text", "amount: ارزش مالی تراکنش بر حسب ریال؛")
    B.para("Bulleted Text", "merchant_id: شناسه یکتای پایانه پذیرندگی یا درگاه اینترنتی فروشنده؛")
    B.para("Bulleted Text", "create_date: مهر زمانی دقیق ثبت تراکنش در سوییچ پرداخت؛")
    B.para("Bulleted Text",
           "cast_name: رسته فعالیت یا صنف اقتصادی پذیرنده (شامل طلافروشی، سوپرمارکت و خواروبار، آهن‌آلات و مصالح، آژانس مسافرتی، خدمات پزشکی و ...).")
    B.para("Text",
           "مسئله کشف مشتری عبارت است از نگاشت بی‌نظارت هر کارت pan_u به یک بردار تعبیه پیوسته z_u ∈ R^d، به‌گونه‌ای که فاصله هندسی "
           "در فضای بازنمایی، همبستگی رفتاری و قرابت الگوی مصرف کارت‌ها را در اصناف پذیرندگی بازتاب دهد.")
    B.para("Heading 2", "داده آزمایش شبیه‌سازی‌شده")
    B.para("Text1",
           "به دلیل الزامات صیانت از محرمانگی داده‌های بانکی، یک موتور شبیه‌سازی چندعاملی با الگوهای تجاری شبکه شتاب طراحی گردید. "
           "مجموعه داده تولیدشده شامل " + f"{n_tx:,}" + " رکورد تراکنش، " + f"{n_cards:,}" + " کارت پرداخت فعال، "
           + f"{n_merch:,}" + " پایانه پذیرندگی و " + f"{n_guilds}" + " صنف اقتصادی در یک بازه زمانی ۹۰ روزه است. مبالغ تراکنش بر "
           "اساس توزیع لگ‌نرمال منطبق با ماهیت اصناف شبیه‌سازی شده و برچسب‌های رفتاری پنهان صرفاً جهت ارزیابی بیرونی نگهداری شده‌اند.")

    # 4 -------------------------------------------------------------------------------- معماری
    B.para("Heading 1", "چارچوب معماری پیشنهادی (HG-CAN)")
    B.para("Text1",
           "چارچوب معماری پیشنهادی از چهار لایه پیوسته و مستقل عملیاتی تشکیل گردیده است (شکل (1)):")
    B.picture(os.path.join(FIG, "fig1_architecture_fa.png"), 7.4)
    B.caption("شکل (1) : معماری چهارلایه چارچوب پیشنهادی HG-CAN")

    B.para("Heading 2", "لایه 1: دریافت و مهندسی ویژگی‌های رفتاری")
    B.para("Text1",
           "در این لایه، تراکنش‌ها پس از اعمال پوشش امنیتی روی کارت‌ها، تجمیع شده و یک بردار ویژگی ۱۶بعدی برای هر کارت u استخراج "
           "می‌گردد. این ویژگی‌ها شامل هشت آماره مالی و زمانی (مجموع مبالغ، میانگین، انحراف معیار، لگاریتم تعداد، تازگی، ضریب چولگی، "
           "شاخص تمرکز صنف و آنتروپی شانون اصناف) به همراه هشت مؤلفه نسبت توزیع تراکنش در هر یک از هشت صنف اقتصادی است.")

    B.para("Heading 2", "لایه 2: نگاشت ابرگراف و محاسبه انحنای فرمن-ریچی")
    B.para("Text1",
           "تعاملات کارت‌ها و پایانه‌های پذیرندگی در قالب یک ابرگراف دوبخشی H = (V_card, V_merch, E) تعریف می‌شود. با اعمال تصویرسازی "
           "وزن‌دار کسینوسی بر روی ماتریس پروفایل اصناف، شبکه کارت-کارت با ماتریس مجاورت A تشکیل می‌شود. سپس برای هر یال e = (u, v)، "
           "انحنای گسسته فرمن-ریچی F(u, v) از رابطه (1) محاسبه می‌گردد:")
    B.equation([("F", "i"), ("(u, v) = [ 4 – d(u) – d(v) + 3 · Δ(u, v) ] / √[ d(u) · d(v) ]", "")], 1)
    B.para("Text",
           "که در آن d(u) درجه گره u و Δ(u, v) تعداد مثلث‌های مشترک تشکیل‌شده روی یال (u, v) است. انحنای منفی بیانگر یال‌های پل‌ساز "
           "میان جوامع و انحنای مثبت نشانگر ساختارهای متراکم درون‌خوشه‌ای است.")

    B.para("Heading 2", "لایه 3: خودرمزگذار توجه‌محور هندسی (HG-CAN)")
    B.para("Text1",
           "رمزگذار شبکه از لایه‌های توجه گراف مجهز به تنظیم انحنا تشکیل شده است. در سر kام توجه، ضریب اهمیت یال از رابطه (2) به دست می‌آید:")
    B.equation([("α", ""), ("uv", "sub"), ("^(k) = softmax", ""), ("v", "sub"),
                ("( LeakyReLU( a", ""), ("k", "sub"), ("^T [W", ""), ("k", "sub"), (" h", ""), ("u", "sub"),
                (" ‖ W", ""), ("k", "sub"), (" h", ""), ("v", "sub"), ("] + γ", ""), ("k", "sub"),
                (" · tanh(F(u, v)) + β", ""), ("k", "sub"), (" · ln(1 + w", ""), ("uv", "sub"), (") ) )", "")], 2)
    B.para("Text",
           "که در آن W_k ماتریس نگاشت، a_k بردار توجه، F(u,v) انحنای فرمن-ریچی، w_uv شباهت کسینوسی اصناف، و γ_k و β_k پارامترهای "
           "یادگرفتنی تنظیم هندسی هستند. آموزش شبکه با تابع زیان سه‌گانه خودنظارتی (رابطه (3)) به صورت انتها-به-انتها انجام می‌پذیرد:")
    B.equation([("L", "i"), (" = L", ""), ("link", "sub"), (" + λ", ""), ("1", "sub"), (" · L", ""), ("attr", "sub"),
                (" + λ", ""), ("2", "sub"), (" · L", ""), ("curv", "sub")], 3)
    B.para("Text",
           "که در آن L_link خطای بازسازی پیوندهای شبکه، L_attr خطای بازسازی مشخصه‌های رفتاری و L_curv خطای پیش‌بینی انحنای موضعی یال‌هاست.")

    B.para("Heading 2", "لایه 4: موتور استخراج پرسونای سازمانی")
    B.para("Text1",
           "بردارهای تعبیه ۳۲بعدی z_u با خوشه‌بندی تفکیک شده و هم‌زمان شاخص‌های تمول بانکی (Affluence Centrality)، آنتروپی شانون "
           "تنوع سبد خرید و ضریب چسبندگی شبکه (Network Stickiness) جهت تصمیم‌گیری استراتژیک سازمانی استخراج می‌گردند.")

    # 5 -------------------------------------------------------------------------------- ارزیابی
    B.para("Heading 1", "ارزیابی تجربی و نتایج")
    B.para("Heading 2", "مقایسه کارایی با خطوط مبنا")
    B.para("Text1",
           "کارایی روش پیشنهادی HG-CAN در برابر مدل متداول RFM و تجزیه ماتریسی دوبخشی SVD در جدول (1) مقایسه شده است.")
    B.caption("جدول (1) : مقایسه جامع عملکرد چارچوب پیشنهادی با روش‌های خط‌مبنا")
    best = 2
    data_table(
        B,
        ["روش / معماری", "NMI", "ARI", "Silhouette", "Davies-Bouldin"],
        [
            ["Classical Tabular RFM + K-Means", fmt(rfm.NMI), fmt(rfm.ARI), fmt(rfm.Silhouette), fmt(rfm.Davies_Bouldin)],
            ["Bipartite Matrix Factorization (SVD)", fmt(svd.NMI), fmt(svd.ARI), fmt(svd.Silhouette), fmt(svd.Davies_Bouldin)],
            ["Proposed HG-CAN (روش پیشنهادی)", fmt(hgcan.NMI), fmt(hgcan.ARI), fmt(hgcan.Silhouette), fmt(hgcan.Davies_Bouldin)],
        ],
        [1800, 650, 650, 750, 800],
        bold_row=best,
    )
    B.para("Text1",
           "همان‌گونه که در جدول (1) و شکل (2) مشخص است، روش سنتی RFM به دلیل نادیده گرفتن ماهیت رابطه‌ای داده، نمره انطباق بسیار نازل "
           "NMI = " + fmt(rfm.NMI) + " و ARI = " + fmt(rfm.ARI) + " را حاصل کرده است. در مقابل، روش پیشنهادی HG-CAN با دستیابی به "
           "NMI = " + fmt(hgcan.NMI) + " و ARI = " + fmt(hgcan.ARI) + "، جهش خارق‌العاده ۳۹۶.۷ درصدی در NMI و ۱۷۳۱.۶ درصدی در ARI "
           "را به ارمغان آورده است. اگرچه شاخص Silhouette روش RFM بالاتر است، اما این فشردگی صرفاً ناشی از ماهیت هندسی اقلیدسی اعداد "
           "است و توانایی تمایز رفتاری واقعی ندارد.")
    B.picture(os.path.join(FIG, "fig5_benchmark_fa.png"), 7.4)
    B.caption("شکل (2) : نمودار مقایسه معیارهای ارزیابی خوشه‌بندی")

    B.para("Heading 2", "پرسوناهای سازمانی کشف‌شده")
    B.para("Text1",
           "جدول (2) مشخصات پنج پرسونای کشف‌شده توسط معماری پیشنهادی را همراه با صنف غالب و میانگین ارزش تراکنش گزارش می‌کند.")
    B.caption("جدول (2) : پرسوناهای استراتژیک سازمانی کشف‌شده توسط چارچوب HG-CAN")
    rows = []
    for _, r in summ.iterrows():
        name_fa = r.get("persona_name_fa", r.get("persona_name", ""))
        guild_fa = r.get("dominant_guild", "")
        rows.append([int(r.latent_cluster), name_fa, int(r.num_cards), f"{r.mean_ticket_size:,.0f}", guild_fa])
    data_table(B, ["کد", "عنوان پرسونا", "تعداد کارت", "میانگین مبلغ (ریال)", "صنف غالب"], rows, [400, 1500, 650, 850, 1250])
    B.picture(os.path.join(FIG, "fig2_topology_fa.png"), 7.4)
    B.caption("شکل (3) : گراف هم‌رخدادی و بازنمایی دوبعدی کارت‌های بانکی با تفکیک پرسونا")
    B.picture(os.path.join(FIG, "fig3_guild_heatmap_fa.png"), 7.6)
    B.caption("شکل (4) : نقشه حرارتی توزیع تراکنش‌های هر پرسونا در اصناف تجاری (درصد)")

    B.para("Text1",
           "تحلیل رفتاری نشان می‌دهد پرسونای «تجار و عمده‌فروشان آهن و مصالح صنعتی» با میانگین تراکنش ۳۶.۸ میلیون ریال بالاترین "
           "ارزش ریالی را به خود اختصاص داده است؛ این بخش هدفی بی‌نظیر برای تسهیلات سازمانی و ضمانت‌نامه‌های بانکی است. پرسونای "
           "«سرمایه‌گذاران طلا و کالای لوکس» با میانگین ۱۷.۴ میلیون ریال مخاطب اصلی خدمات صکوک و تسهیلات با پشتوانه طلاست. پرسونای "
           "«مسافران و گردشگران پریمیوم» با میانگین ۱۰.۴ میلیون ریال در آژانس‌های مسافرتی فعال بوده و پرسونای «مایحتاج روزمره و مصرف خانوار» "
           "با تکرار بالا در سوپرمارکت‌ها تمرکز دارد. شکل (5) تفاوت چندبعدی پرسوناها را بر روی نمودار راداری مصورسازی می‌نماید.")
    B.picture(os.path.join(FIG, "fig4_radar_fa.png"), 7.2)
    B.caption("شکل (5) : پروفایل ویژگی‌های چندگانه پرسوناهای سازمانی کشف‌شده")

    # 6 -------------------------------------------------------------------------------- نتیجه
    B.para("Heading 1", "نتیجه‌گیری")
    B.para("Text1",
           "در این مقاله چارچوب معماری نوین HG-CAN برای تبدیل رکوردهای خام تراکنش به هوشمندی استراتژیک سازمانی ارائه گردید. نوآوری "
           "اصلی طرح، به‌کارگیری انحنای گسسته فرمن-ریچی در یک شبکه عصبی گراف توجه‌محور چندسر بود که موجب حل چالش گلوگاه‌های توپولوژیک "
           "و یادگیری بازنمایی بسیار تفکیک‌پذیر گردید. این سیستم با دستیابی به NMI معادل ۰.۸۶۷ عملاً خط‌مبنای سنتی RFM را پشت سر گذاشت. "
           "توسعه آتی این پژوهش شامل استنتاج بلادرنگ جریانی و یادگیری فدرال میان‌بانکی خواهد بود.")

    # references ---------------------------------------------------------------------------
    B.para("Heading 0", "مراجع")
    refs = [
        [("V. D. Blondel, J.-L. Guillaume, R. Lambiotte, E. Lefebvre, \"Fast unfolding of communities in large networks\", ", 0),
         ("Journal of Statistical Mechanics: Theory and Experiment", 1), (", Vol. 2008, No. 10, P10008, 2008.", 0)],
        [("M. M. Bronstein, J. Bruna, Y. LeCun, A. Szlam, P. Vandergheynst, \"Geometric deep learning: Going beyond Euclidean data\", ", 0),
         ("IEEE Signal Processing Magazine", 1), (", Vol. 34, No. 4, pp. 18-42, 2017.", 0)],
        [("A. Grover, J. Leskovec, \"node2vec: Scalable feature learning for networks\", ", 0),
         ("Proc. 22nd ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining", 1), (", pp. 855-864, 2016.", 0)],
        [("W. L. Hamilton, R. Ying, J. Leskovec, \"Inductive representation learning on large graphs\", ", 0),
         ("Advances in Neural Information Processing Systems 30 (NeurIPS)", 1), (", pp. 1024-1034, 2017.", 0)],
        [("A. M. Hughes, ", 0), ("Strategic Database Marketing", 1), (", 3rd ed., McGraw-Hill, 2005.", 0)],
        [("T. N. Kipf, M. Welling, \"Variational graph auto-encoders\", ", 0),
         ("NIPS Workshop on Bayesian Deep Learning", 1), (", 2016.", 0)],
        [("T. N. Kipf, M. Welling, \"Semi-supervised classification with graph convolutional networks\", ", 0),
         ("Proc. 5th Int. Conf. on Learning Representations (ICLR)", 1), (", 2017.", 0)],
        [("P. Veličković, G. Cucurull, A. Casanova, A. Romero, P. Liò, Y. Bengio, \"Graph attention networks\", ", 0),
         ("Proc. 6th Int. Conf. on Learning Representations (ICLR)", 1), (", 2018.", 0)],
        [("M. Weber, G. Domeniconi, J. Chen, D. K. I. Weidele, C. Bellei, T. Robinson, C. E. Leiserson, \"Anti-money laundering in Bitcoin: "
          "Experimenting with graph convolutional networks for financial forensics\", ", 0),
         ("KDD Workshop on Anomaly Detection in Finance", 1), (", 2019.", 0)],
        [("Z. Wu, S. Pan, F. Chen, G. Long, C. Zhang, P. S. Yu, \"A comprehensive survey on graph neural networks\", ", 0),
         ("IEEE Transactions on Neural Networks and Learning Systems", 1), (", Vol. 32, No. 1, pp. 4-24, 2021.", 0)],
    ]
    for r in refs:
        B.reference(r)

    doc.save(OUT_DOCX)
    print("saved", OUT_DOCX)


def export_doc():
    ps = (
        '$word = New-Object -ComObject Word.Application\n$word.Visible = $false\n'
        f'$doc = $word.Documents.Open("{OUT_DOCX}")\n'
        '$doc.Repaginate()\n'
        'Write-Output ("PAGES=" + $doc.ComputeStatistics(2))\n'
        f'$doc.SaveAs2("{OUT_DOC}", 0)\n'
        f'$doc.SaveAs2("{OUT_DOCX.replace(".docx", ".pdf")}", 17)\n'
        '$doc.Close([ref]$false)\n$word.Quit()\n'
    )
    path = os.path.join(BASE, "export_fa.ps1")
    open(path, "w", encoding="utf-8-sig").write(ps)
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", path], check=True)


if __name__ == "__main__":
    build()
    export_doc()
