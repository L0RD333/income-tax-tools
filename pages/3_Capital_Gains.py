import streamlit as st
import pandas as pd
from shared import style, brandbar, inr, build_pdf

CESS = 0.04
CUR_AY = 2026          # AY 2026-27
CUR_AY_LABEL = "2026-27"
style("Capital Gains Calculator", "📈")
st.title("Capital Gains Calculator")
brandbar("FY 2025-26 (AY 2026-27) · Post-23-July-2024 rates · with loss carry-forward")

st.markdown("Rates: equity **STCG 111A @20%**, equity **LTCG 112A @12.5%** after **₹1.25L**, "
            "other **LTCG @12.5%**.")

st.subheader("Current-year gains")
c1, c2 = st.columns(2)
with c1:
    stcg_eq = st.number_input("STCG — equity / equity MF, 111A (₹)", min_value=0, value=0, step=10000)
    ltcg_eq = st.number_input("LTCG — equity / equity MF, 112A (₹)", min_value=0, value=0, step=10000)
    ltcg_oth = st.number_input("LTCG — other assets @12.5% (₹)", min_value=0, value=0, step=10000)
with c2:
    stcl_cy = st.number_input("Current-year short-term capital LOSS (₹)", min_value=0, value=0, step=10000)
    ltcl_cy = st.number_input("Current-year long-term capital LOSS (₹)", min_value=0, value=0, step=10000)
    exm54 = st.number_input("Section 54 / 54F / 54EC exemption vs LTCG (₹)", min_value=0, value=0, step=10000)

with st.expander("Brought-forward losses from earlier years (carry-forward tracking)"):
    st.caption("STCL may set off against STCG and LTCG; LTCL only against LTCG. Unabsorbed losses "
               "carry forward up to **8 assessment years** from the year they arose, then lapse.")
    up = st.file_uploader("Prefill from last year's carry-forward CSV (optional)", type=["csv"], key="cf_csv")
    if up is not None:
        try:
            import re
            raw = pd.read_csv(up)
            def _amt(v): return float(re.sub(r"[^0-9.]", "", str(v)) or 0)
            def _pick(r, names):
                for n in names:
                    if n in r and str(r[n]).strip() != "": return r[n]
                return None
            recs = []
            for r in raw.to_dict("records"):
                ay = _pick(r, ["Assessment Year", "Loss origin (AY)"])
                tp = _pick(r, ["Loss type", "Type"]) or "STCL"
                am = _amt(_pick(r, ["Amount (₹)", "Amount"]))
                if ay and am > 0:
                    recs.append({"Assessment Year": str(ay), "Loss type": str(tp), "Amount (₹)": am})
            st.session_state["bf_default"] = recs or None
            st.success(f"Loaded {len(recs)} brought-forward loss row(s).")
        except Exception as e:
            st.error(f"Could not read CSV: {e}")
    base = st.session_state.get("bf_default")
    default = pd.DataFrame(base) if base else pd.DataFrame([{"Assessment Year": "", "Loss type": "STCL", "Amount (₹)": 0}])
    edited = st.data_editor(default, num_rows="dynamic", use_container_width=True,
        column_config={"Loss type": st.column_config.SelectboxColumn(options=["STCL", "LTCL"]),
                       "Amount (₹)": st.column_config.NumberColumn(min_value=0, step=10000),
                       "Assessment Year": st.column_config.TextColumn(help="e.g. 2022-23")})

with st.expander("Pre-23-July-2024 property — indexation comparison (optional)"):
    idx_gain = st.number_input("Indexed gain for 20%-with-indexation option (₹), 0 to skip",
                               min_value=0, value=0, step=10000)
tds = st.number_input("TDS / advance tax paid (₹)", min_value=0, value=0, step=5000)

# ---------------- set-off engine ----------------
g = {"stcg": float(stcg_eq), "lto": float(ltcg_oth), "lte": float(ltcg_eq)}

def off(loss, keys):
    for k in keys:
        t = min(loss, g[k]); g[k] -= t; loss -= t
    return loss

# 1) 54-series exemption reduces LTCG (other first, then equity)
ex = exm54
for k in ("lto", "lte"):
    t = min(ex, g[k]); g[k] -= t; ex -= t
# 2) current-year losses (STCL: STCG->LTCG; LTCL: LTCG)
rem_stcl_cy = off(float(stcl_cy), ["stcg", "lto", "lte"])
rem_ltcl_cy = off(float(ltcl_cy), ["lto", "lte"])

# 3) brought-forward losses (oldest first), tracking remaining per row
bf = []
for r in edited.to_dict("records"):
    ay_raw = str(r.get("Assessment Year", "")).strip()
    try: ay = int(ay_raw[:4])
    except: ay = None
    amt = float(r.get("Amount (₹)") or 0)
    typ = r.get("Loss type", "STCL")
    if ay and amt > 0:
        bf.append(dict(ay=ay, type=typ, amt=amt, rem=amt,
                       expires=ay + 8, expired=CUR_AY > ay + 8))
bf.sort(key=lambda x: x["ay"])
for row in bf:
    if row["expired"]:
        continue
    if row["type"] == "STCL":
        before = row["rem"]; row["rem"] = off(row["rem"], ["stcg", "lto", "lte"])
    else:
        before = row["rem"]; row["rem"] = off(row["rem"], ["lto", "lte"])

# ---------------- tax ----------------
stcg_net, ltcg_oth_net, ltcg_eq_net = g["stcg"], g["lto"], g["lte"]
ltcg_eq_taxable = max(0, ltcg_eq_net - 125000)
tax_stcg = stcg_net * 0.20
tax_ltcg_eq = ltcg_eq_taxable * 0.125
tax_ltcg_oth = min(ltcg_oth_net*0.125, idx_gain*0.20) if idx_gain > 0 else ltcg_oth_net*0.125
tax_before_cess = tax_stcg + tax_ltcg_eq + tax_ltcg_oth
total = round(tax_before_cess * (1 + CESS))
net = total - tds

st.session_state["cg_gains"] = dict(stcg_eq=stcg_net, ltcg_eq_taxable=ltcg_eq_taxable,
                                    ltcg_oth=ltcg_oth_net, idx_gain=idx_gain)

st.subheader("Result")
m1, m2, m3 = st.columns(3)
m1.metric("Total taxable gain", inr(stcg_net + ltcg_eq_taxable + ltcg_oth_net))
m2.metric("Tax before cess", inr(tax_before_cess))
m3.metric("Net payable / refund", inr(net) if net >= 0 else "Refund " + inr(-net))

# ---------------- carry-forward schedule ----------------
cf_rows = []
if rem_stcl_cy > 0:
    cf_rows.append((CUR_AY_LABEL, "STCL", rem_stcl_cy, f"{CUR_AY+8}-{str(CUR_AY+9)[2:]}"))
if rem_ltcl_cy > 0:
    cf_rows.append((CUR_AY_LABEL, "LTCL", rem_ltcl_cy, f"{CUR_AY+8}-{str(CUR_AY+9)[2:]}"))
for row in bf:
    if not row["expired"] and row["rem"] > 0:
        cf_rows.append((f"{row['ay']}-{str(row['ay']+1)[2:]}", row["type"], row["rem"],
                        f"{row['expires']}-{str(row['expires']+1)[2:]}"))
lapsed = [r for r in bf if r["expired"] and r["amt"] > 0]

st.subheader("Loss carry-forward to next year")
if cf_rows:
    df = pd.DataFrame([(ay, t, inr(a), exp) for ay, t, a, exp in cf_rows],
                      columns=["Loss origin (AY)", "Type", "Amount", "Carry-forward upto (AY)"])
    st.table(df)
    st.download_button("⬇ Download carry-forward schedule (CSV)",
        data=df.to_csv(index=False).encode(), file_name="loss-carry-forward.csv", mime="text/csv")
else:
    st.caption("No losses carry forward — all set off this year (or none entered).")
if lapsed:
    st.warning("Lapsed (older than 8 years, cannot be set off): " +
               ", ".join(f"{r['ay']}-{str(r['ay']+1)[2:]} {r['type']} {inr(r['amt'])}" for r in lapsed))

with st.expander("Transaction-wise working"):
    st.markdown("| Gain type | Taxable | Rate | Tax |\n|---|---:|---:|---:|")
    st.markdown(f"| STCG equity (111A) | {inr(stcg_net)} | 20% | {inr(tax_stcg)} |")
    st.markdown(f"| LTCG equity (112A, after ₹1.25L) | {inr(ltcg_eq_taxable)} | 12.5% | {inr(tax_ltcg_eq)} |")
    st.markdown(f"| LTCG other | {inr(ltcg_oth_net)} | {'lower 12.5%/20%' if idx_gain>0 else '12.5%'} | {inr(tax_ltcg_oth)} |")
    st.markdown(f"| Cess (4%) | | | {inr(tax_before_cess*CESS)} |")
    st.markdown(f"| **Total tax** | | | **{inr(total)}** |")

st.info("These gains feed the **Income Tax Calculator** tab — tick “Add capital gains on top”.")

rows = [("##Capital gains computation",""),
        ("STCG equity (111A) @20%", inr(stcg_net)),
        ("LTCG equity (112A) taxable @12.5%", inr(ltcg_eq_taxable)),
        ("LTCG other @12.5%", inr(ltcg_oth_net)),
        ("Tax before cess", inr(tax_before_cess)),
        ("Cess (4%)", inr(tax_before_cess*CESS)),
        ("**Total tax", inr(total)),
        ("TDS / advance tax paid", inr(tds)),
        ("**Net payable / refund", inr(net) if net>=0 else "Refund "+inr(-net))]
if cf_rows:
    rows.append(("##Loss carry-forward",""))
    for ay, t, a, exp in cf_rows:
        rows.append((f"{t} from AY {ay} (upto {exp})", inr(a)))
st.session_state["report_cg"] = rows
st.download_button("⬇ Download computation (PDF)",
    data=build_pdf("Capital Gains Computation", "FY 2025-26 (AY 2026-27) · Resident Individual/HUF",
        rows, "Set-off: 54-series, then current-year losses, then brought-forward (oldest first). "
        "STCL→STCG/LTCG, LTCL→LTCG. Unabsorbed losses carry forward 8 AYs. Verify before filing."),
    file_name="capital-gains-computation.pdf", mime="application/pdf")
