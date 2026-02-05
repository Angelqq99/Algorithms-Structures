# model/compression/huffman.py
import heapq
from collections import Counter
from typing import Dict, List, Any


class HuffmanNode:
    """Узел дерева Хаффмана."""
    
    def __init__(self, symbol=None, frequency=None):
        self.symbol = symbol
        self.frequency = frequency
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        if self.frequency == other.frequency:
            # Сравниваем символы, если частоты равны. 
            # У промежуточных узлов symbol=None, поэтому используем пустую строку.
            return (self.symbol or "") < (other.symbol or "")
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
        
        # Для пошагового выполнения
        self._step_generator = None
        self.current_phase = "initial"
    
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
            # Спец-случай: в тексте только один уникальный символ
        if self.root.is_leaf():
            self.codes[self.root.symbol] = "0"
            self.reverse_codes["0"] = self.root.symbol
            return self.codes
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
    
    def encode_text(self):
        """Кодирует текст с использованием построенного дерева Хаффмана."""
        if not self.root:
            raise ValueError("Дерево Хаффмана не построено")
        
        if not self.codes:
            self.generate_huffman_codes_iterative()
                
        encoded_text = ""
        
        for char in self.text:
            if char in self.codes:
                encoded_text += self.codes[char]
            else:
                # Если символ не найден в кодах (не должен происходить при корректной работе)
                raise ValueError(f"Символ '{char}' не найден в таблице кодов")
        
        # Расчет статистики сжатия
        original_bits = len(self.text.encode('utf-8')) * 8  # ASCII предполагает 8 бит на символ
        compressed_bits = len(encoded_text)
        
        # Защита от деления на ноль
        if compressed_bits == 0:
            self.compression_ratio = 0
            self.savings_percentage = 0
        else:
            self.compression_ratio = original_bits / compressed_bits
            self.savings_percentage = ((original_bits - compressed_bits) / original_bits) * 100
        
        self.compressed_size_bits = compressed_bits
        self.encoded_text = encoded_text
        
        return encoded_text
    
    def decode_text(self, encoded_text: str = None) -> str:
        """
        Декодирует бинарную строку обратно в текст с детальной диагностикой.
        """
        if encoded_text is not None:
            self.encoded_text = encoded_text
        
        if not self.encoded_text:
            return ""
        
        if not self.root:
            raise ValueError("Дерево Хаффмана не построено")
        
        # Упрощенная диагностика без emoji для Windows
        diagnostics = {
            "total_bits": len(self.encoded_text),
            "decoded_symbols": 0,
            "errors": [],
            "warnings": []
        }
        
        # Специальный случай: один символ
        if self.root.is_leaf():
            expected_symbol = self.root.symbol
            # Для дерева с одним символом просто возвращаем символы по количеству бит
            if expected_symbol is not None:
                # Каждый символ кодируется одним битом в этом случае
                result = expected_symbol * len(self.encoded_text)
                self.decoded_text = result
                diagnostics["decoded_symbols"] = len(result)
                diagnostics["warnings"].append(
                    "Специальный случай: дерево содержит только один символ"
                )
                return self.decoded_text
            else:
                raise ValueError("Корневой узел не содержит символа")
        
        # Стандартное декодирование
        decoded_chars = []
        current_node = self.root
        
        for i, bit in enumerate(self.encoded_text):
            try:
                # Проверяем корректность бита
                if bit not in ('0', '1'):
                    error_msg = f"Некорректный бит на позиции {i}: '{bit}' (должен быть 0 или 1)"
                    diagnostics["errors"].append(error_msg)
                    # Пытаемся пропустить некорректный бит и продолжить
                    continue
                
                # Переходим по дереву
                if bit == '0':
                    if not current_node.left:
                        error_msg = f"Нет левого узла при переходе по '0'"
                        diagnostics["errors"].append(error_msg)
                        # Возвращаемся к корню и пробуем продолжить
                        current_node = self.root
                        continue
                    current_node = current_node.left
                else:  # bit == '1'
                    if not current_node.right:
                        error_msg = f"Нет правого узла при переходе по '1'"
                        diagnostics["errors"].append(error_msg)
                        current_node = self.root
                        continue
                    current_node = current_node.right
                
                # Если достигли листа
                if current_node.is_leaf():
                    decoded_symbol = current_node.symbol
                    decoded_chars.append(decoded_symbol)
                    diagnostics["decoded_symbols"] += 1
                    
                    # Сбрасываем для следующего символа
                    current_node = self.root
                    
            except Exception as e:
                # Логируем ошибку, но продолжаем декодирование
                error_info = f"Ошибка на бите {i}: {str(e)}"
                diagnostics["errors"].append(error_info)
                current_node = self.root  # Сбрасываем на корень
        
        # Формируем результат
        self.decoded_text = "".join(decoded_chars)
        
        # Сохраняем диагностику
        self.last_diagnostics = diagnostics
        
        # Простая логировка диагностики
        if diagnostics["errors"]:
            print(f"Ошибки декодирования: {len(diagnostics['errors'])}")
        if diagnostics["warnings"]:
            print(f"Предупреждения: {len(diagnostics['warnings'])}")
        
        return self.decoded_text

    def _log_diagnostics(self, diagnostics):
        """
        Логирует диагностическую информацию.
        
        Args:
            diagnostics: Словарь с диагностической информацией
        """
        # Сохраняем диагностику для доступа извне
        self.last_diagnostics = diagnostics
        
        print("\n" + "="*60)
        print(" ДИАГНОСТИКА ДЕКОДИРОВАНИЯ")
        print("="*60)
        
        print(f"• Всего бит: {diagnostics['total_bits']}")
        print(f"• Декодировано символов: {diagnostics['decoded_symbols']}")
        
        if diagnostics["path_trace"]:
            print(f"\n📝 Путь декодирования (первые 10 символов):")
            for i, trace in enumerate(diagnostics["path_trace"][:10]):
                symbol_display = self._format_char(trace["symbol"])
                print(f"  {i+1:3d}. Бит(ы): {trace['bits']:10s} → '{symbol_display}' "
                    f"(частота: {trace['frequency']})")
            
            if len(diagnostics["path_trace"]) > 10:
                print(f"  ... и еще {len(diagnostics['path_trace']) - 10} символов")
        
        if diagnostics["warnings"]:
            print(f"\n⚠️ Предупреждения:")
            for warning in diagnostics["warnings"]:
                print(f"  • {warning}")
        
        if diagnostics["errors"]:
            print(f"\n❌ Ошибки:")
            for error in diagnostics["errors"]:
                print(f"  • {error}")
        
        print("="*60)
    
    def get_decoding_diagnostics(self):
        """
        Возвращает диагностическую информацию о последнем декодировании.
        """
        return getattr(self, 'last_diagnostics', {
            "total_bits": 0,
            "decoded_symbols": 0,
            "errors": [],
            "warnings": []
        })
    
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
        """Безопасное форматирование символа."""
        if not char:
            return ""
        
        # Если char это строка, берем первый символ
        if isinstance(char, str) and len(char) > 0:
            char_code = char[0]
        else:
            char_code = char
        
        # Проверяем, является ли символ печатным
        try:
            # Попытка закодировать в ASCII (безопасно для Windows)
            char_str = str(char_code)
            if char_str.isprintable():
                return char_str
            else:
                # Непечатаемые символы заменяем на hex
                return f"\\x{ord(char_str):02x}"
        except:
            return "?"
    
    def create_step_generator(self):
        """Создает генератор для пошагового выполнения алгоритма."""
        try:
            # Фаза 1: Расчет частот
            self.calculate_frequencies()
            yield {
                "type": "frequencies_calculated",
                "frequencies": self.frequencies,
                "description": f"📊 Частоты символов рассчитаны: {len(self.frequencies)} уникальных символов"
            }
            
            # Фаза 2: Построение дерева
            self.build_huffman_tree()
            
            # Эмулируем шаги построения дерева из истории
            for step_data in self.history:
                if step_data["type"] in ["initial_nodes", "nodes_selected", "nodes_merged", "heap_updated", "tree_built"]:
                    yield step_data
            
            # Фаза 3: Генерация кодов
            self.generate_huffman_codes_iterative()
            
            # Эмулируем шаги генерации кодов из истории
            for step_data in self.history:
                if step_data["type"] in ["code_generation_start", "code_assigned", "codes_generated"]:
                    yield step_data
            
            # Фаза 4: Кодирование текста
            encoded_text = self.encode_text()
            
            yield {
                "type": "encoding_complete",
                "encoded_text": encoded_text,
                "original_bits": len(self.original_text) * 8,
                "compressed_bits": len(encoded_text),
                "compression_ratio": self.compression_ratio,
                "savings_percentage": self.savings_percentage,
                "description": f"✅ Текст закодирован! Коэффициент сжатия: {self.compression_ratio:.2f}:1"
            }
            
            # Фаза 5: Декодирование
            decoded_text = self.decode_text()
            
            yield {
                "type": "decoding_complete",
                "decoded_text": decoded_text,
                "is_correct": decoded_text == self.original_text,
                "description": f"✅ Текст успешно декодирован! Совпадение с оригиналом: {decoded_text == self.original_text}"
            }
            
            # Фаза 6: Завершение
            yield {
                "type": "complete",
                "description": "✅ Алгоритм Хаффмана выполнен полностью!",
                "stats": self.get_compression_stats()
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "description": f"❌ Ошибка: {str(e)}"
            }
    
    def step_generator(self):
        """Генератор для пошагового выполнения алгоритма (устаревший метод, для совместимости)."""
        return self.create_step_generator()
    
    def get_step_generator(self):
        """Возвращает генератор для пошагового выполнения."""
        if self._step_generator is None:
            self._step_generator = self.create_step_generator()
        return self._step_generator
    
    def step(self):
        """Выполняет один шаг алгоритма."""
        if self._step_generator is None:
            self._step_generator = self.create_step_generator()
        
        try:
            return next(self._step_generator)
        except StopIteration:
            return {
                "type": "complete",
                "description": "✅ Алгоритм завершен!",
                "stats": self.get_compression_stats()
            }
        except Exception as e:
            return {
                "type": "error",
                "description": f"❌ Ошибка при выполнении шага: {str(e)}"
            }
    
    def reset(self):
        """Сбрасывает состояние."""
        self.current_step = 0
        self.history = []
        self.codes = {}
        self.reverse_codes = {}
        self.encoded_text = ""
        self.decoded_text = ""
        self.root = None
        self._step_generator = None
        self.current_phase = "initial"


# Примеры текстов
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


