"""Guards against the static Fund enum drifting from the packaged CSVs."""

from __future__ import annotations

from fr_retraite_complementaire.data_loader import list_funds
from fr_retraite_complementaire.enums import Currency, Fund


def test_fund_enum_matches_packaged_csv_files():
    enum_values = {member.value for member in Fund}
    csv_identifiers = set(list_funds())

    missing_from_enum = csv_identifiers - enum_values
    missing_csv_file = enum_values - csv_identifiers

    assert not missing_from_enum, (
        f"These CSV files have no corresponding Fund enum member: {sorted(missing_from_enum)}"
    )
    assert not missing_csv_file, (
        f"These Fund enum members have no corresponding CSV file: {sorted(missing_csv_file)}"
    )


def test_fund_enum_has_no_duplicate_values():
    values = [member.value for member in Fund]
    assert len(values) == len(set(values))


def test_fund_str_returns_raw_identifier():
    assert str(Fund.AGIRC) == "agirc"
    assert Fund.CAISSE_GUTENBERG.value == "caisse-gutenberg"


def test_fund_equals_plain_string():
    assert Fund.AGIRC == "agirc"
    assert Fund("agirc") is Fund.AGIRC


def test_currency_str_returns_raw_value():
    assert str(Currency.FRF_ANCIEN) == "FRF (ancien)"
    assert Currency("FRF (ancien)") is Currency.FRF_ANCIEN
