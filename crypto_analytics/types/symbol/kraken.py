from .base import (SymbolStandard, Symbol, SymbolPair, SymbolPairConverter,
    SymbolPairConverterError)

class KrakenSymbolPairConverter(SymbolPairConverter[str]):
    standard = SymbolStandard.KRAKEN
    # data from https://api.kraken.com/0/public/AssetPairs
    from_pair_map = {
        # to BITCOIN
        SymbolPair(Symbol.BITCOIN_CASH, Symbol.BITCOIN): 'BCHXBT',
        SymbolPair(Symbol.EOS, Symbol.BITCOIN): 'EOSXBT',
        SymbolPair(Symbol.ETHERIUM, Symbol.BITCOIN): 'XETHXXBT',
        SymbolPair(Symbol.LITECOIN, Symbol.BITCOIN): 'XLTCXXBT',
        SymbolPair(Symbol.XRP, Symbol.BITCOIN): 'XXRPXXBT',
        # to JPY
        SymbolPair(Symbol.BITCOIN, Symbol.JPY): 'XXBTZJPY',
        SymbolPair(Symbol.XRP, Symbol.JPY): 'XXRPZJPY',
        # to USD
        SymbolPair(Symbol.BITCOIN, Symbol.USD): 'XXBTZUSD',
        SymbolPair(Symbol.BITCOIN_CASH, Symbol.USD): 'BCHUSD',
        SymbolPair(Symbol.EOS, Symbol.USD): 'EOSUSD',
        SymbolPair(Symbol.ETHERIUM, Symbol.USD): 'XETHZUSD',
        SymbolPair(Symbol.LITECOIN, Symbol.USD): 'XLTCZUSD',
        SymbolPair(Symbol.XRP, Symbol.USD): 'XXRPZUSD',
    }

    to_pair_map = {
        # to BITCOIN
        'BCHXBT': SymbolPair(Symbol.BITCOIN_CASH, Symbol.BITCOIN),
        'EOSXBT': SymbolPair(Symbol.EOS, Symbol.BITCOIN),
        'XETHXXBT': SymbolPair(Symbol.ETHERIUM, Symbol.BITCOIN),
        'XLTCXXBT': SymbolPair(Symbol.LITECOIN, Symbol.BITCOIN),
        'XXRPXXBT': SymbolPair(Symbol.XRP, Symbol.BITCOIN),
        # to JPY
        'XXBTZJPY': SymbolPair(Symbol.BITCOIN, Symbol.JPY),
        'XXRPZJPY': SymbolPair(Symbol.XRP, Symbol.JPY),
        # to USD
        'XXBTZUSD': SymbolPair(Symbol.BITCOIN, Symbol.USD),
        'BCHUSD': SymbolPair(Symbol.BITCOIN_CASH, Symbol.USD),
        'EOSUSD': SymbolPair(Symbol.EOS, Symbol.USD),
        'XETHZUSD': SymbolPair(Symbol.ETHERIUM, Symbol.USD),
        'XLTCZUSD': SymbolPair(Symbol.LITECOIN, Symbol.USD),
        'XXRPZUSD': SymbolPair(Symbol.XRP, Symbol.USD),
    }

    @classmethod
    def from_pair(cls, pair: SymbolPair) -> str:
        try:
            result = cls.from_pair_map[pair]
        except:
            raise SymbolPairConverterError(pair, cls.standard)
        return result

    @classmethod
    def to_pair(cls, value: str) -> SymbolPair:
        try:
            result = cls.to_pair_map[value]
        except:
            raise SymbolPairConverterError(value, cls.standard)
        return result
