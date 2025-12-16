from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from backend.repositories import (
    CalendarRepo,
    DiaryRepo,
    IntakePlansRepo,
    LlmRunCreate,
    LlmRunsRepo,
    MedicinesRepo,
    NotesRepo,
)


_ISO_DT_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?$")


def _parse_iso_local_dt(s: str) -> datetime:

    s = (s or "").strip()
    m = _ISO_DT_RE.match(s)
    if not m:
        raise ValueError(f"Невалидный datetime: {s!r}")
    y, mo, d, hh, mm, ss = m.groups()
    return datetime(
        int(y),
        int(mo),
        int(d),
        int(hh),
        int(mm),
        int(ss) if ss is not None else 0,
    )


def _to_iso_local(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _try_extract_mg(text: str | None) -> int | None:
    if not text:
        return None
                                       
    t = text.lower().replace(",", ".")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(mg|мг|g|гр|г)", t)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2)
    if unit in {"g", "г", "гр"}:
        val *= 1000.0
    return int(round(val))


def _safe_list(x: Any) -> list[Any]:
    return x if isinstance(x, list) else []


def _safe_dict(x: Any) -> dict[str, Any]:
    return x if isinstance(x, dict) else {}


@dataclass
class SavedPlanner:
    llm_run_id: int
    intake_plan_ids: list[int]
    calendar_event_ids: list[int]
    diary_entry_ids: list[int]
    note_ids: list[int]


def save_llm_result(
    conn: sqlite3.Connection,
    *,
    user_text: str,
    model: str,
    language: str,
    llm_json: dict,
) -> int:
    saved = save_llm_result_full(
        conn,
        user_text=user_text,
        model=model,
        language=language,
        llm_json=llm_json,
    )
    return saved.llm_run_id


def save_llm_result_full(
    conn: sqlite3.Connection,
    *,
    user_text: str,
    model: str,
    language: str,
    llm_json: dict,
) -> SavedPlanner:
                               
    llm_run_id = LlmRunsRepo(conn).create(
        LlmRunCreate(
            language=language or "ru",
            model=model or "",
            user_text=user_text or "",
            response_json=llm_json,
            status="ok",
            error_text=None,
        )
    )

                                                   
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS llm_results(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            model TEXT,
            language TEXT,
            user_text TEXT,
            llm_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "INSERT INTO llm_results(model, language, user_text, llm_json) VALUES(?,?,?,?)",
        (model, language, user_text, json.dumps(llm_json, ensure_ascii=False)),
    )
    conn.commit()

    medicines_repo = MedicinesRepo(conn)
    plans_repo = IntakePlansRepo(conn)
    calendar_repo = CalendarRepo(conn)
    diary_repo = DiaryRepo(conn)
    notes_repo = NotesRepo(conn)

    intake_plan_ids: list[int] = []
    calendar_event_ids: list[int] = []
    diary_entry_ids: list[int] = []
    note_ids: list[int] = []

                                                             
    recs = _safe_list(llm_json.get("recommendations"))
    for r in recs:
        r = _safe_dict(r)
        name = str(r.get("name") or r.get("medicine_name") or "").strip()
        if not name:
            continue
        dose_text = str(r.get("dose") or "").strip()
        dose_mg = _try_extract_mg(dose_text)
        med_id = medicines_repo.get_or_create(name=name, form=None, strength_mg=dose_mg)

        how = str(r.get("how_to_take") or "").strip()
        course = str(r.get("course") or "").strip()
        warnings = "; ".join([str(x) for x in _safe_list(r.get("warnings")) if str(x).strip()])
        contraind = "; ".join([str(x) for x in _safe_list(r.get("contraindications")) if str(x).strip()])
        interactions = "; ".join([str(x) for x in _safe_list(r.get("interactions")) if str(x).strip()])

        instructions_parts = [p for p in [dose_text, how, course] if p]
        if warnings:
            instructions_parts.append(f"Предупреждения: {warnings}")
        if contraind:
            instructions_parts.append(f"Противопоказания: {contraind}")
        if interactions:
            instructions_parts.append(f"Взаимодействия: {interactions}")

        plan_id = plans_repo.create(
            medicine_id=med_id,
            medicine_name_text=name,
            dose_mg=dose_mg,
            max_per_day_mg=None,
            instructions="\n".join(instructions_parts) if instructions_parts else None,
            start_date=None,
            end_date=None,
            times=None,
            frequency_hours=None,
            source_llm_run_id=llm_run_id,
        )
        intake_plan_ids.append(plan_id)

                                                         
    planner = _safe_dict(llm_json.get("planner"))
    events = _safe_list(planner.get("calendar_events"))
    for e in events:
        e = _safe_dict(e)
        title = str(e.get("title") or "Напоминание").strip() or "Напоминание"
        dt_str = str(e.get("datetime") or e.get("start") or "").strip()
        if not dt_str:
            continue

        try:
            start_dt = _parse_iso_local_dt(dt_str)
        except Exception:
                                                               
            try:
                start_dt = _parse_iso_local_dt(dt_str + ":00")
            except Exception:
                continue

        duration_min = e.get("duration_min")
        end_dt: datetime | None = None
        if isinstance(duration_min, (int, float)) and duration_min > 0:
            end_dt = start_dt + timedelta(minutes=int(duration_min))

        note = str(e.get("note") or e.get("notes") or "").strip() or None

        ev_id = calendar_repo.create(
            title=title,
            start_local=_to_iso_local(start_dt),
            end_local=_to_iso_local(end_dt) if end_dt else None,
            recurrence=None,
            reminders_min_before=None,
            notes=note,
            intake_plan_id=intake_plan_ids[0] if intake_plan_ids else None,
            source_llm_run_id=llm_run_id,
        )
        calendar_event_ids.append(ev_id)

                                                                                                   
                                                         
    if not calendar_event_ids and intake_plan_ids:
        try:
            planner = _safe_dict(llm_json.get("planner"))
            start_date = str(planner.get("start_date") or "").strip()
            if start_date:
                try:
                    base_date = datetime.strptime(start_date, "%Y-%m-%d")
                except Exception:
                    base_date = datetime.now()
            else:
                base_date = datetime.now()

            base_dt = base_date.replace(hour=9, minute=0, second=0, microsecond=0)
            title = None
            try:
                r0 = _safe_list(llm_json.get("recommendations"))[0]
                r0 = _safe_dict(r0)
                title = str(r0.get("name") or "").strip() or None
            except Exception:
                title = None
            title = title or "Приём лекарства"

            ev_id = calendar_repo.create(
                title=title,
                start_local=_to_iso_local(base_dt),
                end_local=None,
                recurrence=None,
                reminders_min_before=10,
                notes="Создано автоматически (уточни расписание при необходимости)",
                intake_plan_id=intake_plan_ids[0],
                source_llm_run_id=llm_run_id,
            )
            calendar_event_ids.append(ev_id)
        except Exception:
            pass

    diary = _safe_dict(planner.get("diary_entry"))
    if diary:
        body = str(diary.get("body") or diary.get("text") or "").strip()
        title = str(diary.get("title") or "").strip()
        if title and body:
            body = f"{title}\n\n{body}"
        text = body or title
        if text:
            entry_date = datetime.now().strftime("%Y-%m-%d")
            diary_entry_ids.append(diary_repo.create(entry_date=entry_date, text=text, source_llm_run_id=llm_run_id))

    notes = _safe_list(planner.get("notes"))
    for n in notes:
        n = _safe_dict(n)
        t = str(n.get("title") or "Заметка").strip() or "Заметка"
        b = str(n.get("body") or n.get("text") or "").strip() or ""
        if b:
            note_ids.append(notes_repo.create(title=t, body=b, source_llm_run_id=llm_run_id))

    return SavedPlanner(
        llm_run_id=llm_run_id,
        intake_plan_ids=intake_plan_ids,
        calendar_event_ids=calendar_event_ids,
        diary_entry_ids=diary_entry_ids,
        note_ids=note_ids,
    )