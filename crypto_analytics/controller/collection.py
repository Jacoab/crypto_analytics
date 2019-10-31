import heapq, time, traceback
from datetime import datetime
from typing import Mapping, List, Tuple, Optional

from crypto_analytics.data_source import DataSource, TimeSeriesDataSource
from crypto_analytics.controller import Controller
from crypto_analytics.types import Interval, MergeType, SymbolPair
from crypto_analytics.utils.typing import RealNumber
from crypto_analytics import utils

QueueType = List[Tuple[RealNumber, int, str]]

class CollectionController(Controller):
    """ A controller to collect data from data sources """
    DataSourcesType = Mapping[str, TimeSeriesDataSource]

    def __init__(self, data_sources: DataSourcesType, redundancy: int = 1, cooldown: RealNumber = 120):
        """ Creates the CollectionController collection object """
        queue: QueueType = []
        for copy_id in range(redundancy):
            for i, (name, data_source) in enumerate(data_sources.items()):
                # the amount of time between redundant copy fetches
                redundancy_spacing = copy_id * (data_source.fetch_period / redundancy)
                # i * cooldown prevents us from trying to fetch things at the same time
                fetch_time = time.time() + redundancy_spacing + i * cooldown
                queue.append((fetch_time, copy_id, name))

        heapq.heapify(queue)

        self._redundancy = redundancy
        self._data_sources = data_sources
        self._queue: QueueType = queue


    @property
    def redundancy(self) -> int:
        return self._redundancy

    @property
    def data_sources(self) -> DataSourcesType:
        return self._data_sources

    def run(self):
        while len(self._queue) > 0:
            print(_format_queue(self._queue))
            # pop queue task
            fetch_time, copy_id, source_name = heapq.heappop(self._queue)
            data_source = self.data_sources[source_name]

            # wait until next fetch
            print('Time remaining before next fetch:')
            utils.time.countdown(fetch_time)

            # fetch data
            try:
                data_source.to_time = fetch_time
                data_source.validated_fetch()
            except Exception:
                message = 'Failed to fetch data for source_name: {} copy_id: {}\n{}'.format(source_name, copy_id, traceback.format_exc())
                utils.console.error(message)

            # write to file
            try:
                start_time = data_source.time[0]
                start_date = utils.time.format_time(start_time, '%Y')
                filename = '{}_{}_{}.csv'.format(source_name, copy_id, start_date)
                data_source.write(filename)
            except Exception as e:
                message = 'Failed to write data for source_name: {} copy_id: {}\n{}'.format(source_name, copy_id, traceback.format_exc())
                utils.console.error(message)

            # print diagnosis
            # print(_format_data_source_diagnosis(data_source))

            # schedule and push new task to queue
            next_fetch_time = data_source.time.tail(1).values[0] + data_source.fetch_period
            heapq.heappush(self._queue, (next_fetch_time, copy_id, source_name))


# private helper functions

# def _format_data_source_diagnosis(data_source: TimeSeriesDataSource):
#     times = data_source.time
#     start_time = times.head(1).values[0]
#     end_time = times.tail(1).values[0]
#     candle_time = utils.time.candle_time(data_source.interval, data_source.to_time)
#     start_time_str = utils.time.format_time(start_time)
#     end_time_str = utils.time.format_time(end_time)
#     candle_time_str = utils.time.format_time(candle_time)
#     to_time_str = utils.time.format_time(data_source.to_time)
#
#     formated_string = 'Data Source Diagnosis: \n'
#     formated_string += '\tstart_time: {}\n'.format(start_time_str)
#     formated_string += '\tend_time: {}\n'.format(end_time_str)
#     formated_string += '\tcandle_time: {}\n'.format(candle_time_str)
#     formated_string += '\tto_time: {}\n'.format(to_time_str)
#     return formated_string

def _format_queue(queue: QueueType) -> str:
    string = 'Priority Queue: ['
    for fetch_time, copy_id, source_name in sorted(queue):
        time_formated = utils.time.format_time(fetch_time)
        string += '\n\ttime: "{}" copy_id: {} source_name: "{}"'.format(time_formated, copy_id, source_name)
    return string + '\n]'
