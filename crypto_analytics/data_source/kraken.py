import pandas as pd
import numpy as np
import requests
from typing import Dict, Union, Optional, cast

from crypto_analytics.data_source import OHLCVDataSource
from crypto_analytics.types import Interval
from crypto_analytics.types.symbol import SymbolPair, KrakenSymbolPairConverter
from crypto_analytics import utils

class KrakenOHLCV(OHLCVDataSource):
    max_rows = 719
    columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
    # TODO: define appropriate dtypes
    dtypes = {'time': np.int64, 'open': object, 'high': object, 'low': object, 'close': object, 'vwap': object, 'volume': object, 'count': np.int64 }
    interval_values = {
        Interval.MINUTE: 1,
        Interval.HOUR: 60,
        Interval.DAY: 60*24,
    }

    def __init__(self, interval: Interval, pair: SymbolPair, rows: Optional[int] = None):
        super().__init__(interval, pair, rows)
        self._last_valid_time: Optional[int] = None
        self._interval_value = type(self).interval_values.get(self.interval)
        self._converted_pair = KrakenSymbolPairConverter.from_pair(self.pair)

    def fetch(self) -> pd.DataFrame:
        # configure endpoint and parameters
        endpoint = 'https://api.kraken.com/0/public/OHLC'
        interval_duration = self.interval.unix
        candle_time = utils.time.candle_time(self.interval, self.to_time)
        since = candle_time - self.rows * interval_duration
        parameters: Dict[str, Union[int, str]] = {
            'pair': self._converted_pair,
            'interval': utils.typing.unwrap(self._interval_value),
            'since': since,
        }

        # fetch response
        response = requests.get(endpoint, params=parameters)
        response.raise_for_status()

        # parse response
        response_json = response.json()
        last_valid_time = int(response_json.get('result', {}).get('last'))
        data_array = response_json.get('result', {}).get(self._converted_pair, {})
        data = pd.DataFrame(data_array, columns=KrakenOHLCV.columns)
        if data.at[data.index[-1], 'time'] > last_valid_time:
            # remove last candle if its not complete
            data = data.drop(data.tail(1).index)
        data = data.head(self.rows)
        data = data.astype(KrakenOHLCV.dtypes)

        self._last_valid_time = last_valid_time
        self._data = data
        return self.data

    @property
    def time(self) -> pd.Series:
        return cast(pd.DataFrame, self.data)['time']

    @property
    def open(self) -> pd.Series:
        return cast(pd.DataFrame, self.data)['open']

    @property
    def close(self) -> pd.Series:
        return cast(pd.DataFrame, self.data)['close']

    @property
    def high(self) -> pd.Series:
        return cast(pd.DataFrame, self.data)['high']

    @property
    def low(self) -> pd.Series:
        return cast(pd.DataFrame, self.data)['low']

    @property
    def volume(self) -> pd.Series:
        return cast(pd.DataFrame, self.data)['volume']

    def prevalidate(self):
        super().prevalidate()
        # check if interval is allowed/not set
        if self._interval_value is None:
            allowed_intervals = list(type(self).interval_values.keys())
            message = 'The interval for {} is not valid. The interval must be one of the following: {} but is currently: {}'.format(self, allowed_intervals, self.interval)
            raise ValueError(message)

    def validate(self):
        super().validate()
        last_time_data = self.data.at[self.data.index[-1], 'time']

        if last_time_data > self._last_valid_time:
            raise ValueError('Last candle was not completed')
