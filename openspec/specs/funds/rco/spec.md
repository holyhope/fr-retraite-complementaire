## Purpose

Lets a `Career` hold and value legacy RCO (artisans' pre-RCI complementary
pension) points, covering the three permanently distinct point values
that apply depending on when the underlying points were acquired, so
that artisans who contributed before RCI's 2013 creation don't lose that
history when their www.info-retraite.fr export or career ledger is
imported.

## Requirements

### Requirement: RCO fund identifiers per acquisition era

The system SHALL expose a distinct fund identifier for each permanently
distinct RCO point-value category confirmed to exist (points acquired
before January 1st, 1979 via "reconstitution de carrière"; points
acquired between January 1st, 1979 and December 31st, 1996; and points
acquired between January 1st, 1997 and December 31st, 2012). Each is
listed by `list_funds()` / iterable via `Fund`, usable anywhere an
existing fund identifier is accepted.

#### Scenario: Each RCO era category appears in the list of available funds

- **WHEN** a caller lists the available funds (library `list_funds()` or
  the `list-funds` CLI command)
- **THEN** a distinct fund identifier for each of the three RCO
  acquisition-era categories is included in the result

#### Scenario: Points can be recorded against a specific RCO era category

- **WHEN** a caller records a point acquisition against one of the RCO
  acquisition-era fund identifiers on a `Career`
- **THEN** the acquisition is accepted (no unknown-fund error is raised),
  independently of any other RCO era category or RCI itself

### Requirement: RCO historical sell-value data

The system SHALL provide a historical sell-value table ("valeur de
service du point") for each RCO acquisition-era fund, as a step function
over time with the same lookup and backward-fill semantics as every
other fund's table (a date between two published values resolves to the
most recent one at or before that date; a date before the earliest
published value raises the same not-available error as other funds).
Because each category values a frozen stock of already-acquired points
(no new points can be acquired under a closed era's rate), these funds
are not required to provide an acquisition cost; a request for
acquisition cost MAY raise the same not-available error for every date.

#### Scenario: Sell value lookup resolves to the value in effect

- **WHEN** an RCO acquisition-era fund's sell value is requested for a
  date that falls on or after a known effective date and before the next
  known effective date
- **THEN** the value published for that earlier effective date is
  returned, converted to EUR

#### Scenario: Date before the earliest known data

- **WHEN** an RCO acquisition-era fund's sell value is requested for a
  date earlier than that fund's earliest known entry
- **THEN** the system raises the same "no value available" error it
  raises for any other fund in that situation

#### Scenario: Acquisition cost is unavailable for a closed era

- **WHEN** an RCO acquisition-era fund's acquisition cost is requested
  for any date
- **THEN** the system either returns a value if one was confirmed to
  exist for that fund, or raises the same "no value available" error it
  raises for any other fund with no data at that date — this is expected
  behavior for a fund valuing a frozen point stock, not a defect

### Requirement: Annuity computation includes RCO contributions

The system SHALL include each RCO acquisition-era fund's contribution in
annuity computation on the same basis as every other fund held.

#### Scenario: Annuity computation includes an RCO era's contribution

- **WHEN** a `Career` holds points recorded against one of the RCO
  acquisition-era fund identifiers and its annuity (or per-fund
  breakdown) is computed as of a given date
- **THEN** the result includes that category's contribution, computed as
  points held times that category's sell value in effect on that date
  (in EUR), on the same basis as every other fund held
