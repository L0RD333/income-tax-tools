import streamlit as st
from shared import (style, brandbar, inr, regime_new, regime_old, combined, build_pdf)

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

cg = st.session_state.get("cg_gains")
include_cg = st.checkbox("Add capital gains on top (from the Capital Gains tab)",
                         value=False, disabled=(cg is None))
if cg is None:
    st.caption("Open the **Capital Gains** tab and compute once — your gains will then be "
               "selectable here.")
elif include_cg:
    g = cg["stcg_eq"] + cg["ltcg_eq_taxable"] + cg["ltcg_oth"]
    st.caption(f"Including capital gains from the Capital Gains tab: STCG {inr(cg['stcg_eq'])}, "
               f"LTCG equity (taxable) {inr(cg['ltcg_eq_taxable'])}, LTCG other {inr(cg['ltcg_oth'])}.")

if include_cg and cg:
    cnew = combined(gross, salaried, age, "new", ded_new, cg)
    cold = combined(gross, salaried, age, "old", ded_old, cg)
    new_total, old_total = cnew["total"], cold["total"]
else:
    nb = regime_new(gross, salaried, age, ded_new)
    ob = regime_old(gross, salaried, age, ded_old)
    new_total, old_total = nb["total"], ob["total"]

best = "New" if new_total <= old_total else "Old"
saving = abs(new_total - old_total)
st.session_state["it_total"] = new_total if best=="New" else old_total
st.session_state["it_regime"] = best

st.subheader("Result")
r1, r2 = st.columns(2)
r1.metric("New Regime — total tax", inr(new_total),
          delta=None if best=="New" else f"+{inr(new_total-old_total)}", delta_color="inverse")
r2.metric("Old Regime — total tax", inr(old_total),
          delta=None if best=="Old" else f"+{inr(old_total-new_total)}", delta_color="inverse")
st.markdown(f"<div class='bestcard'>✅ <b>{best} Regime</b> is better by <b>{inr(saving)}</b>. "
            f"{'New regime is the default.' if best=='New' else 'Opt out of the default new regime when filing.'}"
            f"</div>", unsafe_allow_html=True)
net = (new_total if best=="New" else old_total) - tds
st.markdown(f"<p class='muted'>Net under the {best.lower()} regime after TDS/advance tax: "
            f"<b>{inr(net) if net>=0 else 'Refund '+inr(-net)}</b></p>", unsafe_allow_html=True)

# breakdown + PDF for the chosen regime
if include_cg and cg:
    ch = cnew if best == "New" else cold
    nrm, sp = ch["normal"], ch["special"]
    rows = [("##Normal (slab) income",""),
            ("Standard deduction", inr(nrm["sd"])),
            ("Taxable normal income", inr(nrm["ti"])),
            ("Slab tax after 87A rebate", inr(nrm["after"])),
            ("##Capital gains (taxed on top)",""),
            ("Basic-exemption set off against gains", inr(sp["be_used"])),
            ("STCG 111A @20%", inr(sp["tax_stcg"])),
            ("LTCG equity 112A @12.5%", inr(sp["tax_eq"])),
            ("LTCG other @12.5%", inr(sp["tax_oth"])),
            ("##Aggregate",""),
            ("Surcharge", inr(ch["surcharge"])),
            ("Cess (4%)", inr(ch["cess"])),
            ("**Total tax", inr(ch["total"])),
            ("TDS / advance tax paid", inr(tds)),
            ("**Net payable / refund", inr(net) if net>=0 else "Refund "+inr(-net))]
    with st.expander("Detailed breakdown (chosen regime, incl. capital gains)"):
        for l, v in rows:
            if l.startswith("##"): st.markdown(f"**{l[2:]}**")
            else: st.markdown(f"- {l.replace('**','')}: **{v}**")
    note = ("Capital gains taxed on top of slab income with resident basic-exemption adjustment "
            "(highest-rate gains first). Surcharge on capital gains is capped at 15%; surcharge "
            "marginal relief is approximate. Verify before filing.")
else:
    nb = regime_new(gross, salaried, age, ded_new); ob = regime_old(gross, salaried, age, ded_old)
    ch = nb if best == "New" else ob
    rows = [("##Computation (%s regime)" % best.lower(), ""),
            ("Standard deduction", inr(ch["sd"])),
            ("Other deductions", inr(ded_new if best=="New" else ded_old)),
            ("Taxable income", inr(ch["ti"])),
            ("Tax before rebate", inr(ch["base"])),
            ("87A rebate", "-"+inr(ch["rebate"])),
            ("Surcharge", inr(ch["sc"])),
            ("Cess (4%)", inr(ch["cess"])),
            ("**Total tax", inr(ch["total"])),
            ("TDS / advance tax paid", inr(tds)),
            ("**Net payable / refund", inr(net) if net>=0 else "Refund "+inr(-net))]
    with st.expander("Detailed breakdown"):
        n = regime_new(gross, salaried, age, ded_new); o = regime_old(gross, salaried, age, ded_old)
        st.markdown("| Particulars | New Regime | Old Regime |\n|---|---:|---:|")
        st.markdown(f"| Standard deduction | {inr(n['sd'])} | {inr(o['sd'])} |")
        st.markdown(f"| Taxable income | {inr(n['ti'])} | {inr(o['ti'])} |")
        st.markdown(f"| Tax before rebate | {inr(n['base'])} | {inr(o['base'])} |")
        st.markdown(f"| 87A rebate | -{inr(n['rebate'])} | -{inr(o['rebate'])} |")
        st.markdown(f"| Surcharge | {inr(n['sc'])} | {inr(o['sc'])} |")
        st.markdown(f"| Cess (4%) | {inr(n['cess'])} | {inr(o['cess'])} |")
        st.markdown(f"| **Total tax** | **{inr(n['total'])}** | **{inr(o['total'])}** |")
    note = ("Estimate for resident individuals. 87A rebate applies to regular income only. "
            "Surcharge marginal relief is approximate at very high incomes.")

st.session_state["report_it"] = rows
st.download_button("⬇ Download computation (PDF)",
    data=build_pdf("Income Tax Computation",
        f"FY 2025-26 (AY 2026-27) · {best} regime" + (" · incl. capital gains" if (include_cg and cg) else ""),
        rows, note),
    file_name="income-tax-computation.pdf", mime="application/pdf")
