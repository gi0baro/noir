from io import StringIO
from pathlib import Path
from typing import Tuple, Optional

import click
import crashtest.inspector

from .__version__ import __version__
from .ctx import Parsers, load_context_file
from .templating import templater
from .utils import dict_to_adict


class CLIException(click.ClickException):
    def _render_exc(self):
        inspector = crashtest.inspector.Inspector(self.message)

        click.secho("Encountered error during rendering.", fg="red")
        click.echo(" "*2 + f"{inspector.exception_name}: {inspector.exception_message}")

        if not inspector.frames:
            return
        frame = inspector.frames[-1]

        click.echo(" " * 2 + f"File {frame.filename}, line {frame.lineno}")
        click.echo(" " * 4 + frame.file_content.split("\n")[frame.lineno - 1])

    def show(self, file=None):
        if isinstance(self.message, Exception):
            self._render_exc()
        else:
            click.secho(str(self.message), fg="red")


def error(msg: str, ctx: click.Context):
    click.secho(msg, fg="red")
    ctx.exit(1)


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("src", type=click.Path(exists=True))
@click.option(
    "-c", "--context",
    help="Context file(s) to use.",
    multiple=True,
)
@click.option(
    "-f", "--format",
    help="Context file format (default: guess from file extension).",
    type=click.Choice(Parsers.registry.keys(), case_sensitive=False)
)
@click.option(
    "-o", "--output",
    default="-",
    help="Target output (default: stdout)",
    type=click.File("w")
)
@click.option(
    "-v", "--var",
    help="Context variable(s) to apply.",
    multiple=True
)
@click.version_option(__version__, message="%(prog)s %(version)s")
@click.pass_context
def main(
    ctx: click.Context,
    src: str,
    context: Tuple[str],
    format: Optional[str],
    output: StringIO,
    var: Tuple[str],
):
    tctx = {}
    for ctx_param in context:
        ctx_raw_ns, ctx_raw_path = (
            ctx_param.split(":", 1) if ":" in ctx_param else
            (None, ctx_param)
        )
        ctx_path = Path(ctx_raw_path).resolve()
        if not ctx_path.is_file():
            error(f"Cannot open context file '{ctx_raw_path}'.", ctx)
        try:
            data = load_context_file(ctx_path, format=format)
        except Exception:
            error(f"Cannot load context file '{ctx_raw_path}'.", ctx)
        if ctx_raw_ns:
            tctx[ctx_raw_ns] = data
        else:
            tctx.update(data)
    for var_param in var:
        try:
            k, v = var_param.split("=")
        except ValueError:
            error(
                f"Invalid var format '{var_param}'. "
                "Supported format: 'key=val', 'namespace:key=val'.",
                ctx
            )
        rctx = tctx
        nk = k.split(":")
        for element in nk[:-1]:
            rctx[element] = rctx.get(element) or {}
            rctx = rctx[element]
        rctx[nk[-1]] = v
    try:
        rendered = templater.render(Path(src).resolve(), dict_to_adict(tctx))
    except Exception as e:
        raise CLIException(e)
    output.write(rendered)


if __name__ == "__main__":
    main(prog_name="noir")
