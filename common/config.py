import os, sys, yaml
from pathlib import Path

def resource_path(relative_path: str) -> Path:
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    
    return Path(relative_path)

def _app_root():
    if getattr(sys, "frozen", False) and hasattr(sys, "executable"):
        return Path(sys.executable).resolve().parent
    
    try:
        import __main__
        return Path(__main__.__file__).resolve().parent
    except Exception:
        return Path.cwd()
    
BASE = _app_root()

def abs_path(rel) -> Path:
    p = Path(rel)
    return p if p.is_absolute() else (BASE / p).resolve()


config_path = resource_path("resources/config.yaml")


with open(config_path, encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
