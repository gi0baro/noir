from typing import Any, Dict


class adict(dict):
    __getattr__ = dict.__getitem__


def dict_to_adict(obj: Dict[str, Any]) -> adict:
    rv = adict()
    for key, val in obj.items():
        if isinstance(val, dict):
            val = dict_to_adict(val)
        rv[key] = val
    return rv
