"""
Менеджер для управления окнами теории
"""

import json
import os
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox


class TheoryManager(QObject):
    """Менеджер окон теории"""
    
    theory_window_created = pyqtSignal()
    theory_window_closed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.theory_windows = {}
        self.current_category = None
        self.current_algorithm = None
        self._window_counter = 0  # Счетчик для создания уникальных ключей
        
        # Загружаем все JSON файлы с теорией
        self.theory_data = self._load_all_theory_files()
    
    def _load_all_theory_files(self):
        """Загружает все JSON файлы с теорией из папки theory/"""
        theory_data = {}
        
        # Список всех JSON файлов с теорией
        theory_files = [
            "hash_tables.json",
            "probabilistic.json",
            "search.json", 
            "sorting.json",
            "trees.json",
            "compression.json",
            "data_structures.json",
            "graphs.json"
        ]
        
        # Создаем папку theory, если её нет
        os.makedirs("theory", exist_ok=True)
        
        for file_name in theory_files:
            file_path = os.path.join("D:\Programming\Projects\diplom\diplom\src\\view\\theory", file_name)
            
            # Извлекаем имя категории из имени файла
            category_name = file_name.replace(".json", "")
            
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        theory_data[category_name] = json.load(f)
                        print(f"✅ Загружен файл теории: {file_name}")
                else:
                    # Создаем пустой файл
                    theory_data[category_name] = {}
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump({}, f, ensure_ascii=False, indent=2)
                    print(f"⚠️ Создан пустой файл: {file_name}")
            except Exception as e:
                print(f"❌ Ошибка загрузки {file_name}: {str(e)}")
                theory_data[category_name] = {}
        
        return theory_data
    
    def show_theory_window(self, category=None, algorithm=None):
        """
        Показывает окно теории
        
        Args:
            category: Ключ категории (например, "sorting", "trees")
            algorithm: Ключ алгоритма (например, "QuickSort", "BST")
        """
        try:
            # Создаем новый ключ окна
            self._window_counter += 1
            window_key = f"theory_{self._window_counter}"
            
            # Создаем новое окно
            from view.theory_window import TheoryWindow
            window = TheoryWindow(self.theory_data)
            
            # Предварительно выбираем категорию и алгоритм
            if category and algorithm:
                window.show_category(category, algorithm)
            elif category:
                window.show_category(category)
            
            # Сохраняем ссылку на окно
            self.theory_windows[window_key] = window
            
            # Подключаем сигнал закрытия окна
            window.destroyed.connect(
                lambda: self._on_window_destroyed(window_key)
            )
            
            # Показываем и активируем окно
            window.show()
            window.raise_()
            window.activateWindow()
            
            self.theory_window_created.emit()
            
            # Сохраняем текущий выбор
            self.current_category = category
            self.current_algorithm = algorithm
            
            return window
            
        except Exception as e:
            print(f"❌ Ошибка создания окна теории: {str(e)}")
            import traceback
            traceback.print_exc()
            
            QMessageBox.critical(
                None, 
                "Ошибка", 
                f"Не удалось открыть окно теории:\n{str(e)}"
            )
            return None
    
    def get_current_theory(self):
        """Возвращает текущую выбранную теорию"""
        return {
            "category": self.current_category,
            "algorithm": self.current_algorithm
        }
    
    def has_open_windows(self):
        """Проверяет, есть ли открытые окна теории"""
        return len(self.theory_windows) > 0
    
    def close_all_windows(self):
        """Закрывает все окна теории"""
        for window_key in list(self.theory_windows.keys()):
            window = self.theory_windows.get(window_key)
            if window:
                try:
                    window.close()
                except:
                    pass
        # Окна удалятся через destroyed сигнал
    
    def _on_window_destroyed(self, window_key):
        """Обработка закрытия окна"""
        try:
            if window_key in self.theory_windows:
                del self.theory_windows[window_key]
            
            if hasattr(self, 'theory_window_closed'):
                self.theory_window_closed.emit()
        except (RuntimeError, KeyError):
            pass
    
    def cleanup(self):
        """Очистка ресурсов перед удалением менеджера"""
        try:
            self.theory_window_created.disconnect()
            self.theory_window_closed.disconnect()
        except:
            pass
        
        self.close_all_windows()
        self.theory_windows.clear()