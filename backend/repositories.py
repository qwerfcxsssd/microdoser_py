import json
import sqlite3
from dataclasses import dataclass
from typing import Any


@dataclass
class LlmRunCreate:
    language: str
    model: str
    user_text: str
    response_json: dict[str, Any]
    status: str = "ok"
    error_text: str | None = None

class LlmRunsRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, item: LlmRunCreate) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO llm_runs(language, model, user_text, response_json, status, error_text)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                item.language,
                item.model,
                item.user_text,
                json.dumps(item.response_json, ensure_ascii=False),
                item.status,
                item.error_text,
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

class MedicinesRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_or_create(self, name: str, form: str | None, strength_mg: int | None) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id FROM medicines
            WHERE name = ? AND IFNULL(form,'') = IFNULL(?, '') AND IFNULL(strength_mg,-1) = IFNULL(?, -1)
            """,
            (name, form, strength_mg),
        )
        row = cur.fetchone()
        if row:
            return int(row["id"])

        cur.execute(
            "INSERT INTO medicines(name, form, strength_mg) VALUES (?, ?, ?)",
            (name, form, strength_mg),
        )
        self.conn.commit()
        return int(cur.lastrowid)

class IntakePlansRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(
        self,
        *,
        medicine_id: int | None,
        medicine_name_text: str,
        dose_mg: int | None,
        max_per_day_mg: int | None,
        instructions: str | None,
        start_date: str | None,
        end_date: str | None,
        times: list[str] | None,
        frequency_hours: int | None,
        source_llm_run_id: int | None,
    ) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO intake_plans(
              medicine_id, medicine_name_text, dose_mg, max_per_day_mg,
              instructions, start_date, end_date, times_json, frequency_hours,
              source_llm_run_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                medicine_id,
                medicine_name_text,
                dose_mg,
                max_per_day_mg,
                instructions,
                start_date,
                end_date,
                json.dumps(times, ensure_ascii=False) if times else None,
                frequency_hours,
                source_llm_run_id,
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

class CalendarRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(
        self,
        *,
        title: str,
        start_local: str,
        end_local: str | None,
        recurrence: dict | None,
        reminders_min_before: list[int] | None,
        notes: str | None,
        intake_plan_id: int | None,
        source_llm_run_id: int | None,
    ) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO calendar_events(
              title, start_local, end_local, recurrence_json, reminders_json, notes,
              intake_plan_id, source_llm_run_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                start_local,
                end_local,
                json.dumps(recurrence, ensure_ascii=False) if recurrence else None,
                json.dumps(reminders_min_before, ensure_ascii=False) if reminders_min_before else None,
                notes,
                intake_plan_id,
                source_llm_run_id,
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def list_between(self, start_local: str, end_local: str) -> list[sqlite3.Row]:

        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT * FROM calendar_events
            WHERE start_local >= ? AND start_local <= ?
            ORDER BY start_local ASC, id ASC
            """,
            (start_local, end_local),
        )
        return cur.fetchall()


class DiaryRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, entry_date: str, text: str, source_llm_run_id: int | None) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO diary_entries(entry_date, text, source_llm_run_id) VALUES (?, ?, ?)",
            (entry_date, text, source_llm_run_id),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def list_between(self, start_date: str, end_date: str) -> list[sqlite3.Row]:

        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT * FROM diary_entries
            WHERE entry_date >= ? AND entry_date <= ?
            ORDER BY entry_date ASC, id ASC
            """,
            (start_date, end_date),
        )
        return cur.fetchall()

class NotesRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, title: str, body: str, source_llm_run_id: int | None) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO notes(title, body, source_llm_run_id) VALUES (?, ?, ?)",
            (title, body, source_llm_run_id),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def list_recent(self, limit: int = 50) -> list[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT * FROM notes
            ORDER BY updated_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cur.fetchall()
