"""The Career ledger: records point acquisitions and computes annuities."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .data_loader import list_funds, load_fund
from .models import FundTable, NoValueAvailableError


@dataclass(frozen=True, slots=True)
class PointAcquisition:
    """A single recorded acquisition of points in a fund.

    :param fund: fund identifier (see :func:`fr_retraite_complementaire.list_funds`).
    :param date: the date the points were credited.
    :param points: the number of points acquired (fund "tokens").
    """

    fund: str
    date: date
    points: Decimal


class UnknownFundError(ValueError):
    """Raised when points are recorded against an unrecognized fund."""


class FundBreakdownEntry:
    """Per-fund contribution to a computed annuity."""

    __slots__ = ("annual_amount_eur", "fund", "point_value_eur", "points")

    def __init__(
        self,
        fund: str,
        points: Decimal,
        point_value_eur: Decimal,
        annual_amount_eur: Decimal,
    ):
        self.fund = fund
        self.points = points
        self.point_value_eur = point_value_eur
        self.annual_amount_eur = annual_amount_eur

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return (
            f"FundBreakdownEntry(fund={self.fund!r}, points={self.points}, "
            f"point_value_eur={self.point_value_eur}, "
            f"annual_amount_eur={self.annual_amount_eur})"
        )


class Career:
    """A ledger of points acquired across one or more funds over a career.

    Example::

        from datetime import date
        from fr_retraite_complementaire import Career

        career = Career()
        career.add_points(fund="agirc", date=date(1995, 6, 1), points=120.5)
        career.add_points(fund="arrco", date=date(1995, 6, 1), points=80)
        career.add_points(fund="agrr", date=date(1980, 1, 1), points=15)

        annual_pension_eur = career.annuity(as_of=date(2025, 1, 1))
    """

    def __init__(self):
        self._acquisitions: list[PointAcquisition] = []
        self._fund_cache: dict[str, FundTable] = {}

    def _resolve_fund(self, fund: str) -> FundTable:
        table = self._fund_cache.get(fund)
        if table is None:
            try:
                table = load_fund(fund)
            except FileNotFoundError as exc:
                raise UnknownFundError(
                    f"Unknown fund {fund!r}. Available funds: {', '.join(list_funds())}"
                ) from exc
            self._fund_cache[fund] = table
        return table

    def add_points(self, fund: str, date: date, points: Decimal | float | str) -> None:
        """Record an acquisition of ``points`` in ``fund`` on ``date``.

        :raises UnknownFundError: if ``fund`` is not a recognized fund
            identifier.
        """
        self._resolve_fund(fund)  # validates the fund exists, eagerly
        self._acquisitions.append(
            PointAcquisition(fund=fund, date=date, points=Decimal(str(points)))
        )

    @property
    def acquisitions(self) -> list[PointAcquisition]:
        return list(self._acquisitions)

    def total_points(self, fund: str | None = None) -> Decimal:
        """Total points acquired, optionally restricted to a single fund."""
        return sum(
            (a.points for a in self._acquisitions if fund is None or a.fund == fund),
            start=Decimal(0),
        )

    def funds(self) -> set[str]:
        """The set of fund identifiers with at least one recorded acquisition."""
        return {a.fund for a in self._acquisitions}

    def breakdown(self, as_of: date) -> list[FundBreakdownEntry]:
        """Per-fund breakdown of the annuity computed as of ``as_of``.

        For each fund with recorded points, the fund's point sell value
        in effect on ``as_of`` (converted to EUR, carried forward from
        the fund's last known value) is multiplied by the total points
        held in that fund.

        :raises NoValueAvailableError: if ``as_of`` precedes the earliest
            known data for a fund the career holds points in.
        """
        totals: dict[str, Decimal] = defaultdict(lambda: Decimal(0))
        for acquisition in self._acquisitions:
            totals[acquisition.fund] += acquisition.points

        result = []
        for fund, points in sorted(totals.items()):
            table = self._resolve_fund(fund)
            point_value_eur = table.sell_value_eur(as_of)
            result.append(
                FundBreakdownEntry(
                    fund=fund,
                    points=points,
                    point_value_eur=point_value_eur,
                    annual_amount_eur=points * point_value_eur,
                )
            )
        return result

    def annuity(self, as_of: date) -> Decimal:
        """The total yearly pension annuity (in EUR) as of ``as_of``.

        Computed as the sum, over every fund the career holds points in,
        of ``total points in that fund x the fund's point sell value in
        effect on as_of`` (converted to EUR).

        :raises NoValueAvailableError: if ``as_of`` precedes the earliest
            known data for a fund the career holds points in.
        """
        return sum(
            (entry.annual_amount_eur for entry in self.breakdown(as_of)),
            start=Decimal(0),
        )


__all__ = [
    "Career",
    "FundBreakdownEntry",
    "NoValueAvailableError",
    "PointAcquisition",
    "UnknownFundError",
]
