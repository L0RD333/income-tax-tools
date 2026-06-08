import streamlit as st
from shared import style, brandbar, inr, build_pdf

style("HRA Exemption Calculator", "🏠")
st.title("HRA Exemption Calculator")
brandbar("FY 2025-26 (AY 2026-27) · Section 10(13A) read with Rule 2A")

regime = st.radio("Tax regime", ["Old Regime", "New Regime"], horizontal=True)
if regime == "New Regime":
    st.warning("HRA exemption under Section 10(13A) is **not available** under the New Regime. "
               "The exempt amount is nil. Switch to the Old Regime to compute an exemption.")

city = st.radio("City of rented house", ["Metro (Delhi, Mumbai, Kolkata, Chennai)", "Non-metro"], horizontal=True)
metro = city.startswith("Metro")

c1, c2 = st.columns(2)
with c1:
    basic = st.number_input("Basic salary (monthly ₹)", min_value=0, value=40000, step=1000)
    da = st.number_input("DA forming part of retirement benefits (monthly ₹)", min_value=0, value=0, step=1000)
    comm = st.number_input("Turnover-based commission (monthly ₹)", min_value=0, value=0, step=1000)
with c2:
    hra = st.number_input("HRA received (monthly ₹)", min_value=0, value=18000, step=1000)
    rent = st.number_input("Rent paid (monthly ₹)", min_value=0, value=20000, step=1000)
    months = st.number_input("Eligible months", min_value=1, max_value=12, value=12, step=1)

salary_m = basic + da + comm
ann_salary = salary_m * months
ann_hra = hra * months
ann_rent = rent * months

least1 = ann_hra
least2 = (0.50 if metro else 0.40) * ann_salary
least3 = max(0, ann_rent - 0.10 * ann_salary)
exempt = 0 if regime == "New Regime" else max(0, min(least1, least2, least3))
taxable_hra = ann_hra - exempt

st.subheader("Result")
m1, m2, m3 = st.columns(3)
m1.metric("HRA exempt", inr(exempt))
m2.metric("Taxable HRA", inr(taxable_hra))
m3.metric("Annual rent", inr(ann_rent))

with st.expander("Rule 2A working (least of the three is exempt)"):
    st.markdown("| Condition | Annual amount |\n|---|---:|")
    st.markdown(f"| 1. Actual HRA received | {inr(least1)} |")
    st.markdown(f"| 2. {'50% (metro)' if metro else '40% (non-metro)'} of salary | {inr(least2)} |")
    st.markdown(f"| 3. Rent paid − 10% of salary | {inr(least3)} |")
    st.markdown(f"| **Exempt (least, old regime)** | **{inr(exempt)}** |")
    st.caption(f"Salary for HRA = Basic + DA(retirement) + commission = {inr(salary_m)}/month "
               f"× {months} = {inr(ann_salary)} per year.")

if ann_rent > 100000 and regime == "Old Regime":
    st.info("Annual rent exceeds ₹1,00,000 — landlord PAN reporting is generally required by the employer.")
items = [("##HRA exemption (Rule 2A)",""),
         ("Regime", regime),
         ("City", "Metro" if metro else "Non-metro"),
         ("Annual salary (Basic+DA+comm)", inr(ann_salary)),
         ("1. Actual HRA received", inr(least1)),
         ("2. %s of salary" % ("50%" if metro else "40%"), inr(least2)),
         ("3. Rent - 10% of salary", inr(least3)),
         ("**HRA exempt", inr(exempt)),
         ("Taxable HRA", inr(taxable_hra))]
st.session_state["report_hra"] = items
st.download_button("⬇ Download computation (PDF)",
    data=build_pdf("HRA Exemption Computation", "FY 2025-26 (AY 2026-27) · Section 10(13A) / Rule 2A",
        items, "Exempt = least of the three (Old Regime only). Verify before filing."),
    file_name="hra-exemption-computation.pdf", mime="application/pdf")

st.caption("HRA exemption applies only where the employee receives HRA, lives in rented "
           "accommodation and actually pays rent. Old regime only.")
