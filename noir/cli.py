from pathlib import Path
from typing import List, Optional

import click
import crashtest.inspector

from .__version__ import __version__
from ._patch import typer
from .ctx import ContextExt, load_context_file
from .templating import templater
from .types import ContextFilePath, ContextVar, Source
from .utils import obj_to_adict


class CLIException(click.ClickException):
    def _render_exc(self):
        inspector = crashtest.inspector.Inspector(self.message)

        typer.secho("Encountered error during rendering", fg="red")
        typer.echo(" "*2 + f"{inspector.exception_name}: {inspector.exception_message}")

        if not inspector.frames:
            return
        frame = inspector.frames[-1]

        typer.echo(" " * 2 + f"File {frame.filename}, line {frame.lineno}")
        typer.echo(" " * 4 + frame.file_content.split("\n")[frame.lineno - 1])

    def show(self, file=None):
        if isinstance(self.message, Exception):
            self._render_exc()
        else:
            typer.secho(str(self.message), fg="red")


app = typer.Typer(name="noir", context_settings={"ignore_unknown_options": True})


def version_callback(value: bool):
    if value:
        typer.echo(f"{app.info.name} {__version__}")
        raise typer.Exit()


def error(msg: str):
    typer.secho(msg, fg="red")
    raise typer.Exit(1)


@app.command()
def main(
    source: Source = typer.Argument(
        ...,
        help="The template file to use."
    ),
    context: List[ContextFilePath] = typer.Option(
        [],
        "--context",
        "-c",
        help="Context file(s) to use."
    ),
    eval: bool = typer.Option(
        False,
        "--eval",
        "-e",
        help="Parse source as template string."
    ),
    format: Optional[ContextExt] = typer.Option(
        None,
        "--format",
        "-f",
        help="Context file format (default: guess from file extension)."
    ),
    output: typer.FileTextWrite = typer.Option(
        "-",
        "--output",
        "-o",
        show_default=False,
        help="Target output (default: stdout)"
    ),
    var: List[ContextVar] = typer.Option(
        [],
        "--var",
        "-v",
        help="Context variable(s) to apply."
    ),
    _: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True,
        help="Show the version and exit."
    )
):
    """
    Render a SOURCE template file using specified contexts and vars.
    """

    if not source.is_path and not eval:
        error(f"Invalid value for 'SOURCE': Path '{source.data}' does not exist.")
    stream_reader = lambda: typer.get_text_stream("stdin")
    tctx = {}
    for ctx_path in context:
        try:
            data = load_context_file(ctx_path.path, stream_reader, format=format)
        except Exception:
            error(f"Cannot load context file @ {ctx_path.path}")
        rctx = tctx
        for ns in ctx_path.namespaces:
            rctx[ns] = rctx.get(ns) or {}
            rctx = rctx[ns]
        rctx.update(data)
    for var_param in var:
        rctx = tctx
        for ns in var_param.namespaces:
            rctx[ns] = rctx.get(ns) or {}
            rctx = rctx[ns]
        rctx[var_param.key] = var_param.val
    try:
        rendered = (
            templater.render(source.data, obj_to_adict(tctx)) if not eval else
            templater._render(source.data, context=obj_to_adict(tctx))
        )
    except Exception as e:
        raise CLIException(e)
    output.write(rendered)


if __name__ == "__main__":
    app(prog_name="noir")
