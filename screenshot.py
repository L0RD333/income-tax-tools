"""Capture a real screenshot of the running app (for the README).

    pip install playwright && playwright install chromium
    streamlit run Home.py          # terminal 1
    python screenshot.py           # terminal 2  -> docs/screenshot.png
Optionally pass a URL: python screenshot.py http://localhost:8501/Income_Tax_Calculator
"""
import sys, pathlib
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8501"
out = pathlib.Path("docs"); out.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(URL, wait_until="networkidle")
    pg.wait_for_timeout(4000)
    pg.screenshot(path=str(out / "screenshot.png"), full_page=True)
    b.close()
print("saved docs/screenshot.png")
