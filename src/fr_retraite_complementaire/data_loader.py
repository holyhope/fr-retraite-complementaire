"""Loads the packaged fund CSV data into :class:`FundTable` objects."""

from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal
from functools import cache
from importlib import resources

from .models import FundEntry, FundTable

_DATA_PACKAGE = "fr_retraite_complementaire.data.funds"


def _parse_date(value: str):
    return datetime.strptime(value, "%m/%d/%Y").date()  # noqa: DTZ007 (date-only, tz is irrelevant)


def _parse_decimal(value: str) -> Decimal | None:
    value = value.strip()
    if not value:
        return None
    return Decimal(value)


@cache
def list_funds() -> tuple[str, ...]:
    """Return the sorted identifiers of all packaged funds.

    A fund identifier is the CSV file's stem, e.g. ``"agirc"``,
    ``"arrco"``, ``"agirc_arrco"``, ``"agrr"``, ``"caisse-gutenberg"``.
    """
    package_files = resources.files(_DATA_PACKAGE)
    names = [
        entry.name[: -len(".csv")]
        for entry in package_files.iterdir()
        if entry.name.endswith(".csv")
    ]
    return tuple(sorted(names))


@cache
def load_fund(name: str) -> FundTable:
    """Load a single fund's historical table by identifier.

    :param name: fund identifier, as returned by :func:`list_funds`.
    :raises FileNotFoundError: if no such fund is packaged.
    """
    resource = resources.files(_DATA_PACKAGE).joinpath(f"{name}.csv")
    if not resource.is_file():
        raise FileNotFoundError(
            f"Unknown fund {name!r}. Available funds: {', '.join(list_funds())}"
        )

    entries: list[FundEntry] = []
    with resource.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(
                FundEntry(
                    starting_from=_parse_date(row["Starting from"]),
                    acquisition_cost=_parse_decimal(row["Acquisition cost"]),
                    sell_value=_parse_decimal(row["Sell value"]),
                    currency=row["Currency"].strip(),
                )
            )
    return FundTable(name=name, entries=entries)


def load_all_funds() -> dict[str, FundTable]:
    """Load every packaged fund, keyed by identifier."""
    return {name: load_fund(name) for name in list_funds()}
