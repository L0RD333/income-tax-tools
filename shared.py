"""Shared helpers: styling, INR formatting, and the FY 2025-26 income-tax engine."""
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
