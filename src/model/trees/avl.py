from ..base_algorithm import BaseAlgorithm

class AVLTree(BaseAlgorithm):
    """Простейший скелет AVL с генератором шагов"""
    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None
            self.height = 1

    def __init__(self, data):
        super().__init__(data)
        self.root = None

    def step_generator(self):
        for val in self.data:
            # Здесь можно реализовать вставку с балансировкой
            yield {"type": "insert", "value": val}
