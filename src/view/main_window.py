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


class MainWindow(QMainWindow):
    """Главное окно визуализатора алгоритмов"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализатор алгоритмов")
        self.setGeometry(100, 100, 1300, 850)
        self.setStyleSheet("background-color: #f4f4f9;")

        # Контроллер
        self.engine = Engine()
        self.engine.step_ready.connect(self.on_step_ready)

        # Состояние
        self.current_algorithm = None
        self.visual_items = []
        self.array_data = []
        self.is_auto_mode = False  # флаг автоматического режима

        self.inspector = Inspector()
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        self._setup_ui()

    # ----------------------------------------------------
    # UI
    # ----------------------------------------------------
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Левая панель
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #ffffff; border-radius: 8px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Сортировки", "Деревья", "Графы", "Хэш-таблицы"])
        self.category_combo.currentTextChanged.connect(self._on_category_changed)

        self.algorithm_combo = QComboBox()
        self._on_category_changed(self.category_combo.currentText())

        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Введите данные через запятую: 5,2,8,1")

        self.generate_btn = QPushButton("🎲 Сгенерировать")
        self.start_btn = QPushButton("▶ Запуск (ручной)")
        self.auto_btn = QPushButton("⚙ Автоматически")
        self.pause_btn = QPushButton("⏸ Пауза")
        self.reset_btn = QPushButton("⟳ Сброс")

        # Изначально кнопка паузы скрыта
        self.pause_btn.hide()

        for btn in [self.generate_btn, self.start_btn, self.auto_btn, self.pause_btn, self.reset_btn]:
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

        # Настройка скорости
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Скорость:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        self.speed_slider.valueChanged.connect(self._update_speed)
        speed_layout.addWidget(self.speed_slider)
        

        # Добавляем элементы в левую панель
        left_layout.addWidget(QLabel("Категория:"))
        left_layout.addWidget(self.category_combo)
        left_layout.addWidget(QLabel("Алгоритм:"))
        left_layout.addWidget(self.algorithm_combo)
        left_layout.addWidget(QLabel("Данные:"))
        left_layout.addWidget(self.data_input)
        left_layout.addWidget(self.generate_btn)
        left_layout.addWidget(self.start_btn)
        left_layout.addWidget(self.auto_btn)
        left_layout.addWidget(self.pause_btn)
        left_layout.addWidget(self.reset_btn)
        left_layout.addLayout(speed_layout)
        left_layout.addWidget(self.inspector)
        left_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Правая панель
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: #ffffff; border-radius: 8px;")
        right_layout = QVBoxLayout(right_panel)

        self.view.setStyleSheet("background: #fafafa; border: 1px solid #ccc; border-radius: 6px;")
        self.view.setAlignment(Qt.AlignmentFlag.AlignBottom)
        right_layout.addWidget(QLabel("Визуализация:"))
        right_layout.addWidget(self.view, 4)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(180)
        self.log_text.setReadOnly(True)
        right_layout.addWidget(QLabel("Пошаговое объяснение:"))
        right_layout.addWidget(self.log_text, 1)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 950])
        main_layout.addWidget(splitter)

        # Сигналы
        self.generate_btn.clicked.connect(self._generate_random_data)
        self.start_btn.clicked.connect(self._step_algorithm)
        self.auto_btn.clicked.connect(self._start_auto_mode)
        self.pause_btn.clicked.connect(self._pause_auto_mode)
        self.reset_btn.clicked.connect(self._reset_algorithm)

        # Первичная генерация
        self._generate_random_data()

    # ----------------------------------------------------
    # Управление категориями и алгоритмами
    # ----------------------------------------------------
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

    # ----------------------------------------------------
    # Управление режимами
    # ----------------------------------------------------
    def _start_auto_mode(self):
        """Запуск автоматического режима"""
        if not self.current_algorithm:
            self._start_algorithm()

        speed_value = self.speed_slider.value()
        interval_ms = int(1000 / speed_value)
        self.engine.run(interval_ms)

        self.is_auto_mode = True
        self.auto_btn.hide()
        self.pause_btn.show()
        self._log(f"▶ Автоматический режим запущен (скорость x{speed_value})")

    def _pause_auto_mode(self):
        """Пауза автоматического режима"""
        self.engine.pause()
        self.is_auto_mode = False
        self.pause_btn.hide()
        self.auto_btn.show()
        self._log("⏸ Автоматический режим приостановлен")

    def _step_algorithm(self):
        """Шаг в ручном режиме"""
        if not self.current_algorithm:
            self._start_algorithm()
        self.engine.step()

    def _reset_algorithm(self):
        """Сброс текущего алгоритма и интерфейса"""
        self.engine.pause()
        self.engine.generator = None
        self.current_algorithm = None
        self.scene.clear()
        self.visual_items.clear()
        self.array_data.clear()
        self.is_auto_mode = False

        self.auto_btn.show()
        self.pause_btn.hide()
        self._log("♻ Алгоритм сброшен. Можно запустить заново.")


    # ----------------------------------------------------
    # Запуск алгоритма
    # ----------------------------------------------------
    def _generate_random_data(self):
        data = [random.randint(5, 50) for _ in range(10)]
        self.data_input.setText(",".join(map(str, data)))
        self._log("Сгенерированы новые данные")

    def _start_algorithm(self):
        text = self.data_input.text()
        try:
            arr = [int(x.strip()) for x in text.split(",") if x.strip()]
        except ValueError:
            self._log("Ошибка: вводите числа через запятую")
            return

        algo_name = self.algorithm_combo.currentText()
        if algo_name == "QuickSort":
            self.current_algorithm = QuickSort(arr.copy())
        elif algo_name == "MergeSort":
            self.current_algorithm = MergeSort(arr.copy())
        elif algo_name == "BubbleSort":
            self.current_algorithm = BubbleSort(arr.copy())
        elif algo_name == "BST":
            self.current_algorithm = BST(arr.copy())
        elif algo_name == "AVL":
            self.current_algorithm = AVLTree(arr.copy())
        elif algo_name == "BFS":
            graph = {i: [i + 1] for i in range(len(arr) - 1)}
            self.current_algorithm = GraphBFS(graph, 0)
        elif algo_name == "DFS":
            graph = {i: [i + 1] for i in range(len(arr) - 1)}
            self.current_algorithm = GraphDFS(graph, 0)
        elif algo_name == "Dijkstra":
            graph = {i: [i + 1] for i in range(len(arr) - 1)}
            self.current_algorithm = Dijkstra(graph, 0)
        elif algo_name == "HashTable":
            self.current_algorithm = HashTable(arr.copy())

        self.engine.load_algorithm(self.current_algorithm)
        self._render_array(arr)
        self._log(f"{algo_name} загружен.")

    # ----------------------------------------------------
    # Визуализация
    # ----------------------------------------------------
    def _render_array(self, arr):
        self.scene.clear()
        self.visual_items.clear()
        self.array_data = arr.copy()
        radius, spacing, y = 25, 20, 200

        for i, val in enumerate(arr):
            x = 60 + i * (radius * 2 + spacing)
            circle = ArrayCircleItem(x, y, val, i, radius)
            self.scene.addItem(circle)
            self.visual_items.append(circle)

    def _swap_items(self, i, j):
        if not (0 <= i < len(self.visual_items) and 0 <= j < len(self.visual_items)):
            return
        item_i, item_j = self.visual_items[i], self.visual_items[j]
        x_i, y_i = item_i.pos().x(), item_i.pos().y()
        x_j, y_j = item_j.pos().x(), item_j.pos().y()
        item_i.setPos(x_j, y_i)
        item_j.setPos(x_i, y_j)
        self.visual_items[i], self.visual_items[j] = self.visual_items[j], self.visual_items[i]

    def _highlight_items(self, indices, color):
        for i in range(len(self.visual_items)):
            if i in indices:
                self.visual_items[i].highlight(color)
            else:
                self.visual_items[i].reset_color()

    # ----------------------------------------------------
    # Обработка шагов
    # ----------------------------------------------------
    def on_step_ready(self, action):
        t = action.get("type")
        if t == "compare":
            i, j = action["indices"]
            self._highlight_items([i, j], "#FFD700")
            self._log(f"Сравнение: {i}, {j}")
        elif t == "swap":
            i, j = action["indices"]
            self._swap_items(i, j)
            self._highlight_items([i, j], "#E94B3C")
            self._log(f"Обмен элементов {i} и {j}")
        elif t == "insert":
            arr = action.get("array")
            if arr:
                self._render_array(arr)
            self._log("Вставка элемента")
        elif t == "collision":
            self._log("Коллизия в хэш-таблице")
        elif t == "visit":
            self._log(f"Посещен узел: {action.get('node')}")
        elif t == "complete":
            self._highlight_items(range(len(self.visual_items)), "#7EE081")
            self._log("✅ Алгоритм завершён!")

        self.inspector.update_info(str(action))

    def _update_speed(self, value):
        """Изменение скорости во время работы"""
        if self.is_auto_mode and self.engine.running:
            new_interval = int(1000 / value)
            self.engine.timer.start(new_interval)
            self._log(f"⚡ Скорость изменена: x{value}")


    def _log(self, msg):
        self.log_text.append(f"• {msg}")
