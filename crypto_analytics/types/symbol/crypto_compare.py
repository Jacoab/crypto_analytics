from typing import NamedTuple

from .base import SymbolStandard, Symbol, SymbolPair, SymbolPairConverter, SymbolPairConverterError

CryptoCompareSymbolPair = NamedTuple('CryptoCompareSymbolPair', [('fsym', str), ('tsym', str)])

class CryptoCompareSymbolPairConverter(SymbolPairConverter[CryptoCompareSymbolPair]):
    standard = SymbolStandard.CRYPTO_COMPARE
    # data from https://min-api.cryptocompare.com/documentation?key=PairMapping&cat=pairMappingMappedSymbolEndpoint
    from_symbol_map = {
        # Fiat
        Symbol.JPY: 'JPY',
        Symbol.USD: 'USD',
        # Crypto
        Symbol.BINANCE_COIN: 'BNB',
        Symbol.BITCOIN: 'BTC',
        Symbol.BITCOIN_CASH: 'BCH',
        Symbol.BITCOIN_SV: 'BSV',
        Symbol.EOS: 'EOS',
        Symbol.ETHERIUM: 'ETH',
        Symbol.LITECOIN: 'LTC',
        Symbol.TETHER: 'USDT',
        Symbol.TRON: 'TRX',
        Symbol.XRP: 'XRP',
    }

    to_symbol_map = {
        # Fiat
        'JPY': Symbol.JPY,
        'USD': Symbol.USD,
        # Crypto
        'BNB': Symbol.BINANCE_COIN,
        'BTC': Symbol.BITCOIN,
        'BCH': Symbol.BITCOIN_CASH,
        'BSV': Symbol.BITCOIN_SV,
        'EOS': Symbol.EOS,
        'ETH': Symbol.ETHERIUM,
        'LTC': Symbol.LITECOIN,
        'USDT': Symbol.TETHER,
        'TRX': Symbol.TRON,
        'XRP': Symbol.XRP,
    }


    @classmethod
    def from_pair(cls, pair: SymbolPair) -> CryptoCompareSymbolPair:
        try:
            fsym = cls.from_symbol_map[pair.fsym]
            tsym = cls.from_symbol_map[pair.tsym]
        except:
            raise SymbolPairConverterError(pair, cls.standard)
        return CryptoCompareSymbolPair(fsym, tsym)

    @classmethod
    def to_pair(cls, value: CryptoCompareSymbolPair) -> SymbolPair:
        try:
            fsym = cls.to_symbol_map[value.fsym]
            tsym = cls.to_symbol_map[value.tsym]
        except:
            raise SymbolPairConverterError(value, cls.standard)
        return SymbolPair(fsym, tsym)
