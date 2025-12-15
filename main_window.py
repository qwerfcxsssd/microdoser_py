from PySide6.QtWidgets import QWidget, QLineEdit, QStackedWidget, QLabel, QDialog, QMessageBox, QProgressDialog
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPixmap
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread

from buttons.calendar import Calendar
from buttons.reminders_panel import RemindersPanel, ReminderItemData

                              
from buttons.sidebar import create_sidebar_buttons
from buttons.bottom_bar import create_bottom_buttons
from buttons.calendar_nav import create_calendar_nav_buttons
from buttons.search_button import create_search_button

        
from screens.home_screen import HomeScreen
from screens.settings_screen import SettingsScreen

         
from dialogs.pick_medicine_dialog import PickMedicineDialog
from dialogs.add_medicine_dialog import AddMedicineDialog

from backend.db import connect, init_db
from backend.save_llm_result import save_llm_result
from backend.llm_service import ask_openrouter_json, DEFAULT_MODEL
from backend.settings import get_setting
import os
from backend.repositories import CalendarRepo

from datetime import datetime, timedelta



class _AddMedicineLlmWorker(QObject):
    ok = Signal(dict)
    err = Signal(str)
    finished = Signal()

    def __init__(self, api_key: str, model: str, language: str, user_text: str):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.language = language
        self.user_text = user_text

    @Slot()
    def run(self):
        try:
            data = ask_openrouter_json(
                api_key=self.api_key,
                model=self.model,
                language=self.language,
                user_text=self.user_text,
            )
            if not isinstance(data, dict):
                raise ValueError("LLM вернул не dict")
            self.ok.emit(data)
        except Exception as e:
            self.err.emit(str(e))
        finally:
            self.finished.emit()


class MainWindow(QWidget):
    def __init__(self, font_circled: str, font_semibold: str):
        super().__init__()

            
        self.conn = connect()
        init_db(self.conn)

        self.font_circled = font_circled
        self.font_semibold = font_semibold

        self.setWindowTitle("Micro Doser")
        self.resize(1920, 1080)

        self.stacked = QStackedWidget(self)
        self.stacked.setGeometry(516, 200, 1320, 650)

        self.page_home = HomeScreen(self.font_circled, self.font_semibold)

        self.page_settings = SettingsScreen(self.font_semibold, self.font_circled, conn=self.conn)

        self.stacked.addWidget(self.page_home)
        self.stacked.addWidget(self.page_settings)           

                                    
        self.reminders_panel = RemindersPanel(
            self.page_home,
            font_title=self.font_semibold,
            font_text=self.font_circled,
        )
        self.reminders_panel.move(0, 130)
        self.reminders_panel.setVisible(False)

                            
        self.calendar = Calendar(
            self.page_home,
            font_text=self.font_circled,
            font_semibold=self.font_semibold
        )
        self.calendar.move(730, 130)                     
        self.calendar.setVisible(False)
        self.calendar.date_selected.connect(self.on_calendar_date_selected)

                                          
        self.month_out = QLabel(self.page_home)
        self.month_out.setText(self.calendar.month_text())
        self.month_out.setStyleSheet("""
            QLabel {
                background-color: rgba(255,255,255,160);
                color: rgba(25,25,25,230);
                border-radius: 18px;
                padding-left: 18px;
                padding-right: 18px;
            }
        """)
        f = QFont(self.font_circled, 14)
        f.setWeight(QFont.Weight.DemiBold)
        self.month_out.setFont(f)
        self.month_out.setFixedHeight(42)
        self.month_out.adjustSize()
        self.month_out.move(1015, 64)
        self.month_out.setVisible(False)

                       
        self.btn_add_medicine, self.btn_pick_medicine = create_bottom_buttons(self, self.font_semibold)
        self.btn_pick_medicine.clicked.connect(lambda _checked=False: self.open_pick_medicine_dialog())
        self.btn_add_medicine.clicked.connect(lambda _checked=False: self.open_add_medicine_dialog())

                                                       
        self.btn_pick_medicine.raise_()
        self.btn_add_medicine.raise_()

                           
        self.prev_month_btn, self.next_month_btn = create_calendar_nav_buttons(
            self, on_prev=self.on_prev_month_clicked, on_next=self.on_next_month_clicked
        )

                                      
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Поиск")
                                                                      
        self.search_input.setFixedSize(1220, 52)
        self.search_input.setStyleSheet(
            f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: white;
                padding-left: 20px;
                font-size: 24px;
                font-family: '{self.font_circled}';
            }}
            """
        )
        self.search_input.move(530, 99)

        self.search_button = create_search_button(self, self.on_search_clicked)

        self.btn_home, self.btn_settings = create_sidebar_buttons(
            self,
            self.font_circled,
            on_home=self.show_home,
            on_settings=self.show_settings,
        )

        self.show_home()

                                            
        self.refresh_home_planner()

    def open_pick_medicine_dialog(self, _checked: bool = False):
        print("CLICK: open_pick_medicine_dialog")

        try:
            from PySide6.QtCore import QDate
            qd = getattr(self.calendar, "selected_date", None)
            if not qd or not isinstance(qd, QDate):
                qd = QDate.currentDate()
            start_date = qd.toString("yyyy-MM-dd")
        except Exception:
            start_date = ""

        try:
            if getattr(self, "_pick_medicine_dlg", None) is not None and self._pick_medicine_dlg.isVisible():
                self._pick_medicine_dlg.raise_()
                self._pick_medicine_dlg.activateWindow()
                return
        except Exception:
            self._pick_medicine_dlg = None

        try:
            print("ABOUT TO CREATE DIALOG")
            self._pick_medicine_dlg = PickMedicineDialog(
                font_title=self.font_semibold,
                font_text=self.font_circled,
                conn=self.conn,
                start_date=start_date,
                parent=self
            )
            print("DIALOG CREATED")
            self._pick_medicine_dlg.raise_()
            self._pick_medicine_dlg.activateWindow()

            res = self._pick_medicine_dlg.exec()
            print("DIALOG RESULT:", res)

                                                                      
            if res != QDialog.DialogCode.Accepted:
                return

            data = None
            try:
                data = self._pick_medicine_dlg.get_llm_json()
            except Exception:
                data = None

            if not isinstance(data, dict):
                QMessageBox.information(
                    self,
                    "Подобрать лекарство",
                    "Сначала нажми «Подобрать», дождись результата и затем «Добавить»."
                )
                return

                                                                                 
            try:
                planner = data.setdefault("planner", {})
                if isinstance(planner, dict) and start_date and "start_date" not in planner:
                    planner["start_date"] = start_date
            except Exception:
                pass

                                    
            try:
                model = self._pick_medicine_dlg.get_model_name()
                language = self._pick_medicine_dlg.get_language()
                user_text = self._pick_medicine_dlg.get_user_text()
            except Exception:
                model = (get_setting(self.conn, "llm_model", DEFAULT_MODEL) or DEFAULT_MODEL).strip()
                language = (get_setting(self.conn, "language", "ru") or "ru").strip()
                user_text = ""

            save_llm_result(self.conn, llm_json=data, model=model, user_text=user_text, language=language)
            self.refresh_home_planner()
            QMessageBox.information(self, "Готово", "План добавлен в ежедневник.")

        except Exception:
            import traceback
            tb = traceback.format_exc()
            print(tb)
            QMessageBox.critical(self, "Ошибка открытия/выполнения", tb)

    def open_add_medicine_dialog(self):
        dlg = AddMedicineDialog(
            font_title=self.font_semibold,
            font_text=self.font_circled,
            parent=self
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        medicine_name = (dlg.get_name_dose() or "").strip()
        if not medicine_name:
            QMessageBox.information(self, "Добавить лекарство", "Введите название лекарства.")
            return

                       
        api_key = (get_setting(self.conn, "openrouter_api_key", "") or "").strip()
        model = (get_setting(self.conn, "llm_model", DEFAULT_MODEL) or DEFAULT_MODEL).strip()
        language = (get_setting(self.conn, "language", "ru") or "ru").strip()

        if not api_key:
            api_key = os.getenv("OPENROUTER_API_KEY", "").strip()

        if not api_key:
            QMessageBox.warning(self, "LLM", "Не задан API key. Открой Настройки → LLM / API и вставь ключ.")
            return

                                                    
        try:
            sd = self.calendar.selected_date
            start_date = f"{sd.year():04d}-{sd.month():02d}-{sd.day():02d}"
        except Exception:
            start_date = datetime.now().strftime("%Y-%m-%d")

                                                                
        user_text = (
            f"Лекарство: {medicine_name}\n"
            f"Стартовая дата для плана: {start_date}\n\n"
            "Составь примерный план напоминаний о приёме. "
            "Требования:\n"
            "1) Верни recommendations ровно с 1 объектом.\n"
            "2) Если точная дозировка неизвестна — НЕ выдумывай, пиши 'см. инструкцию/назначение врача'.\n"
            "3) В planner.calendar_events создай напоминания (title, datetime, duration_min, note) минимум на 3–7 дней, "
            "datetime строго YYYY-MM-DDTHH:MM, начиная с указанной стартовой даты.\n"
            "4) Верни ТОЛЬКО один валидный JSON по схеме."
        )

                      
        self._add_med_progress = QProgressDialog("Генерирую план…", None, 0, 0, self)
        self._add_med_progress.setWindowTitle("LLM")
        self._add_med_progress.setWindowModality(Qt.ApplicationModal)
        self._add_med_progress.setCancelButton(None)
        self._add_med_progress.show()

                                                               
        self._add_med_thread = QThread(self)
        self._add_med_worker = _AddMedicineLlmWorker(api_key, model, language, user_text)
        self._add_med_worker.moveToThread(self._add_med_thread)

                                                                                        
        self._add_med_ctx = {
            "start_date": start_date,
            "user_text": user_text,
            "model": model,
            "language": language,
        }

        self._add_med_thread.started.connect(self._add_med_worker.run)
                                                                                     
                                                                                           
        self._add_med_worker.ok.connect(self._add_med_on_ok, Qt.ConnectionType.QueuedConnection)
        self._add_med_worker.err.connect(self._add_med_on_err, Qt.ConnectionType.QueuedConnection)

        self._add_med_worker.finished.connect(self._add_med_thread.quit)
        self._add_med_worker.finished.connect(self._add_med_worker.deleteLater)
        self._add_med_thread.finished.connect(self._add_med_thread.deleteLater)
        self._add_med_thread.finished.connect(self._add_med_on_finished)

        self._add_med_thread.start()


    def paintEvent(self, event):
        painter = QPainter(self)

        painter.fillRect(self.rect(), QColor("#2C2C2C"))

        painter.setBrush(QBrush(QColor(75, 75, 75)))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, 435, self.height())

                                                      
                                                                 
        try:
            on_home = self.stacked.currentWidget() == self.page_home
        except Exception:
            on_home = True

        if on_home:
            painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
            painter.setPen(Qt.NoPen)
                                                     
            painter.drawRoundedRect(500, 78, 1330, 95, 30, 30)

                                                                            

        def text_with_icon(x, y, text, icon_path, icon_size=32, icon_offset_y=0):
            ipix = QPixmap(icon_path)
            if not ipix.isNull():
                painter.drawPixmap(x, y + icon_offset_y, icon_size, icon_size, ipix)

            painter.setPen(QColor(255, 255, 255))
            font_title = QFont(self.font_semibold, 30)
            font_title.setWeight(QFont.Weight.DemiBold)
            painter.setFont(font_title)
            painter.drawText(x + icon_size + 15, y + 33, text)

        text_with_icon(67, 100, "Micro Doser", "icons/pils.png", 40, icon_offset_y=6)

    def _set_home_ui_visible(self, visible: bool):
        self.search_input.setVisible(visible)
        self.search_button.setVisible(visible)
        self.prev_month_btn.setVisible(visible)
        self.next_month_btn.setVisible(visible)
        self.btn_add_medicine.setVisible(visible)
        self.btn_pick_medicine.setVisible(visible)

        self.calendar.setVisible(visible)
        self.month_out.setVisible(visible)

        self.reminders_panel.setVisible(visible)

        self.update()

                            
                                                 
                            
    @Slot(dict)
    def _add_med_on_ok(self, data: dict):
        try:
            ctx = getattr(self, "_add_med_ctx", {}) or {}
            start_date = ctx.get("start_date")
            user_text = ctx.get("user_text")
            model = ctx.get("model")
            language = ctx.get("language")

                                           
            recs = data.get("recommendations")
            if isinstance(recs, list) and len(recs) > 1:
                data = dict(data)
                data["recommendations"] = [recs[0]]

                                            
            try:
                planner = data.setdefault("planner", {})
                if isinstance(planner, dict) and start_date and "start_date" not in planner:
                    planner["start_date"] = start_date
            except Exception:
                pass

            save_llm_result(self.conn, llm_json=data, model=model, user_text=user_text, language=language)
            self.refresh_home_planner()
            QMessageBox.information(self, "Готово", "План добавлен в ежедневник.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    @Slot(str)
    def _add_med_on_err(self, msg: str):
        QMessageBox.critical(self, "Ошибка LLM", msg)

    @Slot()
    def _add_med_on_finished(self):
        try:
            if getattr(self, "_add_med_progress", None) is not None:
                self._add_med_progress.close()
        except Exception:
            pass
        self._add_med_worker = None
        self._add_med_thread = None
        self._add_med_ctx = None

    def _refresh_month_out(self):
        self.month_out.setText(self.calendar.month_text())
        self.month_out.adjustSize()

    def on_prev_month_clicked(self):
        self.calendar.prev_month()
        self._refresh_month_out()
        self.refresh_home_planner()

    def on_next_month_clicked(self):
        self.calendar.next_month()
        self._refresh_month_out()
        self.refresh_home_planner()

    def on_calendar_date_selected(self, qdate):
                                                       
        self.refresh_home_planner()

    def refresh_home_planner(self):
    
        try:
            repo = CalendarRepo(self.conn)

                                       
            y = self.calendar.current_date.year()
            m = self.calendar.current_date.month()
            first = datetime(y, m, 1, 0, 0, 0)
                                      
            if m == 12:
                next_month = datetime(y + 1, 1, 1, 0, 0, 0)
            else:
                next_month = datetime(y, m + 1, 1, 0, 0, 0)
            last = next_month - timedelta(seconds=1)

            month_events = repo.list_between(first.strftime("%Y-%m-%dT%H:%M:%S"), last.strftime("%Y-%m-%dT%H:%M:%S"))
            days_with_events = set()
            for r in month_events:
                try:
                    dt = datetime.strptime(r["start_local"], "%Y-%m-%dT%H:%M:%S")
                    days_with_events.add(dt.day)
                except Exception:
                    continue
            self.calendar.set_marked_days(days_with_events)

                            
            sd = self.calendar.selected_date
            start = datetime(sd.year(), sd.month(), sd.day(), 0, 0, 0)
            end = datetime(sd.year(), sd.month(), sd.day(), 23, 59, 59)
            day_events = repo.list_between(start.strftime("%Y-%m-%dT%H:%M:%S"), end.strftime("%Y-%m-%dT%H:%M:%S"))

            items = []
            for r in day_events:
                items.append(
                    ReminderItemData(
                        title=r["title"],
                        start_local=r["start_local"],
                        notes=r["notes"],
                    )
                )
                                   
            items.sort(key=lambda i: i.start_local)
            self.reminders_panel.set_header_date(sd.toString("dd.MM.yyyy"))
            self.reminders_panel.set_items(items)
        except Exception:
            import traceback
            traceback.print_exc()

    def on_search_clicked(self):
        print("Ищем по:", self.search_input.text())

    def show_home(self):
        self._set_home_ui_visible(True)
        self.stacked.setCurrentWidget(self.page_home)

                                                                         
        self.refresh_home_planner()

                                                       
        self.btn_pick_medicine.raise_()
        self.btn_add_medicine.raise_()

    def show_diary(self):
        self._set_home_ui_visible(False)
        self.stacked.setCurrentWidget(self.page_diary)

    def show_settings(self):
        self._set_home_ui_visible(False)
        self.stacked.setCurrentWidget(self.page_settings)