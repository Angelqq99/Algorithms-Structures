from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QComboBox, QPushButton, QLineEdit, QLabel, QSlider, QTextEdit,
    QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor, QPainter
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

from view.scene_items import ArrayBarItem
from view.inspector import Inspector

import random

# ---------------------------
# Виджеты для визуализации
# ---------------------------
class ArrayWidget(QWidget):
    """Визуализация массива с плавной анимацией подсветки"""
    def __init__(self):
        super().__init__()
        self.data = []
        self.highlighted_indices = set()
        self._highlight_colors = {}
        self.setMinimumSize(600, 400)

    def set_data(self, data):
        self.data = data
        self.update()

    def highlight(self, indices):
        # Плавно анимируем каждый новый индекс
        for idx in indices:
            self._animate_highlight(idx)
        self.highlighted_indices = set(indices)

    def _animate_highlight(self, idx):
        color_start = QColor("#5A9BD5")  # обычный
        color_end = QColor("#E94B3C")    # подсветка
        self._highlight_colors[idx] = color_start

        anim = QPropertyAnimation(self, b"dummy")
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.valueChanged.connect(lambda val, i=idx: self._update_color(i, val))
        anim.start()

    def _update_color(self, idx, value):
        # value: 0..1
        start = QColor("#5A9BD5")
        end = QColor("#E94B3C")
        r = start.red() + (end.red()-start.red())*value
        g = start.green() + (end.green()-start.green())*value
        b = start.blue() + (end.blue()-start.blue())*value
        self._highlight_colors[idx] = QColor(int(r), int(g), int(b))
        self.update()

    def swap_items(self, i, j):
        self.data[i], self.data[j] = self.data[j], self.data[i]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.data:
            return
        width = self.width() / len(self.data)
        for i, val in enumerate(self.data):
            color = self._highlight_colors.get(i, QColor("#5A9BD5"))
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

        # Панель инспектора
        self.inspector = Inspector()

        # Алгоритм и виджет
        self.current_algorithm = None
        self.current_widget = None

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
                background-color: #5A9BD5;
                color: white;
                border-radius: 6px;
                padding: 6px;
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
        left_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Правая панель
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.Shape.StyledPanel)
        right_panel.setStyleSheet("background-color: #ffffff; border-radius: 8px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10,10,10,10)
        right_layout.setSpacing(8)

        self.visualization_area = QWidget()
        self.visualization_area.setStyleSheet("background-color: #fdfdfd; border: 1px solid #ccc; border-radius: 6px;")
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(180)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc; border-radius: 6px;")

        right_layout.addWidget(self.visualization_area)
        right_layout.addWidget(QLabel("Пошаговое объяснение:"))
        right_layout.addWidget(self.log_text)

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
        left_panel.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 10px;
            padding: 10px;
            border: 1px solid #ddd;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
        """)

        right_panel.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 10px;
            padding: 10px;
            border: 1px solid #ddd;
            box-shadow: 2px 2px 15px rgba(0,0,0,0.2);
        """)

        self.visualization_area.setStyleSheet("""
            background-color: #fdfdfd;
            border-radius: 8px;
            border: 1px solid #ccc;
            box-shadow: inset 0px 0px 10px rgba(0,0,0,0.05);
        """)





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
        data = [random.randint(1, 50) for _ in range(15)]
        self.data_input.setText(",".join(map(str, data)))

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
            # Добавить MergeSort и BubbleSort аналогично
            self.current_widget = ArrayWidget()
            self.current_widget.set_data(data)

        elif category == "Деревья":
            if algo_name == "BST":
                self.current_algorithm = BST(data.copy())
            elif algo_name == "AVL":
                self.current_algorithm = AVLTree(data.copy())
            self.current_widget = TreeWidget()
            self.current_widget.set_tree(data)

        elif category == "Графы":
            # Простейший пример графа
            graph = {i: [i+1] for i in range(len(data)-1)}
            if algo_name == "BFS":
                self.current_algorithm = GraphBFS(graph, 0)
            # DFS и Dijkstra аналогично
            self.current_widget = GraphWidget()
            self.current_widget.set_graph(graph, [])

        elif category == "Хэш-таблицы":
            self.current_algorithm = HashTable(data.copy())
            self.current_widget = HashWidget(size=self.current_algorithm.size)
            self.current_widget.set_table([None]*self.current_algorithm.size)

        # Подмена области визуализации
        old_widget = self.visualization_area
        self.visualization_area = self.current_widget
        self.visualization_area.setParent(None)
        self.centralWidget().layout().replaceWidget(old_widget, self.current_widget)
        old_widget.deleteLater()

        # Загружаем алгоритм в Engine
        self.engine.load_algorithm(self.current_algorithm)
        self._log(f"{algo_name} запущен")

    def _step_algorithm(self):
        if self.current_algorithm:
            self.engine.step()

    def _reset_algorithm(self):
        if self.current_algorithm:
            self.current_algorithm.reset()
            self._log("Алгоритм сброшен")

    def on_step_ready(self, action):
        """Обработка шага алгоритма"""
        t = action.get("type")
        if t in ["compare", "swap", "insert", "collision"]:
            indices = action.get("indices")
            if indices:
                self.current_widget.highlight(indices)
            if t == "swap":
                i, j = indices
                self.current_widget.swap_items(i, j)
            if t == "insert" and "table" in action:
                self.current_widget.set_table(action["table"])
            self._log(str(action))
        elif t == "visit":
            self._log(f"Посещен узел: {action['node']}")
        elif t == "complete":
            self._log("Алгоритм завершен")

    def _log(self, message):
        self.log_text.append(f"• {message}")
