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
# supported Agirc-Arrco/Ircantec/RCI rows, and an unsupported RCO
# scheme -- RCI's own pre-2013 predecessor, which this package has data
# for as its own Fund but which the importer does not map any label to,
# per tasks.md 7.2). A *real* export is personal data and is never
# committed; see tests/data/info-retraite.csv in .gitignore.
FIXTURE = Path(__file__).parent / "data" / "info-retraite-sample.csv"


def test_loads_sample_export_warn_policy():
    with pytest.warns(UserWarning, match="RCO"):
        result = load_career(FIXTURE)

    assert result.career.funds() == {Fund.AGIRC_ARRCO, Fund.IRCANTEC, Fund.RCI}
    assert result.career.total_points(Fund.AGIRC_ARRCO) == Decimal("66.75")
    assert result.career.total_points(Fund.IRCANTEC) == Decimal(8)
    assert result.career.total_points(Fund.RCI) == Decimal(16)
    # RCO (2013) + RCO (2014); RCI (2016) is now a supported fund.
    assert len(result.skipped) == 2
    assert {entry.label for entry in result.skipped} == {"RCO"}


def test_skip_policy_emits_no_warning(recwarn):
    result = load_career(FIXTURE, on_unsupported=UnsupportedFundPolicy.SKIP)
    assert len(recwarn) == 0
    assert len(result.skipped) == 2


def test_error_policy_raises():
    with pytest.raises(UnsupportedFundInImportError, match="RCO"):
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
