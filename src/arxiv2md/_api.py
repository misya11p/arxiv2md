from pathlib import Path
import tempfile

from ._utils import extract_arxiv_id
from ._get_source import get_source
from ._convert import tex2xml, JATSConverter


DNAME_SOURCE_ARXIV = "arxiv_source"


def _core_arxiv2md_cli(arxiv_id, dpath_source) -> str:
    from halo import Halo

    dpath_source = Path(dpath_source).resolve()
    if not dpath_source.exists():
        dpath_source.mkdir(parents=True)
    dpath_source_arxiv = dpath_source / DNAME_SOURCE_ARXIV

    with Halo(
        text=f"Get source for arXiv:{arxiv_id}",
        spinner="dots",
    ) as spinner:
        get_source(arxiv_id, dpath_source_arxiv)
        spinner.succeed()

    with Halo(
        text=f"Convert to Markdown",
        spinner="dots",
    ) as spinner:
        fpath_jats = tex2xml(dpath_source_arxiv)
        converter = JATSConverter(fpath_jats)
        content_md = converter.convert_to_md()
        spinner.succeed()

    return content_md


def _core_arxiv2md(arxiv_id, dpath_source) -> str:
    dpath_source = Path(dpath_source).resolve()
    if not dpath_source.exists():
        dpath_source.mkdir(parents=True)
    dpath_source_arxiv = dpath_source / DNAME_SOURCE_ARXIV

    get_source(arxiv_id, dpath_source_arxiv)
    fpath_jats = tex2xml(dpath_source_arxiv)
    converter = JATSConverter(fpath_jats)
    content_md = converter.convert_to_md()

    return content_md


def arxiv2md_cli(url: str, dpath_source: str | None = None) -> str:
    arxiv_id = extract_arxiv_id(url)

    if dpath_source:
        content_md = _core_arxiv2md_cli(arxiv_id, dpath_source)
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            content_md = _core_arxiv2md_cli(arxiv_id, tempdir)

    return content_md


def arxiv2md(url: str, dpath_source: str | None = None) -> str:
    arxiv_id = extract_arxiv_id(url)

    if dpath_source:
        content_md = _core_arxiv2md(arxiv_id, dpath_source)
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            content_md = _core_arxiv2md(arxiv_id, tempdir)

    return content_md
