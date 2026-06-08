import json
import streamlit as st
from shared import style, brandbar, inr, build_pdf

style("ITR-1 Computation Utility", "🧾")
st.title("ITR-1 Computation Utility")
brandbar("Reads an ITR-1 JSON and prepares a computation / working paper · salary + interest")

st.markdown("Upload an **ITR-1 JSON** (as exported from the e-filing utility). This tool reads the "
            "details and prepares a computation sheet and PDF. It does **not** generate portal JSON.")

# ---------------- defensive JSON helpers ----------------
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

SAMPLE = {"ITR": {"ITR1": {
    "Form_ITR1": {"FormName": "ITR1", "AssessmentYear": "2025"},
    "PersonalInfo": {"AssesseeName": {"FirstName": "Asha", "SurNameOrOrgName": "Verma"},
                     "PAN": "ABCPV1234K",
                     "Address": {"CityOrTownOrDistrict": "Bengaluru", "StateCode": "29",
                                 "PinCode": 560001, "EmailAddress": "asha@example.com",
                                 "MobileNo": 9800000000}},
    "FilingStatus": {"OptOutNewTaxRegime": "N"},
    "ITR1_IncomeDeductions": {"GrossSalary": 700000, "DeductionUs16ia": 75000,
                              "IncomeFromSal": 625000, "TotalIncomeOfHP": 0,
                              "IncomeOthSrc": 18000, "GrossTotIncome": 643000,
                              "DeductUndChapVIA": {"TotalChapVIADeductions": 0},
                              "TotalIncome": 643000},
    "ITR1_TaxComputation": {"TotalTaxPayable": 0, "Rebate87A": 11150, "EducationCess": 0,
                            "GrossTaxLiability": 0, "TotalIntrstPay": 0, "NetTaxLiability": 0},
    "TaxPaid": {"TaxesPaid": {"TDS": 5000, "TCS": 0, "AdvanceTax": 0, "SelfAssessmentTax": 0,
                              "TotalTaxesPaid": 5000}, "BalTaxPayable": 0},
    "Refund": {"RefundDue": 5000},
    "TDSonSalaries": {"TDSonSalary": [{"EmployerOrDeductorOrCollectDetl":
        {"TAN": "BLRA12345B", "EmployerOrDeductorOrCollecterName": "Acme Pvt Ltd"},
        "IncChrgSal": 700000, "TotalTDSSal": 5000}]},
    "TDSonOthThanSals": {"TDSonOthThanSal": [{"EmployerOrDeductorOrCollectDetl":
        {"TAN": "BLRB54321C", "EmployerOrDeductorOrCollecterName": "XYZ Bank"},
        "IncChrgblUndHd": 18000, "TotTDSonOthThanSals": 0}]},
}}}

c1, c2 = st.columns([3, 1])
up = c1.file_uploader("Choose ITR-1 JSON", type=["json"])
if c2.button("🧪 Load sample"):
    st.session_state["itr1_data"] = SAMPLE
if up is not None:
    try:
        st.session_state["itr1_data"] = json.load(up)
        st.success("JSON loaded.")
    except Exception as e:
        st.error(f"Could not parse JSON: {e}")

data = st.session_state.get("itr1_data")
if not data:
    st.info("Upload an ITR-1 JSON or click **Load sample** to see the workflow.")
    st.stop()

# ---------------- extract ----------------
fn = first(data, "FirstName") or ""
sn = first(data, "SurNameOrOrgName") or ""
name = (str(fn) + " " + str(sn)).strip() or "-"
pan = first(data, "PAN") or "-"
ay = fmt_ay(first(data, "AssessmentYear"))
city = first(data, "CityOrTownOrDistrict") or ""
email = first(data, "EmailAddress") or ""
opt_out = first(data, "OptOutNewTaxRegime")
regime = "Old regime" if str(opt_out).upper() == "Y" else "New regime (default)"

salary = num(first(data, "IncomeFromSal", "GrossSalary"))
hp = num(first(data, "TotalIncomeOfHP", "IncomeOfHP"))
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

tds = num(first(data, "TDS"))
tcs = num(first(data, "TCS"))
adv = num(first(data, "AdvanceTax"))
sat = num(first(data, "SelfAssessmentTax"))
total_paid = num(first(data, "TotalTaxesPaid")) or (tds + tcs + adv + sat)
refund = num(first(data, "RefundDue"))
bal = num(first(data, "BalTaxPayable"))

# ---------------- display ----------------
h1, h2, h3, h4 = st.columns(4)
h1.metric("PAN", pan)
h2.metric("Assessment Year", ay.replace("AY ", ""))
h3.metric("Gross total income", inr(gti))
h4.metric("Refund" if refund >= bal else "Tax payable",
          inr(refund) if refund >= bal else inr(bal))

st.caption(f"**{name}** · {city} · {email} · {regime}")

st.subheader("Income & deductions")
st.markdown("| Particulars | Amount |\n|---|---:|")
st.markdown(f"| Income from salary | {inr(salary)} |")
st.markdown(f"| Income from house property | {inr(hp)} |")
st.markdown(f"| Income from other sources | {inr(oth)} |")
st.markdown(f"| **Gross total income** | **{inr(gti)}** |")
st.markdown(f"| Chapter VI-A deductions | -{inr(chvia)} |")
st.markdown(f"| **Total income** | **{inr(ti)}** |")

st.subheader("Tax computation")
st.markdown("| Particulars | Amount |\n|---|---:|")
st.markdown(f"| Tax on total income | {inr(tax_payable)} |")
st.markdown(f"| Less: rebate u/s 87A | -{inr(rebate)} |")
st.markdown(f"| Health & education cess | {inr(cess)} |")
st.markdown(f"| Interest | {inr(interest)} |")
st.markdown(f"| **Net tax liability** | **{inr(net_liab or gross_liab)}** |")
st.markdown(f"| Less: taxes paid (TDS {inr(tds)}, TCS {inr(tcs)}, advance {inr(adv)}, SA {inr(sat)}) | -{inr(total_paid)} |")
st.markdown(f"| **{'Refund due' if refund>=bal else 'Balance payable'}** | **{inr(refund) if refund>=bal else inr(bal)}** |")

# TDS schedule
def tds_rows(node_list_key, name_key, tan_key, amt_keys, inc_keys):
    lst = deep_find(data, node_list_key)
    rows = []
    if isinstance(lst, dict):
        lst = [lst]
    if isinstance(lst, list):
        for e in lst:
            rows.append((first(e, name_key) or "-", first(e, tan_key) or "-",
                         num(first(e, *inc_keys)), num(first(e, *amt_keys))))
    return rows

tds_all = (tds_rows("TDSonSalary", "EmployerOrDeductorOrCollecterName", "TAN",
                    ["TotalTDSSal"], ["IncChrgSal"]) +
           tds_rows("TDSonOthThanSal", "EmployerOrDeductorOrCollecterName", "TAN",
                    ["TotTDSonOthThanSals", "TDSAmt"], ["IncChrgblUndHd", "GrossAmount"]))
if tds_all:
    st.subheader("TDS details")
    st.markdown("| Deductor | TAN | Income | TDS |\n|---|---|---:|---:|")
    for nm, tan, inc, t in tds_all:
        st.markdown(f"| {nm} | {tan} | {inr(inc)} | {inr(t)} |")

# ---------------- PDF ----------------
rows = [("##Taxpayer", ""), ("Name", name), ("PAN", pan), ("Assessment year", ay), ("Regime", regime),
        ("##Income & deductions", ""), ("Income from salary", inr(salary)),
        ("Income from house property", inr(hp)), ("Income from other sources", inr(oth)),
        ("**Gross total income", inr(gti)), ("Chapter VI-A deductions", "-"+inr(chvia)),
        ("**Total income", inr(ti)),
        ("##Tax computation", ""), ("Tax on total income", inr(tax_payable)),
        ("Rebate u/s 87A", "-"+inr(rebate)), ("Cess", inr(cess)), ("Interest", inr(interest)),
        ("**Net tax liability", inr(net_liab or gross_liab)),
        ("Taxes paid (TDS/TCS/advance/SA)", "-"+inr(total_paid)),
        ("**"+("Refund due" if refund>=bal else "Balance payable"),
         inr(refund) if refund>=bal else inr(bal))]
st.download_button("⬇ Download computation (PDF)",
    data=build_pdf("ITR-1 Computation", f"{ay} · {name} · PAN {pan}", rows,
        "Working paper prepared from the uploaded ITR-1 JSON. Figures are read as filed; this tool "
        "does not recompute tax or generate portal JSON. Verify against the filed return."),
    file_name="itr1-computation.pdf", mime="application/pdf")

st.caption("Reads salary + interest ITR-1 returns. Field names follow the e-filing ITR-1 schema "
           "with fallbacks; if a value reads as 0, confirm it exists under the expected key in your JSON.")
