from pathlib import Path
from typing import Dict
from win32com.client import DispatchEx

import pythoncom

WD_FIND_CONTINUE = 1
WD_REPLACE_ALL = 2
WD_HF_PRIMARY, WD_HF_FIRST, WD_HF_EVEN = 1, 2, 3
WD_FORMAT_PDF = 17

STORY_TYPES = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
]

def _replace_in_range(rng, mapping: Dict[str, str]):
    try:
        text = rng.Text
    except Exception:
        return
    
    original = text

    for k in mapping.keys():
        ph = "{{" + k + "}}"
        if ph in text:
            print(f"Placeholder visible in the range {ph}")

    for k, v in mapping.items():
        placeholder = "{{" + k + "}}"
        replacement = str(v)

        try:
            search = rng.Duplicate
            find = search.Find
            find.ClearFormatting()
            find.Replacement.ClearFormatting()

            find.Text = placeholder
            find.Forward = True
            find.Wrap = 0

            count = 0

            while find.Execute():
                count += 1

                try:
                    search.Text = replacement

                    if k == "HEADER":
                        try:
                            search.Font.Bold = True
                        except Exception as e:
                            print(f"Failed to make bold: {e}")

                except Exception as e:
                    print(f"Failed tom write replacement {e}")

                try:
                    search.Collapse(0)
                except Exception:
                    break

                find = search.Find
                find.ClearFormatting()
                find.Replacement.ClearFormatting()
                find.Text = placeholder
                find.Forward = True
                find.Wrap = 0
            
            """ if count > 0:
                print(f"Replaced {placeholder} - {replacement}")
            else:
                print(f"Not found {placeholder}") """

        except Exception as e:
            print(f"Error placing {placeholder}: {e}")

def _iter_story_ranges(doc):
    for story_type in STORY_TYPES:
        try:
            rng = doc.StoryRanges(story_type)
        except Exception:
            continue
            
        while rng is not None:
            yield rng
            try:
                rng = rng.NextStoryRange
            except Exception:
                break

def _iter_shapes(doc):
    for s in list(getattr(doc, "Shapes", []) or []):
        yield s

    for sec in list(getattr(doc, "Sections", []) or []):
        for coll in (sec.Headers(WD_HF_PRIMARY) , sec.Headers(WD_HF_FIRST),
                     sec.Headers(WD_HF_EVEN), sec.Footers(WD_HF_PRIMARY),
                     sec.Footers(WD_HF_FIRST), sec.Footers(WD_HF_EVEN)):
            try:
                for s in coll.Shapes: yield s
            except Exception:
                continue

def replace_text_everywhere(docx_path: str | Path, mapping: Dict[str, str]):
    pythoncom.CoInitialize()
    app = None

    try:
        app = DispatchEx("Word.Application")
        app.Visible = False
        doc = app.Documents.Open(str(docx_path))

        for rng in _iter_story_ranges(doc):
            _replace_in_range(rng, mapping)

        for s in _iter_shapes(doc):
            try:
                tf = s.TextFrame
                if tf.HasText:
                    _replace_in_range(tf.TextRange, mapping)
            except Exception:
                pass

        doc.Save(); doc.Close(False)
    finally:
        if app:
            try: app.Quit()
            except Exception: pass

        pythoncom.CoUninitialize()

def export_pdf(docx_path: str | Path, pdf_path: str | Path):
    pythoncom.CoInitialize()

    app = None

    try:
        app = DispatchEx("Word.Application")
        app.Visible = False

        doc = app.Documents.Open(str(docx_path))

        doc.SaveAs2(str(pdf_path), FileFormat=WD_FORMAT_PDF)

        doc.Close(False)

    finally:
        if app: 
            try:
                app.Quit()
            except Exception:
                pass
        
        pythoncom.CoUninitialize()