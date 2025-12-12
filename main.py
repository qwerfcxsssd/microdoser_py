import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase

from main_window import MainWindow


def load_font(path, fallback="Arial"):
    if not os.path.exists(path):
        print(f"Предупреждение: шрифт не найден: {path}")
        return fallback

    font_id = QFontDatabase.addApplicationFont(path)
    families = QFontDatabase.applicationFontFamilies(font_id)
    return families[0] if families else fallback


def main():
    app = QApplication(sys.argv)

    # Загружаем шрифты
    font_circled = load_font("fonts/circled.ttf", "Arial")
    font_semibold = load_font("fonts/MontserratAlternates-SemiBold.ttf", "Arial")

    print(f"Загружены шрифты: {font_circled}, {font_semibold}")

    # Передаём 2 шрифта в окно
    window = MainWindow(
        font_circled,
        font_semibold
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()