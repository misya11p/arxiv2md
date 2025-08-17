import tempfile
from pathlib import Path

import typer
from halo import Halo

from _api import DNAME_SOURCE
from _utils import extract_arxiv_id
from _get_source import get_source
from _convert import tex2xml, JATSConverter


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
app = typer.Typer(add_completion=False, context_settings=CONTEXT_SETTINGS)


@app.command()
def main(
    url: str = typer.Argument(help="The URL of the arXiv"),
    fpath_output: str = typer.Option(
        None,
        "--output", "-o",
        help=(
            "The path to the output Markdown file. "
            "If None, the file will be named as `arxiv_<arxiv_id>.md`."
        ),
    )
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

    with tempfile.TemporaryDirectory() as tempdir:
        dpath_temp = Path(tempdir)
        dpath_source = dpath_temp / DNAME_SOURCE

        with Halo(
            text=f"Get source for arXiv:{arxiv_id}",
            spinner="dots",
            enabled=not stdout,
        ) as spinner:
            get_source(arxiv_id, dpath_source)
            spinner.succeed()

        with Halo(
            text=f"Convert to Markdown",
            spinner="dots",
            enabled=not stdout,
        ) as spinner:
            fpath_jats = tex2xml(dpath_source)
            converter = JATSConverter(fpath_jats)
            content_md = converter.convert_to_md()
            spinner.succeed()

    if stdout:
        print(content_md)
    else:
        with open(fpath_output, "w", encoding="utf-8") as f:
            f.write(content_md)
        print(f"Markdown file saved to {fpath_output}")


if __name__ == "__main__":
    app()
