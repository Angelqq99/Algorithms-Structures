from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QComboBox, QPushButton, QLineEdit, QLabel, QSlider, QTextEdit,
    QFrame, QSizePolicy, QSpacerItem, QGraphicsView, QGraphicsScene
)
from PyQt6.QtCore import Qt
from controller.engine import Engine

from model.sorting.quicksort import QuickSort
from model.sorting.mergesort import MergeSort
from model.sorting.bubblesort import BubbleSort
from model.trees.bst import BST
from model.trees.avl import AVLTree
from model.graphs.bfs import GraphBFS
from model.graphs.dfs import GraphDFS
from model.graphs.dijkstra import Dijkstra
from model.hashtable.hashtable import HashTable

from view.scene_items import ArrayCircleItem
from view.inspector import Inspector

import random

# ---------------------------
# Виджеты для визуализации
# ---------------------------
class ArrayWidget(QWidget):
    """Для массивов (сортировки) - упрощенная версия"""
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

    def swap_items(self, i, j):
        self.data[i], self.data[j] = self.data[j], self.data[i]
        self.update()

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QColor
        painter = QPainter(self)
        if not self.data:
            return
        width = self.width() / len(self.data)
        for i, val in enumerate(self.data):
            color = QColor("#5A9BD5")
            if i in self.highlighted_indices:
                color = QColor("#E94B3C")
            painter.fillRect(i * width, self.height() - val * 10, width - 2, val * 10, color)

class GraphWidget(QWidget):
    """Для графов"""
    def __init__(self):
        super().__init__()
        self.nodes = {}
        self.edges = []
        self.highlighted_nodes = set()
        self.setStyleSheet("background-color: #fdfdfd; border: 1px solid #ccc; border-radius: 6px;")

    def set_graph(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.update()

    def highlight(self, nodes):
        self.highlighted_nodes = set(nodes)
        self.update()

class TreeWidget(QWidget):
    """Для деревьев"""
    def __init__(self):
        super().__init__()
        self.tree_data = []
        self.highlighted_nodes = set()
        self.setStyleSheet("background-color: #fdfdfd; border: 1px solid #ccc; border-radius: 6px;")

    def set_tree(self, tree_data):
        self.tree_data = tree_data
        self.update()

    def highlight(self, nodes):
        self.highlighted_nodes = set(nodes)
        self.update()

class HashWidget(QWidget):
    """Для хэш-таблиц"""
    def __init__(self, size=10):
        super().__init__()
        self.table = [None] * size
        self.highlighted_indices = set()
        self.setStyleSheet("background-color: #fdfdfd; border: 1px solid #ccc; border-radius: 6px;")

    def set_table(self, table):
        self.table = table
        self.update()

    def highlight(self, indices):
        self.highlighted_indices = set(indices)
        self.update()

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QColor
        painter = QPainter(self)
        width = self.width() / len(self.table)
        height = self.height() / 2
        for i, val in enumerate(self.table):
            color = QColor("#5A9BD5")
            if i in self.highlighted_indices:
                color = QColor("#E94B3C")
            painter.fillRect(i * width, height / 2, width - 2, height, color)
            if val is not None:
                painter.drawText(i * width + width / 4, height, str(val))

# ---------------------------
# Главное окно
# ---------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализатор алгоритмов")
        self.setGeometry(100, 100, 1300, 850)
        self.setStyleSheet("background-color: #f4f4f9;")

        # Контроллер
        self.engine = Engine()
        self.engine.step_ready.connect(self.on_step_ready)

        # Текущий алгоритм и данные
        self.current_algorithm = None
        self.current_widget = None
        self.array_data = []
        self.visual_items = []

        # Панель инспектора
        self.inspector = Inspector()

        # Графическая сцена (для сортировок)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        self._setup_ui()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5,5,5,5)
        main_layout.setSpacing(5)

        # Левая панель
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.Shape.StyledPanel)
        left_panel.setStyleSheet("background-color: #ffffff; border-radius: 8px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10,10,10,10)
        left_layout.setSpacing(8)

        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("padding: 4px; font-size: 14px;")
        self.category_combo.addItems(["Сортировки", "Деревья", "Графы", "Хэш-таблицы"])
        self.category_combo.currentTextChanged.connect(self._on_category_changed)

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setStyleSheet("padding: 4px; font-size: 14px;")
        self._on_category_changed(self.category_combo.currentText())

        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Введите данные через запятую: 5,2,8,1")
        self.data_input.setStyleSheet("padding: 4px; font-size: 14px;")

        self.generate_btn = QPushButton("Сгенерировать данные")
        self.start_btn = QPushButton("Старт")
        self.step_btn = QPushButton("Шаг")
        self.reset_btn = QPushButton("Сброс")
        
        for btn in [self.generate_btn, self.start_btn, self.step_btn, self.reset_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #5A9BD5;
                    color: white;
                    border-radius: 6px;
                    padding: 6px;
                }
                QPushButton:hover { background-color: #4B89C6; }
                QPushButton:pressed { background-color: #3A6FA3; }
            """)

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Скорость:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        speed_layout.addWidget(self.speed_slider)

        # Добавляем элементы на левую панель
        left_layout.addWidget(QLabel("Категория:"))
        left_layout.addWidget(self.category_combo)
        left_layout.addWidget(QLabel("Алгоритм:"))
        left_layout.addWidget(self.algorithm_combo)
        left_layout.addWidget(QLabel("Данные:"))
        left_layout.addWidget(self.data_input)
        left_layout.addWidget(self.generate_btn)
        left_layout.addWidget(self.start_btn)
        left_layout.addWidget(self.step_btn)
        left_layout.addWidget(self.reset_btn)
        left_layout.addLayout(speed_layout)
        left_layout.addWidget(self.inspector)
        left_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Правая панель
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.Shape.StyledPanel)
        right_panel.setStyleSheet("background-color: #ffffff; border-radius: 8px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10,10,10,10)
        right_layout.setSpacing(8)

        # Область визуализации
        self.visualization_widget = QWidget()
        self.visualization_layout = QVBoxLayout(self.visualization_widget)
        
        # По умолчанию используем графическую сцену для сортировок
        self.view.setStyleSheet("background: #fafafa; border: 1px solid #ccc; border-radius: 6px;")
        self.view.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.visualization_layout.addWidget(self.view)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(180)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc; border-radius: 6px;")

        right_layout.addWidget(QLabel("Визуализация:"))
        right_layout.addWidget(self.visualization_widget, 4)
        right_layout.addWidget(QLabel("Пошаговое объяснение:"))
        right_layout.addWidget(self.log_text, 1)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 950])
        main_layout.addWidget(splitter)

        # Сигналы
        self.generate_btn.clicked.connect(self._generate_random_data)
        self.start_btn.clicked.connect(self._start_algorithm)
        self.step_btn.clicked.connect(self._step_algorithm)
        self.reset_btn.clicked.connect(self._reset_algorithm)

        # Тестовые данные
        self._generate_random_data()

    # ---------------------------
    # Методы управления
    # ---------------------------
    def _on_category_changed(self, category):
        self.algorithm_combo.clear()
        if category == "Сортировки":
            self.algorithm_combo.addItems(["QuickSort", "MergeSort", "BubbleSort"])
        elif category == "Деревья":
            self.algorithm_combo.addItems(["BST", "AVL"])
        elif category == "Графы":
            self.algorithm_combo.addItems(["BFS", "DFS", "Dijkstra"])
        elif category == "Хэш-таблицы":
            self.algorithm_combo.addItems(["HashTable"])

    def _generate_random_data(self):
        category = self.category_combo.currentText()
        if category == "Сортировки":
            data = [random.randint(5, 50) for _ in range(10)]
        elif category == "Деревья":
            data = [random.randint(1, 100) for _ in range(8)]
        elif category == "Графы":
            data = [random.randint(1, 20) for _ in range(6)]
        elif category == "Хэш-таблицы":
            data = [random.randint(1, 50) for _ in range(5)]
        
        self.data_input.setText(",".join(map(str, data)))
        self._log("Сгенерированы новые данные")

    def _start_algorithm(self):
        data_text = self.data_input.text()
        try:
            data = [int(x.strip()) for x in data_text.split(",") if x.strip()]
        except ValueError:
            self._log("Ошибка: вводите только числа через запятую")
            return

        category = self.category_combo.currentText()
        algo_name = self.algorithm_combo.currentText()

        # Выбор алгоритма и виджета
        if category == "Сортировки":
            if algo_name == "QuickSort":
                self.current_algorithm = QuickSort(data.copy())
            elif algo_name == "MergeSort":
                self.current_algorithm = MergeSort(data.copy())
            elif algo_name == "BubbleSort":
                self.current_algorithm = BubbleSort(data.copy())
            
            # Используем графическую сцену для сортировок
            self._switch_visualization_widget(self.view)
            self._render_array(data)

        elif category == "Деревья":
            if algo_name == "BST":
                self.current_algorithm = BST(data.copy())
            elif algo_name == "AVL":
                self.current_algorithm = AVLTree(data.copy())
            
            tree_widget = TreeWidget()
            tree_widget.set_tree(data)
            self._switch_visualization_widget(tree_widget)

        elif category == "Графы":
            # Простейший пример графа
            graph = {i: [i+1] for i in range(len(data)-1)}
            if algo_name == "BFS":
                self.current_algorithm = GraphBFS(graph, 0)
            elif algo_name == "DFS":
                self.current_algorithm = GraphDFS(graph, 0)
            elif algo_name == "Dijkstra":
                self.current_algorithm = Dijkstra(graph, 0)
            
            graph_widget = GraphWidget()
            graph_widget.set_graph(graph, [])
            self._switch_visualization_widget(graph_widget)

        elif category == "Хэш-таблицы":
            self.current_algorithm = HashTable(data.copy())
            hash_widget = HashWidget(size=self.current_algorithm.size)
            hash_widget.set_table([None]*self.current_algorithm.size)
            self._switch_visualization_widget(hash_widget)

        # Загружаем алгоритм в Engine
        self.engine.load_algorithm(self.current_algorithm)
        self._log(f"{algo_name} запущен")

    def _switch_visualization_widget(self, new_widget):
        """Переключает виджет визуализации"""
        # Удаляем старый виджет
        old_widget = self.visualization_layout.takeAt(0)
        if old_widget and old_widget.widget():
            old_widget.widget().setParent(None)
        
        # Добавляем новый
        self.visualization_layout.addWidget(new_widget)
        self.current_widget = new_widget

    def _step_algorithm(self):
        if self.current_algorithm:
            self.engine.step()

    def _reset_algorithm(self):
        if self.current_algorithm:
            self.current_algorithm.reset()
            if hasattr(self, 'array_data') and self.array_data:
                self._render_array(self.array_data)
            self._log("Алгоритм сброшен")

    # ---------------------------
    # Методы для визуализации сортировок
    # ---------------------------
    def _render_array(self, arr):
        """Отрисовка массива в виде кружков с числами"""
        self.scene.clear()
        self.visual_items.clear()
        self.array_data = arr.copy()
        
        radius = 25
        spacing = 20
        total_width = len(arr) * (radius * 2 + spacing)
        start_x = 50  # начальная позиция
        y = 200  # позиция по вертикали

        for i, val in enumerate(arr):
            x = start_x + i * (radius * 2 + spacing)
            circle = ArrayCircleItem(x, y, val, i, radius)
            self.scene.addItem(circle)
            self.visual_items.append(circle)

    def _swap_items(self, i, j):
        """Анимация обмена кружков"""
        if not (0 <= i < len(self.visual_items) and 0 <= j < len(self.visual_items)):
            return

        item_i = self.visual_items[i]
        item_j = self.visual_items[j]
        x_i, y_i = item_i.pos().x(), item_i.pos().y()
        x_j, y_j = item_j.pos().x(), item_j.pos().y()

        # Мгновенная перестановка
        item_i.setPos(x_j, y_i)
        item_j.setPos(x_i, y_j)

        # Обновляем порядок
        self.visual_items[i], self.visual_items[j] = self.visual_items[j], self.visual_items[i]

    def _highlight_items(self, indices, color):
        """Подсветка элементов"""
        for i in range(len(self.visual_items)):
            if i in indices:
                self.visual_items[i].highlight(color)
            else:
                self.visual_items[i].reset_color()

    # ---------------------------
    # Обработка шагов алгоритма
    # ---------------------------
    def on_step_ready(self, action):
        """Обработка шага алгоритма"""
        t = action.get("type")
        
        if t in ["compare", "swap", "insert", "collision"]:
            indices = action.get("indices", [])
            
            if t == "compare":
                self._highlight_items(indices, "#FFD700")
                self._log(f"🔍 СРАВНЕНИЕ: элементы {indices}")
            elif t == "swap":
                i, j = indices
                self._swap_items(i, j)
                self._highlight_items([i, j], "#E94B3C")
                self._log(f"🔄 ОБМЕН: элементы {i} и {j} меняются местами")
            elif t == "insert":
                arr = action.get("array")
                if arr:
                    self._render_array(arr)
                self._log("Вставка элемента")
            elif t == "collision":
                self._log("Коллизия в хэш-таблице")
                
        elif t == "visit":
            node = action.get("node")
            if hasattr(self.current_widget, 'highlight'):
                self.current_widget.highlight([node])
            self._log(f"Посещен узел: {node}")
            
        elif t == "complete":
            if hasattr(self, 'visual_items') and self.visual_items:
                self._highlight_items(range(len(self.visual_items)), "#7EE081")
            self._log("✅ Алгоритм завершён!")

        # Обновляем инспектор
        self.inspector.update_info(str(action))

    def _log(self, message):
        """Добавление сообщения в лог"""
        self.log_text.append(f"• {message}")