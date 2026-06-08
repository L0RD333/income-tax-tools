"""Unit tests for the FY 2025-26 tax engine and combined capital-gains logic."""
import pytest
import shared as s


# ---------------- INR formatting ----------------
@pytest.mark.parametrize("val,expected", [
    (0, "₹0"), (500, "₹500"), (1000, "₹1,000"), (100000, "₹1,00,000"),
    (1200000, "₹12,00,000"), (-5000, "-₹5,000"),
])
def test_inr(val, expected):
    assert s.inr(val) == expected


# ---------------- new regime ----------------
def test_new_regime_rebate_makes_12L_nil():
    # ₹12.75L salary -> ₹12L taxable -> rebate -> nil
    assert s.regime_new(1275000, True, "below60", 0)["total"] == 0

def test_new_regime_15L_taxable():
    # 20000 + 40000 + 45000 = 105000; +4% cess = 109200
    assert s.regime_new(1500000, False, "below60", 0)["total"] == 109200

def test_new_regime_16L_taxable():
    assert s.regime_new(1600000, False, "below60", 0)["total"] == 124800

def test_new_regime_marginal_relief_just_above_12L():
    # taxable 12,10,000 -> MR caps tax at the ₹10,000 excess (+cess)
    r = s.regime_new(1210000, False, "below60", 0)
    assert r["total"] == round(10000 * 1.04)  # 10400

def test_new_regime_standard_deduction_75k():
    assert s.regime_new(800000, True, "below60", 0)["ti"] == 725000


# ---------------- old regime ----------------
def test_old_regime_5L_rebate_nil():
    # ₹5.5L gross, salaried -> ₹5L taxable -> 87A rebate -> nil
    assert s.regime_old(550000, True, "below60", 0)["total"] == 0

def test_old_regime_10L_taxable():
    # gross 12L - 50k SD - 1.5L ded = 10L taxable; 12500 + 100000 = 112500; +4% = 117000
    assert s.regime_old(1200000, True, "below60", 150000)["total"] == 117000

def test_old_regime_senior_exemption_3L():
    assert s.regime_old(300000, False, "senior", 0)["total"] == 0

def test_old_regime_super_senior_exemption_5L():
    assert s.regime_old(500000, False, "super", 0)["total"] == 0


# ---------------- surcharge + marginal relief ----------------
def test_new_regime_surcharge_60L():
    # base 13,80,000 -> 10% surcharge (no MR) -> *1.04 = 15,78,720
    assert s.regime_new(6000000, False, "below60", 0)["total"] == 1578720

def test_new_regime_surcharge_capped_at_25pct():
    # very high income: surcharge rate must not exceed 25% under the new regime
    r = s.regime_new(60000000, False, "below60", 0)
    implied = r["sc"] / r["after"]
    assert implied <= 0.25 + 1e-9


# ---------------- basic-exemption adjustment (combined) ----------------
def test_be_adjustment_stcg_new():
    cg = dict(stcg_eq=500000, ltcg_eq_taxable=0, ltcg_oth=0, idx_gain=0)
    r = s.combined(0, False, "below60", "new", 0, cg)
    assert r["special"]["be_used"] == 400000      # ₹4L basic limit absorbed
    assert r["special"]["stcg"] == 100000         # remaining gain
    assert r["total"] == 20800                     # 100000*20% *1.04

def test_be_adjustment_ltcg_old_senior():
    cg = dict(stcg_eq=0, ltcg_eq_taxable=0, ltcg_oth=400000, idx_gain=0)
    r = s.combined(200000, False, "senior", "old", 0, cg)
    assert r["special"]["be_used"] == 100000       # 3L limit - 2L income
    assert r["total"] == 39000                      # 300000*12.5% *1.04

def test_combined_equity_ltcg_on_top():
    cg = dict(stcg_eq=0, ltcg_eq_taxable=300000, ltcg_oth=0, idx_gain=0)
    r = s.combined(600000, True, "below60", "new", 0, cg)
    # normal ti 525000 (slab tax rebated to 0); LTCG 300000*12.5% = 37500; +cess = 39000
    assert r["total"] == 39000

def test_cg_surcharge_capped_15pct():
    # large gains: surcharge on the special component must be capped at 15%
    cg = dict(stcg_eq=30000000, ltcg_eq_taxable=0, ltcg_oth=0, idx_gain=0)
    r = s.combined(0, False, "below60", "new", 0, cg)
    sp_tax = r["special"]["tax"]
    # surcharge attributable to gains should be <= 15% of special tax
    assert r["surcharge"] <= sp_tax * 0.15 + 1e-6


# ---------------- basic_limit ----------------
def test_basic_limit_values():
    assert s.basic_limit("new", "below60") == 400000
    assert s.basic_limit("old", "below60") == 250000
    assert s.basic_limit("old", "senior") == 300000
    assert s.basic_limit("old", "super") == 500000


# ---------------- PDF builder ----------------
def test_build_pdf_returns_valid_bytes():
    pdf = s.build_pdf("Test", "subtitle", [("Item", "₹1,000"), ("**Total", "₹2,000")], "note")
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 1000
