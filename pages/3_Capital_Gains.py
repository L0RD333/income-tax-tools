import streamlit as st
from shared import style, brandbar, inr, build_pdf

CESS = 0.04
style("Capital Gains Calculator", "📈")
st.title("Capital Gains Calculator")
brandbar("FY 2025-26 (AY 2026-27) · Post-23-July-2024 rates · Resident Individual / HUF")

st.markdown("Enter gains by category. Rates: equity **STCG 111A @20%**, equity "
            "**LTCG 112A @12.5%** after a **₹1.25L** exemption, other **LTCG @12.5%**.")

c1, c2 = st.columns(2)
with c1:
    stcg_eq = st.number_input("STCG — equity / equity MF, 111A (₹)", min_value=0, value=0, step=10000)
    ltcg_eq = st.number_input("LTCG — equity / equity MF, 112A (₹)", min_value=0, value=0, step=10000)
    ltcg_oth = st.number_input("LTCG — other assets (property/gold/unlisted) @12.5% (₹)", min_value=0, value=0, step=10000)
with c2:
    stcl = st.number_input("Short-term capital loss to set off (₹)", min_value=0, value=0, step=10000)
    ltcl = st.number_input("Long-term capital loss to set off (₹)", min_value=0, value=0, step=10000)
    exm54 = st.number_input("Section 54 / 54F / 54EC exemption against LTCG (₹)", min_value=0, value=0, step=10000)

with st.expander("Pre-23-July-2024 property — indexation comparison (optional)"):
    idx_gain = st.number_input("Indexed gain for the 20%-with-indexation option (₹), 0 to skip",
                               min_value=0, value=0, step=10000)
    st.caption("For land/building acquired before 23 Jul 2024, tax is the lower of 12.5% (no index) "
               "and 20% (with index).")

tds = st.number_input("TDS / advance tax paid (₹)", min_value=0, value=0, step=5000)

def absorb(amount, *buckets):
    out = []
    for b in buckets:
        take = min(amount, b); out.append(b - take); amount -= take
    return out, amount

stcg_net = max(0, stcg_eq - stcl)
stcl_left = max(0, stcl - stcg_eq)
(ltcg_oth_net, ltcg_eq_net), _ = absorb(ltcl + stcl_left, ltcg_oth, ltcg_eq)
(ltcg_oth_net, ltcg_eq_net), _ = absorb(exm54, ltcg_oth_net, ltcg_eq_net)

tax_stcg = stcg_net * 0.20
ltcg_eq_taxable = max(0, ltcg_eq_net - 125000)
tax_ltcg_eq = ltcg_eq_taxable * 0.125
tax_ltcg_oth = min(ltcg_oth_net*0.125, idx_gain*0.20) if idx_gain > 0 else ltcg_oth_net*0.125
tax_before_cess = tax_stcg + tax_ltcg_eq + tax_ltcg_oth
total = round(tax_before_cess * (1 + CESS))
net = total - tds

# share with the Income Tax page
st.session_state["cg_gains"] = dict(stcg_eq=stcg_net, ltcg_eq_taxable=ltcg_eq_taxable,
                                    ltcg_oth=ltcg_oth_net, idx_gain=idx_gain)

st.subheader("Result")
m1, m2, m3 = st.columns(3)
m1.metric("Total taxable gain", inr(stcg_net + ltcg_eq_taxable + ltcg_oth_net))
m2.metric("Tax before cess", inr(tax_before_cess))
m3.metric("Net payable / refund", inr(net) if net >= 0 else "Refund " + inr(-net))

with st.expander("Transaction-wise working"):
    st.markdown("| Gain type | Taxable | Rate | Tax |\n|---|---:|---:|---:|")
    st.markdown(f"| STCG equity (111A) | {inr(stcg_net)} | 20% | {inr(tax_stcg)} |")
    st.markdown(f"| LTCG equity (112A, after ₹1.25L) | {inr(ltcg_eq_taxable)} | 12.5% | {inr(tax_ltcg_eq)} |")
    st.markdown(f"| LTCG other assets | {inr(ltcg_oth_net)} | {'lower of 12.5%/20%' if idx_gain>0 else '12.5%'} | {inr(tax_ltcg_oth)} |")
    st.markdown(f"| Cess (4%) | | | {inr(tax_before_cess*CESS)} |")
    st.markdown(f"| **Total tax** | | | **{inr(total)}** |")

st.info("These gains are now available in the **Income Tax Calculator** tab — tick "
        "“Add capital gains on top” there to tax them above your slab income with the "
        "basic-exemption adjustment.")

items = [("##Capital gains computation",""),
         ("STCG equity (111A) @20%", inr(stcg_net)),
         ("LTCG equity (112A) taxable @12.5%", inr(ltcg_eq_taxable)),
         ("LTCG other assets @12.5%", inr(ltcg_oth_net)),
         ("Tax before cess", inr(tax_before_cess)),
         ("Cess (4%)", inr(tax_before_cess*CESS)),
         ("**Total tax", inr(total)),
         ("TDS / advance tax paid", inr(tds)),
         ("**Net payable / refund", inr(net) if net>=0 else "Refund "+inr(-net))]
st.download_button("⬇ Download computation (PDF)",
    data=build_pdf("Capital Gains Computation", "FY 2025-26 (AY 2026-27) · Resident Individual/HUF",
        items, "Simplified estimate. Set-off LTCL→LTCG, STCL→STCG then LTCG. Basic-exemption "
        "adjustment and slab-rate STCG are handled in the Income Tax tab. Verify before filing."),
    file_name="capital-gains-computation.pdf", mime="application/pdf")

st.caption("Simplified estimate for resident Individual/HUF. Slab-rate STCG on non-equity assets, "
           "grandfathering, non-resident/DTAA and full 54-series conditions are not modelled.")
