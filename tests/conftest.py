from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from fr_retraite_complementaire.models import FundEntry, FundTable


@pytest.fixture
def synthetic_fund() -> FundTable:
    """A small, hand-built fund table spanning all three currency regimes."""
    entries = [
        FundEntry(date(1958, 1, 1), Decimal(100), Decimal(10), "FRF (ancien)"),
        FundEntry(date(1960, 1, 1), Decimal(2), Decimal("0.5"), "FRF"),
        FundEntry(date(1970, 1, 1), Decimal(4), None, "FRF"),  # unchanged sell value
        FundEntry(date(2002, 1, 1), Decimal(5), Decimal(1), "EUR"),
        FundEntry(date(2026, 1, 1), Decimal(6), None, "EUR"),  # not yet published
    ]
    return FundTable(name="synthetic", entries=entries)


@pytest.fixture
def tmp_career_csv(tmp_path: Path) -> Path:
    path = tmp_path / "career.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["fund", "date", "points"])
        writer.writerow(["agirc", "1995-06-01", "120.5"])
        writer.writerow(["arrco", "1995-06-01", "80"])
    return path
