from PySide6.QtWidgets import QWidget, QLineEdit, QStackedWidget, QLabel
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPixmap
from PySide6.QtCore import Qt

from buttons.calendar import Calendar

# Кнопки / элементы интерфейса
from buttons.sidebar import create_sidebar_buttons
from buttons.bottom_bar import create_bottom_buttons
from buttons.calendar_nav import create_calendar_nav_buttons
from buttons.search_button import create_search_button

# Экраны
from screens.home.home_screen import HomeScreen
from screens.diary.diary_screen import DiaryScreen
from screens.settings.settings_screen import SettingsScreen

# Диалоги
from dialogs.pick_medicine_dialog import PickMedicineDialog
from dialogs.add_medicine_dialog import AddMedicineDialog


class MainWindow(QWidget):
    def __init__(self, font_circled: str, font_semibold: str):
        super().__init__()

        self.font_circled = font_circled
        self.font_semibold = font_semibold

        self.setWindowTitle("Micro Doser")
        self.resize(1920, 1080)

        self.stacked = QStackedWidget(self)
        self.stacked.setGeometry(516, 200, 1320, 780)

        self.page_home = HomeScreen(self.font_circled, self.font_semibold)
        self.page_settings = SettingsScreen(self.font_semibold, self.font_circled)
        self.page_diary = DiaryScreen(self.font_semibold, self.font_circled)

        self.stacked.addWidget(self.page_home)      # index 0
        self.stacked.addWidget(self.page_diary)     # index 1
        self.stacked.addWidget(self.page_settings)  # index 2

        # Календарь (плашка)
        self.calendar = Calendar(
            self.page_home,
            font_text=self.font_circled,
            font_semibold=self.font_semibold
        )

        self.calendar.move(730, 130)# внутри HomeScreen
        self.calendar.setVisible(False)

        # Плашка месяца рядом с календарм
        self.month_out = QLabel(self.page_home)
        self.month_out.setText(self.calendar.month_text())
        self.month_out.setStyleSheet("""
            QLabel {
                background-color: rgba(255,255,255,160);
                color: rgba(25,25,25,230);
                border-radius: 18px;
                padding-left: 18px;
                padding-right: 18px;
            }
        """)
        f = QFont(self.font_circled, 14)
        f.setWeight(QFont.Weight.DemiBold)
        self.month_out.setFont(f)
        self.month_out.setFixedHeight(42)
        self.month_out.adjustSize()
        self.month_out.move(1015, 64)
        self.month_out.setVisible(False)

        # Нижние кнопки
        self.btn_add_medicine, self.btn_pick_medicine = create_bottom_buttons(
            self, self.font_semibold
        )
        self.btn_pick_medicine.clicked.connect(self.open_pick_medicine_dialog)
        self.btn_add_medicine.clicked.connect(self.open_add_medicine_dialog)

        # Стрелки календаря
        self.prev_month_btn, self.next_month_btn = create_calendar_nav_buttons(
            self, on_prev=self.on_prev_month_clicked, on_next=self.on_next_month_clicked
        )

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

        self.btn_home, self.btn_diary, self.btn_settings = create_sidebar_buttons(
            self,
            self.font_circled,
            on_home=self.show_home,
            on_diary=self.show_diary,
            on_settings=self.show_settings,
        )

        self.show_home()

    def _refresh_month_out(self):
        self.month_out.setText(self.calendar.month_text())
        self.month_out.adjustSize()

    def on_prev_month_clicked(self):
        self.calendar.prev_month()
        self._refresh_month_out()

    def on_next_month_clicked(self):
        self.calendar.next_month()
        self._refresh_month_out()

    def open_pick_medicine_dialog(self):
        dlg = PickMedicineDialog(
            font_title=self.font_semibold,
            font_text=self.font_circled,
            parent=self
        )
        if dlg.exec() == dlg.Accepted:
            print("Пользователь ввёл:", dlg.get_user_text())
            print("Рекомендации:", dlg.get_recommendations_text())

    def open_add_medicine_dialog(self):
        dlg = AddMedicineDialog(
            font_title=self.font_semibold,
            font_text=self.font_circled,
            parent=self
        )
        if dlg.exec() == dlg.Accepted:
            print("Добавить:", dlg.get_name_dose())
            print("Инфо:", dlg.get_info())

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.fillRect(self.rect(), QColor("#2C2C2C"))

        painter.setBrush(QBrush(QColor(75, 75, 75)))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, 435, self.height())

        painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
        painter.setPen(QPen(QColor(44, 44, 44, 60), 1))
        if self.stacked.currentWidget() == self.page_home:
            painter.drawRoundedRect(516, 82, 1324, 95, 16, 16)

        painter.setPen(QColor(255, 255, 255))

        def text_with_icon(x, y, text, icon_path, scale, icon_offset_y=2, text_offset_y=0):
            padding = 15
            icon = QPixmap(icon_path).scaled(
                scale, scale, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            painter.drawPixmap(x, y - scale + icon_offset_y, icon)
            painter.drawText(x + scale + padding, y + text_offset_y, text)

        font_title = QFont(self.font_semibold, 26)
        font_title.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font_title)

        text_with_icon(67, 100, "Micro Doser", "icons/pils.png", 40, icon_offset_y=6)

    def _set_home_ui_visible(self, visible: bool):
        self.search_input.setVisible(visible)
        self.search_button.setVisible(visible)
        self.prev_month_btn.setVisible(visible)
        self.next_month_btn.setVisible(visible)
        self.btn_add_medicine.setVisible(visible)
        self.btn_pick_medicine.setVisible(visible)

        self.calendar.setVisible(visible)
        self.month_out.setVisible(visible)

        self.update()

    def on_search_clicked(self):
        print("Ищем по:", self.search_input.text())

    def show_home(self):
        self._set_home_ui_visible(True)
        self.stacked.setCurrentWidget(self.page_home)

    def show_diary(self):
        self._set_home_ui_visible(False)
        self.stacked.setCurrentWidget(self.page_diary)

    def show_settings(self):
        self._set_home_ui_visible(False)
        self.stacked.setCurrentWidget(self.page_settings)
