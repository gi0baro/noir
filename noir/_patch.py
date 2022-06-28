from typing import Any

import click
import typer

from .types import ContextFilePath, ContextVar, Source

CUSTOM_TYPES = {ContextFilePath, ContextVar, Source}

_get_click_type = typer.main.get_click_type


def get_click_type(
    *, annotation: Any, parameter_info: typer.main.ParameterInfo
) -> click.ParamType:
    if annotation in CUSTOM_TYPES:
        return annotation.cli_parser()
    return _get_click_type(annotation=annotation, parameter_info=parameter_info)


typer.main.get_click_type = get_click_type
