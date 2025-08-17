import re
from pathlib import Path


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


def get_main_texfile(dpath_source: Path) -> Path:
    tex_files = list(dpath_source.glob("*.tex"))
    for fpath in tex_files:
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith(r"\documentclass"):
                    return fpath
    else:
        raise FileNotFoundError("No .tex files found in the source directory.")
