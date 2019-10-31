import pytest, time, requests, re, os
import pandas as pd
from unittest.mock import call
from pandas.util.testing import assert_frame_equal, assert_series_equal

from crypto_analytics.data_source import DataSource
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
def setup_existing_file(tmp_dir):
    def setup_fn(filename, data_frame):
        filepath = os.path.join(tmp_dir, filename)
        data_frame.to_csv(filepath, index=False)
        return filepath

    return setup_fn



# DataSource tests

def test_data_source_data(init_abc):
    # get
    data_source = init_abc(DataSource)
    data_source._data = pd.DataFrame([[1, 2], [3, 4]], columns=['a', 'b'])
    # when
    result = data_source.data
    # then
    expected = pd.DataFrame([[1, 2], [3, 4]], columns=['a', 'b'])
    assert_frame_equal(result, expected)

def test_data_source_first_write(init_abc, tmp_dir):
    # given
    data_source = init_abc(DataSource)
    data_source._data = pd.DataFrame([[4, 3], [2, 1]], columns=['a', 'b'])
    filepath = os.path.join(tmp_dir, 'test_data_source_first_write.csv')
    # when
    data_source.write(filepath)
    # then
    result = pd.read_csv(filepath)
    expected = pd.DataFrame([[4, 3], [2, 1]], columns=['a', 'b'])
    assert_frame_equal(result, expected)

def test_data_source_write_existing_file(init_abc, setup_existing_file):
    # given
    existing_file_data = pd.DataFrame([[1, 2], [3, 4]], columns=['a', 'b'])
    filepath = setup_existing_file('test_data_source_write_existing_file.csv', existing_file_data)
    data_source = init_abc(DataSource)
    data_source._data = pd.DataFrame([[4, 3], [2, 1]], columns=['a', 'b'])
    # when
    data_source.write(filepath)
    # then
    result = pd.read_csv(filepath)
    expected = pd.DataFrame([[1, 2], [3, 4], [4, 3], [2, 1]], columns=['a', 'b'])
    assert_frame_equal(result, expected)

def test_data_source_validate_success(init_abc):
    # get
    data_source = init_abc(DataSource)
    data_source._data = pd.DataFrame([[1, 2], [3, 4]], columns=['a', 'b'])
    # when
    data_source.validate()
    # then
    # (no exception)
