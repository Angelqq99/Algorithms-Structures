import math
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem, QGraphicsItemGroup
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPen, QBrush, QFont

class HashVisualizer:
    """
    Визуализатор хэш-таблицы.
    Рисует полное состояние таблицы за один проход (без анимации перемещения).
    """
    def __init__(self, scene):
        self.scene = scene
        # Константы для отрисовки
        self.CELL_SIZE = 60
        self.SPACING = 10
        self.START_X = 50
        self.START_Y = 100
        
        # Цвета
        self.COLOR_INDEX = QColor("#E0E0E0")      # Серый для индексов
        self.COLOR_EMPTY = QColor("#F5F5F5")      # Светло-серый для пустых ячеек
        self.COLOR_FILLED = QColor("#81C784")     # Зеленый для заполненных
        self.COLOR_COLLISION = QColor("#FFB74D")  # Оранжевый (если нужно выделить)
        self.COLOR_BORDER = QColor("#424242")
        self.FONT = QFont("Arial", 12)
        self.FONT_SMALL = QFont("Arial", 10)

    def draw_snapshot(self, algo):
        """
        Полная перерисовка таблицы на основе данных алгоритма.
        :param algo: экземпляр класса HashTable
        """
        self.scene.clear()
        
        table_data = algo._get_table_copy()
        method = algo.collision_method
        
        if method == "chaining":
            self._draw_chaining(table_data)
        else:
            self._draw_open_addressing(table_data)

    def _draw_open_addressing(self, table):
        """Отрисовка для открытой адресации (линейный массив)."""
        count = len(table)
        
        # Рисуем заголовок
        title = QGraphicsTextItem("Хэш-таблица (Открытая адресация)")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setPos(self.START_X, self.START_Y - 60)
        self.scene.addItem(title)

        for i, val in enumerate(table):
            x = self.START_X + i * (self.CELL_SIZE + self.SPACING)
            y = self.START_Y
            
            # 1. Ячейка индекса (сверху)
            idx_rect = QGraphicsRectItem(x, y - 30, self.CELL_SIZE, 30)
            idx_rect.setBrush(QBrush(self.COLOR_INDEX))
            idx_rect.setPen(QPen(self.COLOR_BORDER))
            self.scene.addItem(idx_rect)
            
            idx_text = QGraphicsTextItem(str(i))
            idx_text.setFont(self.FONT_SMALL)
            # Центрируем текст
            tx = x + (self.CELL_SIZE - idx_text.boundingRect().width()) / 2
            ty = y - 30 + (30 - idx_text.boundingRect().height()) / 2
            idx_text.setPos(tx, ty)
            self.scene.addItem(idx_text)

            # 2. Ячейка значения (БЕЛЫЙ прямоугольник)
            val_rect = QGraphicsRectItem(x, y, self.CELL_SIZE, self.CELL_SIZE)
            color = self.COLOR_EMPTY if val is None else self.COLOR_FILLED
            val_rect.setBrush(QBrush(color))
            val_rect.setPen(QPen(self.COLOR_BORDER, 1.5))
            self.scene.addItem(val_rect)

            # Текст значения (внутри белого прямоугольника)
            if val is not None:
                text_str = str(val)
                val_text = QGraphicsTextItem(text_str)
                val_text.setFont(self.FONT)
                vx = x + (self.CELL_SIZE - val_text.boundingRect().width()) / 2
                vy = y + (self.CELL_SIZE - val_text.boundingRect().height()) / 2
                val_text.setPos(vx, vy)
                self.scene.addItem(val_text)

    def _draw_chaining(self, table):
        """Отрисовка для метода цепочек (вертикальные списки)."""
        count = len(table)
        
        # Рисуем заголовок
        title = QGraphicsTextItem("Хэш-таблица (Метод цепочек)")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setPos(self.START_X, self.START_Y - 60)
        self.scene.addItem(title)

        for i, chain in enumerate(table):
            # Координаты столбца
            x = self.START_X + i * (self.CELL_SIZE + self.SPACING * 2)
            y = self.START_Y

            # 1. Заголовок бакета (индекс) - БЕЛЫЙ прямоугольник
            bucket_rect = QGraphicsRectItem(x, y, self.CELL_SIZE, self.CELL_SIZE)
            bucket_rect.setBrush(QBrush(self.COLOR_EMPTY if not chain else self.COLOR_INDEX))
            bucket_rect.setPen(QPen(self.COLOR_BORDER, 1.5))
            self.scene.addItem(bucket_rect)

            idx_text = QGraphicsTextItem(f"[{i}]")
            idx_text.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            tx = x + (self.CELL_SIZE - idx_text.boundingRect().width()) / 2
            ty = y + (self.CELL_SIZE - idx_text.boundingRect().height()) / 2
            idx_text.setPos(tx, ty)
            self.scene.addItem(idx_text)

            # 2. Цепочка элементов (вниз)
            if chain: # Если в бакете есть элементы
                current_y = y + self.CELL_SIZE + 10 # Отступ первой стрелки
                prev_x = x + self.CELL_SIZE / 2
                prev_y = y + self.CELL_SIZE
                
                for key in chain:
                    # Рисуем стрелку вниз
                    line = QGraphicsLineItem(prev_x, prev_y, prev_x, current_y)
                    line.setPen(QPen(Qt.GlobalColor.black, 1))
                    self.scene.addItem(line)
                    
                    # Рисуем узел - БЕЛЫЙ прямоугольник
                    node_rect = QGraphicsRectItem(x, current_y, self.CELL_SIZE, self.CELL_SIZE)
                    node_rect.setBrush(QBrush(self.COLOR_FILLED))
                    node_rect.setPen(QPen(self.COLOR_BORDER, 1.5))
                    self.scene.addItem(node_rect)
                    
                    # Текст узла (внутри белого прямоугольника)
                    key_text = QGraphicsTextItem(str(key))
                    key_text.setFont(self.FONT)
                    kx = x + (self.CELL_SIZE - key_text.boundingRect().width()) / 2
                    ky = current_y + (self.CELL_SIZE - key_text.boundingRect().height()) / 2
                    key_text.setPos(kx, ky)
                    self.scene.addItem(key_text)
                    
                    prev_y = current_y + self.CELL_SIZE
                    current_y += self.CELL_SIZE + 10 # Сдвиг для следующего

                # Рисуем NULL/Землю в конце
                line = QGraphicsLineItem(prev_x, prev_y, prev_x, current_y)
                self.scene.addItem(line)
                
                null_line1 = QGraphicsLineItem(x + 10, current_y, x + self.CELL_SIZE - 10, current_y)
                null_line2 = QGraphicsLineItem(x + 20, current_y + 4, x + self.CELL_SIZE - 20, current_y + 4)
                self.scene.addItem(null_line1)
                self.scene.addItem(null_line2)