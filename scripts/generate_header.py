import re
from common.common import *

def build_header(next_num: int, mm: int, yyyy: int) -> str:
    return cfg["HEADER_MASK"].format(num=next_num, pg=cfg["PRODUCT_GROUP"], mm=f"{mm:02d}", yyyy=yyyy)

def header_core_for_display(header: str) -> str:
    header_clean = (header or "").strip()

    header_clean = re.sub(r"/[^_]*(?=_)", "", header_clean, count=1)

    return re.sub(r"[\s_\-]*\d{2}\.\d{4}\s*$", "", header_clean)

def make_header(date_str: str, latest_num: int | None) -> str:
    mm, yyyy = parse_month_year(date_str)
    num = (latest_num or 0) + 1 
    h = build_header(num, mm, yyyy)
    validator_header(h, cfg["HEADER_REGEX"])
    return h