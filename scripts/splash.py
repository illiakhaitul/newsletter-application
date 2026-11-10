import time, threading
import customtkinter as ctk
import tkinter as tk
from PIL import Image

from common.common import *
from scripts.scripts import *
import common.consts as const

class LoadingSplashScreen(ctk.CTkToplevel):
    def __init__(self, parent, on_cancel=None):
        super().__init__(parent)

        self.on_cancel = on_cancel
        self.running = True
        self.width = const.BASE_W
        self.height = const.BASE_H

        self._configure_window()
        self._init_fonts()
        self._build_ui()

    def _configure_window(self):
        self.overrideredirect(False)
        self.title("Newsletter Application")
        
        self.app_icon = tk.PhotoImage(file=const.IMG_ICON_PATH)
        self.after(200, lambda: self.iconphoto(False, self.app_icon))

        center_window(self, self.width, self.height)
        self.configure(fg_color=const.COLOR_WHITE)

    def _init_fonts(self):
        self.font_title = ctk.CTkFont(size=18, weight="bold")
        self.font_percent = ctk.CTkFont(size=40, weight="bold")
        self.font_feedback = ctk.CTkFont(size=14)

    def _build_ui(self):
        self._build_header()
        self._build_progress_section()

    def _build_header(self):
        top = ctk.CTkFrame(self, fg_color=const.COLOR_WHITE)
        top.pack(fill="x", pady=(20,10))

        title = ctk.CTkLabel(top, text="Loading Application", font=self.font_title, text_color=const.COLOR_BLACK)
        title.pack(anchor = "w", padx = 25)

        divider = ctk.CTkFrame(top, height=2, fg_color=const.DIVIDER_COLOR, corner_radius=0)
        divider.pack(fill="x", pady=(10,0))

    def _build_progress_section(self):
        content = ctk.CTkFrame(self, fg_color=const.COLOR_WHITE)
        content.pack(padx = 25, pady = 20, anchor = "w")

        # on percent text
        self.percent_var = ctk.StringVar(value="0%")
        progress_cont = ctk.CTkLabel(content, textvariable = self.percent_var, font=self.font_percent, text_color=const.COLOR_BLACK)
        progress_cont.pack(anchor="w", pady=(0,10))

        self.progress = ctk.CTkProgressBar(content, width=self.width-80, height=6, corner_radius=0, fg_color=const.DIVIDER_COLOR, progress_color = const.PROGRESS_COLOR)
        self.progress.pack(anchor="w")
        self.progress.set(0)

        self.feedback_var = ctk.StringVar(value="Proceeding...")
        feedback_cont = ctk.CTkLabel(content, textvariable = self.feedback_var, font=self.font_feedback, text_color=const.COLOR_BLACK, width=self.width-80, anchor="w")
        feedback_cont.pack(anchor="w", pady=(6,0))

    def _safe_close(self):
        try:
            self.running = False
            self.after(10, self.destroy)
        
        except:
            pass

    def close(self):
        self.running = False
        self._safe_close()

    def update_ui(self, i):
        if not self.running:
            return
        
        self.percent_var.set(f"{i}%")
        self.progress.set(i / 100)
        self.feedback_var.set("Proceeding...")

class PreSplash(ctk.CTkToplevel):
    def __init__(self, parent, image_path, on_finish):
        super().__init__(parent)

        self.on_finish = on_finish

        self.overrideredirect(True)
        self.configure(fg_color=const.COLOR_WHITE)

        img = Image.open(image_path)

        img_height = const.BASE_H / 2
        img_weight = const.BASE_W / 2 

        img.thumbnail((img_height, img_weight))

        self.image = ctk.CTkImage(light_image=img, size=img.size)

        self.width, self.height = img.size

        center_window(self, self.width, self.height)

        self.label = ctk.CTkLabel(self, image=self.image, text="")
        self.label.pack()

        self.after(const.CLOSE_DELAY, self._close)

    def _close(self):
        if self.winfo_exists():
            self.destroy()
        
        if callable(self.on_finish):
            self.on_finish()

