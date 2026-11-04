"""Step 0: rules for the repository itself. Run: python3 -m pytest -v"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] # the repo folder

def test_data_is_never_committed():
    # IMPORTANT: the data's license allows sharing only with its own terms, so it never goes into git
    assert "data/" in (ROOT / ".gitignore").read_text().splitlines()


def test_every_requirement_has_an_exact_version():
    lines = [x for x in (ROOT / "requirements.txt").read_text().splitlines() if x and not x.startswith("#")]
    assert lines and all("==" in x for x in lines) # pandas==3.1.0 never just pandas