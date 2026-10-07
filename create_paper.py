"""
Research Paper Document Generator
Generates IEEE-Formatted 2-Column Research Paper Manuscript in:
1. Microsoft Word (.docx and .doc via COM)
2. PDF via Word Automation (.pdf)

Title: "A Temporal Graph AI Framework for Peer-Relative Merchant Opportunity Ranking in Payment Networks"
"""

import os
import sys
import subprocess
import docx
from docx.shared import Inches, Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import pandas as pd
from src.config import cfg

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def set_cols(sec, n_cols=2, space_dxa=240):
    sectPr = sec._sectPr
    cols = sectPr.xpath('./w:cols')
    if cols:
        cols[0].set(qn('w:num'), str(n_cols))
        cols[0].set(qn('w:space'), str(space_dxa))
    else:
        c = OxmlElement('w:cols')
        c.set(qn('w:num'), str(n_cols))
        c.set(qn('w:space'), str(space_dxa))
        sectPr.append(c)


def set_cell_margins(cell, top=25, bottom=25, left=35, right=35):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_cell_shading(cell, color_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))


def remove_table_borders(table):
    tblPr = table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'none')
        tblBorders.append(border)
    tblPr.append(tblBorders)


def format_ieee_table(table, col_widths, borders=True):
    tblPr = table._tbl.tblPr
    for tag in ('w:tblW', 'w:tblLayout', 'w:tblBorders', 'w:tblInd'):
        for el in tblPr.findall(qn(tag)):
            tblPr.remove(el)

    total_w = sum(col_widths)
    tw = OxmlElement('w:tblW')
    tw.set(qn('w:w'), str(total_w))
    tw.set(qn('w:type'), 'dxa')
    tblPr.append(tw)

    lay = OxmlElement('w:tblLayout')
    lay.set(qn('w:type'), 'fixed')
    tblPr.append(lay)

    if borders:
        b = OxmlElement('w:tblBorders')
        for side, sz in (('top', 8), ('bottom', 8), ('insideH', 4)):
            e = OxmlElement(f'w:{side}')
            e.set(qn('w:val'), 'single')
            e.set(qn('w:sz'), str(sz))
            e.set(qn('w:space'), '0')
            e.set(qn('w:color'), '000000' if sz == 8 else '808080')
            b.append(e)
        tblPr.append(b)

    grid = table._tbl.tblGrid
    for gc in list(grid):
        grid.remove(gc)
    for w in col_widths:
        gc = OxmlElement('w:gridCol')
        gc.set(qn('w:w'), str(w))
        grid.append(gc)

    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        for cell, w in zip(row.cells, col_widths):
            tcPr = cell._tc.get_or_add_tcPr()
            for el in tcPr.findall(qn('w:tcW')):
                tcPr.remove(el)
            tcw = OxmlElement('w:tcW')
            tcw.set(qn('w:w'), str(w))
            tcw.set(qn('w:type'), 'dxa')
            tcPr.insert(0, tcw)


def build_word_document():
    doc = docx.Document()

    # ------------------- SECTION 0: TITLE & AUTHORS (1 COLUMN, A4) -------------------
    sec0 = doc.sections[0]
    sec0.page_width = Mm(210)
    sec0.page_height = Mm(297)
    sec0.top_margin = Mm(19.0)
    sec0.bottom_margin = Mm(25.4)
    sec0.left_margin = Mm(15.8)
    sec0.right_margin = Mm(15.8)
    set_cols(sec0, 1, 720)

    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(9.0)
    font.color.rgb = RGBColor(0, 0, 0)

    # Title - Clean IEEE style without marketing subtitle
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(6)
    run_title = p_title.add_run("A Temporal Graph AI Framework for Peer-Relative Merchant Opportunity Ranking in Payment Networks")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(15.0)
    run_title.bold = True

    # Authors - Clean professional titles
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_after = Pt(9)

    run_auth1 = p_auth.add_run("Saeed Aliakbari*¹ and Saeed Shahsavan²\n")
    run_auth1.bold = True
    run_auth1.font.size = Pt(9.5)
    run_auth2 = p_auth.add_run(
        "¹Business Intelligence Specialist, Rayamate Inc., Tehran, Iran (Corresponding Author: saeed.aliakbari@rayamate.ir)\n"
        "²Software Architect, Rayamate Inc., Tehran, Iran (saeed.shahsavan@rayamate.ir)"
    )
    run_auth2.font.size = Pt(8.5)
    run_auth2.italic = True

    # ------------------- SECTION 1: 2-COLUMN BODY (A4) -------------------
    sec1 = doc.add_section(docx.enum.section.WD_SECTION_START.CONTINUOUS)
    sec1.page_width = Mm(210)
    sec1.page_height = Mm(297)
    sec1.top_margin = Mm(19.0)
    sec1.bottom_margin = Mm(25.4)
    sec1.left_margin = Mm(15.8)
    sec1.right_margin = Mm(15.8)
    set_cols(sec1, 2, 240)

    # Abstract & Keywords - Clean text conforming to IEEE rules (No math symbols, @, ±, or citations)
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.space_before = Pt(1)
    p_abs.paragraph_format.space_after = Pt(3)
    p_abs.paragraph_format.line_spacing = 1.01
    r_abs_label = p_abs.add_run("Abstract—")
    r_abs_label.bold = True
    r_abs_label.font.size = Pt(8.5)
    r_abs_text = p_abs.add_run(
        "Payment service providers, acquiring banks, and card clearing switches process massive volumes of transactional records across electronic payment terminals daily. "
        "Traditional merchant intelligence relies predominantly on static tabular heuristics or aggregate volume ranking, which prioritize established high-volume merchants "
        "while remaining topologically blind to relational network dynamics. Crucially, acquiring institutions face a pressing operational need: identifying merchants who, "
        "relative to their structural peers, underperform in expected transaction volume under observational ledgers and thus represent prime candidates for transaction-boosting marketing campaigns. "
        "We propose HAMTA, an end-to-end merchant-centric Temporal Graph AI framework formulated under a dual-component decision architecture: "
        "pairing a relational opportunity ranking engine with operational business safeguards, including one-sided prediction intervals and graph evidence shrinkage, to prevent ungrounded campaign spend. "
        "Operating strictly on five standard transactional fields without external covariates, HAMTA models transactional flows as a discrete-snapshot temporal bipartite card-merchant graph. "
        "Candidate peer structures are induced through co-visiting customer overlap, business category compatibility, and discrete Forman-Ricci curvature. "
        "A temporal graph attention model trained under a chronology-preserving protocol forecasts transaction counts under a Negative Binomial likelihood, "
        "coupled with one-sided empirical prediction interval calibration to establish conservative natural performance bounds. "
        "We formalize the M-GATO score, integrating graph support evidence with relative performance gaps against robust peer benchmarks. "
        "Evaluated on a synthetic 90-day transaction stream spanning 35,000 transactions, 350 merchants, and 1,480 payment cards across 8 business categories over 10 random seeds, "
        "HAMTA achieves a forecasting mean absolute error of 4.48 transactions and delivers campaign targeting precision of 36.6 percent at top-35 selection, "
        "achieving a 2.51-fold improvement over random expectation and establishing an operational, treatment-label-free foundation for merchant acquiring portfolio intelligence."
    )
    r_abs_text.font.size = Pt(8.5)

    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_kw.paragraph_format.space_after = Pt(6)
    p_kw.paragraph_format.line_spacing = 1.01
    r_kw_label = p_kw.add_run("Keywords—")
    r_kw_label.bold = True
    r_kw_label.italic = True
    r_kw_label.font.size = Pt(8.5)
    r_kw_text = p_kw.add_run("Payment Systems, Temporal Graph Neural Networks, Merchant Intelligence, Campaign Targeting, Conformal Prediction, Peer Benchmarking, Forman-Ricci Curvature, FinTech.")
    r_kw_text.font.size = Pt(8.5)

    def add_heading_1(text):
        h = doc.add_paragraph()
        h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        h.paragraph_format.space_before = Pt(5)
        h.paragraph_format.space_after = Pt(1)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.bold = True
        r.font.size = Pt(8.8)
        return h

    def add_heading_2(text):
        h = doc.add_paragraph()
        h.alignment = WD_ALIGN_PARAGRAPH.LEFT
        h.paragraph_format.space_before = Pt(3.5)
        h.paragraph_format.space_after = Pt(1)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.italic = True
        r.font.size = Pt(8.3)
        return h

    def add_para(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(1.5)
        p.paragraph_format.line_spacing = 0.98
        p.paragraph_format.first_line_indent = Inches(0.14)
        r = p.add_run(text)
        r.font.size = Pt(8.3)
        return p

    def add_equation(eq_text, eq_num):
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        remove_table_borders(tbl)
        c0 = tbl.cell(0, 0)
        c1 = tbl.cell(0, 1)
        c0.width = Inches(2.95)
        c1.width = Inches(0.35)
        set_cell_margins(c0, 6, 6, 0, 0)
        set_cell_margins(c1, 6, 6, 0, 0)

        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.paragraph_format.space_before = Pt(0.5)
        p0.paragraph_format.space_after = Pt(0.5)
        r0 = p0.add_run(eq_text)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(7.8)
        r0.italic = True

        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_before = Pt(0.5)
        p1.paragraph_format.space_after = Pt(0.5)
        r1 = p1.add_run(f"({eq_num})")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(7.8)

    def add_column_figure(img_path, caption):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(2.5)
            p_img.paragraph_format.space_after = Pt(1)
            p_img.paragraph_format.keep_with_next = True
            p_img.add_run().add_picture(img_path, width=Inches(3.10))

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_cap.paragraph_format.space_after = Pt(2.5)
            r = p_cap.add_run(caption)
            r.font.size = Pt(7.2)
            r.italic = True

    # ------------------- SECTION I: INTRODUCTION -------------------
    add_heading_1("I. INTRODUCTION")
    add_para(
        "Commercial card payment networks, merchant acquirers, and interbank clearing switches process hundreds of millions of retail transactions daily [1], [2]. "
        "Historically, commercial portfolio management in acquiring institutions has focused heavily on retrospective volume aggregations—such as Recency, Frequency, and Monetary (RFM) scoring [3]—"
        "or gross payment volume (GPV) leaderboards. However, conventional heuristics conflate three fundamentally distinct operational concepts: "
        "Lowest Absolute Volume ≠ Peer-Relative Underperformance ≠ Campaign Growth Opportunity. "
        "For example, consider Merchant A with 50 transactions whose peers within the same business category and shared-customer interaction neighborhood also average 50 transactions: Merchant A is operating at natural baseline. "
        "Conversely, consider Merchant B with 100 transactions whose structural peers achieve 180 transactions: Merchant B exhibits a genuine peer-relative capability gap. "
        "Our objective is not to find merchants with the lowest absolute volume, but rather to identify merchants who, relative to their structural peers, perform below expected capacity under observational transaction streams."
    )
    add_para(
        "Identifying these underperforming yet high-potential merchants is vital for transaction-growth marketing campaigns (e.g., promotional fee discounts, merchant working-capital advances, POS terminal upgrades, or co-branded customer loyalty incentives). "
        "Formulating this problem introduces four core methodological challenges: "
        "(1) Relational Blindness: tabular heuristics treat merchant establishments as isolated rows, discarding bipartite co-spending networks; "
        "(2) Count Overdispersion: merchant transaction frequencies exhibit extreme variance (Var(Y) > E[Y]) that standard Gaussian regression fails to capture; "
        "(3) Misalignment of Forecasting vs. Opportunity Discovery: standard time-series forecasting merely projects inertia, failing to assess whether an underperforming merchant has peer-validated capacity to expand; and "
        "(4) Strict Data Minimization: models must function strictly on five observational transaction fields: "
        "Masked Card Identifier (pan), Monetary Amount (amount), Merchant Identifier (merchant_id), Timestamp (create_date), and Business Category (cast_name)."
    )
    add_para(
        "To resolve these challenges, this paper presents HAMTA, an end-to-end merchant-centric Temporal Graph AI architecture formulated as a three-layer decision framework: "
        "a Relational Opportunity Ranking Engine, Operational Decision Safeguards, and Structural Topological Refinement. "
        "HAMTA establishes a fundamental paradigm shift: cards serve strictly as topological bridges to construct a dynamic bipartite customer-merchant graph, from which Top-K merchant peer structures are induced. "
        "Crucially, the primary objective of HAMTA is Opportunity Ranking & Prioritization under observational transaction streams, NOT one-step point forecasting error minimization. "
        "Univariate statistical smoothers like ETS can achieve lower point forecast error on stationary series, but are topologically blind and incapable of identifying peer gaps. "
        "HAMTA combines temporal graph representation learning with discrete Riemannian curvature [4]–[7] and one-sided temporal prediction intervals [8] to separate expected natural performance from conservative peer benchmarks. "
        "We formalize the M-GATO metric to prioritize merchants for marketing campaigns."
    )
    add_para(
        "Scope & Novelty Positioning: In payment marketing literature, Liu et al. (CIKM 2019) [9] formulated graph representation learning for merchant incentive optimization on Alipay, "
        "optimizing promotional coupon subsidies in a supervised uplift setting with historical campaign response logs. "
        "In contrast, acquiring banks and PSP switches in typical payment networks lack historical campaign logs and counterfactual treatment assignments. "
        "HAMTA resolves this fundamental operational constraint by introducing an observational, treatment-label-free opportunity discovery paradigm: unifying (1) peer-relative opportunity discovery, "
        "(2) temporal graph count forecasting, (3) calibrated one-sided prediction intervals, and (4) graph-support shrinkage into a coherent prioritization framework without requiring historical campaign treatment labels."
    )

    # ------------------- SECTION II: RELATED WORK -------------------
    add_heading_1("II. RELATED WORK")
    add_heading_2("A. Graph Neural Networks in Finance")
    add_para(
        "Graph Neural Networks (GNNs) have shown substantial success in financial forensics, anti-money laundering (AML), and fraud detection [9]–[11]. "
        "Architectures like GCN and GAT [12], [13] model entities as nodes and transactions as edges. Foundational formulations such as variational graph auto-encoders [14] "
        "and inductive architectures on transaction graphs [15] have expanded topological embedding. In merchant marketing, Liu et al. [9] formulated merchant networks for incentive allocation; "
        "however, their model relies on historical promotional logs. Standard acquiring switches operate strictly on observational ledgers, requiring topological peer discovery without campaign treatment labels."
    )
    add_heading_2("B. Temporal Graph Learning")
    add_para(
        "Dynamic transaction networks require continuous-time or discrete-snapshot representation learning. Frameworks such as TGAT [16], TGN [17], and EvolveGCN [18], alongside recent dynamic graph surveys [19], encode temporal event streams "
        "using attention mechanisms and recurrent state updates. These models support temporal representation learning and are trained under chronology-preserving protocols that prevent look-ahead leakage."
    )
    add_heading_2("C. Financial Topologies and Curvature")
    add_para(
        "Transaction graphs frequently exhibit community bottlenecks and degree skewness [20], [21]. In geometric deep learning, discrete Riemannian curvatures—notably Forman-Ricci curvature [4], [5]—"
        "quantify edge bridging properties and mitigate over-squashing in graph neural networks [6], [7], [22], providing natural structural priors for transaction networks."
    )
    add_heading_2("D. Uncertainty & Prediction Interval Calibration")
    add_para(
        "Point forecasts fail to separate structural capability from natural noise. Prediction interval calibration [8] and non-exchangeable conformal methods for temporal graphs [23] provide empirical uncertainty intervals based on historical residuals, "
        "ensuring that random temporal dips are not falsely identified as commercial expansion opportunities. Our interval procedure is empirical one-sided temporal calibration rather than a theoretical non-exchangeable conformal guarantee."
    )
    add_heading_2("E. Peer Benchmarking & Frontier Analysis")
    add_para(
        "In economic modeling, Stochastic Frontier Analysis (SFA) evaluates an entity's operational efficiency relative to an empirical best-practice frontier [24]. "
        "In retail payment ecosystems, merchant performance must be evaluated not against global maxima, but against topological peers sharing overlapping customer interaction neighborhoods."
    )
    add_heading_2("F. Discrete Count Models in Retail Payments")
    add_para(
        "Retail transaction counts exhibit non-negative integer support and overdispersion (Var(Y) > E[Y]). Continuous Gaussian approximations produce negative forecasts and distorted likelihoods. "
        "Discrete count modeling under a Negative Binomial distribution [25] provides a principled likelihood that accounts for quadratic variance scaling without variance collapse."
    )

    # ------------------- SECTION III: PROPOSED METHOD -------------------
    add_heading_1("III. PROPOSED METHOD (HAMTA FRAMEWORK)")
    add_para(
        "The HAMTA framework comprises four operational stages: stream ingestion & bipartite graph construction, Top-K merchant peer graph induction, temporal graph count forecasting with empirical calibration, and M-GATO campaign prioritization (Fig. 1)."
    )

    add_column_figure(
        os.path.join(cfg.FIGURES_DIR, "fig1_framework_architecture.png"),
        "Fig. 1. End-to-end architectural pipeline of the HAMTA framework for merchant opportunity discovery and campaign targeting."
    )

    add_heading_2("A. Problem Formulation & Ledger Schema")
    add_para(
        "Let the transaction stream be formalized as an append-only ledger L = {e_1, e_2, ..., e_N}. Each transaction event e_k is strictly defined by the 5-tuple: "
        "e_k = (pan_k, amount_k, merchant_id_k, create_date_k, cast_name_k), where pan represents the masked card token, amount is monetary volume, "
        "merchant_id is the unique merchant identifier provided by the PSP ledger, create_date is the timestamp, and cast_name is the business category (e.g., Supermarkets, Restaurants, Apparel, Electronics, Medical Clinics, Travel Agencies, Gold & Jewelry, Industrial Wholesale). "
        "From these five raw fields, HAMTA constructs a 16-dimensional merchant node feature vector x_{m, t} ∈ ℝ¹⁶ without external covariates: "
        "(1–4) Temporal volume lags and peer momentum: log transaction count at t-1, t-2, t-3, and peer-neighborhood mean lag; "
        "(5–7) Monetary scale aggregations from transaction amount: log monetary volume log(1 + ∑ amount), mean transaction size, and amount standard deviation; "
        "(8) Customer interaction breadth: number of distinct masked card identifiers |C_{m, t}|; and (9–16) Business category one-hot categorical encoding across the 8 retail guilds. "
        "The feature pipeline follows a strict causal dependency graph: Raw 5 Fields → Historical Peer Graph G_{<=t} → Peer Lag Aggregation → Temporal GNN at time t, strictly avoiding forward leakage. "
        "Transaction amount provides vital economic scale normalization, ensuring peer comparisons occur between economically commensurate enterprises. "
        "The objective is defined at the merchant level: for each merchant m in M, forecast future transaction count Y_{m, t+1} in ℕ_0 for period t+1, and evaluate its structural opportunity against peer benchmark B^G_{m, t+1}."
    )

    add_heading_2("B. Temporal Bipartite Card–Merchant Graph")
    add_para(
        "Within observation window t, interactions form a discrete-snapshot bipartite graph G^(B)_t = (C_t, M_t, E_t). A binary interaction edge exists if card c transacted at least once at merchant m in window t. "
        "Cards function strictly as relational bridges connecting merchant establishments, preserving cardholder anonymity while capturing mutual shared-customer interaction neighborhoods."
    )

    add_heading_2("C. Top-K Merchant Peer Graph & Curvature")
    add_para(
        "To avoid dense O(|M|^2) comparisons, HAMTA employs an inverted bipartite card index to generate candidate peers. An inverted map I(c) retrieves all merchants visited by card c in historical windows. "
        "For target merchant m, candidate peers are gathered from the 2-hop bipartite neighborhood C(m) = ⋃_{c ∈ C_m} I(c) \\ {m} in O(|C_m| · d_card). "
        "Similarity between candidate merchants m and j is computed as:"
    )
    add_equation("S(m, j) = λ · S_covisit(m, j) + (1 - λ) · S_category(m, j)", 1)
    add_para(
        "where S_covisit is the cosine similarity of card interaction incidence vectors v_m, v_j ∈ {0, 1}^{|C|}, S_category is business category match (cast_name), "
        "and λ = 0.65 is calibrated on historical validation data. A max-heap extracts the Top-K peers (K=6) in O(|C(m)| log K), scaling globally as O(|M| · K · d_avg). "
        "Because Top-K peer selection is directed, the peer graph is symmetrized prior to curvature computation: G_peer = Top-K ∪ Top-K^T. "
        "On G_peer, normalized augmented Forman-Ricci curvature F(m, j) is computed using the augmented formulation [4], [5]:"
    )
    add_equation("F(m, j) = (4 - d(m) - d(j) + 3 · Δ(m, j)) / √(d(m) · d(j))", 2)
    add_para(
        "where d(m) is node degree in G_peer, Δ(m, j) is the count of mutual triangles, and √(d(m) · d(j)) is a degree-balancing normalization proposed to prevent dense hubs from dominating curvature scores. Curvature modulates peer weights as a structural refinement:"
    )
    add_equation("w̃_{mj} ∝ w_{mj} · (1 + η · tanh(F(m, j)))", 3)
    add_para("with scale parameter η = 0.25.")

    add_column_figure(
        os.path.join(cfg.FIGURES_DIR, "fig2_graph_topology_communities.png"),
        "Fig. 2. Two-dimensional projection of merchant peer embeddings across eight business categories; red node rings indicate injected opportunity target merchants."
    )

    add_heading_2("D. Temporal Graph Count Forecasting Architecture")
    add_para(
        "The forecasting target is future transaction count Y_{m, t+1}. Because transaction counts exhibit empirical overdispersion (Var(Y)/E[Y] ≈ 3.24), HAMTA trains a temporal GNN under a Negative Binomial likelihood:"
    )
    add_equation("L_NB = -∑_m [ ln Γ(Y_m + φ) - ln Γ(φ) - ln Γ(Y_m + 1) + φ ln(φ / (φ + μ̂_m)) + Y_m ln(μ̂_m / (φ + μ̂_m)) ]", 4)
    add_para(
        "where μ̂_m is predicted mean count and φ is the dispersion parameter. Information is restricted strictly to G_{<=t}; chronology-preserving evaluation protocols prevent test-period leakage. "
        "Architecture Specifications: HAMTA utilizes a 2-layer TGAT-inspired temporal graph attention architecture with time-decay positional encoding. "
        "The model operates with input feature dimension d_in = 16, hidden embedding dimension d_h = 32, and 2 attention heads. "
        "Hidden activations utilize LeakyReLU (alpha = 0.2) with dropout rate 0.15 and layer normalization. "
        "Optimization is performed using Adam (learning rate 0.005, weight decay 1e-4) for 70 epochs with early stopping on Period 3 validation loss, followed by final fitting on Periods 0-3."
    )

    add_heading_2("E. One-Sided Temporal Prediction-Interval Calibration")
    add_para(
        "Rather than heuristic parametric assumptions (± 1.96σ), HAMTA employs one-sided temporal prediction-interval calibration [8] strictly on clean Period 4 historical residuals prior to opportunity injection. "
        "Nonconformity residuals R_m = max(0, Y_m - μ̂_m) evaluate one-sided natural upside prediction deviations. "
        "For nominal miscoverage α = 0.15 (targeting 85% one-sided upper coverage), calibration quantile q_{0.85} = Quantile_{1-α}(R) is extracted. "
        "The Upper Natural Forecast Bound is formalized as:"
    )
    add_equation("U_{m, t+1} = μ̂_{m, t+1} + q_{0.85}", 5)
    add_para(
        "defining the upper performance threshold under business-as-usual conditions. Crucially, because calibration is performed strictly on unperturbed Period 4 data prior to synthetic opportunity injection in Period 5, calibration data are not affected by the synthetic treatment perturbation. "
        "In temporal graphs, empirical validation across 10 random seeds demonstrates robust empirical upper coverage (Coverage = 86.2% ± 3.1% with mean interval width 4.6 ± 0.3 transactions), confirming practical interval calibration without claiming theoretical non-exchangeable guarantees."
    )

    add_heading_2("F. Conservative Graph-Weighted Peer Benchmark (B^G)")
    add_para(
        "To avoid over-optimistic targets, the peer benchmark is constructed from conservative lower prediction bounds of peers: L_{j, t+1} = max(0, μ̂_{j, t+1} - q_j), with q_j = q_{0.85}:"
    )
    add_equation("B^G_{m, t+1} = [ ∑_{j ∈ N_K(m)} w̃_{mj} · L_{j, t+1} ] / [ ∑_{j ∈ N_K(m)} w̃_{mj} ]", 6)
    add_para("This establishes a robust empirical capability benchmark grounded in shared-customer interaction neighborhoods and guild operations.")

    add_heading_2("G. M-GATO Score Formulation & Numerical Walkthrough")
    add_para(
        "The Merchant Graph-Aware Transaction Opportunity score is formulated as:"
    )
    add_equation("Q_{m, t} = 1 - exp(-O_{m, t} / κ)", 7)
    add_equation("M-GATO_{m, t} = Q_{m, t} · [ (B^G_{m, t+1} - U_{m, t+1}) / (B^G_{m, t+1} + ε) ]_+", 8)
    add_para(
        "where [x]_+ = max(0, x), O_{m, t} = ∑_{j ∈ N_K(m)} |C_m ∩ C_j| is total shared customer interactions with top-K peers, and κ = 18.0 is a saturation parameter. "
        "M-GATO formalizes a Forecast-Bound Peer Gap (B^G - U) modulated by graph support, functioning as a Peer-Relative Opportunity Score rather than a measurement of current raw underperformance (B^G - Y). "
        "Notice that actual observed count Y_{m, t} does not appear directly in the numerator of (8). Point forecast μ̂ and calibrated upper bound U already condition on historical transaction activity. "
        "Directly subtracting raw count Y would conflate short-term transient fluctuations with structural opportunity. "
        "Graph support Q_{m, t} ∈ [0, 1] acts as a conservative shrinkage penalty: if a merchant has negligible customer overlap with its peers, Q → 0, down-weighting ungrounded gaps."
    )
    add_para(
        "Numerical Walkthrough: Consider target merchant MERCH_00322 in the Travel Agency guild: Actual count = 100, Model Forecast = 105.0, Calibrated Upper Bound = 112.0. "
        "Its top peers achieve conservative lower bound benchmark B^G = 170.0. With Graph Support Q = 0.90: "
        "Forecast-bound peer gap = 170.0 - 112.0 = 58.0 (relative gap = 58.0 / 170.0 = 0.3412, or 34.1%). "
        "M-GATO = 0.90 · 0.3412 = 0.307. Interpretation: the merchant exhibits a forecast-bound peer gap of 58 transactions above its upper natural bound relative to peer benchmark (whereas the current observed gap is 170 - 100 = 70 transactions)."
    )

    add_column_figure(
        os.path.join(cfg.FIGURES_DIR, "fig3_latent_tsne_comparison.png"),
        "Fig. 3. Pedagogical walkthrough of the M-GATO score formulation: actual transaction volume Y, model forecast μ̂, calibrated upper natural bound U, and conservative peer benchmark B^G."
    )

    # ------------------- SECTION IV: EXPERIMENTAL DESIGN -------------------
    add_heading_1("IV. EXPERIMENTAL DESIGN")
    add_para(
        "To evaluate HAMTA under known ground truth without circular bias, experiments utilize a synthetic payment stream evaluated over 10 random seeds (SEEDS = [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]). "
        "Each dataset comprises 35,000 transactions across 350 merchants and 1,480 unique payment cards over a 90-day observation window. "
        "Business categories follow a predefined synthetic merchant-category distribution summing to 100.0%: Supermarkets (35%), Restaurants (18%), Apparel (15%), Electronics (10%), Medical Clinics (10%), Travel Agencies (5%), Gold & Jewelry (4%), and Industrial Wholesale (3%). "
        "The 90-day timeline is partitioned into 6 discrete 15-day snapshot windows (Periods 0 to 5). A chronological temporal holdout protocol is enforced: "
        "training on Periods 0-2, validation on Period 3, final fit on Periods 0-3, clean calibration strictly on unperturbed Period 4, and opportunity recovery testing on Period 5. "
        "No test-period data influences graph construction, peer similarity tuning, or conformal calibration."
    )
    add_para(
        "Opportunity Ground-Truth Formalization: In observational payments, commercial growth capacity cannot be directly measured without counterfactual marketing trials. "
        "Therefore, ground truth is formalized strictly as the mathematical recovery of synthetic structural-underperformance targets. "
        "A merchant is labeled Opportunity(m) = 1 iff an exogenous underperformance drop d > 0 was synthetically injected into its transaction generation rate starting in Test Period 5. "
        "Exactly 51 out of 350 merchants (~14.6%) across all 8 business categories are selected via stratified random sampling. Target-peer overlap is low: on average only 11.8% of top-K peers are themselves targets, ensuring uncontaminated peer benchmarks. "
        "Injected drop magnitudes span Scenario A (d = 0.18, noise σ = 3.0), Scenario B (d = 0.32, noise σ = 1.8), and Scenario C (d = 0.48, noise σ = 0.9). "
        "In Scenario 0 (Negative Control), d = 0 for all merchants, establishing an empty positive set (TP = 0 by construction) to evaluate false discovery."
    )
    add_para(
        "Hyperparameter Protocol & Sensitivity Grids: Hyperparameters were tuned on historical training data (Periods 0-2 train, Period 3 validation). "
        "Grid search selected similarity weight λ = 0.65 from {0.4, 0.5, 0.65, 0.8, 0.9}, curvature scale η = 0.25 from {0.0, 0.15, 0.25, 0.35, 0.5}, "
        "saturation parameter κ = 18.0 from {10, 15, 18, 25, 30}, peer neighborhood size K = 6 from {3, 5, 6, 8, 10}, and nominal calibration quantile q = 0.85 from {0.75, 0.80, 0.85, 0.90, 0.95}. "
        "Empirical sensitivity analysis across 10 random seeds demonstrates reasonable stability: NDCG@35 remains bounded across neighborhood sizes K ∈ [3, 10] (NDCG@35 ∈ [0.353, 0.397]), "
        "curvature weights η ∈ [0.0, 0.5] (NDCG ∈ [0.382, 0.409]), and saturation parameters κ ∈ [10, 30] (NDCG ∈ [0.382, 0.397])."
    )

    # ------------------- SECTION V: RESULTS AND DISCUSSION -------------------
    add_heading_1("V. RESULTS AND DISCUSSION")
    add_heading_2("A. Forecasting Accuracy Benchmark")
    add_para(
        "Table I reports natural forecasting metrics on unperturbed test observations across 10 random seeds (mean ± std). "
        "Deterministic point forecasters do not define a parametric count likelihood; hence Negative Binomial NLL is reported strictly for probabilistic models."
    )

    # Table I: Forecasting Benchmark
    fc_path = os.path.join(cfg.OUTPUT_DIR, "hamta_forecasting_benchmark.csv")
    df_fc = pd.read_csv(fc_path) if os.path.exists(fc_path) else pd.DataFrame()

    p_tbl1 = doc.add_paragraph()
    p_tbl1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tbl1.paragraph_format.space_before = Pt(3)
    p_tbl1.paragraph_format.space_after = Pt(2)
    p_tbl1.paragraph_format.keep_with_next = True
    r_tbl1 = p_tbl1.add_run("TABLE I. NATURAL FORECASTING ACCURACY ON UNPERTURBED DATA (10 SEEDS)")
    r_tbl1.bold = True
    r_tbl1.font.size = Pt(7.2)

    headers1 = ["Model / Architecture", "MAE", "RMSE", "sMAPE (%)", "NB NLL"]
    col_w1 = [1700, 750, 750, 850, 750]  # sum = 4800 dxa (~3.33 in)

    table1 = doc.add_table(rows=len(df_fc) + 1, cols=5)
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_ieee_table(table1, col_w1)

    for ci, h in enumerate(headers1):
        cell = table1.cell(0, ci)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(6.5)
        set_cell_shading(cell, "E0E0E0")
        set_cell_margins(cell, 20, 20, 25, 25)

    short_fc_names = [
        "Persistence (Last-Period)",
        "Moving Average (3-Period)",
        "Exp. Smoothing (ETS)",
        "Tabular GBDT (RFM)",
        "NB-GLM (Category)",
        "Static GNN (Bipartite)",
        "HAMTA Temporal (Ours)"
    ]
    for ri, (_, row) in enumerate(df_fc.iterrows(), start=1):
        m_name = short_fc_names[ri - 1] if ri - 1 < len(short_fc_names) else str(row["Model"])[:18]
        mae_s = str(row["MAE_disp"]).replace(" ", "\u00A0") if "MAE_disp" in row else f"{row['MAE']:.2f}"
        rmse_s = str(row["RMSE_disp"]).replace(" ", "\u00A0") if "RMSE_disp" in row else f"{row['RMSE']:.2f}"
        smape_s = str(row["sMAPE_disp"]).replace(" ", "\u00A0") if "sMAPE_disp" in row else f"{row['sMAPE (%)']:.1f}%"
        nll_s = str(row["NLL_disp"]).replace(" ", "\u00A0") if (ri >= 5 and "NLL_disp" in row) else "—"

        vals = [m_name, mae_s, rmse_s, smape_s, nll_s]
        for ci, val in enumerate(vals):
            cell = table1.cell(ri, ci)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.size = Pt(6.0)
            if ri == len(df_fc):
                r.bold = True
                set_cell_shading(cell, "E8F5E9")
            set_cell_margins(cell, 15, 15, 20, 20)

    add_para(
        "As reported in Table I, HAMTA achieves a forecasting MAE of 4.48 ± 0.42 and RMSE of 5.86 ± 0.58 under leak-free chronological evaluation. "
        "Crucially, natural forecast accuracy evaluates baseline prediction fidelity on unperturbed data. "
        "Stationary statistical smoothers (ETS MAE 3.41 ± 0.16, Moving Average MAE 3.51 ± 0.19) minimize one-step point error on stationary series, "
        "but they are topologically blind to relational network structure, co-visiting customer basins, and peer distributions. "
        "Consequently, univariate forecasters cannot induce peer benchmarks or rank relative opportunity gaps. "
        "HAMTA significantly outperforms the static graph baseline (Static GNN MAE 5.98 ± 0.54) and accepts a modest point-forecast trade-off "
        "in order to learn topologically expressive representations essential for downstream peer benchmarking and structural opportunity ranking."
    )

    add_heading_2("B. Campaign Prioritization Ranking Benchmark")
    add_para(
        "Table II details opportunity recovery performance when selecting the Top-35 candidate merchants (a realistic 10% acquiring campaign budget out of 350 merchants) across 10 random seeds."
    )

    # Table II: Ranking Benchmark
    rk_path = os.path.join(cfg.OUTPUT_DIR, "hamta_ranking_benchmark.csv")
    df_rk = pd.read_csv(rk_path) if os.path.exists(rk_path) else pd.DataFrame()

    p_tbl2 = doc.add_paragraph()
    p_tbl2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tbl2.paragraph_format.space_before = Pt(3)
    p_tbl2.paragraph_format.space_after = Pt(2)
    p_tbl2.paragraph_format.keep_with_next = True
    r_tbl2 = p_tbl2.add_run("TABLE II. CAMPAIGN PRIORITIZATION BENCHMARK (TOP-35 MERCHANTS, 10 SEEDS)")
    r_tbl2.bold = True
    r_tbl2.font.size = Pt(7.2)

    headers2 = ["Model / Strategy", "P@35", "R@35", "R-Prec", "NDCG@35", "MAP@35"]
    col_w2 = [1350, 690, 690, 690, 690, 690]  # sum = 4800 dxa (~3.33 in)

    table2 = doc.add_table(rows=len(df_rk) + 1, cols=6)
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_ieee_table(table2, col_w2)

    for ci, h in enumerate(headers2):
        cell = table2.cell(0, ci)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(5.8)
        set_cell_shading(cell, "E0E0E0")
        set_cell_margins(cell, 14, 14, 8, 8)

    short_rk_names = [
        "Lowest Volume",
        "Recent Volume",
        "Tabular GBDT",
        "kNN Peer Gap",
        "Static GNN",
        "SFA Frontier",
        "M-GATO (w/o Q)",
        "HAMTA Proposed"
    ]
    for ri, (_, row) in enumerate(df_rk.iterrows(), start=1):
        r_name = short_rk_names[ri - 1] if ri - 1 < len(short_rk_names) else str(row["Model / Strategy"])[:15]
        p_s = str(row["Precision_disp"]).replace(" ", "\u00A0") if "Precision_disp" in row else f"{row['Precision@K']:.3f}"
        rec_s = str(row["Recall_disp"]).replace(" ", "\u00A0") if "Recall_disp" in row else f"{row['Recall@K']:.3f}"
        rprec_s = str(row["RPrec_disp"]).replace(" ", "\u00A0") if "RPrec_disp" in row else f"{row['R_Precision']:.3f}"
        ndcg_s = str(row["NDCG_disp"]).replace(" ", "\u00A0") if "NDCG_disp" in row else f"{row['NDCG@K']:.3f}"
        map_s = str(row["MAP_disp"]).replace(" ", "\u00A0") if "MAP_disp" in row else f"{row['MAP@K']:.3f}"

        vals = [r_name, p_s, rec_s, rprec_s, ndcg_s, map_s]
        for ci, val in enumerate(vals):
            cell = table2.cell(ri, ci)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.size = Pt(5.5)
            if ri == len(df_rk):
                r.bold = True
                set_cell_shading(cell, "E8F5E9")
            set_cell_margins(cell, 12, 12, 8, 8)

    add_column_figure(
        os.path.join(cfg.FIGURES_DIR, "fig5_benchmark_comparison_bar.png"),
        "Fig. 4. Quantitative benchmark comparison across 10 random seeds: (a) Forecasting accuracy (MAE, lower is better) and (b) Campaign targeting quality (NDCG@35, higher is better)."
    )

    add_para(
        "Under synthetic opportunity prevalence of 51/350 (random expectation = 0.146, 14.6%), Table II confirms that HAMTA Proposed (M-GATO) achieves Precision@35 = 0.366 ± 0.120, "
        "Recall@35 = 0.246 ± 0.081, R-Precision = 0.342 ± 0.077, NDCG@35 = 0.382 ± 0.116, and MAP@35 = 0.180 ± 0.092. R-Precision evaluates precision at R = 51 targets, while MAP@35 denotes mean average precision truncated at rank 35 across seeds. "
        "This represents a 2.51× lift over random selection and substantially outperforms Lowest Volume (P@35 = 0.197 ± 0.053) and Tabular Point Gap (P@35 = 0.214 ± 0.064). "
        "Recall@35 reaches 0.246 ± 0.081, noting that maximum possible Recall@35 under 35 slots for 51 targets is capped at 35/51 = 0.686."
    )

    # Multi-Budget Table & Analysis
    add_heading_2("C. Multi-Budget Ranking & Statistical Significance")
    add_para(
        "To evaluate operational robustness across realistic campaign budget constraints, Table III profiles ranking performance across selection budgets "
        "K ∈ {10, 20, 35, 50} merchants (corresponding to 2.9%, 5.7%, 10.0%, and 14.3% of the merchant portfolio) across 10 random seeds."
    )

    # Table III: Multi-Budget Benchmark
    mb_path = os.path.join(cfg.OUTPUT_DIR, "table2b_multibudget_10seeds.csv")
    df_mb = pd.read_csv(mb_path) if os.path.exists(mb_path) else pd.DataFrame()

    p_tbl_mb = doc.add_paragraph()
    p_tbl_mb.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tbl_mb.paragraph_format.space_before = Pt(3)
    p_tbl_mb.paragraph_format.space_after = Pt(2)
    p_tbl_mb.paragraph_format.keep_with_next = True
    r_tbl_mb = p_tbl_mb.add_run("TABLE III. MULTI-BUDGET CAMPAIGN TARGETING BENCHMARK (10 SEEDS)")
    r_tbl_mb.bold = True
    r_tbl_mb.font.size = Pt(7.2)

    headers_mb = ["Budget", "Targeting Strategy", "Prec@K", "Recall@K", "NDCG@K"]
    col_w_mb = [700, 1550, 850, 850, 850]  # sum = 4800 dxa (~3.33 in)

    table_mb = doc.add_table(rows=len(df_mb) + 1, cols=5)
    table_mb.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_ieee_table(table_mb, col_w_mb)

    for ci, h in enumerate(headers_mb):
        cell = table_mb.cell(0, ci)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(6.0)
        set_cell_shading(cell, "E0E0E0")
        set_cell_margins(cell, 14, 14, 8, 8)

    short_mb_strat = {
        "Lowest Volume Heuristic (Test)": "Lowest Volume",
        "Tabular Point Gap (GBDT)": "Tabular GBDT",
        "Static GNN Gap": "Static GNN",
        "SFA-Style Frontier Gap": "SFA Frontier",
        "HAMTA Proposed (M-GATO)": "HAMTA (M-GATO)"
    }
    for ri, (_, row) in enumerate(df_mb.iterrows(), start=1):
        b_k = str(row["Budget (K)"])
        s_name = short_mb_strat.get(row["Strategy"], str(row["Strategy"])[:15])
        p_val = str(row["Precision@K"]).replace(" ", "\u00A0")
        r_val = str(row["Recall@K"]).replace(" ", "\u00A0")
        n_val = str(row["NDCG@K"]).replace(" ", "\u00A0")

        vals = [b_k, s_name, p_val, r_val, n_val]
        for ci, val in enumerate(vals):
            cell = table_mb.cell(ri, ci)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 1 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val)
            r.font.size = Pt(5.6)
            if "HAMTA" in s_name:
                r.bold = True
                set_cell_shading(cell, "E8F5E9")
            set_cell_margins(cell, 12, 12, 8, 8)

    add_para(
        "Multi-Budget Analysis: At the most restrictive campaign budget (K=10), SFA Frontier Gap achieves higher precision (0.430 ± 0.127) than HAMTA (0.400 ± 0.089), demonstrating the strength of parametric frontiers on severe budget bottlenecks. "
        "However, HAMTA becomes increasingly competitive as campaign capacity expands and outperforms the SFA frontier baseline from K=20 onward in the reported experiments: "
        "(1) At K=20, HAMTA achieves Precision@20 = 0.410 ± 0.109 versus SFA (0.345 ± 0.118), outperforming Lowest Volume (0.200, p_adj = 0.005) and Tabular GBDT (0.265, p_adj = 0.005) under Holm-Bonferroni correction; "
        "(2) At K=35, HAMTA (0.366) exceeds SFA (0.280) and Static GNN (0.286, p_adj = 0.0488); and "
        "(3) At K=50, HAMTA maintains precision 0.320 versus SFA 0.230 while capturing Recall@50 = 0.327 ± 0.069. Secondary comparisons are exploratory unadjusted diagnostics."
    )

    add_heading_2("D. Multi-Scenario Circularity & Robustness Evaluation")
    add_para(
        "Table IV reports performance across four distinct evaluation scenarios, confirming that HAMTA does not merely replicate an injected drop pattern."
    )

    # Table IV: Multi-Scenario Benchmark
    sc_path = os.path.join(cfg.OUTPUT_DIR, "hamta_scenarios_results.csv")
    df_sc = pd.read_csv(sc_path) if os.path.exists(sc_path) else pd.DataFrame()

    p_tbl4 = doc.add_paragraph()
    p_tbl4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tbl4.paragraph_format.space_before = Pt(3)
    p_tbl4.paragraph_format.space_after = Pt(2)
    p_tbl4.paragraph_format.keep_with_next = True
    r_tbl4 = p_tbl4.add_run("TABLE IV. MULTI-SCENARIO BENCHMARK EVALUATION (10 SEEDS)")
    r_tbl4.bold = True
    r_tbl4.font.size = Pt(7.2)

    headers4 = ["Scenario", "Drop", "Prec@35", "NDCG@35", "FPR@35", "Coverage"]
    col_w4 = [1350, 500, 750, 750, 700, 750]  # sum = 4800 dxa (~3.33 in)

    table4 = doc.add_table(rows=len(df_sc) + 1, cols=6)
    table4.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_ieee_table(table4, col_w4)

    for ci, h in enumerate(headers4):
        cell = table4.cell(0, ci)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(6.0)
        set_cell_shading(cell, "E0E0E0")
        set_cell_margins(cell, 14, 14, 8, 8)

    short_sc_names = [
        "Negative Control",
        "Scenario A (Weak)",
        "Scenario B (Medium)",
        "Scenario C (Strong)"
    ]
    for ri, (_, row) in enumerate(df_sc.iterrows(), start=1):
        s_name = short_sc_names[ri - 1] if ri - 1 < len(short_sc_names) else str(row["Scenario"])[:18]
        drop_s = f"{row['Drop Rate']:.2f}"
        p_s = str(row["Precision@35"]).replace(" ", "\u00A0")
        ndcg_s = str(row["NDCG@35"]).replace(" ", "\u00A0")
        fpr_s = str(row["FPR@35"]).replace(" ", "\u00A0")
        cov_s = str(row["Coverage (%)"]).replace(" ", "\u00A0")

        vals = [s_name, drop_s, p_s, ndcg_s, fpr_s, cov_s]
        for ci, val in enumerate(vals):
            cell = table4.cell(ri, ci)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.size = Pt(5.5)
            if ri == 1:
                set_cell_shading(cell, "FFF9C4")
            elif ri == 3:
                r.bold = True
                set_cell_shading(cell, "E8F5E9")
            set_cell_margins(cell, 12, 12, 8, 8)

    add_para(
        "In the negative-control setting (Scenario 0), the model produces no true positives by construction (TP = 0); "
        "the reported 0.10 false-selection rate corresponds directly to the fixed top-35 selection budget (35/350 = 0.10) "
        "and therefore should not be interpreted as a model-specific false-positive guarantee. "
        "Instead, empirical prediction interval coverage (86.2% ± 3.1% with mean interval width 4.6 ± 0.3 transactions) "
        "serves as the independent metric confirming that calibrated bounds successfully accommodate natural volume fluctuations without generating ungrounded opportunity gaps."
    )

    add_heading_2("E. Systematic Component Ablation Study")
    add_para(
        "Table V isolates the contribution of each architectural component across 10 random seeds with paired Wilcoxon signed-rank tests against the full model."
    )

    # Table V: Ablation Study
    ab_path = os.path.join(cfg.OUTPUT_DIR, "hamta_ablation_results.csv")
    df_ab = pd.read_csv(ab_path) if os.path.exists(ab_path) else pd.DataFrame()

    p_tbl5 = doc.add_paragraph()
    p_tbl5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tbl5.paragraph_format.space_before = Pt(3)
    p_tbl5.paragraph_format.space_after = Pt(2)
    p_tbl5.paragraph_format.keep_with_next = True
    r_tbl5 = p_tbl5.add_run("TABLE V. SYSTEMATIC COMPONENT ABLATION STUDY (10 SEEDS)")
    r_tbl5.bold = True
    r_tbl5.font.size = Pt(7.2)

    headers5 = ["Architecture Variant", "NDCG@35", "Prec@35", "Δ NDCG", "Significance"]
    col_w5 = [1600, 750, 750, 700, 1000]  # sum = 4800 dxa (~3.33 in)

    table5 = doc.add_table(rows=len(df_ab) + 1, cols=5)
    table5.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_ieee_table(table5, col_w5)

    for ci, h in enumerate(headers5):
        cell = table5.cell(0, ci)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(6.0)
        set_cell_shading(cell, "E0E0E0")
        set_cell_margins(cell, 14, 14, 8, 8)

    short_ab_names = [
        "Full HAMTA Proposed",
        "w/o Curvature Mod.",
        "w/o Graph Support (Q=1)",
        "w/o Uncertainty Bounds",
        "w/o Graph Benchmark",
        "w/o Temporal Dynamic",
        "w/o Graph (Tabular)"
    ]
    sig_clean = {
        "Ref (Ours)": "Ref (Ours)",
        "p=0.8457 (t=0.6892)": "p = 0.846",
        "p=0.3750 (t=0.3484)": "p = 0.375",
        "p=0.0273 (t=0.0368)": "p = 0.027",
        "p=0.6953 (t=0.5897)": "p = 0.695",
        "p=0.0840 (t=0.0607)": "p = 0.084",
        "p=0.0020 (t=0.0002)": "p = 0.002"
    }
    for ri, (_, row) in enumerate(df_ab.iterrows(), start=1):
        a_name = short_ab_names[ri - 1] if ri - 1 < len(short_ab_names) else str(row["Architecture Variant"])[:18]
        ndcg_s = str(row["NDCG_disp"]).replace(" ", "\u00A0") if "NDCG_disp" in row else f"{row['NDCG@35']:.3f}"
        p_s = str(row["Prec_disp"]).replace(" ", "\u00A0") if "Prec_disp" in row else f"{row['Precision@35']:.3f}"
        delta_s = f"{row['Delta_NDCG']:+.3f}"
        raw_sig = str(row["Significance"]).strip()
        sig_s = sig_clean.get(raw_sig, raw_sig[:12])

        vals = [a_name, ndcg_s, p_s, delta_s, sig_s]
        for ci, val in enumerate(vals):
            cell = table5.cell(ri, ci)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.size = Pt(5.5)
            if ri == 1:
                r.bold = True
                set_cell_shading(cell, "E8F5E9")
            set_cell_margins(cell, 12, 12, 8, 8)

    add_para(
        "Ablation Analysis & Three-Layer Architecture: A superficial inspection of Table V might suggest that omitting uncertainty bounds (NDCG@35 = 0.415 ± 0.095, p = 0.0273) or graph support (NDCG@35 = 0.396 ± 0.102) improves raw ranking metrics. "
        "Crucially, HAMTA's three-layer architecture clarifies their distinct roles: "
        "(1) Relational Ranking Engine: Relational graph information provides the largest measured contribution among the evaluated components, lifting NDCG@35 by +0.145 over tabular GBDT (p = 0.0020) and +0.072 over static GNN (p = 0.0840). "
        "(2) Operational Decision Safeguards: Uncertainty bounds U and graph support Q act as safeguards against false alerts and wasted spend. Omitting U captures synthetic drops aggressively at the cost of high false-alert risk under natural volatility. "
        "Omitting Q inflates weak-support selections (O_m < 5) to 24.3%, recommending relational outliers with negligible peer overlap. "
        "(3) Structural Topological Refinement: Forman-Ricci curvature operates as an optional inductive regularizer against bottleneck over-squashing rather than a ranking metric driver (Δ = -0.002, p = 0.8457). Reported p-values are exploratory unadjusted paired comparisons."
    )

    add_heading_2("F. Qualitative Case Study & Operational Trade-offs")
    add_para(
        "Table VI presents illustrative opportunity candidates discovered by HAMTA on the synthetic dataset, illustrating the mechanics of the M-GATO score."
    )

    # Table VI: Top Opportunities
    opp_path = os.path.join(cfg.OUTPUT_DIR, "hamta_top_opportunities.csv")
    df_opp = pd.read_csv(opp_path) if os.path.exists(opp_path) else pd.DataFrame()

    p_tbl6 = doc.add_paragraph()
    p_tbl6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tbl6.paragraph_format.space_before = Pt(3)
    p_tbl6.paragraph_format.space_after = Pt(2)
    p_tbl6.paragraph_format.keep_with_next = True
    r_tbl6 = p_tbl6.add_run("TABLE VI. TOP DISCOVERED OPPORTUNITY CANDIDATES (ILLUSTRATIVE CASE STUDY)")
    r_tbl6.bold = True
    r_tbl6.font.size = Pt(7.2)

    headers6 = ["Merchant ID", "Category", "Act", "Fore", "Upper", "Peer", "Score"]
    col_w6 = [1050, 1150, 480, 530, 530, 530, 530]  # sum = 4800 dxa (~3.33 in)

    table6 = doc.add_table(rows=min(6, len(df_opp) + 1), cols=7)
    table6.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_ieee_table(table6, col_w6)

    for ci, h in enumerate(headers6):
        cell = table6.cell(0, ci)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(6.0)
        set_cell_shading(cell, "E0E0E0")
        set_cell_margins(cell, 14, 14, 8, 8)

    guild_en_trans = {
        "Industrial Wholesale": "Industrial Wholesale",
        "Travel & Tourism": "Travel Agency",
        "Medical & Healthcare": "Medical Clinics",
        "Supermarket": "Supermarket",
        "Gold & Jewelry": "Gold & Jewelry",
        "Restaurant": "Restaurant",
        "Apparel": "Apparel & Shoes",
        "Electronics": "Electronics",
        "پوشاک و کیف و کفش": "Apparel & Shoes",
        "رستوران و کافی‌شاپ": "Restaurant",
        "لوازم خانگی و صوتی تصویری": "Electronics",
        "آهن‌آلات و مصالح صنعتی": "Industrial Wholesale",
        "آژانس مسافرتی و گردشگری": "Travel Agency",
        "خدمات پزشکی و داروخانه": "Medical Clinics",
        "سوپرمارکت و خواروبار": "Supermarket",
        "طلا و جواهر": "Gold & Jewelry"
    }

    for ri, (_, row) in enumerate(df_opp.head(5).iterrows(), start=1):
        raw_g = str(row["guild"])
        en_g = str(row.get("guild_en", guild_en_trans.get(raw_g, raw_g[:14])))
        if en_g in ("nan", ""):
            en_g = guild_en_trans.get(raw_g, raw_g[:14])
        vals = [
            str(row["merchant_id"]),
            en_g,
            str(int(row["current_tx"])),
            f"{row['forecast_tx']:.1f}",
            f"{row['upper_bound']:.1f}",
            f"{row['peer_benchmark']:.1f}",
            f"{row['mgato_score']:.3f}"
        ]
        for ci, val in enumerate(vals):
            cell = table6.cell(ri, ci)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci <= 1 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.size = Pt(5.5)
            set_cell_margins(cell, 12, 12, 8, 8)

    add_column_figure(
        os.path.join(cfg.FIGURES_DIR, "fig4_radar_persona_profiles.png"),
        "Fig. 5. Opportunity recovery precision (Precision@K) across marketing campaign budgets K in {10, 20, 35, 50} comparing HAMTA with frontier and heuristic baselines (10 random seeds, mean ± std)."
    )

    add_para(
        "Micro-Merchant Bias & Activity Threshold Sensitivity: Because M-GATO calculates a relative performance ratio, 56.0% ± 16.5% of top candidates in the unconstrained formulation are micro-merchants (< 10 transactions) due to ratio sensitivity with small denominators. "
        "Evaluating activity thresholds reveals clear operational trade-offs: Y >= 5 retains 22.4% low-volume terminals with NDCG@35 = 0.355 ± 0.082; Y >= 10 eliminates micro-merchants entirely while maintaining competitive targeting (NDCG@35 = 0.327 ± 0.077, P@35 = 0.286 ± 0.056); "
        "and Y >= 20 restricts targeting to mature enterprises (NDCG = 0.298, P@35 = 0.245). Alternatively, incorporating a continuous exponential discount factor Q_total = Q_graph · (1 - exp(-Y_m / τ_a)) with τ_a = 15 smoothly dampens low-volume noise without hard threshold cuts."
    )
    add_para(
        "Threats to Validity: (1) Peer Cannibalization: the framework assumes independent customer demand; localized competitive cannibalization between neighboring POS terminals is not explicitly modeled. "
        "(2) Omitted Covariates: observational ledgers are restricted to 5 transaction fields; unobserved attributes (store area, operating hours, staffing) may confound natural performance capacity. "
        "(3) Synthetic Benchmark: while synthetic generation enables controlled ground-truth benchmarking across 10 seeds, production PSP environments exhibit greater non-stationary macroeconomic drift. "
        "(4) Absence of Treatment Labels: M-GATO prioritizes observational opportunity rather than estimating causal uplift; active A/B marketing trials are required to measure causal return on investment."
    )
    add_para(
        "Computational Scalability: Profiling across three graph configurations shows approximately linear empirical scaling over the tested configurations across evaluated benchmark ranges (Intel Core i7, 8 cores, 16 GB RAM, PyTorch 2.4, 5 warm-up passes, 10-repetition mean): "
        "Small (100 merchants, 10k tx, 500 cards: 1.54s wall-clock, 6,505 tx/s); Medium (350 merchants, 35k tx, 1.5k cards: 6.28s, 5,570 tx/s); and Large (1,000 merchants, 100k tx, 4k cards: 28.17s wall-clock, 3,550 tx/s). "
        "Candidate generation via inverted bipartite card index is bounded by O(|M| · K · d_avg), avoiding quadratic O(|M|^2) overhead."
    )

    # ------------------- SECTION VI: CONCLUSION -------------------
    add_heading_1("VI. CONCLUSION AND FUTURE WORK")
    add_para(
        "This paper presented HAMTA, a merchant-centric Temporal Graph AI framework establishing a three-layer decision framework for treatment-label-free merchant opportunity discovery and campaign targeting in electronic payment systems. "
        "Operating strictly on standard five-field payment streams, HAMTA establishes discrete-window temporal bipartite graphs, Top-K peer networks modulated by Forman-Ricci curvature, "
        "and Negative Binomial temporal count forecasting. By subtracting calibrated upper natural bounds from conservative peer benchmarks, the M-GATO score identifies merchants exhibiting "
        "structural underperformance relative to their topological peers while filtering ungrounded opportunities through graph evidence shrinkage. "
        "Simulated experiments across 10 random seeds validate the recovery of predefined structural-underperformance targets across multiple campaign budgets, with statistically significant improvements on selected pairwise comparisons against static graph and tabular baselines. "
        "Importantly, this controlled experiment validates the recovery of a predefined structural perturbation signal, not actual incremental campaign response."
    )
    add_para(
        "Future Work: Current validation relies on controlled synthetic streams to establish verified ground truth. "
        "Future research will explore coupling HAMTA's observational opportunity prioritization with causal Individual Treatment Effect (ITE) uplift estimation once active campaign response data is collected in production acquiring environments."
    )
    add_para(
        "Data and Code Availability: The complete Python implementation of HAMTA, baseline algorithms, and synthetic experiment pipelines will be made available upon publication at: "
        "https://github.com/saeedaliakbari4j/hamta-payment-graph-intelligence. "
        "All synthetic experiment streams are fully reproducible via logged random seeds [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]. "
        "Proprietary bank/PSP payment ledger extracts cannot be released due to banking secrecy and PCI-DSS compliance regulations."
    )

    # ------------------- REFERENCES -------------------
    add_heading_1("REFERENCES")
    refs = [
        "[1] Bank for International Settlements (BIS), \"Red Book: Statistics on payment, clearing and settlement systems,\" CPMI, Basel, Tech. Rep., 2023.",
        "[2] European Central Bank (ECB), \"Study on payment attitudes of consumers in the euro area (SPACE),\" ECB, Frankfurt, Tech. Rep., Dec. 2022.",
        "[3] J. T. Wei, S. Y. Lin, and H. H. Wu, \"A review of the application of RFM model,\" African J. Bus. Manag., vol. 4, no. 19, pp. 4199–4206, 2010.",
        "[4] R. Forman, \"Bochner's method for cell complexes and combinatorial Ricci curvature,\" Discrete Comput. Geom., vol. 29, no. 3, pp. 323–374, 2003.",
        "[5] M. Weber, E. Saucan, and J. Jost, \"Characterizing complex networks with Forman-Ricci curvature,\" J. Complex Netw., vol. 5, no. 4, pp. 527–550, 2017.",
        "[6] J. Topping, F. Di Giovanni, B. P. Chamberlain, X. Dong, and M. M. Bronstein, \"Understanding over-squashing and bottlenecks via curvature,\" in Proc. ICLR, 2022.",
        "[7] I. Marisca, J. Bamberger, C. Alippi, and M. M. Bronstein, \"Over-squashing in spatiotemporal graph neural networks,\" in Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 37, pp. 38213–38243, 2024 (publ. 2025).",
        "[8] A. N. Angelopoulos and S. Bates, \"A gentle introduction to conformal prediction and distribution-free uncertainty,\" arXiv:2107.07511, 2021.",
        "[9] Z. Liu, C. Chen, X. Yang, J. Zhou, X. Li, and L. Song, \"Graph representation learning for merchant incentive optimization in mobile payment marketing,\" in Proc. 28th ACM Int. Conf. Inf. Knowl. Manage. (CIKM), 2019, pp. 2577–2584.",
        "[10] M. Weber et al., \"Anti-money laundering in Bitcoin: Experimenting with graph convolutional networks,\" in Proc. KDD Workshop Anomaly Detection in Finance, 2019.",
        "[11] Y. Dou, Z. Liu, L. Sun, Y. Deng, H. Peng, and P. S. Yu, \"Enhancing graph neural network-based fraud detectors against camouflaged fraudsters,\" in Proc. 29th ACM Int. Conf. Inf. Knowl. Manage. (CIKM), 2020, pp. 315–324.",
        "[12] P. Veličković, G. Cucurull, A. Casanova, A. Romero, P. Liò, and Y. Bengio, \"Graph attention networks,\" in Proc. ICLR, 2018.",
        "[13] W. L. Hamilton, R. Ying, and J. Leskovec, \"Inductive representation learning on large graphs,\" in Adv. Neural Inf. Process. Syst. (NeurIPS), 2017, pp. 1024–1034.",
        "[14] T. N. Kipf and M. Welling, \"Variational graph auto-encoders,\" in NIPS Workshop Bayesian Deep Learning, 2016.",
        "[15] M. Tare, C. Rattasits, Y. Wu, and E. Wielewski, \"Representation learning on large transaction networks using inductive architectures,\" Expert Syst. Appl., vol. 248, p. 123480, 2024.",
        "[16] D. Xu, C. Ruan, E. Korpeoglu, S. Kumar, and K. Achan, \"Inductive representation learning on temporal graphs,\" in Proc. ICLR, 2020.",
        "[17] E. Rossi, B. Chamberlain, F. Frasca, D. Eynard, F. Monti, and M. Bronstein, \"Temporal graph networks on dynamic graphs,\" in ICML Workshop Graph Representation Learning, 2020.",
        "[18] A. Pareja et al., \"EvolveGCN: Evolving graph convolutional networks for dynamic graphs,\" in Proc. 34th AAAI Conf. Artif. Intell., 2020, pp. 5363–5370.",
        "[19] J. Zhang et al., \"A survey on dynamic graph neural networks,\" Front. Comput. Sci., vol. 19, no. 1, p. 191301, 2025.",
        "[20] M. M. Bronstein, J. Bruna, Y. LeCun, A. Szlam, and P. Vandergheynst, \"Geometric deep learning: Going beyond Euclidean data,\" IEEE Signal Process. Mag., vol. 34, no. 4, pp. 18–42, 2017.",
        "[21] V. D. Blondel, J.-L. Guillaume, R. Lambiotte, and E. Lefebvre, \"Fast unfolding of communities in large networks,\" J. Stat. Mech. Theory Exp., 2008.",
        "[22] F. Di Giovanni, J. Rowbottom, B. P. Chamberlain, T. Markovich, and M. M. Bronstein, \"Graph neural networks as gradient flows: understanding over-smoothing and over-squashing via total variation,\" in Proc. ICLR, 2023.",
        "[23] S. Zargarbashi, S. Antonelli, and K. Borgwardt, \"Non-exchangeable conformal prediction for temporal graph neural networks,\" in Proc. 31st ACM SIGKDD Conf. Knowl. Discov. Data Min. (KDD), 2025.",
        "[24] S. C. Kumbhakar and C. A. K. Lovell, Stochastic Frontier Analysis. Cambridge, U.K.: Cambridge Univ. Press, 2000.",
        "[25] A. C. Cameron and P. K. Trivedi, Regression Analysis of Count Data, 2nd ed. Cambridge, U.K.: Cambridge Univ. Press, 2013.",
        "[26] E. Ascarza, \"Retention first, but for whom? Identifying targets for churn management,\" J. Mark. Res., vol. 55, no. 2, pp. 181–198, 2018.",
        "[27] F. Devriendt, D. Moldovan, and W. Verbeke, \"Why you should stop using cross-entropy for uplift modeling,\" Inf. Sci., vol. 535, pp. 110–126, 2020."
    ]

    for r_text in refs:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.space_after = Pt(0.5)
        p_ref.paragraph_format.line_spacing = 0.95
        p_ref.paragraph_format.left_indent = Inches(0.18)
        p_ref.paragraph_format.first_line_indent = Inches(-0.18)
        r = p_ref.add_run(r_text)
        r.font.size = Pt(6.5)

    docx_path = os.path.join(cfg.BASE_DIR, "From_Transactional_Data_to_Organizational_Intelligence.docx")
    doc.save(docx_path)
    print(f"[PaperGenerator] Saved IEEE 2-Column Word Document to {docx_path}")
    return docx_path


def export_word_to_doc_and_pdf():
    subprocess.run(["powershell", "-Command", "Get-Process -Name WINWORD -ErrorAction SilentlyContinue | Stop-Process -Force"], capture_output=True)

    ps_content = """$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("D:\\project\\hamta\\From_Transactional_Data_to_Organizational_Intelligence.docx")
$doc.Repaginate()
Write-Output ("PAGES=" + $doc.ComputeStatistics(2))
$doc.SaveAs2("D:\\project\\hamta\\From_Transactional_Data_to_Organizational_Intelligence.doc", 0)
$doc.SaveAs2("D:\\project\\hamta\\From_Transactional_Data_to_Organizational_Intelligence.pdf", 17)
$doc.Close([ref]$false)
$word.Quit()
"""
    ps_path = os.path.join(cfg.BASE_DIR, "export_en.ps1")
    with open(ps_path, "w", encoding="utf-8-sig") as f:
        f.write(ps_content)

    print("[PaperGenerator] Exporting to .doc and .pdf via Word Automation...")
    res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_path], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)


if __name__ == "__main__":
    docx_file = build_word_document()
    export_word_to_doc_and_pdf()
