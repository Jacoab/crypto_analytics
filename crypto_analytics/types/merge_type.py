""" Contains merge type definitions """
from enum import Enum

class MergeType(Enum):
    """ An enum of merge types """
    INTERSECT = 'INTERSECT'
    UNION = 'UNION'

    def pandas(self) -> str:
        """ Converts merge type to a pandas `how` parameter for using `pd.merge` """
        switch = {
            MergeType.UNION: 'outer',
            MergeType.INTERSECT: 'inner',
        }
        return switch[self]
