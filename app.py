"""
Income Tax Calculator — FY 2025-26 (AY 2026-27)
Old Regime vs New Regime, for resident individuals.
Author: Rahul
"""
import streamlit as st

CESS = 0.04

# ----------------------------- tax engine -----------------------------
def slab_tax_new(ti):
    bands = [(400000, 0), (800000, .05), (1200000, .10), (1600000, .15),
             (2000000, .20), (2400000, .25), (float("inf"), .30)]
    tax, lo = 0.0, 0
    for hi, r in bands:
        if ti > lo:
            tax += (min(ti, hi) - lo) * r
            lo = hi
        else:
            break
    return tax

def slab_tax_old(ti, age):
    exempt = {"below60": 250000, "senior": 300000, "super": 500000}[age]
    bands = [(exempt, 0), (500000, .05), (1000000, .20), (float("inf"), .30)]
    tax, lo = 0.0, 0
    for hi, r in bands:
        if ti > lo:
            tax += (min(ti, max(hi, exempt)) - lo) * r
            lo = max(hi, exempt) if r == 0 else hi
        else:
            break
    return tax

def surcharge_with_mr(base_tax, ti, regime, age):
    bands = [(5000000, .10), (10000000, .15), (20000000, .25),
             (50000000, .25 if regime == "new" else .37)]
    rate, thr, prev = 0, 0, 0
    for i, (t, r) in enumerate(bands):
        if ti > t:
            prev = bands[i - 1][1] if i > 0 else 0
            rate, thr = r, t
    if rate == 0:
        return 0.0
    sc = base_tax * rate
    # liability exactly at the threshold (base tax there + surcharge at the lower band rate)
    if regime == "new":
        b_thr = slab_tax_new(thr)
        b_thr = b_thr if thr > 1200000 else max(0, b_thr - 60000)
    else:
        b_thr = slab_tax_old(thr, age)
        b_thr = b_thr if thr > 500000 else max(0, b_thr - 12500)
    liab_thr = b_thr * (1 + prev)
    if base_tax + sc - liab_thr > (ti - thr):
        sc = max(0, liab_thr + (ti - thr) - base_tax)
    return sc

def regime_new(gross, salaried, age, ded_new):
    sd = 75000 if salaried else 0
    ti = max(0, gross - sd - ded_new)
    base = slab_tax_new(ti)
    if ti <= 1200000:
        rebate = min(base, 60000)
        after = base - rebate
    else:  # marginal relief on the 87A rebate just above 12L
        rebate = 0
        excess = ti - 1200000
        after = min(base, excess) if base > excess else base
    sc = surcharge_with_mr(after, ti, "new", age)
    total = round((after + sc) * (1 + CESS))
    return dict(sd=sd, ti=ti, base=base, rebate=rebate, after=after,
                sc=sc, cess=(after + sc) * CESS, total=total)

def regime_old(gross, salaried, age, ded_old):
    sd = 50000 if salaried else 0
    ti = max(0, gross - sd - ded_old)
    base = slab_tax_old(ti, age)
    rebate = min(base, 12500) if ti <= 500000 else 0
    after = base - rebate
    sc = surcharge_with_mr(after, ti, "old", age)
    total = round((after + sc) * (1 + CESS))
    return dict(sd=sd, ti=ti, base=base, rebate=rebate, after=after,
                sc=sc, cess=(after + sc) * CESS, total=total)

def inr(x):
    x = round(x)
    s = str(abs(int(x)))
    if len(s) > 3:
        last3 = s[-3:]; rest = s[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:]); rest = rest[:-2]
        if rest: parts.insert(0, rest)
        s = ",".join(parts) + "," + last3
    return ("-" if x < 0 else "") + "₹" + s

# ----------------------------- UI -----------------------------
st.set_page_config(page_title="Income Tax Calculator FY 2025-26", page_icon="🧮", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Spectral:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Spectral', Georgia, serif; }
h1, h2, h3 { font-family: 'Fraunces', serif !important; color:#1c4a3a; }
.stApp { background:#f7f4ed; }
.brandbar { border-left:3px solid #9a6a1f; padding:6px 0 6px 12px; color:#6b675d;
  font-size:13px; margin-bottom:14px; background:linear-gradient(90deg,#eef2ed,transparent); }
.brandbar b { color:#1c4a3a; font-family:'Fraunces',serif; }
.bestcard { border:2px solid #1c4a3a; border-radius:6px; padding:14px 18px; background:#fff; }
.muted { color:#6b675d; font-size:13px; }
</style>
""", unsafe_allow_html=True)

st.title("Income Tax Calculator")
st.markdown("<div class='brandbar'><b>Rahul</b> — Income Tax Tools<br>"
            "FY 2025-26 (AY 2026-27) · Old Regime vs New Regime · Resident individuals</div>",
            unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    gross = st.number_input("Gross total income (₹)", min_value=0, value=1200000, step=10000)
    salaried = st.checkbox("Salaried / pensioner (standard deduction applies)", value=True)
    tds = st.number_input("TDS / advance tax already paid (₹)", min_value=0, value=0, step=5000)
with c2:
    age_label = st.radio("Age category (old regime limit)",
                         ["Below 60", "Senior (60–79)", "Super senior (80+)"])
    age = {"Below 60": "below60", "Senior (60–79)": "senior", "Super senior (80+)": "super"}[age_label]
    ded_old = st.number_input("Old-regime deductions — 80C, 80D, HRA, etc. (₹)",
                              min_value=0, value=150000, step=10000)
    ded_new = st.number_input("New-regime allowed deductions — e.g. employer NPS 80CCD(2) (₹)",
                              min_value=0, value=0, step=5000)

new = regime_new(gross, salaried, age, ded_new)
old = regime_old(gross, salaried, age, ded_old)
best = "New" if new["total"] <= old["total"] else "Old"
saving = abs(new["total"] - old["total"])

st.subheader("Result")
r1, r2 = st.columns(2)
r1.metric("New Regime — total tax", inr(new["total"]),
          delta=None if best == "New" else f"+{inr(new['total']-old['total'])}", delta_color="inverse")
r2.metric("Old Regime — total tax", inr(old["total"]),
          delta=None if best == "Old" else f"+{inr(old['total']-new['total'])}", delta_color="inverse")

st.markdown(f"<div class='bestcard'>✅ <b>{best} Regime</b> is better by "
            f"<b>{inr(saving)}</b>. {'New regime is the default.' if best=='New' else 'Remember to opt out of the default new regime when filing.'}"
            f"</div>", unsafe_allow_html=True)

chosen = new if best == "New" else old
net = chosen["total"] - tds
st.markdown(f"<p class='muted'>Net payable under the {best.lower()} regime after TDS/advance tax: "
            f"<b>{inr(net) if net>=0 else 'Refund '+inr(-net)}</b></p>", unsafe_allow_html=True)

with st.expander("Detailed breakdown"):
    def row(label, n, o):
        st.markdown(f"| {label} | {n} | {o} |")
    st.markdown("| Particulars | New Regime | Old Regime |\n|---|---:|---:|")
    st.markdown(f"| Standard deduction | {inr(new['sd'])} | {inr(old['sd'])} |")
    st.markdown(f"| Other deductions | {inr(ded_new)} | {inr(ded_old)} |")
    st.markdown(f"| Taxable income | {inr(new['ti'])} | {inr(old['ti'])} |")
    st.markdown(f"| Tax before rebate | {inr(new['base'])} | {inr(old['base'])} |")
    st.markdown(f"| 87A rebate | -{inr(new['rebate'])} | -{inr(old['rebate'])} |")
    st.markdown(f"| Surcharge | {inr(new['sc'])} | {inr(old['sc'])} |")
    st.markdown(f"| Health & education cess (4%) | {inr(new['cess'])} | {inr(old['cess'])} |")
    st.markdown(f"| **Total tax** | **{inr(new['total'])}** | **{inr(old['total'])}** |")

st.caption("Estimate for resident individuals on regular slab-rate income. New regime is the "
           "default u/s 115BAC. The 87A rebate applies only to regular income, not special-rate "
           "income such as capital gains. Surcharge marginal relief is approximate at very high "
           "incomes. Verify with the official portal / ITR utility before filing.")
