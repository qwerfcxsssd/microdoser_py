from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPixmap
from PySide6.QtCore import Qt

class HomeScreen(QWidget):
    def __init__(self, font_circled: str, font_semibold: str):
        super().__init__()
        self.font_circled = font_circled
        self.font_semibold = font_semibold

    def paintEvent(self, event):
        painter = QPainter(self)

                             
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
        painter.setPen(QPen(QColor(44, 44, 44, 60), 1))

        painter.drawRoundedRect(0, 108, 514, 403, 16, 16)
             

        painter.setPen(QColor(255, 255, 255))

        def text_with_icon(x, y, text, icon_path, scale, icon_offset_y=2, text_offset_y=0):
            padding = 15
            icon = QPixmap(icon_path).scaled(
                scale, scale, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            painter.drawPixmap(x, y - scale + icon_offset_y, icon)
            painter.drawText(x + scale + padding, y + text_offset_y, text)

        font_section = QFont(self.font_circled, 21)
        painter.setFont(font_section)

        text_with_icon(0, 79, "Напоминания", "icons/notification.png", 25)
        text_with_icon(553, 79, "Календарь", "icons/calendar.png", 25)
