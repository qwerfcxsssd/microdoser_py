import os
import sqlite3

from backend.schema import SCHEMA_VERSION, SCHEMA_V1_SQL
from backend.settings import get_setting, set_setting

DB_FILENAME = "microdoser.sqlite3"


def _project_root() -> str:
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(backend_dir)


def connect(db_path: str | None = None) -> sqlite3.Connection:
    """
    Локальная SQLite БД.
    По умолчанию кладём файл в корень проекта (рядом с main.py).
    """
    if db_path is None:
        db_path = os.path.join(_project_root(), DB_FILENAME)

    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Инициализация и миграции БД (безопасно вызывать много раз)."""
                                                                                
    conn.executescript(SCHEMA_V1_SQL)

                                           
    cur_ver = get_setting(conn, "schema_version", "")
    if str(cur_ver).strip() != str(SCHEMA_VERSION):
        set_setting(conn, "schema_version", str(SCHEMA_VERSION))
