## 1. Source and transcribe Ircantec data

- [x] 1.1 Research and record the exact official Ircantec source(s) for
      historical "salaire de référence" (acquisition cost) and "valeur
      de service du point" (sell value) figures, with effective dates —
      done: acquisition cost from `baseircantec.retraites.fr`'s
      "Evolution des taux théoriques et du salaire de référence
      Ircantec" (cross-checked across two editions dated 14/12/2023 and
      26/02/2026), covering 1947-2026; sell value from
      `ircantec.retraites.fr/retraite/valeur-point`, covering
      01/04/2011-01/01/2026. See design.md Context for the full
      findings (irregular pre-2019 effective dates, 1935-1946 and
      1971-2011 gaps).
- [x] 1.2 Create `src/fr_retraite_complementaire/data/funds/ircantec.csv`
      with columns `Starting from,Acquisition cost,Sell value,Currency`,
      using the split-row technique (one row per effective date per
      column, per design.md's revised Decisions) — verify by loading
      the file with `load_fund("ircantec")` and confirming
      `table.earliest_date == date(1947, 1, 1)`,
      `table.latest_date == date(2026, 1, 1)`,
      `table.acquisition_cost_eur(date(1947, 1, 1))` and
      `table.sell_value_eur(date(2011, 4, 1))` both resolve without
      error, and `table.sell_value_eur(date(2010, 1, 1))` raises
      `NoValueAvailableError` (documented sell-value gap).

## 2. Add the Ircantec fund identifier

- [x] 2.1 Add `IRCANTEC = "ircantec"` to the `Fund` enum in
      `src/fr_retraite_complementaire/enums.py` (alphabetically ordered
      among existing members) — verify
      `tests/test_enums.py::test_fund_enum_matches_packaged_csv_files`
      passes (enum/CSV in sync).
- [x] 2.2 Confirm `Fund.IRCANTEC` is usable wherever a fund identifier
      is accepted (`Career.add_points`, `load_fund`, CLI `list-funds`)
      with no further code changes — verify by running
      `fr-retraite-complementaire list-funds` and confirming `ircantec`
      is listed, and `fr-retraite-complementaire compute` with a sample
      career CSV containing an `ircantec` row succeeds.

## 3. Update the info-retraite.fr importer

- [x] 3.1 Add `"Ircantec": Fund.IRCANTEC` to `FUND_LABELS` in
      `src/fr_retraite_complementaire/importers/info_retraite.py` —
      verify by importing a fixture export containing an `"Ircantec : N
      points"` row and asserting the resulting `Career` has those
      points under `Fund.IRCANTEC`, with no corresponding entry in
      `ImportResult.skipped`.
- [x] 3.2 Update the module docstring and `FUND_LABELS` comment in
      `info_retraite.py` that currently list Ircantec as an example of
      an unsupported scheme — verify by re-reading the docstring for
      remaining stale references.

## 4. Update tests

- [x] 4.1 Update `tests/test_data_loader.py::test_list_funds_includes_known_funds`
      (and any other hardcoded fund-count assertion, e.g. "52 funds")
      to the new total — verify `uv run pytest tests/test_data_loader.py -q`
      passes.
- [x] 4.2 Update `tests/test_importers.py` and the synthetic fixture
      `tests/data/info-retraite-sample.csv` so the suite still covers
      both a now-supported scheme (Ircantec) and at least one remaining
      unsupported scheme (RCI): adjust
      `test_loads_sample_export_warn_policy`'s skipped-label assertions
      and point totals accordingly, and add a case asserting Ircantec
      points land under `Fund.IRCANTEC` — verify
      `uv run pytest tests/test_importers.py -q` passes.
- [x] 4.3 Update `tests/test_cli.py` if it references Ircantec as
      unsupported or asserts on skipped-scheme warnings tied to the old
      fixture content — verify `uv run pytest tests/test_cli.py -q`
      passes.
- [x] 4.4 Add a focused test for `ircantec.csv` loading/lookup (mirrors
      `test_agirc_arrco_acquisition_cost_changes_on_january_1st` in
      spirit): assert a known effective date resolves to its published
      sell value and acquisition cost in EUR — verify the new test
      passes.

## 5. Update documentation

- [x] 5.1 Add an `ircantec.csv` bullet to the README "Files" list under
      "Data", citing its own source (distinct from the Agirc-Arrco
      compilation PDF cited for the other 52 files) and its covered
      date range — verify by reading the rendered section for
      consistency with the other file bullets.
- [x] 5.2 Update the "Importing a www.info-retraite.fr export" section
      to no longer list Ircantec as an example of an unsupported scheme
      (keep RCI as the example) — verify by re-reading that section.

## 6. Full verification

- [x] 6.1 Run `uv run pytest -q` and confirm all tests pass.
- [x] 6.2 Run `uv run ruff check src tests` and `uv run ruff format
      --check src tests` and confirm no issues.
- [x] 6.3 Run `uv build` and confirm `ircantec.csv` is present inside
      the built wheel alongside the other packaged fund CSVs.
