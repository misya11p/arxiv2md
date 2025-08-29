import re
from pathlib import Path
import tarfile
import json

import arxiv


DNAME_SOURCE_ARXIV = "source_arxiv_{arxiv_id}"
FNAME_METADATA = "metadata.json"


def extract_arxiv_id(url: str) -> str:
    match = re.search(r"(\d{4}\.\d{4,5})", url)
    if match:
        arxiv_id = match.group(1)
        return arxiv_id
    else:
        raise ValueError(
            f"Invalid arXiv URL: {url}. "
            "Could not extract arXiv ID."
        )


def get_source(url: str, dpath_source: Path) -> str:
    arxiv_id = extract_arxiv_id(url)
    paper = next(arxiv.Client().results(arxiv.Search(id_list=[arxiv_id])))
    fpath_source = paper.download_source(dpath_source)

    dname_source_arxiv = DNAME_SOURCE_ARXIV.format(
        arxiv_id=arxiv_id.replace('.', '-')
    )
    dpath_source_arxiv = dpath_source / dname_source_arxiv
    with tarfile.open(fpath_source, mode="r:gz") as tar:
        tar.extractall(dpath_source_arxiv)

    metadata = {
        "arxiv_id": arxiv_id,
        "title": paper.title,
        "published": paper.published.strftime("%Y-%m-%d"),
        "authors": [author.name for author in paper.authors],
    }
    with open(dpath_source / FNAME_METADATA, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return dpath_source_arxiv


def get_main_texfile(dpath_source: Path) -> Path:
    tex_files = list(dpath_source.glob("*.tex"))
    for fpath in tex_files:
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith(r"\documentclass"):
                    return fpath
    else:
        raise FileNotFoundError("No .tex files found in the source directory.")
