from pathlib import Path
import tempfile
from typing import Tuple

from ._utils import extract_arxiv_id, get_source
from ._convert import tex2xml, JATSConverter


def _core_arxiv2md_cli(arxiv_id: str, dpath_source: str) -> str:
    from halo import Halo

    dpath_source = Path(dpath_source).resolve()
    if not dpath_source.exists():
        dpath_source.mkdir(parents=True)

    with Halo(
        text=f"Get source for arXiv:{arxiv_id}",
        spinner="dots",
    ) as spinner:
        dpath_source_arxiv = get_source(arxiv_id, dpath_source)
        spinner.succeed()

    with Halo(
        text=f"Convert to Markdown",
        spinner="dots",
    ) as spinner:
        tex2xml(dpath_source_arxiv)
        converter = JATSConverter(dpath_source)
        content_md, metadata = converter.convert_to_md()
        spinner.succeed()

    return content_md, metadata


def _core_arxiv2md(arxiv_id: str, dpath_source: str) -> str:
    dpath_source = Path(dpath_source).resolve()
    if not dpath_source.exists():
        dpath_source.mkdir(parents=True)

    dpath_source_arxiv = get_source(arxiv_id, dpath_source)
    tex2xml(dpath_source_arxiv)
    converter = JATSConverter(dpath_source)
    content_md, metadata = converter.convert_to_md()

    return content_md, metadata


def arxiv2md_cli(url: str, dpath_source: str | None = None) -> str:
    arxiv_id = extract_arxiv_id(url)

    if dpath_source:
        content_md, metadata = _core_arxiv2md_cli(arxiv_id, dpath_source)
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            content_md, metadata = _core_arxiv2md_cli(arxiv_id, tempdir)

    return content_md, metadata


def arxiv2md(url: str, dpath_source: str | None = None) -> Tuple[str, dict]:
    """
    Convert an arXiv paper to Markdown.

    Args:
        url (str): The URL of the arXiv paper or the arXiv ID.
        dpath_source (str | None, optional): The directory path to store
            the source files (e.g., .tex, .xml). If None, a temporary
            directory will be used. Defaults to None.

    Returns:
        Tuple[str, dict]: A tuple containing the Markdown content and
            metadata. The metadata includes the arXiv ID, title,
            published date, and authors.
    """
    arxiv_id = extract_arxiv_id(url)

    if dpath_source:
        content_md, metadata = _core_arxiv2md(arxiv_id, dpath_source)
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            content_md, metadata = _core_arxiv2md(arxiv_id, tempdir)

    return content_md, metadata
