import os, re, shutil, time, threading, pyglet, ctypes
import customtkinter as ctk
import tkinter as tk

from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from ui.widgets.widgets import CustomDropDown, MultiSelectDropDown
from common.common import *
from scripts.scripts import *


class GenerateTab(ctk.CTkFrame):
    def __init__(self, master, font_section, font_label, font_note, font_check, bold_font):
        super().__init__(master, fg_color=const.COLOR_WHITE)
        self._init_dependencies(font_section, font_label, font_note, font_check, bold_font)
        self._init_state()
        self._build_ui()

    def _init_dependencies(self, font_section, font_label, font_note, font_check, bold_font) -> None:
        self.font_section = font_section
        self.font_label = font_label
        self.font_note = font_note
        self.font_check = font_check
        self.bold_font = bold_font
        self.app = self.winfo_toplevel()

        self.main = self

    def _init_state(self) -> None:
        self.excel_var = ctk.StringVar(value="No file chosen")
        
        self.tpl_de_var = ctk.StringVar(value="No file chosen")
        self.tpl_en_var = ctk.StringVar(value="No file chosen")

        self._xls: Optional[ExcelSource] = None
        self._excel_path: Optional[str] = None

        self._tpl_de_path: Optional[str] = None
        self._tpl_en_path: Optional[str] = None

        self._row_map: Dict[str, str] = {}

    def _build_ui(self):
        self._build_excel_section()
        self._build_create_new_section()
        self._build_template_section()

    def _build_excel_section(self) -> None:    
        # excel
        f1 = ctk.CTkFrame(self.main, fg_color=const.COLOR_WHITE) 
        f1.pack(fill="x", pady=10, padx = 20)

        ctk.CTkLabel(f1, text="Excel Document", font=self.font_section, text_color=const.COLOR_TEXT).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,12))
        ctk.CTkLabel(f1, text="File:", font=self.font_label, text_color=const.COLOR_TEXT).grid(row=1, column=0, sticky="w", padx=(0,12), pady=4)

        file_frame = ctk.CTkFrame(f1, fg_color=const.COLOR_WHITE)
        file_frame.grid(row=1, column=1, columnspan=2, sticky="w")

        self.choose_btn = ctk.CTkButton(
            f1, text="Select File",
            width=90, height=40,
            fg_color=const.COLOR_WHITE, text_color=const.COLOR_BRAND,
            border_color=const.COLOR_BRAND, border_width=1,
            corner_radius=4, hover_color=const.COLOR_BRAND_HOVER,
            command=self._pick_excel
        )
        self.choose_btn.grid(row=1, column=1, sticky="w", padx=(52,10), pady=8)

        self.excel_file_label = ctk.CTkLabel(file_frame, textvariable = self.excel_var, text_color=const.COLOR_FILE_LABEL, font=self.font_note)
        self.excel_file_label.pack(side="left", padx=(150,10))

        # row selection
        ctk.CTkLabel(f1, text="Row:", font=self.font_label, text_color=const.COLOR_TEXT, fg_color=const.COLOR_WHITE).grid(row=2, column=0, sticky="e", padx=(0,12), pady=12)
        
        def format_row_value(value: str) -> str:
            format_value = (
                value.split(":", 1)[1].strip()
                if ":" in value
                else value
            )

            return format_value.split(" - ", 1)[0].strip()
        
        self.row_combo = CustomDropDown(f1, values=[], width=250, height=40, display_formatter=format_row_value)
        self.row_combo.grid(row=2, column=1, sticky="w", padx=(52,10), pady=0)
        self.row_combo.entry.configure(border_width=1, border_color=const.COLOR_DROPDOWN_BORDER)

        f1.columnconfigure(2, weight=1)

    def _build_create_new_section(self) -> None:
        # copy icon
        copy_icon_img = Image.open(const.COPY_ICON)
        self.copy_icon_ctk = ctk.CTkImage(copy_icon_img, size=(16,16))

        # open popup icon
        open_pu_icon_img = Image.open(const.OPEN_POPUP_ICON)
        self.open_pu_icon_ctk = ctk.CTkImage(open_pu_icon_img, size=(16,16))

        # close popup icon
        close_pu_icon_img = Image.open(const.CLOSE_POPUP_ICON)
        self.close_pu_icon_ctk = ctk.CTkImage(close_pu_icon_img, size=(16,16))

        wrap = ctk.CTkFrame(self.main, fg_color=const.COLOR_WHITE) 
        wrap.pack(fill="x", pady=10, padx=20)

        hdr = ctk.CTkFrame(wrap, fg_color=const.COLOR_WHITE)
        hdr.pack(fill="x")   
        
        self.new_mode = ctk.BooleanVar(value=False)

        self.new_mode_checkbox = ctk.CTkButton(
            hdr,
            text="Create a new Number",
            image=self.open_pu_icon_ctk,
            width=240,
            height=40,
            command=self.open_popup_mode,
            fg_color=const.COLOR_WHITE,
            hover_color=const.COLOR_INACTIVE_TEXT_HOVER,
            border_width=1,
            border_color=const.COLOR_BRAND,
            corner_radius=4,
            text_color=const.COLOR_BRAND,
            font=self.font_note,
        )
        
        self.new_mode_checkbox.grid(row=0, column=0, sticky="w", padx=(0,10), pady=6)

        # body - hidden
        self.body = ctk.CTkFrame(wrap, fg_color=const.COLOR_WHITE)

        # input fields
        self.date = ctk.CTkEntry(self.body, width=100, height=40, corner_radius=4, border_width=1, 
                                 border_color=const.COLOR_DROPDOWN_BORDER, fg_color=const.COLOR_WHITE, justify="center")
        self.date.insert(0, datetime.now().strftime("%m.%Y"))

        self.num = ctk.CTkEntry(self.body, width=100, height=40, corner_radius=4, border_width=1, 
                                border_color=const.COLOR_DROPDOWN_BORDER, fg_color=const.COLOR_WHITE, justify="center")

        """ #self.typ = ctk.CTkEntry(self.body, width=80, corner_radius=0, border_width=1, fg_color=COLOR_WHITE, justify="center")
        self.typ = CustomDropDown(self.body, values=["PI", "DI", "TI", "LI", "MI"], width=80, 
                                  height=const.DROPDOWN_HEIGHT, typ_popup_width=100, typ_popup_height=150)
        self.typ.set("PI")
        self.typ.entry.configure(border_width=1, border_color=const.COLOR_DROPDOWN_BORDER) """

        # product group input field
        Product_Group_variables = ["TF 2plus", "VFplus", "TS 5", "MPS", "RFID", "MIT", "Mtpro 5.0", "MGE", "MT", "MPS", "MTpro", "MGE/MP5", "Intralogistik", "AT", "Service", ]
        
        self.pg = CustomDropDown(self.body, values=Product_Group_variables, width=90 + const.DROPDOWN_BTN_W, height=40, typ_popup_width=110, typ_popup_height=150)
        self.pg.set(cfg.get("PRODUCT_GROUP", "MGE"))
        self.pg.entry.configure(border_width=1, border_color=const.COLOR_DROPDOWN_BORDER)

        def cell(lbl: str, widget: ctk.CTkEntry, col: int) -> None:
            ctk.CTkLabel(self.body, text=lbl, text_color=const.COLOR_TEXT).grid(row=0, column=col, sticky="e", padx=4, pady=2)
            widget.grid(row=0, column=col + 1, sticky="w", padx=4, pady=10)

        cell("Number:", self.num, 0)
        cell("Date:", self.date, 2)
        cell("Product Group:", self.pg, 4)
        """ cell("Typ:", self.typ, 4) """

        # thema input field
        self.thema = ctk.CTkEntry(self.body, width=100, height=40, corner_radius=4, border_width=1, border_color=const.COLOR_DROPDOWN_BORDER, fg_color=const.COLOR_WHITE)

        ctk.CTkLabel(self.body, text="Thema:", text_color=const.COLOR_TEXT).grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.thema.grid(row=1, column=1, columnspan=5, sticky="ew", padx=4, pady=2)

        for c in range(1, 3, 5):
            self.body.columnconfigure(c, weight=1)

        self.body.pack_forget()

    def _build_template_section(self) -> None:
        f2 = ctk.CTkFrame(self.main, fg_color=const.COLOR_WHITE)
        f2.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(f2, text="Docx template", font=self.font_section, text_color=const.COLOR_TEXT).grid(row=0, column=0, sticky="w", pady=(0,12), columnspan=3)

        # de template
        ctk.CTkLabel(f2, text="File (DE):", font=self.font_label, text_color=const.COLOR_TEXT).grid(row=1, column=0, sticky="e", padx=(0,10), pady=4)

        file_frame_de = ctk.CTkFrame(f2, fg_color=const.COLOR_WHITE)
        file_frame_de.grid(row=1, column=1, columnspan=2, sticky="w")

        self.choose_tpl_de_btn = ctk.CTkButton(
            f2, text="Select File",
            width=90, height=40,
            fg_color=const.COLOR_WHITE, text_color=const.COLOR_BRAND,
            border_color=const.COLOR_BRAND, border_width=1,
            corner_radius=4, hover_color=const.COLOR_BRAND_HOVER,
            command=lambda: self._pick_tpl("de")
        )
        self.choose_tpl_de_btn.grid(row=1, column=1, sticky="w", padx=(25,10), pady=8)

        self.tpl_de_file_label = ctk.CTkLabel(file_frame_de, textvariable=self.tpl_de_var, text_color=const.COLOR_FILE_LABEL, font=self.font_note)
        self.tpl_de_file_label.pack(side="left", padx=(123,10))

        # eng template
        ctk.CTkLabel(f2, text="File (EN):", font=self.font_label, text_color=const.COLOR_TEXT).grid(row=2, column=0, sticky="e", padx=(0,10), pady=4)

        file_frame_en = ctk.CTkFrame(f2, fg_color=const.COLOR_WHITE)
        file_frame_en.grid(row=2, column=1, columnspan=2, sticky="w")

        self.choose_tpl_en_btn = ctk.CTkButton(
            f2, text="Select File",
            width=90, height=40,
            fg_color=const.COLOR_WHITE, text_color=const.COLOR_BRAND,
            border_color=const.COLOR_BRAND, border_width=1,
            corner_radius=4, hover_color=const.COLOR_BRAND_HOVER,
            command=lambda: self._pick_tpl("en")
        )
        self.choose_tpl_en_btn.grid(row=2, column=1, sticky="w", padx=(25,10), pady=8)

        self.tpl_en_file_label = ctk.CTkLabel(file_frame_en, textvariable=self.tpl_en_var, text_color=const.COLOR_FILE_LABEL, font=self.font_note)
        self.tpl_en_file_label.pack(side="left", padx=(123,10))
    
    def _toggle(self) -> None:
        base_w, base_h = const.BASE_W, const.BASE_H
        extra_h = 20

        if self.new_mode.get():
            self.new_mode_checkbox.configure(image=self.close_pu_icon_ctk)
            self.body.pack(fill="x")
            self.row_combo.disable()
            self.app.geometry(f"{base_w}x{base_h + extra_h}")
        else:
            self.new_mode_checkbox.configure(image=self.open_pu_icon_ctk)
            self.body.pack_forget()
            self.row_combo.enable()
            self.app.geometry(f"{base_w}x{base_h}")
        self.focus_set()

    def open_popup_mode(self) -> None:
        self.new_mode.set(not self.new_mode.get())
        self._toggle()

    def _pick_excel(self):
        p = filedialog.askopenfilename(title="Select Excel Document", filetypes=[("Excel", "*.xlsx;*.xlsm;*.xls")])
        if not p: return
        
        self._excel_path = p
        self.excel_var.set(os.path.basename(p))

        try:
            self._xls = ExcelSource(p)
            rows = self._xls.list_rows()

            try:
                last_num = self._xls.get_number()
                next_num = last_num + 1

                self.num.configure(state="normal")
                self.num.delete(0, "end")
                self.num.insert(0, f"{next_num:05d}")
                self.num.configure(state="readonly")
                
            except Exception as e:
                print("Failed to auto fill the number:", e)

            self._row_map = {
                f"{r['idx']}: {r.get('Header') or '-'} - {r.get('Thema') or ''} - {r.get('MM.JJJJ') or ''}":str(r['idx'])
                for r in rows
            }

            if not self._row_map:
                self.row_combo.configure_values(["-"])
                self.row_combo.set("-")
                return

            values = list(self._row_map.keys())
            self.row_combo.configure_values(values)
            self.row_combo.set_placeholder("Select an existing Number...")
            
        except Exception as e:
            messagebox.showerror("Excel", str(e))

    def _pick_tpl(self, lang: str) -> None:
        p = filedialog.askopenfilename(title="Select DOCX Template", filetypes=[("Word", "*.docx")])
        if not p:
            return
        if lang == "de": 
            self._tpl_de_path = p
            self.tpl_de_var.set(os.path.basename(p))
        elif lang == "en":
            self._tpl_en_path = p
            self.tpl_en_var.set(os.path.basename(p))

    def _row_from_combo(self) -> Dict[str, str]:
        raw = self.row_combo.get()
        if not raw: 
            raise RuntimeError("Select row in Excel doc")
        idx_str = raw.split(":", 1)[0].strip()
        idx = int(idx_str)
        return self._xls.get_row(idx)