from datetime import date
from decimal import Decimal

import pytest

from fr_retraite_complementaire.currency import FRF_PER_EUR
from fr_retraite_complementaire.models import NoValueAvailableError


def test_before_earliest_date_raises(synthetic_fund):
    with pytest.raises(NoValueAvailableError):
        synthetic_fund.sell_value_eur(date(1957, 12, 31))


def test_exact_match(synthetic_fund):
    assert synthetic_fund.sell_value_eur(date(1960, 1, 1)) == Decimal("0.5") / FRF_PER_EUR


def test_carries_forward_between_entries(synthetic_fund):
    # Just before the 1970 entry, still governed by the 1960 entry.
    assert synthetic_fund.sell_value_eur(date(1969, 12, 31)) == Decimal("0.5") / FRF_PER_EUR


def test_carries_forward_through_blank_sell_value(synthetic_fund):
    # The 1970 entry has no sell value of its own; it must fall back to
    # the last known value (from 1960), even though acquisition cost
    # changed in 1970.
    assert synthetic_fund.sell_value_eur(date(1971, 1, 1)) == Decimal("0.5") / FRF_PER_EUR


def test_eur_regime(synthetic_fund):
    assert synthetic_fund.sell_value_eur(date(2002, 1, 1)) == Decimal(1)


def test_falls_back_when_latest_entry_not_yet_published(synthetic_fund):
    # The 2026 entry has no sell value yet; must fall back to 2002's.
    assert synthetic_fund.sell_value_eur(date(2026, 6, 1)) == Decimal(1)


def test_acquisition_cost_ancien_franc(synthetic_fund):
    # 100 (ancien francs) -> 1 nouveau franc -> 1/FRF_PER_EUR euros
    assert synthetic_fund.acquisition_cost_eur(date(1958, 1, 1)) == Decimal(1) / FRF_PER_EUR
