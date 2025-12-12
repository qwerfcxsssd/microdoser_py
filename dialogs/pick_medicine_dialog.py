from PySide6.QtWidgets import (
    QDialog, QLabel, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QWidget
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class PickMedicineDialog(QDialog):


    def __init__(self, font_title: str, font_text: str, parent=None):
        super().__init__(parent)

        self.font_title = font_title
        self.font_text = font_text

        self.setModal(True)
        self.setWindowTitle("Подобрать лекарства")
        self.setFixedSize(1200, 700)

        # фон окна
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(90, 90, 90, 255);
            }
            QLabel {
                color: rgba(240,240,240,240);
            }
            QTextEdit {
                background-color: rgba(120,120,120,190);
                border: 1px solid rgba(255,255,255,40);
                border-radius: 16px;
                color: rgba(245,245,245,240);
                padding: 14px;
                font-size: 18px;
            }
            QPushButton {
                border: none;
                border-radius: 16px;
                font-size: 18px;
                color: white;
                padding: 12px 18px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,30);
            }
            QPushButton:pressed {
                background-color: rgba(255,255,255,16);
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 18, 28, 22)
        root.setSpacing(18)


        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Подобрать лекарства")
        f = QFont(self.font_title, 22)
        f.setWeight(QFont.Weight.DemiBold)
        title.setFont(f)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(40, 40)
        btn_close.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 22px;
                color: rgba(240,240,240,240);
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,25);
                border-radius: 12px;
            }
            QPushButton:pressed {
                background-color: rgba(255,255,255,16);
                border-radius: 12px;
            }
        """)
        btn_close.clicked.connect(self.reject)

        top_row.addWidget(title)
        top_row.addStretch(1)
        top_row.addWidget(btn_close)

        root.addLayout(top_row)


        lbl1 = QLabel("Введите что вас беспокоит:")
        lbl1.setFont(QFont(self.font_text, 14))

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Например: головная боль, температура, насморк…")
        self.input_text.setFont(QFont(self.font_text, 16))
        self.input_text.setFixedHeight(190)
        self.input_text.textChanged.connect(self._update_recommendations_stub)

        root.addWidget(lbl1)
        root.addWidget(self.input_text)


        lbl2 = QLabel("Наши рекомендации:")
        lbl2.setFont(QFont(self.font_text, 14))

        self.recommendations = QTextEdit()
        self.recommendations.setReadOnly(True)
        self.recommendations.setFont(QFont(self.font_text, 16))
        self.recommendations.setFixedHeight(230)
        self.recommendations.setText("Пока рекомендаций нет. Опишите симптомы выше.")

        root.addWidget(lbl2)
        root.addWidget(self.recommendations)


        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(16)

        hint = QLabel("Добавить это лекарство в список приема?")
        hint.setFont(QFont(self.font_text, 14))
        hint.setStyleSheet("color: rgba(240,240,240,190);")

        bottom.addWidget(hint)
        bottom.addStretch(1)

        btn_accept = QPushButton("Принять")
        btn_accept.setFixedSize(150, 52)
        btn_accept.setStyleSheet("""
            QPushButton {
                background-color: rgba(131, 123, 228, 255);
                border-radius: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(107, 80, 156, 220);
            }
            QPushButton:pressed {
                background-color: rgba(107, 80, 156, 190);
            }
        """)
        btn_accept.clicked.connect(self.accept)

        btn_cancel = QPushButton("Отказаться")
        btn_cancel.setFixedSize(170, 52)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: rgba(120,120,120,210);
                border-radius: 16px;
                font-weight: 600;
            }
        """)
        btn_cancel.clicked.connect(self.reject)

        bottom.addWidget(btn_accept)
        bottom.addWidget(btn_cancel)

        root.addLayout(bottom)

    def _update_recommendations_stub(self):

        #Заглушка

        text = self.get_user_text().strip()
        if not text:
            self.recommendations.setText("Пока рекомендаций нет. Опишите симптомы выше.")
            return

    def get_user_text(self) -> str:
        return self.input_text.toPlainText()

    def get_recommendations_text(self) -> str:
        return self.recommendations.toPlainText()
