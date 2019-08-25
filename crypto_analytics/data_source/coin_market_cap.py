import pandas as pd
import json
import requests
from typing import Dict, Union

from enum import Enum
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from crypto_analytics.data_source import DataSource
from crypto_analytics.types import Interval

class CoinMarketCap(DataSource):

    def __init__(self, key: str, endpoint: str):
        super().__init__()
        self.key = key
        self.endpoint = endpoint
        self.url = "https://pro-api.coinmarketcap.com/" + endpoint

        self.headers = {
            'X-CMC_PRO_API_KEY': key,
        }
        self.params: Dict[str, Union[int, str]] = {}

        self.session = Session()
        self.session.headers.update(self.headers)

    def fetch(self) -> pd.DataFrame:
        response = self.session.get(self.url, params=self.params)
        response.raise_for_status
        if response.status_code != 200:
            raise ConnectionError('Code: {}\nReason: {}'.format(response.status_code,
                                                                response.reason))

        data = response.json()
        self._data = pd.DataFrame(data['data'])
        return self.data
