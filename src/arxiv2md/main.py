import tempfile
from pathlib import Path

import typer
from halo import Halo

from _utils import extract_arxiv_id
from _get_source import get_source
from _convert import tex2xml, xml2md


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
app = typer.Typer(add_completion=False, context_settings=CONTEXT_SETTINGS)


@app.command()
def main(
    url: str = typer.Argument(help="The URL of the arXiv"),
    fpath_output: str = typer.Option(
        None,
        "--output", "-o",
        help="The path to the output Markdown file. If None, the file will be named as `arxiv_<arxiv_id>.md`.",),
):
    arxiv_id = extract_arxiv_id(url)
    fpath_output = fpath_output or f"arxiv_{arxiv_id.replace('.', '-')}.md"
    fpath_output = Path(fpath_output).resolve()
    if fpath_output.exists():
        if not typer.confirm(f"{fpath_output} already exists. Do you want to overwrite it?"):
            raise typer.Exit()

    with tempfile.TemporaryDirectory() as tmpdir:
        dpath_temp = Path(tmpdir)
        dpath_arxiv = dpath_temp / "arxiv_source"

        with Halo(text=f"Get source for arXiv", spinner="dots") as spinner:
            dpath_source = get_source(arxiv_id, dpath_arxiv)
            spinner.succeed()

        with Halo(text=f"Convert to JATS XML", spinner="dots") as spinner:
            fpath_jats = tex2xml(dpath_source, dpath_arxiv)
            xml2md(fpath_jats, fpath_output)
            spinner.succeed()


if __name__ == "__main__":
    app()
