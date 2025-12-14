from ..base_algorithm import BaseAlgorithm

class HashTable(BaseAlgorithm):
    """Хэш-таблица с выбором функции хеширования и метода разрешения коллизий"""
    def __init__(self, data, size=10, hash_function="division", collision_method="linear"):
        super().__init__(data)
        self.size = size
        self.hash_function = hash_function
        self.collision_method = collision_method
        self.table = [None] * size
        self.inserted_keys = []  # Для отслеживания вставленных ключей
        self.collisions_count = 0
        self.probing_steps = []  # Для отслеживания шагов пробирования
        self.max_chain_length = 0  # Максимальная длина цепочки

    def _hash(self, key):
        """Различные функции хеширования"""
        if self.hash_function == "division":
            return key % self.size
        elif self.hash_function == "multiplication":
            # Метод умножения
            A = 0.6180339887  # Золотое сечение
            return int(self.size * ((key * A) % 1))
        elif self.hash_function == "simple":
            return key % (self.size * 2) % self.size
        return key % self.size  # По умолчанию

    def _probe(self, key, idx):
        """Методы разрешения коллизий"""
        original_idx = idx
        steps = []
        
        if self.collision_method == "linear":
            # Линейное пробирование
            step = 1
            probe_idx = idx
            i = 1
            while self.table[probe_idx] is not None:
                steps.append(probe_idx)
                probe_idx = (original_idx + i * step) % self.size
                i += 1
                if i > self.size:
                    return None, steps  # Таблица полна
            return probe_idx, steps
                
        elif self.collision_method == "quadratic":
            # Квадратичное пробирование
            probe_idx = idx
            i = 1
            while self.table[probe_idx] is not None:
                steps.append(probe_idx)
                probe_idx = (original_idx + i * i) % self.size
                i += 1
                if i > self.size:
                    return None, steps
            return probe_idx, steps
                    
        elif self.collision_method == "double":
            # Двойное хеширование
            def hash2(k):
                return 1 + (k % (self.size - 1))
            
            step = hash2(key)
            probe_idx = idx
            i = 1
            while self.table[probe_idx] is not None:
                steps.append(probe_idx)
                probe_idx = (original_idx + i * step) % self.size
                i += 1
                if i > self.size:
                    return None, steps
            return probe_idx, steps
                    
        elif self.collision_method == "chaining":
            # Метод цепочек
            return idx, []

    def step_generator(self):
        """Генератор операций с дополнительной информацией"""
        for key_index, key in enumerate(self.data):
            idx = self._hash(key)
            original_idx = idx
            collision_occurred = False
            probing_steps = []
            
            # Добавляем информацию о входных данных
            yield {
                "type": "info",
                "key": key,
                "hash_index": idx,
                "original_index": original_idx,
                "description": f"Обработка ключа {key} (хэш-функция: {self.hash_function}, индекс: {idx})"
            }
            
            if self.collision_method == "chaining":
                # Метод цепочек
                if self.table[idx] is None:
                    self.table[idx] = []
                
                # Проверяем дубликаты в цепочке
                existing_keys = [k for k, _ in self.table[idx]]
                if key in existing_keys:
                    # Ключ уже существует
                    yield {
                        "type": "duplicate", 
                        "index": idx, 
                        "key": key,
                        "chain_length": len(self.table[idx]),
                        "description": f"Ключ {key} уже существует в цепочке {idx}"
                    }
                    continue
                
                # Проверяем коллизию
                if len(self.table[idx]) > 0:
                    collision_occurred = True
                    self.collisions_count += 1
                    yield {
                        "type": "collision", 
                        "index": idx, 
                        "key": key,
                        "chain_length": len(self.table[idx]),
                        "description": f"Коллизия при вставке {key} в индекс {idx} (цепочка: {len(self.table[idx])} элементов)"
                    }
                
                # Вставляем в цепочку
                self.table[idx].append((key, f"value_{key}"))
                self.inserted_keys.append(key)
                
                # Обновляем максимальную длину цепочки
                if len(self.table[idx]) > self.max_chain_length:
                    self.max_chain_length = len(self.table[idx])
                
                yield {
                    "type": "insert", 
                    "index": idx, 
                    "key": key,
                    "table": self._get_table_copy(),
                    "chains": self._get_chains_info(),
                    "collisions": self.collisions_count,
                    "max_chain_length": self.max_chain_length,
                    "key_index": key_index,
                    "total_keys": len(self.data),
                    "description": f"Вставлен ключ {key} в цепочку {idx} (длина: {len(self.table[idx])})"
                }
                
            else:
                # Открытая адресация
                if self.table[idx] is not None:
                    collision_occurred = True
                    self.collisions_count += 1
                    yield {
                        "type": "collision", 
                        "index": idx, 
                        "key": key,
                        "occupied_key": self.table[idx][0] if self.table[idx] else None,
                        "description": f"Коллизия: ключ {key} пытается встать в занятый индекс {idx}"
                    }
                    
                    # Ищем новую позицию
                    new_idx, probing_steps = self._probe(key, idx)
                    self.probing_steps.extend(probing_steps)
                    
                    if new_idx is None:
                        yield {
                            "type": "full", 
                            "index": idx, 
                            "key": key,
                            "description": f"Таблица полна, не удалось вставить {key}"
                        }
                        continue
                    
                    # Показываем шаги пробирования
                    if probing_steps:
                        for step_num, step_idx in enumerate(probing_steps, 1):
                            yield {
                                "type": "probing_step",
                                "step": step_num,
                                "index": step_idx,
                                "key": key,
                                "description": f"Шаг {step_num} пробирования: проверка индекса {step_idx}"
                            }
                    
                    idx = new_idx
                
                # Вставляем ключ
                self.table[idx] = (key, f"value_{key}")
                self.inserted_keys.append(key)
                
                probe_info = {
                    "probed_index": idx if collision_occurred else None,
                    "original_index": original_idx if collision_occurred else None,
                    "probing_steps": probing_steps if collision_occurred else [],
                    "probing_steps_count": len(probing_steps) if collision_occurred else 0
                }
                
                yield {
                    "type": "insert", 
                    "index": idx, 
                    "key": key,
                    "table": self._get_table_copy(),
                    "collisions": self.collisions_count,
                    "key_index": key_index,
                    "total_keys": len(self.data),
                    **probe_info,
                    "description": f"Вставлен ключ {key} в индекс {idx}" + 
                                  (f" (первоначально {original_idx}, шагов пробирования: {len(probing_steps)})" 
                                   if collision_occurred else "")
                }
        
        # Финальный результат
        yield {
            "type": "complete",
            "table": self._get_table_copy(),
            "collisions": self.collisions_count,
            "load_factor": len(self.inserted_keys) / self.size,
            "filled_cells": sum(1 for x in self.table if x is not None),
            "total_cells": self.size,
            "max_chain_length": self.max_chain_length,
            "probing_steps_total": len(self.probing_steps),
            "hash_function": self.hash_function,
            "collision_method": self.collision_method,
            "table_size": self.size,
            "description": f"✅ Хэш-таблица построена!\n"
                          f"• Размер таблицы: {self.size}\n"
                          f"• Ключей вставлено: {len(self.inserted_keys)} из {len(self.data)}\n"
                          f"• Коллизий: {self.collisions_count}\n"
                          f"• Коэффициент заполнения: {len(self.inserted_keys)/self.size:.2f}\n"
                          f"• Функция хеширования: {self.hash_function}\n"
                          f"• Метод разрешения коллизий: {self.collision_method}"
        }

    def _get_table_copy(self):
        """Возвращает копию таблицы для отображения"""
        if self.collision_method == "chaining":
            # Для цепочек возвращаем список ключей в каждой цепочке
            result = []
            for chain in self.table:
                if chain:
                    result.append([key for key, _ in chain])
                else:
                    result.append(None)
            return result
        else:
            # Для открытой адресации возвращаем ключи или None
            return [(entry[0] if entry else None) for entry in self.table]

    def _get_chains_info(self):
        """Возвращает информацию о цепочках для метода цепочек"""
        if self.collision_method != "chaining":
            return {}
        
        chains_info = {}
        for i, chain in enumerate(self.table):
            if chain:
                chains_info[i] = {
                    "length": len(chain),
                    "keys": [key for key, _ in chain]
                }
        return chains_info