import pytest, requests, re, os
import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal, assert_series_equal

from crypto_analytics.data_source import OHLCVDataSource, KrakenOHLCV
from crypto_analytics.types import Interval
from crypto_analytics.types.symbol import Symbol, SymbolPair, KrakenSymbolPairConverter
from crypto_analytics import utils


# mock data

k_ohclv_dtypes = {'time': np.int64, 'open': object, 'high': object, 'low': object, 'close': object, 'vwap': object, 'volume': object, 'count': np.int64 }
k_ohclv_columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
k_ohclv_success = {'error': [], 'result': {'XXBTZUSD': [[1560123060, '7633.2', '7636.2', '7633.2', '7635.6', '7635.7', '2.23099305', 6]], 'last': 1560123060}}
k_ohclv_success_df = pd.DataFrame(k_ohclv_success['result']['XXBTZUSD'], columns=k_ohclv_columns).astype(k_ohclv_dtypes)
k_ohclv_incomplete_candle = {'error': [], 'result': {'XXBTZUSD': [[1560123060, '7633.2', '7636.2', '7633.2', '7635.6', '7635.7', '2.23099305', 6], [1560123120, '7635.6', '7635.6', '7630.5', '7633.1', '7630.6', '0.58258092', 2]], 'last': 1560123060}}
k_ohclv_incomplete_candle_df = pd.DataFrame(k_ohclv_incomplete_candle['result']['XXBTZUSD'], columns=k_ohclv_columns).astype(k_ohclv_dtypes)


# fixtures

@pytest.fixture(scope='function')
def mock_fetch(requests_mock, mocker):
    def setup_fn(sympair, candle_time, requests_mock_params):
        # mock symbol pair conversion
        mocker.patch.object(KrakenSymbolPairConverter, 'from_pair')
        KrakenSymbolPairConverter.from_pair.return_value = sympair
        # mock candle_time function
        mocker.patch.object(utils.time, 'candle_time')
        utils.time.candle_time.return_value = candle_time
        # mock endpoint response
        endpoint = 'https://api.kraken.com/0/public/OHLC'
        requests_mock.get(endpoint, **requests_mock_params)
        # mock validate method
        mocker.patch.object(KrakenOHLCV, 'validate')

    return setup_fn

@pytest.fixture(scope='function')
def mock_validate(mocker):
    # mock super validate
    mocker.patch.object(OHLCVDataSource, 'validate')

@pytest.fixture(scope='function')
def mock_prevalidate(mocker):
    # mock super validate
    mocker.patch.object(OHLCVDataSource, 'prevalidate')


# fetch method tests

def test_kraken_ohlcv_fetch_success(mock_fetch):
    # given
    candle_time = 1560123060
    mock_fetch('XXBTZUSD', candle_time, { 'json': k_ohclv_success })
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.MINUTE, pair, 1)
    # when
    data = candles.fetch()
    # then
    expected = k_ohclv_success_df
    assert_frame_equal(data, expected)

def test_kraken_ohlcv_fetch_incomplete_candle_success(mock_fetch):
    # given
    candle_time = 1560123060
    mock_fetch('XXBTZUSD', candle_time, { 'json': k_ohclv_incomplete_candle })
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.MINUTE, pair, 1)
    # when
    data = candles.fetch()
    # then
    expected = k_ohclv_incomplete_candle_df.head(1)
    assert_frame_equal(data, expected)

def test_kraken_ohlcv_fetch_connect_timeout(mock_fetch):
    # given
    candle_time = 1560123060
    mock_fetch('XXBTZUSD', candle_time, { 'exc': requests.exceptions.ConnectTimeout })
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.MINUTE, pair, 1)
    # when/then
    with pytest.raises(requests.exceptions.ConnectTimeout):
        data = candles.fetch()
    # then
    assert candles.data == None


# write method tests

def test_kraken_ohlcv_write(tmp_dir):
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.MINUTE, pair, 1)
    candles._data = k_ohclv_success_df
    filepath = os.path.join(tmp_dir, 'test_k_ohlcv_write.csv')
    # when
    candles.write(filepath)
    # then
    data = pd.read_csv(filepath, dtype=k_ohclv_dtypes)
    expected = k_ohclv_success_df
    assert_frame_equal(data, expected)


# prevalidate method tests

def test_kraken_ohlcv_prevalidate_invalid_interval(mock_prevalidate):
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV('MINUTE', pair, 2)
    # when/then
    error_msg_regx = re.compile('interval', re.IGNORECASE)
    with pytest.raises(ValueError, match=error_msg_regx):
        data = candles.prevalidate()

def test_kraken_ohlcv_prevalidate_super_call(mock_prevalidate):
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.MINUTE, pair, 2)
    # when
    data = candles.prevalidate()
    # then
    assert OHLCVDataSource.prevalidate.call_count == 1


# validate method tests

def test_kraken_ohlcv_validate_incomplete_candle(mock_validate):
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.MINUTE, pair, 2)
    candles._last_valid_time = 1560123060
    candles._data = k_ohclv_incomplete_candle_df
    # when/then
    error_msg_regx = re.compile('candle', re.IGNORECASE)
    with pytest.raises(ValueError, match=error_msg_regx):
        data = candles.validate()

def test_kraken_ohlcv_validate_super_call(mock_validate):
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.MINUTE, pair, 2)
    candles._last_valid_time = 1560123060
    candles._data = k_ohclv_success_df
    # when
    data = candles.validate()
    # then
    assert OHLCVDataSource.validate.call_count == 1

# def test_kraken_ohlcv_fetch_invalid_interval(mock_fetch):
#     # given
#     candle_time = 1560123060
#     mock_fetch('XXBTZUSD', candle_time, { 'json': k_ohclv_success })
#     pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
#     candles = KrakenOHLCV('', pair, 1)
#     # when/then
#     error_msg_regx = re.compile('interval', re.IGNORECASE)
#     with pytest.raises(ValueError, match=error_msg_regx):
#         data = candles.fetch()
#     # then
#     assert candles.data == None


# property getter method tests

def test_kraken_ohlcv_get_time():
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.MINUTE, pair, 1)
    candles._data = k_ohclv_success_df
    # when
    data = candles.time
    # then
    expected = k_ohclv_success_df['time']
    assert_series_equal(data, expected)

def test_kraken_ohlcv_get_open():
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.MINUTE, pair, 1)
    candles._data = k_ohclv_success_df
    # when
    data = candles.open
    # then
    expected = k_ohclv_success_df['open']
    assert_series_equal(data, expected)

def test_kraken_ohlcv_get_high():
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.MINUTE, pair, 1)
    candles._data = k_ohclv_success_df
    # when
    data = candles.high
    # then
    expected = k_ohclv_success_df['high']
    assert_series_equal(data, expected)

def test_kraken_ohlcv_get_low():
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.MINUTE, pair, 1)
    candles._data = k_ohclv_success_df
    # when
    data = candles.low
    # then
    expected = k_ohclv_success_df['low']
    assert_series_equal(data, expected)

def test_kraken_ohlcv_get_close():
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.MINUTE, pair, 1)
    candles._data = k_ohclv_success_df
    # when
    data = candles.close
    # then
    expected = k_ohclv_success_df['close']
    assert_series_equal(data, expected)

def test_kraken_ohlcv_get_volume():
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = KrakenOHLCV(Interval.MINUTE, pair, 1)
    candles._data = k_ohclv_success_df
    # when
    data = candles.volume
    # then
    expected = k_ohclv_success_df['volume']
    assert_series_equal(data, expected)
