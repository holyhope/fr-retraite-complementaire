from datetime import date

from fr_retraite_complementaire.data_loader import list_funds, load_all_funds, load_fund


def test_list_funds_includes_known_funds():
    funds = list_funds()
    assert "agirc" in funds
    assert "arrco" in funds
    assert "agirc_arrco" in funds
    assert "agrr" in funds
    assert len(funds) == 52  # 3 unified tables + 49 affiliated funds


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
