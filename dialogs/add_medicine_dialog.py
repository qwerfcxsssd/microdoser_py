from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QTextEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from backend.llm_service import resolve_llm_settings


class AddMedicineDialog(QDialog):
    def __init__(self, font_title: str, font_text: str, parent=None):
        super().__init__(parent)

        self.font_title = font_title
        self.font_text = font_text

        self.font_title = font_title
        self.font_text = font_text

        self.llm_json = None

        self.setModal(True)
        self.setWindowTitle("Добавить лекарство")
        self.setFixedSize(975, 631)

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
                font-size: 14px;
                font-family: '{self.font_text}';
            }}

            QTextEdit::viewport {{
                background: transparent;
                border: none;
            }}

            QLineEdit::placeholder, QTextEdit::placeholder {{
                color: rgba(240,240,240,140);
            }}

            QPushButton {{
                border: none;
                border-radius: 16px;
                font-size: 14px;
                color: white;
                font-family: '{self.font_text}';
                padding: 12px 18px;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 24)
        root.setSpacing(18)


        title = QLabel("Добавить лекарство")
        title_font = QFont(self.font_title, 22)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        root.addWidget(title)


        lbl1 = QLabel("Введите название лекарства и дозировку в мг")
        lbl1.setFont(QFont(self.font_text, 10))
        root.addWidget(lbl1)

        name_panel, self.name_dose = self._make_line_panel(
            "Например: Ибупрофен 200 мг",
            height=58
        )
        root.addWidget(name_panel)


        lbl2 = QLabel("Информация о лекарстве:")
        lbl2.setFont(QFont(self.font_text, 10))
        root.addWidget(lbl2)

        info_panel, self.info = self._make_text_panel(
            "Например: как принимать, курс, противопоказания…",
            height=315
        )
        root.addWidget(info_panel)

        root.addStretch()


        bottom = QHBoxLayout()

        bottom_label = QLabel("Добавить это лекарство?")
        bottom_font = QFont(self.font_text, 12)
        bottom_font.setWeight(QFont.Weight.DemiBold)
        bottom_label.setFont(bottom_font)
        bottom_label.setStyleSheet("color: rgba(240,240,240,210);")

        bottom.addWidget(bottom_label)
        bottom.addStretch()

        ok = QPushButton("Принять")
        ok.setFixedSize(120, 46)
        ok.setStyleSheet("background-color: rgba(131,123,228,255);")
        ok.clicked.connect(self.on_accept_clicked)

        cancel = QPushButton("Отказаться")
        cancel.setFixedSize(143, 46)
        cancel.setStyleSheet("background-color: rgba(120,120,120,210);")
        cancel.clicked.connect(self.reject)

        bottom.addWidget(ok)
        bottom.addWidget(cancel)
        root.addLayout(bottom)


    def _panel_style(self):
        return """
            QWidget {
                background-color: rgba(120,120,120,190);
                border-radius: 14px;
            }
        """

    def _make_line_panel(self, placeholder: str, height: int):
        panel = QWidget()
        panel.setStyleSheet(self._panel_style())
        panel.setFixedHeight(height)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(height)
        edit.setStyleSheet("""
            QLineEdit {
                padding-left: 18px;
                padding-right: 18px;
                padding-top: 8px;
                padding-bottom: 8px;
            }
        """)

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
                     
        edit.setReadOnly(False)
        edit.setFocusPolicy(Qt.StrongFocus)
        edit.setCursor(Qt.IBeamCursor)
        edit.setFrameStyle(QTextEdit.NoFrame)
        edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        edit.setStyleSheet("""
            QTextEdit {
                padding-left: 18px;
                padding-right: 18px;
                padding-top: 10px;
                padding-bottom: 10px;
            }
            QTextEdit::viewport {
                background: transparent;
            }
        """)

        layout.addWidget(edit)
        return panel, edit

                            
    def get_name_dose(self) -> str:
        return self.name_dose.text().strip()

    def get_info(self) -> str:
        return self.info.toPlainText().strip()

    def get_llm_json(self):
        return self.llm_json

    def on_accept_clicked(self):
        self.accept()

    def accept(self):
        # 1) читаем ввод
        name_dose = self.get_name_dose()
        info = self.get_info()

        if not name_dose:
            return

        conn = getattr(self.parent(), "conn", None)

        def _get_setting(key: str, default=""):
            if conn is None:
                return default
            conn.execute(
                "CREATE TABLE IF NOT EXISTS app_settings(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
            )
            cur = conn.execute("SELECT value FROM app_settings WHERE key=?", (key,))
            row = cur.fetchone()
            return row[0] if row else default

        db_settings = {
            "openrouter_api_key": (_get_setting("openrouter_api_key", "") or "").strip(),
            "openrouter_model": (_get_setting("llm_model", "") or "").strip(),
            "language": (_get_setting("language", "ru") or "ru").strip(),
            "max_tokens": int(_get_setting("max_tokens", 1200) or 1200),
        }

        # ВАЖНО: resolve_llm_settings сам сначала читает llm_config.json
        resolved = resolve_llm_settings(db_settings)

        resolved = resolve_llm_settings(db_settings)

        if not resolved["api_key"]:
            # покажи пользователю, что нужен llm_config.json или резерв в настройках
            self.info.setPlainText(
                "не найден api key. положи llm_config.json в корень проекта или укажи ключ в настройках (резерв)."
            )
            return

        # 3) собираем промпт: ОБЯЗАТЕЛЬНО включаем info
        user_payload = (
            f"лекарство и дозировка: {name_dose}\n"
            f"информация от пользователя (учитывать буквально): {info}\n\n"
            "требования:\n"
            "1) если пользователь указал курс/сроки (например '5 дней') — сделай ровно так.\n"
            "2) верни только валидный json по схеме.\n"
        )

        # 4) вызываем LLM и сохраняем результат в диалоге
        from backend.llm_service import ask_openrouter_json

        data = ask_openrouter_json(
            api_key=resolved["api_key"],
            model=resolved["model"],
            language=resolved["language"],
            user_text=user_payload,
            max_tokens=resolved["max_tokens"],
        )

        self.llm_json = data  # чтобы main_window мог взять dlg.get_llm_json()
        super().accept()
