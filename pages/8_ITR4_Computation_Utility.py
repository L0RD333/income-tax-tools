import json
import streamlit as st
from shared import style, brandbar, inr, build_pdf

style("ITR-4 Computation Utility", "🏪")
st.title("ITR-4 Computation Utility")
brandbar("Reads an ITR-4 JSON · presumptive business 44AD / 44ADA / 44AE + working paper")

st.markdown("Upload an **ITR-4 JSON** (presumptive business / profession). This tool reads the "
            "details, prepares a computation and a simple P&L working paper. It does **not** "
            "generate portal JSON.")

# ---------------- defensive helpers (shared style with ITR-1) ----------------
def deep_find(o, key):
    if isinstance(o, dict):
        if key in o and o[key] not in (None, ""):
            return o[key]
        for v in o.values():
            r = deep_find(v, key)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = deep_find(v, key)
            if r is not None:
                return r
    return None

def first(o, *keys):
    for k in keys:
        r = deep_find(o, k)
        if r is not None:
            return r
    return None

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0

def fmt_ay(v):
    s = str(v or "").strip()
    if len(s) == 4 and s.isdigit():
        return f"AY {s}-{str(int(s)+1)[2:]}"
    return f"AY {s}" if s else "-"

SAMPLE = {"ITR": {"ITR4": {
    "Form_ITR4": {"FormName": "ITR4", "AssessmentYear": "2025"},
    "PersonalInfo": {"AssesseeName": {"FirstName": "Ravi", "SurNameOrOrgName": "Kumar"},
                     "PAN": "AAAPK1234M",
                     "Address": {"CityOrTownOrDistrict": "Pune", "EmailAddress": "ravi@example.com"}},
    "FilingStatus": {"OptOutNewTaxRegime": "Y"},
    "IncomeDeductions": {"GrossSalary": 0, "IncomeFromSal": 0, "TotalIncomeOfHP": 0,
                         "IncomeOthSrc": 12000, "GrossTotIncome": 612000,
                         "DeductUndChapVIA": {"TotalChapVIADeductions": 150000}, "TotalIncome": 462000},
    "ScheduleBP": {"BusinessIncOthThanSpecified": 600000},
    "Schedule44AD": {"NatureOfBusiness": "Retail trade", "GrsTrnOverBnkMode": 7000000,
                     "GrsTrnOverOthMode": 1000000, "PresumptiveInc44AD": 600000},
    "FinancialParticulars": {"Sundrydebtors": 200000, "Sundrycreditors": 150000,
                             "ClosingStock": 300000, "CashBalance": 80000},
    "TaxComputation": {"TotalTaxPayable": 11500, "Rebate87A": 0, "EducationCess": 460,
                       "GrossTaxLiability": 11960, "TotalIntrstPay": 0, "NetTaxLiability": 11960},
    "TaxPaid": {"TaxesPaid": {"TDS": 4000, "TCS": 0, "AdvanceTax": 8000, "SelfAssessmentTax": 0,
                              "TotalTaxesPaid": 12000}, "BalTaxPayable": 0},
    "Refund": {"RefundDue": 40},
    "TDSonOthThanSals": {"TDSonOthThanSal": [{"EmployerOrDeductorOrCollectDetl":
        {"TAN": "PNEB12345D", "EmployerOrDeductorOrCollecterName": "Distributor Co"},
        "IncChrgblUndHd": 0, "TotTDSonOthThanSals": 4000}]},
}}}

c1, c2 = st.columns([3, 1])
up = c1.file_uploader("Choose ITR-4 JSON", type=["json"])
if c2.button("🧪 Load sample"):
    st.session_state["itr4_data"] = SAMPLE
if up is not None:
    try:
        st.session_state["itr4_data"] = json.load(up)
        st.success("JSON loaded.")
    except Exception as e:
        st.error(f"Could not parse JSON: {e}")

data = st.session_state.get("itr4_data")
if not data:
    st.info("Upload an ITR-4 JSON or click **Load sample** to see the workflow.")
    st.stop()

# ---------------- extract ----------------
name = ((str(first(data, "FirstName") or "") + " " + str(first(data, "SurNameOrOrgName") or "")).strip()) or "-"
pan = first(data, "PAN") or "-"
ay = fmt_ay(first(data, "AssessmentYear"))
city = first(data, "CityOrTownOrDistrict") or ""
regime = "Old regime" if str(first(data, "OptOutNewTaxRegime")).upper() == "Y" else "New regime (default)"

nature = first(data, "NatureOfBusiness") or "-"
turn_bank = num(first(data, "GrsTrnOverBnkMode"))
turn_cash = num(first(data, "GrsTrnOverOthMode"))
turnover = turn_bank + turn_cash
presum_44ad = num(first(data, "PresumptiveInc44AD"))
gross_receipts_44ada = num(first(data, "GrossReceipts"))
presum_44ada = num(first(data, "PresumptiveInc44ADA"))
biz_income = num(first(data, "BusinessIncOthThanSpecified", "IncomeFromBusinessProf")) or (presum_44ad + presum_44ada)

salary = num(first(data, "IncomeFromSal", "GrossSalary"))
hp = num(first(data, "TotalIncomeOfHP"))
oth = num(first(data, "IncomeOthSrc"))
gti = num(first(data, "GrossTotIncome"))
chvia = num(first(data, "TotalChapVIADeductions"))
ti = num(first(data, "TotalIncome"))

tax_payable = num(first(data, "TotalTaxPayable"))
rebate = num(first(data, "Rebate87A"))
cess = num(first(data, "EducationCess"))
interest = num(first(data, "TotalIntrstPay"))
gross_liab = num(first(data, "GrossTaxLiability"))
net_liab = num(first(data, "NetTaxLiability"))
total_paid = num(first(data, "TotalTaxesPaid"))
refund = num(first(data, "RefundDue"))
bal = num(first(data, "BalTaxPayable"))

debtors = num(first(data, "Sundrydebtors"))
creditors = num(first(data, "Sundrycreditors"))
stock = num(first(data, "ClosingStock"))
cash = num(first(data, "CashBalance"))

# ---------------- display ----------------
h1, h2, h3, h4 = st.columns(4)
h1.metric("PAN", pan)
h2.metric("Assessment Year", ay.replace("AY ", ""))
h3.metric("Business income", inr(biz_income))
h4.metric("Refund" if refund >= bal else "Tax payable", inr(refund) if refund >= bal else inr(bal))
st.caption(f"**{name}** · {city} · {regime} · {nature}")

st.subheader("Presumptive business (44AD / 44ADA)")
st.markdown("| Particulars | Amount |\n|---|---:|")
if turnover:
    st.markdown(f"| Gross turnover — bank/digital | {inr(turn_bank)} |")
    st.markdown(f"| Gross turnover — cash/other | {inr(turn_cash)} |")
    st.markdown(f"| **Total turnover (44AD)** | **{inr(turnover)}** |")
    if turnover:
        st.markdown(f"| Presumptive income declared | {inr(presum_44ad)} ({presum_44ad/turnover*100:.1f}%) |")
if gross_receipts_44ada:
    st.markdown(f"| Gross receipts (44ADA profession) | {inr(gross_receipts_44ada)} |")
    st.markdown(f"| Presumptive income (44ADA) | {inr(presum_44ada)} |")

st.subheader("Income & deductions")
st.markdown("| Particulars | Amount |\n|---|---:|")
st.markdown(f"| Business / profession income | {inr(biz_income)} |")
st.markdown(f"| Salary | {inr(salary)} |")
st.markdown(f"| House property | {inr(hp)} |")
st.markdown(f"| Other sources | {inr(oth)} |")
st.markdown(f"| **Gross total income** | **{inr(gti)}** |")
st.markdown(f"| Chapter VI-A deductions | -{inr(chvia)} |")
st.markdown(f"| **Total income** | **{inr(ti)}** |")

with st.expander("P&L / Balance-sheet working paper (auto-generated)"):
    st.caption("Net profit is set equal to the presumptive business income shown in the JSON; "
               "other figures are working-paper estimates — replace with actual books where available.")
    st.markdown("| Particulars | Amount |\n|---|---:|")
    st.markdown(f"| Gross receipts / turnover | {inr(turnover or gross_receipts_44ada)} |")
    st.markdown(f"| Net profit (presumptive) | {inr(biz_income)} |")
    st.markdown(f"| Sundry debtors | {inr(debtors)} |")
    st.markdown(f"| Sundry creditors | {inr(creditors)} |")
    st.markdown(f"| Closing stock | {inr(stock)} |")
    st.markdown(f"| Cash balance | {inr(cash)} |")

st.subheader("Tax computation")
st.markdown("| Particulars | Amount |\n|---|---:|")
st.markdown(f"| Tax on total income | {inr(tax_payable)} |")
st.markdown(f"| Less: rebate u/s 87A | -{inr(rebate)} |")
st.markdown(f"| Health & education cess | {inr(cess)} |")
st.markdown(f"| Interest | {inr(interest)} |")
st.markdown(f"| **Net tax liability** | **{inr(net_liab or gross_liab)}** |")
st.markdown(f"| Less: taxes paid | -{inr(total_paid)} |")
st.markdown(f"| **{'Refund due' if refund>=bal else 'Balance payable'}** | **{inr(refund) if refund>=bal else inr(bal)}** |")

# ---------------- PDF ----------------
rows = [("##Taxpayer", ""), ("Name", name), ("PAN", pan), ("Assessment year", ay),
        ("Regime", regime), ("Nature of business", nature),
        ("##Presumptive business", ""), ("Total turnover (44AD)", inr(turnover)),
        ("Presumptive income", inr(biz_income)),
        ("##Income & deductions", ""), ("Business/profession", inr(biz_income)),
        ("Salary", inr(salary)), ("House property", inr(hp)), ("Other sources", inr(oth)),
        ("**Gross total income", inr(gti)), ("Chapter VI-A deductions", "-"+inr(chvia)),
        ("**Total income", inr(ti)),
        ("##Tax computation", ""), ("Tax on total income", inr(tax_payable)),
        ("Rebate u/s 87A", "-"+inr(rebate)), ("Cess", inr(cess)), ("Interest", inr(interest)),
        ("**Net tax liability", inr(net_liab or gross_liab)),
        ("Taxes paid", "-"+inr(total_paid)),
        ("**"+("Refund due" if refund>=bal else "Balance payable"),
         inr(refund) if refund>=bal else inr(bal))]
st.download_button("⬇ Download computation (PDF)",
    data=build_pdf("ITR-4 Computation", f"{ay} · {name} · PAN {pan}", rows,
        "Working paper from the uploaded ITR-4 JSON. P&L/BS items beyond presumptive net profit are "
        "estimates. This tool reads figures as filed and does not generate portal JSON. Verify "
        "against the filed return and actual books."),
    file_name="itr4-computation.pdf", mime="application/pdf")

st.caption("Reads presumptive (44AD/44ADA) ITR-4 returns following the e-filing schema with "
           "fallbacks; if a value reads as 0, confirm the key exists in your JSON.")
