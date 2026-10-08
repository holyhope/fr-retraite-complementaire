## Purpose

Lets a `Career` hold and value legacy "RC" (régime des conjoints de
commerçants) points — a complementary pension scheme for commerçants'
spouses that predates RCI — so that spouses who hold such points don't
lose that history when their www.info-retraite.fr export or career
ledger is imported.

## Requirements

### Requirement: RC-conjoints fund identifier

The system SHALL expose a `Fund` identifier for the RC-conjoints scheme,
listed by `list_funds()` / iterable via `Fund`, usable anywhere an
existing fund identifier is accepted.

#### Scenario: RC-conjoints appears in the list of available funds

- **WHEN** a caller lists the available funds (library `list_funds()` or
  the `list-funds` CLI command)
- **THEN** the RC-conjoints fund identifier is included in the result

#### Scenario: Points can be recorded against RC-conjoints

- **WHEN** a caller records a point acquisition against the RC-conjoints
  fund identifier on a `Career`
- **THEN** the acquisition is accepted (no unknown-fund error is raised)

### Requirement: RC-conjoints historical sell-value data

The system SHALL provide a historical sell-value table ("valeur de
service du point") for the RC-conjoints fund, as a step function over
time with the same lookup and backward-fill semantics as every other
fund's table (a date between two published values resolves to the most
recent one at or before that date; a date before the earliest published
value raises the same not-available error as other funds). Because
RC-conjoints values a frozen stock of already-acquired points, this fund
is not required to provide an acquisition cost; a request for
acquisition cost MAY raise the same not-available error for every date.

#### Scenario: Sell value lookup resolves to the value in effect

- **WHEN** the RC-conjoints fund's sell value is requested for a date
  that falls on or after a known effective date and before the next
  known effective date
- **THEN** the value published for that earlier effective date is
  returned, converted to EUR

#### Scenario: Date before the earliest known data

- **WHEN** the RC-conjoints fund's sell value is requested for a date
  earlier than the fund's earliest known entry
- **THEN** the system raises the same "no value available" error it
  raises for any other fund in that situation

### Requirement: Annuity computation includes RC-conjoints contributions

The system SHALL include the RC-conjoints fund's contribution in annuity
computation on the same basis as every other fund held.

#### Scenario: Annuity computation includes RC-conjoints' contribution

- **WHEN** a `Career` holds points recorded against the RC-conjoints fund
  and its annuity (or per-fund breakdown) is computed as of a given date
- **THEN** the result includes RC-conjoints' contribution, computed as
  points held times the RC-conjoints sell value in effect on that date
  (in EUR), on the same basis as every other fund held
