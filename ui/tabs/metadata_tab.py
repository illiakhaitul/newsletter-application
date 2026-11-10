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

class MetadataTab(ctk.CTkFrame):
    def __init__(self, master, font_label, font_note):
        super().__init__(master, fg_color=const.COLOR_WHITE)
        self._init_dependencies(font_label, font_note)
        self._init_state()
        self._build_ui()

    def _init_dependencies(self, font_label, font_note) -> None:
        self.font_label = font_label
        self.font_note = font_note

        self.metadata_frame = self

    def _init_state(self) -> None:
        self.metadata_vars = {}

    def _build_ui(self) -> None:
        self._build_metadata_section()

    def _build_metadata_section(self):
        wrapper = ctk.CTkFrame(self.metadata_frame, fg_color=const.COLOR_WHITE, width=520, height=430)
        wrapper.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(wrapper, text="These values will be used for metadata generation", text_color="gray", font=self.font_note).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 15))

        keywords_values = ["Manuelle Produktionssysteme", "Gleitschiene", "EcoShape", "Abdeckkappe", "Abdeckleiste Socket strip", "ABDECKUNG SOCKET STRIP", "ACTIVE Cockpit", "al-ca", "bremse", "bruecke", "CABLE PASSAGE", "COMPENSATING CABLE", "CORNER PROTECTION", "Cover cap", "COVER SOCKET STRIP", "Curve" "Hägglunds"]
        
        country_values = ["XC - International", "AE - Middle East", "AR - Argentina", "AT - Austria", "AU - Australia", "BA - Bosnia and Herzeg.", "BE - Belgium", "BR - Brazil", "BG - Bulgaria", "BY - Belarus", "CA - Canada", "CH - Switzerland", "CL - Chile", "CN - China", "CO - Colombio", "CZ - Czech Rpl.", "DE - Germany", "DK - Denmark", "ES - Spain", "FI - Finland", "FR - France", "GB - United Kingdom", "GR - Greece", "HU - Hungary", "HR - Croatia", "ID - Indonesia", "IE - Ireland", "IN - India", "IN - India", "JP - Japan", "KR - Korea", "KZ - Kazakhstan", "MX - Mexico", "MY - Malaysia", "NL - Netherlands", "NO - Norway", "NZ - New Zealand", "PE - Peru", "PL - Poland", "PT - Portugal", "RO - Romania", "RU - Russia", "RS - Serbia", "SG - Singapore", "SI - Slovenia", "SE - Sweden", "TH - Thailand", "TR - Turkey", "TW - Taiwan", "UA - Ukraine"]
        
        target_group_values = ["public", "authenticated", "partner", "distribution_AT", "distribution_AE", "distribution_IH", "distribution_LT", "distribution_MH", "distribution_TT", "distribution_HD_large", "distribution_HD_small", "distribution_RN", "service_AE", "service_IH", "service_point_MH", "service_repair_MH", "service_repair_HD_large", "service_repair_HD_small", "service_field_HD", "service_RN", "solution_MH", "solution_AE", "solution_elion_MH", "employees"]
        
        row_index = 2

        # tags / keywords
        ctk.CTkLabel(wrapper, text="Tags / Keywords:", text_color=const.COLOR_TEXT, font=self.font_label).grid(row=row_index, column=0, sticky="w", padx=(0,10), pady=3)
        
        keywords_dropdown = MultiSelectDropDown(wrapper, values=keywords_values, width=370, height=40, popup_width=340, popup_height=260)
        keywords_dropdown.grid(row=row_index, column=1, columnspan=3, sticky="w", pady=3)

        self.metadata_vars["keywords"] = keywords_dropdown

        row_index += 1

        # DC county
        ctk.CTkLabel(wrapper, text="DC Country:", text_color=const.COLOR_TEXT, font=self.font_label).grid(row=row_index, column=0, sticky="w", padx=(0,10), pady=3)

        country_dropdown = CustomDropDown(wrapper, values=country_values, width=370, height=40, typ_popup_width=340, typ_popup_height=260)
        country_dropdown.grid(row=row_index, column=1, sticky="w", pady=3)
        country_dropdown.entry.configure(border_width=1, border_color=const.COLOR_DROPDOWN_BORDER)

        self.metadata_vars["country"] = country_dropdown

        row_index += 1

        # target group
        ctk.CTkLabel(wrapper, text="Target Group:", text_color=const.COLOR_TEXT, font=self.font_label).grid(row=row_index, column=0, sticky="w", padx=(0,10), pady=3)

        target_group_dropdown = MultiSelectDropDown(wrapper, values=target_group_values, width=370, height=40, popup_width=340, popup_height=260)
        target_group_dropdown.grid(row=row_index, column=1, sticky="w", pady=3)

        self.metadata_vars["target_group"] = target_group_dropdown

        row_index += 1

    def get_metadata_values(self) -> Dict[str, str]:
        metadata = {}

        for key, entry in self.metadata_vars.items():
            metadata[key] = entry.get().strip()

        return metadata