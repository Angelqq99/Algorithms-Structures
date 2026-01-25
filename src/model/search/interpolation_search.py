import time
from typing import List, Generator, Dict, Any

class InterpolationSearch:
    """Алгоритм интерполяционного поиска с пошаговой визуализацией."""
    
    def __init__(self, arr: List[int], target: int):
        """
        Инициализация алгоритма интерполяционного поиска.
        
        Args:
            arr: Отсортированный массив для поиска
            target: Искомое значение
        """
        self.arr = arr.copy()
        self.target = target
        self.n = len(arr)
        
    def step_generator(self) -> Generator[Dict[str, Any], None, None]:
        """Генератор пошагового выполнения интерполяционного поиска."""
        
        # Начало поиска
        yield {
            "type": "interpolation_search_start",
            "target": self.target,
            "description": f"Начинаем интерполяционный поиск значения {self.target}"
        }
        
        left, right = 0, self.n - 1
        steps = 0
        
        while left <= right and self.target >= self.arr[left] and self.target <= self.arr[right]:
            steps += 1
            
            # Вычисляем позицию с помощью интерполяционной формулы
            if left == right:
                pos = left
            else:
                # Интерполяционная формула
                pos = left + ((self.target - self.arr[left]) * (right - left)) // (self.arr[right] - self.arr[left])
            
            # Ограничиваем pos в пределах массива
            pos = max(left, min(pos, right))
            pos_value = self.arr[pos]
            
            yield {
                "type": "interpolation_search_calc",
                "left": left,
                "right": right,
                "pos": pos,
                "pos_value": pos_value,
                "left_value": self.arr[left],
                "right_value": self.arr[right],
                "description": f"Шаг {steps}: рассчитанная позиция {pos} по формуле интерполяции"
            }
            
            # Сравниваем элемент на рассчитанной позиции с целевым значением
            if pos_value == self.target:
                yield {
                    "type": "interpolation_search_compare",
                    "pos": pos,
                    "pos_value": pos_value,
                    "target": self.target,
                    "comparison": "equal",
                    "description": f"✅ Найдено! Значение {self.target} на позиции {pos}"
                }
                return
            elif pos_value < self.target:
                yield {
                    "type": "interpolation_search_compare",
                    "pos": pos,
                    "pos_value": pos_value,
                    "target": self.target,
                    "comparison": "less",
                    "description": f"{pos_value} < {self.target}, ищем справа"
                }
                left = pos + 1
                direction = "right"
            else:
                yield {
                    "type": "interpolation_search_compare",
                    "pos": pos,
                    "pos_value": pos_value,
                    "target": self.target,
                    "comparison": "greater",
                    "description": f"{pos_value} > {self.target}, ищем слева"
                }
                right = pos - 1
                direction = "left"
            
            # Показываем сужение диапазона
            if left <= right:
                yield {
                    "type": "interpolation_search_narrow",
                    "left": left,
                    "right": right,
                    "direction": direction,
                    "description": f"Сужение поиска до {'правой' if direction == 'right' else 'левой'} части"
                }
        
        # Элемент не найден
        yield {
            "type": "interpolation_search_not_found",
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
            "array": self.arr.copy(),
            "algorithm": "Interpolation Search"
        }