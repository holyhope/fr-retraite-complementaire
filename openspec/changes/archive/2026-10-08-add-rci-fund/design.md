## Context

See `proposal.md` — Why/What Changes for motivation and scope. This
package's existing fund-data architecture (per `README.md` "Data" section
and `src/fr_retraite_complementaire/models.py`, `data_loader.py`,
`enums.py`) already generalizes to any fund: a `Fund` enum member, a
packaged `data/funds/<slug>.csv` file with columns `Starting
from,Acquisition cost,Sell value,Currency`, loaded into a `FundTable`
that does independent per-column backward-fill lookups.

**RCI itself is done** (`Fund.RCI`, `rci.csv`, 2013 onward, confirmed via
CNAV circulaire n°2025-31 — "Revalorisation des valeurs du régime
complémentaire des travailleurs indépendants (RCI) au 1er janvier 2026" —
cross-checked against `statistiques-recherche.lassuranceretraite.fr`'s
annual "Fiche stock RCI" PDFs (2021-2025 editions) and the IPP
`baremes-ipp-yaml` compilation, whose `pt_rci.yaml`/`salref_rci.yaml`
files themselves cite `legislation.cnav.fr` barème pages). Both
acquisition cost and sell value move on the same effective dates from
2015-10-01 onward; only the very first row splits (acquisition cost
effective 2013-01-01, sell value effective 2013-04-01), so `rci.csv`
uses the same per-column split-row technique as `ircantec.csv`, just for
one date pair instead of throughout.

**The research task (originally "investigate, don't commit") found
confirmed, citable official data for every predecessor/legacy category**,
richer than the original two-scheme (RCO/NRCO) assumption. The same CNAV
circular that confirmed RCI's 2026 value lists, as of January 1st, 2026,
six distinct "valeur de service du point" lines:

| Category | Scheme | Value at 1/1/2026 |
|---|---|---|
| Point RCI cotisé | RCI, 2013+ | 1.347 € |
| Point NRCO et points RCO acquis à compter de 1997 | NRCO (commerçants, 2004+) / RCO (artisans, 1997-2012) | 1.347 € |
| Point RC | commerçants'-spouses legacy scheme | 1.347 € |
| Point CMP | spouses not meeting RC's matrimonial condition | 1.347 € |
| Point RCO cotisé à partir du 1979 (jusqu'au 1996) | RCO, artisans, 1979-1996 | 1.205 € |
| Point RCO de reconstitution de carrière | RCO, artisans, pre-1979 | 1.158 € |

Four of these six have converged to RCI's own current value — not by
coincidence, but by explicit regulatory "alignment" starting in 2013 (the
IPP compilation's `pt_rc_art.yaml` carries the note: "A partir de 2013,
les valeurs des points sont alignées avec le régime complémentaire des
commerçants, au sein d'un régime complémentaire des indépendants
(RCI)"). Before 2013 each had its own, different historical series (e.g.
RCO's 1997-2012 bucket ranged ~0.287-0.323 €/point, nothing like RCI's
~1.18-1.35 €/point scale) — so modeling "aligned since 2013" as a mere
cross-reference to `Fund.RCI` would be wrong for any pre-2013 lookup;
each needs its own independent CSV covering its own pre-2013 history,
even though several of their post-2013 numbers happen to repeat RCI's.

Separately, `statistiques-recherche.lassuranceretraite.fr`'s 2024 "Fiche
stock RCI" surfaced a previously-unknown fourth predecessor/absorbed
scheme: **RCEBTP** ("régime d'assurance vieillesse complémentaire des
entrepreneurs du bâtiment et des travaux publics"), whose accrued rights
were "migrés et convertis en points RCI" on January 1st, 2023. Unlike
RCO/NRCO/RC/CMP, no historical point-value table for RCEBTP has yet been
located — whether one exists and is findable is still open (see Risks).

**Architecture implication**: RCO's three post-2009 era buckets (pre-1979
reconstitution, 1979-1996, 1997-2012) are not merely different *valuation
dates* of one series — they are permanently different values depending on
*when the underlying points were acquired*, for points being valued at
the *same* current date. `FundTable` has no acquisition-date dimension;
it only backward-fills by valuation date. So each permanently-distinct
rate must be its own `Fund` member with its own CSV, not a column or
parameter within a shared `rco.csv`. This is the same pattern this
package already uses for Agirc vs. Arrco vs. the 49 individual pre-1999
affiliated funds — many small funds, not one parameterized fund.

## Goals / Non-Goals

**Goals:**
- Add RCI as a fully regular fund — **done**.
- Add RCO, NRCO, RC-conjoints, and CMP as fully regular funds (one or
  more `Fund` members each, per the Architecture implication above),
  each with its own confirmed historical series.
- Add RCEBTP as a fully regular fund **if** a citable pre-2023 table is
  found during implementation.
- Keep every addition additive and backward compatible: no existing
  fund, CSV, or public API shape changes.

**Non-Goals:**
- Modeling point-conversion coefficients between RCI (or any of its
  legacy schemes) and Agirc-Arrco/Ircantec — they remain independent
  schemes, each contributing its own line to a combined annuity (same
  non-goal this package already applies to the 2019 Agirc-Arrco merger).
- Adding RCEBTP's historical table if no citable pre-2023 source is
  found — in that case, `funds/rcebtp` is reduced to documenting the
  2023 migration event as a known limitation (README), the same posture
  `add-ircantec-fund` took for IPACTE/IGRANTE, rather than fabricating a
  table or guessing values from RCI's post-2023 rate.
- Reconciling or cross-converting between the legacy schemes themselves
  (e.g. treating RC and CMP as "the same" just because they currently
  share RCI's value) — each gets its own CSV with its own confirmed
  historical series, even where recent values happen to coincide.

## Decisions

- **Data sources** (all confirmed primary, not web-search summaries):
  CNAV circulaire n°2025-31 (22 Dec 2025, PDF, text-extracted via
  `pdftotext`); `statistiques-recherche.lassuranceretraite.fr`'s annual
  "Fiche stock RCI" PDFs (2021 through 2025 editions, each stating that
  year's point value as of December 31st); the IPP `baremes-ipp-yaml`
  GitLab repo's `pt_rci.yaml`, `salref_rci.yaml`, `pt_rc_art.yaml`,
  `pt_rc_com.yaml`, `salref_rc_art.yaml`, `salref_rc_com.yaml` (each
  citing its own `legislation.cnav.fr` barème source in its
  `documentation` field). RCEBTP's source, if any, is still to be found.
- **One `Fund` per permanently-distinct rate, not one per "scheme" label**:
  RCO is not one fund — it is at minimum three (reconstitution-de-carrière,
  1979-1996, 1997-2012-aligned), because `FundTable` cannot otherwise
  represent "value depends on both valuation date and acquisition date".
  The exact final count and `Fund` member names for RCO (and whether
  NRCO/RC/CMP each stay single funds, which the data so far suggests) are
  confirmed during implementation once each era's full series is pulled —
  not fixed here, same posture as RCI's own split-row decision.
- **Legacy/frozen funds are sell-value-only where no ongoing acquisition
  exists**: RCO's three differentiated buckets, and NRCO/RC/CMP after
  their respective end dates, value a frozen stock of already-acquired
  points — there is no "buy a new RCO-1979-1996 point today" acquisition
  cost to transcribe. Their CSVs carry a sell value series only; querying
  `acquisition_cost_eur` on them is expected to raise
  `NoValueAvailableError` for every date, which is valid existing
  `FundTable` behavior, not a defect.
- **Currency per era**: pre-2001 RCO/NRCO figures are in `FRF` (not
  `FRF (ancien)` — these schemes start in 1979/2004, after the 1960
  ancien-franc redenomination); `EUR` from 2001/2002 onward, matching the
  observed scale discontinuity in the source series at the euro
  changeover.

## Risks / Trade-offs

- [Risk] RCEBTP's pre-2023 historical table may not exist in a citable
  form (unlike RCO/NRCO/RC/CMP, which are now confirmed). → Mitigation:
  explicit conditional Non-Goal above; if not found, document the gap
  rather than guess or omit the 2023 migration event entirely.
- [Risk] RC-conjoints and CMP's apparent full historical alignment with
  RCI's/NRCO's rate (not just currently, but throughout) is unconfirmed
  beyond the 2026 circular snapshot — their own pre-2026 series still
  needs to be independently pulled during implementation, the same way
  RCO/NRCO's was for this design, rather than assumed to simply mirror
  NRCO's numbers. → Mitigation: tracked as its own research+transcribe
  task pair in `tasks.md`, mirroring RCI's own.
- [Risk] Six new/expanded funds significantly increase the surface this
  change touches (enum members, CSVs, specs, tests, README bullets) in
  one change. → Mitigation: `tasks.md` sequences research-and-transcribe
  per scheme as independent, individually-verifiable task groups, so a
  partial result (e.g. RCEBTP data not found) doesn't block the rest.
- [Risk] Fund-count assumptions baked into existing tests will need
  updating multiple times as funds are added incrementally. →
  Mitigation: the drift-check test
  (`tests/test_enums.py::test_fund_enum_matches_packaged_csv_files`)
  forces enum/CSV pairs to be added together; a single final test-count
  update task runs after all new funds exist.

## Open Questions

(none requiring a decision before proceeding — the scope question this
design previously deferred has been resolved by the user: build all five
newly-confirmed legacy/predecessor schemes, with RCEBTP conditional on
finding its source. Remaining unknowns, such as RCO's exact `Fund`-member
count and RCEBTP's data availability, are implementation research tasks
with their own verification steps in `tasks.md`, not open design
questions.)
