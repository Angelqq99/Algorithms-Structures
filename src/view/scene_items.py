"""
Элементы визуализации для QGraphicsScene.
"""
from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QBrush, QColor


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
