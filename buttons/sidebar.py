from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import QSize


def create_sidebar_buttons(parent, font_family,
                           on_home=None,  on_settings=None):

                 
    style = _sidebar_button_style()

             
    btn_home = QPushButton("   Главное", parent)
    btn_home.setIcon(QIcon("icons/mainMenu.png"))
    btn_home.setIconSize(QSize(17, 17))
    btn_home.resize(225, 75)
    btn_home.setFont(QFont(font_family, 12))
    btn_home.setStyleSheet(style)
    btn_home.move(53, 143)
    if on_home:
        btn_home.clicked.connect(on_home)

               
    btn_settings = QPushButton("   Настройки", parent)
    btn_settings.setIcon(QIcon("icons/settings.png"))
    btn_settings.setIconSize(QSize(19, 19))
    btn_settings.resize(225, 75)
    btn_settings.setFont(QFont(font_family, 12))
    btn_settings.setStyleSheet(style)
    btn_settings.move(53, 218)
    if on_settings:
        btn_settings.clicked.connect(on_settings)

    return btn_home, btn_settings


def _sidebar_button_style():
    return """
        QPushButton {
            padding: 10px;
            text-align: left;
            border: none;
            color: white;
            background-color: transparent;
            border-radius: 8px;
            font-size: 20px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 40);
        }
        QPushButton:pressed {
            background-color: rgba(255, 255, 255, 16);
        }
    """
