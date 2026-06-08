import streamlit as st
from shared import style, brandbar

style("Section Mapper 1961 ↔ 2025", "🔁")
st.title("Income-tax Act 1961 ↔ 2025 — Section Mapper")
brandbar("Effective 1 April 2026 · Tax Year 2026-27 · partial reference, verify before relying")

st.warning("For **FY 2025-26** (the July 2026 ITR season) you still use the **old 1961** section "
           "numbers. The new 2025-Act numbers apply from **Tax Year 2026-27** onwards.")

# verified mappings (old 1961 -> new 2025). Compiled from public CBDT-correspondence-based sources.
MAP = [
    dict(old="80C", new="123", subject="Deductions — LIC/PF/PPF/ELSS/tuition/housing principal",
         note="₹1.5L cap unchanged; available under the old regime only.",
         alias=["80C"]),
    dict(old="80D", new="126", subject="Medical insurance premium",
         note="₹25,000 / ₹50,000 limits unchanged.", alias=["80D"]),
    dict(old="115BAC", new="202", subject="Default (new) tax regime",
         note="Now the default regime; ₹75,000 standard deduction codified in the Act.", alias=["115BAC"]),
    dict(old="44AB", new="63", subject="Tax audit",
         note="Audit thresholds substantively preserved.", alias=["44AB"]),
    dict(old="234A", new="423", subject="Interest — late filing of return",
         note="1% per month; mechanics unchanged.", alias=["234A"]),
    dict(old="234B", new="424", subject="Interest — default in advance tax",
         note="1% per month from 1 Apr of the tax year.", alias=["234B"]),
    dict(old="234C", new="425", subject="Interest — deferment of advance tax instalments",
         note="1% per month per shortfall instalment.", alias=["234C"]),
    dict(old="139", new="263", subject="Return of income",
         note="ITR-U (updated return) window extended to 48 months.", alias=["139"]),
    dict(old="147", new="279", subject="Income escaping assessment",
         note="2021 reassessment structure preserved in substance.", alias=["147"]),
    dict(old="148", new="280", subject="Notice for reassessment", note="", alias=["148"]),
    dict(old="148A", new="281", subject="Show-cause procedure before reassessment", note="", alias=["148A"]),
    dict(old="149", new="282", subject="Time limit for reassessment", note="", alias=["149"]),
    dict(old="151", new="284", subject="Sanction for reassessment", note="", alias=["151"]),
    dict(old="192", new="392", subject="TDS on salary",
         note="Payment codes 1001–1004; quarterly Form 138.", alias=["192"]),
    dict(old="194A/194C/194I/194J", new="393(1)", subject="TDS — resident non-salary payments",
         note="All non-salary resident TDS consolidated under Section 393; quote numeric payment "
              "codes (1005–1038), not the old section number.",
         alias=["194A","194B","194C","194D","194H","194I","194J","194K","194Q","193","194"]),
    dict(old="195", new="393(2)", subject="TDS on payments to non-residents",
         note="Under the consolidated Section 393; codes 1039–1057.", alias=["195"]),
    dict(old="206C", new="394", subject="Tax collected at source (TCS)",
         note="Codes 1068–1092.", alias=["206C","206"]),
    dict(old="10", new="Schedule II", subject="Exemptions (HRA, gratuity, leave encashment, etc.)",
         note="Section 10 exemptions moved to Schedule II; substance preserved.",
         alias=["10","10(13A)","10(10D)","10(14)"]),
    dict(old="2 / 3 (PY & AY)", new="3 (Tax Year)", subject="Previous Year & Assessment Year",
         note="Replaced by a single 'Tax Year' running 1 Apr–31 Mar.", alias=["3","2"]),
]

def norm(s):
    s = str(s).lower().replace("section", "").replace("sec.", "").replace("sec", "").replace("s.", "")
    return s.replace(" ", "").replace("§", "").strip().upper()

direction = st.radio("Direction", ["Old (1961) → New (2025)", "New (2025) → Old (1961)"], horizontal=True)
old_to_new = direction.startswith("Old")

st.caption("Popular: 80C · 80D · 115BAC · 139 · 147 · 148 · 192 · 194J · 195 · 234A · 234B · 234C · 44AB · 10")
q = st.text_input("Enter a section number", placeholder="e.g. 80C, 139, 194J, 10(13A), 195")

def find(query):
    n = norm(query)
    hits = []
    for e in MAP:
        keys = ([norm(a) for a in e["alias"]] + [norm(e["old"])]) if old_to_new else [norm(e["new"])]
        if any(n == k or (len(n) >= 2 and (n == k or k.startswith(n) or n.startswith(k))) for k in keys):
            hits.append(e)
    return hits

if q:
    res = find(q)
    if res:
        for e in res:
            src, dst = (e["old"], e["new"]) if old_to_new else (e["new"], e["old"])
            st.markdown(f"<div class='bestcard'><b>{src}</b> &nbsp;→&nbsp; <b>{dst}</b><br>"
                        f"<span class='muted'>{e['subject']}</span>"
                        f"{'<br>' + e['note'] if e['note'] else ''}</div>", unsafe_allow_html=True)
    else:
        st.info("Not in this partial reference set. Check the official CBDT section-to-clause "
                "correspondence or a full mapper for complete coverage.")

with st.expander("Browse all mapped sections"):
    st.markdown("| Old (1961) | New (2025) | Subject |\n|---|---|---|")
    for e in MAP:
        st.markdown(f"| {e['old']} | {e['new']} | {e['subject']} |")

st.caption("Partial reference covering commonly-cited sections, compiled from public sources based "
           "on the CBDT section-to-clause correspondence (ClearTax, Tax2win, Taxmann, CAclubindia, "
           "CA Alok Kumar, KDK). The 1961 Act’s ~819 sections map to ~536 in the 2025 Act; many "
           "provisions are merged (e.g. TDS under §393) or moved to schedules (e.g. §10 → Sch II). "
           "Not professional advice — verify against the bare Act before relying.")
