from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize


def create_search_button(parent, on_clicked):


    btn = QPushButton(parent)
    btn.setIcon(QIcon("icons/search.png"))
    btn.setIconSize(QSize(28, 28))
    btn.resize(48, 48)
    btn.setStyleSheet("""
        QPushButton {
            background: transparent;
            border: none;
        }
        QPushButton:hover {
            background-color: rgba(255,255,255,40);
            border-radius: 24px;
        }
        QPushButton:pressed {
            background-color: rgba(255,255,255,16);
            border-radius: 24px;
        }
    """)

    # справа в блоке поиска
    btn.move(1761, 105)

    btn.clicked.connect(on_clicked)
    return btn
