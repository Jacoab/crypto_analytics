from typing import Optional, TypeVar, Union, Callable, List, Any, cast

T = TypeVar('T')

RealNumber = Union[int, float]
Coalescable = Union[Callable[[], Optional[T]], Optional[T]]

def coalesce(*arg: Coalescable[T]) -> T:
    """ Returns the first non-None valued Optional or function return value in *arg """
    for element in arg:
        optional = element() if callable(element) else element
        if optional is not None:
            return cast(T, optional)
    raise ValueError('must have at least one non-None valued optional to coalesce')

def unwrap(optional: Optional[T]) -> T:
    """ Returns unwraped Optional value and raises exception if value is None """
    if optional is None:
        raise ValueError('cannot unwrap optional because its value is None')
    return cast(T, optional)
