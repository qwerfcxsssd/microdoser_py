import calendar
from typing import Iterable

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QFont, QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QLabel, QPushButton, QFrame,
    QGridLayout, QVBoxLayout,
    QSizePolicy, QWidget
)
class DayButton(QPushButton):

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)

        self.has_event = False
        self.is_today = False

        self.dot_color = QColor(131, 123, 228, 200)
        self.dot_r = 3         # радиус точки
        self.dot_offset_y = 18   # насколько вниз под цифрой

    def paintEvent(self, event):
        super().paintEvent(event)

        if not (self.has_event or self.is_today):
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        w, h = self.width(), self.height()


        #маленькая точка под цифрой
        if self.has_event and not self.is_today:
            p.setPen(Qt.NoPen)
            p.setBrush(self.dot_color)
            cx = w // 2
            cy = h // 2 + self.dot_offset_y
            r = self.dot_r
            p.drawEllipse(cx - r, cy - r, 2 * r, 2 * r)

        p.end()


class Calendar(QWidget):
    date_selected = Signal(QDate)
    btn_size = 44

    style_day = """
        QPushButton {
            background-color: rgba(255, 255, 255, 0);
            border-radius: 21px;
            color: rgba(240,240,240,210);
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 60);
        }
        QPushButton:pressed {
            background-color: rgba(95, 70, 140, 255);
        }
    """

    style_today = """
        QPushButton {
            background-color: rgba(107, 80, 156, 255);
            color: white;
            border-radius: 21px;
        }
        QPushButton:hover {
            background-color: rgba(104, 80, 156, 190);
        }
        QPushButton:pressed {
            background-color: rgba(104, 80, 156, 190);
        }
    """

    def __init__(self, parent=None, font_text="Arial", font_semibold="Arial"):
        super().__init__(parent)

        self.font_text = font_text
        self.font_semibold = font_semibold

        self.current_date = QDate.currentDate()
        self.selected_date = QDate.currentDate()
        self._marked_days: set[int] = set()
        self.init_ui()

    def set_marked_days(self, days: Iterable[int]) -> None:
        self._marked_days = {int(d) for d in days if int(d) > 0}
        self.update_calendar()

    def init_ui(self):

        self.setFixedSize(443, 403)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.calendar_panel = QFrame(self)
        self.calendar_panel.setObjectName("calendar_panel")
        self.calendar_panel.setFixedSize(443, 403)
        self.calendar_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.calendar_panel.setStyleSheet("""
            QFrame#calendar_panel {
                background-color: rgba(255, 255, 255, 40);
                border-radius: 18px;
            }
        """)
        main_layout.addWidget(self.calendar_panel)

        panel_layout = QVBoxLayout(self.calendar_panel)
        panel_layout.setContentsMargins(18, 16, 18, 18)
        panel_layout.setSpacing(10)

        self.weekdays_grid = QGridLayout()
        self.weekdays_grid.setContentsMargins(0, 0, 0, 0)
        self.weekdays_grid.setHorizontalSpacing(12)
        self.weekdays_grid.setVerticalSpacing(8)

        weekdays = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
        for i, day in enumerate(weekdays):
            label = QLabel(day)
            label.setAlignment(Qt.AlignCenter)

            f = QFont(self.font_semibold, 17)
            f.setWeight(QFont.Weight.DemiBold)
            label.setFont(f)

            label.setStyleSheet("color: rgba(245,245,245,220);")
            self.weekdays_grid.addWidget(label, 0, i)

        panel_layout.addLayout(self.weekdays_grid)

        self.days_area = QFrame()
        self.days_area.setStyleSheet("background: transparent;")
        self.days_area.setFixedHeight(6 * self.btn_size + 5 * 11)

        self.days_grid = QGridLayout(self.days_area)
        self.days_grid.setContentsMargins(0, 0, 0, 0)
        self.days_grid.setHorizontalSpacing(12)
        self.days_grid.setVerticalSpacing(15)

        panel_layout.addWidget(self.days_area)

        self.update_calendar()

    def month_text(self) -> str:
        month_names = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        month_idx = self.current_date.month() - 1
        return month_names[month_idx]  # ← Только "Декабрь"

    def update_calendar(self):
        for i in reversed(range(self.days_grid.count())):
            item = self.days_grid.itemAt(i)
            w = item.widget() if item else None
            if w:
                w.deleteLater()

        cal = calendar.monthcalendar(self.current_date.year(), self.current_date.month())
        today = QDate.currentDate()

        for row, week in enumerate(cal):
            for col, day in enumerate(week):
                if day == 0:
                    ph = QLabel("")
                    ph.setFixedSize(self.btn_size, self.btn_size)
                    self.days_grid.addWidget(ph, row, col, alignment=Qt.AlignCenter)
                    continue

                day_btn = DayButton(str(day))
                day_btn.setFixedSize(self.btn_size, self.btn_size)
                day_btn.setCursor(Qt.PointingHandCursor)

                f = QFont(self.font_text, 16)
                f.setWeight(QFont.Weight.Medium)
                day_btn.setFont(f)

                is_today = (
                        day == today.day()
                        and self.current_date.month() == today.month()
                        and self.current_date.year() == today.year()
                )

                has_event = day in self._marked_days
                is_selected = (
                        day == self.selected_date.day()
                        and self.current_date.month() == self.selected_date.month()
                        and self.current_date.year() == self.selected_date.year()
                )

                if is_today:
                    base = self.style_today
                else:
                    base = self.style_day

                day_btn.setStyleSheet(base)

                day_btn.is_today = is_today
                day_btn.has_event = has_event
                day_btn.clicked.connect(lambda checked=False, d=day: self.day_clicked(d))
                self.days_grid.addWidget(day_btn, row, col, alignment=Qt.AlignCenter)

    def prev_month(self):
        self.current_date = self.current_date.addMonths(-1)

        if self.selected_date.month() != self.current_date.month() or self.selected_date.year() != self.current_date.year():
            self.selected_date = QDate(self.current_date.year(), self.current_date.month(), 1)
        self.update_calendar()

    def next_month(self):
        self.current_date = self.current_date.addMonths(1)
        if self.selected_date.month() != self.current_date.month() or self.selected_date.year() != self.current_date.year():
            self.selected_date = QDate(self.current_date.year(), self.current_date.month(), 1)
        self.update_calendar()

    def day_clicked(self, day):
        self.selected_date = QDate(self.current_date.year(), self.current_date.month(), int(day))
        self.date_selected.emit(self.selected_date)
        self.update_calendar()

