from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "integration" / "fixtures"


@pytest.fixture
def sample_csv(fixtures_dir):
    return fixtures_dir / "sample.csv"
