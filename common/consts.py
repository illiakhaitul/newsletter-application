import customtkinter as ctk
from common.common import *
from scripts.scripts import *

# window geometry
APP_TITLE = "Newsletter Application"
BASE_GEOMETRY = "584x715"
BASE_W, BASE_H = 584, 715

# input values
TYP_value = "NEWSLETTER"

# basic colors
COLOR_WHITE = "white"
COLOR_BLACK = "black"
COLOR_TEXT = "#000000"
# Color brand #3094ff
COLOR_TEXT_BRAND = "#687286"
COLOR_INACTIVE_TEXT_HOVER = "#fafafa"
COLOR_BRAND = "#007BC0"
COLOR_BRAND_BORDER = "#eaecf6"
COLOR_BRAND_HOVER = "#e5f6fb"
COLOR_ENTRY_BG = "#E0E0E0"
COLOR_ENTRY_HOVER = "#D0D0D0"
COLOR_FILE_LABEL = "#687286"
COLOR_DROPDOWN_ITEM_HOVER = "#fafafa"

# dropdown colors
COLOR_DROPDOWN_BORDER = "#e6e6e8"

# splash screen
DIVIDER_COLOR = "#D0D0D0"
PROGRESS_COLOR = "#007bc0"

# content block sizes
DROPDOWN_WIDTH = 200
DROPDOWN_HEIGHT = 35
DROPDOWN_BTN_W = 30
DROPDOWN_POPUP_W = 700
DROPDOWN_POPUP_H = 400

# Title splash screen consts
CLOSE_DELAY = 2000
ANIMATION_DELAY = 50

# local img path
IMG_HEADER_PATH = resource_path("resources/imgs/header.png")
IMG_ARROW_PATH = resource_path("resources/imgs/scroll.png")
IMG_ICON_PATH = resource_path("resources/imgs/icon_main.png")
CLOSE_ICON_PATH = resource_path("resources/imgs/close-icon.png")
COPY_ICON = resource_path("resources/imgs/copy.png")

# popup menu icons
OPEN_POPUP_ICON = resource_path("resources/imgs/open_popup_icon.png")
CLOSE_POPUP_ICON = resource_path("resources/imgs/close_popup_icon.png")