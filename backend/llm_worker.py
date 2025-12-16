from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal, Qt

from backend.llm_service import ask_openrouter_json, DEFAULT_MODEL



class _Worker(QObject):
    ok = Signal(dict)
    err = Signal(str)
    finished = Signal()



    def __init__(self, *, model: str, language: str, user_text: str, api_key: str | None):
        super().__init__()
        self.model = model or DEFAULT_MODEL
        self.language = language or "ru"
        self.user_text = user_text
        self.api_key = api_key

    def run(self):
        try:
            data = ask_openrouter_json(
                api_key=self.api_key,
                model=self.model,
                language=self.language,
                user_text=self.user_text,
            )
            self.ok.emit(data)
        except Exception as e:
            self.err.emit(str(e))
        finally:
            self.finished.emit()


def run_llm_in_thread(
    *,
    model: str,
    language: str,
    user_text: str,
    api_key: str | None,
    on_ok,
    on_err,
) -> QThread:
    thread = QThread()
    worker = _Worker(model=model, language=language, user_text=user_text, api_key=api_key)
    worker.moveToThread(thread)

    thread.started.connect(worker.run)

    worker.ok.connect(on_ok, Qt.ConnectionType.QueuedConnection)
    worker.err.connect(on_err, Qt.ConnectionType.QueuedConnection)

    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

                                                   
    thread._worker = worker                              

    thread.start()
    return thread
