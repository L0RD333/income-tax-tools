"""Shared helpers: styling, INR formatting, and the FY 2025-26 income-tax engine."""
import os as _os
import streamlit as st

CESS = 0.04

def inr(x):
    x = round(x)
    neg = x < 0
    s = str(abs(int(x)))
    if len(s) > 3:
        last3 = s[-3:]; rest = s[:-3]; parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:]); rest = rest[:-2]
        if rest: parts.insert(0, rest)
        s = ",".join(parts) + "," + last3
    return ("-" if neg else "") + "₹" + s

def style(page_title, page_icon="🧮"):
    st.set_page_config(page_title=page_title, page_icon=page_icon, layout="centered")
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Spectral:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family:'Spectral',Georgia,serif; }
    h1,h2,h3 { font-family:'Fraunces',serif !important; color:#1c4a3a; }
    .stApp { background:#f7f4ed; }
    .brandbar { border-left:3px solid #9a6a1f; padding:6px 0 6px 12px; color:#6b675d;
      font-size:13px; margin-bottom:14px; background:linear-gradient(90deg,#eef2ed,transparent); }
    .brandbar b { color:#1c4a3a; font-family:'Fraunces',serif; }
    .bestcard { border:2px solid #1c4a3a; border-radius:6px; padding:14px 18px; background:#fff; }
    .muted { color:#6b675d; font-size:13px; }
    </style>""", unsafe_allow_html=True)

def brandbar(subtitle):
    st.markdown(f"<div class='brandbar'><b>Rahul</b> — Income Tax Tools<br>{subtitle}</div>",
                unsafe_allow_html=True)

# ----------------------------- income-tax engine -----------------------------
def slab_tax_new(ti):
    bands = [(400000,0),(800000,.05),(1200000,.10),(1600000,.15),
             (2000000,.20),(2400000,.25),(float("inf"),.30)]
    tax, lo = 0.0, 0
    for hi, r in bands:
        if ti > lo: tax += (min(ti,hi)-lo)*r; lo = hi
        else: break
    return tax

def slab_tax_old(ti, age):
    exempt = {"below60":250000,"senior":300000,"super":500000}[age]
    bands = [(exempt,0),(500000,.05),(1000000,.20),(float("inf"),.30)]
    tax, lo = 0.0, 0
    for hi, r in bands:
        if ti > lo: tax += (min(ti,max(hi,exempt))-lo)*r; lo = max(hi,exempt) if r==0 else hi
        else: break
    return tax

def _surcharge_mr(base_tax, ti, regime, age):
    bands = [(5000000,.10),(10000000,.15),(20000000,.25),(50000000,.25 if regime=="new" else .37)]
    rate, thr, prev = 0, 0, 0
    for i,(t,r) in enumerate(bands):
        if ti > t: prev = bands[i-1][1] if i>0 else 0; rate, thr = r, t
    if rate == 0: return 0.0
    sc = base_tax*rate
    if regime == "new":
        b = slab_tax_new(thr); b = b if thr>1200000 else max(0,b-60000)
    else:
        b = slab_tax_old(thr,age); b = b if thr>500000 else max(0,b-12500)
    liab_thr = b*(1+prev)
    if base_tax+sc-liab_thr > (ti-thr):
        sc = max(0, liab_thr+(ti-thr)-base_tax)
    return sc

def regime_new(gross, salaried, age, ded_new):
    sd = 75000 if salaried else 0
    ti = max(0, gross-sd-ded_new)
    base = slab_tax_new(ti)
    if ti <= 1200000:
        rebate = min(base,60000); after = base-rebate
    else:
        rebate = 0; excess = ti-1200000
        after = min(base,excess) if base>excess else base
    sc = _surcharge_mr(after, ti, "new", age)
    return dict(sd=sd, ti=ti, base=base, rebate=rebate, after=after,
                sc=sc, cess=(after+sc)*CESS, total=round((after+sc)*(1+CESS)))

def regime_old(gross, salaried, age, ded_old):
    sd = 50000 if salaried else 0
    ti = max(0, gross-sd-ded_old)
    base = slab_tax_old(ti, age)
    rebate = min(base,12500) if ti<=500000 else 0
    after = base-rebate
    sc = _surcharge_mr(after, ti, "old", age)
    return dict(sd=sd, ti=ti, base=base, rebate=rebate, after=after,
                sc=sc, cess=(after+sc)*CESS, total=round((after+sc)*(1+CESS)))

# ----------------------------- basic-exemption + combined CG -----------------------------
def basic_limit(regime, age):
    return 400000 if regime == "new" else {"below60":250000,"senior":300000,"super":500000}[age]

def special_tax_with_be(normal_ti, regime, age, stcg_eq, ltcg_eq_taxable, ltcg_oth, idx_gain, resident=True):
    """Resident basic-exemption shortfall is set off against special-rate gains,
    highest rate first (STCG 20% -> other LTCG 12.5% -> equity LTCG 12.5%)."""
    bl = basic_limit(regime, age)
    short = max(0, bl - normal_ti) if resident else 0
    s = short
    t = min(s, stcg_eq); stcg_eq -= t; s -= t
    t = min(s, ltcg_oth)
    if ltcg_oth > 0 and idx_gain > 0:
        idx_gain *= (ltcg_oth - t) / ltcg_oth
    ltcg_oth -= t; s -= t
    t = min(s, ltcg_eq_taxable); ltcg_eq_taxable -= t; s -= t
    tax_stcg = stcg_eq * 0.20
    tax_oth = min(ltcg_oth*0.125, idx_gain*0.20) if idx_gain > 0 else ltcg_oth*0.125
    tax_eq = ltcg_eq_taxable * 0.125
    return dict(stcg=stcg_eq, ltcg_oth=ltcg_oth, ltcg_eq=ltcg_eq_taxable,
                tax_stcg=tax_stcg, tax_oth=tax_oth, tax_eq=tax_eq,
                tax=tax_stcg+tax_oth+tax_eq, be_used=short - s)

def _surcharge_rate(ti, regime):
    top = .25 if regime == "new" else .37
    for t, r in [(50000000, top), (20000000, .25), (10000000, .15), (5000000, .10)]:
        if ti > t: return r
    return 0.0

def combined(gross_normal, salaried, age, regime, ded, cg, resident=True):
    """Normal slab income + capital gains on top, with basic-exemption adjustment.
    cg = dict(stcg_eq, ltcg_eq_taxable, ltcg_oth, idx_gain) — amounts AFTER the
    Capital Gains page's own set-off, the 1.25L equity exemption and 54-series."""
    base = regime_new(gross_normal, salaried, age, ded) if regime == "new" \
        else regime_old(gross_normal, salaried, age, ded)
    sp = special_tax_with_be(base["ti"], regime, age,
                             cg.get("stcg_eq",0), cg.get("ltcg_eq_taxable",0),
                             cg.get("ltcg_oth",0), cg.get("idx_gain",0), resident)
    gains_total = cg.get("stcg_eq",0)+cg.get("ltcg_eq_taxable",0)+cg.get("ltcg_oth",0)
    total_income = base["ti"] + gains_total
    r = _surcharge_rate(total_income, regime)
    sc = base["after"]*r + sp["tax"]*min(r, 0.15)   # CG surcharge capped at 15%
    tax_before_cess = base["after"] + sp["tax"] + sc
    total = round(tax_before_cess * (1 + CESS))
    return dict(normal=base, special=sp, surcharge=sc, total_income=total_income,
                cess=tax_before_cess*CESS, total=total)

# ----------------------------- PDF builder -----------------------------
def _pdf_font_paths():
    here = _os.path.dirname(_os.path.abspath(__file__))
    return (_os.path.join(here, "assets", "DejaVuSans.ttf"),
            _os.path.join(here, "assets", "DejaVuSans-Bold.ttf"))

def build_pdf(title, subtitle, line_items, note=""):
    """line_items: list of (label, value). label starting with '##' = section header;
    label starting with '**' = bold total row. Returns PDF bytes."""
    from fpdf import FPDF
    reg, bold = _pdf_font_paths()
    pdf = FPDF(format="A4"); pdf.set_auto_page_break(True, 18); pdf.add_page()
    pdf.add_font("DV", "", reg); pdf.add_font("DV", "B", bold)
    GREEN = (28, 74, 58); GOLD = (154, 106, 31); MUT = (107, 103, 93)

    pdf.set_font("DV", "B", 9); pdf.set_text_color(*GOLD)
    pdf.cell(0, 5, "RAHUL  —  INCOME TAX TOOLS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DV", "B", 18); pdf.set_text_color(*GREEN)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DV", "", 10); pdf.set_text_color(*MUT)
    pdf.cell(0, 6, subtitle, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2); pdf.set_draw_color(*GREEN); pdf.set_line_width(0.5)
    y = pdf.get_y(); pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y); pdf.ln(4)

    W = pdf.w - pdf.l_margin - pdf.r_margin
    for label, value in line_items:
        if label.startswith("##"):
            pdf.ln(2); pdf.set_font("DV", "B", 11); pdf.set_text_color(*GREEN)
            pdf.cell(0, 7, label[2:].strip(), new_x="LMARGIN", new_y="NEXT"); continue
        bold_row = label.startswith("**")
        lbl = label.replace("**", "")
        pdf.set_font("DV", "B" if bold_row else "", 10)
        pdf.set_text_color(*(GREEN if bold_row else (28,28,25)))
        pdf.cell(W*0.62, 7, lbl, border="B")
        pdf.cell(W*0.38, 7, str(value), border="B", align="R", new_x="LMARGIN", new_y="NEXT")
    if note:
        pdf.ln(4); pdf.set_font("DV", "", 8); pdf.set_text_color(*MUT)
        pdf.multi_cell(0, 4, note)
    pdf.ln(3); pdf.set_font("DV", "", 8); pdf.set_text_color(*MUT)
    pdf.cell(0, 4, "Generated by Rahul — Income Tax Tools · estimate, verify before filing.")
    return bytes(pdf.output())
