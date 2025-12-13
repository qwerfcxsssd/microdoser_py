import calendar

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QLabel, QPushButton, QFrame,
    QGridLayout, QVBoxLayout,
    QSizePolicy, QWidget
)


class Calendar(QWidget):
    btn_size = 56

    style_day = """
        QPushButton {
            background-color: rgba(255, 255, 255, 0);
            border-radius: 27px;
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
            border-radius: 27px;
        }
        QPushButton:hover {
            background-color: rgba(104, 80, 156, 190);
        }
        QPushButton:pressed {
            background-color: #3e9144;
        }
    """

    def __init__(self, parent=None, font_text="Arial", font_semibold="Arial"):
        super().__init__(parent)

        self.font_text = font_text          # для цифр дней
        self.font_semibold = font_semibold  # для пн вт 

        self.current_date = QDate.currentDate()
        self.init_ui()

    def init_ui(self):
        # сам виджет ровно под плашку
        self.setFixedSize(590, 485)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # плашка календаря
        self.calendar_panel = QFrame(self)
        self.calendar_panel.setObjectName("calendar_panel")
        self.calendar_panel.setFixedSize(590, 485)
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

        # дни недели
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

        # сетка дней месяца
        self.days_area = QFrame()
        self.days_area.setStyleSheet("background: transparent;")
        self.days_area.setFixedHeight(6 * self.btn_size + 5 * 11)  # 6 рядов, 5 промежутков

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
        year = self.current_date.year()
        return f"{month_names[month_idx]} {year}"

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

                day_btn = QPushButton(str(day))
                day_btn.setFixedSize(self.btn_size, self.btn_size)
                day_btn.setCursor(Qt.PointingHandCursor)

                # шрифт цифр
                f = QFont(self.font_text, 16)
                f.setWeight(QFont.Weight.Medium)
                day_btn.setFont(f)

                is_today = (
                    day == today.day()
                    and self.current_date.month() == today.month()
                    and self.current_date.year() == today.year()
                )
                day_btn.setStyleSheet(self.style_today if is_today else self.style_day)

                day_btn.clicked.connect(lambda checked=False, d=day: self.day_clicked(d))
                self.days_grid.addWidget(day_btn, row, col, alignment=Qt.AlignCenter)

    def prev_month(self):
        self.current_date = self.current_date.addMonths(-1)
        self.update_calendar()

    def next_month(self):
        self.current_date = self.current_date.addMonths(1)
        self.update_calendar()

    def day_clicked(self, day):
        print(f"Выбран день: {day}.{self.current_date.month()}.{self.current_date.year()}")
