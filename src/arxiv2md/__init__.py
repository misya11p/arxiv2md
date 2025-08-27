from ._api import arxiv2md

from importlib.metadata import (
    version as _version,
    PackageNotFoundError
)
try:
    __version__ = _version(__package__)
except PackageNotFoundError:
    pass
