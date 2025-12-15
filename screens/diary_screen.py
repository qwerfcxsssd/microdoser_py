from PySide6.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QLabel, QFrame, QPushButton
)
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt, Signal, QEvent


from backend.db import connect, init_db
from backend.save_llm_result import save_llm_result
from dialogs.pick_medicine_dialog import PickMedicineDialog



WEEKDAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
]


class DayRow(QFrame):

    clicked = Signal(str)

    def __init__(self, text: str, font_text: str):
        super().__init__()
        self.text = text
        self.font_text = font_text
        self.setFixedHeight(86)

        self.btn = QPushButton(self)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setStyleSheet("QPushButton{background:transparent;border:none;}")
        self.btn.clicked.connect(lambda: self.clicked.emit(self.text))

               
        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont(self.font_text, 16))
        self.lbl.setStyleSheet("color: rgba(255,255,255,210);")
        self.lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.lbl.setContentsMargins(34, 0, 0, 0)

        self._hover = False
        self._pressed = False

                                         
        self.btn.installEventFilter(self)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.btn.setGeometry(0, 0, self.width(), self.height())
        self.lbl.setGeometry(0, 0, self.width(), self.height())

    def eventFilter(self, obj, event):
        if obj is self.btn:
            t = event.type()

            if t == QEvent.Type.Enter:
                self._hover = True
                self.update()

            elif t == QEvent.Type.Leave:
                self._hover = False
                self._pressed = False
                self.update()

            elif t == QEvent.Type.MouseButtonPress:
                                                                         
                if hasattr(event, "button") and event.button() == Qt.LeftButton:
                    self._pressed = True
                    self.update()

            elif t == QEvent.Type.MouseButtonRelease:
                self._pressed = False
                self.update()

        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)


        bg = QColor(117, 117, 117, 90)
        border = QColor(255, 255, 255, 55)

        if self._pressed:
            bg = QColor(117, 117, 117, 120)
            border = QColor(255, 255, 255, 75)
        elif self._hover:
            bg = QColor(117, 117, 117, 105)
            border = QColor(255, 255, 255, 70)

        r = self.rect().adjusted(1, 1, -1, -1)
        p.setPen(border)
        p.setBrush(bg)
        p.drawRoundedRect(r, 18, 18)


class DiaryScreen(QWidget):

    def __init__(self, font_title: str, font_text: str):
        super().__init__()
        self.font_title = font_title
        self.font_text = font_text

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; }
            QScrollBar:vertical { width: 10px; background: transparent; }
            QScrollBar::handle:vertical { background: rgba(255,255,255,40); border-radius: 5px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(60, 40, 70, 60)
        body_layout.setSpacing(18)

        title = QLabel("Ежедневник")
        title.setFont(QFont(self.font_title, 26))
        title.setStyleSheet("color: rgba(255,255,255,235);")

        subtitle = QLabel("Эта неделя")
        subtitle.setFont(QFont(self.font_text, 12))
        subtitle.setStyleSheet("color: rgba(255,255,255,120);")

        body_layout.addWidget(title)
        body_layout.addWidget(subtitle)
        body_layout.addSpacing(10)

        for day in WEEKDAYS:
            pill = DayRow(day, self.font_text)
            body_layout.addWidget(pill)

        body_layout.addStretch(1)

        self.scroll.setWidget(body)
        root.addWidget(self.scroll)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(0, 0, 0, 0))


    def open_pick_medicine_dialog(self):
        dlg = PickMedicineDialog(
            font_title=self.font_semibold,
            font_text=self.font_circled,
            parent=self
        )

        if dlg.exec() == dlg.Accepted:
            llm_json = dlg.get_llm_json()
            if not llm_json:
                return

            save_llm_result(
                self.conn,
                llm_json=llm_json,
                model=dlg.get_model_name(),                       
                user_text=dlg.get_user_text(),
                language=dlg.get_language()
            )

                                                                   
                                                    

