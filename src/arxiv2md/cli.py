import tempfile
from pathlib import Path

import typer
from halo import Halo

from ._api import DNAME_SOURCE_ARXIV
from ._utils import extract_arxiv_id
from ._get_source import get_source
from ._convert import tex2xml, JATSConverter


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
app = typer.Typer(add_completion=False, context_settings=CONTEXT_SETTINGS)


@app.command()
def cli(
    url: str = typer.Argument(help="The URL of the arXiv"),
    fpath_output: str = typer.Option(
        None,
        "--output", "-o",
        help=(
            "The path to the output Markdown file. "
            "If None, the file will be named as `arxiv_<arxiv_id>.md`."
        ),
    ),
    dpath_source: str = typer.Option(
        None,
        "--dir_source",
        help=(
            "The directory to store the source files (e.g., .tex, .xml). "
            "If None, a temporary directory will be used."
        )
    ),
):
    stdout = True if fpath_output == "-" else False
    arxiv_id = extract_arxiv_id(url)

    if not stdout:
        fpath_output = fpath_output or f"arxiv_{arxiv_id.replace('.', '-')}.md"
        fpath_output = Path(fpath_output).resolve()

        if not fpath_output.parent.exists():
            if typer.confirm(
                f"The directory `{fpath_output.parent}` does not exist. "
                "Do you want to create it?",
                default=True,
            ):
                fpath_output.parent.mkdir(parents=True)

        if not fpath_output.suffix:
            fpath_output = fpath_output.with_suffix(".md")

        if fpath_output.exists():
            if not typer.confirm(
                f"{fpath_output} already exists. "
                "Do you want to overwrite it?"
            ):
                raise typer.Exit()

    if dpath_source:
        content_md = convert_arxiv_to_md(
            dpath_source, arxiv_id, enabled_spinner=not stdout
        )
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            content_md = convert_arxiv_to_md(
                tempdir, arxiv_id, enabled_spinner=not stdout
            )

    if stdout:
        print(content_md)
    else:
        with open(fpath_output, "w", encoding="utf-8") as f:
            f.write(content_md)
        print(f"Markdown file saved to `{fpath_output}`")


def convert_arxiv_to_md(dpath_source, arxiv_id, enabled_spinner):
    dpath_source = Path(dpath_source).resolve()
    if not dpath_source.exists():
        dpath_source.mkdir(parents=True)
    dpath_source_arxiv = dpath_source / DNAME_SOURCE_ARXIV

    with Halo(
        text=f"Get source for arXiv:{arxiv_id}",
        spinner="dots",
        enabled=enabled_spinner,
    ) as spinner:
        get_source(arxiv_id, dpath_source_arxiv)
        spinner.succeed()

    with Halo(
        text=f"Convert to Markdown",
        spinner="dots",
        enabled=enabled_spinner,
    ) as spinner:
        fpath_jats = tex2xml(dpath_source_arxiv)
        converter = JATSConverter(fpath_jats)
        content_md = converter.convert_to_md()
        spinner.succeed()

    return content_md
