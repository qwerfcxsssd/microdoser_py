from __future__ import annotations

"""Экспорт событий в системные macOS Calendar/Reminders (best-effort).

⚠️ Работает только на macOS (sys.platform == 'darwin').
При первом запуске система запросит разрешение на доступ к Calendar/Reminders.

Реализация через AppleScript (osascript), чтобы не тянуть PyObjC.
"""

import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional


@dataclass
class MacEvent:
    title: str
    start_local: str                            
    end_local: Optional[str] = None
    notes: Optional[str] = None


def _parse_iso(s: str) -> datetime:
                                                                  
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")


def _osascript(lines: list[str]) -> None:
    if sys.platform != "darwin":
        raise RuntimeError("macOS export доступен только на macOS.")
    cmd = ["osascript"]
    for ln in lines:
        cmd += ["-e", ln]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        msg = (res.stderr or res.stdout or "").strip()
        raise RuntimeError(msg or "osascript failed")


def export_to_calendar(
    events: Iterable[MacEvent],
    *,
    calendar_name: str = "Micro Doser",
) -> None:
    """Создаёт/находит календарь и добавляет события."""
    evs = list(events)
    if not evs:
        return

    cal_esc = (calendar_name or "Micro Doser").replace('"', '\\"')

    lines: list[str] = [
        'tell application "Calendar"',
        f'  set calName to "{cal_esc}"',
        '  set mlist to {January, February, March, April, May, June, July, August, September, October, November, December}',
        '  if not (exists calendar calName) then',
        '    make new calendar with properties {name:calName}',
        '  end if',
        '  tell calendar calName',
    ]

    for e in evs:
        start = _parse_iso(e.start_local)
        end = _parse_iso(e.end_local) if e.end_local else start
        title = e.title.replace('"', '\\"')
        notes = (e.notes or "").replace('"', '\\"')

                                                 
        lines += [
            '    set d1 to current date',
            f'    set year of d1 to {start.year}',
            f'    set month of d1 to (item {start.month} of mlist)',
            f'    set day of d1 to {start.day}',
            f'    set hours of d1 to {start.hour}',
            f'    set minutes of d1 to {start.minute}',
            '    set seconds of d1 to 0',
            '    set d2 to current date',
            f'    set year of d2 to {end.year}',
            f'    set month of d2 to (item {end.month} of mlist)',
            f'    set day of d2 to {end.day}',
            f'    set hours of d2 to {end.hour}',
            f'    set minutes of d2 to {end.minute}',
            '    set seconds of d2 to 0',
            f'    make new event with properties {{summary:"{title}", start date:d1, end date:d2, description:"{notes}"}}',
        ]

    lines += ['  end tell', 'end tell']
    _osascript(lines)


def export_to_reminders(
    reminders: Iterable[MacEvent],
    *,
    list_name: str = "Micro Doser",
) -> None:
    """Создаёт/находит список Reminders и добавляет напоминания."""
    rms = list(reminders)
    if not rms:
        return

    list_esc = (list_name or "Micro Doser").replace('"', '\\"')

    lines: list[str] = [
        'tell application "Reminders"',
        f'  set listName to "{list_esc}"',
        '  set mlist to {January, February, March, April, May, June, July, August, September, October, November, December}',
        '  if not (exists list listName) then',
        '    make new list with properties {name:listName}',
        '  end if',
        '  tell list listName',
    ]

    for r in rms:
        due = _parse_iso(r.start_local)
        title = r.title.replace('"', '\\"')
        body = (r.notes or "").replace('"', '\\"')
        lines += [
            '    set d to current date',
            f'    set year of d to {due.year}',
            f'    set month of d to (item {due.month} of mlist)',
            f'    set day of d to {due.day}',
            f'    set hours of d to {due.hour}',
            f'    set minutes of d to {due.minute}',
            '    set seconds of d to 0',
            f'    make new reminder with properties {{name:"{title}", due date:d, body:"{body}"}}',
        ]

    lines += ['  end tell', 'end tell']
    _osascript(lines)
