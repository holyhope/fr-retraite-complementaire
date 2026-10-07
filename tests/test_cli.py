from pathlib import Path

from fr_retraite_complementaire.cli import main


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

    import pytest

    with pytest.raises(SystemExit):
        main(["compute", "--career", str(path), "--as-of", "2018-11-01"])
