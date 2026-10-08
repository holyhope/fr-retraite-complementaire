## Context

See `proposal.md` — Why/What Changes for motivation and scope. This
package's existing fund-data architecture (per `README.md` "Data" section
and `src/fr_retraite_complementaire/models.py`, `data_loader.py`,
`enums.py`) already generalizes to any fund: a `Fund` enum member, a
packaged `data/funds/<slug>.csv` file with columns `Starting
from,Acquisition cost,Sell value,Currency`, loaded into a `FundTable`
that does independent per-column backward-fill lookups. Adding RCI is
adding one more fund of that same shape.

RCI ("Régime Complémentaire des Indépendants") is a points-based
complementary pension scheme for self-employed workers, created January
1st, 2013 by merging two predecessor schemes: RCO ("Régime Complémentaire
Obligatoire", artisans, in effect since 1979) and NRCO ("Nouveau Régime
Complémentaire des Commerçants"). A preliminary web search (not yet a
full source audit — that is implementation work, same as it was for
Ircantec) found a unified "valeur de service du point" and "revenu de
référence" (acquisition cost) series published year-by-year from 2013
through 2026, cross-corroborated across CNAV/Assurance Retraite circulars
and an independent actuarial-parameters compilation (IPP). The exact
official URL(s) to cite, and whether finer-grained (sub-annual) effective
dates exist like `agirc_arrco.csv`'s Jan 1st/Nov 1st split, are left to
implementation research (`tasks.md` 1.1), following the same
"research-first, then transcribe" posture used for `ircantec.csv` — this
design does not assume a one-row-per-year shape in advance.

The same preliminary search surfaced that RCI's official circulars still
list several *other*, lower, point values for specific legacy point
categories carried over from before the 2013 merger (e.g. "points RCO
1979-1996", "points de reconstitution de carrière avant 1979") — these
are not a current RCI member's going-forward point value, but a
backward-compatible valuation for pre-merger point stocks, the same kind
of merger artifact as the point-conversion coefficients this package
already declines to model for the 2019 Agirc-Arrco merger (see that
capability's non-goal). This design treats them the same way.

## Goals / Non-Goals

**Goals:**
- Add RCI as a fully regular fund: same `Fund` enum pattern, same CSV
  shape, same `FundTable` lookup behavior, same currency handling as
  every other fund.
- Make the `info_retraite` importer treat `"RCI"` rows as this fund.
- Keep the change additive and backward compatible: no existing fund,
  CSV, or public API shape changes.

**Non-Goals:**
- Modeling RCI's legacy pre-merger point-value sub-categories ("points
  RCO 1979-1996", pre-1979 "reconstitution de carrière" points, and any
  other such category found during research) as separate values within
  `rci.csv`. `rci.csv` models only the single, unified point value used
  for points acquired under RCI itself (2013 onward) — the same scope
  decision this package already made for not modeling the Agirc/Arrco
  2019 merger's conversion coefficients.
- Adding `funds/rco` or `funds/nrco` as part of *this* change. Per
  `proposal.md`, researching whether official historical tables exist for
  either pre-2013 predecessor scheme is in scope (`tasks.md` 1.x), but
  actually adding either as a bundled fund is not: it requires its own
  capability and delta spec, decided and added separately before any
  `rco.csv`/`nrco.csv` is written. This mirrors how `add-ircantec-fund`
  treated IPACTE/IGRANTE (researched, found insufficient evidence, and
  explicitly left out) — except here the research outcome is still
  unknown, so the next step if a table *is* found is "propose a follow-up
  change", not "implement it anyway".
- Modeling any point-conversion coefficients between RCI and
  Agirc-Arrco/Ircantec — they are and remain independent schemes, each
  contributing its own line to a combined annuity.

## Decisions

- **Data source**: RCI's own official publications (CNAV/Assurance
  Retraite circulars, `statistiques-recherche.lassuranceretraite.fr`,
  `legislation.lassuranceretraite.fr`), not the Agirc-Arrco PDF — same
  "second source, clearly labeled" pattern already established for
  `ircantec.csv`. The exact citable URL(s) are confirmed during
  implementation (`tasks.md` 1.1), not fixed here.
- **Scope: unified RCI only (2013 onward), structure confirmed during
  implementation**: `rci.csv` covers RCI's own, single, unified
  acquisition-cost/sell-value series starting January 1st, 2013. Whether
  it needs the split-row technique `agirc_arrco.csv`/`ircantec.csv` use
  (independent effective dates per column) or a simpler one-row-per-year
  shape is a transcription detail resolved by what the sources actually
  publish, not assumed here — same posture as `add-ircantec-fund`'s
  corrected design, learned the hard way during that change's
  implementation.
- **Currency**: `EUR` throughout, since RCI's entire history (2013
  onward) postdates the euro changeover — no `FRF`/`FRF (ancien)` rows
  are expected, unlike `ircantec.csv` or the pre-1999 affiliated funds.
- **RCO/NRCO are a research task, not a commitment**: `tasks.md` includes
  an explicit research step to check whether either predecessor scheme
  has a citable historical point-value table (akin to the pre-1999 Arrco
  affiliated funds' tables already bundled). The *outcome* of that
  research (found or not found, and in what shape) determines next
  steps per the Non-Goals above — it does not retroactively change what
  this change implements.
- **Importer change is additive, not restructured**: `FUND_LABELS` in
  `info_retraite.py` is a plain `dict[str, Fund]`; adding `"RCI":
  Fund.RCI` is the only code change needed there.

## Risks / Trade-offs

- [Risk] The preliminary source research for this design is a single web
  search, not a verified primary-source read (unlike `ircantec.csv`,
  where the actual PDF/page tables were fetched and visually confirmed
  before writing design.md). The 2013-2026 figures cited above could
  be wrong or incomplete. → Mitigation: `tasks.md` 1.1 requires
  re-deriving and citing the data directly from primary sources
  (official circulars/PDFs) before any CSV is written, exactly as was
  done for `ircantec.csv` after its own design was found to be wrong.
- [Risk] RCO/NRCO research could reveal a citable table *mid-task*,
  creating pressure to just add it since the data is sitting right
  there. → Mitigation: explicit Non-Goal above and a dedicated
  "stop and report" step in `tasks.md`, following this project's
  established apply-phase-pause precedent (see
  `add-ircantec-fund`'s design.md decision log) — surface the finding
  and let the user decide whether to fold it into this change or file a
  follow-up, rather than silently expanding scope.
- [Risk] Fund count assumptions baked into existing tests (e.g. "53
  funds") will fail once this fund is added. → Mitigation: tracked
  explicitly as a task; the drift-check test
  (`tests/test_enums.py::test_fund_enum_matches_packaged_csv_files`)
  will itself force the enum and CSV to be added together.

## Open Questions

(none — the one open question this design could have left open, whether
to pursue RCO/NRCO, is resolved above: research it, but treat any
positive finding as follow-up work requiring a separate decision, not an
automatic addition to this change.)
