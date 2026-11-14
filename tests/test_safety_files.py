import csv
from pathlib import Path

from safety_stats import asil

SAFETY = Path(__file__).parent.parent / "docs" / "safety"


def rows(name):
    return list(csv.DictReader((SAFETY / name).open()))


def test_hara_asil_matches_s_e_c():
    for r in rows("hara.csv"):
        assert r["ASIL"] == asil(int(r["S"]), int(r["E"]), int(r["C"])), r["id"]


def test_fmea_rpn_is_s_times_o_times_d():
    for r in rows("fmea.csv"):
        assert int(r["RPN"]) == int(r["S"]) * int(r["O"]) * int(r["D"]), r["id"]


def test_every_row_says_where_it_is_tested():
    for r in rows("hara.csv") + rows("fmea.csv"):
        assert (r.get("checked_in") or r.get("tested_in")).startswith("Step"), r["id"]


def test_every_s3_hazard_is_flagged_for_review():
    for r in rows("hara.csv"):
        assert r["review"] == ("yes" if r["S"] == "3" else "no"), r["id"]
