import streamlit as st
from shared import style, brandbar, inr, regime_new, regime_old

style("Advance Tax Calculator", "📅")
st.title("Advance Tax Calculator")
brandbar("FY 2025-26 (AY 2026-27) · Instalment schedule · 234C / 234B estimate")

st.markdown("Advance tax is payable if estimated tax after TDS is **₹10,000 or more**. "
            "Due dates: 15 Jun, 15 Sep, 15 Dec (FY 2025-26) and 15 Mar 2026.")

# ---- tax liability basis ----
prefill = st.session_state.get("it_total")
c1, c2 = st.columns(2)
with c1:
    gross = st.number_input("Estimated total income for the year (₹)", min_value=0, value=1500000, step=10000)
    salaried = st.checkbox("Salaried / pensioner (standard deduction)", value=True)
    regime = st.radio("Regime", ["New", "Old"], horizontal=True)
with c2:
    age_label = st.radio("Age category", ["Below 60", "Senior (60–79)", "Super senior (80+)"])
    age = {"Below 60":"below60","Senior (60–79)":"senior","Super senior (80+)":"super"}[age_label]
    ded = st.number_input("Deductions (₹)", min_value=0, value=150000, step=10000)
    tds = st.number_input("TDS / TCS expected for the year (₹)", min_value=0, value=0, step=5000)

computed = (regime_new(gross, salaried, age, ded) if regime == "New"
            else regime_old(gross, salaried, age, ded))["total"]
manual = st.number_input("Override total tax liability (₹) — 0 to use the computed figure",
                         min_value=0, value=int(prefill) if prefill else 0, step=1000)
liability = manual if manual > 0 else computed
presumptive = st.checkbox("Presumptive taxation u/s 44AD / 44ADA (100% by 15 Mar)", value=False)

adv = max(0, liability - tds)
applies = adv >= 10000

st.subheader("Result")
m1, m2, m3 = st.columns(3)
m1.metric("Estimated tax", inr(liability))
m2.metric("Less: TDS/TCS", inr(tds))
m3.metric("Advance tax payable", inr(adv) if applies else "Not applicable")
if not applies:
    st.caption("Advance tax after TDS is below ₹10,000 — no advance tax / 234C liability.")

# ---- schedule ----
dates = ["15 Jun 2025", "15 Sep 2025", "15 Dec 2025", "15 Mar 2026"]
cum_pct = [0.15, 0.45, 0.75, 1.00]
if presumptive:
    dates, cum_pct = ["15 Mar 2026"], [1.00]

st.subheader("Instalment schedule")
paid_inputs = []
cols = st.columns(len(dates))
for i, d in enumerate(dates):
    with cols[i]:
        paid_inputs.append(st.number_input(f"Paid up to {d} (₹)", min_value=0, value=0, step=5000, key=f"p{i}"))

st.markdown("| Due date | Cumulative % | Required cumulative | Paid cumulative | Shortfall |\n|---|---:|---:|---:|---:|")
for i, d in enumerate(dates):
    req = round(adv * cum_pct[i])
    paid = paid_inputs[i]
    short = max(0, req - paid)
    st.markdown(f"| {d} | {int(cum_pct[i]*100)}% | {inr(req)} | {inr(paid)} | {inr(short)} |")

# ---- 234C (simplified) ----
interest_234c = 0
if applies and not presumptive:
    relaxed = [0.12, 0.36, 0.75, 1.00]; months = [3, 3, 3, 1]
    for i in range(4):
        if paid_inputs[i] < relaxed[i] * adv:
            interest_234c += (round(adv*cum_pct[i]) - paid_inputs[i]) * 0.01 * months[i]
    interest_234c = max(0, round(interest_234c))

# ---- 234B (simplified) ----
m234b = st.number_input("Months for 234B interest (Apr → date of payment of self-assessment tax)",
                        min_value=0, max_value=24, value=4, step=1)
total_paid = sum(paid_inputs)
interest_234b = 0
if applies and total_paid < 0.90 * adv:
    interest_234b = round((adv - total_paid) * 0.01 * m234b)

st.subheader("Interest estimate")
i1, i2, i3 = st.columns(3)
i1.metric("234C (deferment)", inr(interest_234c))
i2.metric("234B (default)", inr(interest_234b))
i3.metric("Total interest", inr(interest_234c + interest_234b))

st.session_state["report_advtax"] = [
    ("##Advance tax", ""),
    ("Estimated tax", inr(liability)), ("Less: TDS/TCS", inr(tds)),
    ("**Advance tax payable", inr(adv) if applies else "Not applicable"),
    ("234C interest (est.)", inr(interest_234c)),
    ("234B interest (est.)", inr(interest_234b))]

st.caption("Estimate only. 234C uses the standard 12%/36% relaxation for the first two "
           "instalments; 234B is approximated over the months you enter. Capital gains / special "
           "incomes that arise later may shift instalment requirements. Verify before paying.")
