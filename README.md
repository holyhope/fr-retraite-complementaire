# fr-retraite-complementaire

A Python SDK to compute French supplementary pension (**Agirc-Arrco**)
annuities for an individual, from the points ("tokens") they earned
across their career.

Anyone can record their career's point acquisitions — per fund, per
date — and compute the resulting yearly pension annuity, using the
official historical point-value data bundled with the package.

## Installation

```bash
pip install fr-retraite-complementaire
# or, with uv:
uv add fr-retraite-complementaire
```

## Usage (library)

```python
from datetime import date
from fr_retraite_complementaire import Career

career = Career()
career.add_points(fund="agirc", date=date(1995, 6, 1), points=120.5)
career.add_points(fund="arrco", date=date(1995, 6, 1), points=80)
career.add_points(fund="agrr", date=date(1980, 1, 1), points=15)  # a pre-1999 affiliated fund

# Yearly pension annuity, in EUR, valued as of a given date:
annual_pension_eur = career.annuity(as_of=date(2025, 1, 1))

# Per-fund breakdown:
for entry in career.breakdown(as_of=date(2025, 1, 1)):
    print(entry.fund, entry.points, entry.point_value_eur, entry.annual_amount_eur)
```

- `Career.add_points(fund, date, points)` records a point acquisition.
  `fund` must be one of the identifiers returned by `list_funds()`.
- `Career.annuity(as_of)` returns the total yearly pension (sum over all
  funds of `points held x the fund's point value in effect on as_of`),
  in EUR.
- `Career.breakdown(as_of)` returns the same computation broken down
  per fund.
- All currencies (`EUR`, `FRF`, `FRF (ancien)`) are automatically
  converted to EUR using the legally fixed FRF/EUR rate (6.55957) and
  the 1960 redenomination rate (100 anciens francs = 1 nouveau franc).

## Usage (CLI)

```bash
fr-retraite-complementaire list-funds

fr-retraite-complementaire compute --career career.csv --as-of 2025-01-01
```

Where `career.csv` has the columns `fund,date,points`:

```csv
fund,date,points
agirc,1995-06-01,120.5
arrco,1995-06-01,80
agrr,1980-01-01,15
```

## Data

Historical point-value data is bundled with the package under
`fr_retraite_complementaire/data/funds/*.csv`, sourced from the official
Agirc-Arrco compilation PDF:

> https://www.agirc-arrco.fr/storage/2024/10/Compilation_valeurs_de_point_novembre_2025.pdf

Each CSV has the columns:

```
Starting from,Acquisition cost,Sell value,Currency
```

- `Starting from` — date from which the row's values apply.
- `Acquisition cost` ("salaire de référence") — cost to acquire one
  point. Only populated on the row where it changes.
- `Sell value` ("valeur de service du point") — value of one point when
  paid out as a pension. Treated as a step function: a date without its
  own sell value inherits the last known one.
- `Currency` — `EUR`, `FRF` (1960–2001), or `FRF (ancien)` (pre-1960).

### Files

- `agirc.csv` — unified Agirc point value, 1947–2018 (Agirc merged into
  Agirc-Arrco from Nov. 2019).
- `arrco.csv` — unified Arrco salaire de référence, 1948–2018. **Sell
  value is only available from 1999 onward** — before 1999 Arrco was a
  federation of ~50 independent affiliated funds, each with its own
  point sell value; there was no single unified Arrco point value prior
  to 1999.
- `agirc_arrco.csv` — unified Agirc-Arrco point value since the Nov.
  2019 merger.
- All other files — one per pre-1999 Arrco-affiliated fund (49 funds),
  covering their individual historical point values before Arrco
  unification (e.g. `agrr.csv`, `caisse-gutenberg.csv`,
  `cpm-convention-de-solidarite.csv`).

### Known limitations

- Fund-level files reflect the source PDF's published date columns;
  its additional year-over-year "% evolution" columns are not
  reproduced.
- `canarep.csv` only includes the "opérations obligatoires" series
  (1972–1998); the source PDF also has a separate "opérations
  facultatives" sub-table for the same fund which is not included.
- A few funds have minor anomalies present in the *source PDF itself*,
  transcribed as-is rather than corrected (e.g. `cnro.csv` has an
  apparent outlier value at 1/1/1986; `cri.csv` has an apparent ~10x
  scale change around 1970).
- This package does **not** model the point-conversion coefficients
  applied when affiliated funds were absorbed into Arrco (1999) or when
  Agirc and Arrco merged (2019); it values points strictly against the
  fund they were recorded in. Real-world pension calculations by a
  points-tracking fund account for those conversions.

No values were fabricated; blank cells reflect either a lack of data in
the source for that field, or no revaluation event for that sub-period.

## Development

```bash
uv sync --group dev
uv run pytest
uv run fr-retraite-complementaire list-funds
```

CI (GitHub Actions) runs the test suite across Python 3.10–3.13 and
builds the package on every push/PR.
