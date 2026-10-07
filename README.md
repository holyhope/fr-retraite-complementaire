# fr-retraite-complementaire

Historical point-value / "salaire de référence" data for the French
mandatory supplementary pension schemes **Agirc** and **Arrco** (merged
into **Agirc-Arrco** since 2019), sourced from the official reference
document published by [agirc-arrco.fr](https://www.agirc-arrco.fr):

> https://www.agirc-arrco.fr/storage/2024/10/Compilation_valeurs_de_point_novembre_2025.pdf

## Data files

All files are plain CSV with the header:

```
Starting from,Acquisition cost,Sell value,Currency
```

- `Starting from` — date (M/D/YYYY) from which the row's values apply.
- `Acquisition cost` ("salaire de référence" / purchase price) — cost to
  acquire one point. Only populated on the row where it changes (usually
  once a year, in January or April); left blank on intermediate
  semi-annual rows where only the point's sell value changed.
- `Sell value` ("valeur de service du point") — value of one point when
  paid out as a pension.
- `Currency` — `EUR`, `FRF` (French franc, 1960–2001), or `FRF (ancien)`
  (pre-1960 "ancien franc", before the 1960 redenomination, 1 new franc =
  100 old francs).

### Top-level files (`data/`)

- `agirc.csv` — unified Agirc point value, 1947–2018 (Agirc merged into
  Agirc-Arrco from Nov. 2019).
- `arrco.csv` — unified Arrco salaire de référence, 1948–2018. **Sell
  value is only available from 1999 onward** — before 1999 Arrco was a
  federation of ~50 independent affiliated funds (see `data/funds/`
  below), each with its own point sell value; there was no single unified
  Arrco point value prior to 1999.
- `agirc_arrco.csv` — unified Agirc-Arrco point value since the Nov. 2019
  merger, through the latest published value.

### Affiliated-fund files (`data/funds/`)

One CSV per pre-1999 Arrco-affiliated fund (49 funds), covering their
individual historical point values before Arrco unification. File names
are the fund's name, lowercased/slugified (e.g. `agrr.csv`,
`caisse-gutenberg.csv`, `cpm-convention-de-solidarite.csv`).

Known simplifications/limitations in the fund-level files:

- Values are given per date column as published in the source PDF; the
  PDF's additional year-over-year "% evolution" columns are not
  reproduced here.
- All fund-level data is in plain `FRF` (none of the funds' tables in the
  source document go back far enough to need the `FRF (ancien)`
  distinction, except where handled specially).
- `canarep.csv` only includes the "opérations obligatoires" series
  (1972–1998); the source PDF also has a separate "opérations
  facultatives" sub-table for the same fund which is not included here.
- A few funds have minor anomalies that are present in the *source PDF
  itself* and have been transcribed as-is rather than corrected (e.g.
  `cnro.csv` has an apparent outlier value at 1/1/1986; `cri.csv` has an
  apparent ~10x scale change around 1970).

## Source

Data manually extracted and transcribed from the official Agirc-Arrco
compilation PDF (link above). No values were fabricated; blank cells
reflect either a lack of data in the source for that field (e.g. no
unified point value), or no revaluation event for that sub-period.
