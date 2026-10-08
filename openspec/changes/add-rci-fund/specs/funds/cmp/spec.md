## Purpose

Lets a `Career` hold and value legacy CMP ("compte minimum de points")
points — a complementary pension scheme for commerçants' spouses who did
not meet the matrimonial condition required for the RC-conjoints scheme
— so that spouses who hold such points don't lose that history when
their www.info-retraite.fr export or career ledger is imported.

## ADDED Requirements

### Requirement: CMP fund identifier

The system SHALL expose a `Fund` identifier for the CMP scheme, listed
by `list_funds()` / iterable via `Fund`, usable anywhere an existing fund
identifier is accepted.

#### Scenario: CMP appears in the list of available funds

- **WHEN** a caller lists the available funds (library `list_funds()` or
  the `list-funds` CLI command)
- **THEN** the CMP fund identifier is included in the result

#### Scenario: Points can be recorded against CMP

- **WHEN** a caller records a point acquisition against the CMP fund
  identifier on a `Career`
- **THEN** the acquisition is accepted (no unknown-fund error is raised)

### Requirement: CMP historical sell-value data

The system SHALL provide a historical sell-value table ("valeur de
service du point") for the CMP fund, as a step function over time with
the same lookup and backward-fill semantics as every other fund's table
(a date between two published values resolves to the most recent one at
or before that date; a date before the earliest published value raises
the same not-available error as other funds). Because CMP values a
frozen stock of already-acquired points, this fund is not required to
provide an acquisition cost; a request for acquisition cost MAY raise
the same not-available error for every date.

#### Scenario: Sell value lookup resolves to the value in effect

- **WHEN** the CMP fund's sell value is requested for a date that falls
  on or after a known effective date and before the next known effective
  date
- **THEN** the value published for that earlier effective date is
  returned, converted to EUR

#### Scenario: Date before the earliest known data

- **WHEN** the CMP fund's sell value is requested for a date earlier
  than the fund's earliest known entry
- **THEN** the system raises the same "no value available" error it
  raises for any other fund in that situation

### Requirement: Annuity computation includes CMP contributions

The system SHALL include the CMP fund's contribution in annuity
computation on the same basis as every other fund held.

#### Scenario: Annuity computation includes CMP's contribution

- **WHEN** a `Career` holds points recorded against the CMP fund and its
  annuity (or per-fund breakdown) is computed as of a given date
- **THEN** the result includes CMP's contribution, computed as points
  held times the CMP sell value in effect on that date (in EUR), on the
  same basis as every other fund held
