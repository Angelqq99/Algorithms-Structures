import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QSplitter, QListWidget, QPushButton,
                               QSlider, QLabel, QTextEdit, QLineEdit, QComboBox)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPalette,QPainter
import random

# ==================== МОДЕЛЬ (АЛГОРИТМЫ) ====================

class Algorithm:
    """Базовый класс для всех алгоритмов"""
    def __init__(self, data):
        self.data = data
        self.steps = []  # История шагов для возможности отката
        self.current_step = 0
        self.comparisons = 0
        self.swaps = 0
        
    def step(self):
        """Выполняет один шаг алгоритма. Возвращает состояние для визуализации"""
        raise NotImplementedError("Метод step должен быть реализован в дочернем классе")
    
    def reset(self):
        """Сброс алгоритма в начальное состояние"""
        self.current_step = 0
        self.comparisons = 0
        self.swaps = 0

class QuickSort(Algorithm):
    """Реализация быстрой сортировки с пошаговым выполнением"""
    def __init__(self, data):
        super().__init__(data)
        self.stack = [(0, len(data) - 1)]  # Стек для границ подмассивов
        self.pivot_index = None
        self.left_ptr = None
        self.right_ptr = None
        self.current_state = "init"
        
    def step(self):
        if self.current_state == "init" and self.stack:
            low, high = self.stack.pop()
            if low < high:
                self.pivot_index = self._partition(low, high)
                self.stack.append((low, self.pivot_index - 1))
                self.stack.append((self.pivot_index + 1, high))
                return {"action": "partition", "pivot": self.pivot_index, "low": low, "high": high}
        return {"action": "complete"}

class GraphBFS(Algorithm):
    """Реализация поиска в ширину (BFS) для графов"""
    def __init__(self, graph, start_node):
        super().__init__(graph)
        self.queue = [start_node]
        self.visited = set([start_node])
        self.current_node = None
        
    def step(self):
        if self.queue:
            self.current_node = self.queue.pop(0)
            # Логика обработки соседей...
            return {"action": "visit", "node": self.current_node}
        return {"action": "complete"}

# ==================== ВИЗУАЛИЗАЦИЯ ====================

class ArrayWidget(QWidget):
    """Виджет для визуализации массивов и сортировок"""
    def __init__(self):
        super().__init__()
        self.data = []
        self.highlighted_indices = set()
        self.setMinimumSize(600, 400)
        
    def set_data(self, data):
        self.data = data
        self.update()
        
    def highlight(self, indices):
        self.highlighted_indices = set(indices)
        self.update()
        
    def paintEvent(self, event):
        # Отрисовка массива в виде столбчатой диаграммы
        painter = QPainter(self)
        width = self.width() / len(self.data)
        
        for i, value in enumerate(self.data):
            color = QColor(100, 150, 250)  # Синий
            if i in self.highlighted_indices:
                color = QColor(255, 100, 100)  # Красный для подсветки
                
            painter.fillRect(i * width, self.height() - value * 10, 
                           width - 2, value * 10, color)

class GraphWidget(QWidget):
    """Виджет для визуализации графов"""
    def __init__(self):
        super().__init__()
        self.nodes = {}
        self.edges = []
        self.highlighted_nodes = set()
        
    def set_graph(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.update()

# ==================== ГЛАВНОЕ ОКНО ====================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализатор алгоритмов")
        self.setGeometry(100, 100, 1200, 800)
        
        # Текущий алгоритм и данные
        self.current_algorithm = None
        self.current_widget = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Создание интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Левая панель - управление
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Выбор категории алгоритмов
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Сортировки", "Графы", "Деревья", "Хэш-таблицы"])
        self.category_combo.currentTextChanged.connect(self._on_category_changed)
        
        # Выбор конкретного алгоритма
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["Быстрая сортировка", "Слиянием", "Пузырьковая"])
        
        # Поле ввода данных
        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Введите данные (через запятую): 5, 2, 8, 1, 9")
        
        # Кнопки управления
        self.generate_btn = QPushButton("Сгенерировать случайные данные")
        self.start_btn = QPushButton("Старт")
        self.pause_btn = QPushButton("Пауza")
        self.step_btn = QPushButton("Шаг вперед")
        self.reset_btn = QPushButton("Сброс")
        
        # Панель скорости
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Скорость:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        
        # Правая панель - визуализация и информация
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Область визуализации
        self.visualization_area = QWidget()
        self.visualization_area.setStyleSheet("background-color: white; border: 1px solid gray;")
        
        # Текстовый лог
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        
        # Сборка интерфейса
        left_layout.addWidget(QLabel("Категория:"))
        left_layout.addWidget(self.category_combo)
        left_layout.addWidget(QLabel("Алгоритм:"))
        left_layout.addWidget(self.algorithm_combo)
        left_layout.addWidget(QLabel("Данные:"))
        left_layout.addWidget(self.data_input)
        left_layout.addWidget(self.generate_btn)
        left_layout.addWidget(self.start_btn)
        left_layout.addWidget(self.pause_btn)
        left_layout.addWidget(self.step_btn)
        left_layout.addWidget(self.reset_btn)
        speed_layout.addWidget(self.speed_slider)
        left_layout.addLayout(speed_layout)
        
        right_layout.addWidget(self.visualization_area)
        right_layout.addWidget(QLabel("Пошаговое объяснение:"))
        right_layout.addWidget(self.log_text)
        
        # Разделитель
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 900])
        
        main_layout.addWidget(splitter)
        
        # Подключение сигналов
        self.generate_btn.clicked.connect(self._generate_random_data)
        self.start_btn.clicked.connect(self._start_algorithm)
        self.step_btn.clicked.connect(self._step_algorithm)
        self.reset_btn.clicked.connect(self._reset_algorithm)
        
    def _on_category_changed(self, category):
        """Обновляет список алгоритмов при смене категории"""
        self.algorithm_combo.clear()
        if category == "Сортировки":
            self.algorithm_combo.addItems(["Быстрая сортировка", "Сортировка слиянием", "Пузырьковая сортировка"])
        elif category == "Графы":
            self.algorithm_combo.addItems(["Поиск в ширину (BFS)", "Поиск в глубину (DFS)", "Алгоритм Дейкстры"])
            
    def _generate_random_data(self):
        """Генерация случайных данных"""
        data = [random.randint(1, 50) for _ in range(15)]
        self.data_input.setText(", ".join(map(str, data)))
        
    def _start_algorithm(self):
        """Запуск алгоритма"""
        data_text = self.data_input.text()
        try:
            data = [int(x.strip()) for x in data_text.split(",")]
            
            # Создаем соответствующий виджет визуализации
            if self.category_combo.currentText() == "Сортировки":
                self.current_widget = ArrayWidget()
                self.current_algorithm = QuickSort(data.copy())
                
            # Заменяем область визуализации
            old_widget = self.visualization_area
            self.visualization_area = self.current_widget
            self.visualization_area.setParent(None)
            self.centralWidget().layout().replaceWidget(old_widget, self.current_widget)
            old_widget.deleteLater()
            
            self.current_widget.set_data(data)
            self._log("Алгоритм запущен. Нажмите 'Шаг вперед' для начала.")
            
        except ValueError:
            self._log("Ошибка: введите числа, разделенные запятыми")
            
    def _step_algorithm(self):
        """Выполнение одного шага алгоритма"""
        if self.current_algorithm:
            result = self.current_algorithm.step()
            self._update_visualization(result)
            
    def _reset_algorithm(self):
        """Сброс алгоритма"""
        if self.current_algorithm:
            self.current_algorithm.reset()
            self._log("Алгоритм сброшен")
            
    def _update_visualization(self, result):
        """Обновление визуализации на основе результата шага"""
        if result["action"] == "partition":
            self.current_widget.highlight([result["pivot"], result["low"], result["high"]])
            self._log(f"Разделение: опорный элемент {self.current_algorithm.data[result['pivot']]}")
            
    def _log(self, message):
        """Добавление сообщения в лог"""
        self.log_text.append(f"• {message}")

# ==================== ЗАПУСК ПРИЛОЖЕНИЯ ====================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Настройка стиля приложения
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())