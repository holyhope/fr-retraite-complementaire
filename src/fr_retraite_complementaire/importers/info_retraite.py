"""Import a points-history export from https://www.info-retraite.fr.

The "Mes points retraite complementaire" export (reachable from the
"synthese" page, e.g. ``https://affcar.info-retraite.fr/#/synthese``) is
a semicolon-delimited CSV, one row per year, shaped like::

    Annee;Duree d'assurance tous regimes;Duree par regime;Points par regime;;;
    2018;4 trimestres;L'Assurance retraite : 4 trimestres;Agirc-Arrco : 163,05 points;;;
    2016;4 trimestres;L'Assurance retraite : 4 trimestres ;"Agirc-Arrco : 61,51 points
    Ircantec : 45 points
    RCI : 16 points";;;

Notes on the format:

- Decimal numbers use a French comma (``16,02`` not ``16.02``).
- The singular "point" is used for a value of exactly 1 (or 0); the
  plural "points" otherwise.
- The "Points par regime" cell can hold multiple lines, one per
  complementary scheme the person accrued points in that year.
- The "Duree ... L'Assurance retraite" columns describe the *base*
  state pension (in trimestres, quarters) and are unrelated to points;
  they are ignored by this importer.

Only funds this package has data for can be converted into a
:class:`~fr_retraite_complementaire.career.Career`. As of this writing,
that is the merged **Agirc-Arrco** scheme (``Fund.AGIRC_ARRCO``),
**Ircantec** (``Fund.IRCANTEC``, public-sector non-permanent staff),
and **RCI** (``Fund.RCI``, self-employed workers). Other complementary
schemes that may appear in an info-retraite.fr export -- such as RCI's
pre-2013 predecessor schemes (RCO, NRCO, RC-conjoints, CMP, RCEBTP) --
are not mapped here: no sample export containing a distinct label for
any of them was available to confirm the exact label string(s)
info-retraite.fr would use, so guessing one risks a silent
mis-mapping. Rows for those (and any other unmapped) schemes are
handled per ``on_unsupported`` (see :func:`load_career`).
"""

from __future__ import annotations

import csv
import re
import warnings
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from pathlib import Path

from ..career import Career
from ..enums import Fund

_POINTS_LINE_RE = re.compile(r"^(?P<label>.+?)\s*:\s*(?P<value>[\d,]+)\s*points?\s*$")

#: Maps an info-retraite.fr scheme label to the :class:`Fund` this
#: package has historical data for. Labels not present here (e.g.
#: ``"RCI"``) are entirely different pension schemes this package does
#: not bundle data for.
FUND_LABELS: dict[str, Fund] = {
    "Agirc-Arrco": Fund.AGIRC_ARRCO,
    "Ircantec": Fund.IRCANTEC,
    "RCI": Fund.RCI,
}


class UnsupportedFundPolicy(str, Enum):
    """What to do with a points line for a scheme this package has no data for."""

    #: Skip the entry and emit a :class:`UserWarning`.
    WARN = "warn"
    #: Silently skip the entry.
    SKIP = "skip"
    #: Raise :class:`UnsupportedFundInImportError`.
    ERROR = "error"

    def __str__(self) -> str:
        return str(self.value)


class UnsupportedFundInImportError(ValueError):
    """Raised when a row references a scheme this package has no data for."""


class InfoRetraiteFormatError(ValueError):
    """Raised when the CSV does not match the expected info-retraite.fr export shape."""


@dataclass(frozen=True, slots=True)
class SkippedEntry:
    """A points line that could not be converted (unsupported scheme)."""

    year: int
    label: str
    points: Decimal


@dataclass(frozen=True, slots=True)
class ImportResult:
    """Result of importing an info-retraite.fr export.

    :param career: a :class:`Career` populated with every points line
        for a supported fund.
    :param skipped: points lines for schemes this package has no data
        for (e.g. Ircantec, RCI), left out of ``career``.
    """

    career: Career
    skipped: list[SkippedEntry]


def _parse_points_cell(cell: str, year: int) -> list[tuple[str, Decimal]]:
    entries = []
    for raw_line in cell.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = _POINTS_LINE_RE.match(line)
        if match is None:
            raise InfoRetraiteFormatError(f"year {year}: could not parse points line {raw_line!r}")
        label = match.group("label").strip()
        value = Decimal(match.group("value").replace(",", "."))
        entries.append((label, value))
    return entries


def load_career(
    path: str | Path,
    *,
    on_unsupported: UnsupportedFundPolicy | str = UnsupportedFundPolicy.WARN,
) -> ImportResult:
    """Parse an info-retraite.fr points-history CSV export into a :class:`Career`.

    :param path: path to the exported CSV file.
    :param on_unsupported: what to do when a row references a scheme
        this package has no data for (``"warn"`` (default), ``"skip"``,
        or ``"error"``).
    :raises UnsupportedFundInImportError: if ``on_unsupported="error"``
        and an unsupported scheme is encountered.
    :raises InfoRetraiteFormatError: if the file does not match the
        expected export shape.
    """
    policy = (
        on_unsupported
        if isinstance(on_unsupported, UnsupportedFundPolicy)
        else UnsupportedFundPolicy(on_unsupported)
    )

    career = Career()
    skipped: list[SkippedEntry] = []

    path = Path(path)
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        try:
            header = next(reader)
        except StopIteration as exc:
            raise InfoRetraiteFormatError(f"{path}: file is empty") from exc

        try:
            points_col = next(
                i for i, name in enumerate(header) if name.strip().startswith("Points par")
            )
        except StopIteration as exc:
            raise InfoRetraiteFormatError(
                f"{path}: expected a 'Points par regime' column, got header {header!r}"
            ) from exc

        for row in reader:
            if not row or not row[0].strip():
                continue
            try:
                year = int(row[0].strip())
            except ValueError as exc:
                raise InfoRetraiteFormatError(
                    f"{path}: expected a year in the first column, got {row[0]!r}"
                ) from exc

            cell = row[points_col] if len(row) > points_col else ""
            for label, points in _parse_points_cell(cell, year):
                fund = FUND_LABELS.get(label)
                if fund is None:
                    entry = SkippedEntry(year=year, label=label, points=points)
                    skipped.append(entry)
                    if policy is UnsupportedFundPolicy.ERROR:
                        raise UnsupportedFundInImportError(
                            f"year {year}: no data for scheme {label!r} "
                            f"(supported: {', '.join(FUND_LABELS)})"
                        )
                    if policy is UnsupportedFundPolicy.WARN:
                        warnings.warn(
                            f"{path}: year {year}: skipping {points} point(s) in "
                            f"unsupported scheme {label!r} "
                            f"(supported: {', '.join(FUND_LABELS)})",
                            stacklevel=2,
                        )
                    continue

                # The export only reports a yearly total, not the exact
                # acquisition date; Career.annuity()/breakdown() only use
                # the *total* points per fund, so the nominal date below
                # does not affect any computation.
                career.add_points(fund=fund, date=date(year, 1, 1), points=points)

    return ImportResult(career=career, skipped=skipped)


__all__ = [
    "FUND_LABELS",
    "ImportResult",
    "InfoRetraiteFormatError",
    "SkippedEntry",
    "UnsupportedFundInImportError",
    "UnsupportedFundPolicy",
    "load_career",
]
