from model.base_algorithm import BaseAlgorithm


class InsertionSort(BaseAlgorithm):
    """Пошаговый Insertion Sort с визуализацией вставки элементов."""
    
    def step_generator(self):
        arr = self.data.copy()
        n = len(arr)
        
        yield {
            "type": "info",
            "description": f"Начинаем сортировку вставками массива из {n} элементов",
            "array": arr.copy()
        }
        
        # Первый элемент считается отсортированным
        yield {
            "type": "insertion_sorted_init",
            "sorted_index": 0,
            "value": arr[0],
            "array": arr.copy(),
            "description": f"✅ Элемент {arr[0]} на позиции 0 считается отсортированным"
        }
        
        for i in range(1, n):
            key = arr[i]
            j = i - 1
            
            # Начинаем вставку текущего элемента
            yield {
                "type": "insertion_start",
                "key_index": i,
                "key_value": key,
                "array": arr.copy(),
                "description": f"🔑 Начинаем вставку элемента {key} с позиции {i}"
            }
            
            # Показываем элементы, с которыми будем сравнивать
            yield {
                "type": "insertion_comparing_range",
                "start_index": i - 1,
                "key_index": i,
                "array": arr.copy(),
                "description": f"📊 Ищем правильное место для {key} среди элементов слева"
            }
            
            # Поиск позиции для вставки
            while j >= 0 and arr[j] > key:
                self.step_count += 1
                
                # Сравнение с текущим элементом
                yield {
                    "type": "insertion_compare",
                    "current_index": j,
                    "key_index": i,
                    "current_value": arr[j],
                    "key_value": key,
                    "array": arr.copy(),
                    "description": f"🔍 Сравнение: arr[{j}]={arr[j]} > {key}"
                }
                
                # Сдвиг элемента вправо
                arr[j + 1] = arr[j]
                
                yield {
                    "type": "insertion_shift",
                    "from_index": j,
                    "to_index": j + 1,
                    "shifted_value": arr[j + 1],
                    "array": arr.copy(),
                    "description": f"➡️ Сдвиг элемента {arr[j + 1]} с позиции {j} на позицию {j + 1}"
                }
                
                # Обновление индекса
                j -= 1
                
                if j >= 0:
                    # Показываем следующее сравнение
                    yield {
                        "type": "insertion_next_comparison",
                        "next_index": j,
                        "key_value": key,
                        "array": arr.copy(),
                        "description": f"📝 Переходим к сравнению с элементом на позиции {j}"
                    }
            
            # Вставка ключа на правильное место
            if j + 1 != i:
                arr[j + 1] = key
                self.step_count += 1
                
                yield {
                    "type": "insertion_insert",
                    "from_index": i,
                    "to_index": j + 1,
                    "value": key,
                    "array": arr.copy(),
                    "description": f"📍 Вставляем элемент {key} на позицию {j + 1}"
                }
            else:
                # Элемент уже на своем месте
                yield {
                    "type": "insertion_already_sorted",
                    "index": i,
                    "value": key,
                    "array": arr.copy(),
                    "description": f"✅ Элемент {key} уже на правильной позиции {i}"
                }
            
            # Показываем отсортированную часть
            sorted_indices = list(range(0, i + 1))
            yield {
                "type": "insertion_sorted_part",
                "sorted_indices": sorted_indices,
                "newly_sorted_index": j + 1,
                "array": arr.copy(),
                "description": f"📊 Первые {i + 1} элементов отсортированы"
            }
            
            # Прогресс
            yield {
                "type": "info",
                "description": f"📈 Прогресс: {i + 1}/{n} элементов обработано",
                "array": arr.copy()
            }
        
        # Завершение сортировки
        yield {
            "type": "complete", 
            "array": arr.copy(),
            "description": "🎉 Сортировка вставками завершена! Массив полностью отсортирован."
        }
    
    def _estimate_total_steps(self):
        """Оценка общего количества шагов для Insertion Sort."""
        n = len(self.data)
        # В худшем случае: сравнений = n*(n-1)/2, сдвигов = n*(n-1)/2
        return n * (n - 1)