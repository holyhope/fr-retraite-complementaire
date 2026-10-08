## Why

This package currently only has point-value data for Agirc-Arrco and
its 49 pre-1999 affiliated funds. Ircantec (the complementary pension
scheme for non-permanent public-sector staff) is a distinct scheme with
its own officially published point-value history, and it already shows
up — unsupported — in real `www.info-retraite.fr` exports: the
`info_retraite` importer explicitly documents Ircantec as a scheme it
has no data for and skips/warns on it today. Adding Ircantec as a
supported fund lets users with Ircantec career points get an accurate
combined annuity instead of a silent gap.

## What Changes

- Add `Fund.IRCANTEC` ("ircantec") as a new fund identifier, backed by a
  packaged `ircantec.csv` historical point-value table, sourced from
  Ircantec's own official publications (not the Agirc-Arrco PDF this
  package otherwise relies on).
- Ircantec's acquisition cost ("salaire de référence") and sell value
  ("valeur de service du point") are published as two independent
  series with their own history and effective dates — acquisition cost
  from 1947, sell value from 2011, with irregular (non-January-1st)
  effective dates before 2019. `ircantec.csv` uses the same split-row
  technique as `agirc_arrco.csv` (one row per effective date per
  column) to represent this. See `design.md` for details.
- Update the `info_retraite` importer's `FUND_LABELS` mapping so an
  `"Ircantec : N points"` row in a `www.info-retraite.fr` export is now
  converted into `Fund.IRCANTEC` points on the `Career`, instead of
  being treated as an unsupported scheme.
- Update documentation (module docstring, README) and existing tests
  that currently assert Ircantec is unsupported, since that is no
  longer true.
- `RCI` remains out of scope and continues to be treated as an
  unsupported scheme by the importer.

## Capabilities

### New Capabilities

- `funds/ircantec`: the package provides a historical point-value table
  for the Ircantec fund (via `Fund.IRCANTEC` and the packaged
  `ircantec.csv`), consistent with the lookup/backward-fill/currency
  behavior all other funds already have, and the `info_retraite`
  importer recognizes `"Ircantec"` rows as this fund instead of
  skipping them.

### Modified Capabilities

(none — no existing capability has a spec file yet; the importer's
current unsupported-fund handling for Ircantec is captured as part of
the new `funds/ircantec` capability above rather than as a modification
to a pre-existing spec.)

## Impact

- `src/fr_retraite_complementaire/enums.py` — new `Fund.IRCANTEC`
  member.
- `src/fr_retraite_complementaire/data/funds/ircantec.csv` — new
  packaged data file.
- `src/fr_retraite_complementaire/importers/info_retraite.py` —
  `FUND_LABELS` gains an `"Ircantec"` entry; module docstring updated.
- `tests/test_enums.py` — drift check continues to pass once the enum
  and CSV are added together (no change needed, but the fund count
  used elsewhere, e.g. `test_data_loader.py::test_list_funds_includes_known_funds`,
  moves from 52 to 53 and must be updated).
- `tests/test_importers.py` — `test_loads_sample_export_warn_policy` and
  related assertions currently expect `"Ircantec"` to be skipped; the
  synthetic fixture (`tests/data/info-retraite-sample.csv`) and/or
  assertions need to change so the test suite still demonstrates both a
  supported scheme (now including Ircantec) and at least one remaining
  unsupported scheme (`RCI`).
- `README.md` — "Files" and "Importing a www.info-retraite.fr export"
  sections currently describe Ircantec as unsupported.
- No breaking change to the public API shape: `Career`, `FundTable`,
  and the CLI are unaffected beyond gaining one more valid fund
  identifier.
