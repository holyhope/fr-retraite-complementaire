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

- [ ] 3.1 Pull RCO's full historical series for each of its three
      permanently-distinct post-2009 era buckets (pre-1979
      "reconstitution de carrière", 1979-1996, 1997-2012-aligned) plus
      its pre-2009 undifferentiated acquisition-cost series
      (`salref_rc_art.yaml`-equivalent primary source), from 1979/2009
      through 2026 — verify by listing each bucket's earliest/latest
      confirmed effective date and citing the source for each.
- [ ] 3.2 Decide and record the final `Fund` member breakdown for RCO
      (how many members, their names/slugs) based on what 3.1 found —
      verify by stating the decision and why, updating this task list
      with the resulting file/enum-member names if they differ from the
      placeholders used below.
- [ ] 3.3 Create `rco_<bucket>.csv` file(s) for each `Fund` member
      decided in 3.2 (sell-value-only for the three differentiated
      buckets per design.md; include the pre-2009 undifferentiated
      acquisition-cost series on whichever bucket inherited it, or as
      its own fund if 3.2 decided that) — verify each loads via
      `load_fund(...)` and resolves a known date without error.

## 4. Research and transcribe NRCO (commerçants' legacy scheme)

- [ ] 4.1 Pull NRCO's full historical series (acquisition cost and sell
      value, 2004-2012, "aligned" with RCI from 2013 onward per
      design.md) — verify by citing the source and earliest/latest
      effective dates.
- [ ] 4.2 Create `src/fr_retraite_complementaire/data/funds/nrco.csv`
      and add `Fund.NRCO` — verify it loads and resolves without error
      on a known pre- and post-2013 date.

## 5. Research and transcribe RC-conjoints and CMP

- [ ] 5.1 Pull RC-conjoints' ("Point RC") full historical series
      independently (not assumed to mirror NRCO/RCI) — verify by citing
      the source and earliest/latest effective dates, or stating that
      only the current (2026) value could be confirmed and documenting
      that limitation.
- [ ] 5.2 Pull CMP's ("compte minimum de points") full historical series
      independently — same verification as 5.1.
- [ ] 5.3 Create `rc_conjoints.csv`/`cmp.csv` and add `Fund.RC_CONJOINTS`
      / `Fund.CMP` — verify both load and resolve without error on a
      known date.

## 6. Research RCEBTP (conditional)

- [ ] 6.1 Research whether a citable, official pre-2023 historical
      point-value table exists for RCEBTP — verify by stating either a
      source and date range, or that none was found (and where this was
      checked).
- [ ] 6.2 If 6.1 found a source: create `rcebtp.csv` and add
      `Fund.RCEBTP`, verified the same way as the other funds. If not:
      do **not** create a fund for it — instead add a README "Known
      limitations" note describing the 2023 RCEBTP→RCI migration and
      that no pre-migration table is bundled — verify by re-reading that
      section.

## 7. Update the info-retraite.fr importer

- [ ] 7.1 Add `"RCI": Fund.RCI` to `FUND_LABELS` in
      `src/fr_retraite_complementaire/importers/info_retraite.py` — NOT
      yet done (checked during an `/opsx-continue` coherence pass:
      `FUND_LABELS` still only has `Agirc-Arrco`/`Ircantec`) — verify by
      inspecting `FUND_LABELS` and importing a fixture export containing
      an `"RCI : N points"` row, asserting the resulting `Career` has
      those points under `Fund.RCI` with no corresponding
      `ImportResult.skipped` entry.
- [ ] 7.2 Determine whether any of RCO/NRCO/RC-conjoints/CMP/RCEBTP ever
      appear as their own distinct labeled rows in a
      www.info-retraite.fr export (as opposed to always being bundled
      into the "RCI" line) — verify by inspecting a real or documented
      export format; add `FUND_LABELS` entries only for labels actually
      confirmed to appear.
- [ ] 7.3 Update the module docstring/comment that cited RCI as an
      unsupported scheme example — NOT yet done (still references RCI
      as unsupported as of this `/opsx-continue` pass) — verify by
      re-reading the docstring and `cli.py`'s help text for remaining
      stale references.

## 8. Update tests

- [ ] 8.1 Update fund-count assertions in `tests/test_data_loader.py` to
      the final total (after all new funds in sections 3-6 exist) —
      verify `uv run pytest tests/test_data_loader.py -q` passes.
- [ ] 8.2 Update `tests/test_importers.py` and the synthetic fixture
      `tests/data/info-retraite-sample.csv` per 7.2's findings (RCI row
      now supported; at least one remaining unsupported scheme still
      covered for the warn/skip/error-policy tests) — verify
      `uv run pytest tests/test_importers.py -q` passes.
- [ ] 8.3 Update `tests/test_cli.py` if it references RCI or any new
      fund as unsupported — verify `uv run pytest tests/test_cli.py -q`
      passes.
- [ ] 8.4 Add a focused load/lookup test per new fund (mirrors
      `test_ircantec_acquisition_cost_and_sell_value_split_rows`):
      assert a known effective date resolves to its published value(s)
      in EUR, and that a date before the fund's earliest entry raises
      `NoValueAvailableError` — verify each new test passes.

## 9. Update documentation

- [ ] 9.1 Add a README "Files" bullet per new CSV (RCI's own bullet
      already added), citing its source and covered date range —
      verify by reading the rendered section for consistency with the
      existing bullets.
- [ ] 9.2 Update the "Importing a www.info-retraite.fr export" section
      per 7.2's findings — verify by re-reading that section.

## 10. Full verification

- [ ] 10.1 Run `uv run pytest -q` and confirm all tests pass.
- [ ] 10.2 Run `uv run ruff check src tests` and `uv run ruff format
       --check src tests` and confirm no issues.
- [ ] 10.3 Run `uv build` and confirm every new fund's CSV is present
       inside the built wheel alongside the other packaged fund CSVs.
