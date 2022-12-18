from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, Type, TypeVar

import click

T = TypeVar("T", bound=click.ParamType)


class CLIType(ABC, Generic[T]):
    parser: Type[T]

    @classmethod
    @abstractmethod
    def cli_parser(cls) -> T:
        ...


class SourceParam(click.Path):
    def convert(self, value: Any, param: Any, ctx: Any) -> Source:
        is_path = True
        try:
            rv = super().convert(value, param, ctx)
        except click.exceptions.BadParameter:
            rv = value
            is_path = False
        return Source(rv, is_path)


class ContextFilePathParam(click.Path):
    def convert(self, value: Any, param: Any, ctx: Any) -> ContextFilePath:
        if not isinstance(value, str):
            ns, path = [], value
        else:
            elements = value.split(":")
            ns, path = elements[:-1], elements[-1]
        rv = super().convert(path, param, ctx)
        return ContextFilePath(ns, rv)


class ContextVarParam(click.types.StringParamType):
    def convert(self, value: Any, param: Any, ctx: Any) -> ContextVar:
        try:
            key, val = value.split("=")
        except Exception:
            self.fail(
                (
                    f"Invalid {self.name} format '{value}'."
                    "Supported formats: 'key=val', 'namespace:key=val'."
                ),
                param,
                ctx,
            )
        elements = key.split(":")
        ns, key = elements[:-1], elements[-1]
        return ContextVar(ns, key, val)


class Source(CLIType[SourceParam]):
    __slots__ = ['data', 'is_path']

    parser = SourceParam

    @classmethod
    def cli_parser(cls) -> SourceParam:
        return SourceParam(
            exists=True,
            file_okay=True,
            readable=True,
            resolve_path=True
        )

    def __init__(self, data: str, is_path: bool) -> None:
        self.data = Path(data) if is_path else data
        self.is_path = is_path


class ContextFilePath(CLIType[ContextFilePathParam]):
    __slots__ = ['namespaces', 'path']

    parser = ContextFilePathParam

    @classmethod
    def cli_parser(cls) -> ContextFilePathParam:
        return ContextFilePathParam(
            exists=True,
            file_okay=True,
            readable=True,
            resolve_path=True,
            allow_dash=True
        )

    def __init__(self, ns, path) -> None:
        self.namespaces = ns
        self.path = Path(path)


class ContextVar(CLIType[ContextVarParam]):
    __slots__ = ["key", "val", "namespaces"]

    parser = ContextVarParam

    @classmethod
    def cli_parser(cls) -> ContextVarParam:
        return ContextVarParam()

    def __init__(self, ns: str, key: str, val: str) -> None:
        self.key = key
        self.val = val
        self.namespaces = ns
