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

Ircantec officially publishes (per `ircantec.retraites.fr`, "Valeur du
point" and "Les paramètres utilisés par l'Ircantec" pages):
- "Valeur de service du point" (sell value) - a fixed amount per
  calendar year, effective January 1st.
- "Salaire de référence" (acquisition cost) - also effective January
  1st of the same calendar year.

Unlike `agirc_arrco.csv` (two different effective dates per year for
the two columns, see README), Ircantec changes both columns on the
**same** date each year - acquisition cost and sell value are present
together on every row, with no split-date rows needed.

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
- Reproducing Ircantec's own "intermediate" sub-annual rate changes, if
  any existed in the past (e.g. mid-year adjustments before the
  scheme's modern once-a-year cadence) beyond what is needed for a
  clean annual step function; see Open Questions.

## Decisions

- **Data source**: Ircantec's own official pages/documents
  (`ircantec.retraites.fr`), not the Agirc-Arrco PDF. This is a
  deliberate change to the "single source" pattern used so far -
  `README.md`'s "Data" section cites one PDF for all 52 existing
  files; it needs a second, clearly-labeled citation for
  `ircantec.csv` once this file exists, following the same
  "transcribe as published, note anomalies" posture already used for
  the existing funds (see "Known limitations").
- **One row per year, both columns filled**: because Ircantec changes
  both values on the same January 1st date, `ircantec.csv` does not
  need the split-row technique `agirc_arrco.csv` uses. Each row simply
  has both `Acquisition cost` and `Sell value` populated (or blank
  where a column is genuinely unpublished for that date), consistent
  with the general `FundTable` step-function/backward-fill contract -
  no new parsing or model code is needed.
- **Currency**: default to `EUR` for the data range transcribed in
  this change (Ircantec's public per-year tables cited in the proposal
  only go back to the point euros were already in use). If, during
  implementation, older Ircantec figures published in francs are
  found and included, they follow the existing `FRF`/`FRF (ancien)`
  conventions already defined in `currency.py` - no new currency
  concept is needed either way.
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
- [Risk] Ircantec's officially published tables may not go as far back
  in time as Agirc-Arrco's (per the proposal's research, back to at
  least 2013 for acquisition cost and 2017 for sell value from the
  pages found; older archives were not located). A `Career` with
  Ircantec points earned before the earliest transcribed date would
  raise the standard "no value available" error. → Mitigation: this
  is the same behavior every other fund already has for dates before
  its earliest entry (see `funds/ircantec` spec, "Date before the
  earliest known data" scenario); no special-casing needed, but the
  earliest supported date should be documented in the README like the
  other funds' coverage ranges are.
- [Risk] Fund count assumptions baked into existing tests (e.g. "52
  funds") will fail once this fund is added. → Mitigation: tracked
  explicitly as a task; the drift-check test
  (`tests/test_enums.py::test_fund_enum_matches_packaged_csv_files`)
  will itself force the enum and CSV to be added together.

## Open Questions

- Exactly how far back Ircantec's officially published, citable figures
  go (beyond the ~2013/2017 starting points found during proposal
  research) is left to implementation-time research; it does not
  change the spec, the approach, or the task breakdown - the fund's
  `earliest_date` is simply whatever the sourced data supports, like
  every other fund.
