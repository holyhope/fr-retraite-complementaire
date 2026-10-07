"""Command-line interface.

Usage::

    fr-retraite-complementaire compute --career career.csv --as-of 2025-01-01
    fr-retraite-complementaire compute --format info-retraite \\
        --career export.csv --as-of 2025-01-01
    fr-retraite-complementaire list-funds

Where ``career.csv`` (``--format career``, the default) has the columns
``fund,date,points``, e.g.::

    fund,date,points
    agirc,1995-06-01,120.5
    arrco,1995-06-01,80
    agrr,1980-01-01,15

``--format info-retraite`` instead reads a "Mes points retraite" export
from https://www.info-retraite.fr (the "synthese" page), as documented in
:mod:`fr_retraite_complementaire.importers.info_retraite`.
"""

from __future__ import annotations

import argparse
import csv
import sys
import warnings
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from .career import Career, UnknownFundError
from .enums import Fund
from .importers.info_retraite import (
    InfoRetraiteFormatError,
    UnsupportedFundInImportError,
    UnsupportedFundPolicy,
)
from .importers.info_retraite import load_career as load_info_retraite_career
from .models import NoValueAvailableError


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()  # noqa: DTZ007 (date-only, tz is irrelevant)


def _load_career_csv(path: Path) -> Career:
    career = Career()
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for lineno, row in enumerate(reader, start=2):
            try:
                career.add_points(
                    fund=row["fund"].strip(),
                    date=_parse_date(row["date"].strip()),
                    points=Decimal(row["points"].strip()),
                )
            except KeyError as exc:
                raise SystemExit(
                    f"{path}: missing column {exc} (expected: fund,date,points)"
                ) from exc
            except UnknownFundError as exc:
                raise SystemExit(f"{path}:{lineno}: {exc}") from exc
    return career


def _load_career_info_retraite(path: Path, on_unsupported: str) -> Career:
    policy = UnsupportedFundPolicy(on_unsupported)
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = load_info_retraite_career(path, on_unsupported=policy)
        for warning in caught:
            print(f"warning: {warning.message}", file=sys.stderr)
    except (InfoRetraiteFormatError, UnsupportedFundInImportError) as exc:
        raise SystemExit(f"{path}: {exc}") from exc

    if result.skipped and policy is UnsupportedFundPolicy.SKIP:
        skipped_funds = sorted({entry.label for entry in result.skipped})
        print(
            f"note: silently skipped {len(result.skipped)} points entry(ies) for "
            f"unsupported scheme(s): {', '.join(skipped_funds)}",
            file=sys.stderr,
        )
    return result.career


def _cmd_compute(args: argparse.Namespace) -> int:
    path = Path(args.career)
    if args.format == "info-retraite":
        career = _load_career_info_retraite(path, args.on_unsupported_fund)
    else:
        career = _load_career_csv(path)

    as_of = _parse_date(args.as_of)
    try:
        breakdown = career.breakdown(as_of)
    except NoValueAvailableError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    total = Decimal(0)
    for entry in breakdown:
        total += entry.annual_amount_eur
        print(
            f"{entry.fund:<32} "
            f"{entry.points:>12} pts  x  "
            f"{entry.point_value_eur:>14.6f} EUR/pt  =  "
            f"{entry.annual_amount_eur:>12.2f} EUR/year"
        )
    print("-" * 80)
    print(f"{'Total annual annuity':<32} {'':>12}  {'':>10}     {total:>12.2f} EUR/year")
    return 0


def _cmd_list_funds(_args: argparse.Namespace) -> int:
    for fund in sorted(Fund, key=lambda f: f.value):
        print(fund.value)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fr-retraite-complementaire")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compute = subparsers.add_parser(
        "compute", help="Compute the annual annuity for a career of recorded points."
    )
    compute.add_argument(
        "--career",
        required=True,
        help="Path to the input CSV file (shape depends on --format).",
    )
    compute.add_argument(
        "--format",
        choices=["career", "info-retraite"],
        default="career",
        help=(
            "Input shape: 'career' (fund,date,points, default) or "
            "'info-retraite' (a www.info-retraite.fr points export)."
        ),
    )
    compute.add_argument(
        "--on-unsupported-fund",
        choices=[policy.value for policy in UnsupportedFundPolicy],
        default=UnsupportedFundPolicy.WARN.value,
        help=(
            "Only used with --format info-retraite: how to handle schemes this "
            "package has no data for (e.g. Ircantec, RCI). Default: warn."
        ),
    )
    compute.add_argument(
        "--as-of",
        required=True,
        help="Date (YYYY-MM-DD) at which to value the annuity.",
    )
    compute.set_defaults(func=_cmd_compute)

    list_funds_cmd = subparsers.add_parser(
        "list-funds", help="List all available fund identifiers."
    )
    list_funds_cmd.set_defaults(func=_cmd_list_funds)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
