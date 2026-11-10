from pathlib import Path
from typing import Optional, Dict, List
from openpyxl import load_workbook
from openpyxl.styles import Alignment

def _norm(s) -> str:
    s = "" if s is None else str(s)
    return " ".join(s.replace("\xa0", " ").strip().lower().split())

class ExcelSource:
    def __init__(self, path: str | Path, sheet: Optional[str] = None):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Excel didnt found: {self.path}")
        wb = load_workbook(self.path, data_only=True, read_only=True)
        self.ws = wb[sheet] if (sheet and sheet in wb.sheetnames) else wb.active
        self.header_row, self.titles = self._find_header_row()

        self.col_header = self._find_col(lambda t: "header" in _norm(t), default=2)
        self.col_theme = self._find_col(lambda t: "thema" in _norm(t) or "theme" in _norm(t))
        self.col_month = self._find_col(lambda t: "mm" in _norm(t) and ("yyyy" in _norm(t) or "jjjj" in _norm(t)))
        self.col_pg = self._find_col(lambda t: "produkt" in _norm(t) and "gruppe" in _norm(t))
        self.col_nummer = self._find_col(lambda t: "nummer" in _norm(t))

        self.col_typ = self._find_col(
            lambda t: (("techn" in _norm(t) and "art" in _norm(t)) or 
                       "produkteinführung" in _norm(t) or 
                       "änderung" in _norm(t) or
                       "lieferinformation" in _norm(t) or
                       "abkündigung" in _norm(t))
        )

    def _find_header_row(self):
        for cells in self.ws.iter_rows(min_row=1, max_row=50):
            titles = [c.value for c in cells[:50]]
            if any("header" in _norm(v) for v in titles):
                return cells[0].row, [("" if v is None else str(v)) for v in titles]
        first = next(self.ws.iter_rows(min_row=1, max_row=1))
        return 1, [("" if c.value is None else str(c.value)) for c in first]
    
    def _find_col(self, pred, default=None) -> Optional[int]:
        for j, t in enumerate(self.titles, start=1):
            if pred(t): return j
        return default
    
    def _val(self, vals: List, col: Optional[int]) -> Optional[str]:
        if not col: return None
        if col-1 < len(vals):
            v = vals[col-1]
            return None if v in (None, "") else str(v)
        return None
    
    def list_rows(self, limit: int = 5000) -> List[Dict[str, Optional[str]]]:
        start = self.header_row + 1
        out = []
        for i, row in enumerate(self.ws.iter_rows(min_row=start, values_only=True), start=start):
            if i - start >= limit: break
            vals = list(row) if row else []

            nummer = self._val(vals, self.col_nummer) or ""
            typ = self._val(vals, self.col_typ) or ""
            produktgruppe = self._val(vals, self.col_pg) or ""
            date = self._val(vals, self.col_month) or ""

            header_val = f"AT_{nummer}_{typ}_{produktgruppe}_{date}".strip("_ ")

            out.append({
                "idx": i,
                "Header": header_val,
                "Thema": self._val(vals, self.col_theme),
                "MM.JJJJ": date,
                "Produktgruppe": produktgruppe,
            })
        return out
    
    def get_row(self, idx: int) -> Dict[str, Optional[str]]:
        cells = next(self.ws.iter_rows(min_row=idx, max_row=idx, values_only=True))
        vals = list(cells) if cells else []

        nummer = self._val(vals, self.col_nummer) or ""
        typ = self._val(vals, self.col_typ) or ""
        produktgruppe = self._val(vals, self.col_pg) or ""
        date = self._val(vals, self.col_month) or ""

        header_val = f"AT_{nummer}_{typ}_{produktgruppe}_{date}".strip("_ ")
        
        return {
            "Header": header_val,
            "Thema": self._val(vals, self.col_theme),
            "MM.JJJJ": date,
            "Produktgruppe": produktgruppe,
        }
    
    # new row
    def append_new(self, header_full: str, date_str: str, *, produktgruppe: Optional[str] = None, thema: Optional[str] = None, typ: Optional[str] = None) -> int:
        wb = load_workbook(self.path)
        ws = wb[self.ws.title]

        # find last not empty row
        r = ws.max_row
        def _row_has_values(rr: int) -> bool:
            return any((ws.cell(row=rr, column=c).value not in (None, "")) for c in range(1, ws.max_column+1))
        while r > self.header_row and not _row_has_values(r):
            r -= 1
        target = r + 1

        center = Alignment(horizontal="center")

        def setcol(col: Optional[int], val, align_center = False):
            if col:
                c = ws.cell(row=target, column=col, value=val)
                if align_center: c.alignment = center

        setcol(self.col_header, header_full)
        setcol(self.col_month, date_str, align_center=True)
        setcol(self.col_pg, produktgruppe or "")
        setcol(self.col_theme, thema or "")
        setcol(self.col_typ, (typ or ""), align_center=True)

        if self.col_nummer:
            import re
            m = re.search(r"AT_(\d{5})_", header_full or "")
            num5 = m.group(1) if m else ""
            setcol(self.col_nummer, num5, align_center=True)

        wb.save(self.path)
        wb.close()
        return target
    
    def get_number(self) -> int:
        if not self.col_header:
            return 0
        
        max_num = 0
        start = self.header_row + 1

        for cells in self.ws.iter_rows(min_row=start, values_only=True):
            if not cells:
                None

            val = cells[self.col_nummer - 1]
            if val is None:
                continue

            try:
                num = int(str(val).strip())
                if num > max_num:
                    max_num = num
            except:
                continue

        return max_num
    

