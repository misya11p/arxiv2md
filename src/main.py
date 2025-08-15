import tempfile
from pathlib import Path

import typer
from halo import Halo

from _get_source import get_source
from _convert import tex2xml, xml2md


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
app = typer.Typer(context_settings=CONTEXT_SETTINGS)


@app.command()
def main(
    url: str = typer.Argument(help="The URL to process"),
    fpath_output: Path = typer.Option(
        "output.md",
        "--output",
        "-o",
        help="The output file path for the Markdown file"
    ),
):
    with tempfile.TemporaryDirectory() as tmpdir:
        dpath_temp = Path(tmpdir)

        with Halo(text=f"Get source for arXiv", spinner="dots") as spinner:
            dpath_source = get_source(url, dpath_temp / "arxiv_source")
            spinner.succeed()

        with Halo(text=f"Convert to JATS XML", spinner="dots") as spinner:
            fpath_jats = tex2xml(dpath_source, dpath_temp / "arxiv_source")
            xml2md(fpath_jats, fpath_output)
            spinner.succeed()


if __name__ == "__main__":
    app()
