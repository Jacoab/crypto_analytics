""" Contains data source classes """
# base abstract classes
from crypto_analytics.data_source.base import (DataSource, TimeSeriesDataSource, OHLCDataSource, OHLCVDataSource)
# other classes
from crypto_analytics.data_source.crypto_compare import CryptoCompareOHLCV
from crypto_analytics.data_source.coin_market_cap import CoinMarketCap
from crypto_analytics.data_source.kraken import KrakenOHLCV

__all__ = ['base', 'crypto_compare', 'coin_market_cap', 'kraken']
