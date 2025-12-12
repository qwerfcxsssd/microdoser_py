from PySide6.QtWidgets import (QWidget, QGridLayout, QPushButton, QLabel,
                             QHBoxLayout, QVBoxLayout, QSizePolicy)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
import calendar


class Calendar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = QDate.currentDate()
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(400, 300)

        # Главный layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(0, 120, 0, 0)

        header_layout = QHBoxLayout()

        # Создаем QLabel с фиксированным размером
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignCenter)
        self.month_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.month_label.setFixedWidth(200)  # Фиксированная ширина
        self.month_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


        style = """
                QPushButton {
                    background: transparent;
                    border: none;
                    border-radius: 20px;
                }
                QPushButton:hover {
                    background-color: rgba(255,255,255,40);
                }
                QPushButton:pressed {
                    background-color: rgba(255,255,255,16);
                }
            """


        header_layout.addWidget(self.month_label)

        main_layout.addLayout(header_layout)

        # Дни недели
        days_layout = QGridLayout()
        days_layout.setSpacing(5)

        # Русские названия дней недели
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(weekdays):
            label = QLabel(day)
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 12, QFont.Bold))
            if i >= 5:  # Суббота и воскресенье
                label.setStyleSheet("color: red;")
            days_layout.addWidget(label, 0, i)

        main_layout.addLayout(days_layout)

        # Сетка с днями месяца
        self.days_grid = QGridLayout()
        self.days_grid.setSpacing(5)
        main_layout.addLayout(self.days_grid)

        # Обновляем отображение
        self.update_calendar()

    def update_calendar(self):
        # Очищаем старые кнопки
        for i in reversed(range(self.days_grid.count())):
            widget = self.days_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Обновляем заголовок
        month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                       "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        month = self.current_date.month() - 1
        year = self.current_date.year()
        self.month_label.setText(f"{month_names[month]} {year}")

        # Получаем календарь на месяц
        cal = calendar.monthcalendar(year, self.current_date.month())

        # Заполняем дни
        row = 0
        for week in cal:
            for col, day in enumerate(week):
                if day != 0:
                    day_btn = QPushButton(str(day))
                    day_btn.setFixedSize(40, 40)
                    day_btn.setCursor(Qt.PointingHandCursor)

                    # Помечаем текущий день
                    if (day == QDate.currentDate().day() and
                            self.current_date.month() == QDate.currentDate().month() and
                            self.current_date.year() == QDate.currentDate().year()):
                        day_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #4CAF50;
                                color: white;
                                border-radius: 5px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: #45a049;
                            }
                        """)
                    # Помечаем выходные
                    elif col >= 5:
                        day_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #f8f9fa;
                                color: red;
                                border: 1px solid #dee2e6;
                                border-radius: 5px;
                            }
                            QPushButton:hover {
                                background-color: #e9ecef;
                            }
                        """)
                    else:
                        day_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #f8f9fa;
                                border: 1px solid #dee2e6;
                                border-radius: 5px;
                            }
                            QPushButton:hover {
                                background-color: #e9ecef;
                            }
                        """)

                    # Подключаем клик
                    day_btn.clicked.connect(lambda checked, d=day: self.day_clicked(d))

                    self.days_grid.addWidget(day_btn, row, col)
            row += 1

    def prev_month(self):
        self.current_date = self.current_date.addMonths(-1)
        self.update_calendar()

    def next_month(self):
        self.current_date = self.current_date.addMonths(1)
        self.update_calendar()

    def day_clicked(self, day):
        print(f"Выбран день: {day}.{self.current_date.month()}.{self.current_date.year()}")
        # Здесь можно добавить логику при клике на день