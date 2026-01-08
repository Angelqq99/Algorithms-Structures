from ..base_algorithm import BaseAlgorithm

class Stack(BaseAlgorithm):
    """Визуализация работы Стека (LIFO - Last In, First Out)"""
    
    def __init__(self, commands):
        """
        commands: список операций стека
        Форматы:
        - ("push", value) - добавить элемент
        - ("pop", None) - извлечь элемент
        - ("peek", None) - посмотреть верхний элемент
        - ("size", None) - получить размер
        - ("is_empty", None) - проверить пустоту
        """
        super().__init__(commands)
        self.stack = []
        self.max_size = 10  # Максимальный размер для визуализации
    
    def step_generator(self):
        """Генератор шагов для визуализации"""
        for command in self.data:
            self.step_count += 1
            
            if isinstance(command, tuple):
                operation, value = command
            else:
                operation, value = "push", command
            
            result = None
            description = ""
            current_state = list(self.stack)
            
            if operation == "push":
                if len(self.stack) < self.max_size:
                    self.stack.append(value)
                    description = f"📥 Добавлен элемент: {value}"
                else:
                    description = "❌ Стек переполнен!"
                
                yield {
                    "type": "push",
                    "value": value,
                    "stack": list(self.stack),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "pop":
                if self.stack:
                    value = self.stack.pop()
                    description = f"📤 Извлечен элемент: {value}"
                    result = value
                else:
                    description = "❌ Стек пуст!"
                
                yield {
                    "type": "pop",
                    "value": result,
                    "stack": list(self.stack),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "peek":
                if self.stack:
                    value = self.stack[-1]
                    description = f"👁 Верхний элемент: {value}"
                    result = value
                else:
                    description = "❌ Стек пуст!"
                
                yield {
                    "type": "peek",
                    "value": result,
                    "stack": list(self.stack),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "size":
                size = len(self.stack)
                description = f"📊 Размер стека: {size}"
                
                yield {
                    "type": "size",
                    "size": size,
                    "stack": list(self.stack),
                    "description": description,
                    "step": self.step_count
                }
                
            elif operation == "is_empty":
                is_empty = len(self.stack) == 0
                status = "пуст" if is_empty else "не пуст"
                description = f"📋 Стек {status}"
                
                yield {
                    "type": "is_empty",
                    "empty": is_empty,
                    "stack": list(self.stack),
                    "description": description,
                    "step": self.step_count
                }
        
        # Завершающий шаг
        yield {
            "type": "complete",
            "stack": list(self.stack),
            "size": len(self.stack),
            "description": "✅ Все операции со стеком выполнены",
            "step": self.step_count
        }
    
    def push(self, value):
        """Добавить элемент в стек (O(1))"""
        if len(self.stack) < self.max_size:
            self.stack.append(value)
            return True
        return False
    
    def pop(self):
        """Извлечь элемент из стека (O(1))"""
        if self.stack:
            return self.stack.pop()
        return None
    
    def peek(self):
        """Посмотреть верхний элемент стека (O(1))"""
        if self.stack:
            return self.stack[-1]
        return None
    
    def size(self):
        """Получить размер стека (O(1))"""
        return len(self.stack)
    
    def is_empty(self):
        """Проверить, пуст ли стек (O(1))"""
        return len(self.stack) == 0
    
    def clear(self):
        """Очистить стек"""
        self.stack.clear()
    
    def __str__(self):
        return f"Stack({self.stack})"