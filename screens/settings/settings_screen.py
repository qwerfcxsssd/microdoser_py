from PySide6.QtWidgets import QWidget, QPushButton
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from PySide6.QtCore import Qt

class SettingsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Создаём вертикальный layout для этого виджета
        layout = QVBoxLayout(self)

        # Устанавливаем отступы
        self.setContentsMargins(0, 60, 0, 0)

        # Настроим заголовок и кнопки
        self.title_label = QLabel("Настройки", self)
        layout.addWidget(self.title_label)
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

        # стеклянный фон
        p.setBrush(QBrush(QColor(85, 85, 85, 210)))
        p.setPen(QPen(QColor(255, 255, 255, 20), 1))
        p.drawRoundedRect(self.rect(), 16, 16)

        # ТЕКСТ — Montserrat Alternates
        p.setPen(QColor(235, 235, 235))
        font = QFont(self.font_family, 22)
        font.setWeight(QFont.Weight.Medium)
        p.setFont(font)
        p.drawText(28, 56, self.text)



class SettingsScreen(QWidget):
    def __init__(self, font_title, font_buttons):
        super().__init__()
        self.font_title = font_title      # Montserrat Alternates
        self.font_buttons = font_buttons  # Montserrat Alternates

        self.margin_left = 60
        self.title_y = 40

        self.row_x = 60
        self.row_y0 = 80
        self.row_gap = 28

        self.row_lang = SettingsRow(self, "Сменить язык", self.font_buttons)
        self.row_kids = SettingsRow(self, "Детский режим", self.font_buttons, with_switch=True)

        rows = [
            self.row_lang,
            self.row_kids
        ]

        y = self.row_y0
        for r in rows:
            r.move(self.row_x, y)
            y += r.height() + self.row_gap


    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.fillRect(self.rect(), QColor(0, 0, 0, 0))

        p.setPen(QColor(235, 235, 235))
        title_font = QFont(self.font_title, 34)
        title_font.setWeight(QFont.Weight.DemiBold)
        p.setFont(title_font)
        p.drawText(self.margin_left, self.title_y, "Настройки")



