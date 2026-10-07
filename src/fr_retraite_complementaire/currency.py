"""Currency normalization helpers.

Historical Agirc-Arrco and affiliated-fund data spans three monetary
regimes:

- ``EUR`` -- euros, used since the Jan 1st, 2002 changeover (some tables
  express the pre-2002 "fixed conversion" period from 1999 onward too).
- ``FRF`` -- "nouveau franc" (new French franc), 1960-2001. Converted to
  EUR using the official, legally fixed conversion rate.
- ``FRF (ancien)`` -- "ancien franc" (old French franc), used before the
  January 1st, 1960 redenomination, where 1 nouveau franc = 100 anciens
  francs.

All monetary amounts in this package are normalized to EUR for
computation, using :func:`to_eur`.
"""

from __future__ import annotations

from decimal import Decimal

from .enums import Currency

# Official, legally fixed conversion rate between the French franc and
# the euro, in effect since January 1st, 1999 (irrevocably fixed).
FRF_PER_EUR = Decimal("6.55957")

# The 1960 redenomination: 1 nouveau franc = 100 anciens francs.
ANCIEN_FRANCS_PER_NOUVEAU_FRANC = Decimal(100)


class UnsupportedCurrencyError(ValueError):
    """Raised when a currency code is not recognized."""


def to_eur(amount: Decimal | float | str, currency: Currency | str) -> Decimal:
    """Convert ``amount`` expressed in ``currency`` to euros.

    :param amount: the amount to convert.
    :param currency: a :class:`Currency` member, or its raw string value
        (``"EUR"``, ``"FRF"``, or ``"FRF (ancien)"``).
    :raises UnsupportedCurrencyError: if ``currency`` is not recognized.
    """
    value = Decimal(str(amount))

    try:
        resolved = currency if isinstance(currency, Currency) else Currency(currency.strip())
    except ValueError as exc:
        supported = ", ".join(c.value for c in Currency)
        raise UnsupportedCurrencyError(
            f"Unsupported currency {currency!r}; expected one of {supported}"
        ) from exc

    if resolved is Currency.EUR:
        return value
    if resolved is Currency.FRF:
        return value / FRF_PER_EUR
    if resolved is Currency.FRF_ANCIEN:
        nouveau_francs = value / ANCIEN_FRANCS_PER_NOUVEAU_FRANC
        return nouveau_francs / FRF_PER_EUR

    raise AssertionError(f"unhandled currency {resolved!r}")  # pragma: no cover
