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

# ---- theme palettes (mirror rahul357.netlify.app :root / [data-theme=light]) ----
_DARK_VARS = """
  --bg:#070912; --bg-2:#0b0f1c; --surface:rgba(255,255,255,.045);
  --surface-2:rgba(255,255,255,.07); --border:rgba(255,255,255,.10);
  --border-glow:rgba(120,140,255,.35);
  --text:#eef1fb; --text-2:#aab2cf; --text-3:#6f7798;
  --accent:#7c84ff; --accent-2:#4ad6c4; --accent-3:#b07cff;
  --glow-1:rgba(124,132,255,.22); --glow-2:rgba(74,214,196,.14);
  --shadow:0 20px 50px -20px rgba(0,0,0,.7);
"""
_LIGHT_VARS = """
  --bg:#f5f7fc; --bg-2:#eef1f9; --surface:rgba(255,255,255,.75);
  --surface-2:#ffffff; --border:rgba(20,30,70,.10);
  --border-glow:rgba(90,100,220,.35);
  --text:#141a2e; --text-2:#46506e; --text-3:#828aa6;
  --accent:#4b53e0; --accent-2:#0fa593; --accent-3:#8a4bd6;
  --glow-1:rgba(75,83,224,.14); --glow-2:rgba(15,165,147,.10);
  --shadow:0 20px 50px -24px rgba(40,50,120,.25);
"""

_BASE_CSS = """
    /* ---- base ---- */
    html, body, [class*="css"], .stApp, .stMarkdown, p, span, label, div, input, button, textarea
      { font-family:'Inter',system-ui,sans-serif; }
    .stApp{ background:var(--bg); color:var(--text); }
    .stApp::before{
      content:""; position:fixed; inset:0; z-index:0; pointer-events:none;
      background:
        radial-gradient(620px circle at 12% 8%, var(--glow-1), transparent 60%),
        radial-gradient(560px circle at 88% 22%, var(--glow-2), transparent 55%),
        radial-gradient(700px circle at 50% 110%, var(--glow-1), transparent 60%);
    }
    .block-container{ position:relative; z-index:1; }
    /* top header bar (Share / GitHub / menu / status) -> themed blurred bar */
    header[data-testid="stHeader"]{
      background:color-mix(in srgb, var(--bg) 70%, transparent);
      backdrop-filter:blur(16px); border-bottom:1px solid var(--border); }
    [data-testid="stToolbar"] button, [data-testid="stToolbar"] a,
    [data-testid="stToolbar"] span, [data-testid="stStatusWidget"]{ color:var(--text-2) !important; }
    [data-testid="stToolbar"] svg{ fill:var(--text-2) !important; }
    [data-testid="stToolbar"] button:hover{ color:var(--text) !important;
      background:var(--surface) !important; border-radius:8px; }
    [data-testid="stToolbar"] button:hover svg{ fill:var(--text) !important; }

    /* ---- headings ---- */
    h1,h2,h3,h4{ font-family:'Sora',sans-serif !important; letter-spacing:-.02em;
      color:var(--text) !important; font-weight:700; }
    h1{ font-weight:800;
      background:linear-gradient(110deg,var(--accent),var(--accent-2) 60%,var(--accent-3));
      -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
    .stMarkdown p, .stMarkdown li{ color:var(--text-2); }
    a, a:visited{ color:var(--accent) !important; }

    /* ---- brand tag ---- */
    .brandbar{ font-family:'JetBrains Mono',monospace; font-size:12.5px; color:var(--text-2);
      background:var(--surface); border:1px solid var(--border); border-radius:12px;
      padding:12px 16px; margin-bottom:18px; backdrop-filter:blur(14px); line-height:1.7; }
    .brandbar b{ color:var(--accent); letter-spacing:.04em; }
    .bestcard{ border:1px solid var(--border-glow); border-radius:18px; padding:18px 22px;
      background:var(--surface); backdrop-filter:blur(14px); box-shadow:var(--shadow); color:var(--text); }
    .muted{ color:var(--text-3); font-size:13px; }

    /* ---- metrics -> glass cards ---- */
    [data-testid="stMetric"]{ background:var(--surface); border:1px solid var(--border);
      border-radius:18px; padding:18px 20px; backdrop-filter:blur(14px); transition:.3s; }
    [data-testid="stMetric"]:hover{ border-color:var(--border-glow); transform:translateY(-3px);
      box-shadow:var(--shadow); }
    [data-testid="stMetricLabel"]{ color:var(--text-3) !important; }
    [data-testid="stMetricValue"]{ font-family:'Sora',sans-serif !important; color:var(--text) !important; }

    /* ---- buttons (gradient) ---- */
    .stButton>button, .stDownloadButton>button, .stFormSubmitButton>button{
      font-family:'Inter',sans-serif; font-weight:600; border-radius:12px; padding:10px 22px;
      border:1px solid transparent; color:#fff !important;
      background:linear-gradient(120deg,var(--accent),var(--accent-3));
      box-shadow:0 10px 28px -12px var(--accent); transition:.25s; }
    .stButton>button:hover, .stDownloadButton>button:hover, .stFormSubmitButton>button:hover{
      transform:translateY(-3px); box-shadow:0 16px 34px -10px var(--accent);
      border:1px solid transparent; }

    /* ---- inputs ---- */
    [data-baseweb="input"], [data-baseweb="select"]>div, [data-baseweb="base-input"],
    .stTextInput input, .stNumberInput input, .stDateInput input, textarea{
      background:var(--surface) !important; border:1px solid var(--border) !important;
      color:var(--text) !important; border-radius:10px !important; }
    .stTextInput input:focus, .stNumberInput input:focus{ border-color:var(--border-glow) !important; }
    label, .stRadio label, .stCheckbox label, [data-testid="stWidgetLabel"]{ color:var(--text-2) !important; }

    /* ---- markdown tables ---- */
    .stMarkdown table{ width:100%; border-collapse:collapse; background:var(--surface);
      border:1px solid var(--border); border-radius:14px; overflow:hidden; }
    .stMarkdown th{ background:rgba(255,255,255,.04); color:var(--accent-2);
      font-family:'JetBrains Mono',monospace; font-weight:600; text-align:left;
      padding:10px 14px; border-bottom:1px solid var(--border); }
    .stMarkdown td{ color:var(--text); padding:9px 14px; border-bottom:1px solid var(--border); }
    .stMarkdown tr:last-child td{ border-bottom:none; }

    /* ---- containers ---- */
    [data-testid="stExpander"]{ background:var(--surface); border:1px solid var(--border);
      border-radius:14px; backdrop-filter:blur(14px); }
    [data-testid="stFileUploader"]{ background:var(--surface); border:1px dashed var(--border);
      border-radius:14px; padding:8px; }
    [data-testid="stFileUploaderDropzone"]{ background:transparent; }
    [data-testid="stSidebar"]{ background:var(--bg-2); border-right:1px solid var(--border); }
    [data-testid="stSidebar"] *{ color:var(--text-2); }
    [data-testid="stDataFrame"]{ border:1px solid var(--border); border-radius:14px; }
    .stTabs [data-baseweb="tab"]{ color:var(--text-2); }
    .stTabs [aria-selected="true"]{ color:var(--accent) !important; }
    .stAlert{ border-radius:12px; }

    /* ---- chrome ---- */
    #MainMenu{ visibility:hidden; } footer{ visibility:hidden; }
"""

def style(page_title, page_icon="🧮"):
    st.set_page_config(page_title=page_title, page_icon=page_icon, layout="centered")
    # day / night toggle (persists across pages via session_state key)
    st.session_state.setdefault("dark_mode", True)
    dark = st.sidebar.toggle("🌙  Dark mode", key="dark_mode",
                             help="Switch between night and day theme")
    vars_css = _DARK_VARS if dark else _LIGHT_VARS
    st.markdown(
        "<style>\n"
        "@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800"
        "&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap');\n"
        ":root{" + vars_css + "}\n"
        + _BASE_CSS +
        "</style>",
        unsafe_allow_html=True,
    )

def brandbar(subtitle):
    st.markdown(f"<div class='brandbar'>// <b>rahul</b> · income-tax-tools<br>"
                f"<span class='muted'>{subtitle}</span></div>", unsafe_allow_html=True)

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
