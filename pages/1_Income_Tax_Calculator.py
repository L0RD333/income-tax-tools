import streamlit as st
from shared import style, brandbar, inr, regime_new, regime_old

style("Income Tax Calculator", "💰")
st.title("Income Tax Calculator")
brandbar("FY 2025-26 (AY 2026-27) · Old Regime vs New Regime")

c1, c2 = st.columns(2)
with c1:
    gross = st.number_input("Gross total income (₹)", min_value=0, value=1200000, step=10000)
    salaried = st.checkbox("Salaried / pensioner (standard deduction applies)", value=True)
    tds = st.number_input("TDS / advance tax already paid (₹)", min_value=0, value=0, step=5000)
with c2:
    age_label = st.radio("Age category (old regime limit)",
                         ["Below 60", "Senior (60–79)", "Super senior (80+)"])
    age = {"Below 60":"below60","Senior (60–79)":"senior","Super senior (80+)":"super"}[age_label]
    ded_old = st.number_input("Old-regime deductions — 80C, 80D, HRA, etc. (₹)", min_value=0, value=150000, step=10000)
    ded_new = st.number_input("New-regime allowed deductions — e.g. employer NPS 80CCD(2) (₹)", min_value=0, value=0, step=5000)

new = regime_new(gross, salaried, age, ded_new)
old = regime_old(gross, salaried, age, ded_old)
best = "New" if new["total"] <= old["total"] else "Old"
saving = abs(new["total"] - old["total"])

st.subheader("Result")
r1, r2 = st.columns(2)
r1.metric("New Regime — total tax", inr(new["total"]),
          delta=None if best=="New" else f"+{inr(new['total']-old['total'])}", delta_color="inverse")
r2.metric("Old Regime — total tax", inr(old["total"]),
          delta=None if best=="Old" else f"+{inr(old['total']-new['total'])}", delta_color="inverse")
st.markdown(f"<div class='bestcard'>✅ <b>{best} Regime</b> is better by <b>{inr(saving)}</b>. "
            f"{'New regime is the default.' if best=='New' else 'Opt out of the default new regime when filing.'}"
            f"</div>", unsafe_allow_html=True)
chosen = new if best=="New" else old
net = chosen["total"] - tds
st.markdown(f"<p class='muted'>Net under the {best.lower()} regime after TDS/advance tax: "
            f"<b>{inr(net) if net>=0 else 'Refund '+inr(-net)}</b></p>", unsafe_allow_html=True)

with st.expander("Detailed breakdown"):
    st.markdown("| Particulars | New Regime | Old Regime |\n|---|---:|---:|")
    st.markdown(f"| Standard deduction | {inr(new['sd'])} | {inr(old['sd'])} |")
    st.markdown(f"| Other deductions | {inr(ded_new)} | {inr(ded_old)} |")
    st.markdown(f"| Taxable income | {inr(new['ti'])} | {inr(old['ti'])} |")
    st.markdown(f"| Tax before rebate | {inr(new['base'])} | {inr(old['base'])} |")
    st.markdown(f"| 87A rebate | -{inr(new['rebate'])} | -{inr(old['rebate'])} |")
    st.markdown(f"| Surcharge | {inr(new['sc'])} | {inr(old['sc'])} |")
    st.markdown(f"| Cess (4%) | {inr(new['cess'])} | {inr(old['cess'])} |")
    st.markdown(f"| **Total tax** | **{inr(new['total'])}** | **{inr(old['total'])}** |")

st.caption("Estimate for resident individuals on regular slab-rate income. 87A rebate applies "
           "only to regular income, not special-rate income such as capital gains. Surcharge "
           "marginal relief is approximate at very high incomes.")
