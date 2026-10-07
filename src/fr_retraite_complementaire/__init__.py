"""fr_retraite_complementaire.

Compute French Agirc-Arrco supplementary pension annuities from a
career's point history, using historical point-value data sourced from
the official Agirc-Arrco compilation document.
"""

from .career import (
    Career,
    FundBreakdownEntry,
    PointAcquisition,
    UnknownFundError,
)
from .currency import UnsupportedCurrencyError, to_eur
from .data_loader import list_funds, load_all_funds, load_fund
from .models import FundEntry, FundTable, NoValueAvailableError

__all__ = [
    "Career",
    "FundBreakdownEntry",
    "FundEntry",
    "FundTable",
    "NoValueAvailableError",
    "PointAcquisition",
    "UnknownFundError",
    "UnsupportedCurrencyError",
    "list_funds",
    "load_all_funds",
    "load_fund",
    "to_eur",
]

__version__ = "0.1.0"
