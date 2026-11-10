import customtkinter as ctk
import tkinter as tk

from PIL import Image, ImageTk
from typing import Dict, List, Optional

from common.common import *
from scripts.scripts import *

class MultiSelectDropDown(ctk.CTkFrame):
    def __init__(self, master, values=None, width=280, height=30, popup_width=300, popup_height=160):
        super().__init__(master, width=width, height=height, fg_color=const.COLOR_WHITE)

        # keep the dropdown size
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.values = [
            value for value in (values or [])
            if value not in (None, "", "None")
        ]

        # list of selected values
        self.selected_values = []

        # dropdown buttons
        self.option_buttons = {}

        # add search bar inside dropdown
        self.search_var = ctk.StringVar(value="")
        self.search_var.trace_add("write", self.filter_options)

        self.search_entry = None
        self.no_results_label = None

        self._dropdown_win = None

        self._width = width
        self._height = height

        self._field_width = (width - const.DROPDOWN_BTN_W)

        self._popup_width = popup_width
        self._popup_height = popup_height
        self._popup_gap = 1

        self._base_height = height
        self._current_height = self._base_height

        # values size
        self._chip_height = 28

        self._field_inner_padding = 2

        self._chip_row_gap = 4
        self._chip_row_height = self._chip_height + self._chip_row_gap

        self._chip_vertical_padding = max(
            0,
            (
                self._base_height - self._chip_height - self._field_inner_padding * 2
            ) // 2
        )

        self._chip_gap = 5

        self.configure(height=self._base_height)

        self.grid_columnconfigure(0, weight=0, minsize=self._field_width)
        self.grid_columnconfigure(1, weight=0, minsize=const.DROPDOWN_BTN_W)
        self.grid_rowconfigure(0, weight=1)

        # size of open dropdown is fixed
        self._active_popup_width = popup_width
        self._active_popup_height = popup_height

        # click handler
        self._outside_bind_id = None

        self.var = ctk.StringVar(value="Select...")

        self.selection_area = ctk.CTkFrame(
            self,
            width=self._field_width,
            height=height,
            fg_color=const.COLOR_WHITE,
            border_width=1,
            border_color=const.COLOR_DROPDOWN_BORDER,
            corner_radius=4,
        )

        self.selection_area.grid_propagate(False)

        self.selection_area.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.selection_area.grid_rowconfigure(0, weight=1)
        self.selection_area.grid_columnconfigure(0, weight=1)

        self.chips_inner = ctk.CTkFrame(self.selection_area, fg_color=const.COLOR_WHITE, corner_radius=0, border_width=0)
        self.chips_inner.grid(row=0, column=0, sticky="nsew", padx=self._field_inner_padding, pady=self._field_inner_padding)

        self.chips_inner.bind("<Button-1>", lambda _event: self._close_dropdown())

        arrow_img = Image.open(const.IMG_ARROW_PATH)
        arrow_ctk = ctk.CTkImage(arrow_img, size=(14,14))
        self.btn = ctk.CTkButton(
            self, image=arrow_ctk, text="", width=const.DROPDOWN_BTN_W, 
            height=self._base_height, fg_color=const.COLOR_WHITE, hover_color=const.COLOR_INACTIVE_TEXT_HOVER, 
            corner_radius=0, command=self._toggle_dropdown)
        self.btn.grid(
            row=0,
            column=1,
            sticky="n",
        )

        self._arrow_img_ref = arrow_img
        self._arrow_ctk_ref = arrow_ctk

        # close dropdown icon
        close_icon_img = Image.open(const.CLOSE_ICON_PATH)
        self.close_icon_ctk = ctk.CTkImage(close_icon_img, size=(16,16))

        self._render_selected_values()

    def _toggle_dropdown(self):
        if self._dropdown_win and self._dropdown_win.winfo_exists():
            self._close_dropdown()
        else:
            self._open_dropdown()

    def _open_dropdown(self):
        if not self.values:
            return
        
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + self._popup_gap

        win_w = self._popup_width
        win_h = self._popup_height

        try:
            screen_h = self.winfo_screenheight()

            if y + win_h > screen_h:
                win_h = max(180, screen_h - y - 8)
        except Exception:
            pass

        self._dropdown_win = ctk.CTkToplevel(self)

        parent_window = self.winfo_toplevel()
        self._dropdown_win.transient(parent_window)

        self._dropdown_win.overrideredirect(True)

        self._dropdown_win.geometry(f"{win_w}x{win_h}+{x}+{y}")

        self._dropdown_win.resizable(width=False, height=False)
     
        self._dropdown_win.minsize(win_w, win_h)
        self._dropdown_win.maxsize(win_w, win_h)

        self._dropdown_win.lift()
        self._dropdown_win.bind("<Escape>", lambda _e: self._close_dropdown())
        self._dropdown_win.after(10, lambda: self._dropdown_win.focus_set())

        # main dropdown container
        container = ctk.CTkFrame(
            self._dropdown_win,
            width=win_w,
            height=win_h,
            fg_color=const.COLOR_WHITE,
            border_width=0, 
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

        # add scroll to dropdown
        scroll = ctk.CTkScrollableFrame(
            container,
            width=win_w - 6,
            height=max(60, win_h - 52),
            fg_color=const.COLOR_WHITE,
            scrollbar_fg_color=const.COLOR_WHITE,
            scrollbar_button_color=const.COLOR_INACTIVE_TEXT_HOVER,
            scrollbar_button_hover_color=const.COLOR_DROPDOWN_BORDER,
            corner_radius=4,
            border_width=0
        )
        
        scroll.pack(
            fill="both",
            expand=True
        )

        self.option_buttons = {}

        for value in self.values:
            is_selected = value in self.selected_values

            option_button = ctk.CTkButton(
                scroll,
                text=value,
                anchor="w",
                height=36,

                fg_color=const.COLOR_WHITE,

                text_color=(
                    const.COLOR_BRAND
                    if is_selected
                    else const.COLOR_TEXT 
                ),

                hover_color=(
                    const.COLOR_INACTIVE_TEXT_HOVER
                    if is_selected
                    else const.COLOR_INACTIVE_TEXT_HOVER
                ),

                corner_radius=0,
                command=lambda current_value=value:
                    self.toggle_values(current_value)
            )

            """ option_button.pack(
                fill="x",
                padx=3,
                pady=1
            ) """

            self.option_buttons[value] = option_button

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

    def filter_options(self, *_args):
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

    def _close_dropdown(self):

        self._remove_outside_click()

        if (
            self._dropdown_win is not None
            and self._dropdown_win.winfo_exists()
        ):
            self._dropdown_win.destroy()

        self._dropdown_win = None
        self.option_buttons = {}
        self.search_entry = None
        self.no_results_label = None

    # select values
    def toggle_values(self, value):
        if value in self.selected_values:
            self.selected_values.remove(value)
        else:
            self.selected_values.append(value)

        self._sync_var()
        self._render_selected_values()
        self._refresh_option_styles()

    def remove_values(self, value):
        if value in self.selected_values:
            self.selected_values.remove(value)

        self._sync_var()
        self._render_selected_values()
        self._refresh_option_styles()

    def _sync_var(self):
        self.var.set(", ".join(self.selected_values))

    def _create_chip(self, value):
        chip = ctk.CTkFrame(
            self.chips_inner,
            width=1,
            height=self._chip_height,
            fg_color=const.COLOR_BRAND,
            bg_color=const.COLOR_WHITE,
            border_width=0,
            corner_radius=1000
        )

        chip.pack_propagate(False)

        chip_label = ctk.CTkLabel(
            chip,
            text=value,
            height=self._chip_height - 5,
            text_color=const.COLOR_WHITE,
            font=ctk.CTkFont(size=13, weight="normal"),
            fg_color="transparent",
            bg_color="transparent",
            border_width=0,
            corner_radius=0
        )
        chip_label.pack(
            side="left",
            padx=(8,0)
        )

        remove_button = ctk.CTkButton(
            chip,
            text=None,
            width=40,
            height=20,
            image=self.close_icon_ctk,
            fg_color="transparent",
            hover=False,
            border_spacing=0,
            command=lambda current_value=value:
                self.remove_values(current_value)
        )
        remove_button.pack(
            side="right",
            padx=(4,6),
            pady=1
        )

        chip.update_idletasks()

        label_width = self._reverse_widget_scaling(chip_label.winfo_reqwidth())

        button_width = self._reverse_widget_scaling(remove_button.winfo_reqwidth())

        real_width = (
            int(round(label_width + button_width + 16))
        )

        chip.configure(
            width = real_width,
            height=self._chip_height
        )

        chip.real_width = real_width

        return chip

    def _reposition_dropdown(self):
        if (
            self._dropdown_win is None
            or not self._dropdown_win.winfo_exists()
        ):
            return
        
        self.update_idletasks()

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + self._popup_gap

        self._dropdown_win.geometry(f"{self._active_popup_width}x{self._active_popup_height}+{x}+{y}")

    def _render_selected_values(self):
        for widget in self.chips_inner.winfo_children():
            widget.destroy()

        left_padding = 4

        available_width = (
            self._field_width - 8
        )

        if not self.selected_values:
            placeholder = ctk.CTkLabel(
                self.chips_inner,
                text="Select Values...",
                text_color=const.COLOR_BLACK,
                width=self._field_width - 4,
                anchor="center"
            )
            placeholder.place(
                x = 0,
                rely = 0.5,
                anchor= "w"
            )
            placeholder.bind(
                "<Button-1>",
                lambda _event: self._close_dropdown()
            )

            self._set_chips_field_size(rows_used=1)
            return
        
        active_row = 0
        current_x = left_padding

        vertical_padding = self._chip_vertical_padding

        for value in self.selected_values:
            chip = self._create_chip(value)
            chip.update_idletasks()

            chip_width = chip.real_width

            should_wrap = (
                current_x > left_padding
                and current_x + chip_width > available_width
            )

            if should_wrap:
                active_row += 1
                current_x = left_padding
            
            chip.place(
                x = current_x,
                y = (
                    vertical_padding + active_row * self._chip_row_height
                ),
            )

            current_x += chip_width + self._chip_gap
        
        rows_used = active_row + 1

        self._set_chips_field_size(rows_used=rows_used)

    def _set_chips_field_size(self, rows_used):
        target_height = (
            self._field_inner_padding * 2
            + self._chip_vertical_padding * 2
            + self._chip_height * rows_used
            + self._chip_row_gap * max(0, rows_used - 1)
        )

        self._current_height = target_height

        self.configure(height = target_height)
        self.selection_area.configure(height=target_height)

        self.after_idle(self._reposition_dropdown)
    
    # update color of list values
    def _refresh_option_styles(self):
        for value, button in self.option_buttons.items():
            if not button.winfo_exists():
                continue
            
            if value in self.selected_values:
                button.configure(
                    fg_color=const.COLOR_WHITE,
                    text_color=const.COLOR_BRAND,
                    hover_color=const.COLOR_BRAND_HOVER
                )
            else:
                button.configure(
                    fg_color=const.COLOR_WHITE,
                    text_color=const.COLOR_TEXT,
                    hover_color=const.COLOR_BRAND_HOVER
                )
    
    def get(self):
        if not self.selected_values:
            return ""
    
        return ", ".join(self.selected_values)
    
    def set_values(self, values):
        self.selected_values = values

        if self.selected_values:
            self.var.set(", ".join(self.selected_values))
        
        else:
            self.var.set("Select...")