from datetime import date
from decimal import Decimal

import pytest

from fr_retraite_complementaire.career import Career, UnknownFundError
from fr_retraite_complementaire.models import NoValueAvailableError


def test_add_points_unknown_fund_raises():
    career = Career()
    with pytest.raises(UnknownFundError):
        career.add_points(fund="not-a-fund", date=date(2000, 1, 1), points=10)


def test_total_points_aggregates_per_fund():
    career = Career()
    career.add_points(fund="agirc", date=date(1995, 1, 1), points=10)
    career.add_points(fund="agirc", date=date(1996, 1, 1), points=5)
    career.add_points(fund="arrco", date=date(1996, 1, 1), points=20)

    assert career.total_points("agirc") == Decimal(15)
    assert career.total_points("arrco") == Decimal(20)
    assert career.total_points() == Decimal(35)
    assert career.funds() == {"agirc", "arrco"}


def test_annuity_combines_funds():
    career = Career()
    career.add_points(fund="agirc", date=date(1995, 1, 1), points=100)
    career.add_points(fund="arrco", date=date(1995, 1, 1), points=50)

    as_of = date(2018, 11, 1)  # a date both unified tables publish

    breakdown = career.breakdown(as_of)
    fund_names = {entry.fund for entry in breakdown}
    assert fund_names == {"agirc", "arrco"}

    total = career.annuity(as_of)
    assert total == sum(e.annual_amount_eur for e in breakdown)
    assert total > 0


def test_annuity_raises_before_fund_existed():
    career = Career()
    career.add_points(fund="agirc", date=date(1950, 1, 1), points=10)
    with pytest.raises(NoValueAvailableError):
        career.annuity(as_of=date(1946, 1, 1))
