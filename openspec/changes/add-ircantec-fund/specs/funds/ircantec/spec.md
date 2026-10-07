## Purpose

Lets a `Career` hold and value points acquired in the Ircantec
complementary pension scheme (public-sector non-permanent staff),
alongside Agirc-Arrco and the other funds this package already
supports, including recognizing Ircantec rows in a
`www.info-retraite.fr` import.

## ADDED Requirements

### Requirement: Ircantec fund identifier

The system SHALL expose a `Fund` identifier for the Ircantec scheme,
listed by `list_funds()` / iterable via `Fund`, usable anywhere an
existing fund identifier (e.g. `"agirc"`, `"arrco"`) is accepted.

#### Scenario: Ircantec appears in the list of available funds

- **WHEN** a caller lists the available funds (library `list_funds()`
  or the `list-funds` CLI command)
- **THEN** the Ircantec fund identifier is included in the result

#### Scenario: Points can be recorded against Ircantec

- **WHEN** a caller records a point acquisition against the Ircantec
  fund identifier on a `Career`
- **THEN** the acquisition is accepted (no `UnknownFundError`/unknown
  fund error is raised)

### Requirement: Ircantec historical point-value data

The system SHALL provide a historical point-value table for the
Ircantec fund, covering both the point's acquisition cost ("salaire de
référence") and sell value ("valeur de service du point"), each as a
step function over time with the same lookup and backward-fill
semantics as every other fund's table (a date between two published
values resolves to the most recent one at or before that date; a date
before the earliest published value raises the same not-available
error as other funds).

#### Scenario: Sell value lookup resolves to the value in effect

- **WHEN** the Ircantec fund's sell value is requested for a date that
  falls on or after a known effective date and before the next known
  effective date
- **THEN** the value published for that earlier effective date is
  returned, converted to EUR

#### Scenario: Date before the earliest known data

- **WHEN** the Ircantec fund's sell value or acquisition cost is
  requested for a date earlier than the fund's earliest known entry
- **THEN** the system raises the same "no value available" error it
  raises for any other fund in that situation

#### Scenario: Annuity computation includes Ircantec contributions

- **WHEN** a `Career` holds points recorded against the Ircantec fund
  and its annuity (or per-fund breakdown) is computed as of a given
  date
- **THEN** the result includes Ircantec's contribution, computed as
  Ircantec points held times the Ircantec sell value in effect on that
  date (in EUR), on the same basis as every other fund held

### Requirement: info-retraite.fr importer recognizes Ircantec

The system SHALL treat a `"Ircantec : <points>"` entry in a
`www.info-retraite.fr` points-history export as a supported scheme and
convert it into points recorded against the Ircantec fund, rather than
treating it as an unsupported scheme.

#### Scenario: Ircantec row is imported, not skipped

- **WHEN** an info-retraite.fr export is imported and it contains an
  `"Ircantec : N points"` entry for a given year
- **THEN** the resulting `Career` has that many points recorded against
  the Ircantec fund for that year, and the entry does NOT appear in the
  import's list of skipped (unsupported) entries

#### Scenario: Other unsupported schemes are still skipped

- **WHEN** the same import also contains an entry for a scheme this
  package has no data for (e.g. `"RCI : N points"`)
- **THEN** that entry is still handled as an unsupported scheme per the
  existing unsupported-fund policy (warn/skip/error), unchanged by this
  capability
