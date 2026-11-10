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

class PageIdPathTab(ctk.CTkFrame):
    def __init__(self, master, hierarchy, languages, font_label):
        super().__init__(master, fg_color=const.COLOR_WHITE)
        self._init_dependencies(hierarchy, languages, font_label)
        self._init_state()
        self._build_ui()

    def _init_dependencies(self, hierarchy, languages, font_label) -> None:
        self.hierarchy = hierarchy
        self.languages = languages
        self.font_label = font_label

        self.upload_frame = self

    def _init_state(self) -> None:
        self.level_dropdown = []

    def _build_ui(self) -> None:
        ctk.CTkLabel(self.upload_frame, text="Language:", text_color=const.COLOR_TEXT, font=self.font_label).grid(row=0, column=0, sticky="w", padx=(20,0), pady=(20,6))
        self.lang_dropdown = CustomDropDown(self.upload_frame, values=self.languages, width=370, height=40)
        self.lang_dropdown.grid(row=0, column=1, sticky="w", pady=(20,2), padx=(10,0))
        self.lang_dropdown.entry.configure(border_width=1, border_color=const.COLOR_DROPDOWN_BORDER)

        self.level_dropdown = []
        
        for i in range(7):
            lbl = ctk.CTkLabel(self.upload_frame, text=f"Level {i+1}:", text_color=const.COLOR_TEXT, font=self.font_label)
            lbl.grid(row=i+2, column=0, sticky="w", padx=(20,0), pady=2)

            dd = CustomDropDown(self.upload_frame, values=[], width=370, height=40)
            dd.grid(row=i+2, column=1, sticky="w", padx=10, pady=2)
            dd.entry.configure(border_width=1, border_color=const.COLOR_DROPDOWN_BORDER)

            self.level_dropdown.append(dd)
        
        self.lang_dropdown.set_callback(lambda _v: self.reload_level_dropdowns())

        for i, dd in enumerate(self.level_dropdown):
            dd.set_callback(lambda _v, lvl=i: self.level_changed(_v, lvl))
        
        ctk.CTkLabel(self.upload_frame, text="Page ID Path:", text_color=const.COLOR_TEXT, font=self.font_label).grid(row=9, column=0, sticky="w", padx=(20,0), pady=(20,6))
        self.pageid_entry = ctk.CTkTextbox(self.upload_frame, width=370, height=40, corner_radius=4, border_width=1, border_color=const.COLOR_DROPDOWN_BORDER, fg_color=const.COLOR_WHITE, wrap = "word")
        self.pageid_entry.grid(row=9, column=1, sticky="w", padx=(10,0), pady=(20,2)) 

        ctk.CTkLabel(self.upload_frame, text="Page ID:", text_color=const.COLOR_TEXT, font=self.font_label).grid(row=10, column=0, sticky="w", padx=(20,6), pady=(10,6))
        self.pageid_single_entry = ctk.CTkEntry(self.upload_frame, width=370, height=40, corner_radius=4, border_width=1, border_color=const.COLOR_DROPDOWN_BORDER, fg_color=const.COLOR_WHITE)
        self.pageid_single_entry.grid(row=10, column=1, sticky="w", padx=(10,0), pady=(4,6)) 

    def clear_pageid_fields(self):
        self.pageid_entry.delete("1.0", "end")
        self.pageid_single_entry.delete(0, "end")

    def update_page_id(self, selections=None):
        lang = self.lang_dropdown.get().strip().lower()
        if selections is None:
            selections = [
            dd.get().strip() or None 
            for dd in self.level_dropdown
        ]

        ids = []

        for level_index, value in enumerate(selections):
            if not value:
                continue

            id_col, name_col = self.hierarchy.Level_Columns[level_index]

            found = None
            for r in self.hierarchy.rows:
                if r.language.lower() == lang and getattr(r, name_col) == value:
                    found = getattr(r, id_col)
                    break

            if found:
                ids.append(found)

        self.pageid_entry.delete("1.0", "end")
        self.pageid_single_entry.delete(0, "end")

        if ids:
            full_path = ",".join(ids)
            self.pageid_entry.insert("1.0", full_path)

            page_id = None
            for id_val in ids:
                if re.fullmatch(r"p\d+", id_val):
                    page_id = id_val

            if page_id:
                self.pageid_single_entry.insert(0, page_id)
        else:
            self.pageid_entry.insert("1.0", "")
            self.pageid_single_entry.insert(0, "")

    def level_changed(self, _v, lvl_index):
        self.pageid_single_entry.delete(0, "end")

        lang = self.lang_dropdown.get().strip().lower()
        selections = [dd.get().strip() or None for dd in self.level_dropdown]

        for index in range(lvl_index + 1, len(selections)):
            selections[index] = None
            self.level_dropdown[index].set("")
        
        prev = self.hierarchy.build_selection_dict(selections)

        if lvl_index + 1 < len(self.level_dropdown):
            next_options = self.hierarchy.get_level_options(level=lvl_index + 1, language=lang, previous_selections=prev)
            self.level_dropdown[lvl_index + 1].configure_values(next_options)
            self.level_dropdown[lvl_index + 1].set("")

            for dd2 in self.level_dropdown[lvl_index + 2:]:
                dd2.configure_values([])

        self.update_page_id(selections)

    def reload_level_dropdowns(self):
        lang = self.lang_dropdown.get().strip().lower()

        for dropdown in self.level_dropdown:
            dropdown.set("")
            dropdown.configure_values([])

        self.clear_pageid_fields()

        if not lang:
            return
        
        # download the 1st level
        level0 = self.hierarchy.get_level_options(level=0, language=lang, previous_selections={})

        self.level_dropdown[0].configure_values(level0)
        self.level_dropdown[0].set("")