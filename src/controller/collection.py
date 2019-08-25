from crypto_analytics.types import Interval
from crypto_analytics.data_source import CryptoCompareOHLCV, KrakenOHLCV
from crypto_analytics.controller import CollectionController
from crypto_analytics.types.symbol import Symbol, SymbolPair

btcusd_pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
ltcusd_pair = SymbolPair(Symbol.LITECOIN, Symbol.USD)
ethusd_pair = SymbolPair(Symbol.ETHERIUM, Symbol.USD)
interval = Interval.MINUTE
redundancy = 2

data_sources = {
    'crypto_compare_ohlcv_btcusd': CryptoCompareOHLCV(interval, btcusd_pair),
    'kraken_ohlcv_btcusd': KrakenOHLCV(interval, btcusd_pair),
    'crypto_compare_ohlcv_ltcusd': CryptoCompareOHLCV(interval, ltcusd_pair),
    'kraken_ohlcv_ltcusd': KrakenOHLCV(interval, ltcusd_pair),
    'crypto_compare_ohlcv_ethusd': CryptoCompareOHLCV(interval, ethusd_pair),
    'kraken_ohlcv_ethusd': KrakenOHLCV(interval, ethusd_pair),
}

collection_controller = CollectionController(data_sources, redundancy)
collection_controller.run()
