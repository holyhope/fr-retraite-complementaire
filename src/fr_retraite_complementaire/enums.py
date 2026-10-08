"""Enumerations for currencies and fund identifiers.

Both are plain-string-backed enums (``str`` mixin), so existing code that
passes raw strings (e.g. ``"agirc"``, ``"EUR"``) keeps working, while
code written against this package gets IDE autocomplete and typo-safety.
"""

from __future__ import annotations

from enum import Enum


class Currency(str, Enum):
    """A currency used in the historical point-value tables."""

    EUR = "EUR"
    FRF = "FRF"
    FRF_ANCIEN = "FRF (ancien)"

    def __str__(self) -> str:
        return str(self.value)


class Fund(str, Enum):
    """Identifier for a fund with a packaged historical point-value table.

    Members correspond 1:1 with the CSV files bundled under
    ``fr_retraite_complementaire/data/funds/`` (see ``tests/test_enums.py``
    for the drift check that keeps this enum in sync with that directory).

    - :attr:`AGIRC`, :attr:`ARRCO`, :attr:`AGIRC_ARRCO` are the unified
      cross-fund tables.
    - :attr:`IRCANTEC` is a distinct complementary pension scheme (for
      non-permanent public-sector staff), not part of the Agirc-Arrco
      lineage.
    - :attr:`RCI` is a distinct complementary pension scheme (for
      self-employed workers), not part of the Agirc-Arrco lineage.
    - All other members are individual, pre-1999 Arrco-affiliated funds.
    """

    AGIRC = "agirc"
    AGIRC_ARRCO = "agirc_arrco"
    AGRR = "agrr"
    ANEP = "anep"
    ARRCO = "arrco"
    CACE = "cace"
    CAISSE_GUTENBERG = "caisse-gutenberg"
    CAMARCA = "camarca"
    CANAREP = "canarep"
    CANRAS = "canras"
    CAPRICAS = "capricas"
    CARBALAS = "carbalas"
    CARCEPT = "carcept"
    CARGSMA = "cargsma"
    CARPILIG = "carpilig"
    CBTPR = "cbtpr"
    CGIS = "cgis"
    CGRR = "cgrr"
    CIPCA = "cipca"
    CIRCO = "circo"
    CIRPS = "cirps"
    CMGRR = "cmgrr"
    CNRO = "cnro"
    CPCEAA = "cpceaa"
    CPM = "cpm"
    CPM_CONVENTION_DE_SOLIDARITE = "cpm-convention-de-solidarite"
    CRE = "cre"
    CREP = "crep"
    CREPAC = "crepac"
    CRI = "cri"
    CRIA_IRCA = "cria-irca"
    CRIP = "crip"
    CRISA = "crisa"
    CRR = "crr"
    CRR_BTP = "crr-btp"
    FNIRR = "fnirr"
    IPRICAS = "ipricas"
    IPRIS = "ipris"
    IRCACIM = "ircacim"
    IRCANTEC = "ircantec"
    IRCASUP = "ircasup"
    IRCEM_RETRAITE = "ircem-retraite"
    IRCOP_SPM = "ircop-spm"
    IREPS = "ireps"
    IRICASE = "iricase"
    IRPC = "irpc"
    IRPSIMMEC = "irpsimmec"
    IRREP = "irrep"
    ISICA = "isica"
    RCI = "rci"
    RESURCA = "resurca"
    RIPS = "rips"
    UNIRS = "unirs"
    UPS = "ups"

    def __str__(self) -> str:
        return str(self.value)
