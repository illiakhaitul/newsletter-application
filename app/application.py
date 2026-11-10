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
from services.services import GenerationService
from common.common import *
from scripts.scripts import *

## False for Debug
useTabelle = True

# main Application
class App(ctk.CTk):
    def __init__(self, use_tabelle = useTabelle):
        super().__init__()

        # hide main window
        self.withdraw()

        self.useTabelle = use_tabelle
        self._initialized = False

        self._init_window()

    def initialize(self, hierarchy=None) -> None:
        if self._initialized:
            return
        
        if self.useTabelle and hierarchy is None:
            raise RuntimeError("useTabelle=True, but ProductHierarchy was not loaded")
        
        self._init_state(hierarchy)
        self._init_fonts()

        self._init_header()

        self._build_navigation()
        self._build_tabs()
        self._init_services()
        self._build_actions_section()

        self.show_generate()

        self.show_generate()

        self._initialized = True

    def _init_window(self) -> None:
        self.title(const.APP_TITLE)
        self.geometry(const.BASE_GEOMETRY)
        self.configure(fg_color=const.COLOR_WHITE)

        self.app_icon = tk.PhotoImage(file=const.IMG_ICON_PATH)
        self.after(1000, lambda: self.iconphoto(False, self.app_icon))

        center_window(self, const.BASE_W, const.BASE_H)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

    def _init_state(self, hierarchy=None) -> None:
        if self.useTabelle:
            self.hierarchy = hierarchy
            self.languages = sorted(
                set(
                    row.language 
                    for row in self.hierarchy.rows
                )
            )
        else:
            self.hierarchy = None
            self.languages = []

        self.active_view = 1

        self._icon_ref = None
        self._header_ctk_img = None

    def _init_fonts(self) -> None:
        self.bold_font = ctk.CTkFont(weight="bold")

        font_path = str(resource_path("resources/fonts/OpenSans-VariableFont_wdth,wght.ttf"))

        if os.path.exists(font_path):
            FR_PRIVATE = 0x10
            path_buffer = ctypes.create_unicode_buffer(font_path)
            result = ctypes.windll.gdi32.AddFontResourceExW(ctypes.byref(path_buffer), FR_PRIVATE, 0)
        else:
            print(f"ERROR: Font file not found at {font_path}")

        # main font
        font_file_path = resource_path("resources/fonts/OpenSans-VariableFont_wdth,wght.ttf")
        pyglet.font.add_file(str(font_file_path))

        # main bosch fonts
        FONT_FAMILY = "Open Sans"

        self.font_title = ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold")
        self.font_section = ctk.CTkFont(family=FONT_FAMILY, size=18, weight="normal")
        self.font_label = ctk.CTkFont(family=FONT_FAMILY, size=16)
        self.font_note = ctk.CTkFont(family=FONT_FAMILY, size=12)
        self.font_check = ctk.CTkFont(family=FONT_FAMILY, size=14)
        self.font_title_nonbold = ctk.CTkFont(family=FONT_FAMILY, size=24)

    def _init_header(self) -> None:
        try:
            logo_img = Image.open(const.IMG_HEADER_PATH)
        except Exception:
            logo_img = Image.new("RGB", (800, 10), "white")

        header_ctk = ctk.CTkImage(light_image=logo_img, size=(800, 10))
        header_label = ctk.CTkLabel(self, image=header_ctk, text="", fg_color=const.COLOR_WHITE, height=10)
        header_label.image = header_ctk
        self._header_ctk_img = header_ctk
        header_label.pack(fill="x", side="top")

        # title
        title_label = ctk.CTkLabel(
            self,
            text=const.APP_TITLE,
            font = self.font_title_nonbold,
            text_color = const.COLOR_TEXT,
        )
        title_label.pack(pady=(20, 10))

    def _build_navigation(self) -> None:
        # navigating menu
        self.nav_frame = ctk.CTkFrame(self, fg_color=const.COLOR_WHITE)
        self.nav_frame.pack(fill="x", pady=(15,5))

        self.nav_inner = ctk.CTkFrame(self.nav_frame, fg_color=const.COLOR_WHITE)
        self.nav_inner.pack(anchor="center")

        # generate section button
        self.btn_generate = ctk.CTkButton(
            self.nav_inner, text="GENERATE",
            width=100, height=30, font=self.bold_font,
            fg_color=const.COLOR_BRAND, text_color=const.COLOR_WHITE,
            hover_color="#005f8a", corner_radius=4, command=self.show_generate
        )
        self.btn_generate.pack(side="left", padx=(0,12))

        # upload to MAM section button
        self.btn_upload = ctk.CTkButton(
            self.nav_inner, text="PAGE ID PATH",
            width=130, height=30, font=self.bold_font,
            fg_color=const.COLOR_WHITE, text_color=const.COLOR_BRAND,
            border_color=const.COLOR_BRAND, border_width=1,
            hover_color=const.COLOR_BRAND_HOVER, corner_radius=4, command=self.show_upload
        )
        
        self.btn_upload.pack(side="left", padx=(0,12))

        # generate metadata button
        self.btn_metadata = ctk.CTkButton(
            self.nav_inner, text="METADATA",
            width=100, height=30, font=self.bold_font,
            fg_color=const.COLOR_BRAND, text_color=const.COLOR_WHITE,
            hover_color="#005f8a", corner_radius=4, command=self.show_metadata
        )
        self.btn_metadata.pack(side="left", padx=(0,12))

    def _build_tabs(self) -> None:
        self.content = ctk.CTkFrame(self, fg_color=const.COLOR_WHITE)
        self.content.pack(
            fill="both",
            expand=True
        )

        self.generate_tab = GenerateTab(
            master=self.content,
            font_section=self.font_section,
            font_label=self.font_label,
            font_note=self.font_note,
            font_check=self.font_check,
            bold_font=self.bold_font
        )

        self.pageidpath_tab = PageIdPathTab(
            master=self.content,
            hierarchy=self.hierarchy,
            languages=self.languages,
            font_label=self.font_label
        )

        self.metadata_tab = MetadataTab(
            master=self.content,
            font_label=self.font_label,
            font_note=self.font_note
        )

        self.main = self.generate_tab
        self.upload_frame = self.pageidpath_tab
        self.metadata_frame = self.metadata_tab

    def _init_services(self) -> None:
        self.generation_service = GenerationService(
            generate_tab = self.generate_tab,
            pageidpath_tab = self.pageidpath_tab,
            metadata_tab = self.metadata_tab,
        )

    def _build_actions_section(self) -> None:
        self.actions_frame = ctk.CTkFrame(self, fg_color=const.COLOR_WHITE)
        self.actions_frame.columnconfigure(0, weight=1)
        self.actions_frame.columnconfigure(1, weight=0)
        self.actions_frame.columnconfigure(2, weight=0)

        # actions
        f3 = ctk.CTkFrame(self.actions_frame, fg_color=const.COLOR_WHITE)
        f3.pack(fill="x")
        
        f3.columnconfigure(0, weight=1)
        f3.columnconfigure(1, weight=0)
        f3.columnconfigure(2, weight=0)

        ctk.CTkButton(
            f3, text="Generate PDF",
            width=140, height=32, font=self.bold_font,
            fg_color=const.COLOR_BRAND, text_color="white",
            hover_color="#005f8a",
            corner_radius=4,
            command=self.generation_service.on_generate
        ).grid(row=0, column=0, padx=(0,10), pady=0, sticky="e")

        ctk.CTkButton(
            f3, text="Open Output Folder",
            width=160, height=32, font=self.bold_font,
            fg_color=const.COLOR_WHITE, text_color=const.COLOR_TEXT_BRAND,
            border_color=const.COLOR_BRAND_BORDER, border_width=1,
            hover_color=const.COLOR_INACTIVE_TEXT_HOVER,
            corner_radius=4,
            command=self.generation_service.open_outlook
        ).grid(row=0, column=1, padx=(0,0), pady=0, sticky="e")
    
    # show main generate window 
    def show_generate(self):
        self.active_view = 1
        self.main.pack_forget()
        self.upload_frame.pack_forget()
        self.metadata_frame.pack_forget()
        self.actions_frame.pack_forget()

        self.main.pack(fill="both", expand=True, padx=16, pady=12)
        self.actions_frame.pack(fill="x", pady=20, padx=20)

        self._highlight_tab(self.btn_generate)

    # self upload window
    def show_upload(self):
        self.active_view = 2
        self.main.pack_forget()
        self.upload_frame.pack_forget()
        self.metadata_frame.pack_forget()
        self.actions_frame.pack_forget()

        self.upload_frame.pack(fill="both", expand=True, padx=16, pady=12)
        self.actions_frame.pack(fill="x", pady=20, padx=20)

        self._highlight_tab(self.btn_upload)

    def show_metadata(self):
        self.active_view = 3
        self.main.pack_forget()
        self.upload_frame.pack_forget()
        self.metadata_frame.pack_forget()
        self.actions_frame.pack_forget()

        self.metadata_frame.pack(fill="both", expand=True, padx=16, pady=12)
        self.actions_frame.pack(fill="x", pady=20, padx=20)

        self._highlight_tab(self.btn_metadata)

    # switch header color active/nonactive
    def _highlight_tab(self, active_btn):
        for b in [self.btn_generate, self.btn_upload, self.btn_metadata]:
            if b == active_btn:
                b.configure(fg_color = const.COLOR_BRAND, text_color = const.COLOR_WHITE, border_color = const.COLOR_BRAND, border_width=1, hover_color = "#005f8a")
            else:
                b.configure(fg_color = const.COLOR_WHITE, text_color = const.COLOR_TEXT_BRAND, border_color = const.COLOR_BRAND_BORDER, border_width=1, hover_color=const.COLOR_INACTIVE_TEXT_HOVER)
