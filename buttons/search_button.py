from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize


def create_search_button(parent, on_clicked):


    btn = QPushButton(parent)
    btn.setIcon(QIcon("icons/search.png"))
    btn.setIconSize(QSize(21, 21))
    btn.resize(36, 36)
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

                                                                                     
                                                                                     
    btn.move(1313, 87)

    btn.clicked.connect(on_clicked)
    return btn
