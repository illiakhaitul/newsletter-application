from pathlib import Path
from docx import Document

from common.common import *
from scripts.scripts import *
from scripts.generate_header import header_core_for_display

def _replace_body(doc, mapping: dict):
    def _repl(p):
        txt = "".join(r.text for r in p.runs) or p.text or ""
        changed = False
        for k, v in mapping.items():
            t = "{{" + k + "}}"
            if t in txt:
                txt = txt.replace(t, v); changed=True
        if changed:
            for r in p.runs: r.text = ""
            (p.runs[0] if p.runs else p.add_run("")).text = txt
    for p in doc.paragraphs: _repl(p)
    for t in doc.tables: 
        for row in t.rows:
            for c in row.cells:
                for p in c.paragraphs: _repl(p)

def render_docx(template_path, out_path, mapping: dict):
    template_path, out_path = Path(template_path), Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = Document(str(template_path))
    _replace_body(doc, mapping)
    doc.save(str(out_path))
    replace_text_everywhere(out_path, mapping)

def generate_de_en_docs(header_full: str, date: str, tpl_de: str, tpl_en: str, thema: str = "", typ: str = "PI", pg: str = "MGE") -> dict:
    header_clean = header_core_for_display(header_full)

    base = {"HEADER": header_clean, "DATE": date}

    out_dir = abs_path(cfg["PATHS"]["output"]) / header_clean
    out_dir.mkdir(parents=True, exist_ok=True)

    de_docx = out_dir / f"{header_clean}_DE.docx"
    en_docx = out_dir / f"{header_clean}_EN.docx"

    render_docx(tpl_de, de_docx, base)
    render_docx(tpl_en, en_docx, base)

    de_pdf = out_dir / f"{header_clean}_DE.pdf"
    en_pdf = out_dir / f"{header_clean}_EN.pdf"

    export_pdf(de_docx, de_pdf)
    export_pdf(en_docx, en_pdf)

    return {"de": str(de_pdf), "en": str(en_pdf), "out_dir": str(out_dir)}