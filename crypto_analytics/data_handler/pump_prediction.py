from crypto_analytics.data_handler import ColumnMapper
from crypto_analytics.data_source import CryptoCompareOHLCV, KrakenOHLCV
from crypto_analytics.types import Interval, MergeType
from crypto_analytics.types.symbol import SymbolPair

class PumpPredictionDataHandler(ColumnMapper):
    """ A data handler used to transdorm data for pump prediction models """

    def __init__(self, pair: SymbolPair, rows: int):
        """ Creates the PumpPredictionDataHandler data handler object """
        interval = Interval.MINUTE
        merge_type = MergeType.INTERSECT
        data_sources = {
            'crypto_compare_ohlcv': CryptoCompareOHLCV(interval, pair, rows),
            'kraken_ohlcv': KrakenOHLCV(interval, pair, rows),
        }
        column_map = {
            'crypto_compare_ohlcv': {
                'time': 'time',
                'open': 'cc_open',
                'high': 'cc_high',
                'low': 'cc_low',
                'close': 'cc_close',
                'volumefrom': 'cc_volumefrom',
                'volumeto': 'cc_volumeto',
            },
            'kraken_ohlcv': {
                'time': 'time',
                'open': 'k_open',
                'high': 'k_high',
                'low': 'k_low',
                'close': 'k_close',
                'vwap': 'k_vwap',
                'volume': 'k_volume',
                'count': 'k_count',
            },
        }
        super().__init__(data_sources, column_map, merge_type)
