import json
from pathlib import Path

def config_path() -> Path:
    # находим корень проекта по файлу main.py
    root = Path(__file__).resolve().parents[1]  # backend/ -> проект
    return root / "llm_config.json"

def load_file_config() -> dict:
    p = config_path()
    print("llm_config path:", p, "exists:", p.exists())
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
