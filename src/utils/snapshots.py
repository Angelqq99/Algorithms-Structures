"""
Реализация Memento — сохранение и восстановление состояния алгоритма.
"""
import copy

class SnapshotManager:
    def __init__(self):
        self.history = []

    def save(self, state):
        self.history.append(copy.deepcopy(state))

    def undo(self):
        if self.history:
            return self.history.pop()
        return None
