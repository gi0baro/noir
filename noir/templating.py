import base64
import datetime
import hashlib
import json
import os
import random

from typing import Any, Dict, Optional

import tomli_w
import yaml

from renoir.apis import Renoir, ESCAPES, MODES
from renoir.writers import Writer as _Writer

from .utils import adict, obj_to_adict


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
    return tomli_w.dumps(obj)


def _to_yaml(obj: Any) -> str:
    return yaml.dump(obj)


def base_ctx(ctx: Dict[str, Any]):
    ctx.update(
        base64=base64,
        datetime=datetime,
        hashlib=hashlib,
        random=random,
        env=obj_to_adict(os.environ),
        indent=_indent,
        to_json=_to_json,
        to_toml=_to_toml,
        to_yaml=_to_yaml
    )


yaml.add_representer(adict, yaml.representer.Representer.represent_dict)
templater = Templater(mode=MODES.plain, adjust_indent=True, contexts=[base_ctx])
