import json

from configparser import ConfigParser
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import tomlkit

from yaml import SafeLoader as ymlLoader, load as ymlload


class Parsers:
    registry: Dict[str, Callable[[str], Dict[str, Any]]] = {}

    @classmethod
    def register(cls, name: str):
        def wrap(f: Callable[[str], Dict[str, Any]]) -> Callable[[str], Dict[str, Any]]:
            cls.registry[name] = f
            return f
        return wrap


class INIParser(ConfigParser):
    def read_string(self, *args, **kwargs):
        super().read_string(*args, **kwargs)
        return self

    def as_dict(self) -> Dict[str, Any]:
        rv = dict(self._sections)
        for key in rv.keys():
            rv[key] = dict(self._defaults, **rv[key])
            rv[key].pop('__name__', None)
        return rv


class UnsupportedFormat(Exception):
    pass


@Parsers.register("env")
def parse_env(data: str) -> Dict[str, Any]:
    return dict(
        (k.lower(), v) for k, v in filter(
            lambda l: len(l) == 2, (
                list(map(str.strip, line.split('=', 1))) for line in data.split("\n")
            )
        )
    )


@Parsers.register("ini")
def parse_ini(data: str) -> Dict[str, Any]:
    return INIParser().read_string(data).as_dict()


@Parsers.register("json")
def parse_json(data: str) -> Dict[str, Any]:
    return json.loads(data)


@Parsers.register("toml")
def parse_toml(data: str) -> Dict[str, Any]:
    return tomlkit.loads(data)


@Parsers.register("yaml")
@Parsers.register("yml")
def parse_yaml(data: str) -> Dict[str, Any]:
    return ymlload(data, Loader=ymlLoader)


def load_context_file(file_path: Path, format: Optional[str] = None):
    try:
        parser = Parsers.registry[format or file_path.suffix[1:] or "env"]
    except KeyError:
        raise UnsupportedFormat()

    with file_path.open("r") as f:
        data = f.read()
    return parser(data)
