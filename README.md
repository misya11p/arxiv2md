# arxiv2md

A command-line tool and Python library for converting arXiv papers to Markdown format.

It retrieves the paper's source code (.tex) from an input arXiv URL and converts it to Markdown format. Note that figures and tables are ignored during conversion.

## Installation

You can install it using `pip`:

```bash
pip install arxiv2md
```

Or using `uv`:

```bash
uv tool install arxiv2md
```

## Usage

Simply provide the arXiv URL as input:

```bash
arxiv2md https://arxiv.org/abs/2401.00001
```

When using the Python library:

```python
from arxiv2md import arxiv2md

markdown = arxiv2md("https://arxiv.org/abs/2401.00001") # Markdown text
with open("output.md", "w") as f:
    f.write(markdown)
```
