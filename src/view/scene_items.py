"""
Элементы визуализации для QGraphicsScene с анимациями.
"""
from PyQt6.QtWidgets import QGraphicsObject, QGraphicsTextItem
from PyQt6.QtGui import QBrush, QColor, QFont, QRadialGradient, QPen, QPainter
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, QPropertyAnimation, pyqtProperty, QEasingCurve


class ArrayCircleItem(QGraphicsObject):
    """Круг для визуализации элемента массива с анимациями."""
    
    def __init__(self, x, y, value, index, radius=25):
        super().__init__()
        self.index = index
        self.value = value
        self.radius = radius
        
        self.default_color = QColor("#5A9BD5")  # Синий
        self.highlight_color = QColor("#FFD700")  # Желтый
        self.swap_color = QColor("#FF6B6B")  # Красный
        self.complete_color = QColor("#7EE081")  # Зеленый
        
        self._current_color = self.default_color
        
        self.setPos(x, y)
        
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(500)
        
        self.color_animation = QPropertyAnimation(self, b"circleColor")
        self.color_animation.setDuration(300)
        
        self.bounce_timer = QTimer()
        self.bounce_timer.timeout.connect(self._bounce_step)
        self.bounce_steps = 0
        self.original_y = y

    def boundingRect(self):
        return QRectF(0, 0, self.radius * 2, self.radius * 2)
        
    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        gradient = QRadialGradient(self.radius, self.radius, self.radius)
        gradient.setColorAt(0, self._current_color.lighter(150))
        gradient.setColorAt(0.7, self._current_color)
        gradient.setColorAt(1, self._current_color.darker(150))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self._current_color.darker(200), 2))
        painter.drawEllipse(0, 0, self.radius * 2, self.radius * 2)
        
        painter.setPen(QColor("white"))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, str(self.value))

    @pyqtProperty(QColor)
    def circleColor(self):
        return self._current_color
        
    @circleColor.setter
    def circleColor(self, value):
        self._current_color = value
        self.update()

    def highlight(self, color):
        if isinstance(color, str):
            target_color = QColor(color)
        else:
            target_color = color
            
        self.color_animation.stop()
        self.color_animation.setStartValue(self._current_color)
        self.color_animation.setEndValue(target_color)
        self.color_animation.start()

    def reset_color(self):
        self.color_animation.stop()
        self.color_animation.setStartValue(self._current_color)
        self.color_animation.setEndValue(self.default_color)
        self.color_animation.start()

    def animate_move(self, new_x, new_y, duration=500):
        self.pos_animation.stop()
        self.pos_animation.setDuration(duration)
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(QPointF(new_x, new_y))
        self.pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.pos_animation.start()

    def bounce_animation(self):
        self.bounce_steps = 0
        self.original_y = self.y()
        self.bounce_timer.start(50)

    def _bounce_step(self):
        if self.bounce_steps >= 8:
            self.bounce_timer.stop()
            self.setY(self.original_y)
            return
            
        import math
        bounce_height = 15
        progress = self.bounce_steps / 8.0
        bounce_offset = math.sin(progress * math.pi) * bounce_height
        
        self.setY(self.original_y - bounce_offset)
        self.bounce_steps += 1

    def update_value(self, value):
        self.value = value
        self.update()

    def __str__(self):
        return f"ArrayCircleItem(index={self.index}, value={self.value})"


class TreeNodeItem(ArrayCircleItem):
    """Узел дерева с поддержкой связей и иерархии."""
    
    def __init__(self, x, y, value, radius=25):
        super().__init__(x, y, value, -1, radius)
        self.children = []
        self.parent = None
        self.level = 0
        self.tree_connections = []
        
        # Цвета для деревьев
        self.default_color = QColor("#9B59B6")  # Фиолетовый для узлов дерева
        self._current_color = self.default_color

    def add_child(self, child_node):
        child_node.parent = self
        child_node.level = self.level + 1
        self.children.append(child_node)

    def add_connection(self, connection):
        self.tree_connections.append(connection)


class TreeConnectionItem(QGraphicsObject):
    """Соединение между узлами дерева."""
    
    def __init__(self, start_node, end_node):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setZValue(-1)  # Линии под узлами
        
        # Добавляем ссылку на соединение в узлы
        start_node.add_connection(self)
        end_node.add_connection(self)

    def boundingRect(self):
        start_pos = self.start_node.scenePos()
        end_pos = self.end_node.scenePos()
        
        padding = 10
        x1 = min(start_pos.x(), end_pos.x()) - padding
        y1 = min(start_pos.y(), end_pos.y()) - padding
        x2 = max(start_pos.x(), end_pos.x()) + padding
        y2 = max(start_pos.y(), end_pos.y()) + padding
        
        return QRectF(x1, y1, x2 - x1, y2 - y1)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Более толстая и контрастная линия для дерева
        painter.setPen(QPen(QColor("#34495E"), 3, Qt.PenStyle.SolidLine))
        
        start_pos = self.start_node.scenePos()
        end_pos = self.end_node.scenePos()
        
        # Смещаем начало и конец линии к краям кругов
        start_radius = self.start_node.radius
        end_radius = self.end_node.radius
        
        # Вычисляем направление вектора
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()
        distance = (dx**2 + dy**2)**0.5
        
        if distance > 0:
            # Нормализуем и умножаем на радиусы
            dx_unit = dx / distance
            dy_unit = dy / distance
            
            start_x = start_pos.x() + dx_unit * start_radius
            start_y = start_pos.y() + dy_unit * start_radius
            end_x = end_pos.x() - dx_unit * end_radius
            end_y = end_pos.y() - dy_unit * end_radius
            
            painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))