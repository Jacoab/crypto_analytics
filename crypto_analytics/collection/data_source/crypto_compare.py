import requests, time, math
import pandas as pd
from typing import Dict, Union

from crypto_analytics.collection.data_source import OHLCVDataSource
from crypto_analytics.types  import Interval
from crypto_analytics.types.symbol import SymbolPair, CryptoCompareSymbolPairConverter
from crypto_analytics import utils

class CryptoCompareOHLCV(OHLCVDataSource):
    endpoints = {
        Interval.MINUTE: 'data/histominute',
        Interval.HOUR: 'data/histohour',
        Interval.DAY: 'data/histoday',
    }

    def fetch(self) -> pd.DataFrame:
        endpoint = type(self).endpoints.get(self.interval)
        url = 'https://min-api.cryptocompare.com/{}'.format(endpoint)

        converted_pair = CryptoCompareSymbolPairConverter.from_pair(self.pair)
        toTs = math.floor(self.to_time)

        parameters: Dict[str, Union[int, str]] = {
            'fsym': converted_pair.fsym,
            'tsym': converted_pair.tsym,
            'limit': self.rows,
            'toTs': toTs,
        }
        response = requests.get(url, params=parameters)
        response.raise_for_status()

        data = response.json()
        self._data = pd.DataFrame(data['Data']).head(self.rows)
        return self.data

    @property
    def time(self):
        return self.data['time']

    @property
    def open(self):
        return self.data['open']

    @property
    def close(self):
        return self.data['close']

    @property
    def high(self):
        return self.data['high']

    @property
    def low(self):
        return self.data['low']

    @property
    def volume(self):
        return self.data['volumefrom']
