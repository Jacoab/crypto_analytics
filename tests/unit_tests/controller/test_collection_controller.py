import pytest, time, heapq
import pandas as pd
from unittest.mock import call

from crypto_analytics.controller import CollectionController
from crypto_analytics.data_source import CryptoCompareOHLCV, KrakenOHLCV
from crypto_analytics.types import Interval
from crypto_analytics.types.symbol import Symbol, SymbolPair, CryptoCompareSymbolPairConverter, CryptoCompareSymbolPair
from crypto_analytics import utils

# fixtures
fake_time = 1560123060

@pytest.fixture(scope='function')
def setup_controller(mocker):
    def setup_fn(sources, redundancy, cooldown):
        # mock time function
        mocker.patch.object(time, 'time')
        time.time.return_value = fake_time
        return CollectionController(sources, redundancy, cooldown)

    return setup_fn

@pytest.fixture(scope='function')
def mock_run(mocker):
    def setup_fn(sources):
        # mock countdown function
        mocker.patch.object(utils.time, 'countdown')
        # mock format_time function
        mocker.patch.object(utils.time, 'format_time')
        utils.time.format_time.return_value = '07_28_2019'
        # mock utils.console.error function
        mocker.patch.object(utils.console, 'error')
        # mock data source methods
        for source in sources.values():
            mocker.patch.object(type(source), 'validated_fetch')
            mocker.patch.object(type(source), 'write')
            mocker.patch.object(type(source), 'time')
            type(source).time = pd.Series([fake_time])
        # mock heapq.heappush so that we don't run infinitely
        mocker.patch.object(heapq, 'heappush')

    return setup_fn


# run method tests

def test_collection_controller_run_countdown_calls(setup_controller, mock_run):
    """ Tests countdown function calls in run method. """
    # given
    sources = {
        'kraken': KrakenOHLCV(Interval.MINUTE, SymbolPair(Symbol.BITCOIN, Symbol.USD), 719),
        'crypto_compare': CryptoCompareOHLCV(Interval.MINUTE, SymbolPair(Symbol.BITCOIN, Symbol.USD), 2000),
    }
    controller = setup_controller(sources, 2, 120)
    mock_run(sources)
    # when
    controller.run()
    # then
    expected = [call(1560123060.0), call(1560123180.0), call(1560144630.0), call(1560183180.0)]
    assert utils.time.countdown.call_args_list == expected

def test_collection_controller_source_validated_fetch_success_calls(setup_controller, mock_run):
    """ Tests data source validated_fetch method calls in run method. """
    # given
    sources = {
        'kraken': KrakenOHLCV(Interval.MINUTE, SymbolPair(Symbol.BITCOIN, Symbol.JPY), 719),
    }
    controller = setup_controller(sources, 3, 60)
    mock_run(sources)
    # when
    controller.run()
    # then
    expected = [call(), call(), call()]
    assert KrakenOHLCV.validated_fetch.call_args_list == expected

def test_collection_controller_source_write_sucess_calls(setup_controller, mock_run):
    """ Tests data source write method calls in run method. """
    # given
    sources = {
        'crypto_compare': CryptoCompareOHLCV(Interval.MINUTE, SymbolPair(Symbol.ETHERIUM, Symbol.USD), 2000),
    }
    controller = setup_controller(sources, 1, 180)
    mock_run(sources)
    # when
    controller.run()
    # then
    expected = [call('crypto_compare_0_07_28_2019.csv')]
    assert CryptoCompareOHLCV.write.call_args_list == expected

def test_collection_controller_source_validated_fetch_error(setup_controller, mock_run):
    """ Tests run method error messaging when data source validated_fetch method fails. """
    # given
    sources = {
        'kraken': KrakenOHLCV(Interval.MINUTE, SymbolPair(Symbol.BITCOIN, Symbol.JPY), 719),
    }
    controller = setup_controller(sources, 1, 60)
    mock_run(sources)
    error_msg = 'validated_fetch failed'
    KrakenOHLCV.validated_fetch.side_effect = Exception(error_msg)
    # when
    controller.run()
    # then
    expected = error_msg
    print(utils.console.error.call_args_list)
    assert expected in str(utils.console.error.call_args_list[0][0])

def test_collection_controller_source_write_error(setup_controller, mock_run):
    """ Tests run method error messaging when data source write method fails. """
    # given
    sources = {
        'crypto_compare': CryptoCompareOHLCV(Interval.MINUTE, SymbolPair(Symbol.ETHERIUM, Symbol.USD), 2000),
    }
    controller = setup_controller(sources, 1, 180)
    mock_run(sources)
    error_msg = 'write failed'
    CryptoCompareOHLCV.write.side_effect = Exception(error_msg)
    # when
    controller.run()
    # then
    expected = error_msg
    print(utils.console.error.call_args_list)
    assert expected in str(utils.console.error.call_args_list[0][0])

def test_collection_controller_heappush_calls(setup_controller, mock_run):
    """ Tests heappush function calls in run method. """
    # given
    sources = {
        'kraken': KrakenOHLCV(Interval.MINUTE, SymbolPair(Symbol.LITECOIN, Symbol.USD), 360),
        'crypto_compare': CryptoCompareOHLCV(Interval.MINUTE, SymbolPair(Symbol.BITCOIN, Symbol.USD), 1000),
    }
    controller = setup_controller(sources, 3, 180)
    mock_run(sources)
    # when
    controller.run()
    # then
    expected = [
        call(controller._queue, (1560144660, 0, 'kraken')),
        call(controller._queue, (1560183060, 0, 'crypto_compare')),
        call(controller._queue, (1560144660, 1, 'kraken')),
        call(controller._queue, (1560144660, 2, 'kraken')),
        call(controller._queue, (1560183060, 1, 'crypto_compare')),
        call(controller._queue, (1560183060, 2, 'crypto_compare')),
    ]
    assert heapq.heappush.call_args_list == expected


# property tests

def test_collection_controller_redundancy(setup_controller):
    """ Tests redundancy property getter method. """
    # given
    sources = {
        'kraken': KrakenOHLCV(Interval.MINUTE, SymbolPair(Symbol.LITECOIN, Symbol.USD), 360),
    }
    controller = setup_controller(sources, 3, 180)
    # when
    result = controller.redundancy
    # then
    expected = 3
    assert result == expected

def test_collection_controller_data_sources(setup_controller):
    """ Tests data_sources property getter method. """
    # given
    sources = {
        'kraken': KrakenOHLCV(Interval.MINUTE, SymbolPair(Symbol.LITECOIN, Symbol.USD), 360),
    }
    controller = setup_controller(sources, 3, 180)
    # when
    result = controller.data_sources
    # then
    expected = sources
    assert result == expected
