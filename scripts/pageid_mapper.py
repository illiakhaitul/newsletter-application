from dataclasses import dataclass
from openpyxl import load_workbook
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
import csv

# data model
@dataclass
class ProductRow:
    uid: str
    language: str
    id3: str
    name4: str
    id5: str
    name6: str
    id7: str
    name8: str
    id9: str
    name10: str
    id11: str
    name12: str
    id13: str
    name14: str
    id15: str
    name16: str

class ProductHierarchy:
    Level_Columns: Sequence[Tuple[str, str]] = [
        ("id3", "name4"), # Level 1
        ("id5", "name6"), # Level 2
        ("id7", "name8"), # Level 3
        ("id9", "name10"), # Level 4
        ("id11", "name12"), # Level 5
        ("id13", "name14"), # Level 6
        ("id15", "name16"), # Level 7        
    ]

    def __init__(self, excel_path: str | Path):
        self.rows: List[ProductRow] = []
        self.load_xlsx(excel_path)

    # data loading
    def load_xlsx(self, excel_path: str | Path) -> None:
        excel_path = Path(excel_path)
        wb = load_workbook(excel_path, data_only=True)
        ws = wb.active

        rows = list(ws.iter_rows(values_only=True))
        headers = [str(h).strip() if h else "" for h in rows[0]]

        for row in rows[1:]:
            row_dict = dict(zip(headers, row))

            pr = ProductRow(
                uid = str(row_dict["uid"]).strip(),
                language = str(row_dict["id"]).strip().lower(),

                id3 = str(row_dict["id3"]).strip(),
                name4 = str(row_dict["name4"]).strip(),
                id5 = str(row_dict["id5"]).strip(),
                name6 = str(row_dict["name6"]).strip(),
                id7 = str(row_dict["id7"]).strip(),
                name8 = str(row_dict["name8"]).strip(),
                id9 = str(row_dict["id9"]).strip(),
                name10 = str(row_dict["name10"]).strip(),
                id11 = str(row_dict["id11"]).strip(),
                name12 = str(row_dict["name12"]).strip(),
                id13 = str(row_dict["id13"]).strip(),
                name14 = str(row_dict["name14"]).strip(),
                id15 = str(row_dict["id15"]).strip(),
                name16 = str(row_dict["name16"]).strip(),
            )

            self.rows.append(pr)
    
    # access
    def get_level_options(self, level: int, language: str, previous_selections: Optional[Dict[str, str]] = None) -> List[str]:
        if level < 0 or level >= len(self.Level_Columns):
            raise ValueError(f"Invalid level index {level}")
        
        _, name_col = self.Level_Columns[level]
        previous_selections = previous_selections or {}

        values: set[str] = set()

        for r in self.rows:
            if r.language.lower() != language.lower():
                continue

            if not self.match_previous_selections(r, previous_selections):
                continue

            value = getattr(r, name_col)
            if value:
                values.add(value)

        return sorted(values)
    
    def match_previous_selections(self, row: ProductRow, previous_selections: Dict[str, str]) -> bool:
        for col_name, excepted_value in previous_selections.items():
            actual_value = getattr(row, col_name)
            if actual_value != excepted_value:
                return False
        return True
    
    # gui integration
    def build_selection_dict(self, selections_by_level: Sequence[Optional[str]]) -> Dict[str, str]:
        mapping: Dict[str, str] = {}

        for level, value in enumerate(selections_by_level):
            if value is None:
                continue

            _, name_col = self.Level_Columns[level]
            mapping[name_col] = value

        return mapping
    
    def find_variants(self, language:str, selections_by_level: Sequence[Optional[str]])-> List[ProductRow]:
        selection_dict = self.build_selection_dict(selections_by_level)

        result: List[ProductRow] = []

        for r in self.rows:
            if r.language.lower() != language.lower():
                continue
            if self.match_previous_selections(r, selection_dict):
                result.append(r)

        return result