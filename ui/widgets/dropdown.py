import customtkinter as ctk
import tkinter as tk

from PIL import Image, ImageTk
from typing import Dict, List, Optional

from common.common import *
from scripts.scripts import *

class CustomDropDown(ctk.CTkFrame):
    def __init__(self, master, values: Optional[List[str]] = None, width: int = const.DROPDOWN_WIDTH, height: int = const.DROPDOWN_HEIGHT, typ_popup_width: Optional[int] = None, typ_popup_height: Optional[int] = None, display_formatter=None):
        super().__init__(master, border_width=1, border_color=const.COLOR_DROPDOWN_BORDER, fg_color=const.COLOR_WHITE)

        self.values: List[str] = values or []
        self.var = ctk.StringVar(value="Select Value...")
        self._dropdown_win: Optional[ctk.CTkToplevel] = None

        # display chosen row 
        self.selected_value = ""
        self.display_formatter = display_formatter

        # click handler
        self._outside_bind_id = None

        self.option_buttons = {}
        self.search_var = ctk.StringVar(value="")
        self.search_var.trace_add("write", self.filter_options)

        self.search_entry = None
        self.no_results_label = None

        self._width = width
        self._height = height
        self._popup_width = typ_popup_width
        self._popup_height = typ_popup_height
        self._popup_gap = 1
        self.callback = None

        # entry (readonly)
        self.entry = ctk.CTkEntry(
            self, textvariable=self.var,
            width=width - const.DROPDOWN_BTN_W, height=height,
            state="readonly", fg_color=const.COLOR_WHITE, justify="center",
            text_color="black", border_width=1, corner_radius=4,
            border_color=const.COLOR_DROPDOWN_BORDER
        )
        self.entry.pack(side="left", fill="y")

        # arrow btn
        arrow_img = Image.open(const.IMG_ARROW_PATH)
        arrow_ctk = ctk.CTkImage(arrow_img, size=(14,14))
        self.btn = ctk.CTkButton(
            self, image=arrow_ctk, text="",
            width=const.DROPDOWN_BTN_W, height=height,
            fg_color=const.COLOR_WHITE, hover_color=const.COLOR_INACTIVE_TEXT_HOVER,
            corner_radius=0, command=self._toggle_dropdown
        )
        self._arrow_img_ref = arrow_img
        self._arrow_ctk_ref = arrow_ctk

        self.btn.pack(side="left")

    # dropdown logic 
    def _toggle_dropdown(self) -> None:
        if self._dropdown_win and self._dropdown_win.winfo_exists():
            self._close_dropdown()
        else:
            self._open_dropdown()

    def _open_dropdown(self) -> None:
        if not self.values:
            return
    
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + self._popup_gap

        win_w = self._popup_width or const.DROPDOWN_POPUP_W
        win_h = self._popup_height or const.DROPDOWN_POPUP_H

        try: 
            screen_h = self.winfo_screenheight()
            if y + win_h > screen_h:
                win_h = max(180, screen_h - y - 8)
        except Exception:
            pass

        self._dropdown_win = ctk.CTkToplevel(self)
        self._dropdown_win.overrideredirect(True)
        self._dropdown_win.geometry(f"{win_w}x{win_h}+{x}+{y}")

        self._dropdown_win.lift()
        self._dropdown_win.bind("<Escape>", lambda _e: self._close_dropdown())
        self._dropdown_win.after(10, lambda: self._dropdown_win.focus_set())

        # main dropdown container
        container = ctk.CTkFrame(
            self._dropdown_win,
            width=win_w,
            height=win_h,
            fg_color=const.COLOR_WHITE,
            border_width=1, 
            border_color=const.COLOR_INACTIVE_TEXT_HOVER,
            corner_radius=4
        )

        container.pack(
            fill="both",
            expand=True,
            padx=1,
            pady=1
        )

        container.pack_propagate(False)
        container.grid_propagate(False)

        # clear the prev search
        self.search_var.set("")

        # add search field at the top op popup
        self.search_entry = ctk.CTkEntry(
            container,
            textvariable=self.search_var,
            height=32,
            placeholder_text="Search...",
            state="normal",
            fg_color=const.COLOR_WHITE,
            text_color=const.COLOR_TEXT,
            border_width=1,
            border_color=const.COLOR_DROPDOWN_BORDER,
            corner_radius=4
        )

        self.search_entry.pack(
            fill="x",
            padx=8,
            pady=(8,6)
        )

        # add scroll
        scroll = ctk.CTkScrollableFrame(
            container,
            width=win_w - 6,
            height=max(60, win_h - 52),
            fg_color=const.COLOR_WHITE,
            scrollbar_fg_color=const.COLOR_WHITE,
            scrollbar_button_color=const.COLOR_INACTIVE_TEXT_HOVER,
            scrollbar_button_hover_color=const.COLOR_DROPDOWN_BORDER,
            corner_radius=4,
            border_width=0,
            border_color=const.COLOR_INACTIVE_TEXT_HOVER
        )
        
        scroll.pack(
            fill="both",
            expand=True
        )

        for val in self.values:
            option_button = ctk.CTkButton(
                scroll,
                text=val, 
                anchor="w",
                width=win_w - 6,
                fg_color=const.COLOR_WHITE,
                text_color=const.COLOR_BLACK,
                hover_color=const.COLOR_DROPDOWN_ITEM_HOVER,
                command=lambda v=val: self._select(v)
            )

            self.option_buttons[val] = option_button

        self.no_results_label = ctk.CTkLabel(
            scroll,
            text="No results",
            text_color=const.COLOR_TEXT,
            height=30
        )

        self.filter_options()

        self._dropdown_win.after(
            50,
            self.search_entry.focus_force
        )

        self.after(100, self._install_outside_click_handler)

    def filter_options(self, *_args) -> None:
        if not self.option_buttons:
            return
        
        query = self.search_var.get().strip().casefold()

        for button in self.option_buttons.values():
            if button.winfo_exists():
                button.pack_forget()

        if (
            self.no_results_label is not None
            and self.no_results_label.winfo_exists()
        ):
            self.no_results_label.pack_forget()

        visible_count = 0

        for value, button in self.option_buttons.items():
            if query in str(value).casefold():
                button.pack(
                    fill="x",
                    padx=3,
                    pady=1
                )
                visible_count += 1
            
        if (
            visible_count == 0
            and self.no_results_label is not None
            and self.no_results_label.winfo_exists()
        ):
            self.no_results_label.pack(
                fill="x",
                padx=3,
                pady=8
            )
    
    def _install_outside_click_handler(self):
        if (
            self._dropdown_win is None
            or not self._dropdown_win.winfo_exists()
        ): 
            return
        
        if self._outside_bind_id is not None:
            return
        
        parent_window = self.winfo_toplevel()

        self._outside_bind_widget = parent_window
        
        self._outside_bind_id = parent_window.bind(
            "<Button-1>",
            self._handle_outside_click, 
            add="+"
        )

    def _handle_outside_click(self, event):
        if (
            self._dropdown_win is None
            or not self._dropdown_win.winfo_exists()
        ): 
            return

        click_x = event.x_root
        click_y = event.y_root

        popup_x1 = self._dropdown_win.winfo_rootx() 
        popup_y1 = self._dropdown_win.winfo_rooty() 

        popup_x2 = (
            popup_x1 + self._dropdown_win.winfo_width()
        )

        popup_y2 = (
            popup_y1 + self._dropdown_win.winfo_height()
        )

        click_inside_popup = (
            popup_x1 <= click_x <= popup_x2
            and popup_y1 <= click_y <= popup_y2
        )

        field_x1 = self.winfo_rootx()
        field_y1 = self.winfo_rooty()

        field_x2 = field_x1 + self.winfo_width()
        field_y2 = field_y1 + self.winfo_height()

        click_inside_field = (
            field_x1 <= click_x <= field_x2
            and field_y1 <= click_y <= field_y2
        )

        if not click_inside_popup and not click_inside_field:
            self._close_dropdown()

    def _remove_outside_click(self):
        if self._outside_bind_id is None:
            return
        
        try:
            if (
                self._outside_bind_widget is not None
                and self._outside_bind_widget.winfo_exists()
            ):
                self._outside_bind_widget.unbind(
                    "<Button-1>",
                    self._outside_bind_id
                )
        
        except tk.TclError:
            pass

        self._outside_bind_id = None
        self._outside_bind_widget = None

    def _close_dropdown(self) -> None:
        self._remove_outside_click()

        if self._dropdown_win and self._dropdown_win.winfo_exists():
            self._dropdown_win.destroy()
        self._dropdown_win = None

        self.option_buttons = {}
        self.search_entry = None
        self.no_results_label = None

    def _select(self, value: str) -> None:
        self.selected_value = value

        display_value = (
            self.display_formatter(value)
            if self.display_formatter
            else value
        )

        self.var.set(display_value)
        self.entry.configure(text_color=const.COLOR_TEXT)

        if self.callback:
            self.callback(value)
            
        self._close_dropdown()

    def configure_values(self, values: Optional[List[str]]) -> None:

        cleaned = [
            v for v in (values or [])
            if v not in (None, "", "None")
        ]

        self.values = cleaned

        if not self.values:
            self.var.set("")
            self.disable()
            return
        
        self.enable()
        
        cur = self.var.get()
        if cur not in self.values or cur == "Select...":
            self.var.set("")

    def set(self, value: str) -> None:
        self.selected_value = value

        display_value = (
            self.display_formatter(value)
            if self.display_formatter
            else value
        )

        self.var.set(display_value)

    def get(self) -> str:
        return self.selected_value
    
    def set_placeholder(self, text) -> None:
        self.selected_value = ""
        self.var.set(text)
        self.entry.configure(text_color=const.COLOR_TEXT)
    
    def disable(self) -> None:
        self.entry.configure(state="disabled", fg_color=const.COLOR_WHITE, text_color="gray")
        self.btn.configure(state="disabled", fg_color=const.COLOR_WHITE)

    def enable(self) -> None:
        self.entry.configure(state="readonly", fg_color=const.COLOR_WHITE, text_color="black")
        self.btn.configure(state="normal", fg_color=const.COLOR_WHITE)

    def set_callback(self, func):
        self.callback = func