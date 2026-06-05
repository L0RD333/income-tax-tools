# Income Tax Calculator — FY 2025-26 (AY 2026-27)

A Streamlit web app that compares **Old Regime vs New Regime** income tax for
resident individuals, with Section 87A rebate, surcharge (with marginal relief),
and 4% health & education cess.

> Estimate only — verify with the official portal / ITR utility before filing.
> The 87A rebate applies to regular slab income, not special-rate income such as
> capital gains.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Then open http://localhost:8501

## Deploy free on Streamlit Community Cloud
1. Push this folder to a **public GitHub repo** (steps below).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app** → **Deploy a public app from GitHub**.
4. Pick your repo, branch `main`, main file `app.py` → **Deploy**.
5. You get a public URL like `https://<your-app>.streamlit.app`.

## Tax logic (FY 2025-26)
- **New regime** slabs: nil ≤ ₹4L, 5% (4–8L), 10% (8–12L), 15% (12–16L),
  20% (16–20L), 25% (20–24L), 30% above ₹24L. Standard deduction ₹75,000
  (salaried). 87A rebate up to ₹60,000 → income ≤ ₹12L taxable pays nil, with
  marginal relief just above ₹12L. Surcharge capped at 25%.
- **Old regime** slabs: basic exemption ₹2.5L / ₹3L (senior) / ₹5L (super senior),
  5% (to 5L), 20% (5–10L), 30% above ₹10L. Standard deduction ₹50,000 (salaried).
  87A rebate ₹12,500 → income ≤ ₹5L taxable pays nil. Surcharge up to 37%.
- 4% cess on tax + surcharge in both regimes.
