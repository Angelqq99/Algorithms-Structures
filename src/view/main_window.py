import faulthandler
faulthandler.enable()
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QComboBox, QPushButton, QLineEdit, QLabel, QSlider, QTextEdit,
    QFrame, QSizePolicy, QSpacerItem, QGraphicsView, QGraphicsScene,
    QProgressBar, QMessageBox, QCheckBox, QGraphicsLineItem, QGraphicsTextItem, QGraphicsRectItem,
    QGridLayout, QGroupBox,QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush
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
from datetime import datetime


class TempArraysWidget(QFrame):
    """Виджет для отображения временных массивов MergeSort."""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(220)
        self.setMaximumHeight(350)
        
        # Состояние
        self.left_array = []
        self.right_array = []
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(8)
        
        # Заголовок
        title = QLabel("📊 ВРЕМЕННЫЕ МАССИВЫ MERGESORT")
        title.setStyleSheet("""
            font-weight: bold; 
            color: #2c3e50; 
            font-size: 14px;
            qproperty-alignment: AlignCenter;
        """)
        self.layout.addWidget(title)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #e0e0e0; margin: 5px 0;")
        separator.setFixedHeight(1)
        self.layout.addWidget(separator)
        
        # Основной контейнер для массивов
        arrays_container = QWidget()
        arrays_layout = QHBoxLayout(arrays_container)
        arrays_layout.setSpacing(30)
        arrays_layout.setContentsMargins(5, 5, 5, 5)
        
        # === ЛЕВЫЙ МАССИВ ===
        left_widget = QWidget()
        left_widget.setFixedWidth(250)  # Фиксированная ширина
        
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        # Заголовок левого массива
        left_title = QLabel("ЛЕВЫЙ МАССИВ (L)")
        left_title.setStyleSheet("""
            font-weight: bold; 
            color: #4ECDC4; 
            font-size: 13px;
            qproperty-alignment: AlignCenter;
            padding-bottom: 5px;
        """)
        left_layout.addWidget(left_title)
        
        # Контейнер для элементов левого массива
        self.left_scroll_area = QScrollArea()
        self.left_scroll_area.setWidgetResizable(True)
        self.left_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.left_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.left_scroll_area.setFixedHeight(120)
        self.left_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        
        self.left_elements_widget = QWidget()
        self.left_elements_layout = QHBoxLayout(self.left_elements_widget)
        self.left_elements_layout.setSpacing(10)
        self.left_elements_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.left_elements_layout.setContentsMargins(10, 10, 10, 10)
        
        self.left_scroll_area.setWidget(self.left_elements_widget)
        left_layout.addWidget(self.left_scroll_area)
        
        # Счетчик элементов слева
        self.left_count_label = QLabel("Элементов: 0")
        self.left_count_label.setStyleSheet("""
            color: #4ECDC4; 
            font-size: 11px;
            qproperty-alignment: AlignCenter;
        """)
        left_layout.addWidget(self.left_count_label)
        
        arrays_layout.addWidget(left_widget)
        
        # === РАЗДЕЛИТЕЛЬ ===
        vertical_separator = QFrame()
        vertical_separator.setFrameShape(QFrame.Shape.VLine)
        vertical_separator.setStyleSheet("background-color: #e0e0e0;")
        vertical_separator.setFixedWidth(1)
        arrays_layout.addWidget(vertical_separator)
        
        # === ПРАВЫЙ МАССИВ ===
        right_widget = QWidget()
        right_widget.setFixedWidth(250)  # Фиксированная ширина
        
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        # Заголовок правого массива
        right_title = QLabel("ПРАВЫЙ МАССИВ (R)")
        right_title.setStyleSheet("""
            font-weight: bold; 
            color: #FF6B6B; 
            font-size: 13px;
            qproperty-alignment: AlignCenter;
            padding-bottom: 5px;
        """)
        right_layout.addWidget(right_title)
        
        # Контейнер для элементов правого массива
        self.right_scroll_area = QScrollArea()
        self.right_scroll_area.setWidgetResizable(True)
        self.right_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.right_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.right_scroll_area.setFixedHeight(120)
        self.right_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        
        self.right_elements_widget = QWidget()
        self.right_elements_layout = QHBoxLayout(self.right_elements_widget)
        self.right_elements_layout.setSpacing(10)
        self.right_elements_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.right_elements_layout.setContentsMargins(10, 10, 10, 10)
        
        self.right_scroll_area.setWidget(self.right_elements_widget)
        right_layout.addWidget(self.right_scroll_area)
        
        # Счетчик элементов справа
        self.right_count_label = QLabel("Элементов: 0")
        self.right_count_label.setStyleSheet("""
            color: #FF6B6B; 
            font-size: 11px;
            qproperty-alignment: AlignCenter;
        """)
        right_layout.addWidget(self.right_count_label)
        
        arrays_layout.addWidget(right_widget)
        
        self.layout.addWidget(arrays_container)
        
        # === ИНФОРМАЦИОННАЯ ПАНЕЛЬ ===
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 10, 0, 0)
        info_layout.setSpacing(3)
        
        # Основная информация
        self.info_label = QLabel("Ожидание слияния...")
        self.info_label.setStyleSheet("""
            color: #2c3e50; 
            font-size: 12px;
            font-weight: bold;
            qproperty-alignment: AlignCenter;
        """)
        info_layout.addWidget(self.info_label)
        
        # Дополнительная информация
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("""
            color: #666; 
            font-size: 10px;
            qproperty-alignment: AlignCenter;
        """)
        info_layout.addWidget(self.detail_label)
        
        self.layout.addWidget(info_container)
        
        # Инициализируем пустое состояние
        self._clear_arrays()
    
    def update_arrays(self, left_array, right_array):
        """Обновляет отображение временных массивов."""
        # Сохраняем массивы
        self.left_array = left_array if left_array is not None else []
        self.right_array = right_array if right_array is not None else []
        
        # Очищаем контейнеры
        self._clear_layout(self.left_elements_layout)
        self._clear_layout(self.right_elements_layout)
        
        # Обновляем счетчики
        self.left_count_label.setText(f"Элементов: {len(self.left_array)}")
        self.right_count_label.setText(f"Элементов: {len(self.right_array)}")
        
        # Отображаем левый массив
        if self.left_array and len(self.left_array) > 0:
            for i, value in enumerate(self.left_array):
                element_widget = self._create_element_widget(value, "#4ECDC4", i)
                self.left_elements_layout.addWidget(element_widget)
        else:
            empty_label = QLabel("(нет элементов)")
            empty_label.setStyleSheet("color: #aaa; font-style: italic; font-size: 12px;")
            empty_label.setFixedHeight(80)
            self.left_elements_layout.addWidget(empty_label)
        
        # Отображаем правый массив
        if self.right_array and len(self.right_array) > 0:
            for i, value in enumerate(self.right_array):
                element_widget = self._create_element_widget(value, "#FF6B6B", i)
                self.right_elements_layout.addWidget(element_widget)
        else:
            empty_label = QLabel("(нет элементов)")
            empty_label.setStyleSheet("color: #aaa; font-style: italic; font-size: 12px;")
            empty_label.setFixedHeight(80)
            self.right_elements_layout.addWidget(empty_label)
        
        # Обновляем информационные метки
        self._update_info_labels()
        
        # Принудительное обновление layout
        self.left_elements_widget.adjustSize()
        self.right_elements_widget.adjustSize()
        
        # Прокрутка к началу
        self.left_scroll_area.horizontalScrollBar().setValue(0)
        self.right_scroll_area.horizontalScrollBar().setValue(0)
    
    def _create_element_widget(self, value, color, index):
        """Создает виджет для отображения элемента массива."""
        container = QWidget()
        container.setFixedSize(60, 80)  # Фиксированный размер для всех элементов
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        # Индекс элемента (маленький текст сверху)
        index_label = QLabel(f"[{index}]")
        index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        index_label.setFixedHeight(15)
        index_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 9px;
                font-weight: normal;
                background: transparent;
                border: none;
                margin: 0;
                padding: 0;
            }}
        """)
        layout.addWidget(index_label)
        
        # Круг с значением
        circle_label = QLabel(str(value))
        circle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        circle_label.setFixedSize(45, 45)
        circle_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-weight: bold;
                font-size: 14px;
                background-color: {color};
                border-radius: 22px;
                border: 2px solid {self._darken_color(color)};
                qproperty-alignment: AlignCenter;
                margin: 0;
                padding: 0;
            }}
        """)
        layout.addWidget(circle_label, 0, Qt.AlignmentFlag.AlignHCenter)
        
        # Значение под кругом (дублируем для ясности)
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFixedHeight(15)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 11px;
                font-weight: bold;
                background: transparent;
                border: none;
                margin: 0;
                padding: 0;
            }}
        """)
        layout.addWidget(value_label)
        
        return container
    
    def _darken_color(self, color_hex):
        """Затемняет цвет для границы."""
        if color_hex == "#4ECDC4":
            return "#2E8B57"
        elif color_hex == "#FF6B6B":
            return "#C0392B"
        else:
            return "#333333"
    
    def _update_info_labels(self):
        """Обновляет информационные метки."""
        left_count = len(self.left_array)
        right_count = len(self.right_array)
        total = left_count + right_count
        
        if total == 0:
            self.info_label.setText("Ожидание слияния...")
            self.detail_label.setText("")
        else:
            self.info_label.setText(f"Слияние {left_count} + {right_count} элементов")
            if left_count > 0 and right_count > 0:
                self.detail_label.setText(f"Сравниваются элементы из обоих массивов")
            elif left_count > 0:
                self.detail_label.setText(f"Используются только элементы левого массива")
            else:
                self.detail_label.setText(f"Используются только элементы правого массива")
    
    def _clear_layout(self, layout):
        """Очищает layout от всех виджетов."""
        if layout:
            # Удаляем все виджеты в обратном порядке
            for i in reversed(range(layout.count())):
                item = layout.takeAt(i)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    # Если это не виджет, а другой layout
                    if item.layout():
                        self._clear_layout(item.layout())
    
    def _clear_arrays(self):
        """Очищает массивы и отображение."""
        self.left_array = []
        self.right_array = []
        
        self._clear_layout(self.left_elements_layout)
        self._clear_layout(self.right_elements_layout)
        
        # Добавляем заглушки
        left_empty = QLabel("(нет элементов)")
        left_empty.setStyleSheet("color: #ccc; font-style: italic; font-size: 12px;")
        left_empty.setFixedHeight(80)
        self.left_elements_layout.addWidget(left_empty)
        
        right_empty = QLabel("(нет элементов)")
        right_empty.setStyleSheet("color: #ccc; font-style: italic; font-size: 12px;")
        right_empty.setFixedHeight(80)
        self.right_elements_layout.addWidget(right_empty)
        
        # Обновляем метки
        self.left_count_label.setText("Элементов: 0")
        self.right_count_label.setText("Элементов: 0")
        self._update_info_labels()
    
    def clear(self):
        """Очищает виджет."""
        self._clear_arrays()

class MainWindow(QMainWindow):
    """Главное окно визуализатора алгоритмов"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализатор алгоритмов")
        self.setGeometry(100, 100, 1400, 850)
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
        self.algorithm_completed = False
        
        # Для отложенной отрисовки деревьев
        self._pending_tree_data = []
        self._last_tree_data = None
        
        # Временные элементы для визуализации
        self._temp_array_items = []
        self._split_lines = []

        # Инициализация сцены и визуализаторов
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)
        self.tree_visualizer = TreeVisualizer(self.scene)
        self._is_rendering_tree = False
        self.graph_visualizer = GraphVisualizer(self.scene, self.view)
        self.inspector = Inspector()
        
        # Виджет временных массивов
        self.temp_arrays_widget = TempArraysWidget()

        # Направленность графа по умолчанию
        self.graph_directed = False

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
        splitter.setSizes([400, 1000])
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
        self._initialize_algorithm_combo()

        # Данные
        left_layout.addWidget(QLabel("Данные:"))
        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Введите данные через запятую: 5,2,8,1")

        # Для графов добавляем выбор компоновки и направленности
        self.graph_settings_label = QLabel("Настройки графа:")
        self.graph_settings_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        
        self.directed_label = QLabel("Направленность:")
        self.directed_checkbox = QCheckBox("Ориентированный граф")
        self.directed_checkbox.setChecked(self.graph_directed)
        self.directed_checkbox.stateChanged.connect(self._on_directed_changed)
        
        self.graph_layout_label = QLabel("Компоновка графа:")
        self.graph_layout_combo = QComboBox()
        self.graph_layout_combo.addItems(["Пружинная", "Круговая", "Древовидная"])
        
        self.graph_settings_label.hide()
        self.directed_label.hide()
        self.directed_checkbox.hide()
        self.graph_layout_label.hide()
        self.graph_layout_combo.hide()
        
        # Кнопки управления
        self.generate_btn = QPushButton("🎲 Сгенерировать случайные данные")
        self.start_btn = QPushButton("▶ Запуск (ручной режим)")
        self.auto_btn = QPushButton("⚙ Автоматический режим")
        self.pause_btn = QPushButton("⏸ Пауза")
        self.reset_btn = QPushButton("⟳ Сброс алгоритма")

        self.pause_btn.hide()

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
        
        left_layout.addWidget(self.graph_settings_label)
        left_layout.addWidget(self.directed_label)
        left_layout.addWidget(self.directed_checkbox)
        left_layout.addWidget(self.graph_layout_label)
        left_layout.addWidget(self.graph_layout_combo)
        
        left_layout.addWidget(self.generate_btn)
        left_layout.addWidget(self.start_btn)
        left_layout.addWidget(self.auto_btn)
        left_layout.addWidget(self.pause_btn)
        left_layout.addWidget(self.reset_btn)
        left_layout.addLayout(speed_layout)
        
        # Виджет временных массивов MergeSort
        left_layout.addWidget(self.temp_arrays_widget)
        self.temp_arrays_widget.hide()
        
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
        
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.view, 4)

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

    def _on_directed_changed(self, state):
        """Обработка изменения направленности графа."""
        self.graph_directed = (state == Qt.CheckState.Checked.value)
        self.graph_visualizer.set_directed(self.graph_directed)
        
        direction_text = "ориентированный" if self.graph_directed else "неориентированный"
        self._log(f"📊 Граф изменен на {direction_text}")
        
        if self.current_algorithm and self.algorithm_combo.currentText() in ["BFS", "DFS", "Dijkstra"]:
            self._reset_algorithm()
            self._log("♻ Настройки графа изменены. Алгоритм сброшен.")

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
        self.engine.set_speed(value)
        self._log(f"⚡ Скорость изменена: x{value}")

    def _on_category_changed(self, category):
        """Обработка изменения категории алгоритма."""
        self._initialize_algorithm_combo()
        
        if self.graph_settings_label:
            if category == "Графы":
                self.graph_settings_label.show()
                self.directed_label.show()
                self.directed_checkbox.show()
                self.graph_layout_label.show()
                self.graph_layout_combo.show()
            else:
                self.graph_settings_label.hide()
                self.directed_label.hide()
                self.directed_checkbox.hide()
                self.graph_layout_label.hide()
                self.graph_layout_combo.hide()

    def _start_auto_mode(self):
        """Запуск автоматического режима."""
        if self.algorithm_completed or not self.current_algorithm:
            if not self._start_algorithm():
                return

        speed_value = self.speed_slider.value()
        interval_ms = max(50, int(600 / speed_value))
        
        self.engine.run(interval_ms)

        self.is_auto_mode = True
        self.auto_btn.hide()
        self.pause_btn.show()
        self.start_btn.setEnabled(False)
        self._log(f"▶ Автоматический режим запущен (скорость x{speed_value})")

    def _pause_auto_mode(self):
        """Пауза автоматического режима."""
        self.engine.pause()
        self.is_auto_mode = False
        self.pause_btn.hide()
        self.auto_btn.show()
        self.start_btn.setEnabled(True)
        self._log("⏸ Автоматический режим приостановлен")

    def _step_algorithm(self):
        """Шаг в ручном режиме."""
        if self.algorithm_completed or not self.current_algorithm:
            if not self._start_algorithm():
                return
        
        if not self.is_animating:
            success = self.engine.step()
            if not success:
                self._log("❌ Алгоритм завершен или произошла ошибка")
                self.algorithm_completed = True

    def _reset_algorithm(self):
        """Сброс текущего алгоритма и интерфейса."""
        try:
            self.engine.pause()
            self.engine.generator = None
            
            if hasattr(self, 'graph_visualizer'):
                self.graph_visualizer.clear()
            
            self.scene.clear()
            
            self.current_algorithm = None
            self.is_auto_mode = False
            self.is_animating = False
            self.algorithm_completed = False
            self.pending_actions.clear()
            self.current_step = 0
            self.total_steps = 0
            
            self._pending_tree_data = []
            self._last_tree_data = None
            self._temp_array_items = []
            self._split_lines = []
            
            # Скрываем виджет временных массивов
            self.temp_arrays_widget.hide()
            self.temp_arrays_widget.clear()

            self.auto_btn.show()
            self.pause_btn.hide()
            self.start_btn.setEnabled(True)
            
            text = self.data_input.text()
            try:
                arr = [int(x.strip()) for x in text.split(",") if x.strip()]
                self._render_array(arr)
            except ValueError:
                if hasattr(self, 'current_data'):
                    self._render_array(self.current_data)
            
            self.scene.update()
            if hasattr(self, 'view'):
                self.view.update()
            
            self._log("♻ Алгоритм сброшен. Можно запустить заново.")
            
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
        
        self.current_data = data.copy()
        self._render_array(data)
        
        self._reset_algorithm()
        self._log(f"🎲 Сгенерированы {count} случайных чисел")
        
        self._schedule_zoom_reset()

    def _schedule_zoom_reset(self):
        """Запланировать сброс зума с небольшой задержкой."""
        if self.zoom_reset_timer.isActive():
            self.zoom_reset_timer.stop()
        
        self.zoom_reset_timer.start(100)

    def _delayed_zoom_reset(self):
        """Отложенный сброс зума к содержимому."""
        try:
            if hasattr(self, 'view') and self.view:
                if hasattr(self.view, 'fit_to_content'):
                    self.view.fit_to_content(200)
                else:
                    rect = self.scene.itemsBoundingRect()
                    if rect.isValid():
                        rect.adjust(-200, -200, 200, 200)
                        self.view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
                
                if self.scene and self.scene.items():
                    rect = self.scene.itemsBoundingRect()
                    if rect.isValid():
                        self.view.centerOn(rect.center())
                        
                self._log("🔍 Масштаб сброшен к содержимому")
        except Exception as e:
            print(f"Error resetting zoom: {e}")

    def _start_algorithm(self):
        """Запуск выбранного алгоритма."""
        self._reset_algorithm()
        
        text = self.data_input.text()
        try:
            arr = [int(x.strip()) for x in text.split(",") if x.strip()]
            if len(arr) < 1:
                QMessageBox.warning(self, "Ошибка", "Введите хотя бы 1 число")
                return False
            
            self.current_data = arr.copy()
            
            algo_name = self.algorithm_combo.currentText()
            
            if algo_name in ["BFS", "DFS", "Dijkstra"]:
                graph_data = self._create_tree_graph(arr, directed=self.graph_directed)
            else:
                graph_data = None
            
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
                "BFS": lambda: GraphBFS(graph_data, arr[0] if arr else 0),
                "DFS": lambda: GraphDFS(graph_data, arr[0] if arr else 0),
                "Dijkstra": lambda: Dijkstra(graph_data, arr[0] if arr else 0),
                "HashTable": lambda: HashTable(arr.copy())
            }

            if algo_name in algorithms:
                try:
                    self.current_algorithm = algorithms[algo_name]()
                    self.engine.load_algorithm(self.current_algorithm)
                    
                    # Показываем виджет временных массивов только для MergeSort
                    if algo_name == "MergeSort":
                        self.temp_arrays_widget.show()
                    else:
                        self.temp_arrays_widget.hide()
                    
                    if algo_name in ["BFS", "DFS", "Dijkstra"]:
                        self.scene.clear()
                        
                        self.graph_visualizer.node_values = {val: val for val in arr}
                        
                        if self.graph_layout_combo:
                            layout_name = self.graph_layout_combo.currentText()
                            layout_map = {
                                "Пружинная": "Spring", 
                                "Круговая": "Circular",
                                "Древовидная": "Tree"
                            }
                            
                            if layout_name in layout_map:
                                selected_layout = layout_map[layout_name]
                                success = self.graph_visualizer.set_layout_algorithm(selected_layout)
                                if success:
                                    self._log(f"📐 Установлена компоновка: {layout_name}")
                        
                        self.graph_visualizer.set_directed(self.graph_directed)
                        
                        direction_text = "ориентированный" if self.graph_directed else "неориентированный"
                        self._log(f"🕸️ Подготовка {direction_text} графа для алгоритма {algo_name}...")
                        
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

    def _create_tree_graph(self, arr, weight_mode="diff", min_weight=1, max_weight=10, directed=False):
        """
        Создает древовидный граф.
        """
        graph = {}
        if not arr:
            return graph

        nodes = list(dict.fromkeys(arr))

        def make_weight(a, b):
            if weight_mode == "diff":
                return max(min_weight, abs(int(a) - int(b)))
            elif weight_mode == "uniform":
                return max(1, int(min_weight))
            elif weight_mode == "random":
                return random.randint(min_weight, max_weight)
            else:
                return max(1, abs(int(a) - int(b)))

        for v in nodes:
            graph[v] = {}

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

        try:
            edge_count = sum(len(neighbors) for neighbors in graph.values())
            if directed:
                self._log(f"🌳 Создан ориентированный граф: узлов={len(nodes)}, ребер={edge_count}")
            else:
                self._log(f"🌳 Создан неориентированный граф: узлов={len(nodes)}, ребер={edge_count}")
        except Exception:
            print(f"Generated tree graph: nodes={len(nodes)}, directed={directed}")

        return graph

    def _render_array(self, arr):
        """Рендеринг массива с анимированным появлением."""
        self.scene.clear()
        self.visual_items.clear()
        self._temp_array_items = []
        self._split_lines = []
        self.array_data = arr.copy()
        
        radius, spacing = 30, 15
        total_width = len(arr) * (radius * 2 + spacing)
        scene_width = max(800, total_width + 100)
        
        extended_scene_rect = QRectF(-2000, -2000, 4000, 4000)
        self.scene.setSceneRect(extended_scene_rect)
        
        start_x = (scene_width - total_width) / 2
        start_y = 150

        for i, val in enumerate(arr):
            x = start_x + i * (radius * 2 + spacing)
            y = start_y
            
            circle = ArrayCircleItem(0, 0, val, i, radius)
            circle.setPos(x, y + 300)
            self.scene.addItem(circle)
            self.visual_items.append(circle)
            
            circle.animate_move(x, y, 400 + i * 80)
            QTimer.singleShot(400 + i * 80, lambda c=circle: setattr(c, "is_spawning", False))

    def _render_tree(self, tree_data):
        if self._is_rendering_tree:
            self._is_rendering_tree = False
            print("DEBUG: Already rendering tree, skipping")
            return
        self._is_rendering_tree = True
        """Рендеринг дерева вместо массива."""
        try:
            self.scene.clear()
            self.visual_items.clear()
            
            extended_scene_rect = QRectF(-3000, -3000, 6000, 6000)
            self.scene.setSceneRect(extended_scene_rect)
            
            if not tree_data:
                text_item = self.scene.addText("Дерево пустое или строится...")
                text_item.setPos(0, 0)
                self._log("ℹ️ Дерево пустое - начните выполнение алгоритма")
                return
            
            root = self.tree_visualizer.create_tree_from_structure(tree_data, animate=True)
            
            if root:
                self._center_on_tree()
                self._log("🌳 Дерево построено и отображено")
            else:
                self._log("❌ Ошибка при построении дерева")
        except Exception as e:
            self._log(f"❌ Ошибка при визуализации дерева: {str(e)}")
            import traceback
            traceback.print_exc()
            if hasattr(self, 'current_data'):
                self._render_array(self.current_data)

    def _center_on_tree(self):
        """Центрирует вид на содержимом сцены с масштабированием."""
        if self.scene.items():
            if hasattr(self, 'view') and self.view:
                if hasattr(self.view, 'fit_to_content'):
                    self.view.fit_to_content(150)
                else:
                    rect = self.scene.itemsBoundingRect()
                    if rect.isValid():
                        rect.adjust(-150, -150, 150, 150)
                        self.view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
                self._log("🔍 Дерево отмасштабировано для обзора")

    def _process_action(self, action):
        """Обработка действия с анимацией."""
        self.is_animating = True
        self.current_step += 1
        self.start_btn.setEnabled(False)
        
        t = action.get("type")
        
        base_delay = 800
        speed_factor = max(0.3, 1.0 / self.speed_slider.value())
        
        if t == "tree":
            tree_data = action.get("tree_data")
            if tree_data:
                self._last_tree_data = tree_data
                self._log(action.get("description", "Вставка узла в дерево"))
            
            self._schedule_next_action(int(600 * speed_factor))
        
        elif t == "traversal":
            node_sequence = action.get("nodes", [])
            if self._last_tree_data:
                self._render_tree(self._last_tree_data)
                self.tree_visualizer.highlight_traversal(node_sequence)
            
            self._log(f"🔄 Обход дерева: {action.get('description', '')}")
            self._schedule_next_action(int(len(node_sequence) * 500 * speed_factor))
        
        elif t == "graph_init":
            success = self.graph_visualizer.process_action(action)
            if success:
                graph_info = self.graph_visualizer.get_graph_info()
                action["graph_info"] = graph_info
                self._log(f"🕸️ Инициализирован граф для {action.get('algorithm', 'алгоритма')}")
            else:
                self._log("❌ Ошибка при создании графа")
            self._schedule_next_action(int(800 * speed_factor))
            
        elif t == "visit":
            node_index = action.get('node')
            if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                success = self.graph_visualizer.process_action(action)
                if success:
                    if node_index in self.graph_visualizer.adjacency_list:
                        action["connections"] = self.graph_visualizer.adjacency_list[node_index]
                    self._log(f"📍 Посещен узел: {node_index}")
            elif node_index < len(self.visual_items):
                self.visual_items[node_index].highlight("#4ECDC4")
                self.visual_items[node_index].bounce_animation()
                self._log(f"📍 Посещен элемент: {node_index}")
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "discover":
            from_node = action.get('from_node')
            to_node = action.get('node')
            if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                success = self.graph_visualizer.process_action(action)
                if success:
                    edge_key = self.graph_visualizer._get_edge_key(from_node, to_node)
                    edge_item = self.graph_visualizer.edges.get(edge_key)
                    if edge_item and hasattr(edge_item, 'weight'):
                        action["edge_weight"] = edge_item.weight
                    self._log(f"🔍 Обнаружен узел {to_node} из узла {from_node}")
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "update_distance":
            node_index = action.get('node')
            new_distance = action.get('new_distance')
            if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                success = self.graph_visualizer.process_action(action)
                if success:
                    self._log(f"📊 Обновлено расстояние до узла {node_index}: {new_distance}")
            self._schedule_next_action(int(600 * speed_factor))
            
        # === ОБРАБОТЧИКИ ДЛЯ MERGESORT ===
        elif t == "split":
            left = action.get("left", 0)
            right = action.get("right", 0)
            mid = action.get("mid", 0)
            
            indices = list(range(left, right + 1))
            self._highlight_items(indices, "#FFA500", action.get("description", ""))
            
            self._draw_split_line(mid, left, right)
            
            self._schedule_next_action(int(1000 * speed_factor))
            
        elif t == "merge_start":
            left = action.get("left", 0)
            mid = action.get("mid", 0)
            right = action.get("right", 0)
            
            for i in range(left, mid + 1):
                if i < len(self.visual_items):
                    self.visual_items[i].highlight("#4ECDC4")
            
            for i in range(mid + 1, right + 1):
                if i < len(self.visual_items):
                    self.visual_items[i].highlight("#FF6B6B")
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(800 * speed_factor))
            
        elif t == "temp_arrays":
            left_copy = action.get("left_copy", [])
            right_copy = action.get("right_copy", [])
            
            # Обновляем виджет временных массивов
            self.temp_arrays_widget.update_arrays(left_copy, right_copy)
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(800 * speed_factor))
            
        elif t == "compare_merge":
            i, j = action.get("indices", (0, 0))
            target_index = action.get("target_index", 0)
            
            if i < len(self.visual_items):
                self.visual_items[i].highlight("#FFD700")
                self.visual_items[i].bounce_animation()
            
            if j < len(self.visual_items):
                self.visual_items[j].highlight("#FFD700")
                self.visual_items[j].bounce_animation()
            
            if target_index < len(self.visual_items):
                self.visual_items[target_index].highlight("#7EE081")
            
            desc = action.get("description", "")
            left_val = action.get("left_value", 0)
            right_val = action.get("right_value", 0)
            self._log(f"🔍 {desc}")
            
            self._schedule_next_action(int(700 * speed_factor))
            
        elif t == "select_left" or t == "select_right" or t == "select_from_left" or t == "select_from_right":
            from_idx = action.get("from_index", 0)
            to_idx = action.get("to_index", 0)
            value = action.get("value", 0)
            
            # Определяем тип действия
            is_from_left = "from_left" in t or "left" in t
            
            if from_idx < len(self.visual_items) and to_idx < len(self.visual_items):
                self.visual_items[from_idx].highlight("#FF6B6B" if is_from_left else "#4ECDC4")
                self.visual_items[to_idx].highlight("#7EE081")
                self.visual_items[to_idx].bounce_animation()
                self.visual_items[to_idx].update_value(value)
                
                if to_idx < len(self.array_data):
                    self.array_data[to_idx] = value
            
            source = "левого" if is_from_left else "правого"
            self._log(f"📥 {action.get('description', f'Выбор из {source} массива')}")
            
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "remaining_left" or t == "remaining_right":
            from_idx = action.get("from_index", 0)
            to_idx = action.get("to_index", 0)
            value = action.get("value", 0)
            
            if to_idx < len(self.visual_items):
                self.visual_items[to_idx].highlight("#FFA500")
                self.visual_items[to_idx].bounce_animation()
                self.visual_items[to_idx].update_value(value)
                
                if to_idx < len(self.array_data):
                    self.array_data[to_idx] = value
            
            source = "левого" if t == "remaining_left" else "правого"
            self._log(f"📋 {action.get('description', f'Оставшийся элемент из {source} массива')}")
            
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "merge_complete" or t == "merge_result":
            left = action.get("left", 0)
            right = action.get("right", 0)
            
            for i in range(left, right + 1):
                if i < len(self.visual_items):
                    self.visual_items[i].highlight("#7EE081")
                    if i == left or i == right:
                        self.visual_items[i].bounce_animation()
            
            # Очищаем виджет временных массивов
            self.temp_arrays_widget.clear()
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(800 * speed_factor))
            
        elif t == "base_case":
            index = action.get("index", 0)
            if index < len(self.visual_items):
                self.visual_items[index].highlight("#7EE081")
                self.visual_items[index].bounce_animation()
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "info":
            self._log(f"ℹ️ {action.get('description', '')}")
            self._schedule_next_action(int(500 * speed_factor))
            
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
            if self._last_tree_data:
                self._render_tree(self._last_tree_data)
                self._log("🌳 Построение дерева завершено")
            elif hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                success = self.graph_visualizer.process_action(action)
                if success:
                    self._log("✅ Алгоритм успешно завершён!")
            else:
                self._animate_completion()
                self._log("✅ Алгоритм успешно завершён!")
            
            # Скрываем виджет временных массивов
            self.temp_arrays_widget.hide()
            self.temp_arrays_widget.clear()
            
            self.is_animating = False
            self.algorithm_completed = True
            
            if self.is_auto_mode:
                self._pause_auto_mode()
            
            self.inspector.update_info(action)
            return
            
        # Обновление инспектора с расширенной информацией
        self.inspector.update_info(action)

    def _draw_split_line(self, mid, left, right):
        """Рисует линию разделения между подмассивами."""
        try:
            if left >= len(self.visual_items) or right >= len(self.visual_items):
                return
                
            left_item = self.visual_items[left]
            right_item = self.visual_items[right]
            
            x1 = left_item.x() + left_item.radius
            x2 = right_item.x() + right_item.radius
            y = left_item.y() - 50
            
            line = QGraphicsLineItem(x1, y, x2, y)
            line.setPen(QPen(QColor("#FFA500"), 3, Qt.PenStyle.DashLine))
            line.setZValue(-1)
            self.scene.addItem(line)
            
            text = QGraphicsTextItem(f"Разделение на [{left}:{mid}] и [{mid+1}:{right}]")
            text.setPos((x1 + x2) / 2 - text.boundingRect().width() / 2, y - 25)
            text.setDefaultTextColor(QColor("#FFA500"))
            text.setFont(QFont("Arial", 10))
            self.scene.addItem(text)
            
            self._split_lines.append((line, text))
            
            QTimer.singleShot(2000, lambda: self._remove_split_line(line, text))
            
        except Exception as e:
            print(f"Error drawing split line: {e}")
    
    def _remove_split_line(self, line, text):
        """Удаляет линию разделения."""
        try:
            if line and line in self.scene.items():
                self.scene.removeItem(line)
            if text and text in self.scene.items():
                self.scene.removeItem(text)
        except:
            pass

    def _swap_items(self, i, j):
        """Анимированный обмен элементов."""
        if not (0 <= i < len(self.visual_items) and 0 <= j < len(self.visual_items)):
            return
            
        self.array_data[i], self.array_data[j] = self.array_data[j], self.array_data[i]
        self.visual_items[i], self.visual_items[j] = self.visual_items[j], self.visual_items[i]
        
        self.visual_items[i].index = i
        self.visual_items[j].index = j
        
        self.visual_items[i].highlight("#FF6B6B")
        self.visual_items[j].highlight("#FF6B6B")
        
        radius, spacing = 30, 15
        total_width = len(self.visual_items) * (radius * 2 + spacing)
        scene_width = max(800, total_width + 100)
        start_x = (scene_width - total_width) / 2
        start_y = 150
        
        new_x_i = start_x + i * (radius * 2 + spacing)
        new_x_j = start_x + j * (radius * 2 + spacing)
        
        self.visual_items[i].animate_move(new_x_i, start_y, 600)
        self.visual_items[j].animate_move(new_x_j, start_y, 600)

    def _highlight_items(self, indices, color, description=""):
        """Анимированная подсветка элементов."""
        for i in range(len(self.visual_items)):
            if i in indices:
                self.visual_items[i].highlight(color)
                if len(indices) <= 3:
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
            QTimer.singleShot(100, self.engine._on_tick)
        else:
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
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {msg}")
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event):
        """Обработка закрытия приложения."""
        self.engine.pause()
        event.accept()