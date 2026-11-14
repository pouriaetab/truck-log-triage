from safety_stats import asil, e_class, miles_needed, wilson


def test_e_class_uses_iso_shares():
    assert [e_class(x) for x in (0.2, 0.05, 0.005, 0)] == ["E4", "E3", "E2", "E1"]


def test_asil_matches_table_4():
    assert asil(3, 4, 3) == "D"  # missed stopped car on the highway, no driver to take over
    assert asil(3, 4, 2) == "C"
    assert asil(2, 4, 2) == "B"  # phantom hard brake, the car behind can usually react
    assert asil(1, 3, 3) == "A"
    assert asil(0, 4, 3) == "QM"


def test_wilson_small_sample():
    lo, hi = wilson(2, 10)
    assert round(lo, 3) == 0.057 and round(hi, 3) == 0.510


def test_rule_of_three():
    assert round(miles_needed(1.19e-8) / 1e6) == 252  # NHTSA 2024: 1.19 deaths per 100 million miles
