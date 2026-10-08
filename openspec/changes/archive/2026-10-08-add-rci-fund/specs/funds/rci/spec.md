## Purpose

Lets a `Career` hold and value points acquired in the RCI (Régime
Complémentaire des Indépendants) complementary pension scheme for
self-employed workers (artisans and commerçants), alongside Agirc-Arrco,
Ircantec, and the other funds this package already supports, including
recognizing RCI rows in a `www.info-retraite.fr` import.

## ADDED Requirements

### Requirement: RCI fund identifier

The system SHALL expose a `Fund` identifier for the RCI scheme, listed by
`list_funds()` / iterable via `Fund`, usable anywhere an existing fund
identifier (e.g. `"agirc"`, `"ircantec"`) is accepted.

#### Scenario: RCI appears in the list of available funds

- **WHEN** a caller lists the available funds (library `list_funds()` or
  the `list-funds` CLI command)
- **THEN** the RCI fund identifier is included in the result

#### Scenario: Points can be recorded against RCI

- **WHEN** a caller records a point acquisition against the RCI fund
  identifier on a `Career`
- **THEN** the acquisition is accepted (no unknown-fund error is raised)

### Requirement: RCI historical point-value data

The system SHALL provide a historical point-value table for the RCI
fund, covering both the point's acquisition cost ("revenu de référence" /
"valeur d'achat du point") and sell value ("valeur de service du point"),
from RCI's creation (January 1st, 2013) onward, as a step function over
time with the same lookup and backward-fill semantics as every other
fund's table (a date between two published values resolves to the most
recent one at or before that date; a date before the earliest published
value raises the same not-available error as other funds).

#### Scenario: Sell value lookup resolves to the value in effect

- **WHEN** the RCI fund's sell value is requested for a date that falls
  on or after a known effective date and before the next known effective
  date
- **THEN** the value published for that earlier effective date is
  returned, converted to EUR

#### Scenario: Date before the earliest known data

- **WHEN** the RCI fund's sell value or acquisition cost is requested for
  a date earlier than the fund's earliest known entry (January 1st, 2013,
  or later if an earlier date is not confirmed during implementation)
- **THEN** the system raises the same "no value available" error it
  raises for any other fund in that situation

#### Scenario: Annuity computation includes RCI contributions

- **WHEN** a `Career` holds points recorded against the RCI fund and its
  annuity (or per-fund breakdown) is computed as of a given date
- **THEN** the result includes RCI's contribution, computed as RCI points
  held times the RCI sell value in effect on that date (in EUR), on the
  same basis as every other fund held

### Requirement: info-retraite.fr importer recognizes RCI

The system SHALL treat an `"RCI : <points>"` entry in a
`www.info-retraite.fr` points-history export as a supported scheme and
convert it into points recorded against the RCI fund, rather than
treating it as an unsupported scheme.

#### Scenario: RCI row is imported, not skipped

- **WHEN** an info-retraite.fr export is imported and it contains an
  `"RCI : N points"` entry for a given year
- **THEN** the resulting `Career` has that many points recorded against
  the RCI fund for that year, and the entry does NOT appear in the
  import's list of skipped (unsupported) entries

#### Scenario: Other unsupported schemes are still skipped

- **WHEN** the same import also contains an entry for a scheme this
  package has no data for
- **THEN** that entry is still handled as an unsupported scheme per the
  existing unsupported-fund policy (warn/skip/error), unchanged by this
  capability
