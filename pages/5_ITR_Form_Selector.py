import streamlit as st
from shared import style, brandbar

style("ITR Form Selector", "🗂")
st.title("Which ITR Form to File?")
brandbar("AY 2026-27 · Practical decision tool for ITR-1 to ITR-7")

c1, c2 = st.columns(2)
with c1:
    ttype = st.selectbox("Taxpayer type",
        ["Individual", "HUF", "Partnership firm", "LLP", "Company", "AOP / BOI", "Trust / NGO / Section 8"])
    res = st.radio("Residential status",
        ["Resident & Ordinarily Resident", "Resident but Not Ordinarily Resident", "Non-Resident"])
    income = st.number_input("Total income (₹)", min_value=0, value=800000, step=50000)
    agri = st.number_input("Agricultural income (₹)", min_value=0, value=0, step=1000)
with c2:
    st.markdown("**Income sources**")
    salary = st.checkbox("Salary / pension", value=True)
    one_two_house = st.checkbox("Income from up to two house properties")
    many_house = st.checkbox("More than two house properties")
    other_src = st.checkbox("Other sources (interest / dividend / family pension)", value=True)
    business = st.checkbox("Business / profession income")
    presumptive = st.checkbox("Presumptive income u/s 44AD / 44ADA / 44AE")
    partner = st.checkbox("Partner in a firm (remuneration / interest)")
    audit = st.checkbox("Audit / regular books business case")

st.markdown("**Capital gains**")
g1, g2 = st.columns(2)
with g1:
    cg_stcg = st.checkbox("Short-term capital gain")
    cg_112a_small = st.checkbox("112A LTCG up to ₹1.25 lakh only")
with g2:
    cg_112a_big = st.checkbox("112A LTCG above ₹1.25 lakh")
    cg_other = st.checkbox("Other CG (property / gold / debt / unlisted, etc.)")

st.markdown("**Special conditions / restrictions**")
s1, s2 = st.columns(2)
with s1:
    director = st.checkbox("Director in a company")
    unlisted = st.checkbox("Held unlisted equity shares")
    foreign_asset = st.checkbox("Foreign asset / signing authority")
    foreign_income = st.checkbox("Foreign income")
    bf_loss = st.checkbox("Brought-forward / carry-forward loss")
with s2:
    esop = st.checkbox("ESOP tax deferred")
    tds194n = st.checkbox("TDS u/s 194N")
    sec11 = st.checkbox("Claiming exemption u/s 11 / 12")
    sec139 = st.checkbox("Covered u/s 139(4A)–(4F)")
    special_rate = st.checkbox("Any special-rate income")

# ---------------- decision logic ----------------
reasons = []
form = "ITR-2"   # safe default for individual/HUF

if ttype in ("Company",):
    form = "ITR-7" if sec11 else "ITR-6"
    reasons.append("Company → ITR-6 (ITR-7 if claiming section 11 exemption).")
elif ttype in ("Trust / NGO / Section 8",) or sec11 or sec139:
    form = "ITR-7"
    reasons.append("Trust / institution / person covered u/s 139(4A)–(4F) or s.11 → ITR-7.")
elif ttype in ("Partnership firm", "LLP", "AOP / BOI"):
    if ttype == "Partnership firm" and presumptive and income <= 5000000 and not audit:
        form = "ITR-4"
        reasons.append("Resident firm (not LLP) with presumptive income ≤ ₹50L → ITR-4.")
    else:
        form = "ITR-5"
        reasons.append("Firm / LLP / AOP / BOI → ITR-5.")
else:  # Individual / HUF
    if business or audit:
        if (presumptive and not audit and income <= 5000000
                and res == "Resident & Ordinarily Resident"
                and not (foreign_asset or foreign_income or director or unlisted)):
            form = "ITR-4"
            reasons.append("Presumptive business/profession, resident, income ≤ ₹50L, no "
                           "disqualifiers → ITR-4.")
        else:
            form = "ITR-3"
            reasons.append("Business / profession income (non-presumptive or audit / disqualified "
                           "from ITR-4) → ITR-3.")
    else:
        # candidate ITR-1, check disqualifiers
        dq = []
        if res != "Resident & Ordinarily Resident": dq.append("not ROR")
        if income > 5000000: dq.append("income > ₹50L")
        if agri > 5000: dq.append("agri income > ₹5,000")
        if many_house: dq.append("more than one* house property")
        if cg_112a_big or cg_other or cg_stcg: dq.append("capital gains beyond small 112A LTCG")
        if any([director, unlisted, foreign_asset, foreign_income, bf_loss, esop, special_rate]):
            dq.append("a restricted condition (director / unlisted / foreign / b-f loss / ESOP / special-rate)")
        if partner: dq.append("partner in a firm")
        if dq:
            form = "ITR-2"
            reasons.append("Not eligible for ITR-1 because: " + "; ".join(dq) + ".")
            reasons.append("Individual/HUF without business income but ineligible for ITR-1 → ITR-2.")
        else:
            form = "ITR-1"
            reasons.append("Resident & ordinarily resident, income ≤ ₹50L, salary/one-house/other "
                           "sources, agri ≤ ₹5,000" +
                           (", small 112A LTCG ≤ ₹1.25L" if cg_112a_small else "") + " → ITR-1.")

st.subheader("Recommendation")
st.markdown(f"<div class='bestcard'>📄 <b>{form}</b></div>", unsafe_allow_html=True)

with st.expander("Why this form?", expanded=True):
    for r in reasons:
        st.markdown(f"- {r}")
    st.caption("*ITR-1 allows income from one house property in the strict sense; up to two is "
               "generally accepted but verify on the portal for your case.")

with st.expander("Quick guide"):
    st.markdown("""
| Form | Broad use |
|---|---|
| ITR-1 | Resident ROR individual, income ≤ ₹50L, salary/pension, one house, other sources, agri ≤ ₹5,000, small 112A LTCG ≤ ₹1.25L. |
| ITR-2 | Individual/HUF without business income but not eligible for ITR-1 (NR/RNOR, capital gains, foreign assets, directorship, more houses). |
| ITR-3 | Individual/HUF with business/profession income, not eligible for ITR-4. |
| ITR-4 | Resident individual/HUF/firm (not LLP) with presumptive income, income ≤ ₹50L, subject to restrictions. |
| ITR-5 | Firm, LLP, AOP, BOI and other non-company / non-ITR-7 persons. |
| ITR-6 | Company other than one claiming s.11 exemption. |
| ITR-7 | Trust/NGO/institution/person required to file u/s 139(4A)–(4F), incl. s.11 cases. |
""")
st.caption("Practical guidance only — confirm against the notified ITR instructions and portal "
           "validation before filing.")
