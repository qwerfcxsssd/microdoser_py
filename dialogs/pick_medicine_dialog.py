import os
import sqlite3
from typing import Any
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QTextEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread

                                                                     
                                                     
_BACKEND_MODE = None
try:
                           
    from backend.llm_service import OpenRouterDeepSeekClient, DEFAULT_MODEL                
    _BACKEND_MODE = "client"
except Exception:
    OpenRouterDeepSeekClient = None                
    try:
                          
        from backend.llm_service import ask_openrouter_json, DEFAULT_MODEL                
        _BACKEND_MODE = "func"
    except Exception as e:
        raise ImportError(
            "Не найден backend.llm_service. Нужно чтобы был либо OpenRouterDeepSeekClient, "
            "либо ask_openrouter_json()."
        ) from e


                                      
try:
    from backend.settings import get_setting                
except Exception:
    def get_setting(conn: sqlite3.Connection | None, key: str, default=None):
        if conn is None:
            return default
        conn.execute("CREATE TABLE IF NOT EXISTS app_settings(key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        cur = conn.execute("SELECT value FROM app_settings WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else default


def _safe_list(x) -> list[str]:
    if isinstance(x, list):
        return [str(i) for i in x if str(i).strip()]
    return []


def _prune_to_single_recommendation(data: dict) -> dict:
    """Гарантирует, что в UI/сохранение пойдёт ровно ОДНА рекомендация.

    Некоторые модели могут вернуть 2–3 варианта, даже если мы просили один.
    Мы не хотим показывать/добавлять несколько вариантов — поэтому жёстко
    оставляем только первый элемент списка.
    """
    if not isinstance(data, dict):
        return data

                             
    recs = data.get("recommendations")
    if isinstance(recs, list):
        if recs:
            data["recommendations"] = [recs[0]]
        else:
            data["recommendations"] = []
        return data

                                         
    recs2 = data.get("medicines")
    if isinstance(recs2, list):
        if recs2:
            data["medicines"] = [recs2[0]]
        else:
            data["medicines"] = []

    return data

def _ensure_min_calendar_event(data: dict, start_date: str | None) -> dict:
    """Если LLM вернул пустой planner.calendar_events — добавим минимум одно событие.

    Это нужно, чтобы кнопка «Добавить» всегда реально добавляла что-то в календарь/напоминания.
    """
    if not isinstance(data, dict):
        return data

    sd = (start_date or "").strip()
    if not sd:
        return data

    planner = data.get("planner")
    if not isinstance(planner, dict):
        planner = {}
        data["planner"] = planner

    events = planner.get("calendar_events")
    if not isinstance(events, list):
        events = []
        planner["calendar_events"] = events

    if len(events) == 0:
        events.append({
            "title": "Приём лекарства",
            "datetime": f"{sd}T09:00",
            "duration_min": 5,
            "note": "Сформировано автоматически",
        })

                                      
    if sd and isinstance(planner, dict) and "start_date" not in planner:
        planner["start_date"] = sd

    return data



def _format_llm_json_ru(data: dict) -> str:
    """
    Красивый вывод: лекарство + особенности + курс + предупреждения.
    Поддерживает разные ключи, если модель вернула чуть другую структуру.
    """
    ui = data.get("ui_hints") or {}
    triage = data.get("triage") or {}
    recs = data.get("recommendations") or data.get("medicines") or []

    lines: list[str] = []

    summary = (ui.get("summary") or "").strip()
    if summary:
        lines.append(f"Сводка: {summary}")

    when = (triage.get("when_to_seek_help") or "").strip()
    red_flags = _safe_list(triage.get("red_flags"))

    if red_flags:
        lines.append("")
        lines.append("Тревожные признаки (лучше обратиться к врачу):")
        for rf in red_flags:
            lines.append(f"• {rf}")

    if when:
        lines.append("")
        lines.append(f"Когда обратиться к врачу: {when}")

    if not isinstance(recs, list) or not recs:
                                             
        fallback = data.get("text") or data.get("answer")
        if isinstance(fallback, str) and fallback.strip():
            lines.append("")
            lines.append(fallback.strip())
        else:
            lines.append("")
            lines.append("Не удалось получить конкретное лекарство. Попробуй уточнить симптомы.")
        return "\n".join(lines).strip()

    lines.append("")
    lines.append("Рекомендованное лекарство (проверь противопоказания!):")

    for idx, r in enumerate(recs, start=1):
        if idx > 1:
            break
        if not isinstance(r, dict):
            continue

        name = (r.get("name") or r.get("medicine_name") or r.get("drug") or "").strip()
        if not name:
            continue

        purpose = (r.get("purpose") or "").strip()
        dose = (r.get("dose") or "").strip()
        how = (r.get("how_to_take") or r.get("instructions") or "").strip()
        course = (r.get("course") or r.get("duration") or "").strip()
        max_day = (r.get("max_per_day") or r.get("max_per_day_mg") or "").strip()

        features = _safe_list(r.get("features"))
        warnings = _safe_list(r.get("warnings"))
        contraind = _safe_list(r.get("contraindications"))
        interactions = _safe_list(r.get("interactions"))

        lines.append("")
        lines.append(f"{idx}) {name}")
        if purpose:
            lines.append(f"   • Для чего: {purpose}")
        if dose:
            lines.append(f"   • Дозировка: {dose}")
        if how:
            lines.append(f"   • Как принимать: {how}")
        if course:
            lines.append(f"   • Курс: {course}")
        if max_day:
            lines.append(f"   • Максимум в сутки: {max_day}")

        if features:
            lines.append("   • Особенности:")
            for f in features:
                lines.append(f"     - {f}")

        if warnings:
            lines.append("   • Предупреждения:")
            for w in warnings:
                lines.append(f"     - {w}")

        if contraind:
            lines.append("   • Противопоказания:")
            for c in contraind:
                lines.append(f"     - {c}")

        if interactions:
            lines.append("   • Взаимодействия:")
            for it in interactions:
                lines.append(f"     - {it}")

    disclaimer = (data.get("disclaimer") or "").strip()
    if disclaimer:
        lines.append("")
        lines.append(disclaimer)

                                                       
    if not disclaimer:
        lines.append("")
        lines.append("Важно: это справочная информация, не диагноз. При сомнениях/ухудшении — к врачу.")

    return "\n".join(lines).strip()


class _BackendLlmWorker(QObject):
    ok = Signal(dict)
    err = Signal(str)
    finished = Signal()

    def __init__(self, api_key: str, model: str, language: str, user_text: str, start_date: str | None = None):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.language = language
        self.user_text = user_text
        self.start_date = start_date

    def run(self):
        try:
                                                                                      
            start_date = (self.start_date or "").strip() or datetime.now().strftime("%Y-%m-%d")
            user_payload = (
                f"{self.user_text}\n\n"
                f"Стартовая дата плана: {start_date}.\n"
                "Требования:\n"
                "1) Предложи РОВНО 1 вариант (если уместно — безрецептурный).\n"
                "2) Заполни recommendations[0] (name, dose, how_to_take, course, warnings/contraindications/interactions).\n"
                "3) В planner.calendar_events создай напоминания минимум на 3–7 дней; datetime строго YYYY-MM-DDTHH:MM (абсолютная дата), начиная со стартовой даты.\n"
                "4) Верни ТОЛЬКО один валидный JSON по схеме, без markdown и текста вне JSON."
            )

            if _BACKEND_MODE == "client":
                client = OpenRouterDeepSeekClient(api_key=self.api_key)                
                data = client.get_json_plan(                
                    model=self.model,
                    language=self.language,
                    user_text=user_payload
                )
            else:
                                         
                data = ask_openrouter_json(                
                    api_key=self.api_key,
                    model=self.model,
                    language=self.language,
                    user_text=user_payload
                )

            if not isinstance(data, dict):
                raise ValueError("backend.llm_service вернул не dict")

            self.ok.emit(data)

        except Exception as e:
            self.err.emit(str(e))
        finally:
            self.finished.emit()


class PickMedicineDialog(QDialog):
    def __init__(self, font_title: str, font_text: str, conn: sqlite3.Connection | None = None, start_date: str | None = None, parent=None):
        super().__init__(parent)

        self.font_title = font_title
        self.font_text = font_text
        self.conn = conn
        self.start_date = start_date

        self.llm_json: dict | None = None
        self._used_model = DEFAULT_MODEL
        self._used_language = "ru"

        self._thread: QThread | None = None
        self._worker: _BackendLlmWorker | None = None
        self._busy = False

        self.setModal(True)
        self.setWindowTitle("Подобрать лекарство")
        self.setFixedSize(1300, 760)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: rgba(90,90,90,255);
            }}
            QLabel {{
                color: rgba(240,240,240,240);
                font-family: '{self.font_text}';
            }}
            QLineEdit, QTextEdit {{
                background: transparent;
                border: none;
                outline: none;
                color: rgba(245,245,245,240);
                font-size: 18px;
                font-family: '{self.font_text}';
            }}
            QTextEdit::viewport {{
                background: transparent;
                border: none;
            }}
            QLineEdit::placeholderText, QTextEdit::placeholderText {{
                color: rgba(240,240,240,140);
            }}
            QPushButton {{
                border: none;
                border-radius: 16px;
                font-size: 18px;
                color: white;
                font-family: '{self.font_text}';
                padding: 12px 18px;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 24)
        root.setSpacing(18)

        title = QLabel("Подобрать лекарство")
        title_font = QFont(self.font_title, 26)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        root.addWidget(title)

        lbl1 = QLabel("Введите свои симптомы")
        lbl1.setFont(QFont(self.font_text, 14))
        root.addWidget(lbl1)

        search_panel, self.search = self._make_line_panel("Например: головная боль, температура", height=70)
        root.addWidget(search_panel)

        lbl2 = QLabel("Результат подбора:")
        lbl2.setFont(QFont(self.font_text, 14))
        root.addWidget(lbl2)

        result_panel, self.result = self._make_text_panel("Здесь появится: лекарство, особенности и курс", height=380)
        root.addWidget(result_panel)

        root.addStretch()

        bottom = QHBoxLayout()

        bottom_label = QLabel("Добавить это лекарство?")
        bottom_font = QFont(self.font_text, 15)
        bottom_font.setWeight(QFont.Weight.DemiBold)
        bottom_label.setFont(bottom_font)
        bottom_label.setStyleSheet("color: rgba(240,240,240,210);")

        bottom.addWidget(bottom_label)
        bottom.addStretch()

        self.pick_btn = QPushButton("Подобрать")
        self.pick_btn.setCursor(Qt.PointingHandCursor)
        self.pick_btn.setFixedSize(190, 56)
        self.pick_btn.setStyleSheet("background-color: rgba(90,90,90,210);")
        self.pick_btn.clicked.connect(self._on_pick_clicked)

        self.add_button = QPushButton("Добавить")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setFixedSize(160, 56)
        self.add_button.setStyleSheet("background-color: rgba(131,123,228,255);")
        self.add_button.setEnabled(False)
        self.add_button.clicked.connect(self.accept)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedSize(190, 56)
        cancel_btn.setStyleSheet("background-color: rgba(120,120,120,210);")
        cancel_btn.clicked.connect(self.reject)

        bottom.addWidget(self.pick_btn)
        bottom.addWidget(self.add_button)
        bottom.addWidget(cancel_btn)

        root.addLayout(bottom)

    def _panel_style(self) -> str:
        return "QWidget { background-color: rgba(120,120,120,190); border-radius: 14px; }"

    def _make_line_panel(self, placeholder: str, height: int):
        panel = QWidget()
        panel.setStyleSheet(self._panel_style())
        panel.setFixedHeight(height)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(height)
        edit.setStyleSheet("QLineEdit { padding-left: 18px; padding-right: 18px; }")

        layout.addWidget(edit)
        return panel, edit

    def _make_text_panel(self, placeholder: str, height: int):
        panel = QWidget()
        panel.setStyleSheet(self._panel_style())
        panel.setFixedHeight(height)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        edit = QTextEdit()
        edit.setPlaceholderText(placeholder)
        edit.setReadOnly(True)
        edit.setFocusPolicy(Qt.NoFocus)
        edit.setCursor(Qt.ArrowCursor)
        edit.setFrameStyle(QTextEdit.NoFrame)
        edit.setStyleSheet("QTextEdit { padding: 10px 18px; }")

        layout.addWidget(edit)
        return panel, edit

                                                                   
    def get_user_text(self) -> str:
        return self.search.text().strip()

    def get_llm_json(self):
        return self.llm_json

    def get_language(self) -> str:
        return self._used_language

    def get_model_name(self) -> str:
        return self._used_model

                      
    def _resolve_conn(self) -> sqlite3.Connection | None:
        if self.conn is not None:
            return self.conn
        return getattr(self.parent(), "conn", None)

    def _read_llm_settings(self) -> tuple[str, str, str]:
        conn = self._resolve_conn()
        api_key = (get_setting(conn, "openrouter_api_key", "") or "").strip()
        model = (get_setting(conn, "llm_model", DEFAULT_MODEL) or DEFAULT_MODEL).strip()
        language = (get_setting(conn, "language", "ru") or "ru").strip()

        if not api_key:
            api_key = os.getenv("OPENROUTER_API_KEY", "").strip()

        return api_key, model, language

    @Slot(dict)
    def _handle_ok(self, data: dict):
        data = _prune_to_single_recommendation(data)
        data = _ensure_min_calendar_event(data, self.start_date)
        self.llm_json = data
        self._busy = False
        self.pick_btn.setEnabled(True)
        self.add_button.setEnabled(True)
        self.result.setPlainText(_format_llm_json_ru(data))

    @Slot(str)
    def _handle_err(self, msg: str):
        self.llm_json = None
        self._busy = False
        self.pick_btn.setEnabled(True)
        self.add_button.setEnabled(False)
        self.result.setPlainText(f"Ошибка LLM: {msg}")

    @Slot()
    def _cleanup_thread(self):
        self._worker = None
        self._thread = None

    def _on_pick_clicked(self):
        if self._busy:
            return

        symptoms = self.search.text().strip()
        if not symptoms:
            self.result.setPlainText("Введите симптомы.")
            return

        api_key, model, language = self._read_llm_settings()
        if not api_key:
            self.result.setPlainText("Не задан API key. Открой Настройки → LLM / API и вставь ключ.")
            return

                                                    
        self._used_model = model
        self._used_language = language

                  
        self._busy = True
        self.llm_json = None
        self.pick_btn.setEnabled(False)
        self.add_button.setEnabled(False)
        self.result.setPlainText("Подбираю…")

                
        self._thread = QThread()
        self._worker = _BackendLlmWorker(
            api_key=api_key,
            model=model,
            language=language,
            user_text=f"Симптомы: {symptoms}",
            start_date=self.start_date,
        )
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.ok.connect(self._handle_ok, Qt.ConnectionType.QueuedConnection)
        self._worker.err.connect(self._handle_err, Qt.ConnectionType.QueuedConnection)

        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._cleanup_thread)

        self._thread.start()

    def reject(self):
                                                         
        if self._busy:
            self.result.setPlainText("Запрос выполняется… подожди, пожалуйста.")
            return
        super().reject()