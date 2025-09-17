# arxiv2md

A command-line tool and Python library for converting arXiv papers to Markdown format.

It retrieves the paper's source code (.tex) from an input arXiv URL and converts it to Markdown format.

## Setup

First, you need to install `latexml`:

```bash
# For macOS
brew install latexml

# For Ubuntu
sudo apt update
sudo apt install latexml
```

Then install `arxiv2md`:

```bash
# Using pip
pip install arxiv2md

# Using uv
uv tool install arxiv2md
```

## Usage

Simply provide the arXiv URL:

```bash
arxiv2md https://arxiv.org/abs/1706.03762
```

For use from Python code:

```python
from arxiv2md import arxiv2md

markdown, metadata = arxiv2md("https://arxiv.org/abs/1706.03762")
with open("output.md", "w") as f:
    f.write(markdown)
```

Example output file: [example.md](example.md)

## Notes

- The input URL doesn't necessarily need to be the arXiv's abstract page. It will work with PDF pages or source code pages as well. Ultimately, it should work with any string containing an arXiv ID.
- Papers without provided LaTeX source code cannot be converted.
- Figures and tables will be ignored.
- Papers not using bibtex will have reference citations displayed incorrectly.
- For papers with a large number of pages, processing by latexml may take considerable time.
