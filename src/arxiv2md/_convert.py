from pathlib import Path
import subprocess
import re

from bs4 import BeautifulSoup, NavigableString

from ._utils import get_main_texfile


FNAME_XML = "paper.xml"
FNAME_JATS = "paper.jats.xml"


def tex2xml(dpath_source: Path, title: str, verbose: bool) -> Path:
    dpath_work = dpath_source.parent
    fpath_xml = dpath_work / FNAME_XML
    fpath_jats = dpath_work / FNAME_JATS

    result = subprocess.run(
        ["which", "latexml"],
        capture_output=True,
        text=True,
    )
    if not result.stdout.strip():
        raise FileNotFoundError(
            "Could not find the `latexml` command. Please refer to "
            "this guide for installing LaTeXML: "
            "https://github.com/misya11p/arxiv2md"
        )

    fpath_tex = get_main_texfile(dpath_source, title)
    if not fpath_tex:
        raise FileNotFoundError(f"Could not find the main .tex file")

    command_latexml = [
        "latexml",
        fpath_tex,
        f"--dest={fpath_xml}"
    ]
    command_latexmlpost = [
        "latexmlpost",
        fpath_xml,
        "--format=jats",
        "--nographicimages",
        "--nodefaultresources",
        "--nopictureimages",
        "--nomathimages",
        f"--dest={fpath_jats}",
    ]
    subprocess_options = {
        "cwd": dpath_work,
        "stdout": None if verbose else subprocess.DEVNULL,
        "stderr": None if verbose else subprocess.DEVNULL,
    }
    subprocess.run(command_latexml, **subprocess_options)
    subprocess.run(command_latexmlpost, **subprocess_options)
    return fpath_jats


# ======================================================================
# The following was primarily written by Claude code, with minor
# modifications made by the developer


class JATSConverter:
    def __init__(self, dpath_source: Path):
        fpath_jats = dpath_source / FNAME_JATS
        with open(fpath_jats, "r", encoding="utf-8") as f:
            content = f.read()
        self.soup = BeautifulSoup(content, "xml")
        self._clear()

    def _clear(self):
        self.ref_counter = 0
        self.references = {}
        self.output = []

    def convert_to_md(self):
        self._clear()

        self._extract_title()
        self._extract_abstract()
        self._extract_body()
        self._extract_references()
        self._format_references()

        markdown_content = "\n".join(self.output)
        if markdown_content[-1] != "\n":
            markdown_content += "\n"

        return markdown_content

    @staticmethod
    def _clean_text(text):
        if not text:
            return ""
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\[\[(\^.*?)\]\]", r"[\1]", text)
        return text

    @staticmethod
    def _clean_bibid(bibid):
        return bibid.replace("bib.bib", "")

    @staticmethod
    def _clean_fnid(fn_id):
        return fn_id.replace("id", "fn")

    def _extract_title(self):
        title = self.soup.find("article-title")
        if title:
            self.output.append(f"# {self._clean_text(title.get_text())}\n")

    def _extract_abstract(self):
        abstract = self.soup.find("abstract")
        if abstract:
            self.output.append("## Abstract\n")
            for p in abstract.find_all("p"):
                self.output.append(self._process_paragraph(p))
            self.output.append("")

    def _extract_body(self):
        body = self.soup.find("body")
        if body:
            for section in body.find_all("sec", recursive=False):
                self._process_section(section, level=2)

    def _extract_references(self):
        ref_list = self.soup.find("ref-list")
        if not ref_list:
            return None

        for ref in ref_list.find_all("ref"):
            ref_id = ref.get("id", "")
            ref_id = self._clean_bibid(ref_id)
            citation = ref.find("mixed-citation") or ref.find("element-citation")
            if citation:
                ref_text = self._format_reference(citation)
                self.references[ref_id] = ref_text

    def _format_references(self):
        if not self.references:
            return

        self.output.append("## References\n")
        max_digit = len(max(self.references.keys(), key=len))
        for ref_id, ref_text in sorted(
            self.references.items(),
            key=lambda x: re.sub(r"\d+", lambda m: m.group(0).zfill(max_digit), x[0])
        ):
            self.output.append(f"[^{ref_id}]: {ref_text}")
        self.output.append("")

    def _process_section(self, section, level):
        title = section.find("title")
        if title:
            title_text = self._clean_text(title.get_text())
            self.output.append(f"{'#' * level} {title_text}\n")

        for child in section.children:
            if child.name == "sec":
                self._process_section(child, level + 1)
            elif child.name == "p":
                self.output.append(self._process_paragraph(child))
                self.output.append("")
            elif child.name == "fig":
                self._process_figure(child)
            elif child.name == "table-wrap":
                self._process_table(child)
            elif child.name in ["disp-formula", "disp-formula-group"]:
                self._process_formula(child)

    def _process_paragraph(self, p):
        result = []
        for child in p.children:
            if isinstance(child, NavigableString):
                result.append(str(child))
            elif child.name == "xref":
                ref_text = self._process_reference(child)
                result.append(ref_text)
            elif child.name == "italic":
                result.append(f"*{self._clean_text(child.get_text())}*")
            elif child.name == "bold":
                result.append(f"**{self._clean_text(child.get_text())}**")
            elif child.name == "inline-formula":
                math_text = self._extract_math_text(child)
                result.append(f"${math_text}$")
            elif child.name == "fn":
                result.append(self._process_footnote(child))
            else:
                result.append(self._process_mixed_content(child))

        processed_text = "".join(result)
        processed_text = re.sub(
            r"\[\[(\d+)\](?:,\s*\[(\d+)\])*\]",
            lambda m: self._fix_citation_group(m.group(0)),
            processed_text
        )
        return self._clean_text(processed_text)

    def _fix_citation_group(self, citation_text):
        numbers = re.findall(r"\d+", citation_text)
        return f"[{', '.join(numbers)}]"

    def _process_mixed_content(self, elem):
        if isinstance(elem, NavigableString):
            return str(elem)

        if elem.name == "xref":
            return self._process_reference(elem)
        elif elem.name == "italic":
            return f"*{self._clean_text(elem.get_text())}*"
        elif elem.name == "bold":
            return f"**{self._clean_text(elem.get_text())}**"
        elif elem.name == "inline-formula":
            math_text = self._extract_math_text(elem)
            return f"${math_text}$"
        else:
            return self._clean_text(elem.get_text())

    def _process_reference(self, xref):
        rid = xref.get("rid", "")
        if rid.startswith("bib.bib"): # Reference to bibliography
            rid = self._clean_bibid(rid)
            return f"[^{rid}]"
        else: # Reference to figure/table
            return xref.get_text()

    def _format_reference(self, citation):
        authors = []
        title = ""
        year = ""
        source = ""

        for person_group in citation.find_all("person-group"):
            for name in person_group.find_all("name"):
                surname = name.find("surname")
                given_names = name.find("given-names")
                if surname:
                    author_name = surname.get_text()
                    if given_names:
                        initials = "".join([n[0] + "." for n in given_names.get_text().split() if n])
                        author_name = f"{surname.get_text()}, {initials}"
                    authors.append(author_name)

        article_title = citation.find("article-title")
        if article_title:
            title = self._clean_text(article_title.get_text())

        year_elem = citation.find("year")
        if year_elem:
            year = year_elem.get_text().strip()

        source_elem = citation.find("source")
        if source_elem:
            source = self._clean_text(source_elem.get_text())

        if authors and title:
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += " et al."

            ref_parts = []
            ref_parts.append(author_str)
            if year:
                ref_parts.append(f"({year})")
            ref_parts.append(f"*{title}*")
            if source:
                ref_parts.append(source)

            return " ".join(ref_parts)

        return self._clean_text(citation.get_text())

    def _process_figure(self, fig):
        caption = fig.find("caption")
        if caption:
            caption_text = self._process_paragraph(caption.find("p"))
            self.output.append(f"Figure: {caption_text}")
            self.output.append("")

    def _process_table(self, table_wrap):
        caption = table_wrap.find("caption")
        if caption:
            caption_text = self._process_paragraph(caption.find("p"))
            self.output.append(f"Table: {caption_text}")
            self.output.append("")

    def _process_formula(self, formula):
        math_elem = formula.find("math")
        if math_elem:
            math_text = self._extract_math_text(math_elem)
            self.output.append(f"$$\n{math_text}\n$$")
            self.output.append("")

    def _process_footnote(self, fn):
        fn_id = fn.get("id", "")
        fn_id = self._clean_fnid(fn_id)
        fn_text = fn.get_text(strip=True)
        if fn_id:
            self.references[fn_id] = fn_text
            return f"[^{fn_id}]"

    def _extract_math_text(self, formula_elem):
        if not formula_elem:
            return ""

        math_elem = formula_elem.find("math")
        if not math_elem:
            math_elem = formula_elem

        alttext = math_elem.get("alttext")
        if alttext:
            alttext = self._clean_math_alttext(alttext)
            return alttext

        return "[math]"

    def _clean_math_alttext(self, alttext):
        if not alttext:
            return ""

        alttext = alttext.replace("&#10;", "")
        alttext = alttext.replace("\n", "")
        alttext = alttext.replace("%", "")
        alttext = re.sub(r"\s+", " ", alttext)
        return alttext.strip()
