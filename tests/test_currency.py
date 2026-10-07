from decimal import Decimal

import pytest

from fr_retraite_complementaire.currency import (
    FRF_PER_EUR,
    UnsupportedCurrencyError,
    to_eur,
)


def test_eur_passthrough():
    assert to_eur("12.34", "EUR") == Decimal("12.34")


def test_frf_conversion():
    assert to_eur(FRF_PER_EUR, "FRF") == Decimal(1)


def test_ancien_franc_conversion():
    # 100 anciens francs = 1 nouveau franc = 1/FRF_PER_EUR euros
    assert to_eur(Decimal(100) * FRF_PER_EUR, "FRF (ancien)") == Decimal(1)


def test_unsupported_currency_raises():
    with pytest.raises(UnsupportedCurrencyError):
        to_eur("1", "USD")
