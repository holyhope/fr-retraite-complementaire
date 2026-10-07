"""Data model for a single fund's historical point-value table."""

from __future__ import annotations

import bisect
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .currency import to_eur


class NoValueAvailableError(LookupError):
    """Raised when a fund has no known point value on or before a date."""


@dataclass(frozen=True, slots=True)
class FundEntry:
    """One row of a fund's historical table.

    :param starting_from: date from which this row's values are in effect.
    :param acquisition_cost: "salaire de reference" - the cost to acquire
        one point, in the row's original currency. ``None`` when not
        published for this row (e.g. unchanged, or not yet published).
    :param sell_value: "valeur de service du point" - the value of one
        point when paid out as a pension, in the row's original currency.
        ``None`` when not available (e.g. not yet published).
    :param currency: one of ``"EUR"``, ``"FRF"``, ``"FRF (ancien)"``.
    """

    starting_from: date
    acquisition_cost: Decimal | None
    sell_value: Decimal | None
    currency: str

    @property
    def sell_value_eur(self) -> Decimal | None:
        if self.sell_value is None:
            return None
        return to_eur(self.sell_value, self.currency)

    @property
    def acquisition_cost_eur(self) -> Decimal | None:
        if self.acquisition_cost is None:
            return None
        return to_eur(self.acquisition_cost, self.currency)


class FundTable:
    """Historical point-value table for a single fund.

    Entries are a step function over time: each entry's values stay in
    effect from its ``starting_from`` date until the next entry's date.
    """

    def __init__(self, name: str, entries: list[FundEntry]):
        self.name = name
        self._entries = sorted(entries, key=lambda e: e.starting_from)
        self._dates = [e.starting_from for e in self._entries]

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"FundTable(name={self.name!r}, entries={len(self._entries)})"

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def entries(self) -> list[FundEntry]:
        return list(self._entries)

    @property
    def earliest_date(self) -> date | None:
        return self._dates[0] if self._dates else None

    @property
    def latest_date(self) -> date | None:
        return self._dates[-1] if self._dates else None

    def _entry_at_or_before(self, as_of: date) -> FundEntry | None:
        idx = bisect.bisect_right(self._dates, as_of) - 1
        if idx < 0:
            return None
        return self._entries[idx]

    def sell_value_eur(self, as_of: date) -> Decimal:
        """Return the point's sell value (in EUR) in effect on ``as_of``.

        Walks backward from ``as_of`` until an entry with a known sell
        value is found (some rows only record a change in acquisition
        cost and leave the sell value blank because it did not change,
        and a few recent rows are blank because the value is not yet
        published).

        :raises NoValueAvailableError: if ``as_of`` precedes the fund's
            earliest known entry, or no entry at/before ``as_of`` carries
            a sell value.
        """
        idx = bisect.bisect_right(self._dates, as_of) - 1
        if idx < 0:
            raise NoValueAvailableError(
                f"Fund {self.name!r} has no data on or before {as_of} "
                f"(earliest known date is {self.earliest_date})"
            )
        for i in range(idx, -1, -1):
            value = self._entries[i].sell_value_eur
            if value is not None:
                return value
        raise NoValueAvailableError(
            f"Fund {self.name!r} has no known sell value on or before {as_of}"
        )

    def acquisition_cost_eur(self, as_of: date) -> Decimal:
        """Return the point's acquisition cost (in EUR) in effect on ``as_of``.

        Same backward-fill behavior as :meth:`sell_value_eur`.
        """
        idx = bisect.bisect_right(self._dates, as_of) - 1
        if idx < 0:
            raise NoValueAvailableError(
                f"Fund {self.name!r} has no data on or before {as_of} "
                f"(earliest known date is {self.earliest_date})"
            )
        for i in range(idx, -1, -1):
            value = self._entries[i].acquisition_cost_eur
            if value is not None:
                return value
        raise NoValueAvailableError(
            f"Fund {self.name!r} has no known acquisition cost on or before {as_of}"
        )
