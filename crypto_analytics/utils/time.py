import time
from datetime import datetime
from typing import Optional

from crypto_analytics.types import Interval
from crypto_analytics.utils.typing import RealNumber, unwrap, coalesce

def candle_time(interval: Interval, timestamp: Optional[RealNumber] = None) -> int:
    """
    Returns the last completed candle time before a given timestamp
    if no timestamp is provided it will use the current time
    """
    interval_duration = interval.unix
    unwrapped_time = coalesce(timestamp, lambda: time.time())
    candel_close_time = int(unwrapped_time // interval_duration) * interval_duration
    candel_open_time = candel_close_time - interval_duration
    return candel_open_time

def format_time(timestamp: RealNumber, format: str = '%m/%d/%Y %H:%M:%S'):
    return datetime.utcfromtimestamp(timestamp).strftime(format)

def countdown(to_time: RealNumber):
    time_remaining = max(to_time - time.time(), 0)
    while time_remaining > 0:
        time_formated = format_time_remaining(time_remaining)
        print('T:', time_formated, end='\r')
        time.sleep(1)
        time_remaining = max(to_time - time.time(), 0)
    print('Time reached')

def format_time_remaining(time_remaining: RealNumber) -> str:
    hrs, rem_hr = divmod(time_remaining, 3600)
    mins, secs = divmod(rem_hr, 60)
    return '{:.0f}:{:02.0f}:{:02.0f}'.format(hrs, mins, secs)
