import copy

from typing import Any, Dict


class adict(dict):
    def __getattr__(self, key: str) -> Any:
        if key.startswith('__'):
            raise AttributeError
        return self[key]

    __getstate__ = lambda self: None
    __copy__ = lambda self: adict(self)
    __deepcopy__ = lambda self, memo: adict(copy.deepcopy(dict(self)))


def dict_to_adict(obj: Dict[str, Any]) -> adict:
    rv = adict()
    for key, val in obj.items():
        if isinstance(val, dict):
            val = dict_to_adict(val)
        rv[key] = val
    return rv
