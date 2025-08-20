import requests
import tarfile
import io


def get_source(arxiv_id: str, dpath_output: str) -> str:
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
