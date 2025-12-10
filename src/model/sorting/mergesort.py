from model.base_algorithm import BaseAlgorithm


class MergeSort(BaseAlgorithm):
    """Пошаговый MergeSort для визуализации."""
    
    def step_generator(self):
        arr = self.data.copy()
        
        # Итеративный подход (bottom-up)
        n = len(arr)
        size = 1
        
        yield {
            "type": "info",
            "description": f"Начинаем сортировку слиянием массива из {n} элементов",
            "array": arr.copy()
        }
        
        while size < n:
            yield {
                "type": "info",
                "description": f"Размер подмассивов для слияния: {size}",
                "array": arr.copy()
            }
            
            for left in range(0, n, 2 * size):
                mid = min(left + size - 1, n - 1)
                right = min(left + 2 * size - 1, n - 1)
                
                if mid < right:  # Если есть что сливать
                    # Показываем, какие подмассивы сливаем
                    yield {
                        "type": "merge_start",
                        "left": left,
                        "mid": mid,
                        "right": right,
                        "left_array": arr[left:mid + 1],
                        "right_array": arr[mid + 1:right + 1],
                        "description": f"Слияние: [{left}:{mid}] и [{mid+1}:{right}]",
                        "array": arr.copy()
                    }
                    
                    # Сливаем с пошаговой визуализацией
                    for action in self._merge_with_steps(arr, left, mid, right):
                        yield action
                    
                    # Показываем результат
                    yield {
                        "type": "merge_complete",
                        "left": left,
                        "right": right,
                        "array": arr.copy(),
                        "description": f"✅ Подмассив [{left}:{right}] отсортирован"
                    }
                else:
                    # Если нечего сливать (подмассив уже отсортирован)
                    yield {
                        "type": "info",
                        "description": f"Подмассив [{left}:{right}] уже отсортирован",
                        "array": arr.copy()
                    }
            
            size *= 2
        
        yield {
            "type": "complete", 
            "array": arr,
            "description": "✅ Сортировка слиянием завершена! Массив отсортирован."
        }
    
    def _merge_with_steps(self, arr, left, mid, right):
        """Слияние с пошаговой визуализацией."""
        left_copy = arr[left:mid + 1]
        right_copy = arr[mid + 1:right + 1]
        
        # Показываем временные массивы
        yield {
            "type": "temp_arrays",
            "left_copy": left_copy.copy(),
            "right_copy": right_copy.copy(),
            "description": f"Временные массивы: L={left_copy}, R={right_copy}",
            "array": arr.copy()
        }
        
        i = j = 0
        k = left
        
        # Основной цикл слияния
        while i < len(left_copy) and j < len(right_copy):
            self.step_count += 1
            
            # Сравнение элементов
            yield {
                "type": "compare_merge",
                "indices": (left + i, mid + 1 + j),
                "left_value": left_copy[i],
                "right_value": right_copy[j],
                "target_index": k,
                "array": arr.copy(),
                "description": f"Сравнение: {left_copy[i]} vs {right_copy[j]}"
            }
            
            if left_copy[i] <= right_copy[j]:
                # Выбираем элемент из левого массива
                arr[k] = left_copy[i]
                yield {
                    "type": "select_left",  # ИСПРАВЛЕНО
                    "from_index": left + i,
                    "to_index": k,
                    "value": left_copy[i],
                    "array": arr.copy(),
                    "description": f"Выбираем {left_copy[i]} из левого массива"
                }
                i += 1
            else:
                # Выбираем элемент из правого массива
                arr[k] = right_copy[j]
                yield {
                    "type": "select_right",  # ИСПРАВЛЕНО
                    "from_index": mid + 1 + j,
                    "to_index": k,
                    "value": right_copy[j],
                    "array": arr.copy(),
                    "description": f"Выбираем {right_copy[j]} из правого массива"
                }
                j += 1
            
            k += 1
        
        # Оставшиеся элементы из левого массива
        while i < len(left_copy):
            arr[k] = left_copy[i]
            self.step_count += 1
            yield {
                "type": "remaining_left",
                "from_index": left + i,
                "to_index": k,
                "value": left_copy[i],
                "array": arr.copy(),
                "description": f"Оставшийся элемент {left_copy[i]} из левого массива"
            }
            i += 1
            k += 1
        
        # Оставшиеся элементы из правого массива
        while j < len(right_copy):
            arr[k] = right_copy[j]
            self.step_count += 1
            yield {
                "type": "remaining_right",
                "from_index": mid + 1 + j,
                "to_index": k,
                "value": right_copy[j],
                "array": arr.copy(),
                "description": f"Оставшийся элемент {right_copy[j]} из правого массива"
            }
            j += 1
            k += 1
        
        # Итоговый результат слияния
        yield {
            "type": "merge_result",
            "left": left,
            "right": right,
            "merged_array": arr[left:right + 1],
            "array": arr.copy(),
            "description": f"Слияние завершено: {arr[left:right + 1]}"
        }

    def _estimate_total_steps(self):
        """Оценка общего количества шагов для MergeSort."""
        n = len(self.data)
        return n * (n.bit_length() + 1)  # O(n log n)