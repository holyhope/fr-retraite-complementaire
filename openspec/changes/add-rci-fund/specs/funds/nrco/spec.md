## Purpose

Lets a `Career` hold and value legacy NRCO (commerçants' pre-RCI
complementary pension) points, from the scheme's effect through its 2013
absorption into RCI, so that commerçants who contributed before RCI's
creation don't lose that history when their www.info-retraite.fr export
or career ledger is imported.

## ADDED Requirements

### Requirement: NRCO fund identifier

The system SHALL expose a `Fund` identifier for the NRCO scheme, listed
by `list_funds()` / iterable via `Fund`, usable anywhere an existing fund
identifier is accepted.

#### Scenario: NRCO appears in the list of available funds

- **WHEN** a caller lists the available funds (library `list_funds()` or
  the `list-funds` CLI command)
- **THEN** the NRCO fund identifier is included in the result

#### Scenario: Points can be recorded against NRCO

- **WHEN** a caller records a point acquisition against the NRCO fund
  identifier on a `Career`
- **THEN** the acquisition is accepted (no unknown-fund error is raised)

### Requirement: NRCO historical point-value data

The system SHALL provide a historical point-value table for the NRCO
fund, covering both acquisition cost and sell value from NRCO's
confirmed earliest effective date through its continuation (at RCI's
own, "aligned" rate) after RCI's 2013 creation, as a step function over
time with the same lookup and backward-fill semantics as every other
fund's table (a date between two published values resolves to the most
recent one at or before that date; a date before the earliest published
value raises the same not-available error as other funds).

#### Scenario: Sell value lookup resolves to the value in effect

- **WHEN** the NRCO fund's sell value is requested for a date that falls
  on or after a known effective date and before the next known effective
  date
- **THEN** the value published for that earlier effective date is
  returned, converted to EUR

#### Scenario: Date before the earliest known data

- **WHEN** the NRCO fund's sell value or acquisition cost is requested
  for a date earlier than the fund's earliest known entry
- **THEN** the system raises the same "no value available" error it
  raises for any other fund in that situation

### Requirement: Annuity computation includes NRCO contributions

The system SHALL include NRCO's contribution in annuity computation on
the same basis as every other fund held.

#### Scenario: Annuity computation includes NRCO's contribution

- **WHEN** a `Career` holds points recorded against the NRCO fund and its
  annuity (or per-fund breakdown) is computed as of a given date
- **THEN** the result includes NRCO's contribution, computed as NRCO
  points held times the NRCO sell value in effect on that date (in EUR),
  on the same basis as every other fund held
