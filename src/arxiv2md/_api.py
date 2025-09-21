from pathlib import Path
import tempfile
from typing import Tuple, Dict

from ._utils import extract_arxiv_id, get_source, concat_metadata
from ._convert import tex2xml, JATSConverter


def _core_arxiv2md_cli(
    arxiv_id: str,
    dpath_source: Path,
    verbose: bool,
) -> str:
    from halo import Halo

    with Halo(
        text=f"Get source for arXiv:{arxiv_id}",
        spinner="dots",
    ) as spinner:
        dpath_source_arxiv, metadata = get_source(arxiv_id, dpath_source)
        spinner.succeed()

    with Halo(
        text=f"Convert to Markdown",
        spinner="dots",
        enabled=not verbose,
    ) as spinner:
        if verbose:
            print("Converting to Markdown")
        tex2xml(dpath_source_arxiv, metadata["title"], verbose)
        converter = JATSConverter(dpath_source)
        content_md = converter.convert_to_md()
        spinner.succeed()

    return content_md, metadata


def _core_arxiv2md(
    arxiv_id: str,
    dpath_source: Path,
    verbose: bool
) -> Tuple[str, Dict]:
    dpath_source_arxiv, metadata = get_source(arxiv_id, dpath_source)
    tex2xml(dpath_source_arxiv, metadata["title"], verbose)
    converter = JATSConverter(dpath_source)
    content_md = converter.convert_to_md()
    return content_md, metadata


def arxiv2md_cli(
    url: str,
    dpath_source: str | Path | None,
    frontmatter: bool,
    verbose: bool,
) -> str:
    arxiv_id = extract_arxiv_id(url)

    if dpath_source:
        content_md, metadata = _core_arxiv2md_cli(
            arxiv_id, dpath_source, verbose
        )
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            dpath_source = Path(tempdir)
            content_md, metadata = _core_arxiv2md_cli(
                arxiv_id, dpath_source, verbose
            )

    if frontmatter:
        content_md = concat_metadata(content_md, metadata)

    return content_md


def arxiv2md(
    url: str,
    dpath_source: str | Path | None = None,
    frontmatter: bool = False,
    verbose: bool = False,
) -> Tuple[str, Dict]:
    """
    Convert an arXiv paper to Markdown.

    Args:
        url (str): The URL of the arXiv paper or the arXiv ID.
        dpath_source (str | None, optional): The directory path to store
            the source files (e.g., .tex, .xml). If None, a temporary
            directory will be used. Defaults to None.
        frontmatter (bool, optional): If True, the output Markdown
            will include frontmatter metadata. Defaults to True.
        verbose (bool, optional): If True, print detailed logs during
            the conversion process. Defaults to False.

    Returns:
        Tuple[str, Dict]: A tuple containing the Markdown content and
            metadata. The metadata includes the arXiv ID, title,
            published date, and authors.
    """
    arxiv_id = extract_arxiv_id(url)

    if dpath_source:
        dpath_source = Path(dpath_source).resolve()
        if dpath_source.exists():
            if len(list(dpath_source.iterdir())) >= 1:
                raise FileExistsError(
                    f"The directory `{dpath_source}` already exists "
                    "and is not empty. Please specify an empty or "
                    "non-existing directory."
                )
        else:
            dpath_source.mkdir(parents=True, exist_ok=True)
        content_md, metadata = _core_arxiv2md(
            arxiv_id, dpath_source, verbose
        )
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            dpath_source = Path(tempdir)
            content_md, metadata = _core_arxiv2md(
                arxiv_id, dpath_source, verbose
            )

    if frontmatter:
        content_md = concat_metadata(content_md, metadata)

    return content_md, metadata
