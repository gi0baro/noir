import json
import os

from typing import Any, Dict, Optional

import tomlkit

from renoir.apis import Renoir, ESCAPES, MODES
from renoir.writers import Writer as _Writer
from yaml import dump as ymldump

from .utils import dict_to_adict


class Writer(_Writer):
    @staticmethod
    def _to_unicode(data):
        if data is None:
            return ""
        if isinstance(data, bool):
            return str(data).lower()
        return _Writer._to_unicode(data)


class Templater(Renoir):
    _writers = {**Renoir._writers, **{ESCAPES.common: Writer}}


def _indent(text: str, spaces: int = 2) -> str:
    offset = " " * spaces
    rv = f"\n{offset}".join(text.split("\n"))
    return rv


def _to_json(obj: Any, indent: Optional[int] = None) -> str:
    return json.dumps(obj, indent=indent)


def _to_toml(obj: Any) -> str:
    return tomlkit.dumps(obj)


def _to_yaml(obj: Any) -> str:
    return ymldump(obj)


def base_ctx(ctx: Dict[str, Any]):
    ctx.update(
        env=dict_to_adict(os.environ),
        indent=_indent,
        to_json=_to_json,
        to_toml=_to_toml,
        to_yaml=_to_yaml
    )


templater = Templater(mode=MODES.plain, adjust_indent=True, contexts=[base_ctx])
