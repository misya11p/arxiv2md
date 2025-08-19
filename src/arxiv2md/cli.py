from pathlib import Path

import typer

from ._utils import extract_arxiv_id
from ._api import arxiv2md_cli


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
    stdout = fpath_output == "-"
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

    content_md = arxiv2md_cli(arxiv_id, dpath_source)

    if stdout:
        print(content_md)
    else:
        with open(fpath_output, "w", encoding="utf-8") as f:
            f.write(content_md)
        print(f"Markdown file saved to `{fpath_output}`")
