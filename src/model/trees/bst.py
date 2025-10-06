from ..base_algorithm import BaseAlgorithm

class BST(BaseAlgorithm):
    """Простейший BST с генератором обхода"""
    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None

    def __init__(self, data):
        super().__init__(data)
        self.root = None

    def step_generator(self):
        # Просто вставка элементов с генерацией шага
        for val in self.data:
            yield {"type": "insert", "value": val}
