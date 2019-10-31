import pytest, requests, re, os
import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal, assert_series_equal

from crypto_analytics.data_source import KrakenOHLCV
from crypto_analytics.types import Interval
from crypto_analytics.types.symbol import Symbol, SymbolPair, KrakenSymbolPairConverter
from crypto_analytics import utils


# mock data

k_ohclv_dtypes = {'time': np.int64, 'open': object, 'high': object, 'low': object, 'close': object, 'vwap': object, 'volume': object, 'count': np.int64 }
k_ohclv_columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
k_ohclv_past = [[1561939200, '10752.3', '11239.0', '9900.0', '10575.9', '10540.6', '14421.98699148', 47029], [1562025600, '10578.7', '10947.3', '9666.0', '10837.3', '10264.2', '15202.33829526', 50769]]
k_ohclv_past_df = pd.DataFrame(k_ohclv_past, columns=k_ohclv_columns).astype(k_ohclv_dtypes)

# fetch method tests

def test_kraken_ohlcv_fetch_past():
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.DAY, pair, 2)
    candles.to_time = 1562197365.6
    # when
    data = candles.fetch()
    # then
    expected = k_ohclv_past_df
    # TODO: investigate why data is not consistent
    assert_frame_equal(data.astype(np.float32), expected.astype(np.float32), check_less_precise=1)

def test_kraken_ohlcv_fetch_live():
    # given
    interval = Interval.MINUTE
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(interval, pair, 2)
    # when
    data = candles.fetch()
    # then
    expected = utils.time.candle_time(interval)
    assert data['time'][1] == expected
