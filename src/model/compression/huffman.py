# model/compression/huffman.py
import heapq
from collections import Counter
from typing import Dict, Tuple, List, Optional, Any

class HuffmanNode:
    """Узел дерева Хаффмана."""
    
    def __init__(self, symbol=None, frequency=None):
        self.symbol = symbol
        self.frequency = frequency
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.frequency < other.frequency
    
    def is_leaf(self):
        return self.symbol is not None
    
    def get_tree_structure(self):
        """Возвращает структуру дерева для визуализации (итеративно)."""
        if self is None:
            return {}
        
        # Итеративный обход дерева
        stack = [(self, None, "root")]
        result = {}
        node_map = {}
        
        while stack:
            node, parent, direction = stack.pop()
            
            # Создаем узел
            node_id = id(node)
            node_data = {
                "value": f"'{node.symbol}'" if node.symbol else f"{node.frequency}",
                "frequency": node.frequency,
                "is_leaf": node.is_leaf(),
                "symbol": node.symbol if node.symbol else None
            }
            node_map[node_id] = node_data
            
            # Связываем с родителем
            if parent is not None:
                parent_data = node_map[id(parent)]
                if direction == "left":
                    parent_data["left"] = node_data
                else:
                    parent_data["right"] = node_data
            
            # Добавляем потомков в стек
            if node.right:
                stack.append((node.right, node, "right"))
            if node.left:
                stack.append((node.left, node, "left"))
        
        return node_map[id(self)] if node_map else {}
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "frequency": self.frequency,
            "is_leaf": self.is_leaf()
        }


class HuffmanCoding:
    """Алгоритм кодирования Хаффмана с безопасной визуализацией."""
    
    def __init__(self, text: str = ""):
        self.text = text
        self.original_text = text
        self.root = None
        self.codes = {}
        self.reverse_codes = {}
        self.frequencies = {}
        self.encoded_text = ""
        self.decoded_text = ""
        self.compression_ratio = 0
        self.savings_percentage = 0
        self.history = []
        self.current_step = 0
    
    def calculate_frequencies(self) -> Dict[str, int]:
        """Вычисляет частоты символов в тексте."""
        self.frequencies = Counter(self.text)
        return dict(self.frequencies)
    
    def build_huffman_tree(self):
        """Строит дерево Хаффмана (безопасная версия)."""
        # Сбрасываем историю
        self.history = []
        
        if not self.frequencies:
            self.calculate_frequencies()
        
        if not self.frequencies:
            self.history.append({
                "type": "error",
                "description": "❌ Нет данных для построения дерева"
            })
            return None
        
        # Создаем начальные узлы
        nodes = [HuffmanNode(char, freq) for char, freq in self.frequencies.items()]
        heapq.heapify(nodes)
        
        # Запоминаем начальное состояние
        self.history.append({
            "type": "initial_nodes",
            "nodes": [n.to_dict() for n in nodes],
            "description": f"🎲 Созданы узлы: {len(nodes)} символов"
        })
        
        step = 1
        max_steps = len(nodes) * 2  # Защита от бесконечного цикла
        
        # Строим дерево
        while len(nodes) > 1 and step <= max_steps:
            # Извлекаем два минимальных узла
            left = heapq.heappop(nodes)
            right = heapq.heappop(nodes)
            
            self.history.append({
                "type": "nodes_selected",
                "step": step,
                "left_node": left.to_dict(),
                "right_node": right.to_dict(),
                "description": f"🔍 Шаг {step}: Узлы {left.frequency} и {right.frequency}"
            })
            
            # Создаем новый узел
            merged_freq = left.frequency + right.frequency
            merged_node = HuffmanNode(frequency=merged_freq)
            merged_node.left = left
            merged_node.right = right
            
            self.history.append({
                "type": "nodes_merged",
                "step": step,
                "merged_frequency": merged_freq,
                "description": f"➕ Шаг {step}: {left.frequency} + {right.frequency} = {merged_freq}"
            })
            
            # Добавляем в кучу
            heapq.heappush(nodes, merged_node)
            
            self.history.append({
                "type": "heap_updated",
                "step": step,
                "heap_size": len(nodes),
                "description": f"📊 Шаг {step}: Узлов в куче: {len(nodes)}"
            })
            
            step += 1
        
        # Сохраняем корень
        self.root = nodes[0] if nodes else None
        
        if self.root:
            self.history.append({
                "type": "tree_built",
                "root_frequency": self.root.frequency,
                "description": f"🌳 Дерево построено! Корень: {self.root.frequency}"
            })
        
        return self.root
    
    def generate_huffman_codes_iterative(self):
        """Генерирует коды Хаффмана итеративно (безопасно)."""
        if not self.root:
            return {}
        
        self.codes = {}
        self.reverse_codes = {}
        
        self.history.append({
            "type": "code_generation_start",
            "description": "🔤 Начало генерации кодов"
        })
        
        # Используем стек вместо рекурсии
        stack = [(self.root, "")]
        step = 0
        
        while stack:
            node, code = stack.pop()
            
            if node.is_leaf():
                self.codes[node.symbol] = code
                self.reverse_codes[code] = node.symbol
                
                self.history.append({
                    "type": "code_assigned",
                    "step": step,
                    "symbol": node.symbol,
                    "code": code,
                    "frequency": node.frequency,
                    "description": f"📝 '{self._format_char(node.symbol)}' → '{code}'"
                })
                step += 1
            
            # Добавляем потомков в стек (сначала правый, потом левый)
            if node.right:
                stack.append((node.right, code + "1"))
            if node.left:
                stack.append((node.left, code + "0"))
        
        self.history.append({
            "type": "codes_generated",
            "codes_count": len(self.codes),
            "description": f"✅ Коды сгенерированы! Всего: {len(self.codes)}"
        })
        
        return self.codes
    
    def generate_huffman_codes_recursive(self, node=None, code=""):
        """Рекурсивная версия (для тестирования)."""
        if node is None:
            node = self.root
        
        self.codes = {}
        self.reverse_codes = {}
        
        def _recursive_helper(node, current_code):
            if node is None:
                return
            
            if node.is_leaf():
                self.codes[node.symbol] = current_code
                self.reverse_codes[current_code] = node.symbol
                return
            
            _recursive_helper(node.left, current_code + "0")
            _recursive_helper(node.right, current_code + "1")
        
        _recursive_helper(node, "")
        return self.codes
    
    def encode_text(self, text=None) -> str:
        """Кодирует текст."""
        if text is not None:
            self.text = text
            self.original_text = text
        
        if not self.codes:
            self.generate_huffman_codes_iterative()
        
        # Кодируем
        encoded_bits = []
        for char in self.text:
            if char in self.codes:
                encoded_bits.append(self.codes[char])
            else:
                encoded_bits.append("")
        
        self.encoded_text = ''.join(encoded_bits)
        
        # Статистика
        original_bits = len(self.text) * 8
        compressed_bits = len(self.encoded_text)
        
        if original_bits > 0:
            self.compression_ratio = original_bits / compressed_bits
            self.savings_percentage = ((original_bits - compressed_bits) / original_bits) * 100
        
        self.history.append({
            "type": "encoding_complete",
            "original_bits": original_bits,
            "compressed_bits": compressed_bits,
            "compression_ratio": self.compression_ratio,
            "savings_percentage": self.savings_percentage,
            "description": f"✅ Текст закодирован! Экономия: {self.savings_percentage:.1f}%"
        })
        
        return self.encoded_text
    
    def decode_text(self, encoded_text: str = None) -> str:
        """Декодирует текст."""
        if encoded_text is not None:
            self.encoded_text = encoded_text
        
        if not self.reverse_codes:
            self.generate_huffman_codes_iterative()
        
        decoded_chars = []
        current_code = ""
        
        for bit in self.encoded_text:
            current_code += bit
            if current_code in self.reverse_codes:
                decoded_chars.append(self.reverse_codes[current_code])
                current_code = ""
        
        self.decoded_text = ''.join(decoded_chars)
        
        self.history.append({
            "type": "decoding_complete",
            "is_correct": self.decoded_text == self.original_text,
            "description": f"✅ Текст декодирован!"
        })
        
        return self.decoded_text
    
    def get_compression_stats(self):
        """Возвращает статистику сжатия."""
        return {
            "original_text": self.original_text,
            "encoded_text": self.encoded_text,
            "original_size_bits": len(self.original_text) * 8,
            "compressed_size_bits": len(self.encoded_text),
            "compression_ratio": self.compression_ratio,
            "savings_percentage": self.savings_percentage,
            "unique_symbols": len(self.frequencies),
            "codes": self.codes,
            "frequencies": self.frequencies
        }
    
    def get_tree_structure(self):
        """Безопасное получение структуры дерева."""
        if not self.root:
            return {}
        
        try:
            return self.root.get_tree_structure()
        except RecursionError:
            # Возвращаем упрощенную структуру
            return {
                "value": f"Корень: {self.root.frequency}",
                "frequency": self.root.frequency,
                "is_leaf": False,
                "symbol": None,
                "warning": "Дерево слишком глубокое для полной визуализации"
            }
    
    def get_codes_table(self):
        """Возвращает таблицу кодов."""
        table = []
        for symbol, code in sorted(self.codes.items(), key=lambda x: (len(x[1]), x[1])):
            table.append({
                "symbol": symbol,
                "code": code,
                "frequency": self.frequencies.get(symbol, 0),
                "original_bits": 8,
                "compressed_bits": len(code),
                "savings": 8 - len(code)
            })
        return table
    
    def step(self):
        """Шаг алгоритма."""
        if self.current_step < len(self.history):
            action = self.history[self.current_step]
            self.current_step += 1
            return action
        return {"type": "complete", "description": "✅ Алгоритм завершен!"}
    
    def reset(self):
        """Сбрасывает состояние."""
        self.current_step = 0
        self.history = []
        self.codes = {}
        self.reverse_codes = {}
        self.encoded_text = ""
        self.decoded_text = ""
        self.root = None
    
    def process_text(self, text: str):
        """Обрабатывает текст полностью (безопасно)."""
        try:
            self.text = text
            self.original_text = text
            
            self.reset()
            
            # 1. Частоты
            self.calculate_frequencies()
            
            # 2. Дерево
            self.build_huffman_tree()
            
            # 3. Коды (итеративно)
            self.generate_huffman_codes_iterative()
            
            # 4. Кодирование
            self.encode_text()
            
            # 5. Декодирование
            self.decode_text()
            
            return self.get_compression_stats()
            
        except Exception as e:
            self.history.append({
                "type": "error",
                "description": f"❌ Ошибка: {str(e)}"
            })
            return None
    
    def _format_char(self, char):
        """Форматирует символ."""
        if char == " ":
            return "[space]"
        elif char == "\n":
            return "\\n"
        elif char == "\t":
            return "\\t"
        elif char == "\r":
            return "\\r"
        elif ord(char) < 32:
            return f"\\x{ord(char):02x}"
        return char


# Примеры текстов (без изменений)
def create_example_texts():
    return [
        {
            "name": "Пример из кода",
            "text": "aaabbbbbbbcccccccccccccccdddddddddddddddddeeeeeeeeeeeeeeeeeeeeeeffffffffffffffffffffffffffffffffffffffffff",
            "description": "Текст с частотами [4, 7, 15, 17, 22, 42]"
        },
        {
            "name": "Английский текст",
            "text": "hello world",
            "description": "Простой текст для тестирования"
        },
        {
            "name": "Русский текст",
            "text": "привет мир",
            "description": "Русский текст"
        },
        {
            "name": "Короткий пример",
            "text": "ABRACADABRA",
            "description": "Классический пример"
        },
        {
            "name": "Очень короткий",
            "text": "aaaabbbccd",
            "description": "Минимальный пример"
        }
    ]