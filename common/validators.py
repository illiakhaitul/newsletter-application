import re

def parse_month_year(s: str):
    s = s.strip()
    if not re.fullmatch(r"\d{2}\.\d{4}", s):
        raise ValueError("Data should be in format MM.YYYY")
    mm, yyyy = map(int, s.split("."))
    if not (1 <= mm <= 12):
        raise ValueError("The month should be between 1-12")
    return mm, yyyy

def validator_header(header: str, regex: str):
    if not re.fullmatch(regex, header):
        raise ValueError(f"Header 'header' does not match the mask")
    
def is_http_url(s: str) -> bool:
    return bool(re.fullmatch(r"https?://\S+", (s or "").strip()))