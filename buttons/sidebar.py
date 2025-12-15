from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import QSize


def create_sidebar_buttons(parent, font_family,
                           on_home=None, on_diary=None, on_settings=None):

                 
    style = _sidebar_button_style()

             
    btn_home = QPushButton("   Главное", parent)
    btn_home.setIcon(QIcon("icons/mainMenu.png"))
    btn_home.setIconSize(QSize(23, 23))
    btn_home.resize(300, 90)
    btn_home.setFont(QFont(font_family, 16))
    btn_home.setStyleSheet(style)
    btn_home.move(70, 172)
    if on_home:
        btn_home.clicked.connect(on_home)

                
    btn_diary = QPushButton("   Ежедневник", parent)
    btn_diary.setIcon(QIcon("icons/diary.png"))
    btn_diary.setIconSize(QSize(23, 23))
    btn_diary.resize(300, 90)
    btn_diary.setFont(QFont(font_family, 16))
    btn_diary.setStyleSheet(style)
    btn_diary.move(70, 263)
    if on_diary:
        btn_diary.clicked.connect(on_diary)

               
    btn_settings = QPushButton("   Настройки", parent)
    btn_settings.setIcon(QIcon("icons/settings.png"))
    btn_settings.setIconSize(QSize(25, 25))
    btn_settings.resize(300, 90)
    btn_settings.setFont(QFont(font_family, 16))
    btn_settings.setStyleSheet(style)
    btn_settings.move(70, 356)
    if on_settings:
        btn_settings.clicked.connect(on_settings)

    return btn_home, btn_diary, btn_settings


def _sidebar_button_style():
    return """
        QPushButton {
            padding: 10px;
            text-align: left;
            border: none;
            color: white;
            background-color: transparent;
            border-radius: 8px;
            font-size: 24px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 40);
        }
        QPushButton:pressed {
            background-color: rgba(255, 255, 255, 16);
        }
    """
