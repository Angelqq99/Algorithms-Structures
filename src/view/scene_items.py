
"""
Элементы визуализации для QGraphicsScene с анимациями.
"""
from PyQt6.QtWidgets import QGraphicsObject, QGraphicsView, QGraphicsTextItem, QGraphicsEllipseItem
from PyQt6.QtGui import QBrush, QColor, QFont, QRadialGradient, QPen, QPainter, QWheelEvent, QPainterPath
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, QPropertyAnimation, pyqtProperty, QEasingCurve, pyqtSignal, QObject
import math


# ==========================
# 🔍 QGraphicsView с масштабированием колесиком
# ==========================
class ZoomableGraphicsView(QGraphicsView):
    """QGraphicsView с поддержкой масштабирования колесиком мыши и расширенной прокруткой."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # Включаем scrollbar и разрешаем большую область прокрутки
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Увеличиваем диапазон scrollbar
        self.horizontalScrollBar().setRange(-10000, 10000)
        self.verticalScrollBar().setRange(-10000, 10000)

        self.scale_factor = 1.15
        self.min_zoom = 0.08
        self.max_zoom = 5.0
        self._current_scale = 1.0
        
        # Сохраняем исходный масштаб для сброса
        self.default_scale = 1.0
        
        # Расширенная область сцены для большой прокрутки
        self._extended_scene_rect = QRectF(-5000, -5000, 10000, 10000)

    def wheelEvent(self, event: QWheelEvent):
        # Зум всегда доступен без Ctrl
        zoom_in = event.angleDelta().y() > 0
        factor = self.scale_factor if zoom_in else 1 / self.scale_factor
        new_scale = self._current_scale * factor

        if self.min_zoom <= new_scale <= self.max_zoom:
            self.scale(factor, factor)
            self._current_scale = new_scale
            
            # Обновляем область сцены при зуме для поддержки прокрутки
            self._update_scene_rect()

    def set_scene_rect_based_on_content(self, content_rect, padding=200):
        """Устанавливает область сцены на основе содержимого с расширением для прокрутки."""
        if content_rect.isValid():
            # Центрируем основное содержимое
            center = content_rect.center()
            
            # Создаем расширенную область вокруг содержимого
            extended_width = max(content_rect.width() * 3, 2000)
            extended_height = max(content_rect.height() * 3, 2000)
            
            self._extended_scene_rect = QRectF(
                center.x() - extended_width / 2,
                center.y() - extended_height / 2,
                extended_width,
                extended_height
            )
            
            # Устанавливаем область сцены
            if self.scene():
                self.scene().setSceneRect(self._extended_scene_rect)
            
            # Центрируем вид на основном содержимом
            self.centerOn(center)

    def _update_scene_rect(self):
        """Обновляет область сцены при изменении масштаба."""
        if self.scene() and hasattr(self, '_extended_scene_rect'):
            # При сильном зуме увеличиваем область для прокрутки
            current_rect = self._extended_scene_rect
            scale_factor = max(1.0, self._current_scale)
            
            extended_rect = QRectF(
                current_rect.x() * scale_factor,
                current_rect.y() * scale_factor,
                current_rect.width() * scale_factor,
                current_rect.height() * scale_factor
            )
            
            self.scene().setSceneRect(extended_rect)

    def reset_zoom(self):
        """Сброс масштаба к исходному."""
        self.resetTransform()
        self._current_scale = self.default_scale
        
    def fit_to_content(self, padding=200):
        """Масштабирует вид чтобы вместить все содержимое с отступами."""
        if self.scene():
            rect = self.scene().itemsBoundingRect()
            if rect.isValid():
                # Добавляем отступы
                rect.adjust(-padding, -padding, padding, padding)
                
                # Устанавливаем расширенную область для прокрутки
                self.set_scene_rect_based_on_content(rect, padding)
                
                # Масштабируем к основному содержимому
                self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
                
                # Обновляем текущий масштаб после fitInView
                self._update_current_scale()
                
    def _update_current_scale(self):
        """Обновляет значение текущего масштаба."""
        try:
            # Получаем текущую трансформацию и вычисляем масштаб
            transform = self.transform()
            self._current_scale = transform.m11()  # m11 и m22 обычно одинаковы для uniform scaling
        except:
            self._current_scale = 1.0

    def ensure_visible_extended(self, rect, xmargin=50, ymargin=50):
        """Обеспечивает видимость области с расширенными границами."""
        try:
            # Преобразуем координаты сцены в координаты вида
            view_rect = self.mapFromScene(rect).boundingRect()
            visible_rect = self.viewport().rect()
            
            # Если область не видна, прокручиваем к ней
            if not visible_rect.contains(view_rect):
                self.centerOn(rect.center())
        except Exception as e:
            print(f"Error ensuring visibility: {e}")


# ==========================
# 🔵 Круг для элементов массива
# ==========================
class ArrayCircleItem(QGraphicsObject):
    """Круг для визуализации элемента массива с анимациями."""

    def __init__(self, x, y, value, index, radius=40):
        """
        x, y - начальные координаты (y рассматриваем как базовую линию).
        index - индекс в массиве (можно обновлять позже).
        """
        super().__init__()
        self.index = index
        self.value = value
        self.radius = radius
        self.is_spawning = True

        self.default_color = QColor("#5A9BD5")
        self.highlight_color = QColor("#FFD700")
        self.swap_color = QColor("#FF6B6B")
        self.complete_color = QColor("#7EE081")

        self._current_color = self.default_color

        # Базовая позиция по Y — та линия, на которой элемент должен стоять
        self.base_y = y
        self.setPos(x, y)
        self.setZValue(1)

        # Анимации
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(600)
        self.pos_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.color_animation = QPropertyAnimation(self, b"circleColor")
        self.color_animation.setDuration(350)
        self.color_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Bounce
        self.bounce_timer = QTimer()
        self.bounce_timer.timeout.connect(self._bounce_step)
        self.bounce_steps = 0
        # original_y используется во время bounce; всегда берём из base_y
        self.original_y = self.base_y

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
        gradient.setColorAt(0.0, self._current_color.lighter(170))
        gradient.setColorAt(0.4, self._current_color)
        gradient.setColorAt(1.0, self._current_color.darker(140))

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self._current_color.darker(220), max(2, int(self.radius * 0.06))))
        painter.drawEllipse(0, 0, self.radius * 2, self.radius * 2)

        font = QFont()
        font.setPointSizeF(self.radius * 0.6)
        font.setBold(True)
        painter.setFont(font)

        text_rect = QRectF(0, 0, self.radius * 2, self.radius * 2)

        # Тень текста
        painter.setPen(QPen(QColor(20, 20, 20, 200)))
        painter.drawText(text_rect.translated(2, 2), Qt.AlignmentFlag.AlignCenter, str(self.value))
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(self.value))

    # === FIX: вспомогательные методы для выравнивания и контроля bounce ===
    def force_set_y(self, y):
        """Принудительно выставить y (без изменения base_y)."""
        if self._is_valid:
            try:
                self.setY(y)
            except RuntimeError:
                pass

    def force_align_to_base(self):
        """Принудительно поставить элемент ровно на base_y."""
        if self._is_valid:
            try:
                self.setY(self.base_y)
            except RuntimeError:
                pass

    def stop_bounce(self):
        """Остановить bounce и вернуть на базовую линию."""
        if self.bounce_timer.isActive():
            self.bounce_timer.stop()
        self.bounce_steps = 0
        self.original_y = self.base_y
        self.force_align_to_base()

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
        target_color = QColor(color) if isinstance(color, (str, QColor)) else self.default_color
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

    def animate_move(self, new_x, new_y, duration=600):
        """
        Плавное перемещение на (new_x, new_y).
        Важно: обновляем base_y на новое значение, чтобы дальнейшие bounce опирались на него.
        """
        if not self._is_valid or not self.scene():
            return

        # Останавливаем bounce, чтобы не было конфликтов
        if self.bounce_timer.isActive():
            self.bounce_timer.stop()
            self.bounce_steps = 0

        # Обновляем базовую линию — считаем, что после перемещения это будет "правильная" линия
        self.base_y = new_y
        self.original_y = self.base_y

        self.pos_animation.stop()
        self.pos_animation.setDuration(max(300, int(duration)))
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(QPointF(new_x, new_y))
        self.pos_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.pos_animation.start()

    def bounce_animation(self):
        if not self._is_valid or not self.scene() or getattr(self, "is_spawning", False):
            return

        self.bounce_steps = 0
        # original_y должен быть фиксированным базовым уровнем, не текущей Y!
        self.original_y = getattr(self, "base_y", self.y())

        self.bounce_timer.start(45)

    def _bounce_step(self):
        if not self._is_valid or not self.scene():
            self.bounce_timer.stop()
            return

        if self.bounce_steps >= 10:
            self.bounce_timer.stop()
            try:
                # Гарантированно вернёмся на original_y (равный base_y)
                self.setY(self.original_y)
            except RuntimeError:
                pass
            return

        import math
        bounce_height = max(8, self.radius * 0.18)
        progress = self.bounce_steps / 10.0
        bounce_offset = math.sin(progress * math.pi) * bounce_height

        try:
            # Прыгаем выше базовой линии (original_y - offset)
            self.setY(self.original_y - bounce_offset)
        except RuntimeError:
            self.bounce_timer.stop()
            return

        self.bounce_steps += 1

    def update_value(self, value):
        if self._is_valid:
            self.value = value
            self.update()


# ==========================
# 🌳 Узел дерева
# ==========================
class TreeNodeItem(ArrayCircleItem):
    """Крупный узел дерева."""

    def __init__(self, x, y, value, radius=95):
        super().__init__(x, y, value, -1, radius)
        self.children = []
        self.parent = None
        self.level = 0
        self.tree_connections = []
        self.subtree_width = 1

        self.default_color = QColor("#6C2EB5")
        self.avl_color = QColor("#2E8B57")
        self.rb_red_color = QColor("#DC143C")
        self.rb_black_color = QColor("#2F4F4F")
        self.splay_color = QColor("#FF8C00")
        self.treap_color = QColor("#9370DB")
        self.b_tree_color = QColor("#20B2AA")

        self._current_color = self.default_color
        self.setZValue(1)

    def paint(self, painter, option, widget):
        if not self._is_valid:
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QRadialGradient(self.radius, self.radius, self.radius)
        gradient.setColorAt(0.0, self._current_color.lighter(170))
        gradient.setColorAt(0.4, self._current_color)
        gradient.setColorAt(1.0, self._current_color.darker(180))

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self._current_color.darker(220), max(3, int(self.radius * 0.05))))
        painter.drawEllipse(0, 0, self.radius * 2, self.radius * 2)

        font = QFont()
        font.setPointSizeF(self.radius * 0.45)
        font.setBold(True)
        painter.setFont(font)

        text_rect = QRectF(0, 0, self.radius * 2, self.radius * 2)

        painter.setPen(QPen(QColor(0, 0, 0, 200)))
        painter.drawText(text_rect.translated(2, 2), Qt.AlignmentFlag.AlignCenter, str(self.value))
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(self.value))

    def set_tree_type_color(self, tree_type):
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
# 🔗 Линия между узлами дерева
# ==========================
class TreeConnectionItem(QGraphicsObject):
    """Соединение между узлами дерева."""

    def __init__(self, start_node, end_node):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setZValue(-1)
        self._is_valid = True
        self._animations = []

        if start_node and hasattr(start_node, 'add_connection'):
            start_node.add_connection(self)
        if end_node and hasattr(end_node, 'add_connection'):
            end_node.add_connection(self)

    def __del__(self):
        self._is_valid = False

    def boundingRect(self):
        if not self._is_valid or not self.start_node or not self.end_node:
            return QRectF(0, 0, 0, 0)

        try:
            start_pos = self.start_node.scenePos()
            end_pos = self.end_node.scenePos()
            padding = max(40, int(self.start_node.radius * 0.6))

            x1 = min(start_pos.x(), end_pos.x()) - padding
            y1 = min(start_pos.y(), end_pos.y()) - padding
            x2 = max(start_pos.x(), end_pos.x()) + padding
            y2 = max(start_pos.y(), end_pos.y()) + padding

            return QRectF(x1, y1, x2 - x1, y2 - y1)
        except RuntimeError:
            return QRectF(0, 0, 0, 0)

    def paint(self, painter, option, widget):
        if not self._is_valid or not self.start_node or not self.end_node:
            return

        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(QColor("#2A2A2A"))
            pen.setWidth(max(3, int(self.start_node.radius * 0.08) + 4))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)

            start_pos = self.start_node.scenePos()
            end_pos = self.end_node.scenePos()

            dx = end_pos.x() - start_pos.x()
            dy = end_pos.y() - start_pos.y()
            distance = (dx**2 + dy**2) ** 0.5

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

class GraphNodeItem(QGraphicsEllipseItem):
    """Визуальный элемент для узла графа."""
    
    def __init__(self, value, is_start=False):
        self.radius = 30
        super().__init__(-self.radius, -self.radius, self.radius * 2, self.radius * 2)
        
        self.value = value
        self._current_color = QColor("#4A90E2")
        self._target_color = self._current_color
        self._pen_color = QColor("#333333")
        self.setZValue(10)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)

        # Текст
        self.text_item = QGraphicsTextItem(str(value), self)
        font = QFont("Arial", 12)
        font.setBold(True)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor("#FFFFFF"))
        
        # Центрируем текст
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(-text_rect.width() / 2, -text_rect.height() / 2)
        
        # Для Дейкстры
        self.distance_text = None 
        if is_start:
            self._current_color = QColor("#F9C80E")
            self._target_color = self._current_color
            self.update()

        # Анимация цвета
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self._update_color_animation)
        self.animation_start_color = None
        self.animation_duration = 300
        self.animation_progress = 0
        
        # Список связанных ребер для обновления
        self.connected_edges = []
        
    def add_connected_edge(self, edge):
        """Добавляет ребро для обновления при перемещении узла."""
        if edge not in self.connected_edges:
            self.connected_edges.append(edge)
            
    def remove_connected_edge(self, edge):
        """Удаляет ребро из списка."""
        if edge in self.connected_edges:
            self.connected_edges.remove(edge)
    
    def setPos(self, pos):
        """Переопределяем для обновления связанных ребер."""
        super().setPos(pos)
        # Обновляем все связанные ребра
        for edge in self.connected_edges:
            if hasattr(edge, 'update_position'):
                edge.update_position()

    def highlight(self, color_hex):
        """Подсветка узла с плавной анимацией."""
        try:
            target_color = QColor(color_hex)
            if self._target_color == target_color:
                return
                
            # Останавливаем текущую анимацию
            if self.color_timer.isActive():
                self.color_timer.stop()
                
            # Запускаем новую анимацию
            self.animation_start_color = self._current_color
            self._target_color = target_color
            self.animation_progress = 0
            
            self.color_timer.start(16)  # ~60 FPS
        except Exception as e:
            print(f"Error in highlight: {e}")

    def _update_color_animation(self):
        """Обновление анимации цвета."""
        try:
            self.animation_progress += 16
            
            if self.animation_progress >= self.animation_duration:
                self.color_timer.stop()
                self._current_color = self._target_color
            else:
                # Интерполяция цвета
                progress = self.animation_progress / self.animation_duration
                r = int(self.animation_start_color.red() + 
                       (self._target_color.red() - self.animation_start_color.red()) * progress)
                g = int(self.animation_start_color.green() + 
                       (self._target_color.green() - self.animation_start_color.green()) * progress)
                b = int(self.animation_start_color.blue() + 
                       (self._target_color.blue() - self.animation_start_color.blue()) * progress)
                
                self._current_color = QColor(r, g, b)
            
            self.update()
        except Exception as e:
            print(f"Error in color animation: {e}")
            self.color_timer.stop()

    def paint(self, painter, option, widget):
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Тело узла
            gradient = QRadialGradient(0, 0, self.radius)
            gradient.setColorAt(0.0, self._current_color.lighter(150))
            gradient.setColorAt(0.7, self._current_color)
            gradient.setColorAt(1.0, self._current_color.darker(120))

            pen = QPen(self._pen_color)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(-self.radius, -self.radius, self.radius * 2, self.radius * 2)
        except Exception as e:
            print(f"Error painting node: {e}")

    def update_distance_text(self, text):
        """Обновляет текст расстояния для Дейкстры."""
        try:
            if not self.distance_text:
                self.distance_text = QGraphicsTextItem(self)
                self.distance_text.setDefaultTextColor(QColor("#444444"))
                self.distance_text.setFont(QFont("Arial", 10))
            
            self.distance_text.setPlainText(f"D: {text}")
            text_rect = self.distance_text.boundingRect()
            self.distance_text.setPos(-text_rect.width() / 2, self.radius + 5)
        except Exception as e:
            print(f"Error updating distance text: {e}")


class GraphEdgeItem(QGraphicsObject):
    """Визуальный элемент для ребра графа."""

    def __init__(self, start_node, end_node, weight=None, is_directed=False):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.weight = weight
        self.is_directed = is_directed
        self.setZValue(0)
        self._color = QColor("#2c3e50")
        self._pen_width = 3
        
        # Уникальный идентификатор ребра для неориентированных графов
        if not is_directed:
            # Создаем нормализованный ключ для неориентированного ребра
            node_values = sorted([start_node.value, end_node.value])
            self.edge_key = f"{node_values[0]}-{node_values[1]}"
        else:
            self.edge_key = f"{start_node.value}-{end_node.value}"
        
        # Регистрируем ребро в узлах
        if hasattr(start_node, 'add_connected_edge'):
            start_node.add_connected_edge(self)
        if hasattr(end_node, 'add_connected_edge'):
            end_node.add_connected_edge(self)
        
        # Текст веса
        self.weight_text = None
        if weight is not None:
            self.weight_text = QGraphicsTextItem(str(weight), self)
            self.weight_text.setDefaultTextColor(QColor("#c0392b"))
            self.weight_text.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        self.setVisible(True)
    
    def update_position(self):
        """Обновляем позицию при перемещении узлов."""
        try:
            self.prepareGeometryChange()
            self.update()
            
            # Также обновляем позицию текста
            if self.weight_text:
                self._update_weight_text_position()
        except Exception as e:
            print(f"Error updating edge position: {e}")
    
    def _update_weight_text_position(self):
        """Обновляет позицию текста веса."""
        try:
            if not self.start_node or not self.end_node:
                return
                
            start_pos = self.start_node.scenePos()
            end_pos = self.end_node.scenePos()
            
            # Вектор от start к end
            dx = end_pos.x() - start_pos.x()
            dy = end_pos.y() - start_pos.y()
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance == 0:
                return
                
            # Нормализованный вектор
            dx_unit = dx / distance
            dy_unit = dy / distance
            
            # Точки начала и конца линии (с учетом радиусов узлов)
            start_radius = getattr(self.start_node, 'radius', 30)
            end_radius = getattr(self.end_node, 'radius', 30)
            
            p1 = QPointF(
                start_pos.x() + dx_unit * start_radius,
                start_pos.y() + dy_unit * start_radius
            )
            p2 = QPointF(
                end_pos.x() - dx_unit * end_radius,
                end_pos.y() - dy_unit * end_radius
            )
            
            # Позиция текста - середина линии со смещением
            mid_point = QPointF(
                (p1.x() + p2.x()) / 2,
                (p1.y() + p2.y()) / 2
            )
            
            # Перпендикулярное смещение для размещения текста
            offset_x = -dy_unit * 20
            offset_y = dx_unit * 20
            
            text_rect = self.weight_text.boundingRect()
            self.weight_text.setPos(
                mid_point.x() + offset_x - text_rect.width() / 2,
                mid_point.y() + offset_y - text_rect.height() / 2
            )
        except Exception as e:
            print(f"Error updating weight text position: {e}")
            
    def boundingRect(self):
        try:
            if not self.start_node or not self.end_node:
                return QRectF(0, 0, 0, 0)

            start_pos = self.start_node.scenePos()
            end_pos = self.end_node.scenePos()
            
            # Вычисляем ограничивающий прямоугольник с запасом для стрелок и текста
            x1 = min(start_pos.x(), end_pos.x()) - 50
            y1 = min(start_pos.y(), end_pos.y()) - 50
            x2 = max(start_pos.x(), end_pos.x()) + 50
            y2 = max(start_pos.y(), end_pos.y()) + 50
            
            return QRectF(x1, y1, x2 - x1, y2 - y1)
        except Exception:
            return QRectF(0, 0, 0, 0)
            
    def paint(self, painter, option, widget):
        try:
            if not self.start_node or not self.end_node:
                return

            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            start_pos = self.start_node.scenePos()
            end_pos = self.end_node.scenePos()

            # Вектор от start к end
            dx = end_pos.x() - start_pos.x()
            dy = end_pos.y() - start_pos.y()
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance == 0:
                return
                
            # Нормализованный вектор
            dx_unit = dx / distance
            dy_unit = dy / distance
            
            # Точки начала и конца линии (с учетом радиусов узлов)
            start_radius = getattr(self.start_node, 'radius', 30)
            end_radius = getattr(self.end_node, 'radius', 30)
            
            p1 = QPointF(
                start_pos.x() + dx_unit * start_radius,
                start_pos.y() + dy_unit * start_radius
            )
            p2 = QPointF(
                end_pos.x() - dx_unit * end_radius,
                end_pos.y() - dy_unit * end_radius
            )

            # Рисуем линию
            pen = QPen(self._color)
            pen.setWidth(self._pen_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(p1, p2)
            
            # Обновляем позицию текста веса
            if self.weight_text and self.weight is not None:
                self._update_weight_text_position()
            
            # ИСПРАВЛЕНИЕ: УБРАН КОД ДЛЯ ОТРИСОВКИ СТРЕЛОК
            # Теперь стрелки не рисуются даже для ориентированных графов
                
        except Exception as e:
            print(f"Error painting edge: {e}")

    def highlight(self, color_hex):
        try:
            self._color = QColor(color_hex)
            self.update()
        except Exception as e:
            print(f"Error highlighting edge: {e}")
        
    def reset_color(self):
        try:
            self._color = QColor("#2c3e50")
            self.update()
        except Exception as e:
            print(f"Error resetting edge color: {e}")

    def __del__(self):
        """При удалении ребра убираем его из узлов."""
        try:
            if hasattr(self, 'start_node') and self.start_node and hasattr(self.start_node, 'remove_connected_edge'):
                self.start_node.remove_connected_edge(self)
            if hasattr(self, 'end_node') and self.end_node and hasattr(self.end_node, 'remove_connected_edge'):
                self.end_node.remove_connected_edge(self)
        except Exception as e:
            print(f"Error in edge destructor: {e}")
