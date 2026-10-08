## 1. Source and transcribe RCI data

- [x] 1.1 Research and record the exact official RCI source(s) for
      historical "revenu de référence" / "valeur d'achat du point"
      (acquisition cost) and "valeur de service du point" (sell value)
      figures, with effective dates — fetch primary sources (CNAV/
      Assurance Retraite circulars, `legislation.lassuranceretraite.fr`,
      `statistiques-recherche.lassuranceretraite.fr`), not just a web
      search summary — verify by listing the chosen URL(s)/PDF(s) and
      the earliest effective date each covers (expected: January 1st,
      2013, RCI's creation, but confirm rather than assume).
- [x] 1.2 Determine the actual row/effective-date structure (one row per
      calendar year with both columns changing together, like this
      design's default assumption, or independent per-column effective
      dates needing the split-row technique like `agirc_arrco.csv`/
      `ircantec.csv`) from what the sources in 1.1 actually publish —
      verify by stating which shape applies and why, citing the source.
- [x] 1.3 Create `src/fr_retraite_complementaire/data/funds/rci.csv` with
      columns `Starting from,Acquisition cost,Sell value,Currency`
      (`EUR` throughout per design.md), using the structure determined in
      1.2 — verify by loading the file with `load_fund("rci")` and
      confirming `table.earliest_date == date(2013, 1, 1)` (or the
      confirmed actual earliest date) and that both
      `acquisition_cost_eur` and `sell_value_eur` resolve without error
      on a known recent date (e.g. `date(2024, 1, 1)`).

## 2. Add the RCI fund identifier

- [x] 2.1 Add `RCI = "rci"` to the `Fund` enum in
      `src/fr_retraite_complementaire/enums.py` (alphabetically ordered
      among existing members) — verified
      `tests/test_enums.py::test_fund_enum_matches_packaged_csv_files`
      passes (enum/CSV in sync).
- [x] 2.2 Confirm `Fund.RCI` is usable wherever a fund identifier is
      accepted (`Career.add_points`, `load_fund`, CLI `list-funds`) with
      no further code changes — verified `fr-retraite-complementaire
      list-funds` lists `rci`, and `fr-retraite-complementaire compute`
      with a sample career CSV containing an `rci` row succeeds (100
      points at the 2024-01-01 rate = 132.70 EUR/year).

## 3. Research and transcribe RCO (artisans' legacy scheme)

- [x] 3.1 Pulled RCO's full historical series from primary sources:
      undifferentiated sell value 1980-2009 and acquisition cost
      1979-2012 from the IPP `baremes-ipp-yaml` repo's
      `parameters/retraites/independants/pt_rc_art.yaml` and
      `salref_rc_art.yaml` (each citing `legislation.cnav.fr`/`rsi.fr`
      barèmes); the three post-2009-differentiated buckets' 2009-2012
      values from the same `pt_rc_art.yaml`; their 2013-2022 values from
      `pt_rci.yaml`; their 2023/2024 values from CNAV/Assurance
      Retraite's "Fiche-stock Régime complémentaire TI" annual stats
      sheets (footnote citing the 1979-1996 and avant-1979 rates
      alongside the headline RCI rate, cross-checked year-by-year
      against `pt_rci.yaml`'s overlapping 2019-2022 values — exact
      match); their 2026 value from CNAV circulaire n°2025-31 (text
      extracted via `pdftotext`). 2025 is a one-year gap (no fiche-stock
      published for it yet) between confirmed 2024 and 2026 values.
      Earliest/latest per bucket: avant-1979 and 1979-1996 both
      1980-01-01–2026-01-01; 1997-2012 bucket 1997-01-01–2026-01-01
      (own acquisition window starts in 1997, inheriting the shared
      pre-2009 curve from its own start date).
- [x] 3.2 Decided: three `Fund` members, `rco_avant_1979`,
      `rco_1979_1996`, `rco_1997_2012` (matching the placeholders
      already used in `rco/spec.md`) — confirmed distinct via the 2026
      circular (1.158€ / 1.205€ / 1.347€ respectively, the last matching
      RCI's own rate exactly, confirming the "1997-2012 aligned" design
      decision). All three are sell-value-only: no acquisition-cost data
      is included for any of them, even though real historical
      acquisition-cost data exists for 1979-1996/1997-2012, because the
      `FundTable` step-function's blank-means-"unchanged" semantics have
      no way to mark the column closed once a scheme's acquisition
      window ends — including it would wrongly resolve to the frozen
      pre-closure rate for any later date. This matches `rco/spec.md`'s
      explicit "MAY raise not-available" allowance.
- [x] 3.3 Created `rco_avant_1979.csv`, `rco_1979_1996.csv`,
      `rco_1997_2012.csv` — verified each loads via `load_fund(...)` and
      resolves `sell_value_eur` without error at 2015-01-01, 2020-01-01,
      2024-01-01, and 2026-06-01 (values: 1.107/1.124/1.177;
      1.116/1.138/1.203; 1.153/1.196/1.327; 1.158/1.205/1.347
      respectively), and that `acquisition_cost_eur` raises
      `NoValueAvailableError` for all three at every tested date.

## 4. Research and transcribe NRCO (commerçants' legacy scheme)

- [x] 4.1 Pulled NRCO's sell-value series 2004-2012 from the IPP
      `baremes-ipp-yaml` repo's `pt_rc_com.yaml` (citing
      `legislation.cnav.fr`/`rsi.fr`/`capital.fr`); 2013 onward reuses
      the RCI/"NRCO et points RCO acquis à compter de 1997" rate
      (confirmed identical to `rco_1997_2012`'s own post-2013 series and
      to `rci.csv`'s own rate, per the circular's single shared 1.347€
      2026 line for both). Earliest/latest: 2004-01-01–2026-01-01.
      Acquisition cost intentionally not modeled (see 4.1's revised task
      text / `nrco/spec.md`'s "MAY raise not-available" requirement).
      Also found, and deliberately did **not** model separately: IPP's
      data tracks an eighth sub-category, "Commerçants, RC (1973-2004)"
      (a commerçants'-own pre-NRCO predecessor scheme, unrelated to the
      circular's "Point RC" conjoints/spouses scheme despite the shared
      abbreviation) — its value is numerically identical to NRCO's at
      every date both exist (2013-2019) and it isn't tracked at all in
      the current CNAV circular, so no separate `Fund` was created for
      it.
- [x] 4.2 Created `src/fr_retraite_complementaire/data/funds/nrco.csv`
      and added `Fund.NRCO` — verified it loads and resolves
      `sell_value_eur` without error at 2015-01-01 (1.177), 2020-01-01
      (1.203), and 2024-01-01 (1.327), and that `acquisition_cost_eur`
      raises `NoValueAvailableError` at every tested date.

## 5. Research and transcribe RC-conjoints and CMP

- [x] 5.1 Searched independently for RC-conjoints' ("Point RC")
      historical series: no dedicated IPP `baremes-ipp-yaml` file exists
      for it (checked the full repo tree for "conjoint"/"rc_com"/
      "rc_art"-named files — only RCO/NRCO's own files turned up), and
      direct `legislation.lassuranceretraite.fr`/`legislation.cnav.fr`
      barème-page fetches 404/failed (likely requiring interactive
      navigation this tooling can't reach). Only the current CNAV
      circulaire n°2025-31 value (1.347€ at 2026-01-01) could be
      confirmed from a primary source — documenting this as a known
      limitation rather than guessing an earlier series.
- [x] 5.2 Same search applied to CMP ("compte minimum de points"): same
      result — only the 2026-01-01 circular value (1.347€) confirmed.
- [x] 5.3 Created `rc_conjoints.csv`/`cmp.csv`, each a single row
      (`1/1/2026,,1.347,EUR`), and added `Fund.RC_CONJOINTS` /
      `Fund.CMP` — verified both load and resolve `sell_value_eur`
      without error at 2026-06-01 (1.347), and raise
      `NoValueAvailableError` for any earlier date (e.g. 2024-01-01),
      consistent with having no confirmed data before 2026.

## 6. Research RCEBTP (conditional)

- [x] 6.1 Researched RCEBTP: no IPP `baremes-ipp-yaml` file exists for
      it (checked the full repo tree); confirmed via
      `lassuranceretraite.fr`'s own 2022 announcement that RCEBTP closed
      to new contributions in 1998 and its remaining points were
      migrated/converted into RCI points on 2023-01-01 ("droits ...
      migrés et convertis en points RCI"); found exactly one historical
      point-value table, on a commercial financial-planning vendor's
      site (Harvest's "Patrithèque", `simulateurs-big.harvest.fr`), not
      an official CNAV/government source — and even that table only
      covers 1980-1998 (FRF), missing 1999-2022 entirely and giving no
      RCEBTP→RCI point-conversion coefficient. This doesn't meet the
      "citable, official" bar — treating this as "no usable source
      found", same as if nothing had turned up.
- [x] 6.2 Did **not** create `Fund.RCEBTP` (6.1 found no official,
      sufficiently complete source) — added a README "Known
      limitations" note instead, describing the 1998 closure, the 2023
      RCEBTP→RCI point migration/conversion, and that no pre-migration
      table is bundled — verified by re-reading that section.

## 7. Update the info-retraite.fr importer

- [x] 7.1 Added `"RCI": Fund.RCI` to `FUND_LABELS` in
      `src/fr_retraite_complementaire/importers/info_retraite.py` —
      verified by adding an `"RCI : 16 points"` row to
      `tests/data/info-retraite-sample.csv` (2016) and asserting (in
      `test_loads_sample_export_warn_policy`) the resulting `Career`
      has `Decimal(16)` points under `Fund.RCI` with no corresponding
      `ImportResult.skipped` entry.
- [x] 7.2 No real or documented www.info-retraite.fr export containing
      a distinct RCO/NRCO/RC-conjoints/CMP/RCEBTP label was found (only
      the format's general shape and an `"RCI : N points"` example from
      a prior session's own export were available) — did **not** add
      speculative `FUND_LABELS` entries for them, since a wrong guess
      would silently mis-map real import data. The test fixture now uses
      `"RCO"` as its representative still-unsupported-scheme example
      (replacing the now-supported `"RCI"`).
- [x] 7.3 Updated the module docstring: RCI is now listed as supported
      (`Fund.RCI`); the unsupported-example callout now names
      RCO/NRCO/RC-conjoints/CMP/RCEBTP instead, with the 7.2 rationale
      (no confirmed label string) — verified by re-reading the
      docstring; `cli.py`'s help text does not name specific funds, so
      needed no change.

## 8. Update tests

- [x] 8.1 Updated the fund-count assertion in `tests/test_data_loader.py`
      to 60 (added explicit `"rci"`/`"nrco"` membership checks too) —
      verified `uv run pytest tests/test_data_loader.py -q` passes.
- [x] 8.2 Updated `tests/test_importers.py` and the synthetic fixture
      `tests/data/info-retraite-sample.csv` per 7.2's findings: added an
      `"RCI : 16 points"` row (now supported, matches the module
      docstring's own example value) and renamed the still-unsupported
      example rows from `"RCI"` to `"RCO"` — verified
      `uv run pytest tests/test_importers.py -q` passes.
- [x] 8.3 Updated `tests/test_cli.py`'s `"RCI" in captured.err` assertion
      to `"RCO"` (same fixture rename as 8.2) — verified
      `uv run pytest tests/test_cli.py -q` passes.
- [x] 8.4 Added one focused load/lookup test per new fund
      (`test_rci_...`, `test_rco_*_...`, `test_nrco_...`,
      `test_rc_conjoints_and_cmp_...`) to `tests/test_data_loader.py`,
      each asserting a known effective date resolves to its published
      sell value in EUR and that `acquisition_cost_eur`/an earlier date
      raises `NoValueAvailableError` — verified
      `uv run pytest tests/test_data_loader.py -q` passes.

## 9. Update documentation

- [x] 9.1 Added a README "Files" bullet per new CSV (`rci.csv`,
      `rco_avant_1979.csv`/`rco_1979_1996.csv`/`rco_1997_2012.csv`,
      `nrco.csv`, `rc_conjoints.csv`/`cmp.csv`), each citing its source
      and covered date range, plus "Known limitations" notes for the
      sell-value-only funds and the single-data-point funds — verified
      by re-reading the rendered section for consistency with the
      existing bullets.
- [x] 9.2 Updated the "Importing a www.info-retraite.fr export" section
      per 7.2's findings: RCI is now listed as supported, and the five
      unmapped legacy schemes (RCO/NRCO/RC-conjoints/CMP/RCEBTP) are
      named with the rationale for not guessing their label strings —
      verified by re-reading that section.

## 10. Full verification

- [x] 10.1 Ran `uv run pytest -q`: 42 passed.
- [x] 10.2 Ran `uv run ruff check src tests` and `uv run ruff format
       --check src tests`: both clean ("All checks passed!", 17 files
       already formatted).
- [x] 10.3 Ran `uv build` and confirmed via `unzip -l` on the built
       wheel that all 60 fund CSVs (including `rci.csv`,
       `rco_avant_1979.csv`, `rco_1979_1996.csv`, `rco_1997_2012.csv`,
       `nrco.csv`, `rc_conjoints.csv`, `cmp.csv`) are packaged.
