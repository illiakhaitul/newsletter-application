import os, re, shutil, time, threading, pyglet, ctypes
import customtkinter as ctk
import tkinter as tk

from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from ui.widgets.widgets import CustomDropDown, MultiSelectDropDown
from ui.tabs.tabs import GenerateTab, PageIdPathTab, MetadataTab
from common.common import *
from scripts.scripts import *

class GenerationService:
    def __init__(self, generate_tab, pageidpath_tab, metadata_tab):
        self.generate_tab = generate_tab
        self.pageidpath_tab = pageidpath_tab
        self.metadata_tab = metadata_tab

    def _outlook_dir(self) -> Path:
        out = abs_path(cfg["PATHS"]["output"])
        out_path = Path(out)
        out_path.mkdir(parents=True, exist_ok=True)
        return out_path
    
    @staticmethod
    def _open_folder(p: str) -> None:
        try: 
            os.startfile(p)
            
        except Exception: 
            filedialog.askopenfilename(initialdir=p)

    def on_generate(self) -> None:
        generate_tab = self.generate_tab
        pageidpath_tab = self.pageidpath_tab
        metadata_tab = self.metadata_tab

        try:
            if not generate_tab._xls: 
                raise RuntimeError("Select Excel Document")
            if not generate_tab._tpl_de_path or not Path(generate_tab._tpl_de_path).exists():
                raise RuntimeError("Select DE Template")
            if not generate_tab._tpl_en_path or not Path(generate_tab._tpl_en_path).exists():
                raise RuntimeError("Select EN Template")
            
            # add fixed typ from consts
            typ = const.TYP_value
            
            if generate_tab.new_mode.get():
                date = generate_tab.date.get().strip(); parse_month_year(date)
                num = generate_tab.num.get().strip();
                pg = generate_tab.pg.get().strip().upper(); th = generate_tab.thema.get().strip()

                header_full = f"AT_{num}_{typ}_{pg}_{date}"

                # write row + centering
                generate_tab._xls.append_new(header_full, date, produktgruppe=pg, thema=th, typ=typ)

                dst = self._outlook_dir() / "excel"
                dst.mkdir(parents=True, exist_ok=True)

                shutil.copy2(generate_tab._excel_path, dst / Path(generate_tab._excel_path).name)

                paths = generate_de_en_docs(header_full, date, generate_tab._tpl_de_path, generate_tab._tpl_en_path, th, typ, pg)
            else:
                row = generate_tab._row_from_combo()
                header_full = (row.get("Header") or row.get("Header  (do not change)") or "").strip()
                if not header_full: raise RuntimeError("No header in selected row")

                date = (row.get("MM.JJJJ") or "").strip()
                if not re.fullmatch(r"\d{2}\.\d{4}", date): 
                    m = re.search(r"(\d{2})\.\d{4})", header_full)
                    date = m.group(1) if m else ""
                paths = generate_de_en_docs(header_full, date, generate_tab._tpl_de_path, generate_tab._tpl_en_path)

            """ generate_upload_kit(header_full, self.thema.get() or "Newsletter", Path(paths["de"]), Path(paths["en"])) """
            page_id = pageidpath_tab.pageid_single_entry.get().strip()
            if not page_id:
                page_id_path = " - "
            
            page_id_path = pageidpath_tab.pageid_entry.get("1.0", "end").strip()
            if not page_id_path:
                page_id_path = " - "

            """ typ_val = row.get("Typ", "PI") if not generate_tab.new_mode.get() else generate_tab.typ.get() """

            # main output folder
            out_dir = Path(paths["out_dir"])

            # two separate folders
            de_folder = out_dir / "DE"
            en_folder = out_dir / "EN"

            de_folder.mkdir(parents=True, exist_ok=True)
            en_folder.mkdir(parents=True, exist_ok=True)

            # move de docs into de folder
            de_pdf = Path(paths["de"])
            de_docx = de_pdf.with_suffix(".docx")

            for de_file in (de_pdf, de_docx):
                de_target = de_folder / de_file.name

                if de_target.exists():
                    de_target.unlink()

                shutil.move(str(de_file), str(de_target))

            en_pdf = Path(paths["en"])
            en_docx = en_pdf.with_suffix(".docx")

            for en_file in (en_pdf, en_docx):
                en_target = en_folder / en_file.name

                if en_target.exists():
                    en_target.unlink()

                shutil.move(str(en_file), str(en_target))

            metadata_values = metadata_tab.get_metadata_values()
            thema_value = generate_tab.thema.get() or "Newsletter"

            # generate metadata inside the related folders
            generate_metadata(
                out_dir=de_folder,
                thema=thema_value,
                lang="DE",
                typ=typ,
                bu="AT",
                dc_page_id_path=page_id_path,
                dc_page_id=page_id,
                metadata = metadata_values,
            )

            generate_metadata(
                out_dir=en_folder, 
                thema=thema_value,
                lang="EN",
                typ=typ,
                bu="AT",
                dc_page_id_path=page_id_path,
                dc_page_id=page_id,
                metadata = metadata_values,
            )

            self._open_folder(paths["out_dir"])
            messagebox.showinfo("Completed", "Documents are generated! \nPlease check the output folder")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_outlook(self):
        self._open_folder(str(self._outlook_dir()))