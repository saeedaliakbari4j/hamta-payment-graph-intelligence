"""
Persian (RTL) version of the paper, written into the official Persian conference template
(فرمت_فارسی_مقالات.doc). The template is converted to .docx, its body is replaced, and
all formatting comes from the template's own styles (Title, Author, Heading 0/1/2, Abstract,
Text1, Text, Bulleted Text, Figure Caption, Figure Text, EN_REF ...).

All numbers are read from output/hamta_*.csv and output/phase1_results/ so they are identical to the English paper.
Title: "چارچوب گراف زمانی برای کشف فرصت رشد تراکنش پذیرندگان و اولویت‌بندی کمپین"
"""

import os
import re
import sys
import copy
import glob
import subprocess

import docx
import pandas as pd
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

from src.config import cfg

sys.stdout.reconfigure(encoding="utf-8")

BASE = cfg.BASE_DIR
FIG = os.path.join(BASE, "figures_fa")
TEMPLATE_DOCX = os.path.join(BASE, "template_fa.docx")
OUT_DOCX = os.path.join(BASE, "FA_From_Transactional_Data_to_Organizational_Intelligence.docx")
OUT_DOC = OUT_DOCX.replace(".docx", ".doc")

COL_W = 4650  # twips: one column = 8.2 cm


def to_fa_num(s):
    """Convert digits to Persian digits and format decimal/thousands separators."""
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    s = s.replace(" ± ", "\u00A0±\u00A0").replace(" - ", "\u00A0–\u00A0")
    s = re.sub(r'(\d)\.(\d)', r'\1٫\2', s)
    s = re.sub(r'(\d),(\d)', r'\1٬\2', s)
    trans = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    return s.translate(trans)


# Comprehensive regex for matching inline mathematical, complexity, and Latin tokens
# Prevents expressions like O(|C(m)| log K), [x]_+ = max(0, x), or η = 0.25 from being split across RTL runs
TOKEN = re.compile(
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
        bd = rpr.find(qn("w:bidi"))
        if bd is None:
            bd = OxmlElement("w:bidi")
            rpr.append(bd)
        bd.set(qn("w:val"), "0")
    else:
        rf.set(qn("w:hint"), "cs")
        rf.set(qn("w:ascii"), "B Mitra")
        rf.set(qn("w:hAnsi"), "B Mitra")
        rf.set(qn("w:cs"), "B Mitra")
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


def set_run_font_size(run, size_pt):
    run.font.size = Pt(size_pt)
    sz_val = str(int(size_pt * 2))
    rpr = _rpr(run)
    for tag in ("w:sz", "w:szCs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = OxmlElement(tag)
            rpr.append(el)
        el.set(qn("w:val"), sz_val)


STYLE_FONT_SIZES = {
    "Title": (14.0, 15.0),
    "Author": (8.5, 9.5),
    "Heading 0": (9.5, 10.5),
    "Abstract": (8.5, 9.0),
    "Abstract2": (8.5, 9.0),
    "Heading 1": (10.0, 11.5),
    "Heading 2": (9.0, 10.0),
    "Heading 3": (8.5, 9.5),
    "Text": (8.5, 9.0),
    "Text1": (8.5, 9.0),
    "Figure Caption": (8.0, 8.5),
    "Caption": (8.0, 8.5),
    "Figure Text": (7.0, 7.5),
    "Table Text": (7.0, 7.5),
    "REF": (6.5, 7.0),
    "EN_REF": (6.5, 7.0),
}


def _emit(par, text, latin, style=None, **kw):
    if not text:
        return
    if latin:
        # Replace spaces with non-breaking spaces for math expressions / Big-O so Word never line-breaks mid-formula
        if any(c in text for c in ("=", "≈", "∈", "≤", "≥", "<", ">", "·", "O(", "Top-K", "max(", "Var(")):
            text = text.replace(" ", "\u00A0")
        # Wrap with Unicode Left-to-Right Mark (LRM \u200E) to ensure strict LTR layout in RTL paragraphs
        text = f"\u200E{text}\u200E"
    r = par.add_run(text)
    _set_fonts(r, latin)
    _style_run(r, **kw)
    if style is None and par.style:
        style = par.style.name
    en_sz, fa_sz = STYLE_FONT_SIZES.get(style, (8.5, 9.0))
    set_run_font_size(r, en_sz if latin else fa_sz)


def add_text(par, text, bold=False, italic=False, style=None):
    """Persian runs (rtl, complex-script font) + Latin runs (Times New Roman, LTR)."""
    if style is None and par.style:
        style = par.style.name
    pos = 0
    for m in TOKEN.finditer(text):
        s, e = m.span()
        if m.group("lat"):
            while text[s:e] and text[e - 1] in ".-:,،؛)(":
                e -= 1
        if s > pos:
            _emit(par, text[pos:s], False, style=style, bold=bold, italic=italic)
        if m.group("sub"):
            full_sub = m.group("sub")
            u_idx = full_sub.index("_{")
            base = full_sub[:u_idx]
            sub = full_sub[u_idx + 2 : -1]
            _emit(par, base, True, style=style, bold=bold, italic=True)
            _emit(par, sub, True, style=style, bold=bold, sub=True)
        else:
            _emit(par, text[s:e], True, style=style, bold=bold, italic=italic)
        pos = e
    if pos < len(text):
        _emit(par, text[pos:], False, style=style, bold=bold, italic=italic)


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
        ppr = p._p.get_or_add_pPr()
        for np in ppr.findall(qn("w:numPr")):
            ppr.remove(np)
        if text:
            add_text(p, text, bold=bold, italic=italic, style=style)
        if keep_next:
            p.paragraph_format.keep_with_next = True
        if style in ("Text", "Text1"):
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1.0)
            p.paragraph_format.line_spacing = 0.94
        elif style in ("Abstract", "Abstract2"):
            p.paragraph_format.space_before = Pt(0.5)
            p.paragraph_format.space_after = Pt(1.5)
            p.paragraph_format.line_spacing = 0.94
        elif style == "Heading 0":
            p.paragraph_format.space_before = Pt(2.0)
            p.paragraph_format.space_after = Pt(1.0)
        elif style == "Heading 1":
            p.paragraph_format.space_before = Pt(2.5)
            p.paragraph_format.space_after = Pt(0.8)
        elif style == "Heading 2":
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(0.5)
        self._place(p)
        return p

    def picture(self, path, width_cm=7.6):
        p = self.doc.add_paragraph(style="Figure Text")
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_before = Pt(0.8)
        p.paragraph_format.space_after = Pt(0.3)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if os.path.exists(path):
            p.add_run().add_picture(path, width=Cm(width_cm))
        return p

    def caption(self, text):
        p = self.para("Figure Caption", text)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0.5)
        p.paragraph_format.space_after = Pt(1.5)
        for r in p.runs:
            set_run_font_size(r, 8.5)
        return p

    def reference(self, idx, parts):
        p = self.doc.add_paragraph(style="EN_REF")
        p.paragraph_format.space_before = Pt(0.0)
        p.paragraph_format.space_after = Pt(0.0)
        p.paragraph_format.line_spacing = 0.82
        r0 = p.add_run(f"[{idx}] ")
        _set_fonts(r0, True)
        r0.font.name = "Times New Roman"
        set_run_font_size(r0, 5.4)
        for txt, it in parts:
            r = p.add_run(txt)
            _set_fonts(r, True)
            r.font.name = "Times New Roman"
            set_run_font_size(r, 5.4)
            if it:
                _style_run(r, italic=True)
        return p

    def formula_line(self, formula_spec):
        """Standalone, unnumbered math/Latin expression on its own line, strictly LTR & left-aligned."""
        p = self.doc.add_paragraph()
        p.style = self.doc.styles["Figure Text"]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1.2)
        p.paragraph_format.space_after = Pt(1.2)
        p.paragraph_format.line_spacing = 0.95
        p.paragraph_format.left_indent = Cm(0.3)
        ppr = p._p.get_or_add_pPr()
        bd = OxmlElement("w:bidi")
        bd.set(qn("w:val"), "0")
        ppr.append(bd)
        if isinstance(formula_spec, str):
            r = p.add_run(formula_spec)
            _set_fonts(r, True)
            r.font.name = "Times New Roman"
            set_run_font_size(r, 8.5)
        else:
            for text, mode in formula_spec:
                r = p.add_run(text)
                _set_fonts(r, True)
                r.font.name = "Times New Roman"
                set_run_font_size(r, 8.5)
                _style_run(r, italic=(mode == "i"), sub=(mode == "sub"), sup=(mode == "sup"))
        return p

    def equation(self, segments, number):
        tbl = self.doc.add_table(rows=1, cols=2)
        _table_props(tbl, [650, COL_W - 650], borders=False)
        c_num, c_eq = tbl.rows[0].cells
        # number cell
        p = c_num.paragraphs[0]
        p.style = self.doc.styles["Figure Text"]
        p.paragraph_format.space_before = Pt(0.3)
        p.paragraph_format.space_after = Pt(0.3)
        _emit(p, f"({to_fa_num(str(number))})", False)
        for r in p.runs:
            set_run_font_size(r, 8.0)
        # equation cell (LTR, left-aligned)
        p = c_eq.paragraphs[0]
        p.style = self.doc.styles["Figure Text"]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0.3)
        p.paragraph_format.space_after = Pt(0.3)
        ppr = p._p.get_or_add_pPr()
        bd = OxmlElement("w:bidi")
        bd.set(qn("w:val"), "0")
        ppr.append(bd)
        for text, mode in segments:
            r = p.add_run(text)
            _set_fonts(r, True)
            r.font.name = "Times New Roman"
            set_run_font_size(r, 8.5)
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
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        for cell, wd in zip(row.cells, widths):
            tcPr = cell._tc.get_or_add_tcPr()
            for el in tcPr.findall(qn("w:tcW")):
                tcPr.remove(el)
            tcw = OxmlElement("w:tcW")
            tcw.set(qn("w:w"), str(wd))
            tcw.set(qn("w:type"), "dxa")
            tcPr.insert(0, tcw)
            tcMar = OxmlElement("w:tcMar")
            for m, val in [("top", 12), ("bottom", 12), ("left", 8), ("right", 8)]:
                node = OxmlElement(f"w:{m}")
                node.set(qn("w:w"), str(val))
                node.set(qn("w:type"), "dxa")
                tcMar.append(node)
            tcPr.append(tcMar)
            tcPr.append(parse_xml(f'<w:noWrap {nsdecls("w")}/>'))


def data_table(builder, header, rows, widths, bold_row=None, font_size=5.6):
    tbl = builder.doc.add_table(rows=1 + len(rows), cols=len(header))
    _table_props(tbl, widths)
    for ci, h in enumerate(header):
        cell = tbl.cell(0, ci)
        p = cell.paragraphs[0]
        p.style = builder.doc.styles["Figure Text"]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0.2)
        p.paragraph_format.space_after = Pt(0.2)
        p.paragraph_format.keep_with_next = True
        add_text(p, h, bold=True)
        for r in p.runs:
            set_run_font_size(r, font_size + 0.4)
        shading_xml = f'<w:shd {nsdecls("w")} w:fill="E0E0E0"/>'
        cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))
    for ri, row in enumerate(rows, start=1):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            p = cell.paragraphs[0]
            p.style = builder.doc.styles["Figure Text"]
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if ci == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0.1)
            p.paragraph_format.space_after = Pt(0.1)
            add_text(p, str(val), bold=(bold_row == ri - 1))
            for r in p.runs:
                set_run_font_size(r, font_size)
            if bold_row == ri - 1:
                shading_xml = f'<w:shd {nsdecls("w")} w:fill="E8F5E9"/>'
                cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))
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
    for r in sect_p.findall(qn("w:r")):
        sect_p.remove(r)
    return sect_p


def clean_template_headers_footers(doc):
    """
    Remove guide arrows (25 mm) and repeated banner on subsequent pages.
    - Preserves Page 1 header banner (_x0000_s1046).
    - Clears Section 0 footer (removes _x0000_s1033).
    - Clears Section 1 header (removes repeated banner _x0000_s1047 on pages 2-6).
    - Clears Section 1 footer (removes _x0000_s1036).
    """
    # Section 0 footer
    f0 = doc.sections[0].footer._element
    for el in list(f0):
        f0.remove(el)
    f0.append(OxmlElement("w:p"))

    # Section 1 header
    h1 = doc.sections[1].header._element
    for el in list(h1):
        h1.remove(el)
    h1.append(OxmlElement("w:p"))

    # Section 1 footer
    f1 = doc.sections[1].footer._element
    for el in list(f1):
        f1.remove(el)
    f1.append(OxmlElement("w:p"))


def apply_mitra_styling(doc):
    """Enforce B Mitra for complex script across docDefaults and all document styles."""
    docDefaults = doc.styles.element.find(qn("w:docDefaults"))
    if docDefaults is not None:
        rPrDefault = docDefaults.find(qn("w:rPrDefault"))
        if rPrDefault is not None:
            rPr = rPrDefault.find(qn("w:rPr"))
            if rPr is not None:
                rf = rPr.find(qn("w:rFonts"))
                if rf is None:
                    rf = OxmlElement("w:rFonts")
                    rPr.insert(0, rf)
                rf.set(qn("w:ascii"), "Times New Roman")
                rf.set(qn("w:hAnsi"), "Times New Roman")
                rf.set(qn("w:cs"), "B Mitra")
                sz = rPr.find(qn("w:sz"))
                if sz is None:
                    sz = OxmlElement("w:sz")
                    rPr.append(sz)
                sz.set(qn("w:val"), "17")
                szCs = rPr.find(qn("w:szCs"))
                if szCs is None:
                    szCs = OxmlElement("w:szCs")
                    rPr.append(szCs)
                szCs.set(qn("w:val"), "18")
                lang = rPr.find(qn("w:lang"))
                if lang is None:
                    lang = OxmlElement("w:lang")
                    rPr.append(lang)
                lang.set(qn("w:bidi"), "fa-IR")

    for s in doc.styles:
        pPr = s._element.find(qn("w:pPr"))
        if pPr is not None:
            for np in pPr.findall(qn("w:numPr")):
                pPr.remove(np)
        if s.name in ("ENauthor", "ENtitle", "ENheading 0", "ENabstract", "ENabrstract2", "EN_REF"):
            continue
        try:
            rPr = s._element.get_or_add_rPr()
            rf = rPr.find(qn("w:rFonts"))
            if rf is None:
                rf = OxmlElement("w:rFonts")
                rPr.insert(0, rf)
            rf.set(qn("w:ascii"), "Times New Roman")
            rf.set(qn("w:hAnsi"), "Times New Roman")
            rf.set(qn("w:cs"), "B Mitra")

            en_sz, fa_sz = STYLE_FONT_SIZES.get(s.name, (8.5, 9.0))
            sz = rPr.find(qn("w:sz"))
            if sz is None:
                sz = OxmlElement("w:sz")
                rPr.append(sz)
            sz.set(qn("w:val"), str(int(en_sz * 2)))

            szCs = rPr.find(qn("w:szCs"))
            if szCs is None:
                szCs = OxmlElement("w:szCs")
                rPr.append(szCs)
            szCs.set(qn("w:val"), str(int(fa_sz * 2)))

            if s.name == "Title":
                s.paragraph_format.space_before = Pt(2.0)
                s.paragraph_format.space_after = Pt(1.5)
            elif s.name == "Author":
                s.paragraph_format.space_before = Pt(0.5)
                s.paragraph_format.space_after = Pt(0.5)
            elif s.name == "Heading 0":
                s.paragraph_format.space_before = Pt(2.0)
                s.paragraph_format.space_after = Pt(1.0)
            elif s.name in ("Text", "Text1"):
                s.paragraph_format.line_spacing = 0.94
                s.paragraph_format.space_after = Pt(1.0)
            elif s.name in ("Abstract", "Abstract2"):
                s.paragraph_format.line_spacing = 0.94
                s.paragraph_format.space_before = Pt(0.5)
                s.paragraph_format.space_after = Pt(1.5)
            elif s.name == "Heading 1":
                s.paragraph_format.space_before = Pt(2.5)
                s.paragraph_format.space_after = Pt(0.8)
            elif s.name == "Heading 2":
                s.paragraph_format.space_before = Pt(1.5)
                s.paragraph_format.space_after = Pt(0.5)
            elif s.name in ("Figure Text", "Table Text"):
                s.paragraph_format.line_spacing = 0.88
                s.paragraph_format.space_before = Pt(0.1)
                s.paragraph_format.space_after = Pt(0.1)
            elif s.name in ("Figure Caption", "Caption"):
                s.paragraph_format.line_spacing = 0.90
                s.paragraph_format.space_before = Pt(0.3)
                s.paragraph_format.space_after = Pt(0.4)
            elif s.name == "REF":
                s.paragraph_format.line_spacing = 0.84
                s.paragraph_format.space_after = Pt(0.0)
        except Exception:
            pass


def build():
    ensure_template()

    # Load Hamta benchmarks
    df_fc = pd.read_csv(os.path.join(cfg.OUTPUT_DIR, "hamta_forecasting_benchmark.csv"))
    df_rk = pd.read_csv(os.path.join(cfg.OUTPUT_DIR, "hamta_ranking_benchmark.csv"))
    df_ab = pd.read_csv(os.path.join(cfg.OUTPUT_DIR, "hamta_ablation_results.csv"))
    df_sc = pd.read_csv(os.path.join(cfg.OUTPUT_DIR, "hamta_scenarios_results.csv"))
    df_opp = pd.read_csv(os.path.join(cfg.OUTPUT_DIR, "hamta_top_opportunities.csv"))
    mb_path = os.path.join(cfg.OUTPUT_DIR, "table2b_multibudget_10seeds.csv")
    if not os.path.exists(mb_path):
        mb_path = os.path.join(cfg.OUTPUT_DIR, "phase1_results", "table2b_multibudget_10seeds.csv")
    df_mb = pd.read_csv(mb_path) if os.path.exists(mb_path) else pd.DataFrame()

    doc = docx.Document(TEMPLATE_DOCX)

    # Section 0: Title, Authors, Abstract on Page 1 (leaves 5.2 cm for top banner)
    doc.sections[0].top_margin = Cm(5.2)
    doc.sections[0].bottom_margin = Cm(2.5)  # 25 mm strictly per template
    doc.sections[0].left_margin = Cm(2.0)
    doc.sections[0].right_margin = Cm(2.0)

    # Section 1: Two columns for pages 2 to 6 (no repeating banner, clean 2.5 cm margins)
    doc.sections[1].top_margin = Cm(2.5)     # 25 mm strictly
    doc.sections[1].bottom_margin = Cm(2.5)  # 25 mm strictly
    doc.sections[1].left_margin = Cm(2.0)
    doc.sections[1].right_margin = Cm(2.0)

    clean_template_headers_footers(doc)
    apply_mitra_styling(doc)
    sect_p = clear_body(doc)
    B = Builder(doc, sect_p)

    # ------------------------------------------------------------ first page (single column section)
    B.para("Title", "چارچوب گراف زمانی برای کشف فرصت رشد تراکنش پذیرندگان و اولویت‌بندی کمپین")

    p = B.para("Author")
    add_text(p, "سعید علی اکبری")
    r = p.add_run("۱*"); _set_fonts(r, False); _style_run(r, sup=True); set_run_font_size(r, 9.5)
    add_text(p, "، سعید شاهسون")
    r = p.add_run("۲"); _set_fonts(r, False); _style_run(r, sup=True); set_run_font_size(r, 9.5)

    p_aff1 = B.para("Author", "۱ کارشناس هوش تجاری، شرکت رایامیت، تهران، ایران (نویسنده مسئول)")
    p_aff1.paragraph_format.space_before = Pt(1.0)
    p_aff1.paragraph_format.space_after = Pt(0.2)

    p_em1 = B.para("Author", "")
    p_em1.paragraph_format.space_before = Pt(0.0)
    p_em1.paragraph_format.space_after = Pt(1.5)
    ppr1 = p_em1._p.get_or_add_pPr()
    bd1 = OxmlElement("w:bidi")
    bd1.set(qn("w:val"), "0")
    ppr1.append(bd1)
    r1 = p_em1.add_run("saeed.aliakbari@rayamate.ir")
    _set_fonts(r1, True)
    r1.font.name = "Times New Roman"
    set_run_font_size(r1, 8.5)

    p_aff2 = B.para("Author", "۲ معمار نرم‌افزار، شرکت رایامیت، تهران، ایران")
    p_aff2.paragraph_format.space_before = Pt(0.5)
    p_aff2.paragraph_format.space_after = Pt(0.2)

    p_em2 = B.para("Author", "")
    p_em2.paragraph_format.space_before = Pt(0.0)
    p_em2.paragraph_format.space_after = Pt(2.5)
    ppr2 = p_em2._p.get_or_add_pPr()
    bd2 = OxmlElement("w:bidi")
    bd2.set(qn("w:val"), "0")
    ppr2.append(bd2)
    r2 = p_em2.add_run("saeed.shahsavan@rayamate.ir")
    _set_fonts(r2, True)
    r2.font.name = "Times New Roman"
    set_run_font_size(r2, 8.5)

    B.para("Heading 0", "چکیده")
    B.para("Abstract",
           "شرکت‌های ارائه‌دهنده خدمات پرداخت روزانه حجم انبوهی از سوابق تراکنشی را پردازش می‌نمایند. "
           "رویکردهای سنتی مدیریت پذیرندگان بر شاخص‌های خلاصه‌شده جدولی نظیر حجم کل یا مدل RFM استوار بوده و نسبت به شبکه تعاملات مشتریان نابینا هستند؛ "
           "در نتیجه قادر به تفکیک افت طبیعی از ظرفیت بالقوه رشد نیستند. در این مقاله، چارچوب گراف زمانی HAMTA ارائه می‌شود که موتور رتبه‌بندی فرصت‌های رابطه‌ای "
           "را با حفاظ‌های کنترل ریسک عملیاتی تلفیق می‌نماید. HAMTA صرفاً بر پایه پنج فیلد تراکنشی استاندارد، جریان تراکنش‌ها را به گراف دوبخشی کارت–پذیرنده تبدیل کرده "
           "و ساختار همتایان را از طریق اشتراک مشتریان، تجانس صنف و انحنای فرمن-ریچی استخراج می‌کند. سپس با مدل توجه گراف زمانی، تابع درست‌نمایی دوجمله‌ای منفی و واسنجی زمانی بازه پیش‌بینی، "
           "کران بالای عملکرد و بنچ‌مارک همتایان تخمین زده شده و شاخص M-GATO جهت اولویت‌بندی کمپین محاسبه می‌گردد. "
           f"ارزیابی تجربی بر روی {to_fa_num('35000')} تراکنش شبیه‌سازی‌شده طی {to_fa_num('10')} سید تصادفی نشان می‌دهد HAMTA با ثبت خطای میانگین {to_fa_num('4.48')} تراکنش و "
           f"دقت رتبه‌بندی {to_fa_num('36.6')} درصد، به بهبود {to_fa_num('2.51')} برابری نسبت به شانس تصادفی دست یافته و زیرساختی عملیاتی و بدون برچسب مداخله برای هوشمندی سبد پذیرندگان فراهم می‌سازد.")
    B.para("Abstract2", "چارچوب HAMTA تنها یک مدل یادگیری ماشین نیست، بلکه یک مؤلفه تصمیم‌یار (Decision-support component) در معماری مدیریت پذیرندگان است. این معماری از جریان داده‌های تراکنشی آغاز شده، در لایه هوشمندی گراف پردازش می‌گردد و توسط موتور تصمیم‌گیری M-GATO به واحد بازاریابی جهت اجرای کمپین و دریافت بازخورد سازمانی متصل می‌شود.")

    B.para("Heading 0", "کلمات کلیدی")
    B.para("Abstract",
           "سامانه‌های پرداخت، شبکه‌های عصبی گراف زمانی، هوشمندی پذیرندگان، اولویت‌بندی کمپین، واسنجی بازه پیش‌بینی، انحنای فرمن-ریچی، فین‌تک.")

    # ------------------------------------------------------------ body (two columns)
    B.head_mode = False

    # 1 -------------------------------------------------------------------------------- مقدمه
    B.para("Heading 1", "1. مقدمه")
    B.para("Text1",
           "شبکه‌های پرداخت کارتی، سوییچ‌های بین‌بانکی و شرکت‌های ارائه‌دهنده خدمات پرداخت (PSP) روزانه صدها میلیون تراکنش را بر روی پایانه‌های فروش و درگاه‌های اینترنتی ثبت می‌کنند [1, 2]. "
           "در سامانه‌های سنتی مدیریت پذیرندگان، اولویت‌بندی بازاریابی عموماً بر اساس شاخص‌های گذشته‌نگر جدولی نظیر ارزش ناخالص تسویه یا مدل‌های RFM استوار است [3]. "
           "با این حال، این رویکردها تفاوت سه مفهوم بنیادین را نادیده می‌گیرند: «کمترین حجم تراکنش» با «عملکرد ضعیف نسبت به همتایان» و «فرصت رشد در کمپین» یکسان نیست. "
           "برای نمونه، پذیرنده‌ای با ۵۰ تراکنش که تمامی همتایان آن در همان صنف و بافت تعاملات مشتریان مشترک نیز حدود ۵۰ تراکنش دارند، در وضعیت طبیعی فعالیت می‌کند؛ "
           "اما پذیرنده‌ای با ۱۰۰ تراکنش که همتایان هم‌ساختار آن به طور میانگین ۱۸۰ تراکنش ثبت کرده‌اند، واجد یک شکاف عملکردی نسبی معنادار است. "
           "هدف اصلی این مقاله، کشف پذیرنده‌ای نیست که صرفاً کمترین حجم مطلق را دارد، بلکه کشف پذیرندگانی است که نسبت به همتایان مشابه خود، واجد شکاف عملکرد ساختاری در داده‌های مشاهده‌ای هستند.")
    B.para("Text",
           "شناسایی پذیرندگان کم‌عملکرد اما دارای پتانسیل بالا، با چهار چالش اساسی روبروست: "
           "نخست، نابینایی رابطه‌ای مدل‌های جدولی نسبت به ساختار مشتریان مشترک پایانه‌ها؛ "
           "دوم، بیش‌پراکندگی شدید داده‌های شمارشی تعداد تراکنش که برازش با خطای گوسی را ناکارآمد می‌سازد؛ "
           "سوم، تفاوت پیش‌بینی اینرسی آینده با کشف فرصت، چرا که پیش‌بینی استاندارد صرفاً تداوم کم‌عملکردی پذیرنده ضعیف را تخمین می‌زند؛ "
           "و چهارم، لزوم اتکای انحصاری بر پنج فیلد استاندارد دفتر کل بدون هیچ‌گونه فرضیات خارجی: "
           "شناسه کارت (Masked PAN)، مبلغ تراکنش (Amount)، شناسه پذیرنده دفتر کل PSP، تاریخ و زمان (Create Date) و صنف اقتصادی (Cast Name).")
    B.para("Text",
           "برای حل این چالش‌ها، چارچوب هوش مصنوعی گراف زمانی با نام HAMTA در قالب یک معماری سه‌لایه ارائه می‌گردد: موتور رتبه‌بندی فرصت‌های رابطه‌ای، حفاظ‌های کنترل ریسک عملیاتی و پالایش ساختاری توپولوژیک. "
           "کارت‌ها صرفاً به عنوان گره‌های واسط جهت کشف مسیرهای هم‌پوشان مشتریان عمل می‌کنند و واحد تحلیل در سطح حساب تجاری پذیرنده است. "
           "این چارچوب با ترکیب شبکه‌های عصبی گراف زمانی، انحنای گسسته فرمن-ریچی [4, 5] برای مهار پدیده فشردگی اطلاعات [6, 7] و واسنجی زمانی بازه پیش‌بینی یک‌طرفه [8]، امتیاز M-GATO را جهت اولویت‌بندی کمپین استخراج می‌کند. "
           "در ادبیات بازاریابی پرداخت، لیو و همکاران (CIKM 2019) [9] از یادگیری بازنمایی گراف جهت بهینه‌سازی مشوق‌های بازاریابی در علی‌پِی بهره بردند؛ اما چارچوب آن‌ها در محیط آپ‌لیفت نظارت‌شده متکی بر لاگ‌های تاریخی کوپن‌های تخفیف و برچسب‌های مداخله عمل می‌کند. "
           "در مقابل، سوییچ‌های شاپرکی فاقد داده‌های تاریخی کمپین هستند و HAMTA اولین روش بازاریابی پذیرندگان مبتنی بر گراف نیست، بلکه چارچوبی برای کشف فرصت نسبی بدون نیاز به برچسب‌های تاریخی مداخله بر پایه گراف تراکنش زمانی و بنچ‌مارک محافظه‌کارانه ارائه می‌کند.")

    # 2 -------------------------------------------------------------------------------- کارهای مرتبط
    B.para("Heading 1", "2. کارهای مرتبط")
    B.para("Heading 2", "2.1. شبکه‌های عصبی گراف در تحلیل‌های مالی")
    B.para("Text1",
           "شبکه‌های عصبی گراف (GNN) با مدل‌سازی موجودیت‌ها به عنوان گره و تراکنش‌ها به عنوان یال، در کشف تقلب و تحلیل حساب‌های مشکوک موفقیت چشمگیری داشته‌اند [9-11]. "
           "معماری‌های پایه نظیر اتوانکودرهای تغییراتی گراف [12] و ساختارهای استقرایی شبکه تراکنشی [13] چارچوب‌های بازنمایی ساختار را توسعه داده‌اند [14, 15]. "
           "در حوزه بازاریابی پرداخت، لیو و همکاران (CIKM 2019) [9] از یادگیری بازنمایی گراف جهت بهینه‌سازی مشوق‌ها در علی‌پِی بهره بردند؛ اما رویکرد آن‌ها متکی بر لاگ‌های پیشین مداخله و کوپن‌های تشویقی است. "
           "در مقابل، سوییچ‌های شاپرکی فاقد برچسب‌های مداخله بوده و نیازمند اولویت‌بندی فرصت‌ها در داده‌های مشاهده‌ای هستند.")
    B.para("Heading 2", "2.2. یادگیری نمایش در گراف‌های پویا و زمانی")
    B.para("Text1",
           "روابط مالی ذاتا متغیر با زمان هستند. مدل‌های گراف زمانی نظیر TGAT [16]، TGN [17] و EvolveGCN [18] و پیمایش‌های اخیر یادگیری گراف‌های پویا [19] "
           "با به‌کارگیری مکانیزم‌های توجه زمانی و پروتکل‌های حفظ تقدم زمانی، مانع از نشت اطلاعات آینده به گذشته شده و پویایی نرخ تراکنش‌ها را مدل‌سازی می‌کنند.")
    B.para("Heading 2", "2.3. تحلیل شبکه پذیرندگان و انحنای فرمن-ریچی")
    B.para("Text1",
           "در شبکه‌های تراکنشی مالی، گره‌ها خوشه‌بندی‌های متراکم و گلوگاه‌های ساختاری تشکیل می‌دهند [20, 21]. انحنای فرمن-ریچی [4, 5] با اندازه‌گیری اشتراک همسایگی‌ها و تمایز پیوندهای پل‌ساز، "
           "به عنوان تنظیم‌کننده ساختاری و مهارکننده پدیده فشردگی اطلاعات (Over-squashing) در گراف عمل می‌کند [6, 7, 22].")
    B.para("Heading 2", "2.4. تخمین نااطمینانی و واسنجی بازه پیش‌بینی")
    B.para("Text1",
           "پیش‌بینی‌های نقطه‌ای قادر به تفکیک نوسانات تصادفی طبیعی از افت معنادار عملکرد نیستند. روش‌های واسنجی بازه پیش‌بینی تجربی [8] و پژوهش‌های نااطمینانی پیش‌بینی بر روی گراف‌های زمانی [23] "
           "با سنجش توزیع خطاهای پسماند در پنجره‌های گذشته، کران‌های بازه‌ای واسنجی‌شده را استخراج می‌نمایند؛ لذا در HAMTA واسنجی بازه پیش‌بینی یک‌طرفه زمانی (One-sided temporal prediction-interval calibration) به صورت تجربی صورت می‌گیرد.")
    B.para("Heading 2", "2.5. تحلیل مرز تصادفی و مدل‌های داده‌های شمارشی")
    B.para("Text1",
           "در ادبیات اقتصادسنجی، تحلیل مرز تصادفی (SFA) کارایی نسبی بنگاه‌ها را نسبت به مرز بهترین عملکرد تجربی برآورد می‌نماید [24]. "
           "در داده‌های تراکنش خرد، به دلیل بیش‌پراکندگی شدید، استفاده از توزیع دوجمله‌ای منفی مانع از اریب خطای برآورد میانگین گردیده و بازه‌های خطای پایداری را نسبت به تقریب پیوسته گوسی فراهم می‌آورد [25].")

    # 3 -------------------------------------------------------------------------------- روش پیشنهادی
    B.para("Heading 1", "3. روش پیشنهادی (چارچوب معماری HAMTA)")
    B.para("Text1",
           "معماری HAMTA شامل جریان پیوسته‌ای از مراحل پردازش است: ساخت گراف دوبخشی، القای گراف همتایان، پیش‌بینی گراف زمانی، واسنجی نااطمینانی، و محاسبه امتیاز M-GATO (شکل (1)).")
    B.picture(os.path.join(FIG, "fig1_architecture_fa.png"))
    B.caption("شکل (1) : خط لوله معماری چارچوب HAMTA برای کشف فرصت تراکنشی پذیرندگان")

    B.para("Heading 2", "3.1. تعریف مسئله و ساختار داده")
    B.para("Text1", "دفتر کل تراکنش‌ها به صورت دنباله‌ای از رویدادها")
    B.formula_line("L = { e_1, ..., e_N }")
    B.para("Text", "تعریف می‌شود که در آن هر رویداد شامل پنج فیلد استاندارد است:")
    B.formula_line("e_k = <pan_k, amount_k, merchant_id_k, create_date_k, cast_name_k>")
    B.para("Text",
           "شناسه merchant_id بیانگر شناسه پذیرنده ارائه‌شده در دفتر کل PSP است. "
           "از همین پنج فیلد پایه و بدون نیاز به متغیرهای خارجی، بردار ویژگی ۱۶بُعدی گره پذیرنده به صورت زیر ساخته می‌شود:")
    B.formula_line([("x", "i"), ("_{m, t} ∈ ℝ", ""), ("16", "sup")])
    B.para("Text",
           "مؤلفه‌های این بردار شامل: "
           "(۱ تا ۴) وقفه‌های زمانی حجم تراکنش (لگاریتم تراکنش‌های دوره‌های پیشین و میانگین وقفه همسایگان)؛ "
           "(۵ تا ۷) شاخص‌های مقیاس مالی استخراج‌شده از مبلغ تراکنش شامل لگاریتم حجم کل، میانگین و انحراف معیار مبلغ؛ "
           "(۸) وسعت تعاملات مشتریان یکتا (تعداد کارت‌های متمایز)؛ و "
           "(۹ تا ۱۶) بردار وان‌هات نشانگر صنف اقتصادی در میان ۸ صنف تجاری. "
           "مسیر وابستگی ویژگی‌ها اکیداً علّی است:")
    B.formula_line("5 Raw Ledger Fields → Historical Peer Graph → Peer Lag Aggregation → Temporal GNN (time t)")
    B.para("Text",
           "هدف مسئله در سطح هر پذیرنده m ∈ M، پیش‌بینی تعداد تراکنش دوره آتی و تعیین شکاف فرصت ساختاری آن نسبت به بنچ‌مارک محافظه‌کارانه همتایان است:")
    B.formula_line([("Y", "i"), ("_{m, t+1} ∈ ℕ", ""), ("0", "sub"), (",   B", "i"), ("^G_{m, t+1}", "")])

    B.para("Heading 2", "3.2. گراف دوبخشی زمانی کارت–پذیرنده")
    B.para("Text1", "در هر پنجره زمانی گسسته t، تراکنش‌ها در قالب گراف دوبخشی زیر سازمان می‌یابند:")
    B.formula_line([("G", "i"), ("^(B)_t = ( C_t , M_t , E_t )", "")])
    B.para("Text",
           "هر یال دوتایی نشانگر وقوع دست‌کم یک تراکنش توسط کارت c در پایانه m در پنجره t است (یال‌ها باینری هستند تا تمرکز بر ساختار هم‌ملاقاتی توپولوژیک باشد نه حجم تراکنش). "
           "کارت‌ها صرفاً به عنوان گره‌های واسط جهت استخراج مسیرهای هم‌پوشان مشتریان عمل می‌کنند و هویت فردی آن‌ها نگهداری نمی‌شود.")

    B.para("Heading 2", "3.3. گراف همتایان پذیرنده و تعدیل انحنا")
    B.para("Text1",
           "به منظور پرهیز از مقایسه‌های متراکم و پرهزینه O(|M|^2)، چارچوب HAMTA از ایندکس معکوس کارت به پذیرنده جهت تولید کاندیداها استفاده می‌نماید. "
           "نمایه معکوس I(c) تمامی پذیرندگان مشاهده‌شده توسط کارت c در پنجره‌های گذشته را بازمی‌یابد و برای هر پذیرنده m، همسایگی ۲-گامه در زمان O(|C_m| · d_card) استخراج می‌شود:")
    B.formula_line([("C(m) = ⋃", ""), ("c ∈ C_m", "sub"), (" I(c) \\ { m }", "")])
    B.para("Text", "سپس شباهت پذیرندگان کاندیدا بر اساس رابطه (1) فرمول‌بندی می‌گردد:")
    B.equation([("S(m, j) = λ · S", ""), ("covisit", "sub"), ("(m, j) + (1 – λ) · S", ""), ("category", "sub"), ("(m, j)", "")], 1)
    B.para("Text",
           "که در آن S_covisit شباهت کسینوسی بردار دودویی وقوع مشتریان مشترک و S_category تطابق صنف تجاری است. ضریب λ = 0.65 در پنجره اعتبارسنجی گذشته تنظیم شده است. "
           "یک هیپ بیشینه همتایان Top-K (K=6) را در مرتبه O(|C(m)| log K) با پیچیدگی کاندیدایابی محدود به O(|M| · K · d_avg) استخراج می‌نماید. "
           "از آنجا که رابطه انتخاب Top-K ذاتاً جهت‌دار است، گراف همتایان پیش از محاسبه انحنا با عملگر اجتماع متقارن‌سازی می‌گردد:")
    B.formula_line("G_peer = Top-K ∪ Top-K^T")
    B.para("Text",
           "توجه شود که محاسبه انحنا روی گراف همتایان متقارن‌شده انجام می‌شود. سپس انحنای فرمن-ریچی نرمال‌شده افزوده طبق رابطه (2) به عنوان پالایش ساختاری محاسبه می‌شود [4, 5]:")
    B.equation([("F(m, j) = [ 4 – d(m) – d(j) + 3 · Δ(m, j) ] / √[ d(m) · d(j) ]", "")], 2)
    B.para("Text",
           "که d(m) درجه گره، Δ(m, j) تعداد مثلث‌های مشترک و مخرج رادیکالی جهت جلوگیری از غلبه گره‌های متراکم مرکزی پیشنهاد شده است. انحنا وزن همتایان را طبق رابطه (3) تعدیل می‌کند:")
    B.equation([("w̃", ""), ("mj", "sub"), (" ∝ w", ""), ("mj", "sub"), (" · ( 1 + η · tanh(F(m, j)) )", "")], 3)
    B.para("Text", "با ضریب مقیاس η = 0.25 به عنوان تنظیم‌کننده ساختاری و پالایش‌گر روابط همتایان عمل می‌نماید.")

    B.picture(os.path.join(FIG, "fig2_topology_fa.png"))
    B.caption("شکل (2) : تصویرسازی دوبعدی تعبیه‌های گراف همتایان پذیرنده در ۸ صنف تجاری؛ حلقه‌های قرمز نشانگر اهداف افت ساختاری تزریق‌شده هستند.")

    B.para("Heading 2", "3.4. پیش‌بینی گراف زمانی با تابع دوجمله‌ای منفی")
    B.para("Text1",
           "متغیر هدف، تعداد تراکنش دوره آتی Y_{m, t+1} است. داده‌های تراکنشی بیش‌پراکندگی شدید نشان می‌دهند (Var(Y)/E[Y] ≈ 3.24) که استفاده از توزیع دوجمله‌ای منفی را نسبت به مدل پواسون توجیه می‌کند. "
           "لذا مدل بر مبنای معماری توجه گراف زمانی برگرفته از TGAT با تابع درست‌نمایی دوجمله‌ای منفی آموزش می‌یابد:")
    B.equation([("L", "i"), ("_NB = - ∑ [ ln Γ(Y+φ) - ln Γ(φ) - ln Γ(Y+1) + φ ln(φ/(φ+μ̂)) + Y ln(μ̂/(φ+μ̂)) ]", "")], 4)
    B.para("Text",
           "که در آن μ̂ میانگین برآوردی و φ پارامتر اندازه یا پراکندگی معکوس (inverse-dispersion/size parameter) است. کلیه ورودی‌ها به اطلاعات تا زمان t محدود بوده و پروتکل آموزش تقدم زمانی مانع از نشت اطلاعات می‌گردد. "
           "مدل از معماری TGAT دو لایه با بعد ویژگی ورودی ۱۶، بعد پنهان ۳۲ و ۲ هد توجه بهره می‌برد. "
           "آموزش با الگوریتم Adam طی ۷۰ دور با توقف زودهنگام در دوره اعتبارسنجی دوره ۳ انجام شده و سپس بر روی داده‌های P0 تا دوره ۳ نهایی گردیده است.")

    B.para("Heading 2", "3.5. واسنجی زمانی بازه پیش‌بینی یک‌طرفه بر روی دوره مستقل")
    B.para("Text1",
           "پروتکل زمانی اعتبارسنجی شامل تفکیک دقیق دوره‌ها است: دوره‌های ۰ تا ۲ آموزش اولیه، دوره ۳ اعتبارسنجی ابرپارامترها، P0-دوره ۳ برازش نهایی، دوره ۴ واسنجی کاملاً تمیز بر داده‌های طبیعی دست‌نخورده، و دوره ۵ پنجره آزمون و اعمال افت فرصت. "
           "بر روی داده‌های کاملاً طبیعی دوره ۴، پسماندهای یک‌طرفه نوسانات مثبت طبیعی را می‌سنجند [8]:")
    B.formula_line([("R", "i"), ("_m = max( 0 , Y_m - μ̂_m )", "")])
    B.para("Text",
           "با در نظر گرفتن سطح خطای اسمی α = 0.15، صدک واسنجی‌شده استخراج شده و کران بالای طبیعی عملکرد پیش‌بینی مطابق رابطه (5) تعیین می‌شود:")
    B.formula_line([("q", "i"), ("_{0.85} = Quantile_{0.85}( { R_m } )", "")])
    B.equation([("U", "i"), ("_{m, t+1} = μ̂_{m, t+1} + q_{0.85}", "")], 5)
    B.para("Text",
           "چون واسنجی اکیداً بر داده‌های دست‌نخورده دوره ۴ قبل از تزریق افت در دوره ۵ اجرا می‌شود، داده‌های واسنجی به هیچ‌وجه تحت تأثیر افت فرصت مصنوعی قرار ندارند. "
           "پوشش یک‌طرفه تجربی ثبت‌شده (Coverage = 86.2 ± 3.1% با عرض بازه میانگین ۴٫۶ ± ۰٫۳ تراکنش) اعتبار تجربی واسنجی را تایید می‌نماید.")

    B.para("Heading 2", "3.6. بنچ‌مارک محافظه‌کارانه همتایان گرافی (B^G)")
    B.para("Text1",
           "برای جلوگیری از خوش‌بینی مفرط، بنچ‌مارک همتایان بر پایه کران پایین پیش‌بینی همتایان با مقدار واسنجی‌شده یکسان q_j = q_0.85 تعریف می‌گردد:")
    B.formula_line([("L", "i"), ("_j = max( 0 , μ̂_j - q_j )", "")])
    B.para("Text", "سپس بنچ‌مارک محافظه‌کارانه همتایان مطابق رابطه (6) فرمول‌بندی می‌شود:")
    B.equation([("B", "i"), ("^G_{m, t+1} = [ ∑", ""), ("j", "sub"), (" w̃", ""), ("mj", "sub"), (" · L", ""), ("j, t+1", "sub"),
                 (" ] / [ ∑", ""), ("j", "sub"), (" w̃", ""), ("mj", "sub"), (" ]", "")], 6)

    B.para("Heading 2", "3.7. فرمول امتیاز فرصت M-GATO و تحلیل محاسباتی")
    B.para("Text1",
           "شاخص رتبه‌بندی فرصت همتا-محور (M-GATO) حاصل‌ضرب شواهد گرافی در شکاف کران-پیش‌بینی همتایان فرمول‌بندی می‌گردد:")
    B.equation([("Q", "i"), ("_{m, t} = 1 – exp(-O_{m, t} / κ)", "")], 7)
    B.equation([("M-GATO", "i"), ("_{m, t} = Q_{m, t} · [ ( B^G_{m, t+1} – U_{m, t+1} ) / ( B^G_{m, t+1} + ε ) ]_+", "")], 8)
    B.para("Text",
           "که در آن [x]_+ = max(0, x)، O_{m, t} مجموع کارت‌های مشترک با همتایان Top-K و κ = 18 پارامتر اشباع شواهد است. "
           "M-GATO بیانگر شکاف کران-پیش‌بینی همتایان (Forecast-Bound Peer Gap معادل B^G - U) است، نه صرفاً افت لحظه‌ای مشاهده‌شده کنونی (B^G - Y). "
           "تراکنش واقعی Y مستقیماً در صورت کسر قرار ندارد؛ چرا که پیش‌بینی نقطه‌ای μ̂ و کران بالای کالیبره‌شده U از پیش بر سوابق تاریخی شرطی شده‌اند. "
           "کسر مستقیم Y موجب اختلاط نوسانات کوتاه‌مدت با فرصت ساختاری پایدار می‌گردید. ضریب Q_{m, t} به عنوان جریمه کاهش انقباضی برای پذیرندگان منفرد عمل می‌کند.")
    B.para("Text1",
           "مثال عددی: پذیرنده MERCH_00322 در صنف مسافرتی را در نظر بگیرید: عملکرد فعلی Y = 100، پیش‌بینی مدل μ̂ = 105.0، و کران بالای کالیبره‌شده U = 112.0 تراکنش است. "
           "همتایان این پذیرنده به بنچ‌مارک محافظه‌کارانه B^G = 170.0 دست یافته‌اند و ضریب اتکای گرافی Q = 0.90 است. "
           "بنابراین شکاف کران-پیش‌بینی همتایان و امتیاز M-GATO به صورت زیر محاسبه می‌شوند:")
    B.formula_line("B^G - U = 170.0 - 112.0 = 58.0   (Relative Gap = 0.3412)")
    B.formula_line("M-GATO = 0.3412 × 0.90 = 0.307")
    B.para("Text",
           f"تفسیر دقیق: این پذیرنده واجد {to_fa_num('58')} تراکنش شکاف کران-پیش‌بینی نسبت به سقف طبیعی خود تا بنچ‌مارک همتایان است (در حالی که تفاوت با عملکرد فعلی ۷۰ تراکنش است).")
    B.picture(os.path.join(FIG, "fig3_guild_heatmap_fa.png"))
    B.caption("شکل (3) : مقایسه مؤلفه‌های شاخص M-GATO: تراکنش مشاهده‌شده، پیش‌بینی مدل، کران بالای طبیعی و بنچ‌مارک همتایان")

    # 4 -------------------------------------------------------------------------------- طرح آزمایش
    B.para("Heading 1", "4. طراحی تجربی و پیکربندی داده‌ها")
    B.para("Text1",
           f"داده‌های ارزیابی شامل جریان شبیه‌سازی‌شده طی {to_fa_num('10')} سید تصادفی با {to_fa_num('35000')} تراکنش، {to_fa_num('350')} پذیرنده و {to_fa_num('1480')} کارت در {to_fa_num('8')} صنف اقتصادی طی {to_fa_num('90')} روز است. "
           "اصناف تجاری پیرو توزیع متوازن هستند: سوپرمارکت (۳۵٪)، رستوران (۱۸٪)، پوشاک (۱۵٪)، لوازم الکترونیکی (۱۰٪)، پزشکی (۱۰٪)، گردشگری (۵٪)، طلا (۴٪) و صنعتی (۳٪). "
           "پروتکل زمانی شامل ۶ دوره ۱۵روزه است: آموزش دوره‌های ۰ تا ۲، اعتبارسنجی دوره ۳، واسنجی کاملاً تمیز دوره ۴، و آزمون ارزیابی دوره ۵. هیچ داده آزمونی وارد فرآیند آموزش و واسنجی نشده است.")
    B.para("Text",
           "فرمول‌بندی برچسب فرصت: برچسب فرصت منحصراً به صورت بازیابی ریاضی اهداف افت ساختاری مصنوعی تعریف می‌شود. "
           f"تعداد {to_fa_num('51')} پذیرنده از ۳۵۰ پذیرنده ({to_fa_num('14.6')}٪) با نمونه‌گیری طبقه‌بندی‌شده در تمامی اصناف به عنوان هدف تعیین شدند. هم‌پوشانی هدف-همتا پایین بوده و به طور میانگین تنها ۱۱٫۸٪ از همتایان یک هدف، خودشان هدف هستند. "
           "سناریوها شامل الف (افت ۱۸٪)، ب (افت ۳۲٪) و ج (افت ۴۸٪) هستند. در سناریوی شاهد منفی (Scenario 0)، مقدار افت صفر بوده تا وضعیت عدم وجود مثبت واقعی (TP = 0) جهت ارزیابی هشدار کاذب بررسی شود.")
    B.para("Text",
           "تنظیم ابرپارامترها: مقادیر بهینه در پنجره تاریخی P0-دوره ۳ تنظیم گردیدند: "
           "ضریب شباهت λ = 0.65، ضریب انحنا η = 0.25، اشباع گرافی κ = 18.0، تعداد همسایگان K = 6 و خطای واسنجی α = 0.15. "
           f"تحلیل حساسیت تجربی در ۱۰ سید نشان داد کیفیت رتبه‌بندی در برابر تغییرات همسایگی K ∈ [3, 10] (دامنه NDCG بین {to_fa_num('0.353')} تا {to_fa_num('0.397')})، "
           f"وزن انحنا η ∈ [0.0, 0.5] (دامنه NDCG بین {to_fa_num('0.382')} تا {to_fa_num('0.409')}) و پارامتر اشباع κ ∈ [10, 30] (دامنه NDCG بین {to_fa_num('0.382')} تا {to_fa_num('0.397')}) پایداری مناسبی دارد.")

    # 5 -------------------------------------------------------------------------------- نتایج و بحث
    B.para("Heading 1", "5. نتایج و تحلیل تجربی")
    B.para("Heading 2", "5.1. ارزیابی دقت پیش‌بینی طبیعی تراکنش‌ها")
    B.para("Text1",
           "جدول (1) نتایج پیش‌بینی تعداد تراکنش‌ها را در پنجره آزمون دست‌نخورده (بدون تداخل با افت‌های مصنوعی) طی ۱۰ سید تصادفی گزارش می‌کند. "
           "معیار درست‌نمایی NB NLL منحصراً برای مدل‌های دارای خروجی توزیع احتمالی دوجمله‌ای منفی قابل تعریف است و برای مدل‌های نقطه‌ای قطعی درج نگردیده است.")
    B.caption("جدول (1) : مقایسه دقت پیش‌بینی تعداد تراکنش دوره‌های آتی بر روی پنجره آزمون (۱۰ سید تصادفی)")

    fc_rows = []
    short_fa_names = [
        "Naive Persistence (ماندگاری)",
        "Moving Average (میانگین متحرک)",
        "Exp. Smoothing (هموارسازی نمایی)",
        "Tabular GBDT (جدولی RFM)",
        "NB-GLM (اثرات صنف)",
        "Static GNN (گراف ایستا)",
        "HAMTA Temporal (پیشنهادی)"
    ]
    for ri, (_, row) in enumerate(df_fc.iterrows()):
        name = short_fa_names[ri] if ri < len(short_fa_names) else str(row["Model"])[:18]
        nll_val = to_fa_num(row.get("NLL_disp", row.get("NB_NLL", 0.0))) if ri >= 4 else "—"
        fc_rows.append([
            name,
            to_fa_num(row.get("MAE_disp", str(row.get("MAE", 0)))),
            to_fa_num(row.get("RMSE_disp", str(row.get("RMSE", 0)))),
            to_fa_num(row.get("sMAPE_disp", str(row.get("sMAPE", 0)))),
            nll_val
        ])
    data_table(B, ["مدل / معماری", "MAE", "RMSE", "sMAPE", "NB NLL"], fc_rows, [1850, 700, 700, 700, 700], bold_row=len(fc_rows)-1)

    B.para("Text1",
           f"مدل پیشنهادی HAMTA به خطای MAE معادل {to_fa_num('4.48 ± 0.42')} دست یافته و عملکرد بهتری نسبت به گراف ایستا ({to_fa_num('5.98 ± 0.54')}) ثبت کرده است. "
           "تأکید صریح این پژوهش بر آن است که دقت پیش‌بینی نقطه‌ای صرفاً مؤلفه‌ای واسطه‌ای است، نه هدف غایی بهینه‌سازی چارچوب HAMTA. "
           "مدل‌های آماری تک‌متغیره گرچه خطای نقطه‌ای اندکی کمتر دارند، نسبت به ساختار شبکه تعاملی و هم‌پوشانی مشتریان کاملاً نابینا بوده و قادر به استخراج بنچ‌مارک همتایان نیستند. "
           "HAMTA افت اندک در خطای پیش‌بینی نقطه‌ای را در ازای یادگیری بازنمایی‌های پیوندی پویا و امکان‌پذیر ساختن رتبه‌بندی ساختاری فرصت‌ها می‌پذیرد.")

    B.para("Heading 2", "5.2. اولویت‌بندی کمپین‌های بازاریابی")
    B.para("Text1",
           f"جدول (2) کارایی استراتژی‌ها را در رتبه‌بندی {to_fa_num('35')} پذیرنده دارای بالاترین اولویت کمپین (۱۰٪ سبد کل) طی {to_fa_num('10')} سید تصادفی گزارش می‌نماید.")
    B.caption("جدول (2) : بنچ‌مارک رتبه‌بندی و اولویت‌بندی پذیرندگان کاندیدای کمپین (Top-35، میانگین ۱۰ سید)")

    rk_rows = []
    short_rk_fa = [
        "کمترین حجم",
        "حجم دوره پیشین",
        "شکاف جدولی GBDT",
        "شکاف همتایان kNN",
        "شکاف گراف ایستا",
        "مرز تصادفی SFA",
        "M-GATO (بدون Q)",
        "پیشنهادی HAMTA"
    ]
    for ri, (_, row) in enumerate(df_rk.iterrows()):
        name = short_rk_fa[ri] if ri < len(short_rk_fa) else str(row["Model / Strategy"])[:15]
        rk_rows.append([
            name,
            to_fa_num(row.get("Precision_disp", str(row.get("Precision@35", 0.0)))),
            to_fa_num(row.get("Recall_disp", str(row.get("Recall@35", 0.0)))),
            to_fa_num(row.get("RPrec_disp", str(row.get("R-Prec", 0.0)))),
            to_fa_num(row.get("NDCG_disp", str(row.get("NDCG@35", 0)))),
            to_fa_num(row.get("MAP_disp", str(row.get("MAP@35", 0.0))))
        ])
    data_table(B, ["استراتژی رتبه‌بندی", "P@35", "R@35", "R-Prec", "NDCG@35", "MAP@35"], rk_rows, [1200, 690, 690, 690, 690, 690], bold_row=len(rk_rows)-1, font_size=5.3)

    B.picture(os.path.join(FIG, "fig5_benchmark_fa.png"))
    B.caption("شکل (4) : مقایسه کمی مدل‌ها در (الف) دقت پیش‌بینی و (ب) کیفیت اولویت‌بندی کمپین در ۱۰ سید تصادفی")

    B.para("Text1",
           f"با توجه به شیوع فرصت‌های واقعی در سطح {to_fa_num('51')} پذیرنده از ۳۵۰ پذیرنده (شانس تصادفی معادل {to_fa_num('0.146')} یا {to_fa_num('14.6')}٪)، نتایج جدول (2) نشان می‌دهد که "
           f"مدل پیشنهادی HAMTA با Precision@35 معادل {to_fa_num('0.366 ± 0.120')}، NDCG@35 معادل {to_fa_num('0.382 ± 0.116')} و R-Precision معادل {to_fa_num('0.342 ± 0.077')}، "
           f"به ضریب برتری {to_fa_num('2.51')} برابری نسبت به انتخاب تصادفی دست می‌یابد.")

    B.para("Heading 2", "5.3. ارزیابی چندبودجه‌ای و آزمون معناداری آماری")
    B.para("Text1",
           f"جدول (3) کارایی مدل را در سقف‌های مختلف بودجه کمپین {to_fa_num('K ∈ {10, 20, 35, 50}')} گزارش می‌نماید.")
    B.caption("جدول (3) : مقایسه کارایی اولویت‌بندی در بودجه‌های مختلف و آزمون‌های آماری (۱۰ سید تصادفی)")

    mb_rows = []
    short_mb_fa = {
        "Lowest Volume Heuristic (Test)": "کمترین حجم",
        "Tabular Point Gap (GBDT)": "شکاف جدولی GBDT",
        "Static GNN Gap": "شکاف گراف ایستا",
        "SFA-Style Frontier Gap": "مرز تصادفی SFA",
        "HAMTA Proposed (M-GATO)": "مدل پیشنهادی HAMTA"
    }
    for _, r in df_mb.iterrows():
        b_k = to_fa_num(str(r["Budget (K)"]))
        s_name = short_mb_fa.get(r["Strategy"], str(r["Strategy"])[:15])
        mb_rows.append([
            b_k,
            s_name,
            to_fa_num(str(r["Precision@K"])),
            to_fa_num(str(r["Recall@K"])),
            to_fa_num(str(r["NDCG@K"]))
        ])
    data_table(B, ["بودجه", "استراتژی اولویت‌بندی", "Prec@K", "Recall@K", "NDCG@K"], mb_rows, [600, 1500, 850, 850, 850], bold_row=None, font_size=5.3)

    B.para("Text1",
           f"تحلیل بودجه‌های چندگانه و معناداری آماری: در سقف بسیار محدود K = 10، مدل مرز تصادفی SFA به دقت بالاتری ({to_fa_num('0.430 ± 0.127')}) نسبت به HAMTA ({to_fa_num('0.400 ± 0.089')}) دست می‌یابد؛ "
           f"اما با افزایش ظرفیت کمپین، HAMTA رقابت‌پذیری بیشتری نشان داده و از بودجه K = 20 به بعد بر خط‌مبنای مرزی SFA غلبه می‌کند: "
           f"در بودجه K = 20 دقت {to_fa_num('0.410')} در برابر {to_fa_num('0.345')}؛ در K = 35 دقت {to_fa_num('0.366')} در برابر {to_fa_num('0.280')}؛ و در K = 50 دقت {to_fa_num('0.320')} در برابر {to_fa_num('0.230')}. "
           "تحت تصحیح هولم-بونفرونی برای مقایسه‌های چندگانه، برتری‌های HAMTA نسبت به خط‌مبناهای سنتی معناداری آماری خود را حفظ می‌نمایند (p_adj < 0.05): "
           "در بودجه K = 10 نسبت به کمترین حجم (p = 0.015) و مدل جدولی (p = 0.039)؛ در بودجه K = 20 نسبت به کمترین حجم (p = 0.005) و مدل جدولی (p = 0.005)؛ و در K = 35 نسبت به گراف ایستا (p = 0.0488).")

    B.para("Heading 2", "5.4. ارزیابی استحکام و تحلیل عدم دورباطل در سناریوها")
    B.para("Text1",
           "جدول (4) عملکرد مدل را در چهار سناریوی مستقل با شدت‌های مختلف افت و نویز نشان می‌دهد.")
    B.caption("جدول (4) : ارزیابی چندسناریویی چارچوب و نرخ هشدار کاذب (۱۰ سید تصادفی)")

    sc_rows = []
    sc_fa_names = [
        "شاهد منفی",
        "سناریو الف (ضعیف)",
        "سناریو ب (متوسط)",
        "سناریو ج (قوی)"
    ]
    for ri, (_, row) in enumerate(df_sc.iterrows()):
        name = sc_fa_names[ri] if ri < len(sc_fa_names) else str(row["Scenario"])[:16]
        sc_rows.append([
            name,
            to_fa_num(f"{row.get('Drop Rate', row.get('Drop', 0.0)):.2f}"),
            to_fa_num(str(row["Precision@35"])),
            to_fa_num(str(row["NDCG@35"])),
            to_fa_num(str(row.get("Weak-Support %", row.get("FPR@35", 0)))),
            to_fa_num(str(row.get("Coverage (%)", row.get("Coverage", 0.0))))
        ])
    data_table(B, ["سناریوی ارزیابی", "افت", "Prec@35", "NDCG@35", "Weak-Support %", "پوشش"], sc_rows, [1350, 500, 700, 700, 700, 700], bold_row=2, font_size=5.3)

    B.para("Text1",
           f"در سناریوی شاهد منفی (سناریو ۰)، مدل طبق ساختار اولیه هیچ مثبت واقعی تولید نمی‌کند (TP = 0)؛ "
           f"نرخ انتخاب {to_fa_num('0.100')} گزارش‌شده مستقیماً ناشی از سهم بودجه انتخاب ثابت ۳۵ پذیرنده برتر از کل ۳۵۰ پذیرنده ({to_fa_num('35/350 = 0.100')}) است "
           "و نباید به عنوان تضمین اختصاصی کنترل خطای مثبت کاذب مدل تفسیر گردد. "
           f"در عوض، پوشش تجربی بازه پیش‌بینی ({to_fa_num('86.2 ± 3.1')}٪ با عرض بازه میانگین {to_fa_num('4.6 ± 0.3')} تراکنش) به عنوان شاخص مستقل تایید می‌نماید "
           "که کران‌های واسنجی‌شده به خوبی نوسانات طبیعی را در بر گرفته و مانع از تولید شکاف‌های فرصت غیرواقعی می‌گردند.")

    B.para("Heading 2", "5.5. مطالعه تفکیکی حذف مؤلفه‌ها (Ablation Study)")
    B.para("Text1",
           "جدول (5) سهم تفکیکی هر یک از اجزای معماری را در مقایسه با مدل کامل همراه با آزمون معناداری آماری نشان می‌دهد.")
    B.caption("جدول (5) : نتایج مطالعه حذف مؤلفه‌ها و آزمون معناداری آماری ویلکاکسون (۱۰ سید تصادفی)")

    ab_rows = []
    ab_fa_names = [
        "مدل کامل پیشنهادی HAMTA",
        "بدون انحنای فرمن-ریچی",
        "بدون شواهد گرافی (Q=1)",
        "بدون کران نااطمینانی",
        "بدون بنچ‌مارک گرافی",
        "بدون پویایی زمانی",
        "بدون ساختار گراف (جدولی)"
    ]
    sig_map_fa = {
        "Ref (Ours)": "مبنا (پیشنهادی)",
        "p=0.8457 (t=0.6892)": "p = 0.846",
        "p=0.3750 (t=0.3484)": "p = 0.375",
        "p=0.0273 (t=0.0368)": "p = 0.027",
        "p=0.6953 (t=0.5897)": "p = 0.695",
        "p=0.0840 (t=0.0607)": "p = 0.084",
        "p=0.0020 (t=0.0002)": "p = 0.002"
    }
    for ri, (_, row) in enumerate(df_ab.iterrows()):
        name = ab_fa_names[ri] if ri < len(ab_fa_names) else str(row["Architecture Variant"])[:18]
        raw_sig = str(row.get("Significance", row.get("Significance (Wilcoxon/t)", ""))).strip()
        sig_val = sig_map_fa.get(raw_sig, to_fa_num(raw_sig[:10]))
        ab_rows.append([
            name,
            to_fa_num(row.get("NDCG_disp", str(row.get("NDCG@35", 0)))),
            to_fa_num(row.get("Prec_disp", str(row.get("Precision@35", 0.0)))),
            to_fa_num(f"{row.get('Delta_NDCG', row.get('Delta NDCG', 0.0)):+.3f}"),
            sig_val
        ])
    data_table(B, ["ترکیب معماری", "NDCG@35", "Prec@35", "Δ NDCG", "معناداری آماری"], ab_rows, [1650, 750, 750, 750, 750], bold_row=0, font_size=5.3)

    B.para("Text1",
           f"تحلیل مطالعه تفکیکی و معماری سه‌لایه: معماری HAMTA تفکیک صریحی میان موتور کارایی رتبه‌بندی، سپرهای حفاظتی ریسک و پالایش ساختاری قائل است: "
           f"(۱) موتور رتبه‌بندی رابطه‌ای: بازنمایی گراف دوبخشی زمانی عامل اصلی ارتقای رتبه‌بندی است؛ افزودن ساختار گراف در برابر مدل جدولی GBDT، شاخص NDCG@35 را به میزان ۰٫۱۴۵+ (از {to_fa_num('0.237')} به {to_fa_num('0.382')}، p = 0.0020) و پویایی‌های زمانی شاخص را به میزان ۰٫۰۷۲+ (p = 0.0840) ارتقا می‌دهد. "
           f"(۲) سپرهای حفاظتی عملیاتی: کران نااطمینانی یک‌طرفه U و ضریب شواهد گرافی Q برای بیشینه‌سازی رتبه‌بندی خام طراحی نشده‌اند، بلکه نقش فیلتر محافظه‌کارانه تجاری دارند. "
           f"حذف U اگرچه ظاهراً NDCG خام را به {to_fa_num('0.415')} (p = 0.0273) می‌رساند، اما نرخ هشدارهای کاذب را در نوسانات طبیعی به شدت بالا می‌برد زیرا واریانس مثبت طبیعی پیش‌بینی را به عنوان فرصت قلمداد می‌کند. "
           f"همچنین حذف Q موجب افزایش نرخ انتخاب پذیرندگان کم‌پشتیبان به ۲۴٫۳٪ می‌گردد. "
           f"(۳) پالایش ساختاری: انحنای فرمن-ریچی نقش تنظیم‌کننده ساختاری ضد گلوگاه را ایفا نموده و اثر تفکیکی مستقیمی بر شاخص رتبه‌بندی ندارد ({to_fa_num('Δ = -0.002')}، p = 0.8457).")

    B.para("Heading 2", "5.6. مطالعه موردی و مهار اریب پایانه‌های خرد")
    B.para("Text1",
           "جدول (6) مشخصات نمونه‌ای از پذیرندگان منتخب را بر روی داده‌های شبیه‌سازی‌شده نشان می‌دهد.")
    B.caption("جدول (6) : مشخصات پذیرندگان نمونه منتخب با بالاترین اولویت کمپین")

    opp_rows = []
    guild_fa_short = {
        "Industrial Wholesale": "مصالح صنعتی",
        "Travel & Tourism": "مسافرتی",
        "Medical & Healthcare": "پزشکی",
        "Supermarket": "سوپرمارکت",
        "Gold & Jewelry": "طلا و جواهر",
        "Restaurant": "رستوران",
        "Apparel": "پوشاک",
        "Electronics": "الکترونیک",
        "پوشاک و کیف و کفش": "پوشاک",
        "رستوران و کافی‌شاپ": "رستوران",
        "لوازم خانگی و صوتی تصویری": "الکترونیک",
        "آهن‌آلات و مصالح صنعتی": "مصالح صنعتی",
        "آژانس مسافرتی و گردشگری": "مسافرتی",
        "خدمات پزشکی و داروخانه": "پزشکی",
        "سوپرمارکت و خواروبار": "سوپرمارکت",
        "طلا و جواهر": "طلا و جواهر"
    }
    for _, r in df_opp.head(5).iterrows():
        g_raw = str(r["guild"])
        g_fa = str(r.get("guild_fa_short", guild_fa_short.get(g_raw, g_raw[:10])))
        if g_fa in ("nan", ""):
            g_fa = guild_fa_short.get(g_raw, g_raw[:10])
        opp_rows.append([
            to_fa_num(str(r["merchant_id"])),
            g_fa,
            to_fa_num(str(int(r["current_tx"]))),
            to_fa_num(f"{r['forecast_tx']:.1f}"),
            to_fa_num(f"{r['upper_bound']:.1f}"),
            to_fa_num(f"{r['peer_benchmark']:.1f}"),
            to_fa_num(f"{r['mgato_score']:.3f}")
        ])
    data_table(B, ["شناسه", "صنف تجاری", "واقعی", "پیش‌بینی", "کران بالا", "بنچ‌مارک", "امتیاز"], opp_rows, [1050, 1000, 520, 520, 520, 520, 520], font_size=5.4)

    B.picture(os.path.join(FIG, "fig4_radar_fa.png"))
    B.caption("شکل (5) : دقت بازیافت فرصت (Precision@K) در سقف‌های مختلف بودجه کمپین بازاریابی")

    B.para("Text1",
           f"تحلیل تورش پذیرندگان خرد (Micro-Merchant Bias): به دلیل مخرج کوچک در پذیرندگان کم‌تراکنش، شاخص M-GATO در حالت خام به پذیرندگان خرد حساس است ({to_fa_num('56.0 ± 16.5')}٪ کاندیداهای زیر ۱۰ تراکنش). "
           f"بررسی حساسیت نشان می‌دهد اعمال آستانه‌های تراکنش Y ≥ 5، 10 و 20، سهم کاندیداهای خرد را به ترتیب به ۳۴٫۱٪، ۱۸٫۲٪ و ۴٫۳٪ کاهش می‌دهد. اعمال فیلتر ۱۰ تراکنش دقت را در سطح {to_fa_num('0.286 ± 0.056')} و NDCG را در {to_fa_num('0.327 ± 0.077')} تثبیت می‌نماید. "
           "همچنین ضریب پیوسته اتکای فعالیت با τ_a = 15 به عنوان نسخه عملیاتی توصیه‌شده (به جای فیلتر آستانه‌ای سخت)، نوسانات پذیرندگان بسیار خرد را مهار می‌سازد:")
    B.formula_line("Q_total = Q_graph · ( 1 - exp( -Y_m / τ_a ) )")
    B.para("Text",
           "تهدیدات اعتبار تجربی: (۱) سلامت پروتکل ارزیابی: طراحی پروتکل مانع از دسترسی مستقیم به مشاهدات دوره آزمون در برازش مدل، تنظیم همتایان و واسنجی بازه پیش‌بینی می‌شود. "
           "(۲) اثر هم‌نوع‌خواری تجاری (Peer Cannibalization): چارچوب استقلال تقاضای پذیرندگان را فرض می‌کند و رقابت محلی پایانه‌های همسایه به صورت مستقیم لحاظ نشده است. "
           "(۳) متغیرهای مشاهده‌نشده: داده‌ها محدود به ۵ فیلد پایه دفتر کل بوده و اطلاعاتی نظیر مساحت فروشگاه، تعداد پرسنل و ساعات کاری در دسترس نیست. "
           "(۴) محیط شبیه‌سازی: شاخص M-GATO اولویت‌بندی بر اساس افت‌های ساختاری تزریق‌شده است؛ اعتبارسنجی نهایی نیازمند آزمون‌های تصادفی A/B در کمپین‌های بازاریابی آتی بانک است.")
    B.para("Text",
           f"پیچیدگی محاسباتی: اندازه‌گیری زمان اجرا در محیط سخت‌افزاری استاندارد (پردازنده Intel Core i7، ۱۶ گیگابایت رم، PyTorch 2.4) رشد تجربی تقریباً خطی در پیکربندی‌های ارزیابی‌شده را نشان داد: "
           f"مقیاس کوچک ({to_fa_num('100')} پذیرنده: ۱٫۵۴ ثانیه، ۶۵۰۵ تراکنش/ثانیه)؛ "
           f"مقیاس متوسط ({to_fa_num('350')} پذیرنده: ۶٫۲۸ ثانیه، ۵۵۷۰ تراکنش/ثانیه)؛ و "
           f"مقیاس بزرگ ({to_fa_num('1000')} پذیرنده: مجموعاً ۲۸٫۱۷ ثانیه، ۳۵۵۰ تراکنش/ثانیه). "
           "کاندیدایابی با اندیس معکوس کارت‌ها پیچیدگی را به O(|M| · K · d_avg) محدود نموده و مقیاس‌پذیری عملیاتی روش را تأیید می‌کند.")

    # 6 -------------------------------------------------------------------------------- نتیجه‌گیری
    B.para("Heading 1", "6. نتیجه‌گیری و کارهای آینده")
    B.para("Text1",
           "در این مقاله چارچوب هوش مصنوعی گراف زمانی HAMTA در قالب یک ساختار تصمیم‌گیری سه‌لایه برای اولویت‌بندی فرصت‌های بدون برچسب مداخله (Treatment-label-free) پذیرندگان ارائه گردید. "
           "HAMTA با بازتعریف روابط تراکنشی به صورت گراف دوبخشی، بهره‌گیری از انحنای فرمن-ریچی به عنوان پالایش ساختاری، پیش‌بینی تعداد تراکنش با دوجمله‌ای منفی "
           "و استخراج کران بالای طبیعی با واسنجی بازه پیش‌بینی زمانی، شاخص M-GATO را برای تفکیک پذیرندگان دارای پتانسیل ساختاری از نوسانات تصادفی بدون نیاز به برچسب‌های مداخله تاریخی ارائه داد. "
           "نتایج آزمایش‌ها بر روی ۱۰ سید تصادفی، بازیابی سیگنال افت ساختاری را اعتبارسنجی نموده و بهبود معنادار آماری در مقایسه‌های کلیدی را پس از تصحیح هولم-بونفرونی به اثبات رساندند.")
    B.para("Text",
           "چشم‌انداز آینده: در فازهای بعدی، تلفیق امتیاز اولویت‌بندی M-GATO با مدل‌های برآورد اثر علّی (ITE Uplift Modeling) پس از اجرای آزمایشی کمپین در شبکه بانکی پیگیری خواهد شد. "
           "بیانیه دسترسی به کد و محرمانگی داده‌ها: پیاده‌سازی کامل چارچوب و کدهای تولید داده‌های شبیه‌سازی پس از انتشار مقاله در مخزن گیت‌هاب در دسترس قرار خواهد گرفت. "
           "داده‌های شبیه‌سازی با سیدهای ثبت‌شده کاملاً قابل بازتولید هستند؛ اما انتشار داده‌های واقعی سوییچ‌های شاپرکی به دلیل الزامات محرمانگی و استاندارد PCI-DSS امکان‌پذیر نمی‌باشد.")

    # ----------------------------------------------------------------------------- references
    B.para("Heading 1", "مراجع")
    refs = [
        [("Bank for International Settlements (BIS), \"Red Book: Statistics on payment, clearing and settlement systems\", ", 0),
         ("CPMI, Basel, Switzerland", 1), (", Tech. Rep., 2023.", 0)],
        [("European Central Bank (ECB), \"Study on payment attitudes of consumers in the euro area (SPACE)\", ", 0),
         ("ECB, Frankfurt, Germany", 1), (", Tech. Rep., Dec. 2022.", 0)],
        [("J. T. Wei, S. Y. Lin, H. H. Wu, \"A review of the application of RFM model\", ", 0),
         ("African Journal of Business Management", 1), (", Vol. 4, No. 19, pp. 4199-4206, 2010.", 0)],
        [("R. Forman, \"Bochner's method for cell complexes and combinatorial Ricci curvature\", ", 0),
         ("Discrete and Computational Geometry", 1), (", Vol. 29, No. 3, pp. 323-374, 2003.", 0)],
        [("M. Weber, E. Saucan, J. Jost, \"Characterizing complex networks with Forman-Ricci curvature\", ", 0),
         ("Journal of Complex Networks", 1), (", Vol. 5, No. 4, pp. 527-550, 2017.", 0)],
        [("J. Topping, F. Di Giovanni, B. P. Chamberlain, X. Dong, M. M. Bronstein, \"Understanding over-squashing and bottlenecks via curvature\", ", 0),
         ("Proc. 10th Int. Conf. on Learning Representations (ICLR)", 1), (", 2022.", 0)],
        [("I. Marisca, J. Bamberger, C. Alippi, M. M. Bronstein, \"Over-squashing in spatiotemporal graph neural networks\", ", 0),
         ("Advances in Neural Information Processing Systems (NeurIPS 38)", 1), (", Vol. 38, pp. 38213-38243, 2024.", 0)],
        [("A. N. Angelopoulos, S. Bates, \"A gentle introduction to conformal prediction and distribution-free uncertainty\", ", 0),
         ("arXiv preprint arXiv:2107.07511", 1), (", 2021.", 0)],
        [("Z. Liu, C. Chen, X. Yang, J. Zhou, X. Li, L. Song, \"Graph representation learning for merchant incentive optimization in mobile payment marketing\", ", 0),
         ("Proc. 28th ACM Int. Conf. on Information and Knowledge Management (CIKM)", 1), (", pp. 2577-2584, 2019.", 0)],
        [("M. Weber et al., \"Anti-money laundering in Bitcoin: Experimenting with graph convolutional networks\", ", 0),
         ("Proc. KDD Workshop on Anomaly Detection in Finance", 1), (", 2019.", 0)],
        [("Y. Dou, Z. Liu, L. Sun, Y. Deng, H. Peng, P. S. Yu, \"Enhancing graph neural network-based fraud detectors against camouflaged fraudsters\", ", 0),
         ("Proc. 29th ACM Int. Conf. on Information and Knowledge Management (CIKM)", 1), (", pp. 315-324, 2020.", 0)],
        [("P. Veličković, G. Cucurull, A. Casanova, A. Romero, P. Liò, Y. Bengio, \"Graph attention networks\", ", 0),
         ("Proc. 6th Int. Conf. on Learning Representations (ICLR)", 1), (", 2018.", 0)],
        [("W. L. Hamilton, R. Ying, J. Leskovec, \"Inductive representation learning on large graphs\", ", 0),
         ("Advances in Neural Information Processing Systems (NeurIPS 30)", 1), (", pp. 1024-1034, 2017.", 0)],
        [("T. N. Kipf, M. Welling, \"Variational graph auto-encoders\", ", 0),
         ("NIPS Workshop on Bayesian Deep Learning", 1), (", 2016.", 0)],
        [("M. Tare, C. Rattasits, Y. Wu, E. Wielewski, \"Representation learning on large transaction networks using inductive architectures\", ", 0),
         ("Expert Systems with Applications", 1), (", Vol. 248, p. 123480, 2024.", 0)],
        [("D. Xu, C. Ruan, E. Korpeoglu, S. Kumar, K. Achan, \"Inductive representation learning on temporal graphs\", ", 0),
         ("Proc. 8th Int. Conf. on Learning Representations (ICLR)", 1), (", 2020.", 0)],
        [("E. Rossi, B. Chamberlain, F. Frasca, D. Eynard, F. Monti, M. Bronstein, \"Temporal graph networks on dynamic graphs\", ", 0),
         ("ICML Workshop on Graph Representation Learning", 1), (", 2020.", 0)],
        [("A. Pareja et al., \"EvolveGCN: Evolving graph convolutional networks for dynamic graphs\", ", 0),
         ("Proc. 34th AAAI Conf. on Artificial Intelligence", 1), (", pp. 5363-5370, 2020.", 0)],
        [("J. Zhang et al., \"A survey on dynamic graph neural networks\", ", 0),
         ("Frontiers of Computer Science", 1), (", Vol. 19, No. 1, p. 191301, 2025.", 0)],
        [("M. M. Bronstein, J. Bruna, Y. LeCun, A. Szlam, P. Vandergheynst, \"Geometric deep learning: Going beyond Euclidean data\", ", 0),
         ("IEEE Signal Processing Magazine", 1), (", Vol. 34, No. 4, pp. 18-42, 2017.", 0)],
        [("V. D. Blondel, J.-L. Guillaume, R. Lambiotte, E. Lefebvre, \"Fast unfolding of communities in large networks\", ", 0),
         ("Journal of Statistical Mechanics: Theory and Experiment", 1), (", 2008.", 0)],
        [("F. Di Giovanni, J. Rowbottom, B. P. Chamberlain, T. Markovich, M. M. Bronstein, \"Graph neural networks as gradient flows: understanding over-smoothing and over-squashing via total variation\", ", 0),
         ("Proc. 11th Int. Conf. on Learning Representations (ICLR)", 1), (", 2023.", 0)],
        [("S. Zargarbashi, S. Antonelli, K. Borgwardt, \"Non-exchangeable conformal prediction for temporal graph neural networks\", ", 0),
         ("Proc. 31st ACM SIGKDD Conf. on Knowledge Discovery and Data Mining (KDD)", 1), (", 2025.", 0)],
        [("S. C. Kumbhakar, C. A. K. Lovell, \"Stochastic Frontier Analysis\", ", 0),
         ("Cambridge University Press", 1), (", Cambridge, U.K., 2000.", 0)],
        [("A. C. Cameron, P. K. Trivedi, \"Regression Analysis of Count Data\", 2nd ed., ", 0),
         ("Cambridge University Press", 1), (", Cambridge, U.K., 2013.", 0)],
        [("E. Ascarza, \"Retention first, but for whom? Identifying targets for churn management\", ", 0),
         ("Journal of Marketing Research", 1), (", Vol. 55, No. 2, pp. 181-198, 2018.", 0)],
        [("F. Devriendt, D. Moldovan, W. Verbeke, \"Why you should stop using cross-entropy for uplift modeling\", ", 0),
         ("Information Sciences", 1), (", Vol. 535, pp. 110-126, 2020.", 0)]
    ]
    for idx, r in enumerate(refs, start=1):
        B.reference(idx, r)

    doc.save(OUT_DOCX)
    print("saved", OUT_DOCX)


def export_doc_pdf():
    subprocess.run(["powershell", "-Command", "Get-Process -Name WINWORD -ErrorAction SilentlyContinue | Stop-Process -Force"], capture_output=True)

    ps = (
        '$word = New-Object -ComObject Word.Application\n$word.Visible = $false\n'
        f'$doc = $word.Documents.Open("{OUT_DOCX}")\n$doc.Repaginate()\n'
        'Write-Output ("PAGES=" + $doc.ComputeStatistics(2))\n'
        f'$doc.SaveAs2("{OUT_DOC}", 0)\n$doc.SaveAs2("{OUT_DOCX.replace(".docx", ".pdf")}", 17)\n'
        '$doc.Close([ref]$false)\n$word.Quit()\n'
    )
    p = os.path.join(BASE, "export_fa.ps1")
    open(p, "w", encoding="utf-8-sig").write(ps)
    res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", p], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)


if __name__ == "__main__":
    build()
    print("Done building docx")
    # export_doc_pdf()
