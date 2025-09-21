import re
from pathlib import Path
import tarfile
import json
from typing import Dict
from difflib import SequenceMatcher

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

    return dpath_source_arxiv, metadata


def _main_tex_score(fpath_tex, title: str) -> float:
    score = 0
    with open(fpath_tex, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith(r"\documentclass"):
                score += 20
            elif line.startswith(r"\begin{document}"):
                score += 5
            elif line.startswith(r"\title"):
                title_latex = re.sub(
                    r"[{}]", "", line[len(r"\title"):].strip()
                )
                ratio = SequenceMatcher(None, title, title_latex).ratio()
                score += 5 * ratio
            elif line.startswith(r"\maketitle"):
                score += 3
    return score

def get_main_texfile(dpath_source: Path, title: str) -> Path | None:
    tex_files = [
        (f, _main_tex_score(f, title))
        for f in dpath_source.glob("*.tex")
    ]
    tex_files = [(f, s) for f, s in tex_files if s > 0]

    if not tex_files:
        return None
    main_tex_file = max(tex_files, key=lambda x: x[1])[0]
    return main_tex_file


def concat_metadata(markdown: str, metadata: Dict) -> str:
    authors = "\n".join(
        [f"  - \"{author}\"" for author in metadata["authors"]]
    )
    frontmatter = "\n".join([
        "---",
        f"title: \"{metadata['title']}\"",
        f"arxiv_id: \"{metadata['arxiv_id']}\"",
        f"published: \"{metadata['published']}\"",
        f"authors: \n{authors}",
        "---",
        "",
    ])
    return frontmatter + markdown
