import sqlite3
from PySide6.QtWidgets import (
    QWidget, QPushButton, QFrame, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
)
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from PySide6.QtCore import Qt, Signal


class ToggleSwitch(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(90, 34)
        self.setStyleSheet("QPushButton{background: transparent; border: none;}")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        bg = QColor(150, 150, 150, 200) if self.isChecked() else QColor(110, 110, 110, 180)

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(bg))
        p.drawRoundedRect(self.rect(), 17, 17)

        knob = 26
        pad = 4
        x = self.width() - pad - knob if self.isChecked() else pad
        y = (self.height() - knob) // 2

        p.setBrush(QBrush(QColor(210, 210, 210, 230)))
        p.drawEllipse(x, y, knob, knob)


class SettingsRow(QWidget):
    clicked = Signal()

    def __init__(self, parent, text: str, font_family: str, with_switch=False):
        super().__init__(parent)
        self.text = text
        self.font_family = font_family
        self.with_switch = with_switch

        self.setFixedSize(1200, 86)

        self.btn = QPushButton("", self)
        self.btn.setGeometry(0, 0, self.width(), self.height())
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setStyleSheet("""
            QPushButton{
                background: transparent;
                border: none;
            }
            QPushButton:hover{
                background-color: rgba(255,255,255,10);
                border-radius: 16px;
            }
            QPushButton:pressed{
                background-color: rgba(255,255,255,6);
                border-radius: 16px;
            }
        """)
        self.btn.clicked.connect(self.clicked.emit)

        self.toggle = None
        if with_switch:
            self.toggle = ToggleSwitch(self)
            self.toggle.move(
                self.width() - 30 - self.toggle.width(),
                (self.height() - self.toggle.height()) // 2
            )
            self.toggle.raise_()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.setBrush(QBrush(QColor(85, 85, 85, 210)))
        p.setPen(QPen(QColor(255, 255, 255, 20), 1))
        p.drawRoundedRect(self.rect(), 16, 16)

        p.setPen(QColor(235, 235, 235))
        font = QFont(self.font_family, 22)
        font.setWeight(QFont.Weight.Medium)
        p.setFont(font)
        p.drawText(28, 56, self.text)


class LanguagePopup(QFrame):
    language_selected = Signal(str)                

    def __init__(self, parent, font_family: str):
        super().__init__(parent)

        self.font_family = font_family
        self.setObjectName("LanguagePopup")
        self.setFixedSize(420, 190)

        self.setStyleSheet(f"""
            QFrame#LanguagePopup {{
                background-color: rgba(70,70,70,245);
                border: 1px solid rgba(255,255,255,25);
                border-radius: 18px;
            }}
            QPushButton {{
                border: none;
                border-radius: 14px;
                font-size: 20px;
                color: white;
                font-family: '{self.font_family}';
                padding: 12px 16px;
                background-color: rgba(110,110,110,200);
            }}
            QPushButton:hover {{
                background-color: rgba(255,255,255,35);
            }}
            QPushButton:pressed {{
                background-color: rgba(255,255,255,18);
            }}
        """)

        self.btn_ru = QPushButton("Русский", self)
        self.btn_en = QPushButton("English", self)

        self.btn_ru.setGeometry(26, 26, 368, 64)
        self.btn_en.setGeometry(26, 100, 368, 64)

        self.btn_ru.clicked.connect(lambda: self.language_selected.emit("ru"))
        self.btn_en.clicked.connect(lambda: self.language_selected.emit("en"))


class SettingsScreen(QWidget):
    def __init__(self, font_title: str, font_buttons: str, conn: sqlite3.Connection | None = None):
        super().__init__()
        self.font_title = font_title
        self.font_buttons = font_buttons
        self.conn = conn

        self.margin_left = 60
        self.title_y = 62

        self.row_x = 60
        self.row_y0 = 110
        self.row_gap = 28

        self.row_lang = SettingsRow(self, "Сменить язык", self.font_buttons)
        self.row_kids = SettingsRow(self, "Детский режим", self.font_buttons, with_switch=True)
        self.row_llm  = SettingsRow(self, "LLM / API", self.font_buttons)

        rows = [self.row_lang, self.row_kids, self.row_llm]

        y = self.row_y0
        for r in rows:
            r.move(self.row_x, y)
            y += r.height() + self.row_gap

              
        self.lang_popup = LanguagePopup(self, self.font_buttons)
        self.lang_popup.hide()
        self.lang_popup.language_selected.connect(self.on_language_selected)
        self.row_lang.clicked.connect(self.show_language_popup)

             
        self.row_llm.clicked.connect(self.open_llm_settings)

                                  
    def _ensure_app_settings_table(self):
        if not self.conn:
            return
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS app_settings(
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def _get_setting(self, key: str, default: str = "") -> str:
        if not self.conn:
            return default
        self._ensure_app_settings_table()
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cur.fetchone()
        return row[0] if row and row[0] is not None else default

    def _set_setting(self, key: str, value: str) -> None:
        if not self.conn:
            return
        self._ensure_app_settings_table()
        self.conn.execute(
            """
            INSERT INTO app_settings(key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
        self.conn.commit()

                            
    def show_language_popup(self):
        anchor = self.row_lang.geometry()
        x = anchor.x() + anchor.width() - self.lang_popup.width()
        y = anchor.y() + anchor.height() + 14

        x = max(20, min(x, self.width() - self.lang_popup.width() - 20))
        y = max(20, min(y, self.height() - self.lang_popup.height() - 20))

        self.lang_popup.move(x, y)
        self.lang_popup.show()
        self.lang_popup.raise_()

    def hide_language_popup(self):
        self.lang_popup.hide()

    def on_language_selected(self, code: str):
        self._set_setting("language", code)
        self.hide_language_popup()

    def mousePressEvent(self, event):
        if self.lang_popup.isVisible():
            if not self.lang_popup.geometry().contains(event.position().toPoint()):
                self.hide_language_popup()
        super().mousePressEvent(event)

                              
    def open_llm_settings(self):
        if not self.conn:
            return

        api_key = self._get_setting("openrouter_api_key", "")
        model = self._get_setting("llm_model", "deepseek/deepseek-chat:free")

        dlg = QDialog(self)
        dlg.setWindowTitle("LLM / API")
        dlg.setModal(True)

        root = QVBoxLayout(dlg)

        root.addWidget(QLabel("OpenRouter API key:"))
        api_in = QLineEdit()
        api_in.setEchoMode(QLineEdit.EchoMode.Password)
        api_in.setPlaceholderText("sk-...")
        api_in.setText(api_key)
        root.addWidget(api_in)

        root.addWidget(QLabel("Модель (OpenRouter id):"))
        model_in = QLineEdit()
        model_in.setPlaceholderText("deepseek/deepseek-chat:free")
        model_in.setText(model)
        root.addWidget(model_in)

        btns = QHBoxLayout()
        btn_cancel = QPushButton("Отмена")
        btn_save = QPushButton("Сохранить")
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)
        root.addLayout(btns)

        def _save():
            self._set_setting("openrouter_api_key", api_in.text().strip())
            self._set_setting("llm_model", model_in.text().strip() or "deepseek/deepseek-chat:free")
            dlg.accept()

        btn_save.clicked.connect(_save)
        btn_cancel.clicked.connect(dlg.reject)

        dlg.exec()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.fillRect(self.rect(), QColor(0, 0, 0, 0))

        p.setPen(QColor(235, 235, 235))
        title_font = QFont(self.font_title, 34)
        title_font.setWeight(QFont.Weight.DemiBold)
        p.setFont(title_font)
        p.drawText(self.margin_left, self.title_y, "Настройки")
