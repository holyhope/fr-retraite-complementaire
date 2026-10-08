## Context

See `proposal.md` - Why/What Changes for motivation and scope. This
package's existing fund-data architecture (per `README.md` "Data"
section and `src/fr_retraite_complementaire/models.py`,
`data_loader.py`, `enums.py`) already generalizes to any fund: a
`Fund` enum member, a packaged `data/funds/<slug>.csv` file with
columns `Starting from,Acquisition cost,Sell value,Currency`, loaded
into a `FundTable` that does independent per-column backward-fill
lookups. Adding Ircantec is adding one more fund of that same shape,
sourced from a different publisher than the Agirc-Arrco compilation
PDF the other 51 fund files come from.

Ircantec officially publishes two series, each with its own history and
cadence - **not** aligned to a single shared date, contrary to this
design's original assumption:

- **Acquisition cost** ("salaire de référence") - per
  `baseircantec.retraites.fr`'s "Evolution des taux théoriques et du
  salaire de référence Ircantec" (verified across two independently
  dated editions, 14/12/2023 and 26/02/2026, with identical historical
  values): one value per calendar year from **1947** (26 anciens
  francs) through **2026** (5.787 EUR), nominally effective January
  1st of each year (explicitly confirmed only "à compter de 2018";
  earlier years are dated January 1st by the same convention every
  other single-value-per-year fund file in this package already uses).
  1935-1946 is excluded: the source splits "salaire de référence" by
  tranche (A/B) for those years with no official single merged value
  and no euro-equivalent computed by the source itself, which does not
  fit this package's single-value-per-fund model - including it would
  mean picking one tranche's figure over the other, which is not a
  decision this package should make silently.
- **Sell value** ("valeur de service du point") - per
  `ircantec.retraites.fr/retraite/valeur-point`: one value per
  effective period from **01/04/2011** (0.45887 EUR) through
  **01/01/2026** (0.56053 EUR), with irregular effective dates (1
  April, 1 October, or 1 January depending on era, plus one mid-year
  change on 1 July 2022) that only settle into a once-a-year, January
  1st cadence from 2019 onward. No official source for 1971-2011 sell
  value was found.

Like `agirc_arrco.csv` (two different effective dates per year for the
two columns, see README), `ircantec.csv` needs the split-row technique:
each row populates only the column whose value changed on that row's
date, generalized here to the full set of real effective dates found
in the sources above (not just two fixed dates per year).

## Goals / Non-Goals

**Goals:**
- Add Ircantec as a fully regular fund: same `Fund` enum pattern, same
  CSV shape, same `FundTable` lookup behavior, same currency handling
  as every other fund.
- Make the `info_retraite` importer treat `"Ircantec"` rows as this
  fund.
- Keep the change additive and backward compatible: no existing fund,
  CSV, or public API shape changes.

**Non-Goals:**
- Supporting `RCI` or any other scheme beyond Ircantec (explicitly out
  of scope per the proposal).
- Supporting Ircantec's pre-1971 predecessor institutions, **IPACTE**
  and **IGRANTE** (merged into Ircantec by décret n° 70-1277 of 23
  December 1970, effective 1 January 1971). Unlike the pre-1999 Arrco
  affiliated funds this package already bundles, IPACTE/IGRANTE do not
  appear to have a published historical point-value table to
  transcribe: pre-1971 service is instead handled through a one-off
  retroactive "validation de services passés" procedure, not an
  ongoing point series. Out of scope unless a genuine published table
  is found.
- Modeling any point-conversion coefficients between Ircantec and
  Agirc-Arrco (there are none - they are and remain two independent
  schemes, each contributing its own line to a combined annuity, same
  as today's Agirc-Arrco + pre-1999 affiliated funds model).
- Transcribing the pre-1947 (1935-1946) tranche-split "salaire de
  référence" figures, for the reason given in Context above.
- Backfilling sell value for 1971-2011 - no official source was found;
  this is a documented gap (see Risks), not a silent omission.

## Decisions

- **Data source**: Ircantec's own official pages/documents
  (`ircantec.retraites.fr`), not the Agirc-Arrco PDF. This is a
  deliberate change to the "single source" pattern used so far -
  `README.md`'s "Data" section cites one PDF for all 52 existing
  files; it needs a second, clearly-labeled citation for
  `ircantec.csv` once this file exists, following the same
  "transcribe as published, note anomalies" posture already used for
  the existing funds (see "Known limitations").
- **Split-row technique, generalized**: `ircantec.csv` uses the same
  one-row-per-effective-date-per-column technique as `agirc_arrco.csv`
  (each row populates only the column that changed on that date),
  generalized to the full set of real dates found (not just two fixed
  dates per year) - no new parsing or model code is needed, since
  `FundTable` already does independent per-column backward-fill.
- **Full available history, not a truncated "modern era"**: acquisition
  cost is transcribed from **1947** (its first year with a single,
  tranche-unified value) through **2026**; sell value from **2011**
  (the earliest the official page tabulates) through **2026**. This is
  a deliberate expansion beyond this design's original ~2013 estimate,
  chosen over a narrower "modern-only" range because the fuller series
  is genuinely published and verifiable (see Context).
- **Currency per source era**: acquisition cost uses `FRF (ancien)`
  (1947-1959, values converted to literal ancien-franc amounts - the
  source's own franc figures for this era are already expressed as
  nouveau-franc equivalents, so they are multiplied by 100 before
  being stored, to match this package's existing `FRF (ancien)` /
  `to_eur()` convention of storing literal ancien-franc amounts, same
  as `agirc.csv`'s pre-1960 rows), `FRF` (1960-2000, literal nouveau-
  franc amounts, no conversion needed), then `EUR` (2001 onward, the
  source's own euro column). Sell value is `EUR` throughout (2011
  onward only). No new currency concept needed.
- **Importer change is additive, not restructured**: `FUND_LABELS` in
  `info_retraite.py` is a plain `dict[str, Fund]`; adding
  `"Ircantec": Fund.IRCANTEC` is the only code change needed there.
  `RCI` is deliberately left absent from that mapping.

## Risks / Trade-offs

- [Risk] Introducing a second data provenance (Ircantec's own site)
  alongside the single Agirc-Arrco PDF this package has relied on so
  far could make the "Data" section of the README read as
  inconsistent if not clearly labeled. → Mitigation: document
  `ircantec.csv`'s source distinctly from the other 52 files in the
  same "Files" list, following the existing per-file bullet
  convention.
- [Risk] Sell value has no official source for 1971 (Ircantec's
  creation) through 2011 - a 40-year gap. A `Career` with Ircantec
  points earned in that window would get a `NoValueAvailableError`
  when computing an annuity, even though acquisition cost (and thus
  points) might be computable back to 1947. → Mitigation: this is the
  same "no value before earliest entry" behavior every other fund
  already has, documented explicitly in the README as a known
  limitation specific to this fund (mirrors `arrco.csv`'s own
  documented sell-value gap before 1999).
- [Risk] Pre-1960 acquisition-cost values require a franc-amount
  conversion (×100, source → literal ancien francs) before storage,
  introducing a manual transcription step that is easy to get wrong
  silently. → Mitigation: cross-checked the converted figures against
  `to_eur()`'s own formula reproducing the source's published
  euro-equivalent column (e.g. 1947: 26 ancien francs → 26/100/
  6.55957 = 0.0396 ≈ the source's own stated 0.04 EUR) before writing
  the CSV; the focused test added in tasks.md re-verifies this.
- [Risk] Fund count assumptions baked into existing tests (e.g. "52
  funds") will fail once this fund is added. → Mitigation: tracked
  explicitly as a task; the drift-check test
  (`tests/test_enums.py::test_fund_enum_matches_packaged_csv_files`)
  will itself force the enum and CSV to be added together.

## Open Questions

(none - resolved during implementation; see Context and Decisions
above.)
