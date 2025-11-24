from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QComboBox, QPushButton, QLineEdit, QLabel, QSlider, QTextEdit,
    QFrame, QSizePolicy, QSpacerItem, QGraphicsView, QGraphicsScene,
    QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter
from controller.engine import Engine
from model.sorting.quicksort import QuickSort
from model.sorting.mergesort import MergeSort
from model.sorting.bubblesort import BubbleSort
from model.trees.bst import BST
from model.trees.avl import AVLTree
from model.trees.red_black_tree import RedBlackTree
from model.trees.splay_tree import SplayTree
from model.trees.treap import Treap
from model.trees.b_tree import BTree
from model.graphs.bfs import GraphBFS
from model.graphs.dfs import GraphDFS
from model.graphs.dijkstra import Dijkstra
from model.hashtable.hashtable import HashTable

from view.tree_visualizer import TreeVisualizer
from view.graph_visualizer import GraphVisualizer
from view.tree_layout import CenteredTreeLayout, CompactTreeLayout
from view.scene_items import ArrayCircleItem, ZoomableGraphicsView
from view.inspector import Inspector

import random
import json
import math


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
        self.algorithm_completed = False  # Флаг завершения алгоритма

        # Инициализация сцены и визуализаторов
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)
        self.tree_visualizer = TreeVisualizer(self.scene)
        self.graph_visualizer = GraphVisualizer(self.scene, self.view)
        self.inspector = Inspector()

        # Инициализация элементов интерфейса для графов
        self.graph_layout_label = None
        self.graph_layout_combo = None

        # Добавляем таймер для отложенного сброса зума
        self.zoom_reset_timer = QTimer()
        self.zoom_reset_timer.setSingleShot(True)
        self.zoom_reset_timer.timeout.connect(self._delayed_zoom_reset)

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
        # Инициализация выпадающего списка алгоритмов
        self._initialize_algorithm_combo()

        # Данные
        left_layout.addWidget(QLabel("Данные:"))
        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Введите данные через запятую: 5,2,8,1")

        # Для графов добавляем выбор компоновки
        self.graph_layout_label = QLabel("Компоновка графа:")
        self.graph_layout_combo = QComboBox()
        self.graph_layout_combo.addItems(["Авто", "Пружинная", "Круговая", "Древовидная", "ForceAtlas"])
        # Сначала скрываем, покажутся при выборе категории "Графы"
        self.graph_layout_label.hide()
        self.graph_layout_combo.hide()
        
        left_layout.addWidget(self.graph_layout_label)
        left_layout.addWidget(self.graph_layout_combo)

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
        
        # Включаем сглаживание для view
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

    def _initialize_algorithm_combo(self):
        """Инициализация выпадающего списка алгоритмов."""
        category = self.category_combo.currentText()
        self.algorithm_combo.clear()
        if category == "Сортировки":
            self.algorithm_combo.addItems(["QuickSort", "MergeSort", "BubbleSort"])
        elif category == "Деревья":
            self.algorithm_combo.addItems(["BST", "AVL", "RedBlackTree", "SplayTree", "Treap", "BTree"])
        elif category == "Графы":
            self.algorithm_combo.addItems(["BFS", "DFS", "Dijkstra"])
        elif category == "Хэш-таблицы":
            self.algorithm_combo.addItems(["HashTable"])

    def _update_speed(self, value):
        """Изменение скорости во время работы."""
        self.speed_label.setText(f"x{value}")
        # Передаем множитель скорости в engine
        self.engine.set_speed(value)
        self._log(f"⚡ Скорость изменена: x{value}")

    def _on_category_changed(self, category):
        """Обработка изменения категории алгоритма."""
        # Сначала обновляем список алгоритмов
        self._initialize_algorithm_combo()
        
        # Показываем/скрываем элементы для графов
        if self.graph_layout_label and self.graph_layout_combo:
            if category == "Графы":
                self.graph_layout_label.show()
                self.graph_layout_combo.show()
            else:
                self.graph_layout_label.hide()
                self.graph_layout_combo.hide()

    def _start_auto_mode(self):
        """Запуск автоматического режима."""
        # Если алгоритм завершен или не загружен, запускаем заново
        if self.algorithm_completed or not self.current_algorithm:
            if not self._start_algorithm():
                return

        speed_value = self.speed_slider.value()
        interval_ms = max(50, int(600 / speed_value))  # Адаптивный интервал
        
        self.engine.run(interval_ms)

        self.is_auto_mode = True
        self.auto_btn.hide()
        self.pause_btn.show()
        self.start_btn.setEnabled(False)  # Отключаем ручной режим в авторежиме
        self._log(f"▶ Автоматический режим запущен (скорость x{speed_value})")

    def _pause_auto_mode(self):
        """Пауза автоматического режима."""
        self.engine.pause()
        self.is_auto_mode = False
        self.pause_btn.hide()
        self.auto_btn.show()
        self.start_btn.setEnabled(True)  # Включаем ручной режим обратно
        self._log("⏸ Автоматический режим приостановлен")

    def _step_algorithm(self):
        """Шаг в ручном режиме."""
        # Если алгоритм завершен или не загружен, запускаем заново
        if self.algorithm_completed or not self.current_algorithm:
            if not self._start_algorithm():
                return
        
        # В ручном режиме принудительно запускаем шаг
        if not self.is_animating:
            success = self.engine.step()
            if not success:
                self._log("❌ Алгоритм завершен или произошла ошибка")
                self.algorithm_completed = True

    def _reset_algorithm(self):
        """Сброс текущего алгоритма и интерфейса."""
        try:
            # Останавливаем движок
            self.engine.pause()
            self.engine.generator = None
            
            # Очищаем визуализаторы
            if hasattr(self, 'graph_visualizer'):
                self.graph_visualizer.clear()
            
            # Очищаем сцену
            self.scene.clear()
            
            # Сбрасываем состояние
            self.current_algorithm = None
            self.is_auto_mode = False
            self.is_animating = False
            self.algorithm_completed = False
            self.pending_actions.clear()
            self.current_step = 0
            self.total_steps = 0

            # Обновляем UI
            self.auto_btn.show()
            self.pause_btn.hide()
            self.start_btn.setEnabled(True)
            
            # Восстанавливаем исходный массив
            text = self.data_input.text()
            try:
                arr = [int(x.strip()) for x in text.split(",") if x.strip()]
                self._render_array(arr)
            except ValueError:
                if hasattr(self, 'current_data'):
                    self._render_array(self.current_data)
            
            # Принудительное обновление
            self.scene.update()
            if hasattr(self, 'view'):
                self.view.update()
            
            self._log("♻ Алгоритм сброшен. Можно запустить заново.")
            
            # Запланировать сброс зума после сброса алгоритма
            self._schedule_zoom_reset()
            
        except Exception as e:
            print(f"Error resetting algorithm: {e}")
            import traceback
            traceback.print_exc()

    def _generate_random_data(self):
        """Генерация случайных данных с анимацией."""
        count = random.randint(6, 12)
        data = [random.randint(10, 99) for _ in range(count)]
        self.data_input.setText(",".join(map(str, data)))
        
        # Сохраняем текущие данные
        self.current_data = data.copy()
        self._render_array(data)
        
        # Автоматически сбрасываем алгоритм при генерации новых данных
        self._reset_algorithm()
        self._log(f"🎲 Сгенерированы {count} случайных чисел")
        
        # Запланировать сброс зума после генерации данных
        self._schedule_zoom_reset()

    def _schedule_zoom_reset(self):
        """Запланировать сброс зума с небольшой задержкой."""
        # Останавливаем предыдущий таймер если он активен
        if self.zoom_reset_timer.isActive():
            self.zoom_reset_timer.stop()
        
        # Запускаем с задержкой чтобы дать время на обновление сцены
        self.zoom_reset_timer.start(100)

    def _delayed_zoom_reset(self):
        """Отложенный сброс зума к содержимому."""
        try:
            if hasattr(self, 'view') and self.view:
                # Используем fit_to_content для масштабирования под содержимое
                if hasattr(self.view, 'fit_to_content'):
                    self.view.fit_to_content(200)  # 200px отступ
                else:
                    # Fallback для старого поведения
                    rect = self.scene.itemsBoundingRect()
                    if rect.isValid():
                        rect.adjust(-200, -200, 200, 200)
                        self.view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
                
                # Дополнительно центрируем вид
                if self.scene and self.scene.items():
                    rect = self.scene.itemsBoundingRect()
                    if rect.isValid():
                        self.view.centerOn(rect.center())
                        
                self._log("🔍 Масштаб сброшен к содержимому")
        except Exception as e:
            print(f"Error resetting zoom: {e}")

    def _start_algorithm(self):
        """Запуск выбранного алгоритма."""
        # Сначала сбрасываем предыдущий алгоритм
        self._reset_algorithm()
        
        text = self.data_input.text()
        try:
            arr = [int(x.strip()) for x in text.split(",") if x.strip()]
            if len(arr) < 1:
                QMessageBox.warning(self, "Ошибка", "Введите хотя бы 1 число")
                return False
            
            # Сохраняем текущие данные
            self.current_data = arr.copy()
            
            algo_name = self.algorithm_combo.currentText()
            
            # Создание алгоритма в зависимости от выбора
            algorithms = {
                "QuickSort": lambda: QuickSort(arr.copy()),
                "MergeSort": lambda: MergeSort(arr.copy()),
                "BubbleSort": lambda: BubbleSort(arr.copy()),
                "BST": lambda: BST(arr.copy()),
                "AVL": lambda: AVLTree(arr.copy()),
                "RedBlackTree": lambda: RedBlackTree(arr.copy()),
                "SplayTree": lambda: SplayTree(arr.copy()),
                "Treap": lambda: Treap(arr.copy()),
                "BTree": lambda: BTree(arr.copy()),
                # Для графов используем правильную направленность
                "BFS": lambda: GraphBFS(self._create_tree_graph(arr), arr[0] if arr else 0),
                "DFS": lambda: GraphDFS(self._create_tree_graph(arr), arr[0] if arr else 0),
                "Dijkstra": lambda: Dijkstra(self._create_tree_graph(arr, weight_mode='diff'), arr[0] if arr else 0),
                "HashTable": lambda: HashTable(arr.copy())
            }

            if algo_name in algorithms:
                try:
                    self.current_algorithm = algorithms[algo_name]()
                    self.engine.load_algorithm(self.current_algorithm)
                    
                    # Для графов используем специальный рендеринг
                    if algo_name in ["BFS", "DFS", "Dijkstra"]:
                        # Очищаем сцену и готовимся к построению графа
                        self.scene.clear()
                        
                        # Создаем граф с использованием значений массива
                        graph_data = self._create_tree_graph(arr)
                        
                        # Устанавливаем соответствие ID -> значение
                        self.graph_visualizer.node_values = {val: val for val in arr}
                        
                        # Устанавливаем выбранный алгоритм компоновки
                        if self.graph_layout_combo:
                            layout_name = self.graph_layout_combo.currentText()
                            layout_map = {
                                "Авто": "Auto",
                                "Пружинная": "Spring", 
                                "Круговая": "Circular",
                                "Древовидная": "Tree",
                                "ForceAtlas": "ForceAtlas"
                            }
                            
                            if layout_name in layout_map:
                                selected_layout = layout_map[layout_name]
                                success = self.graph_visualizer.set_layout_algorithm(selected_layout)
                                if success:
                                    if layout_name == "Авто":
                                        self._log("📐 Используется автоматический выбор компоновки")
                                    else:
                                        self._log(f"📐 Установлена компоновка: {layout_name}")
                        
                        self._log(f"🕸️ Подготовка графа для алгоритма {algo_name}...")
                        
                    else:
                        self._render_array(arr)
                        
                    self._log(f"🔧 Алгоритм '{algo_name}' загружен. Готов к выполнению.")
                    return True
                except Exception as e:
                    self._log(f"❌ Ошибка при создании алгоритма: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                self._log(f"❌ Алгоритм '{algo_name}' не найден")
                return False
                
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Вводите только числа через запятую")
            return False
    def _get_initial_tree_structure(self):
        """Получает начальную структуру дерева из алгоритма."""
        if hasattr(self.current_algorithm, '_get_tree_structure'):
            # Передаем только root, без self
            return self.current_algorithm._get_tree_structure(self.current_algorithm.root)
        return None

    def _create_tree_graph(self, arr, weight_mode="diff", min_weight=1, max_weight=10, directed=False):
        """
        Создает древовидный граф вместо полного графа.
        
        Параметры:
        - arr: список значений для узлов
        - weight_mode: "diff", "uniform", "random"
        - min_weight, max_weight: диапазон весов для random режима
        - directed: True для ориентированного графа, False для неориентированного
        """
        graph = {}
        if not arr:
            return graph

        # Уникальные узлы (сохраняем порядок входного списка)
        nodes = list(dict.fromkeys(arr))

        # Вспомог: генерация веса между двумя значениями
        def make_weight(a, b):
            if weight_mode == "diff":
                return max(min_weight, abs(int(a) - int(b)))
            elif weight_mode == "uniform":
                return max(1, int(min_weight))
            elif weight_mode == "random":
                return random.randint(min_weight, max_weight)
            else:
                # fallback
                return max(1, abs(int(a) - int(b)))

        # Инициализация пустых словарей
        for v in nodes:
            graph[v] = {}

        # Строим сбалансированное дерево из узлов
        if len(nodes) == 1:
            return graph

        # Создаем древовидную структуру
        root = nodes[0]
        remaining_nodes = nodes[1:]
        
        # Распределяем оставшиеся узлы как детей
        level_nodes = [root]
        
        while remaining_nodes:
            next_level = []
            for parent in level_nodes:
                if not remaining_nodes:
                    break
                    
                # Создаем 1-2 детей для каждого родителя
                num_children = min(2, len(remaining_nodes))
                for _ in range(num_children):
                    if not remaining_nodes:
                        break
                    child = remaining_nodes.pop(0)
                    
                    # Добавляем связь родитель-ребенок
                    w = make_weight(parent, child)
                    graph[parent][child] = w
                    
                    # Для неориентированного графа добавляем обратную связь
                    if not directed:
                        graph[child][parent] = w
                    
                    next_level.append(child)
            
            level_nodes = next_level

        # Небольшой лог
        try:
            edge_count = sum(len(neighbors) for neighbors in graph.values())
            if directed:
                self._log(f"🌳 Создан ориентированный граф: узлов={len(nodes)}, ребер={edge_count}")
            else:
                self._log(f"🌳 Создан неориентированный граф: узлов={len(nodes)}, ребер={edge_count}")
        except Exception:
            print(f"Generated tree graph: nodes={len(nodes)}")

        return graph

    def _create_sample_graph(self, arr,
                             graph_type="tree",  # По умолчанию используем древовидную структуру
                             directed=False,
                             weight_mode="diff",
                             density=0.5,
                             rows=None,
                             cols=None,
                             min_weight=1,
                             max_weight=10):
        """
        Генерация образцового графа.

        Параметры:
        - arr: список уникальных значений узлов
        - graph_type: "complete", "random", "chain", "star", "grid", "tree"
        - directed: True/False
        - weight_mode: "diff" (|a-b|, минимум 1), "random", "uniform"
        - density: для "random" - вероятность наличия ребра (0..1)
        - rows, cols: для "grid" можно указать размеры сетки; если не указаны, подбираются автоматически
        - min_weight, max_weight: для режима "random" диапазон весов

        Возвращает словарь вида:
        { node_value: { neighbor_value: weight, ... }, ... }
        (всегда словари соседей, удобно для Dijkstra)
        """
        graph = {}
        if not arr:
            return graph

        # Уникальные узлы (сохраняем порядок входного списка)
        nodes = list(dict.fromkeys(arr))

        # Вспомог: генерация веса между двумя значениями
        def make_weight(a, b):
            if weight_mode == "diff":
                return max(min_weight, abs(int(a) - int(b)))
            elif weight_mode == "uniform":
                return max(1, int(min_weight))
            elif weight_mode == "random":
                return random.randint(min_weight, max_weight)
            else:
                # fallback
                return max(1, abs(int(a) - int(b)))

        # Инициализация пустых словарей
        for v in nodes:
            graph[v] = {}

        if graph_type == "complete":
            for i, u in enumerate(nodes):
                for j, v in enumerate(nodes):
                    if i == j:
                        continue
                    w = make_weight(u, v)
                    graph[u][v] = w
                    if not directed:
                        graph[v][u] = w

        elif graph_type == "random":
            # Плотность: вероятность наличия ребра между парой узлов
            p = max(0.0, min(1.0, float(density)))
            for i, u in enumerate(nodes):
                for j, v in enumerate(nodes):
                    if i == j:
                        continue
                    if random.random() <= p:
                        w = make_weight(u, v)
                        graph[u][v] = w
                        if not directed:
                            graph[v][u] = w

        elif graph_type == "chain":
            # Связываем в последовательную цепочку: 0-1-2-...
            for i in range(len(nodes)-1):
                u = nodes[i]
                v = nodes[i+1]
                w = make_weight(u, v)
                graph[u][v] = w
                if not directed:
                    graph[v][u] = w

        elif graph_type == "star":
            # Первый узел центр
            center = nodes[0]
            for v in nodes[1:]:
                w = make_weight(center, v)
                graph[center][v] = w
                if not directed:
                    graph[v][center] = w

        elif graph_type == "grid":
            # Параметры rows x cols
            n = len(nodes)
            if rows is None or cols is None:
                # стараемся подобрать близкую к квадрату сетку
                cols = int(math.ceil(math.sqrt(n)))
                rows = int(math.ceil(n / cols))
            # размещаем ноды в сетку по порядку
            grid = []
            idx = 0
            for r in range(rows):
                row = []
                for c in range(cols):
                    if idx < n:
                        row.append(nodes[idx])
                        idx += 1
                    else:
                        row.append(None)
                grid.append(row)
            # соединяем соседей по 4-направлениям
            for r in range(rows):
                for c in range(cols):
                    u = grid[r][c]
                    if u is None:
                        continue
                    neighbors = []
                    for dr, dc in ((0,1),(1,0),(0,-1),(-1,0)):
                        rr = r + dr
                        cc = c + dc
                        if 0 <= rr < rows and 0 <= cc < cols:
                            v = grid[rr][cc]
                            if v is not None:
                                neighbors.append(v)
                    for v in neighbors:
                        w = make_weight(u, v)
                        graph[u][v] = w
                        if not directed:
                            graph[v][u] = w

        elif graph_type == "tree":
            # Генерация сбалансированного дерева
            if len(nodes) == 1:
                return graph

            root = nodes[0]
            remaining_nodes = nodes[1:]
            
            level_nodes = [root]
            
            while remaining_nodes:
                next_level = []
                for parent in level_nodes:
                    if not remaining_nodes:
                        break
                        
                    # Создаем 1-2 детей для каждого родителя
                    num_children = min(2, len(remaining_nodes))
                    for _ in range(num_children):
                        if not remaining_nodes:
                            break
                        child = remaining_nodes.pop(0)
                        
                        w = make_weight(parent, child)
                        graph[parent][child] = w
                        if not directed:
                            graph[child][parent] = w
                        
                        next_level.append(child)
                
                level_nodes = next_level

        else:
            # fallback to tree
            if len(nodes) == 1:
                return graph

            root = nodes[0]
            remaining_nodes = nodes[1:]
            
            level_nodes = [root]
            
            while remaining_nodes:
                next_level = []
                for parent in level_nodes:
                    if not remaining_nodes:
                        break
                        
                    num_children = min(2, len(remaining_nodes))
                    for _ in range(num_children):
                        if not remaining_nodes:
                            break
                        child = remaining_nodes.pop(0)
                        
                        w = make_weight(parent, child)
                        graph[parent][child] = w
                        if not directed:
                            graph[child][parent] = w
                        
                        next_level.append(child)
                
                level_nodes = next_level

        # Убедимся, что для неориентированного графа все связи симметричны
        if not directed:
            for u in list(graph.keys()):
                for v, w in list(graph[u].items()):
                    if v not in graph:
                        graph[v] = {}
                    if u not in graph[v]:
                        graph[v][u] = w

        # Небольшой лог (удобно при отладке)
        try:
            self._log(f"🧩 Generated graph: type={graph_type}, nodes={len(nodes)}, directed={directed}")
        except Exception:
            # если _log недоступен (редко), печатаем в stdout
            print(f"Generated graph: type={graph_type}, nodes={len(nodes)}, directed={directed}")

        return graph

    def _render_array(self, arr):
        """Рендеринг массива с анимированным появлением."""
        self.scene.clear()
        self.visual_items.clear()
        self.array_data = arr.copy()
        
        radius, spacing = 30, 15
        total_width = len(arr) * (radius * 2 + spacing)
        scene_width = max(800, total_width + 100)
        
        # Устанавливаем расширенную область сцены для прокрутки
        extended_scene_rect = QRectF(-2000, -2000, 4000, 4000)
        self.scene.setSceneRect(extended_scene_rect)
        
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
            QTimer.singleShot(400 + i * 80, lambda c=circle: setattr(c, "is_spawning", False))

    def _render_tree(self, tree_data):
        """Рендеринг дерева вместо массива."""
        try:
            # Очищаем сцену безопасно
            self.scene.clear()
            self.visual_items.clear()
            
            # Устанавливаем расширенную область сцены для прокрутки
            extended_scene_rect = QRectF(-3000, -3000, 6000, 6000)
            self.scene.setSceneRect(extended_scene_rect)
            
            # Если данных нет, показываем сообщение
            if not tree_data:
                text_item = self.scene.addText("Дерево пустое или строится...")
                text_item.setPos(0, 0)
                self._log("ℹ️ Дерево пустое - начните выполнение алгоритма")
                return
            
            # Создаем дерево с анимацией
            root = self.tree_visualizer.create_tree_from_structure(tree_data, animate=True)
            
            if root:
                # Центрируем view на дереве
                self._center_on_tree()
                self._log("🌳 Дерево построено и отображено")
            else:
                self._log("❌ Ошибка при построении дерева")
        except Exception as e:
            self._log(f"❌ Ошибка при визуализации дерева: {str(e)}")
            import traceback
            traceback.print_exc()
            # В случае ошибки отображаем массив
            if hasattr(self, 'current_data'):
                self._render_array(self.current_data)

    def _center_on_tree(self):
        """Центрирует вид на содержимом сцены с масштабированием."""
        if self.scene.items():
            # Используем fit_to_content для автоматического масштабирования
            if hasattr(self, 'view') and self.view:
                if hasattr(self.view, 'fit_to_content'):
                    self.view.fit_to_content(150)
                else:
                    rect = self.scene.itemsBoundingRect()
                    if rect.isValid():
                        rect.adjust(-150, -150, 150, 150)
                        self.view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
                self._log("🔍 Дерево отмасштабировано для обзора")

    def _center_and_scale_graph(self):
        """Центрирует и масштабирует граф для лучшего отображения."""
        if not self.nodes:
            return
            
        try:
            # Находим границы графа с учетом увеличенных расстояний
            all_positions = [node.pos() for node in self.nodes.values()]
            min_x = min(pos.x() for pos in all_positions)
            max_x = max(pos.x() for pos in all_positions)
            min_y = min(pos.y() for pos in all_positions)
            max_y = max(pos.y() for pos in all_positions)
            
            width = max_x - min_x
            height = max_y - min_y
            
            # Добавляем отступы для лучшего отображения
            padding = 150  # Увеличенный отступ
            scene_rect = QRectF(min_x - padding, min_y - padding, 
                               width + 2*padding, height + 2*padding)
            
            # Устанавливаем расширенную область сцены
            if hasattr(self.view, 'set_scene_rect_based_on_content'):
                self.view.set_scene_rect_based_on_content(scene_rect, padding)
            else:
                # Fallback
                extended_rect = QRectF(-2000, -2000, 4000, 4000)
                self.scene.setSceneRect(extended_rect)
            
            # Центрируем вид на графе с помощью fit_to_content
            if self.view:
                if hasattr(self.view, 'fit_to_content'):
                    self.view.fit_to_content(padding)
                else:
                    self.view.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)
                self._log("🔍 Граф отмасштабирован для лучшего обзора")
            
        except Exception as e:
            print(f"Error centering graph: {e}")

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
        self.start_btn.setEnabled(False)
        
        t = action.get("type")
        
        # Базовые длительности анимаций
        base_delay = 800
        speed_factor = max(0.3, 1.0 / self.speed_slider.value())
        
        if t == "tree":
            # Обработка действий с деревьями
            tree_data = action.get("tree_data")
            if tree_data:
                self._render_tree(tree_data)
            self._log(action.get("description", "Действие с деревом"))
            self._schedule_next_action(int(600 * speed_factor))
        
        elif t == "traversal":
            # Обход дерева
            node_sequence = action.get("nodes", [])
            self.tree_visualizer.highlight_traversal(node_sequence)
            self._log(f"🔄 Обход дерева: {action.get('description', '')}")
            self._schedule_next_action(int(len(node_sequence) * 500 * speed_factor))
        
        elif t == "graph_init":
            # Инициализация графа через GraphVisualizer
            success = self.graph_visualizer.process_action(action)
            if success:
                # Получаем дополнительную информацию о графе для инспектора
                graph_info = self.graph_visualizer.get_graph_info()
                action["graph_info"] = graph_info
                self._log(f"🕸️ Инициализирован граф для {action.get('algorithm', 'алгоритма')}")
            else:
                self._log("❌ Ошибка при создании графа")
            self._schedule_next_action(int(800 * speed_factor))
            
        elif t == "visit":
            node_index = action.get('node')
            # Для графов используем визуализатор графов
            if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                success = self.graph_visualizer.process_action(action)
                if success:
                    # Добавляем информацию о связях для инспектора
                    if node_index in self.graph_visualizer.adjacency_list:
                        action["connections"] = self.graph_visualizer.adjacency_list[node_index]
                    self._log(f"📍 Посещен узел: {node_index}")
            # Для массивов используем обычную подсветку
            elif node_index < len(self.visual_items):
                self.visual_items[node_index].highlight("#4ECDC4")
                self.visual_items[node_index].bounce_animation()
                self._log(f"📍 Посещен элемент: {node_index}")
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "discover":
            from_node = action.get('from_node')
            to_node = action.get('node')
            # Для графов используем визуализатор графов
            if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                success = self.graph_visualizer.process_action(action)
                if success:
                    # Добавляем информацию о весе ребра для инспектора
                    edge_key = self.graph_visualizer._get_edge_key(from_node, to_node)
                    edge_item = self.graph_visualizer.edges.get(edge_key)
                    if edge_item and hasattr(edge_item, 'weight'):
                        action["edge_weight"] = edge_item.weight
                    self._log(f"🔍 Обнаружен узел {to_node} из узла {from_node}")
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "update_distance":
            node_index = action.get('node')
            new_distance = action.get('new_distance')
            # Для графов используем визуализатор графов
            if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                success = self.graph_visualizer.process_action(action)
                if success:
                    self._log(f"📊 Обновлено расстояние до узла {node_index}: {new_distance}")
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "compare":
            i, j = action["indices"]
            self._highlight_items([i, j], "#FFD700", 
                                f"🔍 Сравнение: элемент[{i}] = {self.array_data[i]} vs элемент[{j}] = {self.array_data[j]}")
            self._schedule_next_action(int(base_delay * speed_factor))
            
        elif t == "swap":
            i, j = action["indices"]
            self._swap_items(i, j)
            self._log(f"🔄 Обмен элементов {i} и {j}")
            self._schedule_next_action(int(1000 * speed_factor))
            
        elif t == "insert":
            arr = action.get("array")
            if arr:
                self._render_array(arr)
            self._log("📥 Вставка элемента")
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "collision":
            for item in self.visual_items:
                item.highlight("#FFA500")
            self._log("⚡ Коллизия в хэш-таблице")
            self._schedule_next_action(int(800 * speed_factor))
            
        elif t == "complete":
            # Завершение алгоритма
            if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                # Для графов используем визуализатор графов
                success = self.graph_visualizer.process_action(action)
                if success:
                    self._log("✅ Алгоритм успешно завершён!")
            else:
                # Для массивов используем обычную анимацию
                self._animate_completion()
                self._log("✅ Алгоритм успешно завершён!")
            
            self.is_animating = False
            self.algorithm_completed = True
            # Автоматически выходим из авторежима при завершении
            if self.is_auto_mode:
                self._pause_auto_mode()

        # Обновление инспектора с расширенной информацией
        self.inspector.update_info(action)

    def _schedule_next_action(self, delay):
        """Запланировать следующее действие после задержки."""
        QTimer.singleShot(delay, self._on_animation_complete)

    def _on_animation_complete(self):
        """Завершение анимации и переход к следующему действию."""
        self.is_animating = False
        
        if self.pending_actions:
            next_action = self.pending_actions.pop(0)
            self._process_action(next_action)
        elif self.is_auto_mode and not self.algorithm_completed:
            # В автоматическом режиме продолжаем выполнение
            QTimer.singleShot(100, self.engine._on_tick)
        else:
            # В ручном режиме просто завершаем анимацию
            # Разблокируем кнопку ручного режима
            self.start_btn.setEnabled(True)

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