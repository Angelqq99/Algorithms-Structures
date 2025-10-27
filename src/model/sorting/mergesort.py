from model.base_algorithm import BaseAlgorithm


class MergeSort(BaseAlgorithm):
    """Пошаговый MergeSort для визуализации."""
    
    def step_generator(self):
        arr = self.data.copy()
        yield from self._merge_sort(arr, 0, len(arr) - 1)
        
        yield {
            "type": "complete", 
            "array": arr,
            "description": "Сортировка слиянием завершена"
        }

    def _merge_sort(self, arr, left, right):
        """Рекурсивная функция сортировки слиянием."""
        if left < right:
            mid = (left + right) // 2
            
            # Сортировка левой половины
            yield from self._merge_sort(arr, left, mid)
            
            # Сортировка правой половины
            yield from self._merge_sort(arr, mid + 1, right)
            
            # Слияние отсортированных половин
            yield from self._merge(arr, left, mid, right)

    def _merge(self, arr, left, mid, right):
        """Слияние двух отсортированных подмассивов."""
        left_copy = arr[left:mid + 1]
        right_copy = arr[mid + 1:right + 1]
        
        i = j = 0
        k = left
        
        while i < len(left_copy) and j < len(right_copy):
            self.step_count += 1
            yield {
                "type": "compare",
                "indices": (left + i, mid + 1 + j),
                "array": arr.copy(),
                "description": f"Сравнение при слиянии: {left_copy[i]} vs {right_copy[j]}"
            }
            
            if left_copy[i] <= right_copy[j]:
                arr[k] = left_copy[i]
                i += 1
            else:
                arr[k] = right_copy[j]
                j += 1
            
            self.step_count += 1
            yield {
                "type": "insert",
                "indices": (k,),
                "array": arr.copy(),
                "description": f"Вставка элемента в позицию {k}"
            }
            k += 1
        
        # Копирование оставшихся элементов
        while i < len(left_copy):
            arr[k] = left_copy[i]
            self.step_count += 1
            yield {
                "type": "insert",
                "indices": (k,),
                "array": arr.copy(),
                "description": f"Вставка оставшегося элемента в позицию {k}"
            }
            i += 1
            k += 1
        
        while j < len(right_copy):
            arr[k] = right_copy[j]
            self.step_count += 1
            yield {
                "type": "insert",
                "indices": (k,),
                "array": arr.copy(),
                "description": f"Вставка оставшегося элемента в позицию {k}"
            }
            j += 1
            k += 1

    def _estimate_total_steps(self):
        """Оценка общего количества шагов для MergeSort."""
        n = len(self.data)
        return n * (n.bit_length() + 1)  # O(n log n)