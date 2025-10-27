"""
Базовый класс для всех алгоритмов.
"""
from abc import ABC, abstractmethod


class BaseAlgorithm(ABC):
    def __init__(self, data):
        self.data = data
        self.step_count = 0
        self.total_steps_estimate = self._estimate_total_steps()

    @abstractmethod
    def step_generator(self):
        """Генератор, который yield'ит шаги алгоритма."""
        pass

    def _estimate_total_steps(self):
        """Оценка общего количества шагов для прогресс-бара."""
        # Базовая реализация - можно переопределить в дочерних классах
        if hasattr(self, 'data'):
            n = len(self.data)
            if hasattr(self, '__class__'):
                algo_name = self.__class__.__name__
                if "Sort" in algo_name:
                    return n * n  # O(n²) для сортировок
                elif algo_name in ["BST", "AVL"]:
                    return n * 3  # O(n) для деревьев
            return n * 2
        return 100

    def get_progress(self):
        """Возвращает прогресс выполнения от 0.0 до 1.0."""
        if self.total_steps_estimate > 0:
            return min(1.0, self.step_count / self.total_steps_estimate)
        return 0.0