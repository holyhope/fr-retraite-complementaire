from datetime import date
from decimal import Decimal

import pytest

from fr_retraite_complementaire.data_loader import list_funds, load_all_funds, load_fund
from fr_retraite_complementaire.models import NoValueAvailableError


def test_list_funds_includes_known_funds():
    funds = list_funds()
    assert "agirc" in funds
    assert "arrco" in funds
    assert "agirc_arrco" in funds
    assert "agrr" in funds
    assert len(funds) == 53  # 3 unified tables + 49 affiliated funds + Ircantec


def test_load_fund_agirc_has_entries_sorted_ascending():
    table = load_fund("agirc")
    assert table.earliest_date == date(1947, 1, 1)
    dates = [e.starting_from for e in table.entries]
    assert dates == sorted(dates)


def test_load_fund_unknown_raises():
    import pytest

    with pytest.raises(FileNotFoundError):
        load_fund("not-a-real-fund")


def test_load_all_funds():
    tables = load_all_funds()
    assert len(tables) == len(list_funds())
    assert all(len(table) > 0 for table in tables.values())


def test_agirc_arrco_acquisition_cost_changes_on_january_1st():
    # Regression test: "Acquisition cost" (valeur d'achat du point)
    # takes effect Jan. 1st each year, while "Sell value" (valeur de
    # service du point) takes effect Nov. 1st -- they must not share a
    # single "Starting from" date, or one column lags by ~10 months.
    table = load_fund("agirc_arrco")

    # 2021's acquisition cost (17.3982) must still be in effect right
    # up to end of 2021, and 2022's new value (17.4316) must already be
    # in effect from Jan. 1st 2022 -- not from Nov. 1st 2022.
    assert table.acquisition_cost_eur(date(2021, 12, 31)) == Decimal("17.3982")
    assert table.acquisition_cost_eur(date(2022, 1, 1)) == Decimal("17.4316")
    assert table.acquisition_cost_eur(date(2022, 10, 31)) == Decimal("17.4316")

    # The sell value, meanwhile, only flips on Nov. 1st.
    assert table.sell_value_eur(date(2022, 10, 31)) == Decimal("1.2841")
    assert table.sell_value_eur(date(2022, 11, 1)) == Decimal("1.3498")


def test_ircantec_acquisition_cost_and_sell_value_split_rows():
    # Regression test: Ircantec's "salaire de reference" (acquisition
    # cost, from 1947) and "valeur de service du point" (sell value,
    # from 2011) are two independently dated series -- not a single
    # once-a-year row like this design originally assumed.
    table = load_fund("ircantec")
    assert table.earliest_date == date(1947, 1, 1)
    assert table.latest_date == date(2026, 1, 1)

    # Acquisition cost: known published values, cross-checked against
    # the source's own euro-equivalent column.
    assert table.acquisition_cost_eur(date(1947, 1, 1)) == pytest.approx(
        Decimal("0.0396"), abs=1e-4
    )
    assert table.acquisition_cost_eur(date(2026, 1, 1)) == Decimal("5.787")

    # Sell value: irregular pre-2019 effective dates, including a
    # mid-year change in 2022.
    assert table.sell_value_eur(date(2011, 4, 1)) == Decimal("0.45887")
    assert table.sell_value_eur(date(2022, 6, 30)) == Decimal("0.49241")
    assert table.sell_value_eur(date(2022, 7, 1)) == Decimal("0.51211")
    assert table.sell_value_eur(date(2026, 1, 1)) == Decimal("0.56053")

    # Documented gap: no official sell value before 2011.
    with pytest.raises(NoValueAvailableError):
        table.sell_value_eur(date(2010, 12, 31))
