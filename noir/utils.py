import copy
import os

from typing import Any, Dict, List, TypeVar, Union, overload

T = TypeVar("T")


class adict(dict):
    def __getattr__(self, key: str) -> Any:
        if key.startswith('__'):
            raise AttributeError
        return self[key]

    __getstate__ = lambda self: None
    __copy__ = lambda self: adict(self)
    __deepcopy__ = lambda self, memo: adict(copy.deepcopy(dict(self)))


@overload
def obj_to_adict(obj: Dict[str, Any]) -> adict:
    ...


@overload
def obj_to_adict(obj: List[Dict[str, Any]]) -> List[adict]:
    ...


@overload
def obj_to_adict(obj: os._Environ) -> adict:
    ...


@overload
def obj_to_adict(obj: T) -> Union[T, adict, List[adict]]:
    ...


def obj_to_adict(obj: Any) -> Any:
    if isinstance(obj, dict):
        rv = adict()
        for key, val in obj.items():
            rv[key] = obj_to_adict(val)
        return rv
    if isinstance(obj, (list, tuple)):
        rv = []
        for element in obj:
            rv.append(obj_to_adict(element))
        return rv
    return obj
