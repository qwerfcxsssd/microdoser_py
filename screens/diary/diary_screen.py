from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt


class DiaryScreen(QWidget):
    def __init__(self, font_circled: str, font_semibold: str):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Ежедневник (тут будет экран)")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
