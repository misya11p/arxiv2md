from ._api import arxiv2md

import importlib.metadata
try:
    __version__ = importlib.metadata.version(__package__)
except importlib.metadata.PackageNotFoundError:
    pass
