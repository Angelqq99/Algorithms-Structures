"""
Элементы визуализации для QGraphicsScene с анимациями.
"""
from PyQt6.QtWidgets import QGraphicsObject, QGraphicsView
from PyQt6.QtGui import QBrush, QColor, QFont, QRadialGradient, QPen, QPainter, QWheelEvent
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, QPropertyAnimation, pyqtProperty, QEasingCurve


# ==========================
# 🔍 QGraphicsView с масштабированием колесиком
# ==========================
class ZoomableGraphicsView(QGraphicsView):
    """QGraphicsView с поддержкой масштабирования колесиком мыши."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.scale_factor = 1.15
        self.min_zoom = 0.2
        self.max_zoom = 4.0
        self._current_scale = 1.0

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            super().wheelEvent(event)
            return
        zoom_in = event.angleDelta().y() > 0
        factor = self.scale_factor if zoom_in else 1 / self.scale_factor
        new_scale = self._current_scale * factor
        if self.min_zoom <= new_scale <= self.max_zoom:
            self.scale(factor, factor)
            self._current_scale = new_scale


# ==========================
# 🔵 Круг для элементов массива
# ==========================
class ArrayCircleItem(QGraphicsObject):
    """Круг для визуализации элемента массива с анимациями."""
    
    def __init__(self, x, y, value, index, radius=40):
        super().__init__()
        self.index = index
        self.value = value
        self.radius = radius
        
        self.default_color = QColor("#5A9BD5")
        self.highlight_color = QColor("#FFD700")
        self.swap_color = QColor("#FF6B6B")
        self.complete_color = QColor("#7EE081")
        
        self._current_color = self.default_color
        
        self.setPos(x, y)
        self.setZValue(1)
        
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(500)
        
        self.color_animation = QPropertyAnimation(self, b"circleColor")
        self.color_animation.setDuration(300)
        
        self.bounce_timer = QTimer()
        self.bounce_timer.timeout.connect(self._bounce_step)
        self.bounce_steps = 0
        self.original_y = y
        self._is_valid = True

    def __del__(self):
        self._is_valid = False

    def boundingRect(self):
        if not self._is_valid:
            return QRectF(0, 0, 0, 0)
        return QRectF(0, 0, self.radius * 2, self.radius * 2)
        
    def paint(self, painter, option, widget):
        if not self._is_valid:
            return
            
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        gradient = QRadialGradient(self.radius, self.radius, self.radius)
        gradient.setColorAt(0, self._current_color.lighter(130))
        gradient.setColorAt(0.7, self._current_color)
        gradient.setColorAt(1, self._current_color.darker(130))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self._current_color.darker(200), 3))
        painter.drawEllipse(0, 0, self.radius * 2, self.radius * 2)
        
        font = QFont()
        font.setPointSizeF(self.radius * 0.6)
        font.setBold(True)
        painter.setFont(font)

        text_rect = QRectF(0, 0, self.radius * 2, self.radius * 2)
        painter.setPen(QColor(30, 30, 30, 160))
        painter.drawText(text_rect.translated(3, 3), Qt.AlignmentFlag.AlignCenter, str(self.value))
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(self.value))

    @pyqtProperty(QColor)
    def circleColor(self):
        return self._current_color
        
    @circleColor.setter
    def circleColor(self, value):
        if self._is_valid:
            self._current_color = value
            self.update()

    def highlight(self, color):
        if not self._is_valid or not self.scene():
            return
        target_color = QColor(color) if isinstance(color, str) else color
        self.color_animation.stop()
        self.color_animation.setStartValue(self._current_color)
        self.color_animation.setEndValue(target_color)
        self.color_animation.start()

    def reset_color(self):
        if not self._is_valid or not self.scene():
            return
        self.color_animation.stop()
        self.color_animation.setStartValue(self._current_color)
        self.color_animation.setEndValue(self.default_color)
        self.color_animation.start()

    def animate_move(self, new_x, new_y, duration=500):
        if not self._is_valid or not self.scene():
            return
        self.pos_animation.stop()
        self.pos_animation.setDuration(duration)
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(QPointF(new_x, new_y))
        self.pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.pos_animation.start()

    def bounce_animation(self):
        if not self._is_valid or not self.scene():
            return
        self.bounce_steps = 0
        self.original_y = self.y()
        self.bounce_timer.start(50)

    def _bounce_step(self):
        if not self._is_valid or not self.scene():
            self.bounce_timer.stop()
            return
        if self.bounce_steps >= 8:
            self.bounce_timer.stop()
            self.setY(self.original_y)
            return
        import math
        bounce_height = 20
        progress = self.bounce_steps / 8.0
        bounce_offset = math.sin(progress * math.pi) * bounce_height
        self.setY(self.original_y - bounce_offset)
        self.bounce_steps += 1

    def update_value(self, value):
        if self._is_valid:
            self.value = value
            self.update()


# ==========================
# 🌳 Узел дерева (увеличенный)
# ==========================
class TreeNodeItem(ArrayCircleItem):
    """Крупный узел дерева."""
    
    def __init__(self, x, y, value, radius=80):  # Увеличен радиус до 80
        super().__init__(x, y, value, -1, radius)
        self.children = []
        self.parent = None
        self.level = 0
        self.tree_connections = []
        self.subtree_width = 1
        
        # Цвета для различных типов деревьев
        self.default_color = QColor("#6C2EB5")  # фиолетовый по умолчанию
        self.avl_color = QColor("#2E8B57")      # зеленый для AVL
        self.rb_red_color = QColor("#DC143C")   # красный для RBT
        self.rb_black_color = QColor("#2F4F4F") # темный для RBT
        self.splay_color = QColor("#FF8C00")    # оранжевый для Splay
        self.treap_color = QColor("#9370DB")    # фиолетовый для Treap
        self.b_tree_color = QColor("#20B2AA")   # бирюзовый для B-Tree
        
        self._current_color = self.default_color
        self.setZValue(1)

    def paint(self, painter, option, widget):
        if not self._is_valid:
            return
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QRadialGradient(self.radius, self.radius, self.radius)
        gradient.setColorAt(0, self._current_color.lighter(130))
        gradient.setColorAt(0.6, self._current_color)
        gradient.setColorAt(1, self._current_color.darker(160))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self._current_color.darker(200), 4))  # Увеличена толщина обводки
        painter.drawEllipse(0, 0, self.radius * 2, self.radius * 2)

        font = QFont()
        font.setPointSizeF(self.radius * 0.5)  # Увеличен размер шрифта
        font.setBold(True)
        painter.setFont(font)

        text_rect = QRectF(0, 0, self.radius * 2, self.radius * 2)
        
        # Тень текста
        painter.setPen(QColor(30, 30, 30, 160))
        painter.drawText(text_rect.translated(2, 2), Qt.AlignmentFlag.AlignCenter, str(self.value))
        
        # Основной текст
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(self.value))

    def set_tree_type_color(self, tree_type):
        """Устанавливает цвет в зависимости от типа дерева."""
        color_map = {
            'AVL': self.avl_color,
            'RedBlackTree_RED': self.rb_red_color,
            'RedBlackTree_BLACK': self.rb_black_color,
            'SplayTree': self.splay_color,
            'Treap': self.treap_color,
            'BTree': self.b_tree_color
        }
        
        if tree_type in color_map:
            self.default_color = color_map[tree_type]
            self._current_color = self.default_color
            self.update()

    def add_child(self, child_node):
        if (self._is_valid and child_node and child_node != self and 
            hasattr(child_node, '_is_valid') and child_node._is_valid):
            child_node.parent = self
            child_node.level = self.level + 1
            self.children.append(child_node)

    def add_connection(self, connection):
        if connection and self._is_valid:
            self.tree_connections.append(connection)


# ==========================
# 🔗 Соединение между узлами
# ==========================
class TreeConnectionItem(QGraphicsObject):
    """Соединение между узлами дерева."""
    
    def __init__(self, start_node, end_node):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setZValue(-1)
        self._is_valid = True
        
        if start_node and hasattr(start_node, 'add_connection'):
            start_node.add_connection(self)
        if end_node and hasattr(end_node, 'add_connection'):
            end_node.add_connection(self)

    def __del__(self):
        self._is_valid = False

    def boundingRect(self):
        if (not self._is_valid or not self.start_node or not self.end_node):
            return QRectF(0, 0, 0, 0)
        try:
            start_pos = self.start_node.scenePos()
            end_pos = self.end_node.scenePos()
            padding = 80  # Увеличен padding
            x1 = min(start_pos.x(), end_pos.x()) - padding
            y1 = min(start_pos.y(), end_pos.y()) - padding
            x2 = max(start_pos.x(), end_pos.x()) + padding
            y2 = max(start_pos.y(), end_pos.y()) + padding
            return QRectF(x1, y1, x2 - x1, y2 - y1)
        except RuntimeError:
            return QRectF(0, 0, 0, 0)

    def paint(self, painter, option, widget):
        if (not self._is_valid or not self.start_node or not self.end_node):
            return
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(QColor("#502C2C"), 6, Qt.PenStyle.SolidLine))  # Увеличена толщина
            start_pos = self.start_node.scenePos()
            end_pos = self.end_node.scenePos()
            dx = end_pos.x() - start_pos.x()
            dy = end_pos.y() - start_pos.y()
            distance = (dx**2 + dy**2)**0.5
            if distance > 0:
                dx_unit = dx / distance
                dy_unit = dy / distance
                start_x = start_pos.x() + dx_unit * self.start_node.radius
                start_y = start_pos.y() + dy_unit * self.start_node.radius
                end_x = end_pos.x() - dx_unit * self.end_node.radius
                end_y = end_pos.y() - dy_unit * self.end_node.radius
                painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))
        except RuntimeError:
            pass