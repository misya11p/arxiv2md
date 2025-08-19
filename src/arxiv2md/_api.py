from pathlib import Path
import tempfile

from ._utils import extract_arxiv_id
from ._get_source import get_source
from ._convert import tex2xml, JATSConverter


DNAME_SOURCE_ARXIV = "arxiv_source"


def arxiv2md(url: str) -> str:
    arxiv_id = extract_arxiv_id(url)

    with tempfile.TemporaryDirectory() as tmpdir:
        dpath_temp = Path(tmpdir)
        dpath_source = dpath_temp / DNAME_SOURCE_ARXIV

        get_source(arxiv_id, dpath_source)
        fpath_jats = tex2xml(dpath_source)
        converter = JATSConverter(fpath_jats)
        content_md = converter.convert_to_md()

    return content_md
