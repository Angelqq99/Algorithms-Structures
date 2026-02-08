"""
Точка входа приложения визуализатора алгоритмов.
"""
import sys
from PyQt6.QtWidgets import QApplication
from view.main_window import MainWindow
import io



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    if sys.platform == "win32":
        # Устанавливаем line_buffering=True для немедленного вывода
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, 
            encoding='utf-8',
            line_buffering=True
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, 
            encoding='utf-8',
            line_buffering=True
        )
    main()