from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional

from PySide6.QtCore import Qt

try:
    from shiboken6 import isValid                
except Exception:                    
    def isValid(obj):
        return obj is not None

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)


@dataclass
class ReminderItemData:
    title: str
    start_local: str                             
    notes: Optional[str] = None

    def time_hhmm(self) -> str:
        try:
            dt = datetime.strptime(self.start_local, "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%H:%M")
        except Exception:
            return ""


class RemindersPanel(QFrame):
    """Плашка "Напоминания" на HomeScreen.

    Сюда кладём события на выбранную дату (по факту — из calendar_events).
    """

    def __init__(self, parent: QWidget, *, font_title: str, font_text: str):
        super().__init__(parent)
        self.font_title = font_title
        self.font_text = font_text

        self.setFixedSize(685, 485)
        self.setStyleSheet(
            """
            QFrame {
                background-color: rgba(255, 255, 255, 40);
                border-radius: 18px;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        self.title_lbl = QLabel("Напоминания")
        f = QFont(self.font_title, 18)
        f.setWeight(QFont.Weight.DemiBold)
        self.title_lbl.setFont(f)
                                                                                                 
        self.title_lbl.setStyleSheet(
            "color: rgba(255,255,255,235); background: transparent; border: none; padding: 0px;"
        )

        self.date_lbl = QLabel("")
        self.date_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.date_lbl.setFont(QFont(self.font_text, 13))
                                                                                   
        self.date_lbl.setStyleSheet(
            "color: rgba(255,255,255,160); background: transparent; border: none; padding: 0px;"
        )

        header.addWidget(self.title_lbl)
        header.addStretch(1)
        header.addWidget(self.date_lbl)
        root.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet(
            """
            QScrollArea { background: transparent; }
            QScrollBar:vertical { width: 10px; background: transparent; }
            QScrollBar::handle:vertical { background: rgba(255,255,255,40); border-radius: 5px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            """
        )

        self.body = QWidget()
        self.body.setStyleSheet("background: transparent;")
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(10)

        self.empty_lbl = QLabel("Пока нет напоминаний")
        self.empty_lbl.setFont(QFont(self.font_text, 14))
        self.empty_lbl.setStyleSheet("color: rgba(255,255,255,150);")
        self.empty_lbl.setAlignment(Qt.AlignCenter)
        self.body_layout.addWidget(self.empty_lbl)
        self.body_layout.addStretch(1)

        self.scroll.setWidget(self.body)
        root.addWidget(self.scroll)

    def set_header_date(self, text: str) -> None:
        self.date_lbl.setText(text)

    def _ensure_empty_label(self) -> None:
                                                                                  
                                    
        if getattr(self, "empty_lbl", None) is None or not isValid(self.empty_lbl):
            self.empty_lbl = QLabel("Пока нет напоминаний")
            self.empty_lbl.setFont(QFont(self.font_text, 14))
            self.empty_lbl.setStyleSheet("color: rgba(255,255,255,150);")
            self.empty_lbl.setAlignment(Qt.AlignCenter)

    def set_items(self, items: Iterable[ReminderItemData]) -> None:
        self._ensure_empty_label()

                                                                    
        while self.body_layout.count():
            it = self.body_layout.takeAt(0)
            w = it.widget()
            if w is None:
                continue
            if w is self.empty_lbl:
                                                       
                w.hide()
                w.setParent(self.body)
                continue
            w.setParent(None)
            w.deleteLater()

        items = list(items)
        if not items:
            self.body_layout.addWidget(self.empty_lbl)
            self.empty_lbl.show()
            self.body_layout.addStretch(1)
            return

        self.empty_lbl.hide()

        for item in items:
            row = self._make_row(item)
            self.body_layout.addWidget(row)

        self.body_layout.addStretch(1)

    def _make_row(self, item: ReminderItemData) -> QWidget:
        row = QFrame()
        row.setStyleSheet(
            """
            QFrame {
                background-color: rgba(120,120,120,120);
                border-radius: 14px;
            }
            """
        )
        row.setFixedHeight(74)

        lay = QHBoxLayout(row)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(12)

                                                                       
        time_badge = QFrame()
        time_badge.setFixedSize(74, 46)
        time_badge.setStyleSheet(
            "QFrame { background-color: rgba(90,90,90,120); border-radius: 12px; }"
        )
        time_badge_lay = QHBoxLayout(time_badge)
        time_badge_lay.setContentsMargins(0, 0, 0, 0)
        time_badge_lay.setSpacing(0)

        time_lbl = QLabel(item.time_hhmm())
        time_lbl.setAlignment(Qt.AlignCenter)
        tf = QFont(self.font_title, 14)
        tf.setWeight(QFont.Weight.DemiBold)
        time_lbl.setFont(tf)
        time_lbl.setStyleSheet(
            "color: rgba(255,255,255,220); background: transparent; border: none; padding: 0px;"
        )
        time_badge_lay.addWidget(time_lbl)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(2)

        title_lbl = QLabel(item.title)
        title_lbl.setFont(QFont(self.font_text, 14))
                                                                      
        title_lbl.setStyleSheet(
            "color: rgba(255,255,255,225); background: transparent; border: none; padding: 0px;"
        )

        title_col.addWidget(title_lbl)

        if item.notes:
            note_lbl = QLabel(item.notes)
            note_lbl.setFont(QFont(self.font_text, 11))
            note_lbl.setStyleSheet(
                "color: rgba(255,255,255,155); background: transparent; border: none; padding: 0px;"
            )
            note_lbl.setWordWrap(True)
            title_col.addWidget(note_lbl)

        lay.addWidget(time_badge)
        lay.addLayout(title_col, 1)

        return row
