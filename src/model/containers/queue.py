from ..base_algorithm import BaseAlgorithm
from collections import deque

class Queue(BaseAlgorithm):
    """Визуализация работы Очереди (FIFO - First In, First Out)"""
    
    def __init__(self, commands):
        """
        commands: список операций очереди
        Форматы:
        - ("enqueue", value) - добавить элемент в очередь
        - ("dequeue", None) - удалить элемент из очереди
        - ("front", None) - посмотреть первый элемент
        - ("back", None) - посмотреть последний элемент
        - ("size", None) - получить размер
        - ("is_empty", None) - проверить пустоту
        """
        super().__init__(commands)
        self.queue = deque()
        self.max_size = 2000  # Максимальный размер для визуализации
    
    def step_generator(self):
        """Генератор шагов для визуализации"""
        for command in self.data:
            self.step_count += 1
            
            if isinstance(command, tuple):
                operation, value = command
            else:
                operation, value = "enqueue", command
            
            result = None
            description = ""
            current_state = list(self.queue)
            
            if operation == "enqueue":
                if len(self.queue) < self.max_size:
                    self.queue.append(value)
                    description = f"📥 Добавлен в очередь: {value}"
                else:
                    description = "❌ Очередь переполнена!"
                
                yield {
                    "type": "enqueue",
                    "value": value,
                    "queue": list(self.queue),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "dequeue":
                if self.queue:
                    value = self.queue.popleft()
                    description = f"📤 Извлечен из очереди: {value}"
                    result = value
                else:
                    description = "❌ Очередь пуста!"
                
                yield {
                    "type": "dequeue",
                    "value": result,
                    "queue": list(self.queue),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "front":
                if self.queue:
                    value = self.queue[0]
                    description = f"👁 Первый элемент: {value}"
                    result = value
                else:
                    description = "❌ Очередь пуста!"
                
                yield {
                    "type": "front",
                    "value": result,
                    "queue": list(self.queue),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "back":
                if self.queue:
                    value = self.queue[-1]
                    description = f"👁 Последний элемент: {value}"
                    result = value
                else:
                    description = "❌ Очередь пуста!"
                
                yield {
                    "type": "back",
                    "value": result,
                    "queue": list(self.queue),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "size":
                size = len(self.queue)
                description = f"📊 Размер очереди: {size}"
                
                yield {
                    "type": "size",
                    "size": size,
                    "queue": list(self.queue),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "is_empty":
                is_empty = len(self.queue) == 0
                status = "пуста" if is_empty else "не пуста"
                description = f"📋 Очередь {status}"
                
                yield {
                    "type": "is_empty",
                    "empty": is_empty,
                    "queue": list(self.queue),
                    "description": description,
                    "step": self.step_count
                }
        
        # Завершающий шаг
        yield {
            "type": "complete",
            "queue": list(self.queue),
            "size": len(self.queue),
            "description": "✅ Все операции с очередью выполнены",
            "step": self.step_count
        }
    
    def enqueue(self, value):
        """Добавить элемент в очередь (O(1))"""
        if len(self.queue) < self.max_size:
            self.queue.append(value)
            return True
        return False
    
    def dequeue(self):
        """Удалить элемент из очереди (O(1))"""
        if self.queue:
            return self.queue.popleft()
        return None
    
    def front(self):
        """Посмотреть первый элемент очереди (O(1))"""
        if self.queue:
            return self.queue[0]
        return None
    
    def back(self):
        """Посмотреть последний элемент очереди (O(1))"""
        if self.queue:
            return self.queue[-1]
        return None
    
    def size(self):
        """Получить размер очереди (O(1))"""
        return len(self.queue)
    
    def is_empty(self):
        """Проверить, пуста ли очередь (O(1))"""
        return len(self.queue) == 0
    
    def clear(self):
        """Очистить очередь"""
        self.queue.clear()
    
    def __str__(self):
        return f"Queue({list(self.queue)})"
    def get_info(self):
        return {
            "type": "Queue",
            "size": len(self._items),
            "empty": self.is_empty(),
            "front": self.front() if not self.is_empty() else None,
            "back": self.back() if not self.is_empty() else None,
            "items": self._items.copy()
        }