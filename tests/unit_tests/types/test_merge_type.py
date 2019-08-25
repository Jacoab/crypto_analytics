import pytest

from crypto_analytics.types import MergeType

# test pandas

test_pandas_data = [
    (MergeType.UNION, 'outer'),
    (MergeType.INTERSECT, 'inner'),
]
@pytest.mark.parametrize("merge_type,expected", test_pandas_data)
def test_merge_type_pandas(merge_type, expected):
    # when
    merge_how = merge_type.pandas()
    # then
    assert merge_how == expected
