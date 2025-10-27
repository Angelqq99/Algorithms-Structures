from model.base_algorithm import BaseAlgorithm


class QuickSort(BaseAlgorithm):
    """Пошаговый QuickSort с генерацией сравнений и обменов."""
    
    def step_generator(self):
        arr = self.data
        stack = [(0, len(arr) - 1)]

        while stack:
            low, high = stack.pop()
            if low < high:
                # Разбиение и получение индекса опорного элемента
                pivot_index = yield from self._partition(arr, low, high)
                
                # Добавляем подмассивы в стек
                stack.append((low, pivot_index - 1))
                stack.append((pivot_index + 1, high))

        yield {
            "type": "complete", 
            "array": arr.copy(),
            "description": "Быстрая сортировка завершена"
        }

    def _partition(self, arr, low, high):
        """Разбиение массива относительно опорного элемента."""
        pivot = arr[high]
        i = low - 1
        
        for j in range(low, high):
            self.step_count += 1
            yield {
                "type": "compare",
                "indices": (j, high),
                "array": arr.copy(),
                "description": f"Сравнение с опорным элементом: {arr[j]} vs {pivot}"
            }
            
            if arr[j] <= pivot:
                i += 1
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    self.step_count += 1
                    yield {
                        "type": "swap",
                        "indices": (i, j),
                        "array": arr.copy(),
                        "description": f"Обмен элементов {i} и {j}"
                    }
        
        # Помещаем опорный элемент на правильную позицию
        if i + 1 != high:
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            self.step_count += 1
            yield {
                "type": "swap",
                "indices": (i + 1, high),
                "array": arr.copy(),
                "description": f"Установка опорного элемента на позицию {i + 1}"
            }
        
        return i + 1

    def _estimate_total_steps(self):
        """Оценка общего количества шагов для QuickSort."""
        n = len(self.data)
        return n * (n.bit_length() + 1)  # O(n log n) в среднем случае