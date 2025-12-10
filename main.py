import sys
import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QStackedWidget
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QIcon, QFontDatabase, QPixmap
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QGraphicsBlurEffect




class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Моё окно")
        self.resize(1920, 1080)

        self.background_color = QColor(44, 44, 44) #30 35 45 цвет Макса
        self.bg_image = QPixmap("icons/bg_full.png")
        self.buttons = []



        # создаём несколько тестовых кнопок
        self.create_button("Добавить лекарство", 0.786, 0.876,"rgba(129, 119, 245, 255)" )  # центр
        self.create_button("Подобрать лекарство", 0.444, 0.876,"rgba(83,83,87,255)")

        self.create_side_button("  Главное", 0.12, 0.22, "icons/mainMenu.png")
        self.create_side_button("  Ежедневник", 0.12, 0.34, "icons/diary.png")
        self.create_side_button("   Настройки", 0.12, 0.46, "icons/settings.png")


    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.bg_image.isNull():
            scaled = self.bg_image.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, scaled)
        else:
            painter.setBrush(QBrush(self.background_color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(0, 0, self.width(), self.height())

        painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
        painter.setPen(QPen(QColor(44, 44, 44, 60), 1))
        # напоминания
        painter.drawRoundedRect(543, 356, 789, 444, 16, 16) #радиус 16
        # календарь
        painter.drawRoundedRect(1366, 356, 452, 444, 16, 16) #радиус 16
        # поиск
        painter.drawRoundedRect(543, 85, 1275, 85,16,16)

        # левое окно
        painter.setBrush(QBrush(QColor(104, 104, 107, 200)))  # сплошной цвет
        painter.setPen(Qt.NoPen)

        painter.drawRect(0, 0, 460, 1212)  # x, y, width, heigh

        # теееекст
        font = QFont(FONT_FAMILY, 24)  # шрифт Arial, размер 16
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))


        def textWithIcon(x,y,text,path_of_icon, scale):
            padding = 50
            icon = QPixmap(path_of_icon).scaled(scale, scale, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(x, y - scale, icon)
            painter.drawText(x + scale + padding, y, text)

        textWithIcon(75,100, "Micro Doser", "icons/pils.png", 70)
        textWithIcon(594,315,"Напоминания","icons/notification.png", 30)
        textWithIcon(1419, 315,"Календарь","icons/calendar.png",30)
        #этот рисователь очень сильно сжимает картинки, лучше чере QLabel. это на будущее


    def draw_button_backgrounds(self, painter):
        """
        Рисует полупрозрачную "стеклянную" подложку под нижними кнопками.
        """
        painter.setPen(Qt.NoPen)

        for btn, _, _ in self.buttons:
            if btn.text() in ("Добавить лекарство", "Подобрать лекарство"):
                # прямоугольник чуть больше кнопки
                rect = btn.geometry().adjusted(-10, -10, 10, 10)

                # "матовое стекло" под кнопкой
                painter.setBrush(QColor(255, 255, 255, 60))  # прозрачность можно крутить
                painter.drawRoundedRect(rect, 18, 18)




    def create_button(self, text, rel_x, rel_y, color):
        btn = QPushButton(text, self)
        btn.resize(621, 95)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 16px;
                border: 0px solid rgba(58,58,58,255);
                color: white;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: rgba(255,255,255,45);
            }}
            QPushButton:pressed {{
                background-color: rgba(255,255,255,25);
            }}
        """)
        # сохраняем кнопку и её относительные координаты
        self.buttons.append((btn, rel_x, rel_y))

        # сразу выставляем начальную позицию
        self.update_button_position(btn, rel_x, rel_y)

        return btn

    def create_side_button(self, text, rel_x, rel_y, icon_path): #данек можно в одну функцию захуячить
        btn = QPushButton(text, self)

        btn.setIcon((QIcon(icon_path)))
        btn.setIconSize(QSize(16, 16))
        btn.resize(300, 90)

        btn.setFont(QFont(FONT_FAMILY,16))

        btn.setStyleSheet("""
                    QPushButton {
                        padding: 10px;
                        text-align: left;
                        border: none;
                        color: white;
                        background-color: transparent;
                        border-radius: 8px;
                        font-size: 16px;
                    }

                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 40); /* светлый градиент */
                    }

                    QPushButton:pressed {
                        background-color: rgba(255, 255, 255, 16);
                    }
                """)

        self.buttons.append((btn, rel_x, rel_y))
        self.update_button_position(btn, rel_x, rel_y)

        return btn



    def update_button_position(self, btn, rel_x, rel_y):
        x = int(self.width() * rel_x - btn.width() / 2)
        y = int(self.height() * rel_y - btn.height() / 2)
        btn.move(x, y)

    def resizeEvent(self, event):
        for btn, rel_x, rel_y in self.buttons:
            self.update_button_position(btn, rel_x, rel_y)

        super().resizeEvent(event)



app = QApplication(sys.argv)

# Регистрируем шрифт
font_id = QFontDatabase.addApplicationFont("fonts/circled.ttf")
FONT_FAMILY = QFontDatabase.applicationFontFamilies(font_id)[0]

window = MainWindow()
window.show()
app.exec()