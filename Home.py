import streamlit as st
from shared import style, brandbar

style("Rahul — Income Tax Tools", "🧮")
st.title("Income Tax Tools")
brandbar("FY 2025-26 (AY 2026-27) · Resident individuals · Estimates only")

st.markdown("""
A small suite of Indian income-tax calculators. Pick a tool from the sidebar:

- **Income Tax Calculator** — Old vs New regime comparison with rebate, surcharge and cess.
- **HRA Exemption** — House Rent Allowance exemption under Section 10(13A) / Rule 2A.
- **Capital Gains** — STCG/LTCG on equity and other assets at the post-July-2024 rates.

> These are estimates for resident individuals on common cases. Verify with the official
> portal / ITR utility before filing. The new regime is the default u/s 115BAC.
""")
st.caption("Built by Rahul · for educational and planning use.")
