# Income Tax Tools — FY 2025-26 (AY 2026-27)

A multi-page Streamlit site with three Indian income-tax calculators for resident
individuals. Built by Rahul.

| Page | What it does |
|---|---|
| **Income Tax Calculator** | Old vs New regime comparison — slabs, 87A rebate, surcharge (with marginal relief), 4% cess, best-regime + net payable. |
| **HRA Exemption** | Section 10(13A) / Rule 2A — least of actual HRA, 40%/50% of salary, rent − 10% of salary. Old regime only. |
| **Capital Gains** | Post-23-Jul-2024 rates — equity STCG 111A @20%, equity LTCG 112A @12.5% (₹1.25L exempt), other LTCG @12.5%, basic set-off and 54-series exemption. Feeds into the Income Tax page. |

> Estimates for common cases — verify with the official portal / ITR utility before
> filing. The new regime is the default u/s 115BAC; the 87A rebate applies to regular
> income, not special-rate income such as capital gains.


## Wiring & PDF export
- Compute once on the **Capital Gains** tab — the gains are stored in session and can be
  pulled into the **Income Tax** tab via *“Add capital gains on top”*. There they are taxed
  above slab income with the **resident basic-exemption adjustment** (unused basic-exemption
  limit set off against the highest-rate gains first) and capital-gains surcharge capped at 15%.
- Every page has a **⬇ Download computation (PDF)** button. PDFs use the bundled DejaVuSans
  font (in `assets/`) so the ₹ symbol renders correctly.

## Project layout
```
Home.py                       # landing page (Streamlit entrypoint)
shared.py                     # styling, ₹ formatting, income-tax engine
pages/
  1_Income_Tax_Calculator.py
  2_HRA_Exemption.py
  3_Capital_Gains.py
assets/                       # bundled DejaVuSans fonts (for ₹ in PDFs)
requirements.txt
.github/workflows/ci.yml      # byte-compile + engine sanity check on push/PR
```

## Run locally
```bash
pip install -r requirements.txt
streamlit run Home.py
```
Open http://localhost:8501 — the three tools appear in the left sidebar.

## Push to GitHub
Create an empty **public** repo on GitHub (no README), then:
```bash
git remote add origin https://github.com/<your-username>/income-tax-tools.git
git push -u origin main
```
(This bundle already has a commit on `main`.)

## Deploy free on Streamlit Community Cloud
1. Go to https://share.streamlit.io and sign in with GitHub.
2. **Create app → Deploy a public app from GitHub**.
3. Repo: yours · Branch: `main` · **Main file path: `Home.py`** → **Deploy**.
4. You get a public URL like `https://<your-app>.streamlit.app`.
