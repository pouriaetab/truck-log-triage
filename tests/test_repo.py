"""Step 0: rules for the repository itself. Run: uv run pytest -v"""

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # the repo folder
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text())


def test_data_is_never_committed():
    # IMPORTANT: the data's license allows sharing only with its own terms, so it never goes into git
    assert "data/" in (ROOT / ".gitignore").read_text().splitlines()


def test_every_dependency_has_an_exact_version():
    deps = PROJECT["project"]["dependencies"] + PROJECT["dependency-groups"]["dev"]
    assert deps and all("==" in d for d in deps)  # pandas==3.1.0, never just pandas


def test_the_lock_file_is_committed():
    # uv.lock pins every package, including the ones our packages pull in, so every machine installs the same set
    assert (ROOT / "uv.lock").exists()
