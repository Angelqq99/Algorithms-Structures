from model.base_algorithm import BaseAlgorithm


class BubbleSort(BaseAlgorithm):
    """Пошаговый BubbleSort с визуализацией сравнений и обменов."""
    
    def step_generator(self):
        arr = self.data
        n = len(arr)
        
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                self.step_count += 1
                yield {
                    "type": "compare", 
                    "indices": (j, j+1), 
                    "array": arr.copy(),
                    "description": f"Сравнение элементов {j} и {j+1}"
                }
                
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
                    self.step_count += 1
                    yield {
                        "type": "swap", 
                        "indices": (j, j+1), 
                        "array": arr.copy(),
                        "description": f"Обмен элементов {j} и {j+1}"
                    }
            
            # Если на этой итерации не было обменов, массив отсортирован
            if not swapped:
                break
        
        yield {
            "type": "complete", 
            "array": arr.copy(),
            "description": "Сортировка пузырьком завершена"
        }

    def _estimate_total_steps(self):
        """Оценка общего количества шагов для BubbleSort."""
        n = len(self.data)
        return n * (n - 1)  # O(n²)