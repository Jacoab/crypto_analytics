import pytest, time, requests, re
import pandas as pd
from unittest.mock import call
from pandas.util.testing import assert_frame_equal, assert_series_equal

from crypto_analytics.data_source import CryptoCompareOHLCV
from crypto_analytics.types import Interval
from crypto_analytics.types.symbol import Symbol, SymbolPair, CryptoCompareSymbolPairConverter, CryptoCompareSymbolPair
from crypto_analytics import utils

# mock data

cc_ohclv_success = {'Response': 'Success', 'Type': 100, 'Aggregated': False, 'Data': [{'time': 1560042540, 'close': 7906.14, 'high': 7906.45, 'low': 7903.86, 'open': 7903.86, 'volumefrom': 3.41, 'volumeto': 26958.13}, {'time': 1560042600, 'close': 7906.14, 'high': 7906.14, 'low': 7906.14, 'open': 7906.14, 'volumefrom': 0, 'volumeto': 0}], 'TimeTo': 1560042600, 'TimeFrom': 1560042540, 'FirstValueInArray': True, 'ConversionType': {'type': 'direct', 'conversionSymbol': ''}, 'RateLimit': {}, 'HasWarning': False}
cc_ohclv_success_df = pd.DataFrame([cc_ohclv_success['Data'][0]])
cc_ohclv_null_fsym_param = {'Response': 'Error', 'Message': 'fsym param is empty or null.', 'HasWarning': False, 'Type': 2, 'RateLimit': {}, 'Data': {}, 'ParamWithError': 'fsym'}
cc_ohclv_warning = {'Response': 'Warning', 'Message': 'rate limit reached.', 'Type': 100, 'Aggregated': False, 'Data': [{'time': 1560042540, 'close': 7906.14, 'high': 7906.45, 'low': 7903.86, 'open': 7903.86, 'volumefrom': 3.41, 'volumeto': 26958.13}, {'time': 1560042600, 'close': 7906.14, 'high': 7906.14, 'low': 7906.14, 'open': 7906.14, 'volumefrom': 0, 'volumeto': 0}], 'TimeTo': 1560042600, 'TimeFrom': 1560042540, 'FirstValueInArray': True, 'ConversionType': {'type': 'direct', 'conversionSymbol': ''}, 'RateLimit': {}, 'HasWarning': True}

# fixtures

@pytest.fixture(scope='function')
def mock_fetch(requests_mock, mocker):
    def setup_fn(sympair, candle_time, requests_mock_params):
        # mock symbol pair conversion
        mocker.patch.object(CryptoCompareSymbolPairConverter, 'from_pair')
        CryptoCompareSymbolPairConverter.from_pair.return_value = sympair
        # mock time function
        mocker.patch.object(time, 'time')
        time.time.return_value = candle_time
        # mock utils.console.warning function
        mocker.patch.object(utils.console, 'warning')
        # mock endpoint response
        endpoint = 'https://min-api.cryptocompare.com/data/histominute'
        requests_mock.get(endpoint, **requests_mock_params)

    return setup_fn


# fetch method tests

def test_crypto_compare_ohlcv_fetch_success(mock_fetch):
    # get
    mock_sympair = CryptoCompareSymbolPair('BTC', 'USD')
    candle_time = 1560042663.56
    mock_fetch(mock_sympair, candle_time, { 'json' : cc_ohclv_success })
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = CryptoCompareOHLCV(Interval.MINUTE, pair, 1)
    # when
    data = candles.fetch()
    # then
    expected_data = cc_ohclv_success_df
    assert_frame_equal(data, expected_data)

def test_crypto_compare_fetch_connect_timeout(mock_fetch):
    # given
    mock_sympair = CryptoCompareSymbolPair('BTC', 'USD')
    candle_time = 1560042663.56
    mock_fetch(mock_sympair, candle_time, { 'exc': requests.exceptions.ConnectTimeout })
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = CryptoCompareOHLCV(Interval.MINUTE, pair, 1)
    # when/then
    with pytest.raises(requests.exceptions.ConnectTimeout):
        data = candles.fetch()
    # then
    assert candles.data == None

def test_crypto_compare_ohlcv_fetch_null_fsym_param(mock_fetch):
    # get
    mock_sympair = CryptoCompareSymbolPair('BTC', 'USD')
    candle_time = 1560042663.56
    mock_fetch(mock_sympair, candle_time, { 'json' : cc_ohclv_null_fsym_param })
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = CryptoCompareOHLCV(Interval.MINUTE, pair, 1)
    # when/then
    error_msg_regx = re.compile('fsym param is empty or null.', re.IGNORECASE)
    with pytest.raises(Exception, match=error_msg_regx):
        data = candles.fetch()

def test_crypto_compare_ohlcv_fetch_warning(mock_fetch):
    # get
    mock_sympair = CryptoCompareSymbolPair('BTC', 'USD')
    candle_time = 1560042663.56
    mock_fetch(mock_sympair, candle_time, { 'json' : cc_ohclv_warning })
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = CryptoCompareOHLCV(Interval.MINUTE, pair, 1)
    # when
    data = candles.fetch()
    # then
    expected = [call('rate limit reached.')]
    assert utils.console.warning.call_args_list == expected


# property getter method tests

def test_crypto_compare_ohlcv_get_time():
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = CryptoCompareOHLCV(Interval.MINUTE, pair, 1)
    candles._data = cc_ohclv_success_df
    # when
    data = candles.time
    # then
    expected = cc_ohclv_success_df['time']
    assert_series_equal(data, expected)

def test_crypto_compare_ohlcv_get_open():
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = CryptoCompareOHLCV(Interval.MINUTE, pair, 1)
    candles._data = cc_ohclv_success_df
    # when
    data = candles.open
    # then
    expected = cc_ohclv_success_df['open']
    assert_series_equal(data, expected)

def test_crypto_compare_ohlcv_get_high():
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = CryptoCompareOHLCV(Interval.MINUTE, pair, 1)
    candles._data = cc_ohclv_success_df
    # when
    data = candles.high
    # then
    expected = cc_ohclv_success_df['high']
    assert_series_equal(data, expected)

def test_crypto_compare_ohlcv_get_low():
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = CryptoCompareOHLCV(Interval.MINUTE, pair, 1)
    candles._data = cc_ohclv_success_df
    # when
    data = candles.low
    # then
    expected = cc_ohclv_success_df['low']
    assert_series_equal(data, expected)

def test_crypto_compare_ohlcv_get_close():
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = CryptoCompareOHLCV(Interval.MINUTE, pair, 1)
    candles._data = cc_ohclv_success_df
    # when
    data = candles.close
    # then
    expected = cc_ohclv_success_df['close']
    assert_series_equal(data, expected)

def test_crypto_compare_ohlcv_get_volume():
    # given
    pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
    candles = CryptoCompareOHLCV(Interval.MINUTE, pair, 1)
    candles._data = cc_ohclv_success_df
    # when
    data = candles.volume
    # then
    expected = cc_ohclv_success_df['volumefrom']
    assert_series_equal(data, expected)
