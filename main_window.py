from PySide6.QtWidgets import QWidget, QLineEdit
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPixmap
from PySide6.QtCore import Qt

from buttons.sidebar import create_sidebar_buttons
from buttons.bottom_bar import create_bottom_buttons
from buttons.calendar_nav import create_calendar_nav_buttons
from buttons.search_button import create_search_button


class MainWindow(QWidget):
    def __init__(self, font_circled: str, font_semibold: str):
        super().__init__()

        #шрифты
        self.font_circled = font_circled
        self.font_semibold = font_semibold

        self.setWindowTitle("Micro Doser")
        self.resize(1920, 1080)

        # Нижние кнопки  semibold
        self.btn_add_medicine, self.btn_pick_medicine = create_bottom_buttons(
            self,
            self.font_semibold,
        )
        # Сайдбар circled
        (
            self.btn_home,
            self.btn_diary,
            self.btn_settings,
        ) = create_sidebar_buttons(
            self,
            self.font_circled,
            on_home=self.show_home,
            on_diary=self.show_diary,
            on_settings=self.show_settings,
        )

        # Календарная навигация
        (
            self.prev_month_btn,
            self.next_month_btn,
        ) = create_calendar_nav_buttons(
            self,
            on_prev=self.on_prev_month,
            on_next=self.on_next_month,
        )

        #поиск
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Поиск")
        self.search_input.resize(1200, 60)
        self.search_input.setStyleSheet(
            f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: white;
                padding-left: 20px;
                font-size: 24px;
                font-family: '{self.font_circled}';
            }}
        """
        )
        self.search_input.move(530, 99)

        self.search_button = create_search_button(self, self.on_search_clicked)

    #рисовка

    def paintEvent(self, event):
        painter = QPainter(self)

        # Фон
        painter.fillRect(self.rect(), QColor("#2C2C2C"))

        #блоки напоминания и календаря
        painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
        painter.setPen(QPen(QColor(44, 44, 44, 60), 1))

        painter.drawRoundedRect(516, 329.86, 684.89, 484.8, 16, 16)
        painter.drawRoundedRect(1247.66, 330.95, 592.34, 483.71, 16, 16)
        painter.drawRoundedRect(516, 82, 1324, 95, 16, 16)

        painter.drawRect(0, 0, 435, self.height())

        painter.setPen(QColor(255, 255, 255))

        def text_with_icon(
            x,
            y,
            text,
            icon_path,
            scale,
            icon_offset_y=2,
            text_offset_y=0,
        ):
            padding = 15
            icon = QPixmap(icon_path).scaled(
                scale,
                scale,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            painter.drawPixmap(x, y - scale + icon_offset_y, icon)
            painter.drawText(x + scale + padding, y + text_offset_y, text)

        font_title = QFont(self.font_semibold, 26)
        font_title.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font_title)

        text_with_icon(
            67,
            100,
            "Micro Doser",
            "icons/pils.png",
            40,
            icon_offset_y=6,
        )

        # Напоминания / Календарь
        font_section = QFont(self.font_circled, 25)
        painter.setFont(font_section)

        text_with_icon(
            516,
            295,
            "Напоминания",
            "icons/notification.png",
            30,
        )

        text_with_icon(
            1253,
            295,
            "Календарь",
            "icons/calendar.png",
            30,
        )


    def on_search_clicked(self):
        print("Ищем по:", self.search_input.text())

    def on_prev_month(self):
        print("Назад по календарю")

    def on_next_month(self):
        print("Вперёд по календарю")

    def show_home(self):
        print("Открыта главная страница")

    def show_diary(self):
        print("Открыт ежедневник")

    def show_settings(self):
        print("Открыты настройки")
