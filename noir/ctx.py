import json

from configparser import ConfigParser
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TextIO

import tomlkit

from typer import get_text_stream
from yaml import SafeLoader as ymlLoader, load as ymlload


class ContextExt(Enum):
    env = "env"
    ini = "ini"
    json = "json"
    toml = "toml"
    yaml = "yaml"
    yml = "yml"


class Parsers:
    registry: Dict[ContextExt, Callable[[str], Dict[str, Any]]] = {}

    @classmethod
    def register(cls, ext: ContextExt):
        def wrap(f: Callable[[str], Dict[str, Any]]) -> Callable[[str], Dict[str, Any]]:
            cls.registry[ext] = f
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


@Parsers.register(ContextExt.env)
def parse_env(data: str) -> Dict[str, Any]:
    return dict(
        (k.lower(), v) for k, v in filter(
            lambda l: len(l) == 2, (
                list(map(str.strip, line.split('=', 1))) for line in data.split("\n")
            )
        )
    )


@Parsers.register(ContextExt.ini)
def parse_ini(data: str) -> Dict[str, Any]:
    return INIParser().read_string(data).as_dict()


@Parsers.register(ContextExt.json)
def parse_json(data: str) -> Dict[str, Any]:
    return json.loads(data)


@Parsers.register(ContextExt.toml)
def parse_toml(data: str) -> Dict[str, Any]:
    return tomlkit.loads(data)


@Parsers.register(ContextExt.yaml)
@Parsers.register(ContextExt.yml)
def parse_yaml(data: str) -> Dict[str, Any]:
    return ymlload(data, Loader=ymlLoader)


def load_context_file(
    file_path: Path,
    stream_reader: Callable[[], TextIO],
    format: Optional[ContextExt] = None
):
    try:
        format = format or ContextExt[file_path.suffix[1:] or "env"]
    except KeyError:
        raise UnsupportedFormat()

    if file_path == Path("-"):
        data = stream_reader().read()
    else:
        with file_path.open("r") as f:
            data = f.read()
    return Parsers.registry[format](data)
