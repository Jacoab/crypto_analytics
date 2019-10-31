import pytest

from crypto_analytics.types import Interval

# test unix

test_unix_data = [
    (Interval.MINUTE, 60),
    (Interval.HOUR, 60*60),
    (Interval.DAY, 60*60*24),
]
@pytest.mark.parametrize("interval,expected", test_unix_data)
def test_interval_unix(interval, expected):
    # when
    unix_time = interval.unix
    # then
    assert unix_time == expected
