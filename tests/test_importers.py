from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from fr_retraite_complementaire.enums import Fund
from fr_retraite_complementaire.importers.info_retraite import (
    InfoRetraiteFormatError,
    UnsupportedFundInImportError,
    UnsupportedFundPolicy,
    load_career,
)

# A synthetic export mirroring the real www.info-retraite.fr format
# (multi-line quoted cell, CRLF rows, comma decimals, singular "point",
# unsupported Ircantec/RCI schemes). A *real* export is personal data
# and is never committed; see tests/data/info-retraite.csv in .gitignore.
FIXTURE = Path(__file__).parent / "data" / "info-retraite-sample.csv"


def test_loads_sample_export_warn_policy():
    with pytest.warns(UserWarning, match="RCI"):
        result = load_career(FIXTURE)

    assert result.career.funds() == {Fund.AGIRC_ARRCO}
    assert result.career.total_points() == Decimal("66.75")
    # RCI (2013) + Ircantec (2014) + RCI (2014)
    assert len(result.skipped) == 3
    assert {entry.label for entry in result.skipped} == {"RCI", "Ircantec"}


def test_skip_policy_emits_no_warning(recwarn):
    result = load_career(FIXTURE, on_unsupported=UnsupportedFundPolicy.SKIP)
    assert len(recwarn) == 0
    assert len(result.skipped) == 3


def test_error_policy_raises():
    with pytest.raises(UnsupportedFundInImportError, match="RCI"):
        load_career(FIXTURE, on_unsupported="error")


def test_single_point_singular_wording_parses(tmp_path: Path):
    path = tmp_path / "export.csv"
    path.write_text(
        "Annee;Duree d'assurance tous regimes;Duree par regime;Points par regime;;;\n"
        "2013;0 trimestre;L'Assurance retraite : 0 trimestre;Agirc-Arrco : 1,28 point;;;\n",
        encoding="utf-8",
    )
    result = load_career(path, on_unsupported="error")
    assert result.career.total_points() == Decimal("1.28")


def test_malformed_points_line_raises(tmp_path: Path):
    path = tmp_path / "export.csv"
    path.write_text(
        "Annee;Duree d'assurance tous regimes;Duree par regime;Points par regime;;;\n"
        "2013;0 trimestre;L'Assurance retraite : 0 trimestre;garbage;;;\n",
        encoding="utf-8",
    )
    with pytest.raises(InfoRetraiteFormatError):
        load_career(path)


def test_missing_points_column_raises(tmp_path: Path):
    path = tmp_path / "export.csv"
    path.write_text("Annee;Duree d'assurance tous regimes\n2013;0 trimestre\n", encoding="utf-8")
    with pytest.raises(InfoRetraiteFormatError):
        load_career(path)
