"""
Элементы визуализации для QGraphicsScene с анимациями.
"""
from PyQt6.QtWidgets import QGraphicsObject, QGraphicsTextItem
from PyQt6.QtGui import QBrush, QColor, QFont, QRadialGradient, QPen, QPainter
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, QPropertyAnimation, pyqtProperty


class ArrayCircleItem(QGraphicsObject):
    """Круг для визуализации элемента массива с анимациями."""
    
    def __init__(self, x, y, value, index, radius=25):
        super().__init__()
        self.index = index
        self.value = value
        self.radius = radius
        
        # ИСПРАВЛЕНИЕ 1: Используем QColor вместо строк для цветов
        self.default_color = QColor("#5A9BD5")  # Синий
        self.highlight_color = QColor("#FFD700")  # Желтый
        self.swap_color = QColor("#FF6B6B")  # Красный
        self.complete_color = QColor("#7EE081")  # Зеленый
        
        # Текущий цвет должен быть QColor, а не строкой
        self._current_color = self.default_color
        
        # Устанавливаем начальную позицию
        self.setPos(x, y)
        
        # Анимация позиции
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(500)
        
        # Анимация цвета - ИСПРАВЛЕНИЕ 2: правильное свойство
        self.color_animation = QPropertyAnimation(self, b"circleColor")
        self.color_animation.setDuration(300)
        
        # Таймер для анимации прыжка
        self.bounce_timer = QTimer()
        self.bounce_timer.timeout.connect(self._bounce_step)
        self.bounce_steps = 0
        self.original_y = y

    def boundingRect(self):
        return QRectF(0, 0, self.radius * 2, self.radius * 2)
        
    def paint(self, painter, option, widget):
        # Включаем сглаживание
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # ИСПРАВЛЕНИЕ 3: Правильное создание градиента
        gradient = QRadialGradient(self.radius, self.radius, self.radius)
        gradient.setColorAt(0, self._current_color.lighter(150))
        gradient.setColorAt(0.7, self._current_color)
        gradient.setColorAt(1, self._current_color.darker(150))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self._current_color.darker(200), 2))
        painter.drawEllipse(0, 0, self.radius * 2, self.radius * 2)
        
        # Рисуем текст значения
        painter.setPen(QColor("white"))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, str(self.value))
        
        # # Рисуем индекс под кругом
        # index_font = QFont("Arial", 8)
        # painter.setFont(index_font)
        # painter.setPen(QColor("#2c3e50"))
        # painter.drawText(0, self.radius * 2 + 5, self.radius * 2, 15, 
        #                 Qt.AlignmentFlag.AlignCenter, f"[{self.index}]")

    # ИСПРАВЛЕНИЕ 4: Правильное свойство для анимации цвета
    @pyqtProperty(QColor)
    def circleColor(self):
        return self._current_color
        
    @circleColor.setter
    def circleColor(self, value):
        self._current_color = value
        self.update()  # Важно: вызываем update для перерисовки

    def highlight(self, color):
        """Подсветка элемента с анимацией."""
        # ИСПРАВЛЕНИЕ 5: Преобразуем строку в QColor если необходимо
        if isinstance(color, str):
            target_color = QColor(color)
        else:
            target_color = color
            
        self.color_animation.stop()
        self.color_animation.setStartValue(self._current_color)
        self.color_animation.setEndValue(target_color)
        self.color_animation.start()

    def reset_color(self):
        """Возврат к стандартному цвету с анимацией."""
        self.color_animation.stop()
        self.color_animation.setStartValue(self._current_color)
        self.color_animation.setEndValue(self.default_color)
        self.color_animation.start()

    def animate_move(self, new_x, new_y, duration=500):
        """Анимированное перемещение элемента."""
        self.pos_animation.stop()
        self.pos_animation.setDuration(duration)
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(QPointF(new_x, new_y))
        
        # ИСПРАВЛЕНИЕ 6: Добавляем easing для плавности
        self.pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.pos_animation.start()

    def bounce_animation(self):
        """Анимация 'прыжка' элемента."""
        self.bounce_steps = 0
        self.original_y = self.y()
        self.bounce_timer.start(50)

    def _bounce_step(self):
        """Шаг анимации прыжка."""
        if self.bounce_steps >= 8:
            self.bounce_timer.stop()
            self.setY(self.original_y)
            return
            
        # Простая синусоидальная анимация для плавного прыжка
        import math
        bounce_height = 15
        progress = self.bounce_steps / 8.0
        bounce_offset = math.sin(progress * math.pi) * bounce_height
        
        self.setY(self.original_y - bounce_offset)
        self.bounce_steps += 1

    def update_value(self, value):
        """Обновление значения."""
        self.value = value
        self.update()

    def __str__(self):
        return f"ArrayCircleItem(index={self.index}, value={self.value})"


# ИСПРАВЛЕНИЕ 7: Добавляем недостающий импорт
from PyQt6.QtCore import QEasingCurve