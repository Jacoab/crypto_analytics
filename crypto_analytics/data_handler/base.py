import time
import pandas as pd
from abc import ABC, abstractmethod
from typing import Mapping, Optional

from crypto_analytics.data_source import TimeSeriesDataSource
from crypto_analytics.types import MergeType
from crypto_analytics.utils.typing import RealNumber, coalesce

class DataHandler(ABC):
    """ An abstract base class for all data handlers """
    DataSourcesType = Mapping[str, TimeSeriesDataSource]

    def __init__(self, data_sources: DataSourcesType):
        """ Creates the data handler object """
        self._data = None
        self._data_sources = data_sources
        super().__init__()

    @property
    def data(self) -> Optional[pd.DataFrame]:
        return self._data

    @property
    def data_sources(self) -> DataSourcesType:
        return self._data_sources

    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """ Fetches the data from all data sources and returns the data """
        pass

    @abstractmethod
    def write(self, filepath: str):
        """ Writes the currently stored data to a file """
        pass


class ColumnMapper(DataHandler):
    """ A data handler base class that combines data sources and renames columns """
    ColumnMapType = Mapping[str, Mapping[str, str]]

    def __init__(self, data_sources: DataHandler.DataSourcesType,
                 column_map: ColumnMapType = {},
                 merge_type: MergeType = MergeType.INTERSECT):
        """ Creates the ColumnMapper data handler object """
        super().__init__(data_sources)
        self._column_map = column_map
        self._merge_type = merge_type
        self._to_time: Optional[RealNumber] = None

    def fetch(self) -> pd.DataFrame:
        """ Fetches the data from all data sources and returns the data """
        merge_how = self.merge_type.pandas()
        tmp_data = None

        # merge data sources
        for name, data_source in self.data_sources.items():
            # fetch data
            current_data = data_source.validated_fetch()
            # rename columns
            columns = self.column_map.get(name, {})
            current_data.rename(columns=columns, inplace=True)
            current_data['time'] = data_source.time
            # merge data
            if not tmp_data is None:
                tmp_data = pd.merge(tmp_data, current_data, how=merge_how,
                                    on='time', validate='one_to_one', sort=True)
            else:
                tmp_data = current_data

        self._data = tmp_data
        return self.data

    def write(self, filepath: str):
        """ Writes the currently stored data to a file """
        if self.data is None:
            raise Exception('No data to write')
        self.data.to_csv(filepath)

    @property
    def column_map(self) -> ColumnMapType:
        return self._column_map

    @property
    def merge_type(self) -> MergeType:
        return self._merge_type

    @property
    def to_time(self) -> RealNumber:
        return coalesce(self._to_time, lambda: time.time())

    @to_time.setter
    def to_time(self, to_time: RealNumber):
        for data_source in self.data_sources.values():
            if isinstance(data_source, TimeSeriesDataSource):
                data_source.to_time = to_time
        self._to_time = to_time
