"""
Элементы визуализации для QGraphicsScene с анимациями.
"""
from PyQt6.QtWidgets import QGraphicsObject, QGraphicsView, QGraphicsTextItem, QGraphicsEllipseItem
from PyQt6.QtGui import QBrush, QColor, QFont, QRadialGradient, QPen, QPainter, QWheelEvent, QPainterPath, QLinearGradient
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

    def __init__(self, x, y, value, index, radius=30):
        """
        x, y - начальные координаты (y рассматриваем как базовую линию).
        index - индекс в массиве (можно обновлять позже).
        """
        super().__init__()
        self.index = index
        self.value = value
        self.radius = radius
        
        # Состояния для новой системы цветов
        self.is_sorted = False
        self.is_spawning = True

        # Цветовая система - используется в MainWindow
        self.default_color = QColor("#5A9BD5")
        self.sorted_color = QColor("#7EE081")
        self.current_color = self.default_color

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
        gradient.setColorAt(0.0, self.current_color.lighter(170))
        gradient.setColorAt(0.4, self.current_color)
        gradient.setColorAt(1.0, self.current_color.darker(140))

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self.current_color.darker(220), max(2, int(self.radius * 0.06))))
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
        return self.current_color

    @circleColor.setter
    def circleColor(self, value):
        if self._is_valid:
            self.current_color = value
            self.update()

    def highlight(self, color):
        """Подсвечивает элемент указанным цветом."""
        if not self._is_valid or not self.scene():
            return
        
        # Определяем цвет
        if isinstance(color, str):
            target_color = QColor(color)
        elif isinstance(color, QColor):
            target_color = color
        else:
            target_color = self.default_color
        
        # Если зеленый - помечаем как отсортированный
        if target_color.name() == "#7ee081" or color == "sorted":
            self.is_sorted = True
            target_color = self.sorted_color
        
        # Анимируем изменение цвета
        self.color_animation.stop()
        self.color_animation.setStartValue(self.current_color)
        self.color_animation.setEndValue(target_color)
        self.color_animation.start()

    def reset_color(self):
        """Сбрасывает цвет к стандартному или отсортированному."""
        if not self._is_valid or not self.scene():
            return
        
        target_color = self.sorted_color if self.is_sorted else self.default_color
        
        self.color_animation.stop()
        self.color_animation.setStartValue(self.current_color)
        self.color_animation.setEndValue(target_color)
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

    def bounce_animation(self, scale_factor=1.0):
        """Запускает анимацию подпрыгивания с возможностью масштабирования."""
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
        """Обновляет значение элемента."""
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

        # Безопасное добавление соединения
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
            
            # 🛠 FIX: Безопасное получение радиуса с fallback-значением
            # Если это BTree узел, у него нет атрибута radius, поэтому используем getattr
            start_radius = getattr(self.start_node, 'radius', 40)
            padding = max(40, int(start_radius * 0.6))

            x1 = min(start_pos.x(), end_pos.x()) - padding
            y1 = min(start_pos.y(), end_pos.y()) - padding
            x2 = max(start_pos.x(), end_pos.x()) + padding
            y2 = max(start_pos.y(), end_pos.y()) + padding

            return QRectF(x1, y1, x2 - x1, y2 - y1)
        except Exception: 
            # Ловим любые ошибки, включая AttributeError, чтобы не крашить paint engine
            return QRectF(0, 0, 0, 0)

    def paint(self, painter, option, widget):
        if not self._is_valid or not self.start_node or not self.end_node:
            return

        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 🛠 FIX: Безопасное получение радиуса
            start_radius = getattr(self.start_node, 'radius', 40)
            end_radius = getattr(self.end_node, 'radius', 40)
            
            pen = QPen(QColor("#2A2A2A"))
            pen.setWidth(max(3, int(start_radius * 0.08) + 4))
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

                start_x = start_pos.x() + dx_unit * start_radius
                start_y = start_pos.y() + dy_unit * start_radius

                end_x = end_pos.x() - dx_unit * end_radius
                end_y = end_pos.y() - dy_unit * end_radius

                painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))

        except Exception:
            # Игнорируем ошибки отрисовки, чтобы предотвратить вылет
            pass

    def prepareForRemoval(self):
        """Подготовка к удалению из сцены."""
        self._is_valid = False
        
        # Останавливаем все анимации
        if hasattr(self, '_animations'):
            for anim in self._animations:
                try:
                    if hasattr(anim, 'stop'):
                        anim.stop()
                except:
                    pass
            self._animations.clear()
        
        # Очищаем ссылки
        self.start_node = None
        self.end_node = None


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
    """Визуальный элемент для ребра графа с отрисовкой стрелок для ориентированных графов."""

    def __init__(self, start_node, end_node, weight=None, is_directed=False):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.weight = weight
        self.is_directed = is_directed
        self.setZValue(0)
        self._color = QColor("#2c3e50")
        self._pen_width = 3
        
        # Уникальный идентификатор ребра
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
            
            # ОТРИСОВКА СТРЕЛОК ДЛЯ ОРИЕНТИРОВАННЫХ ГРАФОВ
            if self.is_directed:
                # Размер стрелки (зависит от толщины линии)
                arrow_size = 14
                
                # Позиция стрелки - ближе к целевому узлу (80% от расстояния)
                arrow_ratio = 0.8
                arrow_point = QPointF(
                    p1.x() + dx_unit * (distance * arrow_ratio - end_radius),
                    p1.y() + dy_unit * (distance * arrow_ratio - end_radius)
                )
                
                # Угол линии
                angle = math.atan2(dy, dx)
                
                # Точки для стрелки (большой треугольник)
                arrow_p1 = QPointF(
                    arrow_point.x() - arrow_size * math.cos(angle - math.pi/6),
                    arrow_point.y() - arrow_size * math.sin(angle - math.pi/6)
                )
                arrow_p2 = QPointF(
                    arrow_point.x() - arrow_size * math.cos(angle + math.pi/6),
                    arrow_point.y() - arrow_size * math.sin(angle + math.pi/6)
                )
                
                # Рисуем стрелку (закрашенный треугольник)
                painter.save()
                
                # Темный контур для лучшей видимости
                painter.setPen(QPen(QColor("#000000"), 1))
                painter.setBrush(QBrush(self._color))
                
                # Рисуем треугольник
                arrow_path = QPainterPath()
                arrow_path.moveTo(arrow_point)
                arrow_path.lineTo(arrow_p1)
                arrow_path.lineTo(arrow_p2)
                arrow_path.closeSubpath()
                
                painter.drawPath(arrow_path)
                painter.restore()
                
                # Добавляем маленькую белую точку в центре стрелки для лучшей видимости
                painter.save()
                painter.setBrush(QBrush(QColor("#FFFFFF")))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(arrow_point, 2, 2)
                painter.restore()
            
            # Обновляем позицию текста веса
            if self.weight_text and self.weight is not None:
                self._update_weight_text_position()
                
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


class BTreeNodeItem(QGraphicsObject):
    """Прямоугольный узел для B-дерева с несколькими ключами."""
    
    def __init__(self, x, y, keys, is_leaf=False, key_count=0):
        super().__init__()
        
        self._is_valid = True
        
        # Устанавливаем флаги
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable, False)
        
        self.keys = keys if keys is not None else []
        self.is_leaf = is_leaf
        self.key_count = key_count if key_count > 0 else len(self.keys)
        
        # Размеры узла
        self.key_width = 40
        self.key_height = 40
        self.key_spacing = 8
        self.padding = 15
        
        # Цвета
        self.bg_color = QColor("#20B2AA")
        self.key_bg_color = QColor("#FFFFFF")
        self.key_text_color = QColor("#333333")
        self.border_color = QColor("#1A7F7A")
        self.leaf_color = QColor("#98FB98") if is_leaf else QColor("#FFD700")
        
        # Вычисляем размеры узла СРАЗУ
        self._update_node_size()
        
        self.setPos(x, y)
        self.setZValue(1)
        
        # Дочерние узлы и соединения
        self.children = []
        self.parent = None
        self.connections = []

    # 🛠 FIX: Добавляем свойство radius для совместимости с TreeConnectionItem
    @property
    def radius(self):
        """Возвращает эмуляцию радиуса (половина диагонали) для корректной стыковки линий."""
        if hasattr(self, 'node_width') and hasattr(self, 'node_height'):
            return math.sqrt(self.node_width**2 + self.node_height**2) / 2
        return 40

    def set_tree_type_color(self, tree_type):
        """Устанавливает цветовую схему в зависимости от типа дерева."""
        if not getattr(self, '_is_valid', False):
            return
        
        if tree_type == "BTree":
            # Цвета для B-дерева
            self.bg_color = QColor("#20B2AA")
            self.border_color = QColor("#1A7F7A")
            self.update()
        else:
            # Цвета по умолчанию для других типов деревьев
            self.bg_color = QColor("#20B2AA")
            self.border_color = QColor("#1A7F7A")
            self.update()
    
    def _update_node_size(self):
        """Обновляет размеры узла на основе количества ключей."""
        # Всегда устанавливаем значения по умолчанию
        if not hasattr(self, 'key_count'):
            self.key_count = 0
        
        if self.key_count == 0:
            self.node_width = 160
        else:
            self.node_width = max(160, 
                                self.key_count * (self.key_width + self.key_spacing) - 
                                self.key_spacing + 2 * self.padding)
        
        self.node_height = self.key_height + 2 * self.padding + 20  # +20 для индикатора листа
        
        # Гарантируем минимальные размеры
        self.node_width = max(self.node_width, 160)
        self.node_height = max(self.node_height, 80)
    
    def boundingRect(self):
        if not self._is_valid:
            return QRectF(0, 0, 0, 0)
        
        try:
            # Убедимся, что размеры вычислены
            if not hasattr(self, 'node_width') or not hasattr(self, 'node_height'):
                self._update_node_size()
            
            width = self.node_width
            height = self.node_height
            
            # Дополнительный запас для тени, обводки
            extra_padding = 10
            
            # Центрируем прямоугольник относительно (0, 0)
            return QRectF(
                -width / 2 - extra_padding, 
                -height / 2 - extra_padding, 
                width + 2 * extra_padding, 
                height + 2 * extra_padding
            )
        except Exception as e:
            print(f"Error in BTreeNodeItem.boundingRect(): {e}")
            # Возвращаем безопасный прямоугольник
            return QRectF(-100, -100, 200, 200)
    
    def paint(self, painter, option, widget):
        if not self._is_valid:
            return
        
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Убедимся, что размеры вычислены
            if not hasattr(self, 'node_width') or not hasattr(self, 'node_height'):
                self._update_node_size()
            
            # Основной прямоугольник узла
            rect = QRectF(-self.node_width/2, -self.node_height/2, 
                         self.node_width, self.node_height)
            
            # Градиентная заливка
            gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            gradient.setColorAt(0.0, self.bg_color.lighter(120))
            gradient.setColorAt(0.5, self.bg_color)
            gradient.setColorAt(1.0, self.bg_color.darker(120))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(self.border_color, 2))
            painter.drawRoundedRect(rect, 10, 10)
            
            # Индикатор типа узла в верхней части
            type_rect = QRectF(-30, -self.node_height/2 + 5, 60, 20)
            type_gradient = QLinearGradient(type_rect.topLeft(), type_rect.bottomRight())
            
            if self.is_leaf:
                type_gradient.setColorAt(0.0, QColor("#98FB98").lighter(120))
                type_gradient.setColorAt(1.0, QColor("#32CD32"))
                type_text = "ЛИСТ"
            else:
                type_gradient.setColorAt(0.0, QColor("#FFD700").lighter(120))
                type_gradient.setColorAt(1.0, QColor("#FFA500"))
                type_text = "УЗЕЛ"
            
            painter.setBrush(QBrush(type_gradient))
            painter.setPen(QPen(self.border_color.darker(150), 1))
            painter.drawRoundedRect(type_rect, 5, 5)
            
            # Текст типа
            painter.setPen(QColor("#333333"))
            font = QFont()
            font.setPointSize(9)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(type_rect, Qt.AlignmentFlag.AlignCenter, type_text)
            
            # Рисуем ключи
            if self.keys and len(self.keys) > 0:
                total_keys_width = len(self.keys) * self.key_width + (len(self.keys) - 1) * self.key_spacing
                start_x = -total_keys_width / 2
                
                for i, key in enumerate(self.keys):
                    key_x = start_x + i * (self.key_width + self.key_spacing)
                    key_rect = QRectF(key_x, -self.key_height/2 + 15, 
                                     self.key_width, self.key_height)
                    
                    # Градиент для ключа
                    key_gradient = QLinearGradient(key_rect.topLeft(), key_rect.bottomRight())
                    key_gradient.setColorAt(0.0, QColor("#FFFFFF"))
                    key_gradient.setColorAt(0.5, self.key_bg_color)
                    key_gradient.setColorAt(1.0, QColor("#F0F0F0"))
                    
                    painter.setBrush(QBrush(key_gradient))
                    painter.setPen(QPen(self.border_color, 1))
                    painter.drawRoundedRect(key_rect, 6, 6)
                    
                    # Текст ключа
                    painter.setPen(self.key_text_color)
                    font.setPointSize(12)
                    font.setBold(True)
                    painter.setFont(font)
                    painter.drawText(key_rect, Qt.AlignmentFlag.AlignCenter, str(key))
                    
                    # Индекс ключа (маленький текст сверху)
                    index_rect = QRectF(key_rect.x(), key_rect.y() - 12, key_rect.width(), 12)
                    font.setPointSize(8)
                    painter.setFont(font)
                    painter.setPen(QColor("#666666"))
                    painter.drawText(index_rect, Qt.AlignmentFlag.AlignCenter, f"K[{i}]")
            
            # Количество ключей в нижней части
            count_text = f"Ключей: {self.key_count}"
            count_rect = QRectF(
                -self.node_width/2 + 10,
                self.node_height/2 - 20,
                self.node_width - 20,
                15
            )
            painter.setPen(QColor("#444444"))
            font.setPointSize(8)
            font.setBold(False)
            painter.setFont(font)
            painter.drawText(count_rect, Qt.AlignmentFlag.AlignLeft, count_text)
            
        except Exception as e:
            print(f"Error painting BTreeNodeItem: {e}")
    
    def prepareForRemoval(self):
        """Подготовка к удалению из сцены."""
        self._is_valid = False
        
        # Останавливаем все анимации
        try:
            if hasattr(self, '_entry_anims'):
                for anim in self._entry_anims:
                    try:
                        if anim and hasattr(anim, 'stop'):
                            anim.stop()
                    except:
                        pass
                self._entry_anims = []
        except:
            pass
        
        # Очищаем связи
        try:
            if hasattr(self, 'connections'):
                for conn in self.connections:
                    try:
                        if conn and hasattr(conn, '_is_valid'):
                            conn._is_valid = False
                    except:
                        pass
                self.connections.clear()
        except:
            pass
        
        try:
            self.children.clear()
        except:
            pass
        
        self.parent = None
    
    def add_child(self, child_node):
        """Добавляет дочерний узел."""
        if not self._is_valid or not child_node or not getattr(child_node, '_is_valid', False):
            return
        
        if not hasattr(self, 'children'):
            self.children = []
        
        if child_node not in self.children:
            self.children.append(child_node)
            child_node.parent = self
    
    # 🛠 FIX: Добавляем метод add_connection, который вызывает TreeConnectionItem
    def add_connection(self, connection):
        """Добавляет соединение (для совместимости с TreeConnectionItem)."""
        if connection and self._is_valid:
            if not hasattr(self, 'connections'):
                self.connections = []
            self.connections.append(connection)

    def update_keys(self, new_keys, animate=True):
        """Обновляет ключи узла с анимацией."""
        if not self._is_valid:
            return
        
        # Сохраняем старые ключи для анимации
        old_keys = self.keys.copy()
        self.keys = new_keys if new_keys is not None else []
        self.key_count = len(self.keys)
        
        # Пересчитываем размер
        self._update_node_size()
        
        if animate:
            # Анимация обновления
            self._animate_keys_update(old_keys, new_keys)
        else:
            self.update()
        
    def _animate_keys_update(self, old_keys, new_keys):
        """Анимирует обновление ключей."""
        # Простая анимация - изменение прозрачности
        if hasattr(self, 'setOpacity'):
            self.setOpacity(0.7)
            
            # Восстанавливаем через задержку
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._finish_keys_animation())
            timer.start(300)
        
        self.update()

    def _finish_keys_animation(self):
        """Завершает анимацию обновления ключей."""
        if hasattr(self, 'setOpacity'):
            self.setOpacity(1.0)
        self.update()