import re


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
