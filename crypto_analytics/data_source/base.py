import time, os
import pandas as pd
from datetime import datetime
from abc import ABC, abstractmethod, abstractproperty
from typing import Optional

from crypto_analytics.types import Interval, SymbolPair
from crypto_analytics.utils.typing import RealNumber, coalesce, unwrap
from crypto_analytics import utils

class DataSource(ABC):
    """ An abstract base class for all data sources """

    def __init__(self):
        super().__init__()
        self._data = None

    @property
    def data(self) -> Optional[pd.DataFrame]:
        return self._data

    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        pass

    def write(self, filepath: str):
        data: pd.DataFrame = unwrap(self.data)
        if os.path.isfile(filepath):
            # concat current data if writing to an existing file
            data.to_csv(filepath, index=False, mode='a', header=False)
        else:
            data.to_csv(filepath, index=False)

    @abstractmethod
    def prevalidate(self):
        pass

    def validate(self):
        # check existance of data
        if self.data is None:
            raise ValueError('No data')
        # check type of data
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError('The data is not an instance of the pandas DataFrame type')

    def validated_fetch(self) -> pd.DataFrame:
        self.prevalidate()
        data = self.fetch()
        self.validate()
        return data



class TimeSeriesDataSource(DataSource):
    """ An abstract class for all time series data sources """
    max_rows: int

    def __init__(self, interval: Interval, rows: Optional[int] = None):
        super().__init__()
        self._interval = interval
        self._rows = coalesce(rows, type(self).max_rows)
        self._to_time: Optional[RealNumber] = None

    @property
    def interval(self) -> Interval:
        return self._interval

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def to_time(self) -> RealNumber:
        return coalesce(self._to_time, lambda: time.time())

    @to_time.setter
    def to_time(self, to_time: RealNumber):
        self._to_time = to_time

    @property
    def fetch_period(self) -> RealNumber:
        return self.interval.unix * self.rows

    def prevalidate(self):
        super().prevalidate()
        # check if rows does not excede max rows
        if self.rows > type(self).max_rows:
            raise ValueError('The number of rows for {} cannot excede {}'.format(type(self).__name__, type(self).max_rows))

    def validate(self):
        super().validate()
        # check for gaps in data
        gaps = self.time.loc[self.time.diff() != self.interval.unix]
        gaps = gaps.drop(gaps.head(1).index)
        if len(gaps.index) > 0:
            message = '{} is missing rows at indices: {}'.format(self, gaps.index.values)
            # utils.console.warning(message)
            raise ValueError(message)
        # check row count of data
        if len(self.data.index) != self.rows:
            message = '{} did not recieve the expected number of rows. Expected {} but got {}'.format(self, self.rows, len(self.data.index))
            # utils.console.warning(message)
            raise ValueError(message)

    @abstractproperty
    def time(self) -> pd.Series:
        pass


class OHLCDataSource(TimeSeriesDataSource):
    """ An abstract class for all OHLC data sources """
    def __init__(self, interval: Interval, pair: SymbolPair, rows: Optional[int] = None):
        super().__init__(interval, rows)
        self.pair = pair

    @abstractproperty
    def open(self) -> pd.Series:
        pass

    @abstractproperty
    def close(self) -> pd.Series:
        pass

    @abstractproperty
    def high(self) -> pd.Series:
        pass

    @abstractproperty
    def low(self) -> pd.Series:
        pass


class OHLCVDataSource(OHLCDataSource):
    """ An abstract class for all OHLCV data sources """

    @abstractproperty
    def volume(self) -> Optional[pd.Series]:
        pass
