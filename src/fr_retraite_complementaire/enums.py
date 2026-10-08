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
    - :attr:`RCO_AVANT_1979`, :attr:`RCO_1979_1996`, :attr:`RCO_1997_2012`
      value RCO (artisans' pre-RCI complementary scheme) points
      depending on when they were acquired, since RCI's 2013 creation
      permanently fixed three distinct point values for them rather than
      merging them into one rate. :attr:`NRCO` is commerçants' pre-RCI
      complementary scheme (2004-2012, aligned with RCI's rate from
      2013). :attr:`RC_CONJOINTS` and :attr:`CMP` are legacy schemes for
      commerçants' spouses, predating RCI.
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
    CMP = "cmp"
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
    NRCO = "nrco"
    RC_CONJOINTS = "rc_conjoints"
    RCI = "rci"
    RCO_1979_1996 = "rco_1979_1996"
    RCO_1997_2012 = "rco_1997_2012"
    RCO_AVANT_1979 = "rco_avant_1979"
    RESURCA = "resurca"
    RIPS = "rips"
    UNIRS = "unirs"
    UPS = "ups"

    def __str__(self) -> str:
        return str(self.value)
