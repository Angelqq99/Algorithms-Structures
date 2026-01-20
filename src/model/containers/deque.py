from ..base_algorithm import BaseAlgorithm
from collections import deque

class Deque(BaseAlgorithm):
    """Визуализация работы Дека (Double Ended Queue)"""
    
    def __init__(self, commands):
        """
        commands: список операций дека
        Форматы:
        - ("push_front", value) - добавить элемент в начало
        - ("push_back", value) - добавить элемент в конец
        - ("pop_front", None) - удалить элемент из начала
        - ("pop_back", None) - удалить элемент из конца
        - ("front", None) - посмотреть первый элемент
        - ("back", None) - посмотреть последний элемент
        - ("size", None) - получить размер
        - ("is_empty", None) - проверить пустоту
        """
        super().__init__(commands)
        self.deque = deque()
        self.max_size = 2000  # Максимальный размер для визуализации
    
    def step_generator(self):
        """Генератор шагов для визуализации"""
        for command in self.data:
            self.step_count += 1
            
            if isinstance(command, tuple):
                operation, value = command
            else:
                operation, value = "push_back", command
            
            result = None
            description = ""
            current_state = list(self.deque)
            
            if operation == "push_front":
                if len(self.deque) < self.max_size:
                    self.deque.appendleft(value)
                    description = f"⬅️ Добавлен в начало: {value}"
                else:
                    description = "❌ Дек переполнен!"
                
                yield {
                    "type": "push_front",
                    "value": value,
                    "deque": list(self.deque),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "push_back":
                if len(self.deque) < self.max_size:
                    self.deque.append(value)
                    description = f"➡️ Добавлен в конец: {value}"
                else:
                    description = "❌ Дек переполнен!"
                
                yield {
                    "type": "push_back",
                    "value": value,
                    "deque": list(self.deque),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "pop_front":
                if self.deque:
                    value = self.deque.popleft()
                    description = f"⬅️ Извлечен из начала: {value}"
                    result = value
                else:
                    description = "❌ Дек пуст!"
                
                yield {
                    "type": "pop_front",
                    "value": result,
                    "deque": list(self.deque),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "pop_back":
                if self.deque:
                    value = self.deque.pop()
                    description = f"➡️ Извлечен из конца: {value}"
                    result = value
                else:
                    description = "❌ Дек пуст!"
                
                yield {
                    "type": "pop_back",
                    "value": result,
                    "deque": list(self.deque),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "front":
                if self.deque:
                    value = self.deque[0]
                    description = f"👁 Первый элемент: {value}"
                    result = value
                else:
                    description = "❌ Дек пуст!"
                
                yield {
                    "type": "front",
                    "value": result,
                    "deque": list(self.deque),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "back":
                if self.deque:
                    value = self.deque[-1]
                    description = f"👁 Последний элемент: {value}"
                    result = value
                else:
                    description = "❌ Дек пуст!"
                
                yield {
                    "type": "back",
                    "value": result,
                    "deque": list(self.deque),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "size":
                size = len(self.deque)
                description = f"📊 Размер дека: {size}"
                
                yield {
                    "type": "size",
                    "size": size,
                    "deque": list(self.deque),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "is_empty":
                is_empty = len(self.deque) == 0
                status = "пуст" if is_empty else "не пуст"
                description = f"📋 Дек {status}"
                
                yield {
                    "type": "is_empty",
                    "empty": is_empty,
                    "deque": list(self.deque),
                    "description": description,
                    "step": self.step_count
                }
        
        # Завершающий шаг
        yield {
            "type": "complete",
            "deque": list(self.deque),
            "size": len(self.deque),
            "description": "✅ Все операции с деком выполнены",
            "step": self.step_count
        }
    
    def push_front(self, value):
        """Добавить элемент в начало дека (O(1))"""
        if len(self.deque) < self.max_size:
            self.deque.appendleft(value)
            return True
        return False
    
    def push_back(self, value):
        """Добавить элемент в конец дека (O(1))"""
        if len(self.deque) < self.max_size:
            self.deque.append(value)
            return True
        return False
    
    def pop_front(self):
        """Извлечь элемент из начала дека (O(1))"""
        if self.deque:
            return self.deque.popleft()
        return None
    
    def pop_back(self):
        """Извлечь элемент из конца дека (O(1))"""
        if self.deque:
            return self.deque.pop()
        return None
    
    def front(self):
        """Посмотреть первый элемент дека (O(1))"""
        if self.deque:
            return self.deque[0]
        return None
    
    def back(self):
        """Посмотреть последний элемент дека (O(1))"""
        if self.deque:
            return self.deque[-1]
        return None
    
    def size(self):
        """Получить размер дека (O(1))"""
        return len(self.deque)
    
    def is_empty(self):
        """Проверить, пуст ли дек (O(1))"""
        return len(self.deque) == 0
    
    def clear(self):
        """Очистить дек"""
        self.deque.clear()
    
    def __str__(self):
        return f"Deque({list(self.deque)})"
    def get_info(self):
        return {
            "type": "Deque",
            "size": len(self._items),
            "empty": self.is_empty(),
            "front": self.front() if not self.is_empty() else None,
            "back": self.back() if not self.is_empty() else None,
            "items": self._items.copy()
        }