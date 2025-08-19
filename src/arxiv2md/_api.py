from pathlib import Path
import tempfile

from halo import Halo

from ._utils import extract_arxiv_id
from ._get_source import get_source
from ._convert import tex2xml, JATSConverter


DNAME_SOURCE_ARXIV = "arxiv_source"


def _core_arxiv2md(arxiv_id, dpath_source, enable_spinner) -> str:
    dpath_source = Path(dpath_source).resolve()
    if not dpath_source.exists():
        dpath_source.mkdir(parents=True)
    dpath_source_arxiv = dpath_source / DNAME_SOURCE_ARXIV

    if enable_spinner: # When used in CLI, spinner is enabled
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

    else:
        # When used as a library, spinner is not used.
        # `Halo` doesn't work properly in ipython, so the `enabled`
        # option won't be used.
        get_source(arxiv_id, dpath_source_arxiv)
        fpath_jats = tex2xml(dpath_source_arxiv)
        converter = JATSConverter(fpath_jats)
        content_md = converter.convert_to_md()

    return content_md


def arxiv2md(url: str, dpath_source: str | None = None) -> str:
    arxiv_id = extract_arxiv_id(url)

    if dpath_source:
        content_md = _core_arxiv2md(arxiv_id, dpath_source, False)
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            content_md = _core_arxiv2md(arxiv_id, tempdir, False)

    return content_md

def arxiv2md_cli(url: str, dpath_source: str | None = None) -> str:
    arxiv_id = extract_arxiv_id(url)

    if dpath_source:
        content_md = _core_arxiv2md(arxiv_id, dpath_source, True)
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            content_md = _core_arxiv2md(arxiv_id, tempdir, True)

    return content_md
