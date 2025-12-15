from PySide6.QtWidgets import QPushButton


def create_bottom_buttons(parent, font_family):

    style_pick = f"""
        QPushButton {{
            background-color: rgba(83,83,87,255);
            border-radius: 16px;
            color: white;
            font-size: 20px;
            font-family: '{font_family}';
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: rgba(255,255,255,45);
        }}
        QPushButton:pressed {{
            background-color: rgba(255,255,255,25);
        }}
    """

    style_add = f"""
        QPushButton {{
            background-color: rgba(107, 80, 156, 255);
            border-radius: 16px;
            color: white;
            font-size: 20px;
            font-family: '{font_family}';
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: rgba(255,255,255,45);
        }}
        QPushButton:pressed {{
            background-color: rgba(255,255,255,25);
        }}
    """

                         
    btn_pick = QPushButton("Подобрать лекарство", parent)
    btn_pick.resize(479, 79)
    btn_pick.setStyleSheet(style_pick)
    btn_pick.move(387, 741)

                        
    btn_add = QPushButton("Добавить лекарство", parent)
    btn_add.resize(479, 79)
    btn_add.setStyleSheet(style_add)
    btn_add.move(901, 741)

    return btn_add, btn_pick
