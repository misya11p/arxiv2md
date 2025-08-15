from pathlib import Path
import subprocess


FNAME_XML = "_paper.xml"
FNAME_JATS = "_paper.jats.xml"
FNAME_MD = "_paper.md"


def get_main_texfile(dpath_source: Path) -> Path:
    tex_files = list(dpath_source.glob("*.tex"))
    for fpath in tex_files:
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith(r"\documentclass"):
                    return fpath
    else:
        raise FileNotFoundError("No .tex files found in the source directory.")


def tex2xml(
    dpath_source: Path,
    dpath_work: Path,
    no_images: bool = True
) -> Path:
    fpath_tex = get_main_texfile(dpath_source)
    fpath_xml = dpath_work / FNAME_XML
    fpath_jats = dpath_work / FNAME_JATS
    command_latexml = [
        "latexml",
        fpath_tex,
        f"--dest={fpath_xml}"
    ]
    command_latexmlpost = [
        "latexmlpost",
        fpath_xml,
        "--format=jats",
        f"--dest={fpath_jats}",
    ]
    if no_images:
        command_latexmlpost += [
            "--nographicimages",
            "--nodefaultresources",
            "--nopictureimages",
            "--nomathimages"
        ]

    subprocess.run(command_latexml, cwd=dpath_work)
    subprocess.run(command_latexmlpost, cwd=dpath_work)
    return fpath_jats
