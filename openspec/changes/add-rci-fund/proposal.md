## Why

`info_retraite.py`'s importer already recognizes `"RCI : N points"` rows in
a www.info-retraite.fr export but treats them as an unsupported scheme
(skipped/warned/errored per `on_unsupported`), because this package has no
historical point-value data for RCI. Self-employed workers (artisans and
commerçants) who import their export today silently lose their RCI points
from the computed annuity. Adding RCI as a fully supported fund — following
the same pattern already used for Agirc-Arrco and, more recently, Ircantec
— closes this gap.

## What Changes

- Add a new `rci.csv` fund covering the unified **RCI** ("Régime
  Complémentaire des Indépendants") point value from its creation on
  **January 1st, 2013** onward (RCI merged the pre-existing RCO, for
  artisans, and NRCO, for commerçants, schemes into one points-based
  regime).
- **Investigate** whether official historical point-value tables exist
  for RCI's pre-2013 predecessor schemes, **RCO** (artisans, in effect
  since 1979) and **NRCO** (commerçants) — mirroring how this package
  already bundles the 49 pre-1999 Arrco-affiliated funds alongside the
  unified `arrco.csv`. This change's `tasks.md` includes that research as
  an early task. If a citable table is found for either scheme, adding it
  as its own fund is **follow-up work**: it needs its own `funds/rco` or
  `funds/nrco` capability and delta spec, added by updating this change
  (or filing a new one) *before* writing the corresponding CSV/code —
  not silently implemented as a side effect of this change's `tasks.md`.
  This proposal commits only to the `funds/rci` capability below; see
  `design.md` "Open Questions" for the decision this research needs to
  resolve.
- Add `Fund.RCI` (and, if their historical tables are found and bundled,
  `Fund.RCO` / `Fund.NRCO`) to the `Fund` enum.
- Update the `info_retraite.py` importer's `FUND_LABELS` so `"RCI : N
  points"` rows are recognized and converted into `Career` points against
  `Fund.RCI`, rather than being skipped as unsupported.
- Update the README and module docstrings that currently cite RCI as an
  example of an unsupported scheme.
- **Not** in scope: reconciling the legacy, still-distinct "valeur de
  service du point" sub-categories that RCI itself keeps for points
  carried over from before the merger (e.g. official circulars list
  separate values for "points RCO 1979-1996" and "points de reconstitution
  de carrière avant 1979", distinct from the single, unified point value
  used for points *acquired* under RCI from 2013 onward). This package
  does not model cross-merger point-conversion coefficients for
  Agirc-Arrco either (see that capability's existing non-goal); RCI's
  legacy sub-categories are the same kind of merger-artifact and are
  called out as an explicit non-goal in `design.md`.

## Capabilities

### New Capabilities

- `funds/rci`: the RCI fund identifier, its historical point-value data
  (2013 onward), and `info_retraite.py` importer recognition of `"RCI"`
  rows — mirrors `funds/ircantec`'s shape and scope. This is the only
  capability this change commits to; see "What Changes" above for why
  `funds/rco` / `funds/nrco` are explicitly not included here.

### Modified Capabilities

(none — RCI's current "unsupported scheme" behavior in `info_retraite.py`
has no existing capability spec of its own to modify; it is folded into
the new `funds/rci` capability, same precedent as `funds/ircantec`.)

## Impact

- New data files: `src/fr_retraite_complementaire/data/funds/rci.csv`,
  and possibly `rco.csv` / `nrco.csv` (see above).
- `src/fr_retraite_complementaire/enums.py`: new `Fund` member(s).
- `src/fr_retraite_complementaire/importers/info_retraite.py`:
  `FUND_LABELS` gains an `"RCI": Fund.RCI` entry; module docstring and
  comments updated.
- `README.md`: "Data" → "Files" list gains new bullet(s); "Importing a
  www.info-retraite.fr export" section no longer cites RCI as
  unsupported.
- Tests: fund-count assertions, importer fixture/tests, and new
  focused data-loading tests for the new fund(s).
- No breaking changes: purely additive, same as `add-ircantec-fund`.
