from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize


def create_calendar_nav_buttons(parent, on_prev=None, on_next=None):


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

    # left icon
    btn_prev = QPushButton(parent)
    btn_prev.setIcon(QIcon("icons/left.png"))
    btn_prev.setIconSize(QSize(40, 40))
    btn_prev.resize(40, 40)
    btn_prev.setStyleSheet(style)
    btn_prev.move(1740, 265)
    if on_prev:
        btn_prev.clicked.connect(on_prev)

    #right icon
    btn_next = QPushButton(parent)
    btn_next.setIcon(QIcon("icons/right.png"))
    btn_next.setIconSize(QSize(40, 40))
    btn_next.resize(40, 40)
    btn_next.setStyleSheet(style)
    btn_next.move(1800, 265)
    if on_next:
        btn_next.clicked.connect(on_next)

    return btn_prev, btn_next
