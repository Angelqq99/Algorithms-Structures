from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QComboBox, QPushButton, QLineEdit, QLabel, QSlider, QTextEdit,
    QFrame, QSizePolicy, QSpacerItem, QGraphicsView, QGraphicsScene,
    QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor, QFont
from controller.engine import Engine
from PyQt6.QtGui import QPainter  # Добавьте этот импорт
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
import json


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
        self.is_auto_mode = False
        self.is_animating = False
        self.pending_actions = []
        self.total_steps = 0
        self.current_step = 0

        self.inspector = Inspector()
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        self._setup_ui()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Левая панель
        left_panel = self._create_left_panel()
        
        # Правая панель
        right_panel = self._create_right_panel()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 950])
        main_layout.addWidget(splitter)

        # Подключение сигналов
        self._connect_signals()

        # Первичная генерация
        self._generate_random_data()

    def _create_left_panel(self):
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff; 
                border-radius: 8px;
                border: 1px solid #d0d0d0;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(8)

        # Заголовок
        title = QLabel("Управление алгоритмами")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        left_layout.addWidget(title)

        # Категория и алгоритм
        left_layout.addWidget(QLabel("Категория:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Сортировки", "Деревья", "Графы", "Хэш-таблицы"])
        
        left_layout.addWidget(QLabel("Алгоритм:"))
        self.algorithm_combo = QComboBox()
        self._on_category_changed(self.category_combo.currentText())

        # Данные
        left_layout.addWidget(QLabel("Данные:"))
        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Введите данные через запятую: 5,2,8,1")

        # Кнопки управления
        self.generate_btn = QPushButton("🎲 Сгенерировать случайные данные")
        self.start_btn = QPushButton("▶ Запуск (ручной режим)")
        self.auto_btn = QPushButton("⚙ Автоматический режим")
        self.pause_btn = QPushButton("⏸ Пауза")
        self.reset_btn = QPushButton("⟳ Сброс алгоритма")

        self.pause_btn.hide()

        # Стилизация кнопок
        button_style = """
            QPushButton {
                background-color: #5A9BD5;
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { 
                background-color: #4B89C6; 
            }
            QPushButton:pressed { 
                background-color: #3A6FA3; 
            }
            QPushButton:disabled {
                background-color: #b0b0b0;
                color: #e0e0e0;
            }
        """
        for btn in [self.generate_btn, self.start_btn, self.auto_btn, self.pause_btn, self.reset_btn]:
            btn.setStyleSheet(button_style)

        # Настройка скорости
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Скорость:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        speed_layout.addWidget(self.speed_slider)
        self.speed_label = QLabel("x5")
        speed_layout.addWidget(self.speed_label)

        # Прогресс
        self.progress_label = QLabel("Прогресс: 0%")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        # Добавление элементов в левую панель
        left_layout.addWidget(self.category_combo)
        left_layout.addWidget(self.algorithm_combo)
        left_layout.addWidget(self.data_input)
        left_layout.addWidget(self.generate_btn)
        left_layout.addWidget(self.start_btn)
        left_layout.addWidget(self.auto_btn)
        left_layout.addWidget(self.pause_btn)
        left_layout.addWidget(self.reset_btn)
        left_layout.addLayout(speed_layout)
        left_layout.addWidget(self.progress_label)
        left_layout.addWidget(self.progress_bar)
        left_layout.addWidget(QLabel("Инспектор состояния:"))
        left_layout.addWidget(self.inspector)
        left_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        return left_panel

    def _create_right_panel(self):
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff; 
                border-radius: 8px;
                border: 1px solid #d0d0d0;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(8)

        # Визуализация
        viz_label = QLabel("Визуализация:")
        viz_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        right_layout.addWidget(viz_label)

        self.view.setStyleSheet("""
            QGraphicsView {
                background: #fafafa; 
                border: 2px solid #e0e0e0; 
                border-radius: 6px;
            }
        """)
        
        # ИСПРАВЛЕНИЕ: Включаем сглаживание для view
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.view, 4)

        # Лог
        log_label = QLabel("Пошаговое объяснение:")
        log_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        right_layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        right_layout.addWidget(self.log_text, 1)

        return right_panel

    def _connect_signals(self):
        """Подключение сигналов к слотам."""
        self.category_combo.currentTextChanged.connect(self._on_category_changed)
        self.speed_slider.valueChanged.connect(self._update_speed)
        self.generate_btn.clicked.connect(self._generate_random_data)
        self.start_btn.clicked.connect(self._step_algorithm)
        self.auto_btn.clicked.connect(self._start_auto_mode)
        self.pause_btn.clicked.connect(self._pause_auto_mode)
        self.reset_btn.clicked.connect(self._reset_algorithm)

    def _update_speed(self, value):
        """Изменение скорости во время работы."""
        self.speed_label.setText(f"x{value}")
        if self.is_auto_mode and hasattr(self.engine, 'running') and self.engine.running:
            new_interval = int(1000 / value)
            if hasattr(self.engine, 'timer'):
                self.engine.timer.setInterval(new_interval)
            self._log(f"⚡ Скорость изменена: x{value}")

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

    def _start_auto_mode(self):
        """Запуск автоматического режима."""
        if not self.current_algorithm:
            if not self._start_algorithm():
                return

        speed_value = self.speed_slider.value()
        interval_ms = int(1000 / speed_value)
        self.engine.run(interval_ms)

        self.is_auto_mode = True
        self.auto_btn.hide()
        self.pause_btn.show()
        self.progress_bar.setVisible(True)
        self._log(f"▶ Автоматический режим запущен (скорость x{speed_value})")

    def _pause_auto_mode(self):
        """Пауза автоматического режима."""
        self.engine.pause()
        self.is_auto_mode = False
        self.pause_btn.hide()
        self.auto_btn.show()
        self._log("⏸ Автоматический режим приостановлен")

    def _step_algorithm(self):
        """Шаг в ручном режиме."""
        if not self.current_algorithm:
            if not self._start_algorithm():
                return
        
        if not self.is_animating:
            self.engine.step()

    def _reset_algorithm(self):
        """Сброс текущего алгоритма и интерфейса."""
        self.engine.pause()
        self.engine.generator = None
        self.current_algorithm = None
        self.is_auto_mode = False
        self.is_animating = False
        self.pending_actions.clear()
        self.current_step = 0
        self.total_steps = 0

        self.auto_btn.show()
        self.pause_btn.hide()
        self.progress_bar.setVisible(False)
        self.progress_label.setText("Прогресс: 0%")
        
        # Восстанавливаем исходный массив
        if hasattr(self, 'original_data'):
            self._render_array(self.original_data)
        
        self._log("♻ Алгоритм сброшен. Можно запустить заново.")

    def _generate_random_data(self):
        """Генерация случайных данных с анимацией."""
        count = random.randint(6, 12)
        data = [random.randint(10, 99) for _ in range(count)]
        self.data_input.setText(",".join(map(str, data)))
        self.original_data = data.copy()
        self._render_array(data)
        self._log(f"🎲 Сгенерированы {count} случайных чисел")

    def _start_algorithm(self):
        """Запуск выбранного алгоритма."""
        text = self.data_input.text()
        try:
            arr = [int(x.strip()) for x in text.split(",") if x.strip()]
            if len(arr) < 2:
                QMessageBox.warning(self, "Ошибка", "Введите хотя бы 2 числа")
                return False
            if len(arr) > 20:
                QMessageBox.warning(self, "Предупреждение", 
                                  "Для лучшей визуализации рекомендуется не более 20 элементов")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Вводите только числа через запятую")
            return False

        algo_name = self.algorithm_combo.currentText()
        
        # Сохраняем оригинальные данные
        self.original_data = arr.copy()
        
        # Создание алгоритма в зависимости от выбора
        algorithms = {
            "QuickSort": lambda: QuickSort(arr.copy()),
            "MergeSort": lambda: MergeSort(arr.copy()),
            "BubbleSort": lambda: BubbleSort(arr.copy()),
            "BST": lambda: BST(arr.copy()),
            "AVL": lambda: AVLTree(arr.copy()),
            "BFS": lambda: GraphBFS(self._create_sample_graph(arr), 0),
            "DFS": lambda: GraphDFS(self._create_sample_graph(arr), 0),
            "Dijkstra": lambda: Dijkstra(self._create_sample_graph(arr), 0),
            "HashTable": lambda: HashTable(arr.copy())
        }

        if algo_name in algorithms:
            self.current_algorithm = algorithms[algo_name]()
            self.engine.load_algorithm(self.current_algorithm)
            self._render_array(arr)
            self._log(f"🔧 Алгоритм '{algo_name}' загружен. Готов к выполнению.")
            return True
        else:
            self._log(f"❌ Алгоритм '{algo_name}' не найден")
            return False

    def _create_sample_graph(self, arr):
        """Создание примерного графа для алгоритмов на графах."""
        graph = {}
        n = len(arr)
        for i in range(n):
            neighbors = []
            if i + 1 < n:
                neighbors.append(i + 1)
            if i * 2 < n:
                neighbors.append(i * 2)
            graph[i] = neighbors
        return graph

    def _render_array(self, arr):
        """Рендеринг массива с анимированным появлением."""
        self.scene.clear()
        self.visual_items.clear()
        self.array_data = arr.copy()
        
        radius, spacing = 30, 15
        total_width = len(arr) * (radius * 2 + spacing)
        scene_width = max(800, total_width + 100)
        self.scene.setSceneRect(0, 0, scene_width, 400)
        
        start_x = (scene_width - total_width) / 2
        start_y = 150

        for i, val in enumerate(arr):
            x = start_x + i * (radius * 2 + spacing)
            y = start_y
            
            circle = ArrayCircleItem(0, 0, val, i, radius)
            circle.setPos(x, y + 300)  # Начальная позиция (ниже)
            self.scene.addItem(circle)
            self.visual_items.append(circle)
            
            # Анимация появления (подъем снизу)
            circle.animate_move(x, y, 400 + i * 80)

    def _swap_items(self, i, j):
        """Анимированный обмен элементов."""
        if not (0 <= i < len(self.visual_items) and 0 <= j < len(self.visual_items)):
            return
            
        # Немедленно обновляем данные
        self.array_data[i], self.array_data[j] = self.array_data[j], self.array_data[i]
        self.visual_items[i], self.visual_items[j] = self.visual_items[j], self.visual_items[i]
        
        # Обновляем индексы
        self.visual_items[i].index = i
        self.visual_items[j].index = j
        
        # Подсветка
        self.visual_items[i].highlight("#FF6B6B")
        self.visual_items[j].highlight("#FF6B6B")
        
        # Получаем новые позиции
        radius, spacing = 30, 15
        total_width = len(self.visual_items) * (radius * 2 + spacing)
        scene_width = max(800, total_width + 100)
        start_x = (scene_width - total_width) / 2
        start_y = 150
        
        new_x_i = start_x + i * (radius * 2 + spacing)
        new_x_j = start_x + j * (radius * 2 + spacing)
        
        # Анимируем перемещение
        self.visual_items[i].animate_move(new_x_i, start_y, 600)
        self.visual_items[j].animate_move(new_x_j, start_y, 600)

    def _highlight_items(self, indices, color, description=""):
        """Анимированная подсветка элементов."""
        for i in range(len(self.visual_items)):
            if i in indices:
                self.visual_items[i].highlight(color)
                if len(indices) <= 3:  # Только для небольших наборов
                    self.visual_items[i].bounce_animation()
            else:
                self.visual_items[i].reset_color()
        
        if description:
            self._log(description)

    def on_step_ready(self, action):
        """Обработка шагов алгоритма с анимациями."""
        if self.is_animating:
            self.pending_actions.append(action)
            return
            
        self._process_action(action)

    def _process_action(self, action):
        """Обработка действия с анимацией."""
        self.is_animating = True
        self.current_step += 1
        
        t = action.get("type")
        
        if t == "compare":
            i, j = action["indices"]
            self._highlight_items([i, j], "#FFD700", 
                                f"🔍 Сравнение: элемент[{i}] = {self.array_data[i]} vs элемент[{j}] = {self.array_data[j]}")
            self._schedule_next_action(800)
            
        elif t == "swap":
            i, j = action["indices"]
            self._swap_items(i, j)
            self._log(f"🔄 Обмен элементов {i} и {j}")
            self._schedule_next_action(1000)
            
        elif t == "insert":
            arr = action.get("array")
            if arr:
                self._render_array(arr)
            self._log("📥 Вставка элемента")
            self._schedule_next_action(600)
            
        elif t == "collision":
            for item in self.visual_items:
                item.highlight("#FFA500")
            self._log("⚡ Коллизия в хэш-таблице")
            self._schedule_next_action(800)
            
        elif t == "visit":
            node_index = action.get('node')
            if node_index < len(self.visual_items):
                self.visual_items[node_index].highlight("#4ECDC4")
                self.visual_items[node_index].bounce_animation()
            self._log(f"📍 Посещен узел: {node_index}")
            self._schedule_next_action(600)
            
        elif t == "complete":
            self._animate_completion()
            self._log("✅ Алгоритм успешно завершён!")
            self.is_animating = False
            self.progress_bar.setValue(100)
            self.progress_label.setText("Прогресс: 100% (завершено)")

        # Обновление инспектора
        self.inspector.update_info(json.dumps(action, indent=2))
        
        # Обновление прогресса
        if hasattr(self.current_algorithm, 'get_progress'):
            progress = self.current_algorithm.get_progress()
            self.progress_bar.setValue(int(progress * 100))
            self.progress_label.setText(f"Прогресс: {int(progress * 100)}%")

    def _schedule_next_action(self, delay):
        """Запланировать следующее действие после задержки."""
        QTimer.singleShot(delay, self._on_animation_complete)

    def _on_animation_complete(self):
        """Завершение анимации и переход к следующему действию."""
        self.is_animating = False
        
        if self.pending_actions:
            next_action = self.pending_actions.pop(0)
            self._process_action(next_action)
        elif self.is_auto_mode:
            # В автоматическом режиме запрашиваем следующий шаг
            QTimer.singleShot(100, self.engine.step)

    def _animate_completion(self):
        """Анимация завершения алгоритма - последовательная подсветка."""
        def highlight_next(index=0):
            if index < len(self.visual_items):
                self.visual_items[index].highlight("#7EE081")
                self.visual_items[index].bounce_animation()
                QTimer.singleShot(150, lambda: highlight_next(index + 1))
            else:
                self.is_animating = False
        
        highlight_next()

    def _log(self, msg):
        """Добавление сообщения в лог."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {msg}")
        # Автопрокрутка к последнему сообщению
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event):
        """Обработка закрытия приложения."""
        self.engine.pause()
        event.accept()


# Необходимый импорт для QPainter
from PyQt6.QtGui import QPainter