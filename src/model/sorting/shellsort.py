from model.base_algorithm import BaseAlgorithm


class ShellSort(BaseAlgorithm):
    """Пошаговый Shell Sort с визуализацией сортировки подмассивов."""
    
    def step_generator(self):
        arr = self.data.copy()
        n = len(arr)
        
        yield {
            "type": "info",
            "description": f"Начинаем сортировку Шелла массива из {n} элементов",
            "array": arr.copy()
        }
        
        # Последовательность интервалов (последовательность Кнута)
        gaps = []
        gap = 1
        while gap < n:
            gaps.append(gap)
            gap = gap * 3 + 1
        
        # Используем последовательность в обратном порядке
        gaps.reverse()
        
        for gap_idx, gap in enumerate(gaps):
            yield {
                "type": "shell_gap_start",
                "gap": gap,
                "gap_index": gap_idx,
                "total_gaps": len(gaps),
                "array": arr.copy(),
                "description": f"🎯 Начинаем этап с интервалом (gap) = {gap}"
            }
            
            # Показываем все группы для данного интервала
            for group_num in range(gap):
                group_indices = list(range(group_num, n, gap))
                if len(group_indices) > 1:
                    yield {
                        "type": "shell_group_start",
                        "group_num": group_num,
                        "gap": gap,
                        "group_indices": group_indices,
                        "array": arr.copy(),
                        "description": f"👥 Группа {group_num + 1} (шаг {gap}): индексы {group_indices}"
                    }
                    
                    # Сортировка вставками для этой группы
                    for i in range(1, len(group_indices)):
                        temp_idx = group_indices[i]
                        temp_val = arr[temp_idx]
                        j = i - 1
                        
                        yield {
                            "type": "shell_current_element",
                            "element_index": temp_idx,
                            "element_value": temp_val,
                            "group_indices": group_indices,
                            "array": arr.copy(),
                            "description": f"🔑 Обрабатываем элемент {temp_val} на позиции {temp_idx}"
                        }
                        
                        while j >= 0 and arr[group_indices[j]] > temp_val:
                            self.step_count += 1
                            
                            # Сравнение
                            compare_idx = group_indices[j]
                            yield {
                                "type": "shell_compare",
                                "current_index": compare_idx,
                                "key_index": temp_idx,
                                "current_value": arr[compare_idx],
                                "key_value": temp_val,
                                "group_indices": group_indices,
                                "gap": gap,
                                "array": arr.copy(),
                                "description": f"🔍 Сравнение в группе: arr[{compare_idx}]={arr[compare_idx]} > {temp_val}"
                            }
                            
                            # Сдвиг
                            arr[group_indices[j + 1]] = arr[group_indices[j]]
                            yield {
                                "type": "shell_shift",
                                "from_index": compare_idx,
                                "to_index": group_indices[j + 1],
                                "shifted_value": arr[group_indices[j + 1]],
                                "gap": gap,
                                "array": arr.copy(),
                                "description": f"➡️ Сдвиг в группе: элемент {arr[group_indices[j + 1]]} на позицию {group_indices[j + 1]}"
                            }
                            
                            j -= 1
                        
                        # Вставка
                        if j + 1 != i:
                            arr[group_indices[j + 1]] = temp_val
                            self.step_count += 1
                            yield {
                                "type": "shell_insert",
                                "original_index": temp_idx,
                                "new_index": group_indices[j + 1],
                                "value": temp_val,
                                "gap": gap,
                                "array": arr.copy(),
                                "description": f"📍 Вставка в группе: {temp_val} на позицию {group_indices[j + 1]}"
                            }
                        
                        # Показываем прогресс внутри группы
                        yield {
                            "type": "shell_group_progress",
                            "group_num": group_num,
                            "gap": gap,
                            "processed_count": i + 1,
                            "total_in_group": len(group_indices),
                            "array": arr.copy(),
                            "description": f"📊 Прогресс в группе: {i + 1}/{len(group_indices)} элементов"
                        }
                    
                    yield {
                        "type": "shell_group_complete",
                        "group_num": group_num,
                        "gap": gap,
                        "group_indices": group_indices,
                        "array": arr.copy(),
                        "description": f"✅ Группа {group_num + 1} отсортирована"
                    }
            
            # Показываем результат после обработки всех групп для данного gap
            yield {
                "type": "shell_gap_complete",
                "gap": gap,
                "gap_index": gap_idx,
                "total_gaps": len(gaps),
                "array": arr.copy(),
                "description": f"✅ Все группы с интервалом {gap} обработаны"
            }
            
            # Показываем состояние массива
            yield {
                "type": "info",
                "description": f"📈 Состояние массива после gap={gap}",
                "array": arr.copy()
            }
        
        # Финальная сортировка вставками (gap = 1)
        yield {
            "type": "shell_final_stage",
            "array": arr.copy(),
            "description": "🎯 Начинаем финальный этап сортировки вставками (gap = 1)"
        }
        
        # Для полноты покажем финальную сортировку
        for i in range(1, n):
            key = arr[i]
            j = i - 1
            
            while j >= 0 and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            
            if j + 1 != i:
                arr[j + 1] = key
        
        # Завершение сортировки
        yield {
            "type": "complete", 
            "array": arr.copy(),
            "description": "🎉 Сортировка Шелла завершена! Массив полностью отсортирован."
        }
    
    def _estimate_total_steps(self):
        """Оценка общего количества шагов для Shell Sort."""
        n = len(self.data)
        # Оценка сложности O(n^(3/2)) для последовательности Кнута
        return int(n * n ** 0.5)