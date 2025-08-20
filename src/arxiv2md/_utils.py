import re
from pathlib import Path
import requests
import tarfile
import io


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


def get_source(url: str, dpath_output: str) -> str:
    arxiv_id = extract_arxiv_id(url)
    url_source = f"https://arxiv.org/e-print/{arxiv_id}"
    try:
        response = requests.get(url_source, timeout=30)
        response.raise_for_status()
        file_like_object = io.BytesIO(response.content)
        with tarfile.open(fileobj=file_like_object, mode="r:gz") as tar:
            tar.extractall(path=dpath_output)
        return dpath_output
    except requests.RequestException as e:
        raise RuntimeError(
            f"Failed to download source from {url_source}: {e}"
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
