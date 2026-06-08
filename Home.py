import streamlit as st
from shared import style, brandbar

style("Rahul — Income Tax Tools", "🧮")
st.title("Income Tax Tools")
brandbar("FY 2025-26 (AY 2026-27) · Resident individuals · Estimates only")

st.markdown("""
A suite of Indian income-tax calculators. Pick a tool from the sidebar:

- **Income Tax Calculator** — Old vs New regime, rebate, surcharge, cess; optionally adds capital gains on top.
- **HRA Exemption** — Section 10(13A) / Rule 2A least-of-three.
- **Capital Gains** — post-July-2024 rates, set-off, and loss carry-forward tracking (CSV in/out).
- **Advance Tax** — instalment schedule and 234C / 234B interest estimate.
- **ITR Form Selector** — which of ITR-1 … ITR-7 to file.
- **Section Mapper** — Income-tax Act 1961 ↔ 2025 section lookup (partial reference).
- **Full Computation Report** — merges Income Tax, HRA, Capital Gains and Advance Tax into one PDF.

> Estimates for common resident-individual cases. Verify with the official portal / ITR utility
> before filing. The new regime is the default u/s 115BAC.
""")
st.caption("Built by Rahul · for educational and planning use.")
