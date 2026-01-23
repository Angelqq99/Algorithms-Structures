import faulthandler
faulthandler.enable()
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QComboBox, QPushButton, QLineEdit, QLabel, QSlider, QTextEdit,
    QFrame, QSizePolicy, QSpacerItem, QGraphicsView, QGraphicsScene,
    QProgressBar, QMessageBox, QCheckBox, QGraphicsLineItem, QGraphicsTextItem,
    QGraphicsObject, QGraphicsRectItem,
    QGridLayout, QGroupBox, QScrollArea, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QApplication,QButtonGroup,QRadioButton
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty, QRectF, pyqtSignal, QEasingCurve, QObject, QPointF
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QLinearGradient, QRadialGradient, QClipboard
from controller.engine import Engine
from model.sorting.quicksort import QuickSort
from model.sorting.mergesort import MergeSort
from model.sorting.bubblesort import BubbleSort
from model.sorting.insertionsort import InsertionSort
from model.sorting.selectionsort import SelectionSort
from model.sorting.shellsort import ShellSort
from model.compression.huffman import HuffmanCoding,create_example_texts
from view.huffman_visualizer import HuffmanVisualizer
from model.trees.bst import BST
from model.trees.avl import AVLTree
from model.trees.red_black_tree import RedBlackTree
from model.trees.splay_tree import SplayTree
from model.trees.treap import Treap
from model.trees.b_tree import BTree
from model.search.binary_search import BinarySearch
from model.trees.heap import BinaryHeap
from model.graphs.bfs import GraphBFS
from model.graphs.dfs import GraphDFS
from model.graphs.dijkstra import Dijkstra
from model.hashtable.hashtable import HashTable

from view.tree_visualizer import TreeVisualizer
from view.graph_visualizer import GraphVisualizer
from view.tree_layout import CenteredTreeLayout, CompactTreeLayout
from view.scene_items import ArrayCircleItem, ZoomableGraphicsView, TreeNodeItem, BTreeNodeItem, TreeConnectionItem
from view.inspector import Inspector

from model.containers.stack import Stack
from model.containers.queue import Queue
from model.containers.deque import Deque
from view.container_visualizer import ContainerVisualizer

import random
import json
import math
from datetime import datetime
import re


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
        left_widget.setFixedWidth(200)
        
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
        right_widget.setFixedWidth(200)
        
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
        container.setFixedSize(60, 80)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        # Индекс элемента
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
        
        # Значение под кругом
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
            for i in reversed(range(layout.count())):
                item = layout.takeAt(i)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
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


class HashTableCell(QGraphicsObject):
    """
    Полная ячейка хэш-таблицы с индексом и значением.
    Все элементы создаются как дочерние для обеспечения целостности позиции.
    """
    def __init__(self, x, y, width, height, index, value=None, chain_length=0, is_probing=False, full_chain=None):
        super().__init__()
        # Основные параметры ячейки
        self._rect = QRectF(0, 0, width, height)
        self.setPos(x, y)
        
        self.index = index
        self.value = value
        self.chain_length = chain_length
        self.is_probing = is_probing
        self.is_collision = False
        self.is_occupied = value is not None
        
        # Для хранения полной цепочки (для метода цепочек)
        self.full_chain = full_chain if full_chain is not None else []
        
        # Размеры внутренних областей
        self.index_width = 100
        self.value_width = width - self.index_width
        
        # Внутренние элементы
        self.index_rect = None
        self.index_text = None
        self.value_rect = None
        self.value_text = None
        self.chain_text = None
        
        # Цвета
        self.default_color = QColor("#ffffff")
        self.occupied_color = QColor("#e8f4fd")
        self.collision_color = QColor("#ffebee")
        self.probing_color = QColor("#fff3e0")
        self.chain_color = QColor("#e0f2f1")
        
        # Создаем все дочерние элементы
        self._create_subitems()
        self.setAcceptHoverEvents(True)
        self.setZValue(1)
        
        # Инициализируем состояние
        self._update_appearance()

    def boundingRect(self):
        """Возвращает ограничивающий прямоугольник всей ячейки."""
        return self._rect
    
    def paint(self, painter, option, widget):
        """Отрисовка (пустая, так как все элементы рисуются как дочерние)."""
        pass
    
    def _create_subitems(self):
        """Создает все дочерние графические элементы."""
        # 1. ОБЛАСТЬ ИНДЕКСА (левая часть)
        self.index_rect = QGraphicsRectItem(0, 0, self.index_width, self._rect.height(), self)
        bg_color = QColor("#ecf0f1") if self.index % 2 == 0 else QColor("#bdc3c7")
        self.index_rect.setBrush(QBrush(bg_color))
        self.index_rect.setPen(QPen(QColor("#7f8c8d"), 1))
        
        # Текст индекса
        self.index_text = QGraphicsTextItem(str(self.index), self)
        self.index_text.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.index_text.setDefaultTextColor(QColor("#2c3e50"))
        # Центрирование текста индекса
        text_width = self.index_text.boundingRect().width()
        text_x = (self.index_width - text_width) / 2
        self.index_text.setPos(text_x, 12)
        
        # 2. ОБЛАСТЬ ЗНАЧЕНИЯ (правая часть)
        self.value_rect = QGraphicsRectItem(self.index_width, 0, self.value_width, self._rect.height(), self)
        self.value_rect.setPen(QPen(QColor("#7f8c8d"), 1))
        
        # Текст значения
        self.value_text = QGraphicsTextItem("", self)
        self.value_text.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.value_text.setDefaultTextColor(QColor("#2c3e50"))
        
        # Текст для отображения длины цепочки
        self.chain_text = QGraphicsTextItem("", self)
        self.chain_text.setFont(QFont("Arial", 10))
        self.chain_text.setDefaultTextColor(QColor("#e74c3c"))
    
    def _update_appearance(self):
        """Обновляет внешний вид всех элементов ячейки."""
        # Обновляем цвет области значения
        current_brush_color = self.default_color
        border_color = QColor("#7f8c8d")
        border_width = 1
        
        if self.is_probing:
            current_brush_color = self.probing_color
            border_color = QColor("#e67e22")
            border_width = 2
        elif self.is_collision:
            current_brush_color = self.collision_color
            border_color = QColor("#c0392b")
            border_width = 2
        elif self.chain_length > 1:
            current_brush_color = self.chain_color
            border_color = QColor("#16a085")
        elif self.is_occupied:
            current_brush_color = self.occupied_color
            border_color = QColor("#2980b9")
        
        self.value_rect.setBrush(QBrush(current_brush_color))
        pen = QPen(border_color, border_width)
        self.value_rect.setPen(pen)
        
        # Обновляем текст значения
        if self.value is not None:
            self.value_text.setPlainText(str(self.value))
            # Центрируем текст значения
            text_width = self.value_text.boundingRect().width()
            text_x = self.index_width + (self.value_width - text_width) / 2
            self.value_text.setPos(text_x, 12)
        else:
            self.value_text.setPlainText("")
        
        # Обновляем текст цепочки
        if self.chain_length > 1:
            self.chain_text.setPlainText(f"+{self.chain_length-1} в списке")
            chain_x = self.index_width + self.value_width - 60
            self.chain_text.setPos(chain_x, 35)
        else:
            self.chain_text.setPlainText("")
        
        # Обновляем цвет текста индекса для контраста
        bg_color = QColor("#ecf0f1") if self.index % 2 == 0 else QColor("#bdc3c7")
        brightness = bg_color.red() * 0.299 + bg_color.green() * 0.587 + bg_color.blue() * 0.114
        text_color = QColor("#2c3e50") if brightness > 128 else QColor("#ffffff")
        self.index_text.setDefaultTextColor(text_color)
    
    def set_value(self, value, chain_length=0, full_chain=None):
        """Устанавливает значение ячейки и обновляет отображение."""
        self.value = value
        self.chain_length = chain_length
        self.is_occupied = value is not None
        
        if full_chain is not None:
            self.full_chain = full_chain
        elif value is not None and chain_length == 1:
            # Если одно значение без явной цепочки, создаем цепочку из одного элемента
            self.full_chain = [value]
        
        self._update_appearance()
    
    def set_collision(self, is_collision=True):
        """Устанавливает состояние коллизии."""
        self.is_collision = is_collision
        self._update_appearance()
    
    def set_probing(self, is_probing=True):
        """Устанавливает состояние пробирования."""
        self.is_probing = is_probing
        self._update_appearance()
    
    def hoverEnterEvent(self, event):
        """Обработка наведения мыши."""
        try:
            tooltip = f"Индекс: {self.index}\n"
            if self.value is not None:
                tooltip += f"Значение: {self.value}\n"
                if hasattr(self, 'full_chain') and self.full_chain and len(self.full_chain) > 1:
                    tooltip += f"Длина цепочки: {len(self.full_chain)}"
            else:
                tooltip += "Значение: Пусто"
            self.setToolTip(tooltip)
        except Exception as e:
            print(f"Error in hoverEnterEvent: {e}")
            self.setToolTip(f"Индекс: {self.index}")
        
        super().hoverEnterEvent(event)


class ChainsViewerDialog(QDialog):
    """Диалог для просмотра всех цепочек в хэш-таблице."""
    
    def __init__(self, hashtable_data, parent=None):
        super().__init__(parent)
        self.hashtable_data = hashtable_data
        self.setWindowTitle("🔗 Просмотр всех цепочек")
        self.setMinimumSize(600, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Настройка интерфейса диалога."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = QLabel("Все цепочки в хэш-таблице")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #e8f4fd;
                border-radius: 8px;
                border: 2px solid #5A9BD5;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Статистика
        stats = self._calculate_statistics()
        stats_label = QLabel(
            f"📊 Статистика:\n"
            f"• Всего цепочек: {stats['total_chains']}\n"
            f"• Макс. длина цепочки: {stats['max_chain_length']}\n"
            f"• Средняя длина: {stats['avg_chain_length']:.2f}\n"
            f"• Пустых ячеек: {stats['empty_cells']}"
        )
        stats_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #5A9BD5;
                padding: 10px;
                background-color: #f0f8ff;
                border-radius: 5px;
                border: 1px solid #d0e0ff;
            }
        """)
        layout.addWidget(stats_label)
        
        # Таблица цепочек
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Индекс", "Длина цепочки", "Элементы"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Заполняем таблицу
        self._populate_table()
        
        # Настройка стиля таблицы
        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #d0d0d0;
                border-radius: 5px;
                background-color: white;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #5A9BD5;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e0f0ff;
                color: #2c3e50;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        # Кнопка копирования
        copy_btn = QPushButton("📋 Копировать все цепочки")
        copy_btn.clicked.connect(self._copy_all_chains)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3dbcb3;
            }
            QPushButton:pressed {
                background-color: #2eaba2;
            }
        """)
        
        # Кнопка закрытия
        close_btn = QPushButton("✖ Закрыть")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border-radius: 6px;
                padding: 10px 30px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e55a5a;
            }
            QPushButton:pressed {
                background-color: #d44a4a;
            }
        """)
        
        button_layout.addWidget(copy_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def _calculate_statistics(self):
        """Вычисляет статистику по цепочкам."""
        total_chains = 0
        max_length = 0
        total_length = 0
        empty_cells = 0
        
        for i, cell_data in enumerate(self.hashtable_data):
            if isinstance(cell_data, list):
                if cell_data:  # Не пустой список
                    length = len(cell_data)
                    total_chains += 1
                    total_length += length
                    if length > max_length:
                        max_length = length
                else:
                    empty_cells += 1
            else:  # Одиночное значение или None
                if cell_data is None:
                    empty_cells += 1
                else:
                    total_chains += 1
                    total_length += 1
                    if 1 > max_length:
                        max_length = 1
        
        avg_length = total_length / total_chains if total_chains > 0 else 0
        
        return {
            'total_chains': total_chains,
            'max_chain_length': max_length,
            'avg_chain_length': avg_length,
            'empty_cells': empty_cells
        }
    
    def _populate_table(self):
        """Заполняет таблицу данными о цепочках."""
        chain_count = 0
        
        for i, cell_data in enumerate(self.hashtable_data):
            chain_items = []
            
            if isinstance(cell_data, list):
                if cell_data:  # Не пустой список
                    chain_items = cell_data
                else:
                    continue  # Пропускаем пустые списки
            elif cell_data is not None:  # Одиночное значение
                chain_items = [cell_data]
            else:
                continue  # Пропускаем None
            
            # Добавляем строку в таблицу
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Индекс
            index_item = QTableWidgetItem(str(i))
            index_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            index_item.setBackground(QColor("#f0f8ff"))
            self.table.setItem(row, 0, index_item)
            
            # Длина цепочки
            length_item = QTableWidgetItem(str(len(chain_items)))
            length_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Цвет в зависимости от длины
            if len(chain_items) == 1:
                length_item.setBackground(QColor("#e8f4fd"))
            elif len(chain_items) <= 3:
                length_item.setBackground(QColor("#fff3e0"))
            else:
                length_item.setBackground(QColor("#ffebee"))
                
            self.table.setItem(row, 1, length_item)
            
            # Элементы цепочки
            elements_text = ", ".join(str(item) for item in chain_items)
            elements_item = QTableWidgetItem(elements_text)
            elements_item.setBackground(QColor("#f9f9f9"))
            self.table.setItem(row, 2, elements_item)
            
            chain_count += 1
        
        # Автонастройка ширины столбцов
        self.table.resizeColumnsToContents()
        
        # Если нет цепочек
        if chain_count == 0:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("Нет цепочек в таблице")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_item.setForeground(QColor("#999"))
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 3)
    
    def _copy_all_chains(self):
        """Копирует все цепочки в текстовном формате."""
        try:
            text = "Все цепочки в хэш-таблице:\n\n"
            
            for i, cell_data in enumerate(self.hashtable_data):
                chain_items = []
                
                if isinstance(cell_data, list):
                    if cell_data:
                        chain_items = cell_data
                    else:
                        continue
                elif cell_data is not None:
                    chain_items = [cell_data]
                else:
                    continue
                
                text += f"Индекс {i} (длина: {len(chain_items)}):\n"
                for j, item in enumerate(chain_items):
                    text += f"  {j+1}. {item}\n"
                text += "\n"
            
            # Копируем в буфер обмена
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # Показываем уведомление
            QMessageBox.information(
                self, 
                "Скопировано", 
                "Все цепочки скопированы в буфер обмена!"
            )
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Ошибка",
                f"Не удалось скопировать данные: {str(e)}"
            )


class MainWindow(QMainWindow):
    """Главное окно визуализатора алгоритмов"""
    
    hashtable_completed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализатор алгоритмов и структур данных")
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
        
        # Для хэш-таблицы
        self.hashtable_cells = []
        self.hashtable_stats = {}
        self.hashtable_display_mode = "initial"
        self.hashtable_scroll_enabled = False
        self.current_hashtable_data = []  # Для хранения текущих данных таблицы
        
        # Для структур данных (стек, очередь, дек)
        self.container_visualizer = None
        self.container_type = None
        
        # Для графов
        self.graph_data = None
        self.graph_directed = False
        self.graph_layout = "Spring"
        
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
        self.container_visualizer = None
        # Для алгоритма Хаффмана
        self.huffman_visualizer = HuffmanVisualizer(self.scene)
        self.huffman_codes_table = []
        self.huffman_current_text = ""
        self.huffman_examples = create_example_texts()
        self.inspector = Inspector()
        
        # Виджет временных массивов
        self.temp_arrays_widget = TempArraysWidget()

        # Добавляем таймер для отложенного сброса зума
        self.zoom_reset_timer = QTimer()
        self.zoom_reset_timer.setSingleShot(True)
        self.zoom_reset_timer.timeout.connect(self._delayed_zoom_reset)
        
        # Таймер для анимации хэш-таблицы
        self.hashtable_animation_timer = QTimer()
        self.hashtable_animation_timer.timeout.connect(self._animate_hashtable_cell)
        self.animation_queue = []

        # Инициализация интерактивных операций
        self.interactive_widget = None
        self.val_input = None
        self.tree_ops_combo = None
        self.execute_btn = None
        self.btn_min = self.btn_max = self.btn_height = self.btn_balance = None
        self.btn_clear = self.btn_random = None
        self.btn_fit_view = self.btn_center = self.btn_zoom_in = self.btn_zoom_out = None
        
        # Для интерактивного поиска
        self._search_generator = None
        self._search_value = None

        # Система цветов
        self._setup_color_system()

        self._setup_ui()
        self._connect_signals()

    def _setup_color_system(self):
        """Инициализация системы цветов для визуализации."""
        # Цветовая палитра для сортировок
        self.color_palette = {
            # Основные состояния
            "default": "#5A9BD5",        # Синий - обычное состояние
            "sorted": "#7EE081",         # Зеленый - отсортированное положение
            "current": "#FFD700",        # Желтый - текущий элемент
            "comparing": "#FFA500",      # Оранжевый - сравнение
            "swapping": "#FF6B6B",       # Красный - обмен
            "pivot": "#9B59B6",         # Фиолетовый - опорный элемент
            "key": "#3498DB",           # Голубой - ключевой элемент (для InsertionSort)
            "shifted": "#E67E22",       # Оранжевый темный - сдвинутый элемент
            "selected": "#1ABC9C",      # Бирюзовый - выбранный (для SelectionSort)
            "group": "#4ECDC4",         # Бирюзовый светлый - группа (ShellSort)
            "merging": "#2ECC71",       # Зеленый - слияние
            "merge_left": "#4ECDC4",    # Бирюзовый - левый массив MergeSort
            "merge_right": "#FF6B6B",   # Красный - правый массив MergeSort
            "merge_target": "#7EE081",  # Светло-зеленый - целевая позиция MergeSort
            
            # Графовые цвета
            "graph_visited": "#7EE081",     # Зеленый - посещенный узел
            "graph_discovered": "#F9C80E",  # Желтый - обнаруженный узел
            "graph_path": "#FF6B6B",        # Красный - путь
            "graph_mst": "#4ECDC4",         # Бирюзовый - ребро MST
            "graph_rejected": "#95A5A6",    # Серый - отвергнутое ребро
            
            # Вспомогательные
            "highlight": "#FFD700",     # Желтый - временная подсветка
            "info": "#3498DB",          # Синий - информационный
            "warning": "#E74C3C",       # Красный - предупреждение
            "success": "#2ECC71",       # Зеленый - успех
        }
        
        # Сброс кэша цветов
        self.current_highlight = set()
        self.last_operation = None

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Левая панель (управление)
        left_panel = self._create_left_panel()
        
        # Центральная панель (визуализация)
        center_panel = self._create_center_panel()
        
        # Правая панель (интерактивные операции)
        right_panel = self._create_interactive_panel()
        self.interactive_widget = right_panel

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 800, 350])
        main_layout.addWidget(splitter)

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
        title = QLabel("Управление алгоритмами и структурами")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        left_layout.addWidget(title)

        # Категория и алгоритм
        left_layout.addWidget(QLabel("Категория:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Сортировки", "Деревья", "Графы", "Хэш-таблицы", "Структуры данных","Сжатие данных"])
        
        left_layout.addWidget(QLabel("Алгоритм:"))
        self.algorithm_combo = QComboBox()
        self._initialize_algorithm_combo()

        # Данные
        left_layout.addWidget(QLabel("Данные:"))
        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Введите данные через запятую: 5,2,8,1")
        
        # Настройки графа
        self.graph_settings_label = QLabel("Настройки графа:")
        self.graph_settings_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        
        # Направленность графа
        self.directed_label = QLabel("Направленность графа:")
        directed_layout = QHBoxLayout()
        self.directed_button_group = QButtonGroup(self)
        self.directed_undirected = QRadioButton("Неориентированный")
        self.directed_directed = QRadioButton("Ориентированный")
        self.directed_undirected.setChecked(True)
        self.directed_button_group.addButton(self.directed_undirected)
        self.directed_button_group.addButton(self.directed_directed)
        directed_layout.addWidget(self.directed_undirected)
        directed_layout.addWidget(self.directed_directed)
        
        # Компоновка графа
        self.graph_layout_label = QLabel("Компоновка графа:")
        self.graph_layout_combo = QComboBox()
        self.graph_layout_combo.addItems(["Пружинная", "Круговая", "Древовидная"])
        
        # Кнопка построения графа
        self.build_graph_btn = QPushButton("🕸️ Построить граф")
        self.build_graph_btn.setStyleSheet("""
            QPushButton {
                background-color: #9B59B6;
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                border: none;
                margin-top: 5px;
            }
            QPushButton:hover { 
                background-color: #8E44AD; 
            }
            QPushButton:pressed { 
                background-color: #7D3C98; 
            }
        """)
        self.build_graph_btn.clicked.connect(self._build_graph)
        
        # Скрываем настройки графов по умолчанию
        self.graph_settings_label.hide()
        self.directed_label.hide()
        self.directed_undirected.hide()
        self.directed_directed.hide()
        self.graph_layout_label.hide()
        self.graph_layout_combo.hide()
        self.build_graph_btn.hide()
        
        # Настройки хэш-таблицы
        self.hashtable_settings_label = QLabel("Настройки хэш-таблицы:")
        self.hashtable_settings_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        
        # Функция хеширования
        self.hash_function_label = QLabel("Функция хеширования:")
        self.hash_function_combo = QComboBox()
        self.hash_function_combo.addItems(["Деления", "Умножения", "Простая"])
        
        # Метод разрешения коллизий
        self.collision_method_label = QLabel("Метод разрешения коллизий:")
        self.collision_method_combo = QComboBox()
        self.collision_method_combo.addItems(["Линейное пробирование", "Квадратичное пробирование", 
                                            "Двойное хеширование", "Метод цепочек"])
        
        # Размер таблиции
        self.table_size_label = QLabel("Размер таблицы:")
        self.table_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.table_size_slider.setRange(5, 30)
        self.table_size_slider.setValue(10)
        self.table_size_value = QLabel("10")
        
        table_size_layout = QHBoxLayout()
        table_size_layout.addWidget(self.table_size_label)
        table_size_layout.addWidget(self.table_size_slider)
        table_size_layout.addWidget(self.table_size_value)
        
        # Скрываем настройки хэш-таблицы по умолчанию
        self.hashtable_settings_label.hide()
        self.hash_function_label.hide()
        self.hash_function_combo.hide()
        self.collision_method_label.hide()
        self.collision_method_combo.hide()
        self.table_size_label.hide()
        self.table_size_slider.hide()
        self.table_size_value.hide()
        
        # Кнопки управления
        self.generate_btn = QPushButton("🎲 Сгенерировать случайные данные")
        self.start_btn = QPushButton("▶ Запуск (ручной режим)")
        self.auto_btn = QPushButton("⚙ Автоматический режим")
        self.pause_btn = QPushButton("⏸ Пауза")
        self.reset_btn = QPushButton("⟳ Сброс алгоритма")
        
        # Новая кнопка для просмотра цепочек
        self.view_chains_btn = QPushButton("🔗 Просмотреть цепочки")
        self.view_chains_btn.clicked.connect(self._show_chains_viewer)
        self.view_chains_btn.setEnabled(False)
        self.view_chains_btn.hide()

        self.pause_btn.hide()

        button_style = """
            QPushButton {
                background-color: #5A9BD5;
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                border: none;
                margin-top: 5px;
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
        
        # Специальный стиль для кнопки просмотра цепочек
        self.view_chains_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                border: 2px solid #2eaba2;
                font-size: 13px;
            }
            QPushButton:hover { 
                background-color: #3dbcb3; 
                border: 2px solid #1d9a91;
            }
            QPushButton:pressed { 
                background-color: #2eaba2; 
            }
            QPushButton:disabled {
                background-color: #b0d0cd;
                color: #e0f0ee;
                border: 2px solid #a0c0bd;
            }
        """)

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
        left_layout.addLayout(directed_layout)
        left_layout.addWidget(self.graph_layout_label)
        left_layout.addWidget(self.graph_layout_combo)
        left_layout.addWidget(self.build_graph_btn)
        
        left_layout.addWidget(self.hashtable_settings_label)
        left_layout.addWidget(self.hash_function_label)
        left_layout.addWidget(self.hash_function_combo)
        left_layout.addWidget(self.collision_method_label)
        left_layout.addWidget(self.collision_method_combo)
        left_layout.addLayout(table_size_layout)
        
        left_layout.addWidget(self.generate_btn)
        left_layout.addWidget(self.start_btn)
        left_layout.addWidget(self.auto_btn)
        left_layout.addWidget(self.pause_btn)
        left_layout.addWidget(self.reset_btn)
        left_layout.addWidget(self.view_chains_btn)
        left_layout.addLayout(speed_layout)
        
        # Виджет временных массивов MergeSort
        left_layout.addWidget(self.temp_arrays_widget)
        self.temp_arrays_widget.hide()
        
        left_layout.addWidget(QLabel("Инспектор состояния:"))
        left_layout.addWidget(self.inspector)
        left_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        return left_panel

    def _create_center_panel(self):
        """Создает центральную панель с визуализацией."""
        center_panel = QFrame()
        center_panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff; 
                border-radius: 8px;
                border: 1px solid #d0d0d0;
            }
        """)
        
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(15, 15, 15, 15)
        center_layout.setSpacing(8)

        viz_label = QLabel("Визуализация:")
        viz_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        center_layout.addWidget(viz_label)

        self.view.setStyleSheet("""
            QGraphicsView {
                background: #fafafa; 
                border: 2px solid #e0e0e0; 
                border-radius: 6px;
            }
        """)
        
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self.view, 4)
        
        # Добавляем панель управления визуализацией
        viz_controls = self._create_visualization_controls()
        center_layout.addWidget(viz_controls)

        log_label = QLabel("Пошаговое объяснение:")
        log_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        center_layout.addWidget(log_label)

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
        center_layout.addWidget(self.log_text, 1)

        return center_panel

    def _create_visualization_controls(self):
        """Создает панель управления визуализацией."""
        controls = QWidget()
        layout = QHBoxLayout(controls)
        layout.setContentsMargins(0, 5, 0, 5)
        
        self.btn_fit_view = QPushButton("🔍 Подогнать вид")
        self.btn_fit_view.clicked.connect(self._fit_to_content)
        self.btn_fit_view.setToolTip("Подогнать масштаб к содержимому")
        
        self.btn_center = QPushButton("🎯 Центрировать")
        self.btn_center.clicked.connect(self._center_view)
        self.btn_center.setToolTip("Центрировать вид")
        
        # Стили кнопок
        button_style = """
            QPushButton {
                background-color: #5A9BD5;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4B89C6;
            }
            QPushButton:pressed {
                background-color: #3A6FA3;
            }
        """
        
        for btn in [self.btn_fit_view, self.btn_center]:
            btn.setStyleSheet(button_style)
            layout.addWidget(btn)
        
        layout.addStretch()
        return controls

    def _create_interactive_panel(self):
        """Создает панель интерактивных операций для структур данных."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #5A9BD5;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Заголовок
        title = QLabel("⚙️ Интерактивные операции")
        title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding-bottom: 5px;
                border-bottom: 2px solid #5A9BD5;
            }
        """)
        layout.addWidget(title)
        
        # Контейнер для операций в зависимости от типа
        self.operations_container = QWidget()
        self.operations_layout = QVBoxLayout(self.operations_container)
        self.operations_layout.setSpacing(8)
        layout.addWidget(self.operations_container)
        
        # Информационная панель
        self.info_label = QLabel("ℹ️ Выберите структуру данных для интерактивных операций")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                font-style: italic;
                padding: 5px;
                background-color: #f0f8ff;
                border-radius: 4px;
                border: 1px solid #d0e0ff;
            }
        """)
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        layout.addStretch()
        
        return panel

    def _create_graph_interactive_panel(self):
        """Создает панель интерактивных операций для графов."""
        # Очищаем контейнер полностью
        self._clear_interactive_panel_children()
        
        # Обновляем информационную метку
        self.info_label.setText("ℹ️ Выполняйте алгоритмы на построенном графе")
        
        # Выбор начального узла
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Начальный узел:"))
        self.graph_start_input = QLineEdit()
        self.graph_start_input.setPlaceholderText("Введите номер узла...")
        self.graph_start_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #5A9BD5;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        start_layout.addWidget(self.graph_start_input)
        self.operations_layout.addLayout(start_layout)
        
        # Выбор алгоритма
        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("Алгоритм:"))
        self.graph_algo_combo = QComboBox()
        self.graph_algo_combo.addItems([
            "BFS (обход в ширину)",
            "DFS (обход в глубину)",
            "Dijkstra (кратчайший путь)"
        ])
        self.graph_algo_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #5A9BD5;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        algo_layout.addWidget(self.graph_algo_combo)
        self.operations_layout.addLayout(algo_layout)
        
        # Кнопка выполнения
        self.graph_execute_btn = QPushButton("Запустить алгоритм")
        self.graph_execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #9B59B6;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #8E44AD;
            }
            QPushButton:pressed {
                background-color: #7D3C98;
            }
        """)
        self.graph_execute_btn.clicked.connect(self._on_graph_algorithm_execute)
        self.operations_layout.addWidget(self.graph_execute_btn)
        
        # Панель быстрых действий
        quick_actions = QGroupBox("Быстрые действия")
        quick_actions.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        quick_layout = QHBoxLayout()
        
        # Кнопки быстрых действий
        self.graph_reset_btn = QPushButton("♻ Сброс алгоритма")
        self.graph_reset_btn.clicked.connect(self._reset_graph_algorithm)
        self.graph_reset_btn.setToolTip("Сбросить текущий алгоритм")
        
        self.graph_clear_btn = QPushButton("🗑️ Очистить граф")
        self.graph_clear_btn.clicked.connect(self._clear_graph)
        self.graph_clear_btn.setToolTip("Удалить граф")
        
        # Стили кнопок быстрых действий
        quick_button_style = """
            QPushButton {
                background-color: #5A9BD5;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4B89C6;
            }
            QPushButton:pressed {
                background-color: #3A6FA3;
            }
        """
        
        for btn in [self.graph_reset_btn, self.graph_clear_btn]:
            btn.setStyleSheet(quick_button_style)
            btn.setMinimumHeight(35)
            quick_layout.addWidget(btn)
        
        quick_actions.setLayout(quick_layout)
        self.operations_layout.addWidget(quick_actions)

    def _clear_interactive_panel_children(self):
        """Очищает все дочерние элементы интерактивной панели."""
        # Удаляем все виджеты из operations_layout
        while self.operations_layout.count():
            item = self.operations_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                # Рекурсивно очищаем вложенные layout
                self._clear_layout_recursive(item.layout())
        
        # Сбрасываем ссылки на виджеты
        self.graph_start_input = None
        self.graph_algo_combo = None
        self.graph_execute_btn = None
        self.graph_reset_btn = None
        self.graph_clear_btn = None
        self.search_val_input = None
        self.search_execute_btn = None
    def _clear_layout_recursive(self, layout):
        """Рекурсивно очищает layout и все его дочерние элементы."""
        if layout:
            for i in reversed(range(layout.count())):
                item = layout.takeAt(i)
                if item.widget():
                    widget = item.widget()
                    widget.setParent(None)
                    widget.deleteLater()
                elif item.layout():
                    self._clear_layout_recursive(item.layout())

    def _create_container_interactive_panel(self, container_type):
        """Создает панель интерактивных операций для контейнеров."""
        # Очищаем контейнер полностью
        self._clear_interactive_panel_children()
        
        # Обновляем информационную метку
        self.info_label.setText(f"ℹ️ Выполняйте операции с {container_type} в реальном времени")
        
        # Поле ввода значения
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Значение:"))
        self.container_val_input = QLineEdit()
        self.container_val_input.setPlaceholderText("Введите число...")
        self.container_val_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #5A9BD5;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        self.container_val_input.returnPressed.connect(self._on_container_operation_execute)
        input_layout.addWidget(self.container_val_input)
        self.operations_layout.addLayout(input_layout)
        
        # Выбор операции
        ops_layout = QHBoxLayout()
        ops_layout.addWidget(QLabel("Операция:"))
        self.container_ops_combo = QComboBox()
        
        # Операции в зависимости от типа контейнера
        if container_type == "stack":
            self.container_ops_combo.addItems([
                "push (добавить)",
                "pop (удалить верхний)",
                "peek (посмотреть верхний)",
                "size (размер)",
                "is_empty (пусто?)"
            ])
        elif container_type == "queue":
            self.container_ops_combo.addItems([
                "enqueue (добавить)",
                "dequeue (удалить первый)",
                "front (посмотреть первый)",
                "back (посмотреть последний)",
                "size (размер)",
                "is_empty (пусто?)"
            ])
        elif container_type == "deque":
            self.container_ops_combo.addItems([
                "push_front (добавить в начало)",
                "push_back (добавить в конец)",
                "pop_front (удалить из начала)",
                "pop_back (удалить из конца)",
                "front (посмотреть первый)",
                "back (посмотреть последний)",
                "size (размер)",
                "is_empty (пусто?)"
            ])
        
        self.container_ops_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #5A9BD5;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        ops_layout.addWidget(self.container_ops_combo)
        self.operations_layout.addLayout(ops_layout)
        
        # Кнопка выполнения
        self.container_execute_btn = QPushButton("Выполнить операцию")
        self.container_execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3dbcb3;
            }
            QPushButton:pressed {
                background-color: #2eaba2;
            }
        """)
        self.container_execute_btn.clicked.connect(self._on_container_operation_execute)
        self.operations_layout.addWidget(self.container_execute_btn)
        
        # Панель быстрых действий
        quick_actions = QGroupBox("Быстрые действия")
        quick_actions.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        quick_layout = QHBoxLayout()
        
        # Кнопки быстрых действий
        self.container_clear_btn = QPushButton("🗑️ Очистить")
        self.container_clear_btn.clicked.connect(self._clear_container)
        self.container_clear_btn.setToolTip("Очистить структуру")
        
        self.container_random_btn = QPushButton("🎲 Добавить 3 случайных")
        self.container_random_btn.clicked.connect(self._add_random_to_container)
        self.container_random_btn.setToolTip("Добавить 3 случайных значения")
        
        # Стили кнопок быстрых действий
        quick_button_style = """
            QPushButton {
                background-color: #5A9BD5;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4B89C6;
            }
            QPushButton:pressed {
                background-color: #3A6FA3;
            }
        """
        
        for btn in [self.container_clear_btn, self.container_random_btn]:
            btn.setStyleSheet(quick_button_style)
            btn.setMinimumHeight(35)
            quick_layout.addWidget(btn)
        
        quick_actions.setLayout(quick_layout)
        self.operations_layout.addWidget(quick_actions)
    def _clear_interactive_panel_children(self):
        """Очищает все дочерние элементы интерактивной панели."""
        # Удаляем все виджеты из operations_layout
        while self.operations_layout.count():
            item = self.operations_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                # Рекурсивно очищаем вложенные layout
                self._clear_layout_recursive(item.layout())
        
        # Сбрасываем ссылки на виджеты
        self.container_val_input = None
        self.container_ops_combo = None
        self.container_execute_btn = None
        self.container_clear_btn = None
        self.container_random_btn = None
    def _create_tree_interactive_panel(self):
        """Создает панель интерактивных операций для деревьев."""
        # Двойная проверка категории
        if self.category_combo.currentText() != "Деревья":
            return
        
        # Полностью очищаем предыдущие виджеты
        self._clear_interactive_panel_children()
        
        # Ждем завершения очистки
        QApplication.processEvents()
        
        # Обновляем информационную метку
        self.info_label.setText("ℹ️ Выполняйте операции с деревом в реальном времени")
        
        # Скрываем панель операций перед созданием новых виджетов
        self.operations_container.hide()
        
        # Вместо создания отдельного виджета, создаем элементы напрямую в operations_layout
        # чтобы избежать временного появления отдельного окна
        
        # Поле ввода значения
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Значение:"))
        self.val_input = QLineEdit()
        self.val_input.setPlaceholderText("Введите число...")
        self.val_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #5A9BD5;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        input_layout.addWidget(self.val_input)
        self.operations_layout.addLayout(input_layout)
        
        # Выбор операции
        self.operations_layout.addWidget(QLabel("Операция:"))
        self.tree_ops_combo = QComboBox()
        algo_name = self.algorithm_combo.currentText()
        if algo_name == "Heap":
                # Операции специфичные для кучи
                self.tree_ops_combo.addItems([
                    "Вставить узел",
                    "Удалить корень (delete)",
                    "Посмотреть корень (peek)",
                    "Получить размер (get_size)",
                    "Проверить на пустоту (is_empty)",
                    "Получить max (для max-heap)",
                    "Получить min (для min-heap)",
                    "Преобразовать в min-heap",
                    "Преобразовать в max-heap",
                    "Очистить кучу"
                ])
        else:
            # Оригинальные операции для других деревьев
            self.tree_ops_combo.addItems([
                "Вставить узел",
                "Удалить узел",
                "Найти узел",
                "Прямой обход (Pre-order)",
                "Центральный обход (In-order)",
                "Обратный обход (Post-order)",
                "Обход в ширину (BFS)"
            ])
        self.tree_ops_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #5A9BD5;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        self.operations_layout.addWidget(self.tree_ops_combo)
        
        # Кнопка выполнения
        self.execute_btn = QPushButton("Выполнить операцию")
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3dbcb3;
            }
            QPushButton:pressed {
                background-color: #2eaba2;
            }
        """)
        self.operations_layout.addWidget(self.execute_btn)
        
        # Панель быстрых действий
        quick_actions = QGroupBox("Быстрые действия")
        quick_actions.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        quick_layout = QGridLayout()
        
        # Кнопки быстрых действий
        self.btn_min = QPushButton("Найти min")
        self.btn_max = QPushButton("Найти max")
        self.btn_height = QPushButton("Высота")
        self.btn_balance = QPushButton("Баланс")
        self.btn_clear = QPushButton("🗑️ Очистить")
        self.btn_random = QPushButton("🎲 Случайные")
        
        # Стили кнопок быстрых действий
        quick_button_style = """
            QPushButton {
                background-color: #5A9BD5;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4B89C6;
            }
            QPushButton:pressed {
                background-color: #3A6FA3;
            }
        """
        
        for btn in [self.btn_min, self.btn_max, self.btn_height, self.btn_balance, 
                    self.btn_clear, self.btn_random]:
            btn.setStyleSheet(quick_button_style)
            btn.setMinimumHeight(35)
        
        # Размещаем кнопки в сетке
        quick_layout.addWidget(self.btn_min, 0, 0)
        quick_layout.addWidget(self.btn_max, 0, 1)
        quick_layout.addWidget(self.btn_height, 1, 0)
        quick_layout.addWidget(self.btn_balance, 1, 1)
        quick_layout.addWidget(self.btn_clear, 2, 0)
        quick_layout.addWidget(self.btn_random, 2, 1)
        
        quick_actions.setLayout(quick_layout)
        self.operations_layout.addWidget(quick_actions)
        
        # Подключаем сигналы
        self.val_input.returnPressed.connect(self._on_operation_execute)
        self.execute_btn.clicked.connect(self._on_operation_execute)
        self.btn_min.clicked.connect(lambda: self._find_min_max("min"))
        self.btn_max.clicked.connect(lambda: self._find_min_max("max"))
        self.btn_height.clicked.connect(self._get_tree_height)
        self.btn_balance.clicked.connect(self._check_balance)
        self.btn_clear.clicked.connect(self._clear_tree)
        self.btn_random.clicked.connect(self._add_random_nodes)
        
        # Показываем панель операций
        self.operations_container.show()
        
        # Принудительное обновление
        self.operations_container.update()
        self.interactive_widget.update()
        QApplication.processEvents()

    def _clear_interactive_panel(self):
        """Очищает панель интерактивных операций."""
        # Очищаем контейнер
        self._clear_interactive_panel_children()
        
        # Возвращаем информационную метку
        self.info_label.setText("ℹ️ Выберите структуру данных для интерактивных операций")

    def _connect_signals(self):
        """Подключение сигналов к слотам."""
        self.category_combo.currentTextChanged.connect(self._on_category_changed)
        self.algorithm_combo.currentTextChanged.connect(self._on_algorithm_changed)
        self.speed_slider.valueChanged.connect(self._update_speed)
        self.generate_btn.clicked.connect(self._generate_random_data)
        self.start_btn.clicked.connect(self._step_algorithm)
        self.auto_btn.clicked.connect(self._start_auto_mode)
        self.pause_btn.clicked.connect(self._pause_auto_mode)
        self.reset_btn.clicked.connect(self._reset_algorithm)
        self.table_size_slider.valueChanged.connect(
            lambda v: self.table_size_value.setText(str(v))
        )
        self.directed_undirected.toggled.connect(lambda: self._on_directed_changed(False))
        self.directed_directed.toggled.connect(lambda: self._on_directed_changed(True))


    def _on_directed_changed(self, is_directed):
        """Обработка изменения направленности графа."""
        self.graph_directed = is_directed
        self.graph_visualizer.set_directed(is_directed)
        
        direction_text = "ориентированный" if is_directed else "неориентированный"
        self._log(f"📊 Граф установлен как {direction_text}")
        
        # Если граф уже построен, перестраиваем его с новой направленностью
        if self.graph_data:
            self._build_graph()

    def _on_algorithm_changed(self, algorithm_name):
        """Обработка изменения алгоритма."""
        # Очищаем интерактивную панель при смене алгоритма
        self._clear_interactive_panel()
        
        # При изменении алгоритма сбрасываем состояние
        if self.current_algorithm:
            self._reset_algorithm()
        
        # Обновляем интерактивную панель
        category = self.category_combo.currentText()
        if category == "Структуры данных":
            # Для структур данных создаем соответствующую панель и инициализируем контейнер
            self._create_container_panel_for_current_algo()
        elif category == "Деревья":
            # Для деревьев создаем соответствующую панель
            self._create_tree_interactive_panel()
        elif category == "Графы":
            # Для графов создаем панель интерактивных операций
            self._create_graph_interactive_panel()
        else:
            # Для других категорий очищаем панель
            self._clear_interactive_panel()

    def _initialize_algorithm_combo(self):
        """Инициализация выпадающего списка алгоритмов."""
        category = self.category_combo.currentText()
        self.algorithm_combo.clear()
        if category == "Сортировки":
            self.algorithm_combo.addItems([
                "QuickSort", 
                "MergeSort", 
                "BubbleSort",
                "InsertionSort",  
                "SelectionSort",  
                "ShellSort"       
            ])
        elif category == "Деревья":
            self.algorithm_combo.addItems(["BST", "AVL", "RedBlackTree", "SplayTree", "Treap", "BTree","Heap"])
        elif category == "Графы":
            self.algorithm_combo.addItems(["Graph"])
        elif category == "Хэш-таблицы":
            self.algorithm_combo.addItems(["HashTable"])
        elif category == "Структуры данных":
            self.algorithm_combo.addItems(["Stack", "Queue", "Deque"])
        elif category == "Сжатие данных":
            self.algorithm_combo.addItems(["Huffman Coding"])

    def _update_speed(self, value):
        """Изменение скорости во время работы."""
        self.speed_label.setText(f"x{value}")
        self.engine.set_speed(value)
        self._log(f"⚡ Скорость изменена: x{value}")

    
    def _on_category_changed(self, category):
        """Обработка изменения категории алгоритма."""
        # 1. Приостанавливаем все операции
        self.engine.pause()
        
        # 2. Скрываем ВСЕ специфичные виджеты
        self.temp_arrays_widget.hide()
        self.temp_arrays_widget.clear()
        
        # 3. Скрываем/показываем настройки графов
        if category == "Графы":
            self.graph_settings_label.show()
            self.directed_label.show()
            self.directed_undirected.show()
            self.directed_directed.show()
            self.graph_layout_label.show()
            self.graph_layout_combo.show()
            self.build_graph_btn.show()
        else:
            self.graph_settings_label.hide()
            self.directed_label.hide()
            self.directed_undirected.hide()
            self.directed_directed.hide()
            self.graph_layout_label.hide()
            self.graph_layout_combo.hide()
            self.build_graph_btn.hide()
        
        # 4. Скрываем настройки хэш-таблицы
        self.hashtable_settings_label.hide()
        self.hash_function_label.hide()
        self.hash_function_combo.hide()
        self.collision_method_label.hide()
        self.collision_method_combo.hide()
        self.table_size_label.hide()
        self.table_size_slider.hide()
        self.table_size_value.hide()
        self.view_chains_btn.hide()
        
        # 5. Очищаем сцену
        self.scene.clear()
        
        # 6. Даем время на очистку
        QApplication.processEvents()
        
        # 7. Очищаем интерактивную панель
        self._clear_interactive_panel()
        
        # 8. Инициализируем список алгоритмов
        self._initialize_algorithm_combo()
        
        # 9. Показываем только нужные виджеты для текущей категории
        if category == "Хэш-таблицы":
            self.hashtable_settings_label.show()
            self.hash_function_label.show()
            self.hash_function_combo.show()
            self.collision_method_label.show()
            self.collision_method_combo.show()
            self.table_size_label.show()
            self.table_size_slider.show()
            self.table_size_value.show()
            self.view_chains_btn.show()
        
        # 10. Обновляем интерактивную панель
        if category == "Деревья":
            QTimer.singleShot(100, self._create_tree_interactive_panel)
        elif category == "Структуры данных":
            QTimer.singleShot(100, self._create_container_panel_for_current_algo)
        elif category == "Графы":
            QTimer.singleShot(100, self._create_graph_interactive_panel)
        elif category == "Сжатие данных":
            QTimer.singleShot(100, self._create_huffman_interactive_panel)
        elif category == "Сортировки":
            # После завершения сортировки показываем панель поиска
            if hasattr(self, 'algorithm_completed') and self.algorithm_completed:
                QTimer.singleShot(100, self._create_search_panel)
        else:
            self._clear_interactive_panel()
        
        # 11. Сбрасываем алгоритм при смене категории
        self._reset_algorithm()
        
        # 12. Для структур данных показываем сообщение
        if category == "Структуры данных":
            self._log("📦 Выберите структуру данных для интерактивных операций")
        elif category == "Графы":
            self._log("🕸️ Постройте граф, затем выберите алгоритм в правой панели")
        elif category == "Сжатие данных":
            self._log("🔤 Выберите алгоритм сжатия данных")

    def _create_container_panel_for_current_algo(self):
        """Создает панель для текущего алгоритма контейнера."""
        algo_name = self.algorithm_combo.currentText()
        if algo_name == "Stack":
            self._create_container_interactive_panel("stack")
            # Инициализируем контейнер сразу
            self.current_algorithm = Stack([])
            self.container_type = "stack"
            self.container_visualizer = ContainerVisualizer(self.scene, "stack")
            # Очищаем сцену и создаем интерфейс
            self.scene.clear()
            self.container_visualizer._create_interface()
            self._log("📚 Стек создан. Используйте интерактивные операции справа.")
        elif algo_name == "Queue":
            self._create_container_interactive_panel("queue")
            self.current_algorithm = Queue([])
            self.container_type = "queue"
            self.container_visualizer = ContainerVisualizer(self.scene, "queue")
            self.scene.clear()
            self.container_visualizer._create_interface()
            self._log("📥 Очередь создана. Используйте интерактивные операции справа.")
        elif algo_name == "Deque":
            self._create_container_interactive_panel("deque")
            self.current_algorithm = Deque([])
            self.container_type = "deque"
            self.container_visualizer = ContainerVisualizer(self.scene, "deque")
            self.scene.clear()
            self.container_visualizer._create_interface()
            self._log("🔄 Дек создан. Используйте интерактивные операции справа.")


    def _start_auto_mode(self):
        """Запуск автоматического режима."""
        category = self.category_combo.currentText()
        
        # === ИСПРАВЛЕНИЕ: Для графов РАЗРЕШАЕМ выполнение ===
        if category == "Структуры данных":
            self._log("ℹ️ Для структур данных используйте интерактивные операции справа")
            return
        # Для графов и других категорий - разрешаем
        
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
        category = self.category_combo.currentText()
        
        # Проверяем, что алгоритм загружен
        if self.algorithm_completed or not self.current_algorithm:
            # === ВАЖНО: Для бинарного поиска НЕ вызываем _start_algorithm() ===
            # _start_algorithm() перезаписывает данные из поля ввода
            if hasattr(self.current_algorithm, '__class__') and self.current_algorithm.__class__.__name__ == "BinarySearch":
                # Для бинарного поиска просто продолжаем выполнение
                if self.current_algorithm and not self.is_animating:
                    success = self.engine.step()
                    if not success:
                        self._log("❌ Алгоритм завершен или произошла ошибка")
                        self.algorithm_completed = True
                return
            else:
                # Для других алгоритмов вызываем стандартную инициализацию
                if not self._start_algorithm():
                    return
        
        # Продолжаем выполнение
        if not self.is_animating:
            success = self.engine.step()
            if not success:
                self._log("❌ Алгоритм завершен или произошла ошибка")
                self.algorithm_completed = True

    def _reset_algorithm(self):
        """Сброс текущего алгоритма и интерфейса."""
        try:
            
            # 1. Останавливаем движок и таймеры
            self.engine.pause()
            self.engine.generator = None
            
            # Останавливаем интерактивный поиск
            self._search_generator = None
            self._search_value = None
            
            # Останавливаем таймеры анимации
            self.hashtable_animation_timer.stop()
            if self.zoom_reset_timer.isActive():
                self.zoom_reset_timer.stop()
            
            # Получаем текущую категорию
            category = self.category_combo.currentText()
            
            # 2. Очищаем контейнеры ПЕРЕД очисткой сцены
            if hasattr(self, 'container_visualizer') and self.container_visualizer:
                try:
                    self.container_visualizer.clear()
                except Exception as e:
                    print(f"Warning clearing container visualizer: {e}")
                self.container_visualizer = None
                self.container_type = None
            
            # 3. Очищаем визуализаторы графов ПЕРЕД очисткой сцены
            # Для графов НЕ очищаем визуализатор полностью, только сбрасываем подсветку
            if category == "Графы":
                if hasattr(self, 'graph_visualizer'):
                    try:
                        self.graph_visualizer.reset_highlights()  # Только сброс подсветки
                    except Exception as e:
                        print(f"Warning resetting graph visualizer highlights: {e}")
            else:
                if hasattr(self, 'graph_visualizer'):
                    try:
                        self.graph_visualizer.clear()  # Для не-графов очищаем полностью
                    except Exception as e:
                        print(f"Warning clearing graph visualizer: {e}")
            
            # 4. Очищаем визуализатор деревьев
            if hasattr(self, 'tree_visualizer'):
                try:
                    self.tree_visualizer.clear()
                except Exception as e:
                    print(f"Warning clearing tree visualizer: {e}")
            
            # 5. Теперь очищаем сцену (кроме графов)
            if category != "Графы":
                if hasattr(self, 'scene'):
                    self.scene.clear()
            
            # 6. Скрываем специфичные виджеты
            self.temp_arrays_widget.hide()
            self.temp_arrays_widget.clear()
            
            # 7. Сброс состояния хэш-таблицы
            self.hashtable_cells = []
            self.hashtable_stats = {}
            self.hashtable_display_mode = "initial"
            self.hashtable_scroll_enabled = False
            self.current_hashtable_data = []
            
            # 8. Сброс других состояний
            self.current_algorithm = None
            self.is_auto_mode = False
            self.is_animating = False
            self.algorithm_completed = False
            self.pending_actions.clear()
            self.current_step = 0
            self.total_steps = 0
            
            # Сброс системы цветов
            self.current_highlight.clear()
            self.last_operation = None
            
            self._pending_tree_data = []
            self._last_tree_data = None
            self._temp_array_items = []
            self._split_lines = []
            self.animation_queue = []
            
            # 9. Отключаем кнопку просмотра цепочек
            self.view_chains_btn.setEnabled(False)
            
            # 10. Восстанавливаем кнопки
            self.auto_btn.show()
            self.pause_btn.hide()
            self.start_btn.setEnabled(True)
            
            # 11. Восстанавливаем начальный вид
            if category == "Структуры данных":
                # Для структур данных просто очищаем сцену
                self._log("📦 Контейнер сброшен")
            elif category == "Хэш-таблицы":
                # Для хэш-таблицы показываем начальный вид
                text = self.data_input.text()
                try:
                    arr = [int(x.strip()) for x in text.split(",") if x.strip()]
                    self._render_hashtable_initial_view(arr)
                except ValueError:
                    pass
            elif category == "Графы":
                # Для графов НЕ перестраиваем граф, только сбрасываем подсветку
                if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                    self._log("♻ Подсветка графа сброшена")
                else:
                    # Если граф не был визуализирован, пытаемся построить
                    if self.graph_data:
                        self._build_graph(skip_log=True)
                    else:
                        self._log("🕸️ Граф еще не построен")
            else:
                # Для всех остальных - массив
                text = self.data_input.text()
                try:
                    arr = [int(x.strip()) for x in text.split(",") if x.strip()]
                    self._render_array(arr)
                except ValueError:
                    if hasattr(self, 'current_data'):
                        self._render_array(self.current_data)
            
            # 12. Обновляем сцену и вид
            if hasattr(self, 'scene'):
                self.scene.update()
            if hasattr(self, 'view'):
                self.view.update()
            
            self._log("♻ Алгоритм сброшен. Можно запустить заново.")
            
            # 13. Планируем сброс зума (только если не графы или граф пустой)
            if category != "Графы" or not self.graph_data:
                self._schedule_zoom_reset()
            
        except Exception as e:
            print(f"Error resetting algorithm: {e}")
            import traceback
            traceback.print_exc()

    def _generate_random_data(self):
        """Генерация случайных данных с анимацией."""
        category = self.category_combo.currentText()
        
        if category == "Структуры данных":
            # Для структур данных просто очищаем
            self._log("🎲 Для структур данных используйте интерактивные операции справа")
            
        else:
            # Для остальных категорий - случайные числа
            count = random.randint(6, 12)
            data = [random.randint(10, 99) for _ in range(count)]
            self.data_input.setText(",".join(map(str, data)))
            
            self.current_data = data.copy()
            
            # Рендерим в зависимости от выбранной категории
            if category == "Хэш-таблицы":
                self._render_hashtable_initial_view(data)
            elif category == "Графы":
                # Для графов просто обновляем поле ввода
                self._log(f"🎲 Сгенерированы {count} случайных чисел для графа")
            else:
                self._render_array(data)
                self._log(f"🎲 Сгенерированы {count} случайных чисел")
        
        self._reset_algorithm()
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
        
        algo_name = self.algorithm_combo.currentText()
        category = self.category_combo.currentText()
        
        if category == "Структуры данных":
            # Для структур данных создаем пустую структуру
            if algo_name == "Stack":
                self.current_algorithm = Stack([])
                self.container_type = "stack"
            elif algo_name == "Queue":
                self.current_algorithm = Queue([])
                self.container_type = "queue"
            elif algo_name == "Deque":
                self.current_algorithm = Deque([])
                self.container_type = "deque"
            else:
                self._log(f"❌ Алгоритм '{algo_name}' не найден")
                return False
            
            # Инициализируем визуализатор
            self.container_visualizer = ContainerVisualizer(self.scene, self.container_type)
            
            # Загружаем в движок (но не запускаем генератор)
            # Для структур данных НЕ используем Engine
            self.engine.pause()
            self.engine.generator = None
            
            # Показываем начальный вид
            self._render_container_initial_view()
            
            # Включаем интерактивную панель
            self._create_container_interactive_panel(self.container_type)
            
            self._log(f"📦 {algo_name} создан. Используйте интерактивные операции справа.")
            return False  # Возвращаем False, так как для контейнеров не нужен запуск через Engine
        
        elif category == "Графы":
            # === ИСПРАВЛЕННЫЙ БЛОК ДЛЯ ГРАФОВ ===
            # Для графов проверяем, что граф построен
            if not self.graph_data:
                self._log("❌ Сначала постройте граф")
                QMessageBox.warning(self, "Ошибка", "Сначала постройте граф (нажмите 'Построить граф')")
                return False
            self._reset_graph_visualization()
            # ИСПРАВЛЕНИЕ: Всегда используем узел из поля ввода
            start_node_text = ""
            if hasattr(self, 'graph_start_input') and self.graph_start_input:
                start_node_text = self.graph_start_input.text().strip()
            
            # Если поле пустое, показываем ошибку
            if not start_node_text:
                QMessageBox.warning(self, "Ошибка", "Введите начальный узел в поле 'Начальный узел'")
                return False
            
            try:
                start_node = int(start_node_text)
                if start_node not in self.graph_data:
                    self._log(f"❌ Узел {start_node} не найден в графе")
                    QMessageBox.warning(self, "Ошибка", f"Узел {start_node} не найден в графе")
                    return False
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректный номер узла")
                return False
            
            # Определяем, какой алгоритм был выбран в правой панели
            algorithm_text = ""
            if hasattr(self, 'graph_algo_combo') and self.graph_algo_combo:
                algorithm_text = self.graph_algo_combo.currentText()
            
            # ИСПРАВЛЕНИЕ: Используем СУЩЕСТВУЮЩИЙ graph_data БЕЗ копирования
            if "BFS" in algorithm_text:
                self.current_algorithm = GraphBFS(self.graph_data, start_node)  # НЕ копируем!
            elif "DFS" in algorithm_text:
                self.current_algorithm = GraphDFS(self.graph_data, start_node)   # НЕ копируем!
            elif "Dijkstra" in algorithm_text:
                self.current_algorithm = Dijkstra(self.graph_data, start_node)   # НЕ копируем!
            else:
                # По умолчанию используем BFS
                self.current_algorithm = GraphBFS(self.graph_data, start_node)   # НЕ копируем!
            
            # Загружаем алгоритм в движок
            self.engine.load_algorithm(self.current_algorithm)
            
            # Сбрасываем подсветку графа перед запуском (только цвета, не структуру)
            self._reset_graph_visualization()
            
            self._log(f"🚀 Алгоритм загружен. Начальный узел: {start_node}")
            return True
        elif category == "Сжатие данных" and algo_name == "Huffman Coding":
            if hasattr(self, 'huffman_text_input'):
                text = self.huffman_text_input.toPlainText().strip()
            else:
                text = self.data_input.text().strip()
            
            if not text:
                QMessageBox.warning(self, "Ошибка", "Введите текст для кодирования Хаффмана")
                return False
            
            self.huffman_current_text = text
            self.current_algorithm = HuffmanCoding(text)
            
            # Загружаем алгоритм в движок
            self.engine.load_algorithm(self.current_algorithm)
            
            # Показываем начальный вид - частоты символов
            self.current_algorithm.calculate_frequencies()
            self.huffman_visualizer.visualize_frequencies(self.current_algorithm.frequencies)
            
            self._log(f"🔤 Алгоритм Хаффмана загружен. Текст: {text[:50]}...")
            return True 
        else:
            # Оригинальная логика для других категорий
            text = self.data_input.text()
            try:
                arr = [int(x.strip()) for x in text.split(",") if x.strip()]
                if len(arr) < 1:
                    QMessageBox.warning(self, "Ошибка", "Введите хотя бы 1 число")
                    return False
                
                self.current_data = arr.copy()
                
                if algo_name in ["BFS", "DFS", "Dijkstra"]:
                    graph_data = self._create_tree_graph(arr, directed=self.graph_directed)
                else:
                    graph_data = None

                if algo_name == "Heap":
                    # Для кучи создаем отдельный экземпляр с поддержкой генератора
                    heap_type = 'max'  # или можно добавить выбор типа в интерфейсе
                    self.current_algorithm = BinaryHeap(arr.copy(), heap_type=heap_type)
                    
                    # Загружаем в движок
                    self.engine.load_algorithm(self.current_algorithm)
                    QTimer.singleShot(100, lambda: self._update_heap_visualization("Куча создана"))
                    # Отображаем начальное состояние
                    heap_structure = self.current_algorithm._get_tree_structure()
                    if heap_structure:
                        self._render_tree(heap_structure)
                    
                    self._log(f"🔧 Куча ({heap_type}-heap) загружена. Готов к выполнению.")
                    return True
                
                algorithms = {
                    "QuickSort": lambda: QuickSort(arr.copy()),
                    "MergeSort": lambda: MergeSort(arr.copy()),
                    "BubbleSort": lambda: BubbleSort(arr.copy()),
                    "InsertionSort": lambda: InsertionSort(arr.copy()),  
                    "SelectionSort": lambda: SelectionSort(arr.copy()),  
                    "ShellSort": lambda: ShellSort(arr.copy()),   
                    "BST": lambda: BST(arr.copy()),
                    "AVL": lambda: AVLTree(arr.copy()),
                    "RedBlackTree": lambda: RedBlackTree(arr.copy()),
                    "SplayTree": lambda: SplayTree(arr.copy()),
                    "Treap": lambda: Treap(arr.copy()),
                    "BTree": lambda: BTree(arr.copy()),
                    "Heap": lambda: BinaryHeap(arr.copy(), heap_type='max'),
                    "HashTable": lambda: self._create_hashtable(arr.copy())
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
                        
                        # Обработка для разных типов алгоритмов
                        if algo_name == "HashTable":
                            # Для хэш-таблицы отображаем начальный вид
                            self._render_hashtable_initial_view(arr)
                            self._log(f"🔑 Подготовка хэш-таблицы с параметрами: " +
                                    f"размер={self.table_size_slider.value()}, " +
                                    f"функция={self.hash_function_combo.currentText()}, " +
                                    f"метод={self.collision_method_combo.currentText()}")
                            
                            # Включаем кнопку просмотра цепочек после завершения
                            self.view_chains_btn.setEnabled(True)
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

    def _create_hashtable(self, data):
        """Создает хэш-таблицу с выбранными параметрами"""
        # Преобразуем выбранные настройки
        hash_function_map = {
            "Деления": "division",
            "Умножения": "multiplication",
            "Простая": "simple"
        }
        
        collision_method_map = {
            "Линейное пробирование": "linear",
            "Квадратичное пробирование": "quadratic",
            "Двойное хеширование": "double",
            "Метод цепочек": "chaining"
        }
        
        hash_func = hash_function_map.get(
            self.hash_function_combo.currentText(), 
            "division"
        )
        
        collision_method = collision_method_map.get(
            self.collision_method_combo.currentText(),
            "linear"
        )
        
        table_size = self.table_size_slider.value()
        
        return HashTable(data, size=table_size, 
                        hash_function=hash_func, 
                        collision_method=collision_method)
    def _build_graph(self, skip_log=False):
        """Строит граф из введенных данных."""
        try:
            text = self.data_input.text()
            if not text:
                if not skip_log:
                    QMessageBox.warning(self, "Ошибка", "Введите данные для построения графа")
                return
            
            try:
                arr = [int(x.strip()) for x in text.split(",") if x.strip()]
                if len(arr) < 1:
                    if not skip_log:
                        QMessageBox.warning(self, "Ошибка", "Введите хотя бы 1 число")
                    return
                
                # Сохраняем данные
                self.current_data = arr.copy()
                
                # Создаем граф из данных
                graph_data = self._create_tree_graph(arr, directed=self.graph_directed)
                self.graph_data = graph_data
                
                # Получаем настройки компоновки
                layout_name = self.graph_layout_combo.currentText()
                layout_map = {
                    "Пружинная": "Spring",
                    "Круговая": "Circular",
                    "Древовидная": "Tree"
                }
                
                # Устанавливаем компоновку
                if layout_name in layout_map:
                    selected_layout = layout_map[layout_name]
                    success = self.graph_visualizer.set_layout_algorithm(selected_layout)
                    if success:
                        self.graph_layout = selected_layout
                
                # Создаем граф в визуализаторе
                success = self.graph_visualizer.create_graph(
                    graph_data, 
                    is_directed=self.graph_directed
                )
                
                if success:
                    direction_text = "ориентированный" if self.graph_directed else "неориентированный"
                    if not skip_log:
                        self._log(f"🕸️ {direction_text} граф построен ({len(graph_data)} узлов, {self.graph_layout} компоновка)")
                        self._log("ℹ️ Выберите алгоритм в правой панели для выполнения")
                    
                    # ОБНОВЛЯЕМ поле начального узла ТОЛЬКО ЕСЛИ ОНО ПУСТОЕ
                    if arr and (not hasattr(self, 'graph_start_input') or not self.graph_start_input.text().strip()):
                        self.graph_start_input.setText(str(arr[0]))
                        
                else:
                    if not skip_log:
                        self._log("❌ Ошибка при построении графа")
                        
            except ValueError:
                if not skip_log:
                    QMessageBox.warning(self, "Ошибка", "Вводите только числа через запятую")
                    
        except Exception as e:
            if not skip_log:
                self._log(f"❌ Ошибка при построении графа: {str(e)}")
            import traceback
            traceback.print_exc()

    def _create_tree_graph(self, arr, weight_mode="diff", min_weight=1, max_weight=10, directed=False):
        """Создает древовидный граф."""
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

        return graph

    def _on_graph_algorithm_execute(self):
        """Выполнение выбранного алгоритма на графе."""
        try:
            # Проверяем, что граф построен
            if not self.graph_data:
                self._log("❌ Сначала постройте граф")
                QMessageBox.warning(self, "Ошибка", "Сначала постройте граф")
                return
            
            # Устанавливаем начальный узел ИЗ ПОЛЯ ВВОДА
            start_node_text = self.graph_start_input.text().strip()
            if not start_node_text:
                self._log("❌ Введите начальный узел")
                QMessageBox.warning(self, "Ошибка", "Введите начальный узел в поле 'Начальный узел'")
                return
            
            try:
                start_node = int(start_node_text)
                if start_node not in self.graph_data:
                    self._log(f"❌ Узел {start_node} не найден в графе")
                    QMessageBox.warning(self, "Ошибка", f"Узел {start_node} не найден в графе")
                    return
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректный номер узла")
                return
            
            # Сбрасываем текущий алгоритм ПЕРЕД запуском нового
            self.engine.pause()
            self.engine.generator = None
            self.current_algorithm = None
            self.is_auto_mode = False
            self.algorithm_completed = False
            
            # Сбрасываем подсветку перед запуском
            self._reset_graph_visualization()
            
            # Определяем, какой алгоритм был выбран в правой панели
            algorithm_text = ""
            if hasattr(self, 'graph_algo_combo') and self.graph_algo_combo:
                algorithm_text = self.graph_algo_combo.currentText()
            
            # ИСПРАВЛЕНИЕ: Используем СУЩЕСТВУЮЩИЙ graph_data с указанным стартовым узлом
            if "BFS" in algorithm_text:
                self.current_algorithm = GraphBFS(self.graph_data, start_node)
            elif "DFS" in algorithm_text:
                self.current_algorithm = GraphDFS(self.graph_data, start_node)
            elif "Dijkstra" in algorithm_text:
                self.current_algorithm = Dijkstra(self.graph_data, start_node)
            else:
                # По умолчанию используем BFS
                self.current_algorithm = GraphBFS(self.graph_data, start_node)
            
            # Загружаем алгоритм в движок
            self.engine.load_algorithm(self.current_algorithm)
            
            self._log(f"🚀 Алгоритм загружен. Начальный узел: {start_node}")
            
            # Запускаем алгоритм через стандартный механизм
            if self._start_algorithm():
                # Запускаем автоматический режим
                self._start_auto_mode()
            else:
                self._log("❌ Не удалось запустить алгоритм")
                
        except Exception as e:
            self._log(f"❌ Ошибка при выполнении алгоритма: {str(e)}")
            import traceback
            traceback.print_exc()
    def _reset_graph_visualization(self):
        """Сбрасывает визуализацию графа перед новым алгоритмом."""
        try:
            if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                # ТОЛЬКО сбрасываем стили, НЕ перестраиваем граф
                self.graph_visualizer.reset_highlights()
                
                # Сбрасываем стили всех узлов
                for node_item in self.graph_visualizer.nodes.values():
                    if hasattr(node_item, 'reset_style'):
                        node_item.reset_style()
                    else:
                        # Если нет reset_style, просто сбрасываем цвет
                        node_item.setBrush(QBrush(QColor("#FFFFFF")))
                        node_item.setPen(QPen(QColor("#000000"), 1))
                
                # Сбрасываем стили всех ребер
                for edge_item in self.graph_visualizer.edges.values():
                    if hasattr(edge_item, 'reset_style'):
                        edge_item.reset_style()
                    else:
                        # Если нет reset_style, просто сбрасываем цвет
                        edge_item.setPen(QPen(QColor("#000000"), 1))
                
                # Очищаем все временные метки (веса, расстояния)
                for item in list(self.scene.items()):
                    if isinstance(item, QGraphicsTextItem) and "distance" in item.toPlainText().lower():
                        self.scene.removeItem(item)
                
                self._log("♻ Подсветка графа сброшена. Граф готов для нового алгоритма.")
            else:
                self._log("ℹ️ Граф еще не построен")
        except Exception as e:
            self._log(f"❌ Ошибка при сбросе визуализации графа: {str(e)}")


    def _reset_graph_algorithm(self):
        """Сбрасывает текущий алгоритм графа, но сохраняет граф."""
        try:
            self.engine.pause()
            self.engine.generator = None
            self.current_algorithm = None  # Сбрасываем только алгоритм
            self.is_auto_mode = False
            self.algorithm_completed = False
            
            # Сбрасываем подсветку графа
            if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                self.graph_visualizer.reset_highlights()
            
            # Восстанавливаем кнопки
            self.auto_btn.show()
            self.pause_btn.hide()
            self.start_btn.setEnabled(True)
            
            # ВАЖНО: НЕ перестраиваем граф, только сбрасываем стили
            if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                # Сбрасываем стили узлов и ребер
                for node_item in self.graph_visualizer.nodes.values():
                    if hasattr(node_item, 'reset_style'):
                        node_item.reset_style()
                
                for edge_item in self.graph_visualizer.edges.values():
                    if hasattr(edge_item, 'reset_style'):
                        edge_item.reset_style()
                
                self._log("♻ Алгоритм графа сброшен. Граф готов для нового алгоритма.")
            else:
                self._log("♻ Алгоритм графа сброшен.")
                
        except Exception as e:
            self._log(f"❌ Ошибка при сбросе алгоритма графа: {str(e)}")

    def _clear_graph(self):
        """Очищает граф."""
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите очистить граф?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.graph_data = None
                self.graph_visualizer.clear()
                self.current_algorithm = None
                
                self._log("🗑️ Граф очищен")
                
                # Сбрасываем интерфейс
                self._reset_algorithm()
                
            except Exception as e:
                self._log(f"❌ Ошибка при очистке графа: {str(e)}")
    def _create_table_header(self, start_x, start_y, width, height):
        """Создает заголовок таблицы."""
        index_width = 100
        value_width = width - index_width
        
        # Фон шапки Индекс
        header_idx = QGraphicsRectItem(start_x, start_y, index_width, height)
        header_idx.setBrush(QBrush(QColor("#2c3e50")))
        header_idx.setPen(QPen(QColor("#ffffff"), 2))
        self.scene.addItem(header_idx)
        
        text_idx = QGraphicsTextItem("INDEX")
        text_idx.setDefaultTextColor(Qt.GlobalColor.white)
        text_idx.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        text_idx.setPos(start_x + 20, start_y + 15)
        self.scene.addItem(text_idx)
        
        # Фон шапки Значение
        header_val = QGraphicsRectItem(start_x + index_width, start_y, value_width, height)
        header_val.setBrush(QBrush(QColor("#34495e")))
        header_val.setPen(QPen(QColor("#ffffff"), 2))
        self.scene.addItem(header_val)
        
        text_val = QGraphicsTextItem("VALUE")
        text_val.setDefaultTextColor(Qt.GlobalColor.white)
        text_val.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        text_val.setPos(start_x + index_width + 110, start_y + 15)
        self.scene.addItem(text_val)

    def _render_hashtable_structure(self, table_size, y_offset=0):
        """Отображает структуру хэш-таблицы как ВЕРТИКАЛЬНУЮ таблицу."""
        # Очищаем старые ячейки
        self.hashtable_cells.clear()
        
        # Параметры верстки
        cell_width = 400  # Общая ширина ячейки (индекс + значение)
        cell_height = 60
        start_x = -150
        start_y = y_offset + 50
        
        # Создаем заголовок таблицы
        self._create_table_header(start_x, start_y - cell_height, cell_width, cell_height)
        
        # Создаем ячейки таблицы
        for i in range(table_size):
            current_y = start_y + i * cell_height
            
            cell = HashTableCell(
                start_x, 
                current_y,
                cell_width, 
                cell_height,
                i
            )
            self.scene.addItem(cell)
            self.hashtable_cells.append(cell)
        
        # Устанавливаем размер сцены
        total_height = table_size * cell_height + 200
        self.scene.setSceneRect(-300, -200, 800, total_height)

    def _render_hashtable_initial_view(self, arr):
        """Отображает начальный вид для хэш-таблицы."""
        self.scene.clear()
        self.hashtable_cells = []
        self.hashtable_display_mode = "initial"
        
        table_size = self.table_size_slider.value()
        
        # Отображаем заголовок
        title = self.scene.addText(f"Хэш-таблица")
        title.setPos(-200, -150)
        title.setDefaultTextColor(QColor("#2c3e50"))
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        
        # Отображаем параметры таблицы
        params_text = self.scene.addText(
            f"Размер: {table_size} | {self.hash_function_combo.currentText()} | {self.collision_method_combo.currentText()}"
        )
        params_text.setPos(-200, -90)
        params_text.setDefaultTextColor(QColor("#5A9BD5"))
        params_text.setFont(QFont("Arial", 14))
        
        # Отображаем пустую таблицу
        self._render_hashtable_structure(table_size, y_offset=0)
        
        # Сразу подстраиваем зум
        if hasattr(self.view, 'fit_to_content'):
            self.view.fit_to_content(100)

    def _render_hashtable_content(self, table_data, collisions=0, max_chain_length=0):
        """Обновляет содержимое ячеек хэш-таблицы."""
        if not self.hashtable_cells:
            return
            
        # Сохраняем текущие данные таблицы
        self.current_hashtable_data = table_data.copy()
            
        # Удаляем старую текстовую статистику (если есть)
        items_to_remove = [item for item in self.scene.items() 
                          if isinstance(item, QGraphicsTextItem) and item.pos().y() > self.hashtable_cells[-1].y() + 50]
        for item in items_to_remove:
            self.scene.removeItem(item)
            
        # Обновляем каждую ячейку
        for i, cell in enumerate(self.hashtable_cells):
            if i < len(table_data):
                value = table_data[i]
                
                if value is not None:
                    if isinstance(value, list):  # Метод цепочек
                        if value:
                            cell.set_value(value[0], len(value), value)
                        else:
                            cell.set_value(None, 0)
                    else:  # Одиночное значение
                        cell.set_value(value, 1, [value])
                else:
                    cell.set_value(None)
        
        # Отображаем статистику снизу таблицы
        if self.hashtable_cells:
            last_cell = self.hashtable_cells[-1]
            stats_y = last_cell.y() + 80
            
            stats_text = self.scene.addText(
                f"Статистика:\n"
                f"• Коллизий: {collisions}\n"
                f"• Макс. длина цепочки: {max_chain_length}\n"
                f"• Заполнение: {sum(1 for x in table_data if x is not None)}/{len(table_data)}"
            )
            stats_text.setPos(last_cell.x() - 50, stats_y)
            stats_text.setDefaultTextColor(QColor("#2c3e50"))
            stats_text.setFont(QFont("Arial", 14))

    def _render_completed_hashtable(self, action):
        """Полностью перестраивает сцену с завершенной хэш-таблицей."""
        self.scene.clear()
        self.hashtable_cells = []
        self.hashtable_display_mode = "completed"
        
        table_size = action.get("table_size", self.table_size_slider.value())
        table_data = action.get("table", [])
        
        # Сохраняем данные таблицы для просмотра цепочек
        self.current_hashtable_data = table_data.copy()
        
        # Параметры верстки
        cell_width = 400
        cell_height = 60
        start_x = -150
        start_y = 50
        
        # --- ЗАГОЛОВОК ---
        title = self.scene.addText(f"✅ Хэш-таблица построена")
        title.setPos(-200, -150)
        title.setDefaultTextColor(QColor("#2c3e50"))
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        
        # Параметры таблицы
        params_text = self.scene.addText(
            f"Размер: {table_size} | {self.hash_function_combo.currentText()} | {self.collision_method_combo.currentText()}"
        )
        params_text.setPos(-200, -90)
        params_text.setDefaultTextColor(QColor("#5A9BD5"))
        params_text.setFont(QFont("Arial", 14))
        
        # Создаем заголовок таблицы
        self._create_table_header(start_x, start_y - cell_height, cell_width, cell_height)
        
        # --- СТРОКИ ТАБЛИЦЫ С ДАННЫМИ ---
        for i in range(table_size):
            current_y = start_y + i * cell_height
            
            # Получаем значение для текущей ячейки
            value = None
            if i < len(table_data):
                value = table_data[i]
            
            # Инициализируем параметры для ячейки
            display_value = None
            chain_length = 0
            full_chain = []
            
            # Обрабатываем значение в зависимости от типа
            if value is not None:
                if isinstance(value, list):  # Метод цепочек
                    if value:  # Не пустой список
                        display_value = value[0]
                        chain_length = len(value)
                        full_chain = value
                    else:  # Пустой список
                        display_value = None
                        chain_length = 0
                        full_chain = []
                else:  # Одиночное значение (не список)
                    display_value = value
                    chain_length = 1
                    full_chain = [value]
            
            # Создаем ячейку с данными
            cell = HashTableCell(
                start_x, 
                current_y,
                cell_width, 
                cell_height,
                i,  # index
                display_value,  # value
                chain_length,  # chain_length
                False,  # is_probing
                full_chain  # full_chain
            )
            
            self.scene.addItem(cell)
            self.hashtable_cells.append(cell)
        
        # --- СТАТИСТИКА СПРАВА ---
        stats_x = start_x + cell_width + 50
        stats_y = start_y - 50
        
        # Вычисляем статистику
        filled_cells = action.get('filled_cells', 0)
        collisions = action.get('collisions', 0)
        max_chain_length = action.get('max_chain_length', 0)
        load_factor = action.get('load_factor', 0)
        
        # Создаем текст статистики
        stats_text = (
            f"📊 Итоговая статистика:\n\n"
            f"• Всего ключей: {len(self.current_data)}\n"
            f"• Размер таблицы: {table_size}\n"
            f"• Заполнено ячеек: {filled_cells}\n"
            f"• Коллизий: {collisions}\n"
            f"• Коэффициент заполнения: {load_factor:.2f}\n"
            f"• Макс. длина цепочки: {max_chain_length}\n"
            f"• Функция хеширования: {self.hash_function_combo.currentText()}\n"
            f"• Метод разрешения коллизий: {self.collision_method_combo.currentText()}"
        )
        
        stats_item = self.scene.addText(stats_text)
        stats_item.setPos(stats_x, stats_y)
        stats_item.setDefaultTextColor(QColor("#2c3e50"))
        stats_item.setFont(QFont("Arial", 11))
        
        # Устанавливаем правильный размер сцены
        total_height = table_size * cell_height + 200
        self.scene.setSceneRect(-300, -200, 1000, total_height)
        
        # Включаем интерактивность для всех ячеек
        for cell in self.hashtable_cells:
            cell.setAcceptHoverEvents(True)
            cell.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        
        # Включаем кнопку просмотра цепочек
        self.view_chains_btn.setEnabled(True)
        self._log("✅ Хэш-таблица построена. Нажмите кнопку '🔗 Просмотреть цепочки' для детального анализа.")

    def _create_tree_graph(self, arr, weight_mode="diff", min_weight=1, max_weight=10, directed=False):
        """Создает древовидный граф."""
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
        """Рендеринг дерева."""
        if self._is_rendering_tree:
            return
        self._is_rendering_tree = True
        
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
            
            # Проверяем, является ли это кучей
            is_heap = isinstance(self.current_algorithm, BinaryHeap) if self.current_algorithm else False
            
            # Отладочная информация
            #if is_heap:
                #self._log(f"📊 Получены данные кучи. Корень: {tree_data.get('value', 'N/A')}")
            #else:
                #elf._log(f"📊 Получены данные дерева: {tree_data}")
            
            # Используем визуализатор
            if is_heap:
                # Для кучи используем стандартное дерево
                root = self.tree_visualizer.create_tree_from_structure(tree_data, animate=False)
            else:
                root = self.tree_visualizer.create_tree_from_structure(tree_data, animate=False)
            
            if root:
                # Сразу центрируем без дополнительных задержек
                self._center_on_tree()
                
                if is_heap:
                    self._log("🌳 Куча построена и отображена")
                    # Добавляем специальную информацию для кучи
                    heap_type = "Max-Heap" if self.current_algorithm.type == 'max' else "Min-Heap"
                    heap_info = self.scene.addText(f"{heap_type}, Размер: {self.current_algorithm.get_size()}")
                    heap_info.setDefaultTextColor(QColor("#3498DB"))
                    heap_info.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                    heap_info.setPos(-200, -100)
                else:
                    self._log("🌳 Дерево построено и отображено")
                
                # Отображаем информацию о количестве узлов
                node_count = self._count_tree_nodes(tree_data)
                self._log(f"📊 Узлов в дереве: {node_count}")
            else:
                self._log("❌ Ошибка при построении дерева")
                
                # Отладочная информация: показываем сырые данные
                debug_text = f"Сырые данные: {json.dumps(tree_data, default=str)}"
                debug_item = self.scene.addText(debug_text)
                debug_item.setPos(-200, 0)
                debug_item.setDefaultTextColor(QColor("#FF6B6B"))
                    
        except Exception as e:
            self._log(f"❌ Ошибка при визуализации дерева: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self._is_rendering_tree = False


    def _count_tree_nodes(self, tree_structure, max_depth=1000):
        """Подсчитывает количество узлов в дереве с защитой от бесконечной рекурсии."""
        if not tree_structure or max_depth <= 0:
            return 0
        
        count = 1
        # Рекурсивно считаем левое поддерево
        if tree_structure.get("left"):
            count += self._count_tree_nodes(tree_structure["left"], max_depth - 1)
        
        # Рекурсивно считаем правое поддерево
        if tree_structure.get("right"):
            count += self._count_tree_nodes(tree_structure["right"], max_depth - 1)
        
        return count

    def _center_on_tree(self):
        """Центрирует вид на содержимом сцены с масштабированием."""
        if self.scene.items():
            if hasattr(self, 'view') and self.view:
                rect = self.scene.itemsBoundingRect()
                if rect.isValid():
                    rect.adjust(-100, -100, 100, 100)
                    self.view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
                    self.view.centerOn(rect.center())

    def _reset_all_colors(self, keep_sorted=False):
        """Сбрасывает все цвета к стандартному состоянию."""
        if not keep_sorted:
            # Полный сброс всех элементов
            for item in self.visual_items:
                item.reset_color()
            self.current_highlight.clear()
        else:
            # Сброс только не-отсортированных элементов
            for item in self.visual_items:
                if not hasattr(item, 'is_sorted') or not item.is_sorted:
                    item.reset_color()
                    
    def _highlight_items(self, indices, color_name, description="", keep_others=False):
        """Улучшенная подсветка элементов с управлением состояниями."""
        if not keep_others:
            # Сбрасываем предыдущую подсветку
            self._reset_all_colors(keep_sorted=True)
        
        # Получаем цвет из палитры
        color = self.color_palette.get(color_name, color_name)
        
        # Запоминаем текущую подсветку
        self.current_highlight = set(indices)
        self.last_operation = description
        
        # Подсвечиваем элементы
        for i in range(len(self.visual_items)):
            if i in indices:
                self.visual_items[i].highlight(color)
                
                # Добавляем анимацию для 1-3 элементов
                if len(indices) <= 3:
                    self.visual_items[i].bounce_animation()
            elif not keep_others:
                # Сбрасываем только если явно не требуется сохранить
                if hasattr(self.visual_items[i], 'is_sorted') and self.visual_items[i].is_sorted:
                    # Оставляем отсортированные элементы зелеными
                    self.visual_items[i].highlight(self.color_palette["sorted"])
                else:
                    self.visual_items[i].reset_color()
        
        # Логируем описание
        if description:
            self._log(description)
            
    def _mark_as_sorted(self, indices):
        """Помечает элементы как отсортированные."""
        for i in indices:
            if i < len(self.visual_items):
                self.visual_items[i].highlight(self.color_palette["sorted"])
                self.visual_items[i].is_sorted = True
                # Небольшая анимация для подтверждения
                self.visual_items[i].bounce_animation(scale_factor=1.1)
                
    def _mark_as_current(self, index):
        """Помечает элемент как текущий."""
        if index < len(self.visual_items):
            self.visual_items[index].highlight(self.color_palette["current"])
            self.visual_items[index].bounce_animation()

    def _process_action(self, action):
        """Обработка действия с улучшенной системой цветов."""
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
                # ВАЖНО: Добавить отрисовку дерева!
                self._render_tree(tree_data)
            
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
            node_index = action.get("node")
            # ПРОВЕРКА: если это граф, используем graph_visualizer
            if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                print(f"  Graph VISIT: {node_index}")
                success = self.graph_visualizer.process_action(action)
                if success:
                    # Логируем информацию о посещении
                    distance = action.get('distance', '')
                    desc = action.get('description', f'Посещен узел {node_index}')
                    if distance != '':
                        self._log(f"📍 {desc} (расстояние: {distance})")
                    else:
                        self._log(f"📍 {desc}")
            elif node_index < len(self.visual_items):
                # Это массив, а не граф
                self._mark_as_current(node_index)
                self._log(f"📍 Посещен элемент: {node_index}")
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "discover":
            from_node = action.get('from_node')
            to_node = action.get('node')
            # ПРОВЕРКА: если это граф, используем graph_visualizer
            if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                print(f"  Graph DISCOVER: {from_node} -> {to_node}")
                success = self.graph_visualizer.process_action(action)
                if success:
                    weight = action.get('weight', 1)
                    desc = action.get('description', f'Обнаружен узел {to_node}')
                    self._log(f"🔍 {desc}")
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "update_distance":
            node_index = action.get('node')
            new_distance = action.get('new_distance')
            old_distance = action.get('old_distance', '∞')
            # ПРОВЕРКА: если это граф, используем graph_visualizer
            if hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                print(f"  Graph UPDATE_DISTANCE: {node_index} ({old_distance} -> {new_distance})")
                success = self.graph_visualizer.process_action(action)
                if success:
                    self._log(f"📊 Обновлено расстояние до узла {node_index}: {old_distance} → {new_distance}")
            self._schedule_next_action(int(600 * speed_factor))
               # ==================== ОБРАБОТЧИКИ ДЛЯ АЛГОРИТМА ХАФФМАНА ====================
        elif t == "frequencies_calculated":
            frequencies = action.get("frequencies", {})
            self.huffman_visualizer.visualize_frequencies(frequencies)
            self._log(action.get("description", ""))
            self._schedule_next_action(int(800 * speed_factor))
            
        elif t == "initial_nodes":
            self._log(action.get("description", ""))
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "nodes_selected":
            self.huffman_visualizer.visualize_tree_building_step(action)
            self._log(action.get("description", ""))
            self._schedule_next_action(int(800 * speed_factor))
            
        elif t == "nodes_merged":
            self.huffman_visualizer.visualize_tree_building_step(action)
            self._log(action.get("description", ""))
            self._schedule_next_action(int(700 * speed_factor))
            
        elif t == "heap_updated":
            self.huffman_visualizer.visualize_tree_building_step(action)
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "tree_built":
            # Получаем и отображаем дерево
            if self.current_algorithm and hasattr(self.current_algorithm, 'get_tree_structure'):
                tree_structure = self.current_algorithm.get_tree_structure()
                if tree_structure:
                    self.huffman_visualizer.visualize_huffman_tree(tree_structure, self.tree_visualizer)
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(800 * speed_factor))
            
        elif t == "code_generation_start":
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "traverse_left":
            self._log(action.get("description", ""))
            self._schedule_next_action(int(400 * speed_factor))
            
        elif t == "traverse_right":
            self._log(action.get("description", ""))
            self._schedule_next_action(int(400 * speed_factor))
            
        elif t == "code_assigned":
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
        elif t == "codes_generated":
            # Отображаем таблицу кодов
            if self.current_algorithm and hasattr(self.current_algorithm, 'get_codes_table'):
                codes_table = self.current_algorithm.get_codes_table()
                self.huffman_visualizer.visualize_codes_table(codes_table)
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(1000 * speed_factor))
        
        elif t == "encoding_complete":
            # Отображаем результат кодирования
            if self.current_algorithm and hasattr(self.current_algorithm, 'get_compression_stats'):
                stats = self.current_algorithm.get_compression_stats()
                self.huffman_visualizer.visualize_encoding_result(stats)
                
                # Сохраняем таблицу кодов
                self.huffman_codes_table = self.current_algorithm.get_codes_table()
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(1000 * speed_factor))
            
        elif t == "decoding_complete":
            self._log(action.get("description", ""))
            self._schedule_next_action(int(600 * speed_factor))
        # binary
# В методе _process_action добавим полную обработку бинарного поиска:
        elif t.startswith("binary_search_"):
            if t == "binary_search_start":
                self._log(f"🔍 Начинаем бинарный поиск значения {action.get('target', '')}")
                self._schedule_next_action(int(500 * speed_factor))
                
            elif t == "binary_search_mid":
                left = action.get("left", 0)
                right = action.get("right", 0)
                mid = action.get("mid", 0)
                mid_value = action.get("mid_value", 0)
                
                # Подсвечиваем весь текущий диапазон
                indices = list(range(left, right + 1))
                self._highlight_items(indices, "comparing", action.get("description", ""), keep_others=True)
                
                # Особо выделяем средний элемент
                if mid < len(self.visual_items):
                    self.visual_items[mid].highlight(self.color_palette["pivot"])
                    self.visual_items[mid].bounce_animation()
                    # Показываем значение
                    self.visual_items[mid].show_value_label(f"mid={mid_value}")
                
                # Показываем границы
                if left < len(self.visual_items):
                    self.visual_items[left].highlight("#3498DB")  # Синий для левой границы
                    self.visual_items[left].show_value_label(f"L={left}")
                
                if right < len(self.visual_items):
                    self.visual_items[right].highlight("#3498DB")  # Синий для правой границы
                    self.visual_items[right].show_value_label(f"R={right}")
                
                self._schedule_next_action(int(800 * speed_factor))
                
            elif t == "binary_search_compare":
                mid = action.get("mid", 0)
                comparison = action.get("comparison", "")
                target = action.get("target", 0)
                
                # В зависимости от сравнения подсвечиваем по-разному
                if mid < len(self.visual_items):
                    if comparison == "equal":
                        self.visual_items[mid].highlight(self.color_palette["sorted"])
                        self.visual_items[mid].bounce_animation(scale_factor=1.2)
                        self.visual_items[mid].show_value_label(f"✓ Найден {target}!")
                    elif comparison == "less":
                        self.visual_items[mid].highlight("#FF6B6B")  # Красный - значение меньше
                        self.visual_items[mid].show_value_label(f"< {target}")
                    else:  # greater
                        self.visual_items[mid].highlight("#FFA500")  # Оранжевый - значение больше
                        self.visual_items[mid].show_value_label(f"> {target}")
                
                self._schedule_next_action(int(700 * speed_factor))
                
            elif t == "binary_search_narrow":
                left = action.get("left", 0)
                right = action.get("right", 0)
                direction = action.get("direction", "")
                
                # Сбрасываем подсветку элементов вне нового диапазона
                for i in range(len(self.visual_items)):
                    if i < left or i > right:
                        self.visual_items[i].reset_color()
                        self.visual_items[i].hide_value_label()
                
                # Показываем новый диапазон
                indices = list(range(left, right + 1))
                if direction == "right":
                    self._highlight_items(indices, "merge_right", f"Ищем в правой половине", keep_others=True)
                else:
                    self._highlight_items(indices, "merge_left", f"Ищем в левой половине", keep_others=True)
                
                self._log(action.get("description", ""))
                self._schedule_next_action(int(600 * speed_factor))
                
            elif t == "binary_search_not_found":
                self._log(f"❌ {action.get('description', '')}")
                # Сбрасываем все подсветки
                self._reset_all_colors()
                self._schedule_next_action(int(500 * speed_factor))
        # === ОБРАБОТЧИКИ ДЛЯ MERGESORT ===
        elif t == "split":
            left = action.get("left", 0)
            right = action.get("right", 0)
            mid = action.get("mid", 0)
            
            indices = list(range(left, right + 1))
            self._highlight_items(indices, "comparing", action.get("description", ""))
            
            self._draw_split_line(mid, left, right)
            
            self._schedule_next_action(int(1000 * speed_factor))
            
        elif t == "merge_start":
            left = action.get("left", 0)
            mid = action.get("mid", 0)
            right = action.get("right", 0)
            
            for i in range(left, mid + 1):
                if i < len(self.visual_items):
                    self.visual_items[i].highlight(self.color_palette["merge_left"])
            
            for i in range(mid + 1, right + 1):
                if i < len(self.visual_items):
                    self.visual_items[i].highlight(self.color_palette["merge_right"])
            
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
                self.visual_items[i].highlight(self.color_palette["comparing"])
                self.visual_items[i].bounce_animation()
            
            if j < len(self.visual_items):
                self.visual_items[j].highlight(self.color_palette["comparing"])
                self.visual_items[j].bounce_animation()
            
            if target_index < len(self.visual_items):
                self.visual_items[target_index].highlight(self.color_palette["merge_target"])
            
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
                color = self.color_palette["merge_left"] if is_from_left else self.color_palette["merge_right"]
                self.visual_items[from_idx].highlight(color)
                self.visual_items[to_idx].highlight(self.color_palette["merge_target"])
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
                self.visual_items[to_idx].highlight(self.color_palette["merge_target"])
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
                    self.visual_items[i].highlight(self.color_palette["sorted"])
                    if i == left or i == right:
                        self.visual_items[i].bounce_animation()
            
            # Очищаем виджет временных массивов
            self.temp_arrays_widget.clear()
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(800 * speed_factor))
            
        elif t == "base_case":
            index = action.get("index", 0)
            if index < len(self.visual_items):
                self.visual_items[index].highlight(self.color_palette["sorted"])
                self.visual_items[index].bounce_animation()
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        # === ОБРАБОТЧИКИ ДЛЯ INSERTION SORT ===
        elif t == "insertion_sorted_init":
            index = action.get("sorted_index", 0)
            if index < len(self.visual_items):
                self._mark_as_sorted([index])
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "insertion_start":
            key_index = action.get("key_index", 0)
            if key_index < len(self.visual_items):
                self.visual_items[key_index].highlight(self.color_palette["key"])
                self.visual_items[key_index].bounce_animation()
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "insertion_comparing_range":
            start_index = action.get("start_index", 0)
            key_index = action.get("key_index", 0)
            
            # Подсвечиваем диапазон для сравнения
            for i in range(start_index + 1):
                if i < len(self.visual_items):
                    self.visual_items[i].highlight(self.color_palette["current"])
            
            if key_index < len(self.visual_items):
                self.visual_items[key_index].highlight(self.color_palette["key"])
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "insertion_compare":
            current_idx = action.get("current_index", 0)
            key_idx = action.get("key_index", 0)
            
            if current_idx < len(self.visual_items):
                self.visual_items[current_idx].highlight(self.color_palette["comparing"])
                self.visual_items[current_idx].bounce_animation()
            
            if key_idx < len(self.visual_items):
                self.visual_items[key_idx].highlight(self.color_palette["key"])
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "insertion_shift":
            from_idx = action.get("from_index", 0)
            to_idx = action.get("to_index", 0)
            
            if from_idx < len(self.visual_items) and to_idx < len(self.visual_items):
                self.visual_items[to_idx].highlight(self.color_palette["shifted"])
                self.visual_items[to_idx].bounce_animation()
                self.visual_items[to_idx].update_value(action.get("shifted_value", 0))
                
                # Обновляем данные массива
                if to_idx < len(self.array_data):
                    self.array_data[to_idx] = action.get("shifted_value", 0)
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "insertion_next_comparison":
            next_idx = action.get("next_index", 0)
            
            if next_idx >= 0 and next_idx < len(self.visual_items):
                self.visual_items[next_idx].highlight(self.color_palette["current"])
                self.visual_items[next_idx].bounce_animation()
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(400 * speed_factor))
            
        elif t == "insertion_insert":
            from_idx = action.get("from_index", 0)
            to_idx = action.get("to_index", 0)
            value = action.get("value", 0)
            
            if to_idx < len(self.visual_items):
                self._mark_as_sorted([to_idx])
                self.visual_items[to_idx].update_value(value)
                
                # Обновляем данные массива
                if to_idx < len(self.array_data):
                    self.array_data[to_idx] = value
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "insertion_already_sorted":
            index = action.get("index", 0)
            
            if index < len(self.visual_items):
                self._mark_as_sorted([index])
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(400 * speed_factor))
            
        elif t == "insertion_sorted_part":
            sorted_indices = action.get("sorted_indices", [])
            new_idx = action.get("newly_sorted_index", 0)
            
            # Помечаем все отсортированные элементы
            self._mark_as_sorted(sorted_indices)
            
            if new_idx < len(self.visual_items):
                self.visual_items[new_idx].bounce_animation()
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(600 * speed_factor))
        
        # === ОБРАБОТЧИКИ ДЛЯ SELECTION SORT ===
        elif t == "selection_current":
            index = action.get("current_index", 0)
            
            if index < len(self.visual_items):
                self._mark_as_current(index)
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "selection_compare":
            indices = action.get("indices", (0, 0))
            min_idx = action.get("current_min_index", 0)
            compare_idx = indices[1]
            
            # Текущий минимум - бирюзовый
            if min_idx < len(self.visual_items):
                self.visual_items[min_idx].highlight(self.color_palette["selected"])
            
            # Сравниваемый элемент - оранжевый
            if compare_idx < len(self.visual_items):
                self.visual_items[compare_idx].highlight(self.color_palette["comparing"])
                self.visual_items[compare_idx].bounce_animation()
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "selection_new_min":
            new_idx = action.get("new_min_index", 0)
            
            if new_idx < len(self.visual_items):
                self.visual_items[new_idx].highlight(self.color_palette["selected"])
                self.visual_items[new_idx].bounce_animation()
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(400 * speed_factor))
            
        elif t == "selection_not_min":
            index = action.get("compared_index", 0)
            
            if index < len(self.visual_items):
                self.visual_items[index].highlight(self.color_palette["default"])
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(300 * speed_factor))
            
        elif t == "selection_pre_swap":
            indices = action.get("indices", (0, 0))
            
            for i in indices:
                if i < len(self.visual_items):
                    self.visual_items[i].highlight(self.color_palette["swapping"])
                    self.visual_items[i].bounce_animation()
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "selection_swap":
            indices = action.get("indices", (0, 0))
            
            # Подсвечиваем обмен
            self._highlight_items(list(indices), "swapping", "🔄 Обмен минимального элемента")
            
            # Выполняем обмен
            if len(indices) == 2:
                i, j = indices
                self._swap_items(i, j)
            
            # После обмена помечаем элемент как отсортированный
            if indices[0] < len(self.visual_items):
                self.visual_items[indices[0]].is_sorted = True
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(800 * speed_factor))
            
        elif t == "selection_already_sorted":
            index = action.get("index", 0)
            
            if index < len(self.visual_items):
                self._mark_as_sorted([index])
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(400 * speed_factor))
            
        elif t == "selection_sorted_part":
            sorted_indices = action.get("sorted_indices", [])
            
            # Помечаем все отсортированные элементы
            self._mark_as_sorted(sorted_indices)
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
        
        # === ОБРАБОТЧИКИ ДЛЯ SHELL SORT ===
        elif t == "shell_gap_start":
            gap = action.get("gap", 1)
            gap_idx = action.get("gap_index", 0)
            total_gaps = action.get("total_gaps", 1)
            
            # Подсвечиваем все элементы, чтобы показать начало нового этапа
            for i in range(len(self.visual_items)):
                self.visual_items[i].highlight(self.color_palette["default"])
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "shell_group_start":
            group_indices = action.get("group_indices", [])
            
            for idx in group_indices:
                if idx < len(self.visual_items):
                    self.visual_items[idx].highlight(self.color_palette["group"])
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "shell_current_element":
            element_idx = action.get("element_index", 0)
            
            if element_idx < len(self.visual_items):
                self.visual_items[element_idx].highlight(self.color_palette["key"])
                self.visual_items[element_idx].bounce_animation()
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(400 * speed_factor))
            
        elif t == "shell_compare":
            current_idx = action.get("current_index", 0)
            key_idx = action.get("key_index", 0)
            
            if current_idx < len(self.visual_items):
                self.visual_items[current_idx].highlight(self.color_palette["comparing"])
                self.visual_items[current_idx].bounce_animation()
            
            if key_idx < len(self.visual_items):
                self.visual_items[key_idx].highlight(self.color_palette["key"])
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "shell_shift":
            from_idx = action.get("from_index", 0)
            to_idx = action.get("to_index", 0)
            
            if to_idx < len(self.visual_items):
                self.visual_items[to_idx].highlight(self.color_palette["shifted"])
                self.visual_items[to_idx].bounce_animation()
                self.visual_items[to_idx].update_value(action.get("shifted_value", 0))
                
                # Обновляем данные массива
                if to_idx < len(self.array_data):
                    self.array_data[to_idx] = action.get("shifted_value", 0)
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "shell_insert":
            new_idx = action.get("new_index", 0)
            value = action.get("value", 0)
            
            if new_idx < len(self.visual_items):
                self._mark_as_sorted([new_idx])
                self.visual_items[new_idx].update_value(value)
                
                # Обновляем данные массива
                if new_idx < len(self.array_data):
                    self.array_data[new_idx] = value
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "shell_group_progress":
            self._log(action.get("description", ""))
            self._schedule_next_action(int(300 * speed_factor))
            
        elif t == "shell_group_complete":
            group_indices = action.get("group_indices", [])
            
            for idx in group_indices:
                if idx < len(self.visual_items):
                    self._mark_as_sorted([idx])
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "shell_gap_complete":
            # Сбрасываем подсветку всех элементов
            for item in self.visual_items:
                item.reset_color()
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "shell_final_stage":
            # Подсвечиваем все элементы для финального этапа
            for item in self.visual_items:
                item.highlight(self.color_palette["key"])
            
            self._log(action.get("description", ""))
            self._schedule_next_action(int(600 * speed_factor))
        
        elif t == "info":
            self._log(f"ℹ️ {action.get('description', '')}")
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "compare":
            i, j = action["indices"]
            self._highlight_items([i, j], "comparing", 
                                f"🔍 Сравнение: элемент[{i}] = {self.array_data[i]} vs элемент[{j}] = {self.array_data[j]}")
            self._schedule_next_action(int(base_delay * speed_factor))
            
        elif t == "swap":
            i, j = action["indices"]
            self._swap_items(i, j)
            self._log(f"🔄 Обмен элементов {i} и {j}")
            self._schedule_next_action(int(1000 * speed_factor))
            
        elif t == "insert" and "table" in action:
            table_data = action.get("table", [])
            collisions = action.get("collisions", 0)
            max_chain_length = action.get("max_chain_length", 0)
            key_index = action.get("key_index", 0)
            total_keys = action.get("total_keys", 0)
            probed_index = action.get("probed_index")
            original_index = action.get("original_index")
            probing_steps_count = action.get("probing_steps_count", 0)
            
            # Обновляем отображение таблицы
            self.hashtable_display_mode = "building"
            self._render_hashtable_content(table_data, collisions, max_chain_length)
            
            # Анимируем вставку
            insert_idx = probed_index if probed_index is not None else action.get("index", 0)
            if insert_idx < len(self.hashtable_cells):
                self.animation_queue.append({
                    "type": "insert_cell",
                    "index": insert_idx,
                    "value": action.get("key", 0),
                    "original_index": original_index,
                    "duration": 500
                })
                
                if not self.hashtable_animation_timer.isActive():
                    self.hashtable_animation_timer.start(50)
            
            # Логируем информацию о вставке
            desc = action.get("description", "")
            if probing_steps_count > 0:
                desc += f" (шагов пробирования: {probing_steps_count})"
            
            self._log(f"📥 {desc}")
            
            # Показываем прогресс
            progress = f"[{key_index + 1}/{total_keys}]" if total_keys > 0 else ""
            self._log(f"📊 Прогресс: {progress} Коллизий: {collisions}")
            
            self._schedule_next_action(int(700 * speed_factor))
            
        elif t == "insert":
            arr = action.get("array")
            if arr:
                self._render_array(arr)
            self._log("📥 Вставка элемента")
            self._schedule_next_action(int(600 * speed_factor))
            
        # === ОБРАБОТЧИКИ ДЛЯ ХЭШ-ТАБЛИЦЫ ===
        elif t == "info" and "hash_index" in action:
            key = action.get("key", 0)
            hash_idx = action.get("hash_index", 0)
            self._log(f"🔑 Обработка ключа {key}: хэш-функция → индекс {hash_idx}")
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "collision" and self.algorithm_combo.currentText() == "HashTable":
            idx = action.get("index", 0)
            key = action.get("key", 0)
            occupied_key = action.get("occupied_key", 0)
            chain_length = action.get("chain_length", 0)
            
            # Подсвечиваем ячейку с коллизией
            if idx < len(self.hashtable_cells):
                self.hashtable_cells[idx].set_collision(True)
                
                # Добавляем анимацию
                self.animation_queue.append({
                    "type": "highlight_cell",
                    "index": idx,
                    "color": "#FF6B6B",
                    "duration": 300
                })
                
                if not self.hashtable_animation_timer.isActive():
                    self.hashtable_animation_timer.start(50)
            
            if chain_length > 0:
                self._log(f"⚡ Коллизия: ключ {key} в индекс {idx} (цепочка: {chain_length} элементов)")
            else:
                self._log(f"⚡ Коллизия: ключ {key} пытается встать в занятый индекс {idx} (занят ключом {occupied_key})")
            
            self._schedule_next_action(int(600 * speed_factor))
            
        elif t == "probing_step":
            step_num = action.get("step", 0)
            idx = action.get("index", 0)
            key = action.get("key", 0)
            
            # Подсвечиваем ячейку пробирования
            if idx < len(self.hashtable_cells):
                self.hashtable_cells[idx].set_probing(True)
                
                # Добавляем анимацию
                self.animation_queue.append({
                    "type": "highlight_cell",
                    "index": idx,
                    "color": "#FFA500",
                    "duration": 200
                })
                
                if not self.hashtable_animation_timer.isActive():
                    self.hashtable_animation_timer.start(50)
            
            self._log(f"🔍 Шаг {step_num} пробирования: проверка индекса {idx} для ключа {key}")
            self._schedule_next_action(int(300 * speed_factor))
            
        elif t == "duplicate":
            idx = action.get("index", 0)
            key = action.get("key", 0)
            
            # Подсвечиваем ячейку с дубликатом
            if idx < len(self.hashtable_cells):
                self.hashtable_cells[idx].set_collision(True)
                
                # Добавляем анимацию
                self.animation_queue.append({
                    "type": "highlight_cell",
                    "index": idx,
                    "color": "#FFA500",
                    "duration": 300
                })
                
                if not self.hashtable_animation_timer.isActive():
                    self.hashtable_animation_timer.start(50)
            
            self._log(f"⚠️ Дубликат: ключ {key} уже существует в индексе {idx}")
            self._schedule_next_action(int(500 * speed_factor))
            
        elif t == "full":
            self._log(f"❌ Таблица полна, невозможно вставить элемент")
            self._schedule_next_action(int(400 * speed_factor))

        elif t in ["push", "pop", "peek", "enqueue", "dequeue", "front", "back", 
                "push_front", "push_back", "pop_front", "pop_back", "size", "is_empty"]:
            
            if self.container_visualizer:
                self.container_visualizer.process_action(action)
                self._log(action.get("description", ""))
            
            self._schedule_next_action(int(700 * speed_factor))
            
        elif t == "complete":
            # 1. Обработка контейнеров
            if self.container_visualizer:
                self.container_visualizer.process_action(action)
                self._log("✅ Все операции с контейнером выполнены")
            
            # 2. Обработка хэш-таблиц
            elif self.algorithm_combo.currentText() == "HashTable":
                # Сохраняем статистику
                self.hashtable_stats = {
                    "table": action.get("table", []),
                    "collisions": action.get("collisions", 0),
                    "load_factor": action.get("load_factor", 0),
                    "filled_cells": action.get("filled_cells", 0),
                    "total_cells": action.get("total_cells", 0),
                    "max_chain_length": action.get("max_chain_length", 0),
                    "probing_steps_total": action.get("probing_steps_total", 0),
                    "hash_function": action.get("hash_function", ""),
                    "collision_method": action.get("collision_method", ""),
                    "table_size": action.get("table_size", 0)
                }
                
                # ПОЛНОСТЬЮ ПЕРЕСТРАИВАЕМ СЦЕНУ С НОВЫМИ ДАННЫМИ
                self._render_completed_hashtable(action)
                
                # Переходим в режим завершения
                self.hashtable_display_mode = "completed"
                
                # Включаем прокрутку
                self._enable_hashtable_scroll()
                
                # Включаем кнопку просмотра цепочек
                self.view_chains_btn.setEnabled(True)
                self._log("✅ Хэш-таблица построена! Используйте прокрутку для просмотра.")
                
                # Завершаем анимацию
                self._schedule_next_action(100)
                        # Завершение алгоритма Хаффмана
            elif self.algorithm_combo.currentText() == "Huffman Coding":
                # Показываем финальную статистику
                if self.current_algorithm and hasattr(self.current_algorithm, 'get_compression_stats'):
                    stats = self.current_algorithm.get_compression_stats()
                    self._update_huffman_stats({
                        "type": "text_encoded",
                        "original_size": stats["original_size_bits"],
                        "compressed_size": stats["compressed_size_bits"],
                        "ratio": stats["compression_ratio"],
                        "savings": stats["savings_percentage"]
                    })
                
                self._log("✅ Алгоритм Хаффмана успешно завершён!")
            # 3. Обработка деревьев
            elif self._last_tree_data:
                self._render_tree(self._last_tree_data)
                self._log("🌳 Построение дерева завершено")
            
            # 4. Обработка графов
            elif hasattr(self, 'graph_visualizer') and self.graph_visualizer.nodes:
                success = self.graph_visualizer.process_action(action)
                if success:
                    self._log("✅ Алгоритм успешно завершён!")
            
            # 5. Обработка массивов (сортировки)
            else:
                # При завершении помечаем все элементы как отсортированные
                all_indices = list(range(len(self.visual_items)))
                self._mark_as_sorted(all_indices)
                
                # Запускаем финальную анимацию
                self._animate_completion()
                self._log("✅ Алгоритм успешно завершён!")
                # ПОСЛЕ ЗАВЕРШЕНИЯ СОРТИРОВКИ ПОКАЗЫВАЕМ ПАНЕЛЬ ПОИСКА
                if self.category_combo.currentText() == "Сортировки":
                    QTimer.singleShot(1500, self._create_search_panel)
            # Скрываем виджет временных массивов (для всех алгоритмов)
            self.temp_arrays_widget.hide()
            self.temp_arrays_widget.clear()
            
            self.is_animating = False
            self.algorithm_completed = True
            
            if self.is_auto_mode:
                self._pause_auto_mode()
            
            self.inspector.update_info(action)
            return
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
        
        self.visual_items[i].highlight(self.color_palette["swapping"])
        self.visual_items[j].highlight(self.color_palette["swapping"])
        
        radius, spacing = 30, 15
        total_width = len(self.visual_items) * (radius * 2 + spacing)
        scene_width = max(800, total_width + 100)
        start_x = (scene_width - total_width) / 2
        start_y = 150
        
        new_x_i = start_x + i * (radius * 2 + spacing)
        new_x_j = start_x + j * (radius * 2 + spacing)
        
        self.visual_items[i].animate_move(new_x_i, start_y, 600)
        self.visual_items[j].animate_move(new_x_j, start_y, 600)

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
                self._mark_as_sorted([index])
                QTimer.singleShot(150, lambda: highlight_next(index + 1))
            else:
                self.is_animating = False
        
        highlight_next()

    def _animate_hashtable_cell(self):
        """Анимация ячеек хэш-таблицы."""
        if not self.animation_queue:
            self.hashtable_animation_timer.stop()
            return
            
        animation = self.animation_queue.pop(0)
        anim_type = animation.get("type")
        
        if anim_type == "highlight_cell":
            idx = animation.get("index", 0)
            color = animation.get("color", "#FF6B6B")
            duration = animation.get("duration", 300)
            
            if idx < len(self.hashtable_cells):
                cell = self.hashtable_cells[idx]
                
                # Временная подсветка через таймер
                timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(lambda: cell.set_collision(False) if color == "#FF6B6B" else cell.set_probing(False))
                timer.start(duration)
                
        elif anim_type == "insert_cell":
            idx = animation.get("index", 0)
            value = animation.get("value", 0)
            original_index = animation.get("original_index")
            duration = animation.get("duration", 500)
            
            if idx < len(self.hashtable_cells):
                cell = self.hashtable_cells[idx]
                
                # Анимация "появления" - масштабирование
                scale_anim = QPropertyAnimation(cell, b"scale")
                scale_anim.setDuration(duration)
                scale_anim.setStartValue(1)
                scale_anim.setEndValue(1.0)
                scale_anim.setEasingCurve(QEasingCurve.Type.OutBounce)
                scale_anim.start()

    def _enable_hashtable_scroll(self):
        """Включает возможность прокрутки для хэш-таблицы."""
        self.hashtable_scroll_enabled = True
        
        # Настраиваем view для прокрутки
        if hasattr(self.view, 'set_scene_rect_based_on_content'):
            # Вычисляем область с содержимым таблицы
            if self.hashtable_cells:
                # Берем первую ячейку для начала
                cells_rect = self.hashtable_cells[0].boundingRect()
                cells_rect.translate(self.hashtable_cells[0].pos())
                
                # Объединяем со всеми ячейками
                for cell in self.hashtable_cells[1:]:
                    r = cell.boundingRect()
                    r.translate(cell.pos())
                    cells_rect = cells_rect.united(r)
                
                # Добавляем пространство для заголовка и статистики
                cells_rect.adjust(-100, -200, 300, 300)
                self.view.set_scene_rect_based_on_content(cells_rect, 50)
        
        # Включаем скроллбары
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def _log(self, msg):
        """Добавление сообщения в лог."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {msg}")
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _show_chains_viewer(self):
        """Показывает диалог просмотра всех цепочек."""
        try:
            if not self.current_hashtable_data:
                QMessageBox.information(
                    self,
                    "Нет данных",
                    "Хэш-таблица еще не построена или данные недоступны."
                )
                return
            
            # Проверяем, есть ли вообще цепочки
            has_chains = False
            for data in self.current_hashtable_data:
                if isinstance(data, list) and len(data) > 1:
                    has_chains = True
                    break
            
            if not has_chains:
                QMessageBox.information(
                    self,
                    "Нет цепочек",
                    "В хэш-таблице нет цепочек (все значения уникальны или используются другие методы разрешения коллизий)."
                )
                return
            
            # Создаем и показываем диалог
            dialog = ChainsViewerDialog(self.current_hashtable_data, self)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось открыть просмотр цепочек: {str(e)}"
            )
            import traceback
            traceback.print_exc()

    # === ИНТЕРАКТИВНЫЕ ОПЕРАЦИИ С ДЕРЕВЬЯМИ ===
    
    def _on_operation_execute(self):
        """Выполнение выбранной операции с деревом."""
        if not self.current_algorithm or not hasattr(self.current_algorithm, '__class__'):
            self._log("❌ Нет активного дерева для операций")
            return
        
        operation = self.tree_ops_combo.currentText()
        value_text = self.val_input.text().strip()
        
        try:
            is_heap = isinstance(self.current_algorithm, BinaryHeap)
            if is_heap:
                # Обработка операций для кучи
                if operation == "Вставить узел":
                    if not value_text:
                        QMessageBox.warning(self, "Ошибка", "Введите значение для операции")
                        return
                    value = int(value_text)
                    self._heap_insert(value)
                    
                elif operation == "Удалить корень (delete)":
                    self._heap_delete()
                    
                elif operation == "Посмотреть корень (peek)":
                    self._heap_peek()
                    
                elif operation == "Получить размер (get_size)":
                    self._heap_get_size()
                    
                elif operation == "Проверить на пустоту (is_empty)":
                    self._heap_is_empty()
                    
                elif operation == "Получить max (для max-heap)":
                    self._heap_get_max()
                    
                elif operation == "Получить min (для min-heap)":
                    self._heap_get_min()
                    
                elif operation == "Преобразовать в min-heap":
                    self._heap_convert_to_min()
                    
                elif operation == "Преобразовать в max-heap":
                    self._heap_convert_to_max()
                    
                elif operation == "Очистить кучу":
                    self._heap_clear()
                
            else:
                if operation in ["Вставить узел", "Удалить узел", "Найти узел"]:
                    if not value_text:
                        QMessageBox.warning(self, "Ошибка", "Введите значение для операции")
                        return
                    
                    value = int(value_text)
                    
                    if operation == "Вставить узел":
                        self._insert_node(value)
                    elif operation == "Удалить узел":
                        self._delete_node(value)  # Используем новый метод
                    elif operation == "Найти узел":
                        self._search_node(value)
                    
                        
                elif operation == "Прямой обход (Pre-order)":
                    self._perform_traversal("preorder")
                elif operation == "Центральный обход (In-order)":
                    self._perform_traversal("inorder")
                elif operation == "Обратный обход (Post-order)":
                    self._perform_traversal("postorder")
                elif operation == "Обход в ширину (BFS)":
                    self._perform_traversal("bfs")
                
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное число")
        except Exception as e:
            self._log(f"❌ Ошибка при выполнении операции: {str(e)}")
    def _update_heap_visualization(self, message=""):
        """Обновляет визуализацию кучи."""
        try:
            heap = self.current_algorithm
            
            if not heap:
                self._log("❌ Куча не инициализирована")
                return
            
            # Получаем структуру дерева кучи
            tree_data = heap._get_tree_structure()
            
            if tree_data:
                # ВАЖНО: Используем TreeVisualizer для отображения кучи как дерева
                self.scene.clear()
                self.visual_items.clear()
                
                # Устанавливаем большой размер сцены
                extended_scene_rect = QRectF(-3000, -3000, 6000, 6000)
                self.scene.setSceneRect(extended_scene_rect)
                
                # Создаем дерево через TreeVisualizer
                self.tree_visualizer.clear()
                root = self.tree_visualizer.create_tree_from_structure(tree_data, animate=False)
                
                if root:
                    if message:
                        self._log(f"📈 {message}")
                    
                    # Отладочная информация
                    heap_type = "Max-Heap" if heap.type == 'max' else "Min-Heap"
                    self._log(f"📊 {heap_type}, Размер: {heap.get_size()}")
                    self._log(f"📊 Массив кучи: {heap.heap}")
                    
                    # Центрируем вид
                    QTimer.singleShot(50, self._center_on_tree)
                    
                    # Подгоняем масштаб
                    QTimer.singleShot(100, lambda: self.view.fit_to_content(100) if hasattr(self.view, 'fit_to_content') else None)
                else:
                    self._log("❌ Не удалось построить визуализацию кучи")
                    
            else:
                # Если куча пустая, показываем сообщение
                self.scene.clear()
                text_item = self.scene.addText("Куча пуста")
                text_item.setDefaultTextColor(QColor("#666"))
                text_item.setFont(QFont("Arial", 16))
                text_item.setPos(-50, -20)
                
                # Добавляем информацию о типе
                heap_type = "Max-Heap" if heap.type == 'max' else "Min-Heap"
                type_item = self.scene.addText(f"Тип: {heap_type}")
                type_item.setDefaultTextColor(QColor("#5A9BD5"))
                type_item.setFont(QFont("Arial", 12))
                type_item.setPos(-50, 20)
                
                self._log("📊 Куча пуста")
                
        except Exception as e:
            self._log(f"❌ Ошибка при обновлении визуализации кучи: {str(e)}")
            import traceback
            traceback.print_exc()
    def _heap_insert(self, value):
        """Вставка элемента в кучу."""
        try:
            heap = self.current_algorithm
            
            # Вставляем элемент
            success = heap.insert(value)
            if success:
                self._log(f"✅ Элемент {value} вставлен в кучу")
                
                # Обновляем визуализацию
                QTimer.singleShot(100, lambda: self._update_heap_visualization(f"Вставлен элемент: {value}"))
                
            else:
                self._log(f"❌ Не удалось вставить элемент {value}")
                
        except Exception as e:
            self._log(f"❌ Ошибка при вставке в кучу: {str(e)}")
            import traceback
            traceback.print_exc()

    def _heap_delete(self):
        """Удаление корневого элемента из кучу."""
        try:
            heap = self.current_algorithm
            
            if heap.is_empty():
                self._log("❌ Куча пуста, нечего удалять")
                return
            
            # Используем пошаговое удаление
            generator = heap.delete_with_steps()
            
            # Загружаем генератор в движок
            self.engine.generator = generator
            
            # Запускаем автоматический режим для визуализации процесса
            self._start_auto_mode()
            # Обновляем визуализацию
            QTimer.singleShot(100, lambda: self._update_heap_visualization("Куча обновлена"))    
        except Exception as e:
            self._log(f"❌ Ошибка при удалении из кучи: {str(e)}")

    def _heap_peek(self):
        """Просмотр корневого элемента без удаления."""
        try:
            heap = self.current_algorithm
            
            if heap.is_empty():
                self._log("❌ Куча пуста")
                return
            
            root_value = heap.peek()
            self._log(f"👁 Корневой элемент кучи: {root_value}")
            
            # Подсвечиваем корень
            if hasattr(self, 'tree_visualizer'):
                self.tree_visualizer.highlight_node_by_value(root_value, "#FFD700", 2000)
                
        except Exception as e:
            self._log(f"❌ Ошибка при просмотре кучи: {str(e)}")

    def _heap_get_size(self):
        """Получение размера кучи."""
        try:
            heap = self.current_algorithm
            size = heap.get_size()
            self._log(f"📊 Размер кучи: {size}")
        except Exception as e:
            self._log(f"❌ Ошибка при получении размера кучи: {str(e)}")

    def _heap_is_empty(self):
        """Проверка кучи на пустоту."""
        try:
            heap = self.current_algorithm
            is_empty = heap.is_empty()
            status = "пуста" if is_empty else "не пуста"
            self._log(f"📋 Куча {status}")
        except Exception as e:
            self._log(f"❌ Ошибка при проверке кучи: {str(e)}")

    def _heap_get_max(self):
        """Получение максимального элемента (для max-heap)."""
        try:
            heap = self.current_algorithm
            
            if heap.type != 'max':
                self._log("❌ Эта операция доступна только для max-heap")
                return
            
            max_value = heap.get_max()
            if max_value is not None:
                self._log(f"📊 Максимальный элемент: {max_value}")
                # Подсвечиваем максимальный элемент (корень)
                if hasattr(self, 'tree_visualizer'):
                    self.tree_visualizer.highlight_node_by_value(max_value, "#FF6B6B", 2000)
            else:
                self._log("❌ Куча пуста")
                
        except Exception as e:
            self._log(f"❌ Ошибка при получении max: {str(e)}")

    def _heap_get_min(self):
        """Получение минимального элемента (для min-heap)."""
        try:
            heap = self.current_algorithm
            
            if heap.type != 'min':
                self._log("❌ Эта операция доступна только для min-heap")
                return
            
            min_value = heap.get_min()
            if min_value is not None:
                self._log(f"📊 Минимальный элемент: {min_value}")
                # Подсвечиваем минимальный элемент (корень)
                if hasattr(self, 'tree_visualizer'):
                    self.tree_visualizer.highlight_node_by_value(min_value, "#4ECDC4", 2000)
            else:
                self._log("❌ Куча пуста")
                
        except Exception as e:
            self._log(f"❌ Ошибка при получении min: {str(e)}")

    def _heap_convert_to_min(self):
        """Преобразование кучи в min-heap."""
        try:
            heap = self.current_algorithm
            
            if heap.type == 'min':
                self._log("ℹ️ Куча уже является min-heap")
                return
            
            # Получаем текущие данные
            data = heap.heap.copy()
            
            # Создаем новую min-heap
            self.current_algorithm = BinaryHeap(data, heap_type='min')
            
            self._log("✅ Куча преобразована в min-heap")
            
            # Обновляем визуализацию
            self._update_heap_visualization("Преобразована в min-heap")
            # Обновляем визуализацию
            QTimer.singleShot(100, lambda: self._update_heap_visualization("Куча обновлена"))
        except Exception as e:
            self._log(f"❌ Ошибка при преобразовании в min-heap: {str(e)}")

    def _heap_convert_to_max(self):
        """Преобразование кучи в max-heap."""
        try:
            heap = self.current_algorithm
            
            if heap.type == 'max':
                self._log("ℹ️ Куча уже является max-heap")
                return
            
            # Получаем текущие данные
            data = heap.heap.copy()
            
            # Создаем новую max-heap
            self.current_algorithm = BinaryHeap(data, heap_type='max')
            
            self._log("✅ Куча преобразована в max-heap")
            
            # Обновляем визуализацию
            self._update_heap_visualization("Преобразована в max-heap")
            # Обновляем визуализацию
            QTimer.singleShot(100, lambda: self._update_heap_visualization("Куча обновлена"))
        except Exception as e:
            self._log(f"❌ Ошибка при преобразовании в max-heap: {str(e)}")

    def _heap_clear(self):
        """Очистка кучи."""
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите очистить кучу?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                heap = self.current_algorithm
                heap.clear()
                
                self._log("🗑️ Куча очищена")
                
                # Очищаем визуализацию
                self.scene.clear()
                self.visual_items.clear()
                
                # Показываем сообщение
                text_item = self.scene.addText("Куча очищена")
                text_item.setDefaultTextColor(QColor("#666"))
                text_item.setFont(QFont("Arial", 16))
                text_item.setPos(-50, -20)
                # Обновляем визуализацию
                QTimer.singleShot(100, lambda: self._update_heap_visualization("Куча обновлена"))
                # Подгоняем масштаб
                self._schedule_zoom_reset()
                
            except Exception as e:
                self._log(f"❌ Ошибка при очистке кучи: {str(e)}")


    def _insert_node(self, value):
        """Вставка узла в дерево."""
        try:
            tree = self.current_algorithm
            
            if not tree:
                self._log("❌ Нет активного дерева для операций")
                return
            
            # Проверяем тип дерева и используем соответствующий метод
            if hasattr(tree, 'insert') or hasattr(tree, 'insert_value'):
                # Для B-дерева используем insert_value
                if isinstance(tree, BTree):
                    tree.insert_value(value)
                    self._log(f"✅ Значение {value} добавлено в B-дерево")
                    
                    # Специальная обработка для B-дерева - полное перестроение
                    tree_data = tree._get_tree_structure_list()
                    if tree_data:
                        # Используем анимацию перестроения
                        self._update_btree_visualization(tree_data, animate=True)
                    else:
                        self._log("⚠️ Не удалось получить данные B-дерева для визуализации")
                else:
                    # Для обычных деревьев
                    tree.insert(value)
                    self._log(f"✅ Узел {value} вставлен в дерево")
                    self._update_tree_visualization(f"Вставлен узел: {value}")
                    
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Некорректное значение: {str(e)}")
        except Exception as e:
            self._log(f"❌ Ошибка при вставке: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _delete_node(self, value):
        """Удаляет узел из дерева."""
        try:
            tree = self.current_algorithm
            
            if not hasattr(tree, 'delete'):
                self._log("❌ Этот тип дерева не поддерживает удаление")
                return
            
            # Подсвечиваем удаляемый узел
            if hasattr(self, 'tree_visualizer'):
                self.tree_visualizer.highlight_node_by_value(value, "#FF6B6B", 1000)
            
            # Удаляем узел
            try:
                tree.delete(value)
                self._log(f"✅ Узел {value} удален из дерева")
            except ValueError as e:
                self._log(f"❌ {str(e)}")
                return
            
            # Обновляем визуализацию
            self._update_tree_visualization(f"Удален узел: {value}")
            
            # Добавляем небольшую задержку для отображения
            QTimer.singleShot(500, lambda: self._center_on_tree())
            
        except Exception as e:
            self._log(f"❌ Ошибка при удалении: {str(e)}")
            import traceback
            traceback.print_exc()
    def _on_search_execute(self):
        """Выполняет бинарный поиск по отсортированному массиву."""
        # Используем ТЕКУЩИЙ массив (self.array_data), а не из поля ввода
        if not hasattr(self, 'array_data') or not self.array_data:
            self._log("❌ Нет данных для поиска")
            QMessageBox.warning(self, "Ошибка", "Сначала выполните сортировку массива")
            return
        
        # Проверяем, отсортирован ли массив
        is_sorted = all(self.array_data[i] <= self.array_data[i+1] for i in range(len(self.array_data)-1))
        if not is_sorted:
            self._log("❌ Массив не отсортирован! Бинарный поиск работает только с отсортированными массивами.")
            QMessageBox.warning(self, "Ошибка", 
                            "Массив не отсортирован!\nБинарный поиск работает только с отсортированными массивами.")
            return
        
        # Запрашиваем искомое значение
        from PyQt6.QtWidgets import QInputDialog
        target, ok = QInputDialog.getInt(
            self, 
            "Бинарный поиск", 
            "Введите искомое значение:", 
            value=0, 
            min=-1000, 
            max=1000
        )
        
        if not ok:
            return  # Пользователь отменил
        
        try:
            # Останавливаем текущие анимации и движок
            self.engine.pause()
            self.engine.generator = None
            self.is_animating = False
            self.pending_actions.clear()
            
            # ===== КРИТИЧЕСКИ ВАЖНО: СБРАСЫВАЕМ СОСТОЯНИЕ =====
            self.algorithm_completed = False  # Сбрасываем флаг завершения алгоритма
            self.current_step = 0             # Сбрасываем счетчик шагов
            self.total_steps = 0              # Сбрасываем общее количество шагов
            
            # Сбрасываем подсветку всех элементов
            self._reset_all_colors()
            
            # Создаем алгоритм бинарного поиска с ТЕКУЩИМ отсортированным массивом
            from model.search.binary_search import BinarySearch
            self.current_algorithm = BinarySearch(self.array_data.copy(), target)
            
            # Обновляем поле ввода (для информации)
            self.search_val_input.setText(str(target))
            
            # Загружаем в движок
            self.engine.load_algorithm(self.current_algorithm)
            
            # Запускаем поиск
            self._log(f"🔍 Запуск бинарного поиска значения {target} в отсортированном массиве...")
            self._log(f"📊 Размер массива: {len(self.array_data)} элементов")
            
            # Запускаем первый шаг поиска
            if not self.is_animating:
                success = self.engine.step()
                if not success:
                    self._log("❌ Не удалось запустить бинарный поиск")
                    self.algorithm_completed = True
            
        except Exception as e:
            self._log(f"❌ Ошибка при выполнении поиска: {str(e)}")
            import traceback
            traceback.print_exc()
    def _create_search_panel(self):
        """Создает панель для бинарного поиска после сортировки."""
        # Очищаем контейнер
        self._clear_interactive_panel_children()
        
        # Проверяем, что массив отсортирован
        is_sorted = False
        if hasattr(self, 'array_data') and self.array_data:
            is_sorted = all(self.array_data[i] <= self.array_data[i+1] for i in range(len(self.array_data)-1))
        
        # Обновляем информационную метку
        if is_sorted:
            self.info_label.setText(f"✅ Массив отсортирован ({len(self.array_data)} элементов)")
            self.info_label.setStyleSheet("""
                QLabel {
                    color: #2ecc71;
                    font-size: 12px;
                    padding: 5px;
                    background-color: #e8f8f1;
                    border-radius: 4px;
                    border: 1px solid #d0f0e0;
                }
            """)
        else:
            self.info_label.setText("⚠️ Массив НЕ отсортирован! Сначала выполните сортировку.")
            self.info_label.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-size: 12px;
                    padding: 5px;
                    background-color: #fdedec;
                    border-radius: 4px;
                    border: 1px solid #f5c6cb;
                }
            """)
        
        # Поле ввода искомого значения
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Искомое значение:"))
        self.search_val_input = QLineEdit()
        self.search_val_input.setPlaceholderText("Нажмите кнопку для ввода...")
        self.search_val_input.setReadOnly(True)
        self.search_val_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #5A9BD5;
                border-radius: 4px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
        """)
        input_layout.addWidget(self.search_val_input)
        self.operations_layout.addLayout(input_layout)
        
        # Кнопка выполнения поиска
        self.search_execute_btn = QPushButton("🔍 Выполнить бинарный поиск")
        self.search_execute_btn.setEnabled(is_sorted)  # Кнопка активна только если массив отсортирован
        self.search_execute_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#4ECDC4' if is_sorted else '#b0b0b0'};
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {'#3dbcb3' if is_sorted else '#a0a0a0'};
            }}
            QPushButton:pressed {{
                background-color: {'#2eaba2' if is_sorted else '#909090'};
            }}
        """)
        self.search_execute_btn.clicked.connect(self._on_search_execute)
        self.operations_layout.addWidget(self.search_execute_btn)
        
        # Информация о сортировке
        info_label = QLabel("ℹ️ Бинарный поиск работает только на отсортированных массивах")
        info_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                font-style: italic;
                padding: 5px;
                background-color: #f0f8ff;
                border-radius: 4px;
                border: 1px solid #d0e0ff;
            }
        """)
        info_label.setWordWrap(True)
        self.operations_layout.addWidget(info_label)
    def _search_node(self, value):
        """Поиск узла в дереве."""
        try:
            if not self.current_algorithm:
                self._log("❌ Нет активного дерева для операций")
                return
            
            tree = self.current_algorithm
            
            # Проверяем поддержку поиска
            if not hasattr(tree, 'search'):
                self._log("❌ Этот тип дерева не поддерживает поиск")
                return
            
            # Останавливаем текущие анимации
            if self.is_auto_mode:
                self._pause_auto_mode()
            
            # Получаем текущую структуру дерева
            if hasattr(tree, '_get_tree_structure_list'):
                tree_data = tree._get_tree_structure_list()
                if tree_data:
                    self._update_btree_visualization(tree_data, animate=False)
            elif hasattr(tree, '_get_tree_structure'):
                tree_data = tree._get_tree_structure(tree.root)
                if tree_data:
                    self._render_tree(tree_data)
            
            # Выполняем поиск
            result = tree.search(value)
            
            if result:
                # Для разных типов деревьев разный формат результата
                if isinstance(result, tuple) and len(result) == 2:  # B-дерево
                    node, idx = result
                    self._log(f"✅ Найден узел со значением {value} в позиции {idx}")
                    self._highlight_found_node_in_btree(node, value, idx)
                else:  # Обычное дерево
                    self._log(f"✅ Найден узел {value}")
                    self._highlight_found_node(value)
            else:
                self._log(f"❌ Узел {value} не найден в дереве")
                QMessageBox.information(self, "Поиск", f"Узел {value} не найден")
                
        except Exception as e:
            self._log(f"❌ Ошибка при поиске: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _highlight_found_node(self, value):
        """Подсвечивает найденный узел."""
        try:
            if hasattr(self, 'tree_visualizer'):
                # Пробуем разные способы поиска узла
                node_found = False
                
                # 1. Ищем в value_to_node
                if hasattr(self.tree_visualizer, 'value_to_node'):
                    if value in self.tree_visualizer.value_to_node:
                        node = self.tree_visualizer.value_to_node[value]
                        if hasattr(node, 'highlight'):
                            original_color = getattr(node, 'circleColor', getattr(node, 'bg_color', None))
                            node.highlight(QColor("#FFD700"))
                            node_found = True
                            
                            # Возвращаем цвет через 2 секунды
                            QTimer.singleShot(2000, lambda: self._reset_node_color(node, original_color))
                
                # 2. Ищем во всех узлах сцены
                if not node_found:
                    for item in self.scene.items():
                        if isinstance(item, TreeNodeItem) and str(item.value) == str(value):
                            item.highlight(QColor("#FFD700"))
                            node_found = True
                            
                            # Возвращаем цвет через 2 секунды
                            original_color = getattr(item, 'circleColor', None)
                            QTimer.singleShot(2000, lambda: self._reset_node_color(item, original_color))
                            break
                        
                        elif isinstance(item, BTreeNodeItem):
                            # Для B-дерева проверяем ключи
                            if hasattr(item, 'keys') and value in item.keys:
                                original_color = item.bg_color
                                item.bg_color = QColor("#FFD700")
                                item.update()
                                node_found = True
                                
                                # Возвращаем цвет через 2 секунды
                                QTimer.singleShot(2000, lambda: self._reset_btree_node_color(item, original_color))
                                break
                
                if not node_found:
                    self._log(f"⚠️ Не удалось визуально выделить узел {value}")
                    
        except Exception as e:
            self._log(f"❌ Ошибка при подсветке узла: {str(e)}")
    
    def _highlight_found_node_in_btree(self, btree_node, value, idx):
        """Подсвечивает найденный узел в B-дереве."""
        try:
            if hasattr(self, 'tree_visualizer'):
                # Ищем узел B-дерева по ключам
                for item in self.scene.items():
                    if isinstance(item, BTreeNodeItem):
                        if hasattr(item, 'keys') and value in item.keys:
                            # Сохраняем оригинальный цвет
                            original_color = item.bg_color
                            
                            # Подсвечиваем весь узел
                            item.bg_color = QColor("#FFD700")
                            item.update()
                            
                            # Также можно подсветить конкретный ключ
                            self._log(f"✅ Найден ключ {value} в B-дереве в позиции {idx}")
                            
                            # Возвращаем цвет через 2 секунды
                            QTimer.singleShot(2000, lambda: self._reset_btree_node_color(item, original_color))
                            break
                            
        except Exception as e:
            self._log(f"❌ Ошибка при подсветке B-дерева узла: {str(e)}")
    
    def _reset_node_color(self, node, color):
        """Сбрасывает цвет узла."""
        try:
            if node and hasattr(node, 'highlight') and color:
                node.highlight(color)
        except:
            pass
    
    def _reset_btree_node_color(self, node, color):
        """Сбрасывает цвет узла B-дерева."""
        try:
            if node and hasattr(node, 'bg_color') and color:
                node.bg_color = color
                if hasattr(node, 'update'):
                    node.update()
        except:
            pass
    
    def _perform_traversal(self, traversal_type):
        """Выполнение обхода дерева."""
        try:
            tree = self.current_algorithm
            
            if not tree:
                self._log("❌ Нет активного дерева для операций")
                return
            
            result = []
            
            if traversal_type == "preorder":
                if hasattr(tree, 'get_preorder'):
                    result = tree.get_preorder()
                    traversal_name = "Прямой обход (Pre-order)"
                else:
                    self._log("❌ Этот тип обхода не поддерживается")
                    return
                    
            elif traversal_type == "inorder":
                if hasattr(tree, 'get_inorder'):
                    result = tree.get_inorder()
                    traversal_name = "Центральный обход (In-order)"
                elif hasattr(tree, '_inorder_traversal'):
                    result = tree._inorder_traversal(tree.root)
                    traversal_name = "Центральный обход (In-order)"
                else:
                    self._log("❌ Этот тип обхода не поддерживается")
                    return
                    
            elif traversal_type == "postorder":
                if hasattr(tree, 'get_postorder'):
                    result = tree.get_postorder()
                    traversal_name = "Обратный обход (Post-order)"
                else:
                    self._log("❌ Этот тип обхода не поддерживается")
                    return
                    
            elif traversal_type == "bfs":
                if hasattr(tree, 'get_bfs'):
                    result = tree.get_bfs()
                    traversal_name = "Обход в ширину (BFS)"
                elif isinstance(tree, BTree):
                    # Специальная обработка для B-дерева
                    result = self._bfs_btree_improved(tree)
                    traversal_name = "Обход в ширину (BFS)"
                else:
                    self._log("❌ Этот тип обхода не поддерживается")
                    return
            
            if result:
                # Форматируем результат в зависимости от типа дерева
                if isinstance(tree, BTree):
                    # Для B-дерева результат должен быть правильно структурирован
                    if traversal_type == "bfs":
                        # BFS уже возвращает правильный формат
                        result_str = ""
                        for i, level_nodes in enumerate(result):
                            if isinstance(level_nodes, list):
                                level_str = ", ".join(f"{keys}" for keys in level_nodes)
                                result_str += f"Уровень {i}: [{level_str}]\n"
                            else:
                                result_str += f"Уровень {i}: [{level_nodes}]\n"
                    else:
                        # Для других обходов
                        result_str = "\n".join(f"Узел: {keys}" for keys in result)
                    
                    self._log(f"📊 {traversal_name}:\n{result_str}")
                    tree_data = tree._get_tree_structure_list()
                    if tree_data:
                        self._update_btree_visualization(tree_data, animate=False)
                    # Для B-дерева просто подсвечиваем узлы без перестройки
                    if traversal_type == "bfs":
                        self._highlight_btree_traversal(result)
                    else:
                        # Просто показываем результат в логе
                        self._log(f"🌳 B-дерево: {traversal_name} выполнен")
                else:
                    # Для обычных деревьев
                    result_str = " → ".join(map(str, result))
                    self._log(f"📊 {traversal_name}: {result_str}")
                    
                    # ЗАМЕНА: Не перестраиваем дерево, а просто подсвечиваем узлы
                    if hasattr(self, 'tree_visualizer'):
                        # Сбрасываем цвета всех узлов
                        self.tree_visualizer.reset_styles()
                        
                        # Подсвечиваем узлы в порядке обхода с анимацией
                        self._animate_traversal_highlight(result, traversal_name)
            else:
                self._log("📊 Дерево пустое")
                
        except Exception as e:
            self._log(f"❌ Ошибка при обходе: {str(e)}")
            import traceback
            traceback.print_exc()

    def _animate_traversal_highlight(self, nodes, traversal_name):
        """Анимированное подсвечивание узлов обхода."""
        if not nodes or not hasattr(self, 'tree_visualizer'):
            return
        
        # Цвета для подсветки
        highlight_color = QColor("#FFD700")  # Золотой для текущего
        
        # Сбрасываем все подсветки
        self.tree_visualizer.reset_styles()
        
        # Последовательно подсвечиваем каждый узел
        for i, node_value in enumerate(nodes):
            delay = i * 500  # 500ms между узлами
            
            # Запланировать подсветку этого узла
            QTimer.singleShot(delay, lambda val=node_value, idx=i: 
                            self._highlight_traversal_node(val, idx, highlight_color, len(nodes)))
        
        # Последний узел подсвечиваем дольше
        last_delay = len(nodes) * 500
        QTimer.singleShot(last_delay + 1000, self.tree_visualizer.reset_styles)

    def _highlight_traversal_node(self, node_value, index, color, total_nodes):
        """Подсвечивает один узел обхода."""
        try:
            if hasattr(self, 'tree_visualizer'):
                # Подсвечиваем узел
                self.tree_visualizer.highlight_node_by_value(node_value, color)
                
                # Обновляем лог для текущего узла
                progress = f"({index + 1}/{total_nodes})"
                self._log(f"📍 {progress} Узел: {node_value}")
        except Exception as e:
            print(f"Error highlighting node: {e}")
    
    def _bfs_btree_improved(self, btree):
        """Улучшенный BFS для B-дерева."""
        from collections import deque
        
        result = []
        if not btree.root:
            return result
        
        queue = deque([btree.root])
        
        while queue:
            level_size = len(queue)
            level_nodes = []
            
            for _ in range(level_size):
                node = queue.popleft()
                # Сохраняем ключи узла
                level_nodes.append(node.keys.copy())
                
                # Добавляем детей в очередь
                for child in node.children:
                    queue.append(child)
            
            result.append(level_nodes)
        
        return result
    
    def _highlight_btree_traversal(self, levels):
        """Подсвечивает обход B-дерева по уровням."""
        # Проверяем и нормализуем формат данных
        normalized_levels = []
        for level in levels:
            if isinstance(level, list):
                normalized_levels.append(level)
            else:
                # Если это просто список ключей (не список списков)
                normalized_levels.append([level])
        
        # Проверяем, что у нас есть данные
        if not normalized_levels:
            return
        
        # Подсвечиваем узлы с задержкой
        for level_idx, level_nodes in enumerate(normalized_levels):
            for node_idx, keys in enumerate(level_nodes):
                # Задержка для анимации
                delay = (level_idx * len(normalized_levels[0]) + node_idx) * 300
                
                QTimer.singleShot(delay, lambda l=level_idx, k=keys: 
                                self._highlight_btree_level(l, k))
        
        # Сбрасываем подсветку через время
        total_delay = len(normalized_levels) * len(normalized_levels[0]) * 300 + 2000
        QTimer.singleShot(total_delay, self._reset_all_highlight)
    
    def _highlight_btree_level(self, level_idx, keys):
        """Подсвечивает уровень B-дерева."""
        try:
            # Ищем узлы с такими ключами
            for item in self.scene.items():
                if isinstance(item, BTreeNodeItem):
                    if hasattr(item, 'keys') and item.keys == keys:
                        # Сохраняем оригинальный цвет
                        if not hasattr(item, '_original_color'):
                            item._original_color = item.bg_color
                        
                        # Подсвечиваем цветом в зависимости от уровня
                        colors = ["#FF6B6B", "#4ECDC4", "#FFD166", "#06D6A0", "#118AB2"]
                        color_idx = level_idx % len(colors)
                        item.bg_color = QColor(colors[color_idx])
                        item.update()
                        break
        except Exception as e:
            print(f"Error highlighting B-tree level: {e}")
    
    def _reset_all_highlight(self):
        """Сбрасывает всю подсветку."""
        for item in self.scene.items():
            if isinstance(item, (TreeNodeItem, BTreeNodeItem)):
                if hasattr(item, '_original_color'):
                    if isinstance(item, BTreeNodeItem):
                        item.bg_color = item._original_color
                        item.update()
                    elif hasattr(item, 'highlight'):
                        item.highlight(item._original_color)
                    delattr(item, '_original_color')
    
    def _find_min_max(self, mode):
        """Находит минимальный или максимальный элемент."""
        try:
            tree = self.current_algorithm
            
            if mode == "min":
                if hasattr(tree, 'get_min'):
                    min_value = tree.get_min()
                    if min_value is not None:
                        self._log(f"📊 Минимальный элемент: {min_value}")
                        self.val_input.setText(str(min_value))
                        self._highlight_found_node(min_value)
                    else:
                        self._log("📊 Дерево пустое")
                else:
                    self._log("❌ Эта операция не поддерживается для данного дерева")
            else:
                if hasattr(tree, 'get_max'):
                    max_value = tree.get_max()
                    if max_value is not None:
                        self._log(f"📊 Максимальный элемент: {max_value}")
                        self.val_input.setText(str(max_value))
                        self._highlight_found_node(max_value)
                    else:
                        self._log("📊 Дерево пустое")
                else:
                    self._log("❌ Эта операция не поддерживается для данного дерева")
                    
        except Exception as e:
            self._log(f"❌ Ошибка при поиске мин/макс: {str(e)}")
    
    def _get_tree_height(self):
        """Вычисляет высоту дерева."""
        try:
            tree = self.current_algorithm
            
            if hasattr(tree, 'get_height'):
                height = tree.get_height()
                self._log(f"📊 Высота дерева: {height}")
            elif hasattr(tree, 'get_tree_height'):
                height = tree.get_tree_height()
                self._log(f"📊 Высота дерева: {height}")
            elif hasattr(tree, 'root'):
                # Простой расчет высоты для бинарных деревьев
                def calc_height(node):
                    if not node:
                        return 0
                    return 1 + max(calc_height(node.left), calc_height(node.right))
                
                height = calc_height(tree.root)
                self._log(f"📊 Высота дерева: {height}")
            else:
                self._log("❌ Не удалось вычислить высоту дерева")
                
        except Exception as e:
            self._log(f"❌ Ошибка при вычислении высоты: {str(e)}")
    
    def _check_balance(self):
        """Проверяет балансировку дерева."""
        try:
            tree = self.current_algorithm
            
            if hasattr(tree, 'is_balanced'):
                balanced = tree.is_balanced()
                if balanced:
                    self._log("✅ Дерево сбалансировано")
                else:
                    self._log("⚠️ Дерево несбалансировано")
            elif hasattr(tree, '_get_balance'):
                # Для AVL деревьев
                balance = tree._get_balance(tree.root)
                self._log(f"📊 Баланс корня: {balance}")
                
                if abs(balance) <= 1:
                    self._log("✅ Дерево сбалансировано")
                else:
                    self._log("⚠️ Дерево несбалансировано")
                    
                # Подсвечиваем корень
                if hasattr(tree, '_get_tree_structure'):
                    tree_data = tree._get_tree_structure(tree.root)
                    if tree_data:
                        self._render_tree(tree_data)
                        self._highlight_root()
            else:
                self._log("ℹ️ Эта операция доступна только для AVL деревьев")
                
        except Exception as e:
            self._log(f"❌ Ошибка при проверке баланса: {str(e)}")
    
    def _clear_tree(self):
        """Очищает дерево."""
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите очистить дерево?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                tree = self.current_algorithm
                
                if hasattr(tree, 'root'):
                    tree.root = None
                    if hasattr(tree, 'data'):
                        tree.data = []
                    
                    self._log("🗑️ Дерево очищено")
                    
                    # Визуально очищаем сцену
                    self.scene.clear()
                    self.visual_items.clear()
                    
                    # Очищаем визуализатор деревьев
                    if hasattr(self, 'tree_visualizer'):
                        self.tree_visualizer.clear()
                    
                    # Сбрасываем последние данные дерева
                    self._last_tree_data = None
                    
                    # Показываем сообщение о пустом дереве
                    text_item = self.scene.addText("Дерево очищено")
                    text_item.setDefaultTextColor(QColor("#666"))
                    text_item.setFont(QFont("Arial", 16))
                    text_item.setPos(-50, -20)
                    
                    # Подгоняем масштаб
                    self._schedule_zoom_reset()
                    
                    # Обновляем инспектор
                    self.inspector.update_info({"type": "tree_cleared", "description": "Дерево очищено"})
                    
            except Exception as e:
                self._log(f"❌ Ошибка при очистке дерева: {str(e)}")
    
    def _add_random_nodes(self):
        """Добавляет случайные узлы в дерево."""
        try:
            values = [random.randint(1, 100) for _ in range(5)]
            
            for value in values:
                if hasattr(self.current_algorithm, 'insert'):
                    self.current_algorithm.insert(value)
                elif hasattr(self.current_algorithm, 'insert_value'):
                    self.current_algorithm.insert_value(value)
            
            self._log(f"🎲 Добавлены случайные значения: {values}")
            self._update_tree_visualization(f"Добавлены случайные узлы: {values}")
            
        except Exception as e:
            self._log(f"❌ Ошибка при добавлении случайных узлов: {str(e)}")
    
    def _update_tree_visualization(self, message=""):
        """Обновляет визуализацию дерева."""
        try:
            tree = self.current_algorithm
                    # Проверяем, является ли дерево кучей
            if isinstance(tree, BinaryHeap):
                self._update_heap_visualization(message)
                return
            if isinstance(tree, RedBlackTree):
                # Специальная обработка для красно-черного дерева
                if hasattr(tree, '_get_tree_structure'):
                    tree_data = tree._get_tree_structure(tree.root)
                    if tree_data:
                        # Устанавливаем тип дерева в визуализаторе
                        self.tree_visualizer.set_tree_type("RedBlackTree")
                        
                        # Очищаем сцену
                        self.scene.clear()
                        self.visual_items.clear()
                        
                        # Устанавливаем большой размер сцены
                        extended_scene_rect = QRectF(-3000, -3000, 6000, 6000)
                        self.scene.setSceneRect(extended_scene_rect)
                        
                        # Создаем дерево без анимации для скорости
                        root = self.tree_visualizer.create_tree_from_structure(tree_data, animate=False)
                        
                        if message:
                            self._log(f"📈 {message}")
                            
                        # Короткая задержка для подгонки вида
                        QTimer.singleShot(10, self._fit_to_content)
                        return
                else:
                    self._log("⚠️ Не удалось получить структуру дерева")
                    return
                    
            elif hasattr(tree, '_get_tree_structure_list'):
                # Для B-дерева используем специальный метод
                tree_data = tree._get_tree_structure_list()
                
                # Обновляем визуализацию с анимацией
                self._update_btree_visualization(tree_data, animate=True)
                
                if message:
                    self._log(f"📈 {message}")
                    
                # Короткая задержка для подгонки вида
                QTimer.singleShot(10, self._fit_to_content)
                
            elif hasattr(tree, '_get_tree_structure'):
                # Для обычных деревьев
                tree_data = tree._get_tree_structure(tree.root)
                if tree_data:
                    # Используем прямое отображение без анимации для интерактивных операций
                    self._render_tree(tree_data)
                    
                    if message:
                        self._log(f"📈 {message}")
                        
                    # Короткая задержка для подгонки вида
                    QTimer.singleShot(10, self._fit_to_content)
                        
        except Exception as e:
            self._log(f"❌ Ошибка при обновлении визуализации: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _update_btree_visualization(self, tree_data, animate=False):
        """Обновляет визуализацию B-дерева с перестроением."""
        try:
            # Очищаем сцену
            self.scene.clear()
            self.visual_items.clear()
            
            # Устанавливаем большой размер сцены для B-дерева
            extended_scene_rect = QRectF(-3000, -3000, 6000, 6000)
            self.scene.setSceneRect(extended_scene_rect)
            
            if not tree_data:
                text_item = self.scene.addText("B-дерево пустое")
                text_item.setPos(0, 0)
                return
            
            # Используем визуализатор для B-дерева
            if hasattr(self, 'tree_visualizer'):
                # Для интерактивных операций НЕ используем анимацию построения
                # Используем только анимацию перестроения
                root = self.tree_visualizer.update_btree_visualization(tree_data, animate=animate)
                
                if root:
                    # Центрируем вид
                    self._center_on_tree()
                    # Подгоняем масштаб
                    self._schedule_zoom_reset()
                    return True
                else:
                    self._log("❌ Ошибка при обновлении B-дерева")
                    return False
                    
        except Exception as e:
            self._log(f"❌ Ошибка при обновлении B-дерева: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _highlight_traversal(self, nodes):
        """Подсвечивает узлы в порядке обхода."""
        if hasattr(self, 'tree_visualizer'):
            self.tree_visualizer.highlight_traversal(nodes)
    
    def _highlight_root(self):
        """Подсвечивает корень дерева."""
        if hasattr(self, 'tree_visualizer'):
            self.tree_visualizer.highlight_node_by_value(self.current_algorithm.root.value, "#FFA500", 2000)
    
    def _on_container_operation_execute(self):
        """Выполнение операций с контейнером."""
        if not self.current_algorithm:
            self._log("❌ Нет активного контейнера для операций")
            return
        
        # Получаем выбранную операцию
        operation_text = self.container_ops_combo.currentText()
        value_text = self.container_val_input.text().strip()
        
        try:
            # Обработка операций с значением
            if operation_text.startswith("push") or operation_text.startswith("enqueue"):
                if not value_text:
                    QMessageBox.warning(self, "Ошибка", "Введите значение для операции")
                    return
                
                value = int(value_text)
                
                # Определяем позицию для дека
                position = "back"
                if operation_text == "push_front (добавить в начало)":
                    position = "front"
                
                # Выполняем операцию на реальной структуре данных
                if isinstance(self.current_algorithm, Stack):
                    self.current_algorithm.push(value)
                    self.container_visualizer.push(value)
                elif isinstance(self.current_algorithm, Queue):
                    self.current_algorithm.enqueue(value)
                    self.container_visualizer.push(value)  # для очереди тоже push
                elif isinstance(self.current_algorithm, Deque):
                    if operation_text == "push_front (добавить в начало)":
                        self.current_algorithm.push_front(value)
                        self.container_visualizer.push(value, "front")
                    else:  # push_back
                        self.current_algorithm.push_back(value)
                        self.container_visualizer.push(value, "back")
                
                # Очищаем поле ввода
                self.container_val_input.clear()
                
            # Обработка операций без значения
            else:
                result = None
                
                if operation_text == "pop (удалить верхний)":
                    result = self.current_algorithm.pop()
                    self.container_visualizer.pop()
                    
                elif operation_text == "peek (посмотреть верхний)":
                    result = self.current_algorithm.peek()
                    self.container_visualizer.peek()
                    
                elif operation_text == "size (размер)":
                    result = len(self.current_algorithm)
                    self.container_visualizer.get_size()
                    
                elif operation_text == "is_empty (пусто?)":
                    result = self.current_algorithm.is_empty()
                    self.container_visualizer.is_empty()
                    
                elif operation_text == "dequeue (удалить первый)":
                    result = self.current_algorithm.dequeue()
                    self.container_visualizer.pop("front")
                    
                elif operation_text == "front (посмотреть первый)":
                    result = self.current_algorithm.front()
                    self.container_visualizer.peek("front")
                    
                elif operation_text == "back (посмотреть последний)":
                    result = self.current_algorithm.back()
                    self.container_visualizer.peek("back")
                    
                elif operation_text == "pop_front (удалить из начала)":
                    result = self.current_algorithm.pop_front()
                    self.container_visualizer.pop("front")
                    
                elif operation_text == "pop_back (удалить из конца)":
                    result = self.current_algorithm.pop_back()
                    self.container_visualizer.pop("back")
                
                # Показываем результат
                if result is not None:
                    self._log(f"📋 Результат операции: {result}")
                    
            # ОБНОВЛЯЕМ ИНСПЕКТОР
            container_info = self.container_visualizer.get_container_info()
            inspector_data = {
                "type": "container_operation",
                "container_type": self.container_type,
                "size": container_info["size"],
                "empty": container_info["empty"],
                "values": container_info["values"],
                "description": f"Выполнена операция: {operation_text}"
            }
            
            # Добавляем специфичную информацию для каждого типа
            if self.container_type == "stack" and container_info.get("top"):
                inspector_data["top"] = container_info["top"]
                inspector_data["description"] += f"\nВерхний элемент: {container_info['top']}"
            elif container_info.get("front") and container_info.get("back"):
                inspector_data["front"] = container_info["front"]
                inspector_data["back"] = container_info["back"]
                inspector_data["description"] += f"\nНачало: {container_info['front']}, Конец: {container_info['back']}"
            
            self.inspector.update_info(inspector_data)
            
        except (ValueError, IndexError) as e:
            error_msg = str(e)
            if "empty" in error_msg.lower():
                self._log("❌ Контейнер пуст!")
            else:
                self._log(f"❌ Ошибка: {error_msg}")
        except Exception as e:
            self._log(f"❌ Неожиданная ошибка: {str(e)}")
            import traceback
            traceback.print_exc()

    def _clear_container(self):
        """Очищает контейнер."""
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите очистить контейнер?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Очищаем визуализатор
                if self.container_visualizer:
                    self.container_visualizer.clear()
                
                # Создаем новый пустой контейнер
                if self.container_type == "stack":
                    self.current_algorithm = Stack([])
                elif self.container_type == "queue":
                    self.current_algorithm = Queue([])
                elif self.container_type == "deque":
                    self.current_algorithm = Deque([])
                
                # Пересоздаем интерфейс
                self.container_visualizer._create_interface()
                
                # Обновляем инспектор
                inspector_data = {
                    "type": "container_cleared",
                    "container_type": self.container_type,
                    "size": 0,
                    "empty": True,
                    "values": [],
                    "description": "Контейнер очищен"
                }
                self.inspector.update_info(inspector_data)
                
                self._log("🗑️ Контейнер очищен")
                
            except Exception as e:
                self._log(f"❌ Ошибка при очистке контейнера: {str(e)}")

    def _add_random_to_container(self):
        """Добавляет случайные элементы в контейнер."""
        if not self.current_algorithm:
            self._log("❌ Нет активного контейнера")
            return
        
        try:
            # Генерируем 3 случайных числа
            values = [random.randint(10, 99) for _ in range(3)]
            
            for value in values:
                # Определяем операцию в зависимости от типа контейнера
                if self.container_type == "stack":
                    self.current_algorithm.push(value)
                    self.container_visualizer.push(value)
                elif self.container_type == "queue":
                    self.current_algorithm.enqueue(value)
                    self.container_visualizer.push(value)  # Для очереди тоже push
                elif self.container_type == "deque":
                    # Для дека добавляем в конец
                    self.current_algorithm.push_back(value)
                    self.container_visualizer.push(value, "back")
                
                # Небольшая задержка между добавлениями для анимации
                QApplication.processEvents()
            
            self._log(f"🎲 Добавлены случайные значения: {values}")
            
            # ОБНОВЛЯЕМ ИНСПЕКТОР
            container_info = self.container_visualizer.get_container_info()
            inspector_data = {
                "type": "container_random_add",
                "container_type": self.container_type,
                "added_values": values,
                "size": container_info["size"],
                "empty": container_info["empty"],
                "values": container_info["values"],
                "description": f"Добавлено {len(values)} случайных значений"
            }
            
            self.inspector.update_info(inspector_data)
            
        except Exception as e:
            self._log(f"❌ Ошибка при добавлении случайных значений: {str(e)}")

    def _render_container_initial_view(self):
        """Отображает начальный вид для контейнера."""
        self.scene.clear()
        
        if self.container_visualizer:
            # Визуализатор сам создает интерфейс
            self.container_visualizer._create_interface()
        
        self._log(f"📦 Инициализирован {self.container_type}")
        # Немедленно обновляем отображение
        self.scene.update()
        self.view.viewport().update()

    def _fit_to_content(self):
        """Подгоняет масштаб к содержимому."""
        self._schedule_zoom_reset()
    
    def _center_view(self):
        """Центрирует вид."""
        if self.scene and self.scene.items():
            rect = self.scene.itemsBoundingRect()
            if rect.isValid():
                self.view.centerOn(rect.center())
                self._log("🎯 Вид отцентрирован")
     # ==================== МЕТОДЫ ДЛЯ ИНТЕРАКТИВНОЙ ПАНЕЛИ ХАФФМАНА ====================
    
    def _create_huffman_interactive_panel(self):
        """Создает панель интерактивных операций для алгоритма Хаффмана."""
        # Очищаем контейнер полностью
        self._clear_interactive_panel_children()
        
        # Обновляем информационную метку
        self.info_label.setText("ℹ️ Кодирование Хаффмана: сжатие данных без потерь")
        
        # Основной контейнер
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        
        # === ПАНЕЛЬ ВВОДА ТЕКСТА ===
        input_group = QGroupBox("📝 Ввод текста")
        input_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #5A9BD5;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #5A9BD5;
            }
        """)
        
        input_layout = QVBoxLayout()
        
        # Текстовое поле
        self.huffman_text_input = QTextEdit()
        self.huffman_text_input.setPlaceholderText("Введите текст для кодирования Хаффмана...")
        self.huffman_text_input.setMaximumHeight(120)
        self.huffman_text_input.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                border: 2px solid #5A9BD5;
                border-radius: 6px;
                font-size: 14px;
                font-family: 'Arial';
                background-color: #f8f9fa;
            }
            QTextEdit:focus {
                border: 2px solid #3498DB;
                background-color: #ffffff;
            }
        """)
        input_layout.addWidget(self.huffman_text_input)
        
        # Панель примеров
        examples_layout = QHBoxLayout()
        examples_layout.addWidget(QLabel("Примеры:"))
        
        self.huffman_examples_combo = QComboBox()
        for example in self.huffman_examples:
            self.huffman_examples_combo.addItem(example["name"])
        
        self.huffman_examples_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #5A9BD5;
                border-radius: 4px;
                font-size: 12px;
                background-color: white;
            }
        """)
        examples_layout.addWidget(self.huffman_examples_combo)
        
        load_example_btn = QPushButton("📥 Загрузить пример")
        load_example_btn.clicked.connect(self._load_huffman_example)
        load_example_btn.setStyleSheet("""
            QPushButton {
                background-color: #5A9BD5;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #4B89C6;
            }
            QPushButton:pressed {
                background-color: #3A6FA3;
            }
        """)
        examples_layout.addWidget(load_example_btn)
        examples_layout.addStretch()
        
        input_layout.addLayout(examples_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # === ПАНЕЛЬ ОПЕРАЦИЙ ===
        ops_group = QGroupBox("⚙️ Операции")
        ops_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4ECDC4;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #4ECDC4;
            }
        """)
        
        ops_grid = QGridLayout()
        
        # Кнопка анализа частот
        self.huffman_analyze_btn = QPushButton("📊 Анализ частот")
        self.huffman_analyze_btn.clicked.connect(self._huffman_analyze_frequencies)
        self.huffman_analyze_btn.setToolTip("Анализировать частоты символов в тексте")
        
        # Кнопка построения дерева
        self.huffman_build_tree_btn = QPushButton("🌳 Построить дерево")
        self.huffman_build_tree_btn.clicked.connect(self._huffman_build_tree)
        self.huffman_build_tree_btn.setToolTip("Построить дерево Хаффмана")
        
        # Кнопка генерации кодов
        self.huffman_generate_codes_btn = QPushButton("🔤 Сгенерировать коды")
        self.huffman_generate_codes_btn.clicked.connect(self._huffman_generate_codes)
        self.huffman_generate_codes_btn.setToolTip("Сгенерировать коды Хаффмана")
        
        # Кнопка кодирования
        self.huffman_encode_btn = QPushButton("🔒 Закодировать текст")
        self.huffman_encode_btn.clicked.connect(self._huffman_encode_text)
        self.huffman_encode_btn.setToolTip("Закодировать текст с использованием кодов Хаффмана")
        
        # Кнопка декодирования
        self.huffman_decode_btn = QPushButton("🔓 Декодировать текст")
        self.huffman_decode_btn.clicked.connect(self._huffman_decode_text)
        self.huffman_decode_btn.setToolTip("Декодировать текст")
        
        # Кнопка полного процесса
        self.huffman_full_process_btn = QPushButton("🚀 Полный процесс")
        self.huffman_full_process_btn.clicked.connect(self._huffman_full_process)
        self.huffman_full_process_btn.setToolTip("Выполнить полный процесс кодирования Хаффмана")
        
        # Стили для кнопок операций
        ops_button_style = """
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                font-weight: bold;
                border: 2px solid #2eaba2;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #3dbcb3;
                border: 2px solid #1d9a91;
            }
            QPushButton:pressed {
                background-color: #2eaba2;
            }
            QPushButton:disabled {
                background-color: #b0d0cd;
                color: #e0f0ee;
                border: 2px solid #a0c0bd;
            }
        """
        
        # Специальный стиль для кнопки полного процесса
        full_process_style = """
            QPushButton {
                background-color: #9B59B6;
                color: white;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #8E44AD;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #8E44AD;
                border: 2px solid #7D3C98;
            }
            QPushButton:pressed {
                background-color: #7D3C98;
            }
        """
        
        # Применяем стили
        for btn in [self.huffman_analyze_btn, self.huffman_build_tree_btn, 
                    self.huffman_generate_codes_btn, self.huffman_encode_btn,
                    self.huffman_decode_btn]:
            btn.setStyleSheet(ops_button_style)
        
        self.huffman_full_process_btn.setStyleSheet(full_process_style)
        
        # Размещаем кнопки в сетке
        ops_grid.addWidget(self.huffman_analyze_btn, 0, 0)
        ops_grid.addWidget(self.huffman_build_tree_btn, 0, 1)
        ops_grid.addWidget(self.huffman_generate_codes_btn, 1, 0)
        ops_grid.addWidget(self.huffman_encode_btn, 1, 1)
        ops_grid.addWidget(self.huffman_decode_btn, 2, 0)
        ops_grid.addWidget(self.huffman_full_process_btn, 2, 1)
        
        ops_group.setLayout(ops_grid)
        layout.addWidget(ops_group)
        
        # === ПАНЕЛЬ СТАТИСТИКИ ===
        self.huffman_stats_label = QLabel("ℹ️ Введите текст и выполните операции")
        self.huffman_stats_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 12px;
                padding: 15px;
                background-color: #f0f8ff;
                border-radius: 8px;
                border: 2px solid #d0e0ff;
                margin-top: 10px;
            }
        """)
        self.huffman_stats_label.setWordWrap(True)
        self.huffman_stats_label.setMinimumHeight(80)
        layout.addWidget(self.huffman_stats_label)
        
        # === ПАНЕЛЬ БЫСТРЫХ ДЕЙСТВИЙ ===
        quick_group = QGroupBox("⚡ Быстрые действия")
        quick_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #FFD166;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #FFD166;
            }
        """)
        
        quick_layout = QHBoxLayout()
        
        # Кнопка очистки
        self.huffman_clear_btn = QPushButton("🗑️ Очистить всё")
        self.huffman_clear_btn.clicked.connect(self._clear_huffman)
        self.huffman_clear_btn.setToolTip("Очистить все данные")
        
        # Кнопка экспорта
        self.huffman_export_btn = QPushButton("💾 Экспорт кодов")
        self.huffman_export_btn.clicked.connect(self._export_huffman_codes)
        self.huffman_export_btn.setToolTip("Экспортировать таблицу кодов")
        
        # Кнопка копирования результата
        self.huffman_copy_btn = QPushButton("📋 Копировать код")
        self.huffman_copy_btn.clicked.connect(self._copy_huffman_code)
        self.huffman_copy_btn.setToolTip("Копировать закодированный текст")
        
        # Стили для быстрых кнопок
        quick_button_style = """
            QPushButton {
                background-color: #FFD166;
                color: #2c3e50;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #E6B84F;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #E6B84F;
                border: 2px solid #D4A847;
            }
            QPushButton:pressed {
                background-color: #D4A847;
            }
        """
        
        for btn in [self.huffman_clear_btn, self.huffman_export_btn, self.huffman_copy_btn]:
            btn.setStyleSheet(quick_button_style)
            quick_layout.addWidget(btn)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        layout.addStretch()
        
        # Добавляем контейнер в operations_layout
        self.operations_layout.addWidget(container)
        
        # Инициализируем состояние кнопок
        self._update_huffman_buttons_state()
    
    def _on_huffman_example_selected(self, index):
        """Обработка выбора примера текста."""
        if 0 <= index < len(self.huffman_examples):
            example = self.huffman_examples[index]
            self.huffman_text_input.setPlainText(example["text"])
            self.huffman_current_text = example["text"]
    
    def _load_huffman_example(self):
        """Загружает выбранный пример текста."""
        index = self.huffman_examples_combo.currentIndex()
        if 0 <= index < len(self.huffman_examples):
            example = self.huffman_examples[index]
            self.huffman_text_input.setPlainText(example["text"])
            self.huffman_current_text = example["text"]
            self._log(f"📖 Загружен пример: {example['name']}")
            self._log(f"📝 {example['description']}")
            self._update_huffman_buttons_state()
    
    def _huffman_analyze_frequencies(self):
        """Анализирует частоты символов в тексте."""
        text = self.huffman_text_input.toPlainText().strip()
        
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст для анализа")
            return
        
        self.huffman_current_text = text
        self.current_algorithm = HuffmanCoding(text)
        
        # Вычисляем частоты
        frequencies = self.current_algorithm.calculate_frequencies()
        
        # Визуализируем частоты
        self.huffman_visualizer.visualize_frequencies(frequencies)
        self._fit_to_content()
        
        # Обновляем статистику
        stats_text = (
            f"📊 Анализ частот завершен:\n\n"
            f"• Всего символов: {len(text)}\n"
            f"• Уникальных символов: {len(frequencies)}\n"
            f"• Энтропия (теоретическая): {self._calculate_entropy(frequencies, len(text)):.2f} бит/символ\n"
            f"• Сжатие возможно до: ≤ {len(text) * self._calculate_entropy(frequencies, len(text)):.0f} бит"
        )
        self.huffman_stats_label.setText(stats_text)
        
        # Включаем следующую кнопку
        self.huffman_build_tree_btn.setEnabled(True)
        self._log(f"📊 Проанализирован текст: {len(text)} символов, {len(frequencies)} уникальных")
    
    def _huffman_build_tree(self):
        """Строит дерево Хаффмана."""
        try:
            if not self.current_algorithm:
                QMessageBox.warning(self, "Ошибка", "Сначала проанализируйте текст")
                return
            
            # Проверяем размер текста
            text_len = len(self.huffman_current_text)
            
            # Строим дерево
            self.current_algorithm.build_huffman_tree()
            tree_structure = self.current_algorithm.get_tree_structure()
            
            if tree_structure:
                # Визуализируем дерево
                success = self.huffman_visualizer.visualize_huffman_tree(
                    tree_structure, 
                    self.tree_visualizer if hasattr(self, 'tree_visualizer') else None
                )
                
                if success:
                    self._fit_to_content()
                    
                    # Обновляем статистику
                    tree_height = self._calculate_tree_height(tree_structure)
                    stats_text = (
                        f"🌳 Дерево Хаффмана построено:\n\n"
                        f"• Корень: {tree_structure.get('frequency', 0)}\n"
                        f"• Узлов: {self.huffman_visualizer._count_tree_nodes(tree_structure)}\n"
                        f"• Высота: {tree_height}\n"
                        f"• Уникальных символов: {len(self.current_algorithm.frequencies)}"
                    )
                    self.huffman_stats_label.setText(stats_text)
                    
                    self.huffman_generate_codes_btn.setEnabled(True)
                    self._log("🌳 Дерево Хаффмана построено!")
                else:
                    self._log("⚠️ Дерево визуализировано в упрощенном формате")
            else:
                self._log("❌ Не удалось построить дерево")
            
            self._update_huffman_buttons_state()
            
        except Exception as e:
            self._log(f"❌ Ошибка: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")
    
    def _huffman_generate_codes(self):
        """Генерирует коды Хаффмана."""
        if not self.current_algorithm:
            QMessageBox.warning(self, "Ошибка", "Сначала постройте дерево")
            return
        
        if not hasattr(self.current_algorithm, 'root') or not self.current_algorithm.root:
            QMessageBox.warning(self, "Ошибка", "Сначала постройте дерево")
            return
        
        try:
            # Генерируем коды - используем правильный метод
            if hasattr(self.current_algorithm, 'generate_huffman_codes_iterative'):
                self.current_algorithm.generate_huffman_codes_iterative()
            else:
                # Альтернативный вариант
                self.current_algorithm.generate_huffman_codes_recursive()
            
            # Получаем таблицу кодов
            if hasattr(self.current_algorithm, 'get_codes_table'):
                self.huffman_codes_table = self.current_algorithm.get_codes_table()
            else:
                # Создаем таблицу кодов вручную
                self.huffman_codes_table = []
                for symbol, code in self.current_algorithm.codes.items():
                    freq = self.current_algorithm.frequencies.get(symbol, 0)
                    self.huffman_codes_table.append({
                        "symbol": symbol,
                        "code": code,
                        "frequency": freq,
                        "savings": 8 - len(code)
                    })
            
            # Визуализируем таблицу кодов
            if hasattr(self, 'huffman_visualizer'):
                self.huffman_visualizer.visualize_codes_table(self.huffman_codes_table)
                self._fit_to_content()
            
            # Включаем кнопки
            if hasattr(self, 'huffman_encode_btn'):
                self.huffman_encode_btn.setEnabled(True)
            if hasattr(self, 'huffman_decode_btn'):
                self.huffman_decode_btn.setEnabled(True)
            
            # Обновляем статистику
            if self.huffman_codes_table:
                total_freq = sum(item["frequency"] for item in self.huffman_codes_table)
                if total_freq > 0:
                    avg_length = sum(len(item["code"]) * item["frequency"] for item in self.huffman_codes_table) / total_freq
                else:
                    avg_length = 0
                    
                stats_text = (
                    f"🔤 Коды Хаффмана сгенерированы:\n\n"
                    f"• Всего кодов: {len(self.huffman_codes_table)}\n"
                    f"• Средняя длина кода: {avg_length:.2f} бит/символ\n"
                    f"• Макс. длина кода: {max(len(item['code']) for item in self.huffman_codes_table)} бит\n"
                    f"• Мин. длина кода: {min(len(item['code']) for item in self.huffman_codes_table)} бит"
                )
            else:
                stats_text = "❌ Не удалось сгенерировать коды"
            
            if hasattr(self, 'huffman_stats_label'):
                self.huffman_stats_label.setText(stats_text)
            
            if hasattr(self, '_log'):
                self._log("🔤 Сгенерированы коды Хаффмана")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при генерации кодов: {str(e)}")
            print(f"Error generating Huffman codes: {e}")
    def _update_huffman_stats(self, data):
        """Обновляет текстовую статистику в интерфейсе Хаффмана."""
        try:
            if not data:
                return
                
            # Если пришли частоты символов
            if "frequencies" in data:
                freqs = data["frequencies"]
                unique_chars = len(freqs)
                total_chars = sum(freqs.values())
                
                # Рассчитываем энтропию (если есть метод)
                entropy_text = ""
                if hasattr(self, "_calculate_entropy"):
                    entropy = self._calculate_entropy(freqs)
                    entropy_text = f"\nЭнтропия: {entropy:.3f} бит/символ"
                
                stats_msg = (
                    f"📊 Частоты рассчитаны:\n"
                    f"Символов: {total_chars}, Уникальных: {unique_chars}"
                    f"{entropy_text}"
                )
                self.huffman_stats_label.setText(stats_msg)
                self._log(f"📊 {stats_msg.splitlines()[0]}")
                
        except Exception as e:
            print(f"Ошибка в _update_huffman_stats: {e}")
    def _complete_huffman_tree_building(self):
        """Завершает построение дерева Хаффмана и переходит к кодированию."""
        try:
            # Останавливаем автоматический режим
            self._pause_auto_mode()
            
            # Проверяем, что дерево построено
            if self.current_algorithm and hasattr(self.current_algorithm, 'root') and self.current_algorithm.root:
                self._log("✅ Дерево Хаффмана построено. Продолжаем кодирование...")
                
                # Генерируем коды с использованием существующего метода
                if hasattr(self.current_algorithm, 'generate_huffman_codes_iterative'):
                    codes = self.current_algorithm.generate_huffman_codes_iterative()
                    self._log(f"✅ Сгенерировано {len(codes)} кодов Хаффмана")
                
                # Кодируем текст
                encoded_text = self.current_algorithm.encode_text()
                
                # Отображаем результаты
                if hasattr(self.current_algorithm, 'get_compression_stats'):
                    stats = self.current_algorithm.get_compression_stats()
                    self.huffman_visualizer.visualize_encoding_result(stats)
                
                self._log("✅ Текст успешно закодирован алгоритмом Хаффмана")
            else:
                self._log("❌ Дерево Хаффмана не было построено")
                QMessageBox.warning(self, "Ошибка", "Не удалось построить дерево Хаффмана")
                
        except Exception as e:
            self._log(f"❌ Ошибка при завершении построения дерева: {str(e)}")
    def _huffman_encode_text(self):
        """Выполняет кодирование текста алгоритмом Хаффмана."""
        try:
            if not self.current_algorithm:
                QMessageBox.warning(self, "Ошибка", "Алгоритм Хаффмана не инициализирован")
                return
            
            # Шаг 1: Убедимся, что дерево построено
            if not hasattr(self.current_algorithm, 'root') or not self.current_algorithm.root:
                self._log("🔧 Построение дерева Хаффмана...")
                # Загружаем алгоритм в движок для пошагового построения дерева
                self.engine.load_algorithm(self.current_algorithm)
                
                # Запускаем автоматический режим для визуализации построения дерева
                self._start_auto_mode()
                
                # Ждем завершения построения дерева
                self._complete_huffman_tree_building
                return
            
            # Шаг 2: Генерация кодов (если еще не сгенерированы)
            if not hasattr(self.current_algorithm, 'codes') or not self.current_algorithm.codes:
                self._log("🔧 Генерация кодов Хаффмана...")
                self.current_algorithm.generate_huffman_codes_iterative()
            
            # Шаг 3: Кодирование текста
            self._log("🔧 Кодирование текста...")
            encoded_text = self.current_algorithm.encode_text()
            
            # Шаг 4: Отображение результатов
            if hasattr(self.current_algorithm, 'get_compression_stats'):
                stats = self.current_algorithm.get_compression_stats()
                self.huffman_visualizer.visualize_encoding_result(stats)
            
            self._log("✅ Текст успешно закодирован алгоритмом Хаффмана")
            
        except ZeroDivisionError:
            self._log("❌ Ошибка: compressed_bits равен 0. Возможно, дерево не построено.")
            QMessageBox.warning(self, "Ошибка", 
                            "Не удалось закодировать текст. Дерево Хаффмана не построено или содержит ошибки.")
        except Exception as e:
            self._log(f"❌ Ошибка при кодировании текста: {str(e)}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось закодировать текст: {str(e)}")
    
    def _huffman_decode_text(self):
        """Декодирует текст."""
        if not self.current_algorithm or not hasattr(self.current_algorithm, 'decode_text'):
            QMessageBox.warning(self, "Ошибка", "Сначала закодируйте текст")
            return
        
        # Декодируем текст
        decoded_text = self.current_algorithm.decode_text()
        
        # Проверяем корректность
        is_correct = decoded_text == self.huffman_current_text
        
        if is_correct:
            self._log("✅ Декодирование успешно! Текст восстановлен без ошибок.")
            QMessageBox.information(self, "Успех", "Текст успешно декодирован и соответствует оригиналу!")
        else:
            self._log("❌ Ошибка декодирования! Текст не соответствует оригиналу.")
            QMessageBox.warning(self, "Ошибка", "Декодированный текст не совпадает с оригиналом")
    
    def _huffman_full_process(self):
        """Выполняет полный процесс сжатия с пошаговой визуализацией через Engine."""
        text = self.huffman_text_input.toPlainText().strip()
        
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст для сжатия")
            return
        
        try:
            # Проверяем размер текста (безопасная проверка)
            if len(text) > 500:
                reply = QMessageBox.question(
                    self, "Внимание",
                    f"Текст большой ({len(text)} символов).\n"
                    f"Рекомендуется использовать текст до 500 символов.\n\n"
                    f"Продолжить?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # Сбрасываем предыдущий алгоритм
            self._reset_algorithm()
            
            # 1. Создаем алгоритм Хаффмана
            self.current_algorithm = HuffmanCoding(text)
            self.huffman_current_text = text
            
            # 2. Рассчитываем частоты и показываем начальный экран
            frequencies = self.current_algorithm.calculate_frequencies()
            self.scene.clear()
            self.huffman_visualizer.visualize_frequencies(frequencies)
            
            # 3. Устанавливаем специальный режим для полного процесса
            self._is_full_huffman_process = True
            self._huffman_process_step = 0  # 0-частоты, 1-построение дерева, 2-генерация кодов, 3-результат
            
            # 4. Логируем начало процесса
            self._log("🚀 Начат полный процесс сжатия Хаффмана")
            self._log(f"📊 Анализируемый текст: {text[:50]}{'...' if len(text) > 50 else ''}")
            self._log(f"📊 Уникальных символов: {len(frequencies)}")
            self._log(f"📊 Общий размер: {len(text)} символов")
            
            # 5. Загружаем алгоритм в движок для пошаговой визуализации
            self.engine.load_algorithm(self.current_algorithm)
            
            # 6. Настраиваем интерактивную панель
            self._update_huffman_buttons_state()
            
            # 7. Запускаем автоматический режим для анимации
            self._start_auto_mode()
            
            # 8. Подгоняем масштаб
            QTimer.singleShot(300, self._fit_to_content)
            
        except Exception as e:
            self._log(f"❌ Ошибка при запуске полного процесса: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка запуска: {str(e)}")
            # Сбрасываем флаги в случае ошибки
            if hasattr(self, '_is_full_huffman_process'):
                self._is_full_huffman_process = False
    
    def _clear_huffman(self):
        """Очищает все данные Хаффмана."""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Очистить все данные кодирования Хаффмана?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Очищаем поля ввода
            self.huffman_text_input.clear()
            
            # Очищаем данные
            self.huffman_codes_table = []
            self.huffman_current_text = ""
            self.current_algorithm = None
            
            # Очищаем сцену
            self.scene.clear()
            
            # Сбрасываем кнопки
            self._update_huffman_buttons_state()
            
            # Сбрасываем статистику
            self.huffman_stats_label.setText("ℹ️ Введите текст и выполните операции")
            
            self._log("🗑️ Данные Хаффмана очищены")
    
    def _export_huffman_codes(self):
        """Экспортирует таблицу кодов Хаффмана."""
        if not self.huffman_codes_table:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return
        
        # Создаем текст для экспорта
        export_text = "=" * 50 + "\n"
        export_text += "ТАБЛИЦА КОДОВ ХАФФМАНА\n"
        export_text += "=" * 50 + "\n\n"
        export_text += f"Текст: {self.huffman_current_text[:50]}...\n"
        export_text += f"Длина: {len(self.huffman_current_text)} символов\n"
        export_text += f"Уникальных символов: {len(self.huffman_codes_table)}\n"
        export_text += "\n" + "=" * 50 + "\n"
        export_text += "СИМВОЛ | КОД | ЧАСТОТА | БИТ/СИМВОЛ | ЭКОНОМИЯ\n"
        export_text += "-" * 50 + "\n"
        
        total_freq = sum(item["frequency"] for item in self.huffman_codes_table)
        total_savings = 0
        
        for item in sorted(self.huffman_codes_table, key=lambda x: (-x["frequency"], x["code"])):
            symbol = item["symbol"]
            if symbol == " ":
                symbol_display = "[space]"
            elif symbol == "\n":
                symbol_display = "\\n"
            elif symbol == "\t":
                symbol_display = "\\t"
            else:
                symbol_display = symbol
            
            savings = item["savings"]
            total_savings += savings * item["frequency"]
            
            export_text += f"'{symbol_display}'\t{item['code']}\t{item['frequency']} ({item['frequency']/total_freq:.1%})\t8 → {len(item['code'])}\t{savings:+d} бит\n"
        
        export_text += "\n" + "=" * 50 + "\n"
        export_text += "СТАТИСТИКА:\n"
        export_text += f"• Общая экономия: {total_savings} бит\n"
        export_text += f"• Средняя длина кода: {sum(len(item['code']) * item['frequency'] for item in self.huffman_codes_table) / total_freq:.2f} бит/символ\n"
        export_text += f"• Теоретический предел сжатия: {total_freq * 8 - total_savings} бит\n"
        export_text += "=" * 50
        
        # Копируем в буфер обмена
        clipboard = QApplication.clipboard()
        clipboard.setText(export_text)
        
        QMessageBox.information(self, "Экспорт", "Таблица кодов скопирована в буфер обмена")
        self._log("📋 Таблица кодов экспортирована")
    
    def _copy_huffman_code(self):
        """Копирует закодированный текст."""
        if not self.current_algorithm or not hasattr(self.current_algorithm, 'encoded_text'):
            QMessageBox.warning(self, "Ошибка", "Нет закодированного текста")
            return
        
        encoded_text = self.current_algorithm.encoded_text
        if not encoded_text:
            QMessageBox.warning(self, "Ошибка", "Сначала закодируйте текст")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(encoded_text)
        
        QMessageBox.information(self, "Копирование", "Закодированный текст скопирован в буфер обмена")
        self._log("📋 Закодированный текст скопирован")
    
    def _update_huffman_buttons_state(self):
        """Обновляет состояние кнопок Хаффмана."""
        has_text = bool(self.huffman_text_input.toPlainText().strip())
        has_algorithm = bool(self.current_algorithm)
        
        # Базовые кнопки
        self.huffman_analyze_btn.setEnabled(has_text)
        self.huffman_full_process_btn.setEnabled(has_text)
        
        # Зависимые кнопки (изначально выключены)
        self.huffman_build_tree_btn.setEnabled(False)
        self.huffman_generate_codes_btn.setEnabled(False)
        self.huffman_encode_btn.setEnabled(False)
        self.huffman_decode_btn.setEnabled(False)
        self.huffman_export_btn.setEnabled(False)
        self.huffman_copy_btn.setEnabled(False)
        
        if has_algorithm:
            # Проверяем состояние алгоритма
            if hasattr(self.current_algorithm, 'frequencies') and self.current_algorithm.frequencies:
                self.huffman_build_tree_btn.setEnabled(True)
            
            if hasattr(self.current_algorithm, 'root') and self.current_algorithm.root:
                self.huffman_generate_codes_btn.setEnabled(True)
            
            if hasattr(self.current_algorithm, 'codes') and self.current_algorithm.codes:
                self.huffman_encode_btn.setEnabled(True)
                self.huffman_decode_btn.setEnabled(True)
                self.huffman_export_btn.setEnabled(True)
            
            if hasattr(self.current_algorithm, 'encoded_text') and self.current_algorithm.encoded_text:
                self.huffman_copy_btn.setEnabled(True)
    
    def _calculate_entropy(self, frequencies, total_chars):
        """Вычисляет энтропию Шеннона."""
        if total_chars == 0:
            return 0
        
        entropy = 0
        for freq in frequencies.values():
            probability = freq / total_chars
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _calculate_tree_height(self, tree_structure):
        """Вычисляет высоту дерева."""
        if not tree_structure:
            return 0
        
        left_height = self._calculate_tree_height(tree_structure.get("left"))
        right_height = self._calculate_tree_height(tree_structure.get("right"))
        
        return 1 + max(left_height, right_height)
    
    def _calculate_average_path_length(self, tree_structure, current_depth=0):
        """Вычисляет среднюю длину пути в дереве."""
        if not tree_structure:
            return 0
        
        # Если это лист (символ)
        if tree_structure.get("is_leaf"):
            frequency = tree_structure.get("frequency", 1)
            return current_depth * frequency
        
        # Рекурсивно вычисляем для левого и правого поддеревьев
        left_length = self._calculate_average_path_length(tree_structure.get("left"), current_depth + 1)
        right_length = self._calculate_average_path_length(tree_structure.get("right"), current_depth + 1)
        
        return left_length + right_length               

    def closeEvent(self, event):
        """Обработка закрытия приложения."""
        self.engine.pause()
        event.accept()