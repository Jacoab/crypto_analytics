"""
Contains symbol, symbol standard, and symbol pair definitions as well as
an abstract base class for symbol pair converters.
"""
from abc import ABCMeta, abstractmethod
from typing import NamedTuple, Any, TypeVar, Generic
from enum import Enum

class Symbol(Enum):
    # Fiat (ISO 4217)
    JPY = 'JPY'
    USD = 'USD'
    # Crypto (full name in UPPER_CASE, until we have an official standard)
    BINANCE_COIN = 'BINANCE_COIN'
    BITCOIN = 'BITCOIN'
    BITCOIN_CASH = 'BITCOIN_CASH'
    BITCOIN_SV = 'BITCOIN_SV'
    EOS = 'EOS'
    ETHERIUM = 'ETHERIUM'
    LITECOIN = 'LITECOIN'
    TETHER = 'TETHER'
    TRON = 'TRON'
    XRP = 'XRP'


class SymbolStandard(Enum):
    CRYPTO_COMPARE = 'CRYPTO_COMPARE'
    KRAKEN = 'KRAKEN'


SymbolPair = NamedTuple('SymbolPair', [('fsym', Symbol), ('tsym', Symbol)])


# used for generic in SymbolPairConverter
ConvertedType = TypeVar('ConvertedType')
class SymbolPairConverter(Generic[ConvertedType], metaclass=ABCMeta):
    standard: SymbolStandard

    @classmethod
    @abstractmethod
    def from_pair(cls, pair: SymbolPair) -> ConvertedType:
        pass

    @classmethod
    @abstractmethod
    def to_pair(cls, value: ConvertedType) -> SymbolPair:
        pass


class SymbolPairConverterError(Exception):
    def __init__(self, obj: Any, standard: SymbolStandard):
        message = 'Conversion from: {0} failed with standard {1}'.format(obj, standard)
        super().__init__(message)
        self.obj = obj
        self.standard = standard
