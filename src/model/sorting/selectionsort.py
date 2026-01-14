from model.base_algorithm import BaseAlgorithm


class SelectionSort(BaseAlgorithm):
    """Пошаговый Selection Sort с визуализацией поиска минимума и обменов."""
    
    def step_generator(self):
        arr = self.data.copy()
        n = len(arr)
        
        yield {
            "type": "info",
            "description": f"Начинаем сортировку выбором массива из {n} элементов",
            "array": arr.copy()
        }
        
        for i in range(n):
            min_idx = i
            
            # Подсвечиваем позицию для вставки минимума
            yield {
                "type": "selection_current",
                "current_index": i,
                "array": arr.copy(),
                "description": f"🔄 Ищем минимальный элемент для позиции {i}"
            }
            
            # Поиск минимального элемента в неотсортированной части
            for j in range(i + 1, n):
                self.step_count += 1
                
                # Подсвечиваем текущие элементы для сравнения
                yield {
                    "type": "selection_compare",
                    "indices": (min_idx, j),
                    "current_min_index": min_idx,
                    "current_min_value": arr[min_idx],
                    "compared_value": arr[j],
                    "array": arr.copy(),
                    "description": f"🔍 Сравниваем: arr[{min_idx}]={arr[min_idx]} vs arr[{j}]={arr[j]}"
                }
                
                if arr[j] < arr[min_idx]:
                    # Новый минимальный элемент найден
                    min_idx = j
                    yield {
                        "type": "selection_new_min",
                        "new_min_index": min_idx,
                        "new_min_value": arr[min_idx],
                        "array": arr.copy(),
                        "description": f"✨ Новый минимальный элемент: {arr[min_idx]} на позиции {min_idx}"
                    }
                else:
                    # Элемент не меньше текущего минимума
                    yield {
                        "type": "selection_not_min",
                        "compared_index": j,
                        "compared_value": arr[j],
                        "current_min_value": arr[min_idx],
                        "array": arr.copy(),
                        "description": f"✖️ Элемент {arr[j]} не меньше текущего минимума {arr[min_idx]}"
                    }
            
            # Если минимальный элемент не на своей позиции - меняем местами
            if min_idx != i:
                # Подготовка к обмену
                yield {
                    "type": "selection_pre_swap",
                    "indices": (i, min_idx),
                    "values": (arr[i], arr[min_idx]),
                    "array": arr.copy(),
                    "description": f"🔄 Меняем местами элементы: arr[{i}]={arr[i]} ↔ arr[{min_idx}]={arr[min_idx]}"
                }
                
                # Обмен
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                self.step_count += 1
                
                yield {
                    "type": "selection_swap",
                    "indices": (i, min_idx),
                    "values": (arr[i], arr[min_idx]),
                    "array": arr.copy(),
                    "description": f"✅ Обмен выполнен: {arr[min_idx]} → позиция {i}, {arr[i]} → позиция {min_idx}"
                }
            else:
                # Элемент уже на правильном месте
                yield {
                    "type": "selection_already_sorted",
                    "index": i,
                    "value": arr[i],
                    "array": arr.copy(),
                    "description": f"✅ Элемент {arr[i]} уже на своей позиции {i}"
                }
            
            # Подсвечиваем отсортированную часть
            sorted_indices = list(range(0, i + 1))
            yield {
                "type": "selection_sorted_part",
                "sorted_indices": sorted_indices,
                "array": arr.copy(),
                "description": f"📊 Отсортировано элементов: {i + 1}/{n}"
            }
            
            # Показываем текущее состояние
            yield {
                "type": "info",
                "description": f"📈 Прогресс: {i + 1}/{n} позиций отсортировано",
                "array": arr.copy()
            }
        
        # Завершение сортировки
        yield {
            "type": "complete", 
            "array": arr.copy(),
            "description": "🎉 Сортировка выбором завершена! Весь массив отсортирован."
        }
    
    def _estimate_total_steps(self):
        """Оценка общего количества шагов для Selection Sort."""
        n = len(self.data)
        # Сравнений: n*(n-1)/2, обменов: n-1 в худшем случае
        return n * (n - 1) // 2 + (n - 1)