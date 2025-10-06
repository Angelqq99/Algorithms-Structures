"""
Панель переменных и состояния (в будущем можно расширить).
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class Inspector(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Инспектор состояния алгоритма")
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_info(self, text):
        self.label.setText(text)

