from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QTextEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class PickMedicineDialog(QDialog):
    def __init__(self, font_title: str, font_text: str, parent=None):
        super().__init__(parent)

        self.font_title = font_title
        self.font_text = font_text

        self.setModal(True)
        self.setWindowTitle("Подобрать лекарство")
        self.setFixedSize(1300, 760)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: rgba(90,90,90,255);
            }}

            QLabel {{
                color: rgba(240,240,240,240);
                font-family: '{self.font_text}';
            }}

            QLineEdit, QTextEdit {{
                background: transparent;
                border: none;
                outline: none;
                color: rgba(245,245,245,240);
                font-size: 18px;
                font-family: '{self.font_text}';
            }}

            QTextEdit::viewport {{
                background: transparent;
                border: none;
            }}

            QLineEdit::placeholder, QTextEdit::placeholder {{
                color: rgba(240,240,240,140);
            }}

            QPushButton {{
                border: none;
                border-radius: 16px;
                font-size: 18px;
                color: white;
                font-family: '{self.font_text}';
                padding: 12px 18px;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 24)
        root.setSpacing(18)

        title = QLabel("Подобрать лекарство")
        title_font = QFont(self.font_title, 26)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        root.addWidget(title)


        lbl1 = QLabel("Введите свои симптомы")
        lbl1.setFont(QFont(self.font_text, 14))
        root.addWidget(lbl1)

        search_panel, self.search = self._make_line_panel(
            "Например: головная боль, температура",
            height=70
        )
        root.addWidget(search_panel)

        lbl2 = QLabel("Результат подбора:")
        lbl2.setFont(QFont(self.font_text, 14))
        root.addWidget(lbl2)

        result_panel, self.result = self._make_text_panel(
            "Здесь появится информация о подходящем лекарстве",
            height=380
        )
        root.addWidget(result_panel)

        root.addStretch()

        bottom = QHBoxLayout()

        bottom_label = QLabel("Добавить это лекарство?")
        bottom_font = QFont(self.font_text, 15)
        bottom_font.setWeight(QFont.Weight.DemiBold)
        bottom_label.setFont(bottom_font)
        bottom_label.setStyleSheet("color: rgba(240,240,240,210);")

        bottom.addWidget(bottom_label)
        bottom.addStretch()

        add_btn = QPushButton("Добавить")
        add_btn.setFixedSize(160, 56)
        add_btn.setStyleSheet("background-color: rgba(131,123,228,255);")
        add_btn.clicked.connect(self.accept)


        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedSize(190, 56)
        cancel_btn.setStyleSheet("background-color: rgba(120,120,120,210);")
        cancel_btn.clicked.connect(self.reject)

        bottom.addWidget(add_btn)
        bottom.addWidget(cancel_btn)
        root.addLayout(bottom)


    def _panel_style(self):
        return """
            QWidget {
                background-color: rgba(120,120,120,190);
                border-radius: 14px;
            }
        """

    def _make_line_panel(self, placeholder: str, height: int):
        panel = QWidget()
        panel.setStyleSheet(self._panel_style())
        panel.setFixedHeight(height)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(height)
        edit.setStyleSheet("""
            QLineEdit {
                padding-left: 18px;
                padding-right: 18px;
                padding-top: 8px;
                padding-bottom: 8px;
            }
        """)

        layout.addWidget(edit)
        return panel, edit

    def _make_text_panel(self, placeholder: str, height: int):
        panel = QWidget()
        panel.setStyleSheet(self._panel_style())
        panel.setFixedHeight(height)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        edit = QTextEdit()
        edit.setPlaceholderText(placeholder)
        edit.setReadOnly(True)
        edit.setFocusPolicy(Qt.NoFocus)
        edit.setCursor(Qt.ArrowCursor)
        edit.setFrameStyle(QTextEdit.NoFrame)
        edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        edit.setStyleSheet("""
            QTextEdit {
                padding-left: 18px;
                padding-right: 18px;
                padding-top: 10px;
                padding-bottom: 10px;
            }
            QTextEdit::viewport {
                background: transparent;
            }
        """)

        layout.addWidget(edit)
        return panel, edit
