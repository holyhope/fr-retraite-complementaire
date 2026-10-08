## 1. Source and transcribe RCI data

- [ ] 1.1 Research and record the exact official RCI source(s) for
      historical "revenu de référence" / "valeur d'achat du point"
      (acquisition cost) and "valeur de service du point" (sell value)
      figures, with effective dates — fetch primary sources (CNAV/
      Assurance Retraite circulars, `legislation.lassuranceretraite.fr`,
      `statistiques-recherche.lassuranceretraite.fr`), not just a web
      search summary — verify by listing the chosen URL(s)/PDF(s) and
      the earliest effective date each covers (expected: January 1st,
      2013, RCI's creation, but confirm rather than assume).
- [ ] 1.2 Determine the actual row/effective-date structure (one row per
      calendar year with both columns changing together, like this
      design's default assumption, or independent per-column effective
      dates needing the split-row technique like `agirc_arrco.csv`/
      `ircantec.csv`) from what the sources in 1.1 actually publish —
      verify by stating which shape applies and why, citing the source.
- [ ] 1.3 Create `src/fr_retraite_complementaire/data/funds/rci.csv` with
      columns `Starting from,Acquisition cost,Sell value,Currency`
      (`EUR` throughout per design.md), using the structure determined in
      1.2 — verify by loading the file with `load_fund("rci")` and
      confirming `table.earliest_date == date(2013, 1, 1)` (or the
      confirmed actual earliest date) and that both
      `acquisition_cost_eur` and `sell_value_eur` resolve without error
      on a known recent date (e.g. `date(2024, 1, 1)`).

## 2. Research RCO/NRCO (predecessor schemes) — report only, no implementation

- [ ] 2.1 Research whether an official, citable historical point-value
      table exists for RCO (artisans, pre-2013) and/or NRCO (commerçants,
      pre-2013) — verify by stating, for each scheme, either a citable
      source and the date range it covers, or that no such table was
      found (and where this was checked).
- [ ] 2.2 Per `design.md`'s Non-Goals, do **not** create `rco.csv`,
      `nrco.csv`, `Fund.RCO`, or `Fund.NRCO` in this change even if 2.1
      finds a citable table. Stop and report the finding to the user
      (source(s), date range, data shape) and let them decide whether to
      fold it into this change (updating `proposal.md`'s Capabilities,
      adding a `funds/rco`/`funds/nrco` delta spec, and extending this
      `tasks.md`) or file it as a separate follow-up change — verify by
      confirming no new fund files/enum members for RCO/NRCO exist in the
      working tree after this task, regardless of what 2.1 found.

## 3. Add the RCI fund identifier

- [ ] 3.1 Add `RCI = "rci"` to the `Fund` enum in
      `src/fr_retraite_complementaire/enums.py` (alphabetically ordered
      among existing members) — verify
      `tests/test_enums.py::test_fund_enum_matches_packaged_csv_files`
      passes (enum/CSV in sync).
- [ ] 3.2 Confirm `Fund.RCI` is usable wherever a fund identifier is
      accepted (`Career.add_points`, `load_fund`, CLI `list-funds`) with
      no further code changes — verify by running
      `fr-retraite-complementaire list-funds` and confirming `rci` is
      listed, and `fr-retraite-complementaire compute` with a sample
      career CSV containing an `rci` row succeeds.

## 4. Update the info-retraite.fr importer

- [ ] 4.1 Add `"RCI": Fund.RCI` to `FUND_LABELS` in
      `src/fr_retraite_complementaire/importers/info_retraite.py` —
      verify by importing a fixture export containing an `"RCI : N
      points"` row and asserting the resulting `Career` has those points
      under `Fund.RCI`, with no corresponding entry in
      `ImportResult.skipped`.
- [ ] 4.2 Update the module docstring and `FUND_LABELS` comment in
      `info_retraite.py` that currently list RCI as an example of an
      unsupported scheme — verify by re-reading the docstring and
      `cli.py`'s help text for remaining stale references.

## 5. Update tests

- [ ] 5.1 Update `tests/test_data_loader.py::test_list_funds_includes_known_funds`
      (and any other hardcoded fund-count assertion) to the new total —
      verify `uv run pytest tests/test_data_loader.py -q` passes.
- [ ] 5.2 Update `tests/test_importers.py` and the synthetic fixture
      `tests/data/info-retraite-sample.csv` so the suite covers a
      now-supported RCI row landing under `Fund.RCI`, while still
      covering at least one remaining unsupported scheme for the
      warn/skip/error-policy tests (introduce a synthetic placeholder
      unsupported scheme label if RCI was the fixture's only remaining
      unsupported example) — verify `uv run pytest tests/test_importers.py -q`
      passes.
- [ ] 5.3 Update `tests/test_cli.py` if it references RCI as unsupported
      or asserts on skipped-scheme warnings tied to the old fixture
      content — verify `uv run pytest tests/test_cli.py -q` passes.
- [ ] 5.4 Add a focused test for `rci.csv` loading/lookup (mirrors
      `test_ircantec_acquisition_cost_and_sell_value_split_rows` in
      spirit): assert a known effective date resolves to its published
      sell value and acquisition cost in EUR, and that a date before the
      fund's earliest entry raises `NoValueAvailableError` — verify the
      new test passes.

## 6. Update documentation

- [ ] 6.1 Add an `rci.csv` bullet to the README "Files" list under
      "Data", citing its own source (distinct from the Agirc-Arrco
      compilation PDF cited for the other files) and its covered date
      range — verify by reading the rendered section for consistency
      with the other file bullets (including `ircantec.csv`'s own
      bullet).
- [ ] 6.2 Update the "Importing a www.info-retraite.fr export" section
      to no longer list RCI as an example of an unsupported scheme
      (replace with a remaining real unsupported example if one exists,
      or state that all schemes seen in a typical export are now
      supported) — verify by re-reading that section.

## 7. Full verification

- [ ] 7.1 Run `uv run pytest -q` and confirm all tests pass.
- [ ] 7.2 Run `uv run ruff check src tests` and `uv run ruff format
      --check src tests` and confirm no issues.
- [ ] 7.3 Run `uv build` and confirm `rci.csv` is present inside the
      built wheel alongside the other packaged fund CSVs.
