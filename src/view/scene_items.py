"""
Элементы визуализации для QGraphicsScene.
"""
from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem,QGraphicsTextItem, QGraphicsDropShadowEffect
from PyQt6.QtGui import QBrush, QColor, QFont, QRadialGradient
from PyQt6.QtCore import QRectF, Qt, QPointF, QPropertyAnimation, QEasingCurve, QVariantAnimation


class ArrayCircleItem(QGraphicsEllipseItem):
    """Круг для визуализации элемента массива с числом внутри."""
    def __init__(self, x, y, value, index, radius=25):
        super().__init__(0, 0, radius * 2, radius * 2)
        self.index = index
        self.value = value
        self.radius = radius

        # Центрируем и задаем позицию
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("#5A9BD5")))
        self.setPen(QColor("#4B89C6"))

        # Добавляем текст
        self.text = QGraphicsTextItem(str(value), self)
        self.text.setDefaultTextColor(Qt.GlobalColor.white)
        font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        self.text.setFont(font)
        self.text.setPos(radius - self.text.boundingRect().width() / 2,
                         radius - self.text.boundingRect().height() / 2)

    def highlight(self, color="#FFD700"):
        self.setBrush(QBrush(QColor(color)))

    def reset_color(self):
        self.setBrush(QBrush(QColor("#5A9BD5")))

    def update_value(self, value):
        self.value = value
        self.text.setPlainText(str(value))


class ArrayCircleItem3D(QGraphicsEllipseItem):
    """Объёмный кружок с числом внутри (3D-эффект + анимации)."""

    def __init__(self, x, y, value, index, radius=25):
        super().__init__(0, 0, radius * 2, radius * 2)
        self.index = index
        self.value = value
        self.radius = radius
        self.setPos(x, y)

        # --- 3D градиент ---
        gradient = QRadialGradient(radius, radius, radius * 1.2)
        gradient.setColorAt(0, QColor("#8FC1FF"))
        gradient.setColorAt(1, QColor("#3E7BFA"))
        self.default_brush = QBrush(gradient)
        self.setBrush(self.default_brush)
        self.setPen(QColor("#3366CC"))

        # --- Тень ---
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(3, 3)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        # --- Текст ---
        self.text = QGraphicsTextItem(str(value), self)
        font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        self.text.setFont(font)
        self.text.setDefaultTextColor(Qt.GlobalColor.white)
        self._center_text()

    def _center_text(self):
        rect = self.text.boundingRect()
        self.text.setPos(self.radius - rect.width() / 2, self.radius - rect.height() / 2)

    # ---------------------------------------
    # Эффекты
    # ---------------------------------------
    def highlight(self, color="#FFD700"):
        """Подсветка кружка (с плавным переходом)."""
        start_brush = self.brush().color()
        end_color = QColor(color)

        anim = QVariantAnimation()
        anim.setStartValue(start_brush)
        anim.setEndValue(end_color)
        anim.setDuration(300)
        anim.valueChanged.connect(lambda c: self.setBrush(QBrush(c)))
        anim.start()
        self._anim = anim  # предотвратить сборку мусора

    def reset_color(self):
        """Возврат к стандартному виду."""
        self.setBrush(self.default_brush)

    def animate_move(self, new_x, new_y):
        """Плавное перемещение элемента (с защитой от GC)."""
        from PyQt6.QtCore import QPropertyAnimation, QPointF, QEasingCurve
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(400)
        anim.setStartValue(self.pos())
        anim.setEndValue(QPointF(new_x, new_y))
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # предотвращаем уничтожение GC
        if not hasattr(self, "_active_anims"):
            self._active_anims = []
        self._active_anims.append(anim)
        anim.finished.connect(lambda: self._active_anims.remove(anim))

        anim.start()


    def update_value(self, value):
        self.value = value
        self.text.setPlainText(str(value))
        self._center_text()


class ArrayBarItem(QGraphicsRectItem):
    """Столбец для визуализации элемента массива."""

    def __init__(self, x, height, index, width=20):
        super().__init__(0, 0, width, height)
        self.index = index
        self.setPos(x, -height)
        self.setBrush(QBrush(QColor("#3E7BFA")))

    def highlight(self, color="#FA3E3E"):
        self.setBrush(QBrush(QColor(color)))

    def reset_color(self):
        self.setBrush(QBrush(QColor("#3E7BFA")))
