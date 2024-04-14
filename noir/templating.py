import base64
import datetime
import hashlib
import ipaddress
import json
import os
import pathlib
import random

from typing import Any, Dict, List, Optional, Tuple

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


def templater(delimiters: Tuple[str, str]):
    return Templater(
        mode=MODES.plain,
        delimiters=delimiters,
        adjust_indent=True,
        contexts=[base_ctx]
    )


def _base64encode(value: Any) -> str:
    if not isinstance(value, bytes):
        if not isinstance(value, str):
            value = str(value)
        value = value.encode("utf8")
    return base64.b64encode(value).decode("utf8")


def _base64decode(value: Any) -> str:
    if not isinstance(value, bytes):
        if not isinstance(value, str):
            value = str(value)
        value = value.encode("utf8")
    return base64.b64decode(value).decode("utf8")


def _cidr_host(prefix: str, hostnum: int) -> str:
    net = ipaddress.ip_network(prefix, strict=False)
    return str(net._address_class(int(net.network_address) + hostnum))


def _cidr_netmask(prefix: str) -> str:
    return str(ipaddress.ip_network(prefix, strict=False).netmask)


def _cidr_subnet(prefix: str, newbits: int, netnum: int) -> str:
    net = ipaddress.ip_network(prefix, strict=False)
    return str(
        net.__class__(
            (
                int(net.network_address) +
                (((int(net.hostmask) + 1) >> newbits) * netnum),
                net._prefixlen + newbits
            )
        )
    )


def _cidr_subnets(prefix: str, *newbits: int) -> List[str]:
    rv = []
    net = ipaddress.ip_network(prefix, strict=False)
    net_address = int(net.network_address)
    shift = 0
    for newbit in newbits:
        offset = (int(net.hostmask) + 1) >> newbit
        delta = 0
        if shift % offset:
            step = int(offset)
            while step < shift:
                step += offset
            delta = step - shift
            offset += delta
        new_prefixlen = net._prefixlen + newbit
        rv.append(str(net.__class__((net_address + shift + delta, new_prefixlen))))
        shift += offset
    return rv


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
        base64encode=_base64encode,
        base64decode=_base64decode,
        cidr=adict(
            host=_cidr_host,
            netmask=_cidr_netmask,
            subnet=_cidr_subnet,
            subnets=_cidr_subnets
        ),
        Path=pathlib.Path,
        indent=_indent,
        to_json=_to_json,
        to_toml=_to_toml,
        to_yaml=_to_yaml
    )


yaml.add_representer(adict, yaml.representer.Representer.represent_dict)
