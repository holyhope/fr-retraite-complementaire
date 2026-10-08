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
  **January 1st, 2013** onward. **[DONE — already implemented.]**
- Add historical point-value data for RCI's pre-2013 predecessor and
  legacy sub-category schemes, confirmed via primary sources (CNAV
  circulaire n°2025-31, `statistiques-recherche.lassuranceretraite.fr`
  annual fiches, and the IPP `baremes-ipp-yaml` compilation):
  - **RCO** (artisans, in effect since 1979) — differentiates into
    permanently distinct sell-value rates by acquisition era from 2009
    onward: points acquired before 1979 ("reconstitution de carrière"),
    1979–1996, and 1997–2012 (the last of which the regulation
    explicitly "aligns" with RCI's own rate from 2013 onward).
  - **NRCO** (commerçants, in effect since 2004, succeeding an earlier
    "RC commerçants" label applied to points from 1973 onward) — single
    continuous rate, also aligned with RCI's rate from 2013 onward.
  - **RC (régime des conjoints de commerçants)** — a legacy scheme for
    commerçants' spouses, listed as its own distinct line in official
    circulars ("Point RC").
  - **CMP** ("compte minimum de points") — a related legacy scheme for
    spouses who didn't meet the matrimonial condition for RC.
  - **RCEBTP** (construction-sector complementary scheme) — migrated
    into RCI points on January 1st, 2023; whether an independent
    pre-2023 historical point-value table exists is still unconfirmed
    and is a research task.
  - Exactly how many `Fund` identifiers each scheme needs (e.g. whether
    RCO needs three separate `Fund` members for its three differentiated
    eras) is a data-shape decision made during implementation, once each
    era's full series is pulled — mirroring how RCI's own split-row
    question was resolved during `/opsx-apply` rather than guessed here.
- Add `Fund.RCI` **[DONE]**, plus new `Fund` members for RCO (one or
  more), NRCO, RC-conjoints, CMP, and — if source data is found — RCEBTP.
- Update the `info_retraite.py` importer's `FUND_LABELS` so `"RCI : N
  points"` rows are recognized (**[DONE]**); extend similarly if any of
  the newly-added legacy schemes also appear as their own labeled rows in
  a www.info-retraite.fr export (to be confirmed during implementation —
  it's possible these only ever appear bundled into the "RCI" line once
  migrated/aligned, in which case no further importer change is needed
  for them).
- Update the README and module docstrings that currently cite RCI as an
  example of an unsupported scheme. **[DONE for RCI itself.]**
- **Still not in scope**: modeling point-conversion coefficients between
  RCI/its legacy schemes and Agirc-Arrco/Ircantec — they remain
  independent schemes, each contributing its own line to a combined
  annuity (same non-goal this package already applies to the 2019
  Agirc-Arrco merger).

## Capabilities

### New Capabilities

- `funds/rci`: the RCI fund identifier and its historical point-value
  data (2013 onward) are **[DONE]**; the `info_retraite.py` importer's
  `"RCI"` row recognition is still outstanding (see Impact).
- `funds/rco`: RCO (artisans' pre-2013 legacy scheme) fund identifier(s)
  and historical point-value data, covering its differentiated
  acquisition-era rates.
- `funds/nrco`: NRCO (commerçants' pre-2013 legacy scheme) fund
  identifier and historical point-value data.
- `funds/rc-conjoints`: the commerçants'-spouses legacy "RC" scheme fund
  identifier and historical point-value data.
- `funds/cmp`: the "compte minimum de points" legacy scheme fund
  identifier and historical point-value data.
- `funds/rcebtp`: the RCEBTP construction-sector scheme fund identifier
  and historical point-value data, if a citable pre-2023 source is
  found during implementation; if not, this capability is reduced to
  documenting the 2023 migration as a known limitation rather than
  providing a historical table (same posture as `add-ircantec-fund`'s
  IPACTE/IGRANTE non-goal).

### Modified Capabilities

(none)

## Impact

- New data files: `src/fr_retraite_complementaire/data/funds/rci.csv`
  **[DONE]**, plus new CSV(s) for RCO (one or more), NRCO, RC-conjoints,
  CMP, and possibly RCEBTP.
- `src/fr_retraite_complementaire/enums.py`: `Fund.RCI` **[DONE]**, plus
  new `Fund` members for RCO, NRCO, RC-conjoints, CMP, and possibly
  RCEBTP.
- `src/fr_retraite_complementaire/importers/info_retraite.py`:
  `FUND_LABELS` still needs an `"RCI": Fund.RCI` entry (not yet added,
  despite `Fund.RCI` and `rci.csv` existing); possibly more entries if
  the legacy schemes appear as distinct labels in exports.
- `README.md`: "Data" → "Files" list gains new bullets; "Importing a
  www.info-retraite.fr export" section still cites RCI as an example of
  an unsupported scheme and needs updating once the importer entry
  above is added.
- Tests: fund-count assertions, importer fixture/tests, and new focused
  data-loading tests for each new fund.
- No breaking changes: purely additive.
