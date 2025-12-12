from PySide6.QtWidgets import QPushButton


def create_bottom_buttons(parent, font_family):

    style_pick = f"""
        QPushButton {{
            background-color: rgba(83,83,87,255);
            border-radius: 16px;
            color: white;
            font-size: 24px;
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
            font-size: 24px;
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

    # Подобрать лекарство
    btn_pick = QPushButton("Подобрать лекарство", parent)
    btn_pick.resize(639, 95)
    btn_pick.setStyleSheet(style_pick)
    btn_pick.move(516, 893)

    # Добавить лекарство
    btn_add = QPushButton("Добавить лекарство", parent)
    btn_add.resize(639, 95)
    btn_add.setStyleSheet(style_add)
    btn_add.move(1201, 893)

    return btn_add, btn_pick
