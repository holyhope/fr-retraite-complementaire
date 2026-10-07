from pathlib import Path

import pytest

from fr_retraite_complementaire.cli import main

INFO_RETRAITE_FIXTURE = Path(__file__).parent / "data" / "info-retraite-sample.csv"


def test_list_funds(capsys):
    rc = main(["list-funds"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "agirc" in out
    assert "arrco" in out


def test_compute(tmp_career_csv: Path, capsys):
    rc = main(
        [
            "compute",
            "--career",
            str(tmp_career_csv),
            "--as-of",
            "2018-11-01",
        ]
    )
    out = capsys.readouterr().out
    assert rc == 0
    assert "agirc" in out
    assert "arrco" in out
    assert "Total annual annuity" in out


def test_compute_unknown_fund_exits(tmp_path: Path):
    path = tmp_path / "career.csv"
    path.write_text("fund,date,points\nnot-a-fund,1995-06-01,10\n")

    with pytest.raises(SystemExit):
        main(["compute", "--career", str(path), "--as-of", "2018-11-01"])


def test_compute_info_retraite_format_warns_and_computes(capsys):
    rc = main(
        [
            "compute",
            "--format",
            "info-retraite",
            "--career",
            str(INFO_RETRAITE_FIXTURE),
            "--as-of",
            "2025-01-01",
        ]
    )
    captured = capsys.readouterr()
    assert rc == 0
    assert "warning:" in captured.err
    assert "RCI" in captured.err
    assert "agirc_arrco" in captured.out
    assert "Total annual annuity" in captured.out


def test_compute_info_retraite_skip_policy_is_quiet(capsys):
    rc = main(
        [
            "compute",
            "--format",
            "info-retraite",
            "--career",
            str(INFO_RETRAITE_FIXTURE),
            "--as-of",
            "2025-01-01",
            "--on-unsupported-fund",
            "skip",
        ]
    )
    captured = capsys.readouterr()
    assert rc == 0
    assert "warning:" not in captured.err
    assert "note: silently skipped" in captured.err


def test_compute_info_retraite_error_policy_exits(capsys):
    with pytest.raises(SystemExit):
        main(
            [
                "compute",
                "--format",
                "info-retraite",
                "--career",
                str(INFO_RETRAITE_FIXTURE),
                "--as-of",
                "2025-01-01",
                "--on-unsupported-fund",
                "error",
            ]
        )
