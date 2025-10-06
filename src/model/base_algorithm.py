"""
Базовый интерфейс алгоритма.
Все алгоритмы наследуются от BaseAlgorithm и реализуют метод step().
"""
from abc import ABC, abstractmethod
from typing import Any, Generator


class BaseAlgorithm(ABC):
    """Абстрактный класс для всех алгоритмов (Model)."""

    def __init__(self, data: Any):
        self.data = data
        self.step_index = 0

    @abstractmethod
    def step_generator(self) -> Generator[dict, None, None]:
        """Возвращает генератор шагов, где каждый шаг — словарь действия."""
        pass

    def reset(self):
        """Сброс состояния алгоритма к начальному."""
        self.step_index = 0

    def snapshot(self) -> dict:
        """Сериализация состояния (для Memento)."""
        return {"data": self.data.copy(), "step_index": self.step_index}
