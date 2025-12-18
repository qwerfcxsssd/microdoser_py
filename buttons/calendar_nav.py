from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

def create_calendar_nav_buttons(parent, on_prev=None, on_next=None):


    style = """
        QPushButton {
            background: transparent;
            border: none;
            border-radius: 16px;
            font-size: 30px;
            color: white;
        }
        QPushButton:hover {
            background-color: rgba(255,255,255,0);
        }
        QPushButton:pressed {
            background-color: rgba(255,255,255,0);
        }
    """

               
    btn_prev = QPushButton("<", parent)

    btn_prev.setIconSize(QSize(30, 30))
    btn_prev.resize(30, 30)
    btn_prev.setStyleSheet(style)
    btn_prev.move(1305, 215)
    if on_prev:
        btn_prev.clicked.connect(on_prev)

               
    btn_next = QPushButton(">",parent)
    btn_next.setIconSize(QSize(30, 30))
    btn_next.resize(30, 30)
    btn_next.setStyleSheet(style)
    btn_next.move(1350, 215)
    if on_next:
        btn_next.clicked.connect(on_next)




    return btn_prev, btn_next
