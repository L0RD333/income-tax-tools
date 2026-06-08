import streamlit as st
from shared import style, brandbar, build_pdf

style("Full Computation Report", "📄")
st.title("Full Computation Report")
brandbar("FY 2025-26 (AY 2026-27) · Merged report — Income Tax · HRA · Capital Gains")

st.markdown("Visit each calculator once; this page merges their latest results into a single PDF.")

sources = [("Income Tax", st.session_state.get("report_it")),
           ("HRA Exemption", st.session_state.get("report_hra")),
           ("Capital Gains", st.session_state.get("report_cg")),
           ("Advance Tax", st.session_state.get("report_advtax"))]
available = [(name, rows) for name, rows in sources if rows]
missing = [name for name, rows in sources if not rows]

c1, c2 = st.columns(2)
c1.metric("Sections ready", f"{len(available)} / 4")
if missing:
    c2.caption("Not yet computed: " + ", ".join(missing) +
               ". Open those tabs and compute to include them.")

for name, rows in available:
    with st.expander(f"{name} — preview", expanded=False):
        for label, value in rows:
            if label.startswith("##"):
                st.markdown(f"**{label[2:]}**")
            else:
                st.markdown(f"- {label.replace('**','')}: **{value}**")

if available:
    merged = []
    for name, rows in available:
        merged.append((f"## {name}", ""))
        merged.extend(rows)
    pdf = build_pdf("Full Tax Computation",
                    "FY 2025-26 (AY 2026-27) · Resident individual · prepared by Rahul",
                    merged,
                    "Combined estimate from the Income Tax, HRA and Capital Gains tools. "
                    "Each is an estimate for common resident-individual cases — verify with the "
                    "official portal / ITR utility before filing.")
    st.download_button("⬇ Download FULL computation (single PDF)", data=pdf,
                       file_name="full-tax-computation.pdf", mime="application/pdf",
                       type="primary")
else:
    st.info("No sections computed yet. Open the calculator tabs in the sidebar and run them, "
            "then return here to download the merged report.")
