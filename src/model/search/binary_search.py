# model/search/binary_search.py

import time
from typing import List, Generator, Dict, Any

class BinarySearch:
    """Алгоритм бинарного поиска с пошаговой визуализацией."""
    
    def __init__(self, arr: List[int], target: int):
        """
        Инициализация алгоритма бинарного поиска.
        
        Args:
            arr: Отсортированный массив для поиска
            target: Искомое значение
        """
        self.arr = arr.copy()
        self.target = target
        self.n = len(arr)
        
    def step_generator(self) -> Generator[Dict[str, Any], None, None]:
        """Генератор пошагового выполнения бинарного поиска."""
        
        # Начало поиска
        yield {
            "type": "binary_search_start",
            "target": self.target,
            "description": f"Начинаем бинарный поиск значения {self.target}"
        }
        
        left, right = 0, self.n - 1
        steps = 0
        
        while left <= right:
            steps += 1
            
            # Вычисляем средний индекс
            mid = (left + right) // 2
            mid_value = self.arr[mid]
            
            yield {
                "type": "binary_search_mid",
                "left": left,
                "right": right,
                "mid": mid,
                "mid_value": mid_value,
                "description": f"Шаг {steps}: диапазон [{left}:{right}], средний индекс {mid}"
            }
            
            # Сравниваем средний элемент с целевым значением
            if mid_value == self.target:
                yield {
                    "type": "binary_search_compare",
                    "mid": mid,
                    "mid_value": mid_value,
                    "target": self.target,
                    "comparison": "equal",
                    "description": f"✅ Найдено! Значение {self.target} на позиции {mid}"
                }
                return
            elif mid_value < self.target:
                yield {
                    "type": "binary_search_compare",
                    "mid": mid,
                    "mid_value": mid_value,
                    "target": self.target,
                    "comparison": "less",
                    "description": f"{mid_value} < {self.target}, ищем в правой половине"
                }
                left = mid + 1
                direction = "right"
            else:
                yield {
                    "type": "binary_search_compare",
                    "mid": mid,
                    "mid_value": mid_value,
                    "target": self.target,
                    "comparison": "greater",
                    "description": f"{mid_value} > {self.target}, ищем в левой половине"
                }
                right = mid - 1
                direction = "left"
            
            # Показываем сужение диапазона
            if left <= right:
                yield {
                    "type": "binary_search_narrow",
                    "left": left,
                    "right": right,
                    "direction": direction,
                    "description": f"Сужение поиска до {'правой' if direction == 'right' else 'левой'} половины"
                }
        
        # Элемент не найден
        yield {
            "type": "binary_search_not_found",
            "target": self.target,
            "description": f"❌ Значение {self.target} не найдено в массиве"
        }
    
    def get_array(self) -> List[int]:
        """Возвращает текущий массив."""
        return self.arr.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику поиска."""
        return {
            "array_size": self.n,
            "target": self.target,
            "array": self.arr.copy()
        }