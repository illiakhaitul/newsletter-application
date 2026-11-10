from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from openpyxl import Workbook

METADATA_HEADERS: List[str] = [
    "Entity Identifier",
    "EntityType Identifier",
    "Categories",
    "Asset Status (dc_asset_status;de)",
    "Asset Status (dc_asset_status;en)",
    "Asset Titel (title;de)",
    "Asset Titel (title;en)",
    "Beschreibung (description;de)",
    "Beschreibung (description;en)",
    "DC Release Channel (dc_release_channel)",
    "DC Country (dc_country)",
    "Target Group (dc_target_group)",
    "Business Unit (dc_bu)",
    "Tags / Keywords (dc_keywords)",
    "Medientyp (dc_media_type;de)",
    "Medientyp (dc_media_type;en)",
    "DC PageID (dc_page_id)",
    "DC PageID Path (dc_page_id_path)",
]

def get_metadata_language(lang: str) -> List[str]:
    lang_lower = lang.lower()

    headers = METADATA_HEADERS.copy()

    if lang_lower == "de":
        headers.insert(16, "Sprache (dc_languages;de)")

    if lang_lower == "en":
        headers.insert(16, "Sprache (dc_languages;en)")

    return headers
    
def get_value(metadata: Optional[Dict[str, str]], key: str, default_value: str = "") -> str:
    if metadata is None:
        return default_value
    
    value = metadata.get(key, "").strip()

    if value:
        return value
    
    return default_value

def build_metadata_values(
        *,
        thema: str,
        lang: str,
        typ: str,
        bu: str,
        dc_page_id_path: str | None,
        dc_page_id: str | None,
        metadata: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    
    lang_lower = lang.lower()
    language_column = ""

    if lang_lower == "de":
        language_column = "Sprache (dc_languages;de)"
        language_value = "Deutsch"
    else: 
        language_column = "Sprache (dc_languages;en)"
        language_value = "English"

    """ return {
        "Entity Identifier": "",
        "EntityType Identifier": "AssetSet",
        "Categories": "dc_at",
        "Asset Status (dc_asset_status;de)": "",
        "Asset Status (dc_asset_status;en)": "",
        "Asset Titel (title;de)": thema or "",
        "Asset Titel (title;en)": thema or "",
        "Beschreibung (description;de)": thema or "",
        "Beschreibung (description;en)": thema or "",
        "DC Release Channel (dc_release_channel)": "",
        "DC Country (dc_country)": "XC - International",
        "Target Group (dc_target_group)": "employees",
        "Business Unit (dc_bu)": "AT",
        "Tags / Keywords (dc_keywords)": "Hägglunds",
        "Medientyp (dc_media_type;de)": "Newsletter",
        "Medientyp (dc_media_type;en)": "Newsletter",
        "Sprache (dc_languages;de)": "Deutsch",
        "DC PageID (dc_page_id)": dc_page_id or "",
        "DC PageID Path (dc_page_id_path)": dc_page_id_path or "",
    } """

    return {
        "Entity Identifier": "",

        "EntityType Identifier": "AssetSet",
        
        "Categories": "dc_at",
        
        "Asset Status (dc_asset_status;de)": "Active",
        
        "Asset Status (dc_asset_status;en)": "Active",
        
        "Asset Titel (title;de)": thema or "",
        
        "Asset Titel (title;en)": thema or "",
        
        "Beschreibung (description;de)": thema or "",
        
        "Beschreibung (description;en)": thema or "",
        
        "DC Release Channel (dc_release_channel)": "Download Center / myRexroth",

        # TODO: only a single-option for DC COUNTRY
        "DC Country (dc_country)": get_value(metadata, "country", ""),

        # TODO: only a multiple-option for TARGET GROUP
        "Target Group (dc_target_group)": get_value(metadata, "target_group", ""),

        # TODO: only a single-option for Business UNIT
        "Business Unit (dc_bu)": "AT",

        # TODO: only a multiple-option for TAGS / KEYw
        "Tags / Keywords (dc_keywords)": get_value(metadata, 
        "keywords", ""),
        
        "Medientyp (dc_media_type;de)": "Newsletter",
        
        "Medientyp (dc_media_type;en)": "Newsletter",
        
        language_column: language_value,
        
        "DC PageID (dc_page_id)": dc_page_id or "",
        
        "DC PageID Path (dc_page_id_path)": dc_page_id_path or "",
    }


def generate_metadata(*, out_dir: Path, thema: str, lang: str, typ: str, bu: str, dc_page_id_path: str | None, dc_page_id: str | None, metadata: Optional[Dict[str, str]] = None) -> Path:
    metadata_dir = out_dir / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    out_file = metadata_dir / f"Metadata_{lang}_{date_str}.xlsx"

    values = build_metadata_values(
        thema=thema,
        lang=lang,
        typ=typ,
        bu=bu,
        dc_page_id_path=dc_page_id_path,
        dc_page_id=dc_page_id,
        metadata=metadata,
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Metadata"

    headers = get_metadata_language(lang)

    # headers
    for col_idx, field in enumerate(headers, start=1):
        ws.cell(row=1, column=col_idx, value=field)
    
    # values
    for col_idx, field in enumerate(headers, start=1):
        ws.cell(row=2, column=col_idx, value=values.get(field, ""))

    wb.save(out_file)
    return out_file