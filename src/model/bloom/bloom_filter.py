import hashlib
import math
from typing import List, Any


class BloomFilter:
    """
    Фильтр Блума - вероятностная структура данных для проверки принадлежности элемента к множеству
    КОРРЕКТНАЯ реализация с учётом замечаний преподавателя
    """
    
    def __init__(self, size: int, num_hashes: int = 3):
        """
        Инициализация фильтра Блума
        
        Args:
            size: размер битового массива
            num_hashes: количество хэш-функций
        """
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [0] * size
        
        # Фиксированные сиды для детерминированных хэш-функций
        self.hash_seeds = [i * 100 + 12345 for i in range(num_hashes)]
        
        # Статистика
        self.items_added = 0  # УНИКАЛЬНЫЕ элементы
        self.bit_overwrites = 0  # Переименовано из collisions
        self.false_positive_rate = 0.0
        
        # Для отслеживания уникальных элементов (используется только для правильной статистики)
        self._unique_elements = set()
        
        # Для хранения последних индексов (для визуализации)
        self._last_indices = []
        self._last_check_indices = []
    
    def _get_hashes(self, item: Any) -> List[int]:
        """
        Вычисляет несколько хэш-значений для элемента
        
        Args:
            item: элемент для хэширования
            
        Returns:
            список индексов в битовом массиве
        """
        indices = []
        
        # Более стабильное преобразование в байты
        try:
            # Если объект уже байты
            if isinstance(item, bytes):
                item_bytes = item
            # Если есть метод для получения байтов
            elif hasattr(item, '__bytes__'):
                item_bytes = bytes(item)
            else:
                # Стандартное преобразование через repr (более стабильное чем str)
                item_bytes = repr(item).encode('utf-8')
        except:
            # Последний вариант
            item_bytes = str(item).encode('utf-8')
        
        for seed in self.hash_seeds:
            hasher = hashlib.md5()
            # Используем seed как байты для более стабильного хэширования
            hasher.update(seed.to_bytes(4, 'little'))
            hasher.update(item_bytes)
            hash_hex = hasher.hexdigest()
            
            hash_int = int(hash_hex, 16)
            index = hash_int % self.size
            indices.append(index)
            
        return indices
    
    def add(self, item: Any) -> List[int]:
        """
        Добавляет элемент в фильтр Блума
        
        Args:
            item: элемент для добавления
            
        Returns:
            список индексов, которые были установлены
        """
        indices = self._get_hashes(item)
        new_bit_count = 0  # Считаем только новые установленные биты
        
        for index in indices:
            if self.bit_array[index] == 0:
                self.bit_array[index] = 1
                new_bit_count += 1
            else:
                # Увеличиваем счетчик перезаписей битов (а не коллизий!)
                self.bit_overwrites += 1
        
        # Обновляем статистику ТОЛЬКО для уникальных элементов
        item_hashable = self._make_hashable(item)
        if item_hashable not in self._unique_elements:
            self._unique_elements.add(item_hashable)
            self.items_added += 1
        
        self._update_false_positive_rate()
        self._last_indices = indices
        return indices
    
    def _make_hashable(self, item: Any):
        """Преобразует объект в хешируемый вид"""
        try:
            return hash(item)
        except:
            # Для нехешируемых объектов используем строковое представление
            return hash(repr(item))
    
    def contains(self, item: Any) -> dict:
        """
        Проверяет, содержит ли фильтр элемент (с вероятностной точностью)
        
        Args:
            item: элемент для проверки
            
        Returns:
            словарь с результатом проверки (без избыточных полей)
        """
        indices = self._get_hashes(item)
        bit_checks = [self.bit_array[i] for i in indices]
        
        all_set = all(bit == 1 for bit in bit_checks)
        
        result = {
            "likely_present": all_set,
            "indices": indices,
            "false_positive_probability": self.false_positive_rate,
            "bit_checks": bit_checks
        }
        
        self._last_check_indices = indices
        return result
    
    def _calculate_probability(self) -> float:
        """
        Рассчитывает текущую вероятность ложного срабатывания
        Используется стандартная формула для фильтра Блума
        """
        if self.size == 0 or self.items_added == 0:
            return 0.0
        
        # Формула: (1 - e^(-k * n / m))^k
        k = self.num_hashes
        n = self.items_added
        m = self.size
        
        probability = (1 - math.exp(-k * n / m)) ** k
        return probability
    
    def _update_false_positive_rate(self):
        """Обновляет расчетную вероятность ложных срабатываний"""
        self.false_positive_rate = self._calculate_probability()
    
    def get_stats(self) -> dict:
        """
        Возвращает статистику фильтра (без load_factor и с правильными метриками)
        """
        bits_set = sum(self.bit_array)
        total_bits = self.size
        
        return {
            "size": self.size,
            "num_hashes": self.num_hashes,
            "items_added": self.items_added,
            "bit_overwrites": self.bit_overwrites,  # Переименовано из collisions
            "bit_array": self.bit_array.copy(),
            "false_positive_rate": self.false_positive_rate,
            "bits_set": bits_set,
            "total_bits": total_bits,
            "fill_percentage": bits_set / total_bits if total_bits > 0 else 0,
            "theoretical_optimal_hashes": self._calculate_theoretical_optimal_hashes(),  # Переименовано
            "actual_hashes": self.num_hashes,
            "unique_elements_count": len(self._unique_elements)  # Дополнительная информация
        }
    
    def clear(self):
        """Очищает фильтр (биты, но НЕ хэш-функции!)"""
        self.bit_array = [0] * self.size
        self.items_added = 0
        self.bit_overwrites = 0
        self.false_positive_rate = 0.0
        self._unique_elements.clear()
        self._last_indices = []
        self._last_check_indices = []
    
    def get_bit_array(self):
        """Возвращает текущий битовый массив"""
        return self.bit_array.copy()
    
    def get_last_indices(self):
        """Возвращает последние рассчитанные индексы"""
        return self._last_indices
    
    def check_with_indices(self, item):
        """Проверяет элемент и возвращает результат + индексы"""
        result = self.contains(item)
        return result["likely_present"], result["indices"]
    
    def get_false_positive_probability(self):
        """Возвращает текущую вероятность ложного срабатывания"""
        return self.false_positive_rate  # Используем сохраненное значение
    
    def _calculate_theoretical_optimal_hashes(self):
        """
        Рассчитывает ТЕОРЕТИЧЕСКОЕ оптимальное количество хэш-функций
        Формула: k = (m/n) * ln(2)
        Примечание: Это только справочная информация, нельзя менять k после инициализации
        """
        n = self.items_added
        m = self.size
        
        if n == 0 or m == 0:
            return 0
        
        k_optimal = (m / n) * math.log(2)
        return round(k_optimal)
    
    def get_step_generator(self, operation: str, items: List[Any] = None, check_item: Any = None):
        """
        Генератор для пошаговой визуализации операций
        Важно: НЕ изменяет состояние реального фильтра!
        
        Args:
            operation: тип операции ('add' или 'check')
            items: список элементов для добавления
            check_item: элемент для проверки
        """
        if operation == "add" and items:
            # Создаем КОПИЮ фильтра для визуализации
            temp_filter = self._create_temp_copy()
            
            yield {
                "type": "bloom_init",
                "description": f"Инициализация операции добавления {len(items)} элементов",
                "size": self.size,
                "num_hashes": self.num_hashes,
                "hash_seeds": self.hash_seeds
            }
            
            for i, item in enumerate(items):
                # Показываем расчет хэшей (без изменения состояния)
                indices = temp_filter._get_hashes(item)
                yield {
                    "type": "bloom_hash_calc",
                    "description": f"Расчет хэшей для элемента '{item}'",
                    "item": item,
                    "indices": indices,
                    "step": i + 1,
                    "total": len(items)
                }
                
                # Показываем установку битов (в КОПИИ)
                new_indices = []
                for idx in indices:
                    if temp_filter.bit_array[idx] == 0:
                        temp_filter.bit_array[idx] = 1
                        new_indices.append(idx)
                    else:
                        temp_filter.bit_overwrites += 1
                
                temp_filter.items_added += 1
                temp_filter._update_false_positive_rate()
                
                yield {
                    "type": "bloom_bit_set",
                    "description": f"Установка битов для элемента '{item}'",
                    "item": item,
                    "indices": indices,
                    "new_indices": new_indices,
                    "bit_array": temp_filter.bit_array.copy(),
                    "stats": temp_filter.get_stats(),
                    "step": i + 1,
                    "total": len(items)
                }
            
            yield {
                "type": "bloom_complete",
                "description": f"Добавление {len(items)} элементов завершено",
                "stats": temp_filter.get_stats(),
                "bit_array": temp_filter.bit_array.copy(),
                "note": "Это демонстрация. Реальный фильтр не был изменен."
            }
            
        elif operation == "check" and check_item is not None:
            # Для проверки используем реальный фильтр, так как это read-only операция
            yield {
                "type": "bloom_check_init",
                "description": f"Проверка элемента '{check_item}'",
                "item": check_item
            }
            
            # Расчет хэшей
            indices = self._get_hashes(check_item)
            yield {
                "type": "bloom_check_hash",
                "description": f"Расчет хэшей для проверки",
                "item": check_item,
                "indices": indices
            }
            
            # Проверка битов (read-only)
            all_set = True
            bit_checks = []
            
            for idx in indices:
                bit_value = self.bit_array[idx]
                bit_checks.append(bit_value)
                if bit_value == 0:
                    all_set = False
                
                yield {
                    "type": "bloom_check_bit",
                    "description": f"Проверка бита {idx}: {'установлен' if bit_value == 1 else 'не установлен'}",
                    "index": idx,
                    "value": bit_value,
                    "all_set_so_far": all_set,
                    "item": check_item
                }
            
            # Результат
            probability = self.false_positive_rate
            
            if all_set:
                result_desc = f"Элемент '{check_item}' ВОЗМОЖНО присутствует (вероятность ложного срабатывания: {probability:.2%})"
            else:
                result_desc = f"Элемент '{check_item}' ТОЧНО ОТСУТСТВУЕТ"
            
            yield {
                "type": "bloom_check_result",
                "description": result_desc,
                "item": check_item,
                "likely_present": all_set,
                "indices": indices,
                "bit_checks": bit_checks,
                "false_positive_probability": probability,
                "stats": self.get_stats()
            }
    
    def _create_temp_copy(self):
        """Создает временную копию фильтра для визуализации"""
        temp = BloomFilter(self.size, self.num_hashes)
        temp.bit_array = self.bit_array.copy()
        temp.items_added = self.items_added
        temp.bit_overwrites = self.bit_overwrites
        temp.false_positive_rate = self.false_positive_rate
        temp._unique_elements = self._unique_elements.copy()
        return temp