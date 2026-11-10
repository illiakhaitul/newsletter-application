import os, re, shutil, time, threading, pyglet, ctypes, queue
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from app.app import App
from common.common import *
from scripts.scripts import *

load_result = queue.Queue()
loading_finished = False

def load_hierarchy():
    try:
        # check if Tabelle2.xlsx is downloaded
        database_path = abs_path("resources/database/Tabelle2.xlsx")

        if not database_path.is_file():
            raise FileNotFoundError(
                f"Product hierarchy database now found:\n"
                f"{database_path}\n\n"
                "Please see resources/database/README.md"
            )
        
        hierarchy = ProductHierarchy(resource_path("resources/database/Tabelle2.xlsx"))
        load_result.put(("success", hierarchy))
    except Exception as error:
        load_result.put(("error", error))

def update_loading_progress(percent, text):
    if loading_finished:
        return
    
    if not splash.winfo_exists():
        return
    
    splash.feedback_var.set(text)
    splash.percent_var.set(f"{percent}%")
    splash.progress.set(percent/100)

def start_background_loading():
    if not root.useTabelle:
        splash.feedback_var.set("Tabelle disabled. Initializing the app...")
        splash.percent_var.set("80%")
        splash.progress.set(0.8)

        root.after(50, lambda: initialize_application(None))
        
        return
    
    splash.feedback_var.set("Loading database...")
    splash.percent_var.set("10%")
    splash.progress.set(0.1)

    # show 40%
    root.after(6000, lambda: update_loading_progress(35, "Loading components..."))

    # show 60%
    root.after(10000, lambda: update_loading_progress(65, "Loading data..."))

    worker = threading.Thread(target=load_hierarchy, daemon=True)
    worker.start()
    
    root.after(50, check_loading_result)

def check_loading_result():
    global loading_finished

    try:
        status, result = load_result.get_nowait()
    except queue.Empty:
        root.after(50, check_loading_result)
        return
    
    loading_finished = True
    
    if status == "error":
        handle_loading_error(result)
        return
    
    hierarchy = result

    splash.feedback_var.set("Initializing UI...")
    splash.percent_var.set("80%")
    splash.progress.set(0.8)

    root.after(50, lambda: initialize_application(hierarchy))

def initialize_application(hierarchy):
    try:
        root.initialize(hierarchy)
    except Exception as error:
        handle_loading_error(error)
        return
    
    splash.feedback_var.set("Ready")
    splash.percent_var.set("100%")
    splash.progress.set(1.0)

    root.after(100, show_application)

def show_application():
    splash.close()
    root.deiconify()
    

def handle_loading_error(error):
    splash.feedback_var.set("Loading Failed")

    messagebox.showerror(
        title="Startup error",
        message=f"Could not load Tabelle2:\n\n{error}",
        parent=splash,
    )

    splash.close()
    root.after(100, root.destroy)

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = App()
    
    splash = LoadingSplashScreen(root)

    root.after(50, start_background_loading)

    root.mainloop()