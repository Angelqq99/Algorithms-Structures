"""
Binary Heap Implementation
Поддерживает Min-Heap и Max-Heap
"""

import random
from typing import List, Optional, Union, Generator, Dict, Any


class BinaryHeap:
    """Реализация двоичной кучи (Min-Heap или Max-Heap)"""
    
    def __init__(self, data: Optional[List[int]] = None, heap_type: str = 'max'):
        """
        Инициализация кучи
        
        Args:
            data: Начальные данные
            heap_type: 'max' для Max-Heap, 'min' для Min-Heap
        """
        self.heap = []
        self.type = heap_type.lower()
        
        if self.type not in ['max', 'min']:
            raise ValueError("Heap type must be 'max' or 'min'")
        
        if data:
            self._build_heap(data)
    
    def _build_heap(self, data: List[int]) -> None:
        """Построение кучи из массива"""
        self.heap = data.copy()
        
        # Начинаем с последнего нелистового узла
        for i in range(len(self.heap) // 2 - 1, -1, -1):
            self._heapify_down(i)
    
    def _heapify_up(self, index: int) -> None:
        """Восстановление свойства кучи снизу вверх"""
        if index == 0:
            return
        
        parent = (index - 1) // 2
        
        if self._should_swap(parent, index):
            self.heap[parent], self.heap[index] = self.heap[index], self.heap[parent]
            self._heapify_up(parent)
    
    def _heapify_down(self, index: int) -> None:
        """Восстановление свойства кучи сверху вниз"""
        size = len(self.heap)
        left = 2 * index + 1
        right = 2 * index + 2
        target = index
        
        if left < size and self._should_swap(index, left):
            target = left
        
        if right < size and self._should_swap(target, right):
            target = right
        
        if target != index:
            self.heap[index], self.heap[target] = self.heap[target], self.heap[index]
            self._heapify_down(target)
    
    def _should_swap(self, parent_idx: int, child_idx: int) -> bool:
        """Определяет, нужно ли менять местами родителя и потомка"""
        parent_val = self.heap[parent_idx]
        child_val = self.heap[child_idx]
        
        if self.type == 'max':
            return child_val > parent_val
        else:  # min-heap
            return child_val < parent_val
    
    def insert(self, value: int) -> bool:
        """Вставка элемента в кучу"""
        self.heap.append(value)
        self._heapify_up(len(self.heap) - 1)
        return True
    
    def delete(self) -> Optional[int]:
        """Удаление корневого элемента (max или min)"""
        if not self.heap:
            return None
        
        if len(self.heap) == 1:
            return self.heap.pop()
        
        root = self.heap[0]
        # Перемещаем последний элемент в корень
        self.heap[0] = self.heap.pop()
        # Восстанавливаем свойство кучи
        self._heapify_down(0)
        
        return root
    
    def peek(self) -> Optional[int]:
        """Получение корневого элемента без удаления"""
        return self.heap[0] if self.heap else None
    
    def get_size(self) -> int:
        """Получение размера кучи"""
        return len(self.heap)
    
    def is_empty(self) -> bool:
        """Проверка на пустоту"""
        return len(self.heap) == 0
    
    def get_max(self) -> Optional[int]:
        """Получение максимального элемента (только для max-heap)"""
        if self.type != 'max':
            raise ValueError("get_max() can only be called on max-heap")
        return self.heap[0] if self.heap else None
    
    def get_min(self) -> Optional[int]:
        """Получение минимального элемента (только для min-heap)"""
        if self.type != 'min':
            raise ValueError("get_min() can only be called on min-heap")
        return self.heap[0] if self.heap else None
    
    def _get_tree_structure(self) -> Optional[dict]:
            """Получение структуры дерева для визуализации кучи."""
            if not self.heap:
                return None
            
            def build_node(index: int) -> dict:
                if index >= len(self.heap):
                    return None
                
                children = [] # Создаем список для детей
                left_idx = 2 * index + 1
                right_idx = 2 * index + 2
                
                # Рекурсивно строим левое поддерево
                if left_idx < len(self.heap):
                    left_node = build_node(left_idx)
                    if left_node:
                        children.append(left_node) # Добавляем в список
                
                # Рекурсивно строим правое поддерево
                if right_idx < len(self.heap):
                    right_node = build_node(right_idx)
                    if right_node:
                        children.append(right_node) # Добавляем в список
                
                node = {
                    'value': self.heap[index],
                    'children': children,  # Используем ключ 'children', как просит визуализатор
                    'index': index,
                    'color': '#FF6B6B' if self.type == 'max' else '#4ECDC4'
                }
                
                return node
            
            return build_node(0)
    
    def __str__(self) -> str:
        """Строковое представление кучи"""
        return f"{self.type.capitalize()}-Heap: {self.heap}"
    
    def clear(self) -> None:
        """Очистка кучи"""
        self.heap = []
    
    # ============ МЕТОДЫ ДЛЯ ВИЗУАЛИЗАЦИИ ============
    
    def step_generator(self) -> Generator[Dict[str, Any], None, None]:
        """Генератор шагов для визуализации построения кучи."""
        # Возвращаем начальное состояние
        yield {
            "type": "tree",
            "tree_data": self._get_tree_structure(),
            "description": f"Начальное состояние {self.type.capitalize()}-Heap",
            "heap": self.heap.copy(),
            "heap_type": self.type
        }
        
        # Если куча не пустая, можно показать процесс построения
        if self.heap:
            # Показываем структуру кучи
            yield {
                "type": "info",
                "description": f"Куча построена: {self.heap}",
                "heap_size": len(self.heap),
                "root_value": self.peek()
            }
            
            # Показываем корень
            root = self.peek()
            if root is not None:
                yield {
                    "type": "info",
                    "description": f"Корневой элемент: {root}",
                    "highlight_node": root
                }
        
        # Завершаем
        yield {
            "type": "complete",
            "description": f"Построение {self.type.capitalize()}-Heap завершено",
            "heap": self.heap.copy(),
            "heap_type": self.type,
            "size": len(self.heap)
        }
    
    def insert_with_steps(self, value: int) -> Generator[Dict[str, Any], None, None]:
        """Вставка элемента с пошаговой визуализацией."""
        yield {
            "type": "info",
            "description": f"Начало вставки элемента {value} в {self.type.capitalize()}-Heap"
        }
        
        # Добавляем элемент в конец
        self.heap.append(value)
        index = len(self.heap) - 1
        
        yield {
            "type": "tree",
            "tree_data": self._get_tree_structure(),
            "description": f"Элемент {value} добавлен в конец кучи (индекс {index})",
            "highlight_node": value,
            "heap": self.heap.copy()
        }
        
        # Просеивание вверх
        while index > 0:
            parent = (index - 1) // 2
            
            yield {
                "type": "info",
                "description": f"Сравнение элемента {self.heap[index]} с родителем {self.heap[parent]}",
                "highlight_nodes": [self.heap[index], self.heap[parent]]
            }
            
            if self._should_swap(parent, index):
                # Обмен
                self.heap[parent], self.heap[index] = self.heap[index], self.heap[parent]
                
                yield {
                    "type": "tree",
                    "tree_data": self._get_tree_structure(),
                    "description": f"Обмен с родителем: {self.heap[index]} ↔ {self.heap[parent]}",
                    "heap": self.heap.copy()
                }
                
                index = parent
            else:
                yield {
                    "type": "info",
                    "description": "Свойство кучи восстановлено, просеивание завершено"
                }
                break
        
        yield {
            "type": "complete",
            "description": f"Элемент {value} успешно вставлен в кучу",
            "heap": self.heap.copy(),
            "heap_type": self.type,
            "size": len(self.heap)
        }
    
    def delete_with_steps(self) -> Generator[Dict[str, Any], None, None]:
        """Удаление корня с пошаговой визуализацией."""
        if not self.heap:
            yield {
                "type": "info",
                "description": "Куча пуста, нечего удалять"
            }
            return
        
        root = self.peek()
        
        yield {
            "type": "info",
            "description": f"Начало удаления корневого элемента {root}"
        }
        
        if len(self.heap) == 1:
            self.heap.pop()
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure(),
                "description": f"Удален единственный элемент {root}",
                "heap": self.heap.copy()
            }
        else:
            # Сохраняем корень
            old_root = self.heap[0]
            
            # Перемещаем последний элемент в корень
            last_element = self.heap[-1]
            self.heap[0] = last_element
            self.heap.pop()
            
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure(),
                "description": f"Последний элемент {last_element} перемещен в корень",
                "heap": self.heap.copy()
            }
            
            # Просеивание вниз
            index = 0
            size = len(self.heap)
            
            while True:
                left = 2 * index + 1
                right = 2 * index + 2
                target = index
                
                if left < size:
                    yield {
                        "type": "info",
                        "description": f"Сравнение с левым потомком {self.heap[left]}",
                        "highlight_nodes": [self.heap[index], self.heap[left]]
                    }
                    
                    if self._should_swap(index, left):
                        target = left
                
                if right < size:
                    yield {
                        "type": "info",
                        "description": f"Сравнение с правым потомком {self.heap[right]}",
                        "highlight_nodes": [self.heap[target], self.heap[right]]
                    }
                    
                    if self._should_swap(target, right):
                        target = right
                
                if target != index:
                    # Обмен
                    self.heap[index], self.heap[target] = self.heap[target], self.heap[index]
                    
                    yield {
                        "type": "tree",
                        "tree_data": self._get_tree_structure(),
                        "description": f"Обмен с потомком: {self.heap[index]} ↔ {self.heap[target]}",
                        "heap": self.heap.copy()
                    }
                    
                    index = target
                else:
                    yield {
                        "type": "info",
                        "description": "Свойство кучи восстановлено, просеивание завершено"
                    }
                    break
        
        yield {
            "type": "complete",
            "description": f"Корневой элемент {old_root} успешно удален",
            "heap": self.heap.copy(),
            "heap_type": self.type,
            "size": len(self.heap)
        }
    
    def build_heap_with_steps(self, data: List[int]) -> Generator[Dict[str, Any], None, None]:
        """Построение кучи из массива с пошаговой визуализацией."""
        self.heap = data.copy()
        
        yield {
            "type": "info",
            "description": f"Начало построения {self.type.capitalize()}-Heap из массива: {data}",
            "array": data.copy()
        }
        
        # Начинаем с последнего нелистового узла
        start_idx = len(self.heap) // 2 - 1
        
        for i in range(start_idx, -1, -1):
            yield {
                "type": "info",
                "description": f"Просеивание вниз для узла с индексом {i} (значение: {self.heap[i]})",
                "current_index": i
            }
            
            # Просеивание вниз для текущего узла
            index = i
            size = len(self.heap)
            
            while True:
                left = 2 * index + 1
                right = 2 * index + 2
                target = index
                
                if left < size and self._should_swap(index, left):
                    target = left
                
                if right < size and self._should_swap(target, right):
                    target = right
                
                if target != index:
                    # Обмен
                    self.heap[index], self.heap[target] = self.heap[target], self.heap[index]
                    
                    yield {
                        "type": "tree",
                        "tree_data": self._get_tree_structure(),
                        "description": f"Обмен при просеивании: {self.heap[index]} ↔ {self.heap[target]}",
                        "heap": self.heap.copy(),
                        "current_index": index
                    }
                    
                    index = target
                else:
                    break
        
        yield {
            "type": "complete",
            "description": f"Построение {self.type.capitalize()}-Heap завершено",
            "heap": self.heap.copy(),
            "heap_type": self.type,
            "size": len(self.heap),
            "root_value": self.peek()
        }