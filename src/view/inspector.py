from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
import json


class JSONHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        
        # Форматы для разных типов данных JSON
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#D32F2F"))
        self.key_format.setFontWeight(QFont.Weight.Bold)
        
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#388E3C"))
        
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#1976D2"))
        
        self.bool_format = QTextCharFormat()
        self.bool_format.setForeground(QColor("#7B1FA2"))
        
        self.null_format = QTextCharFormat()
        self.null_format.setForeground(QColor("#F57C00"))
        
        self.special_format = QTextCharFormat()
        self.special_format.setForeground(QColor("#FF8C00"))
        self.special_format.setFontWeight(QFont.Weight.Bold)

    def highlightBlock(self, text):
        import re
        
        # JSON ключи
        pattern = r'\"(\w+)\"\s*:'
        for match in re.finditer(pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.key_format)
        
        # Строковые значения
        pattern = r':\s*\"([^\"]*)\"'
        for match in re.finditer(pattern, text):
            self.setFormat(match.start() + 2, match.end() - match.start() - 2, self.string_format)
        
        # Числовые значения
        pattern = r':\s*(\d+)'
        for match in re.finditer(pattern, text):
            self.setFormat(match.start() + 1, match.end() - match.start() - 1, self.number_format)
        
        # Булевы значения
        pattern = r':\s*(true|false)'
        for match in re.finditer(pattern, text):
            self.setFormat(match.start() + 1, match.end() - match.start() - 1, self.bool_format)
        
        # Null значения
        pattern = r':\s*(null)'
        for match in re.finditer(pattern, text):
            self.setFormat(match.start() + 1, match.end() - match.start() - 1, self.null_format)
        
        # Специальные ключи для хэш-таблицы
        special_keys = ['hash_function', 'collision_method', 'table_size', 'load_factor', 
                       'collisions', 'max_chain_length', 'probing_steps']
        for key in special_keys:
            pattern = f'\"{key}\"'
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), self.special_format)


class Inspector(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setMaximumHeight(180)
        self.setReadOnly(True)
        self.setPlaceholderText("Информация о текущем состоянии алгоритма...")
        self.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
            }
        """)
        
        # Установка подсветки синтаксиса JSON
        self.highlighter = JSONHighlighter(self.document())
        
    def update_info(self, info):
        """Обновление информации с красивым форматированием."""
        try:
            # Если info уже строка, пытаемся распарсить как JSON
            if isinstance(info, str):
                try:
                    parsed = json.loads(info)
                except:
                    parsed = {"raw": info}
            else:
                parsed = info
            
            # Добавляем человеко-читаемое описание
            enhanced_info = self._enhance_with_description(parsed)
            
            # Форматируем JSON
            formatted_info = json.dumps(enhanced_info, indent=2, ensure_ascii=False)
            self.setPlainText(formatted_info)
        except Exception as e:
            # Если не JSON, отображаем как есть
            self.setPlainText(str(info))
    
    def _enhance_with_description(self, data):
        """Добавляет человеко-читаемое описание к данным."""
        if not isinstance(data, dict):
            return data
            
        action_type = data.get('type', '')
        description = ""
        
        if action_type == "graph_init":
            graph_data = data.get('graph', {})
            start_node = data.get('start_node', '')
            description = f"Инициализация графа. Начальный узел: {start_node}. Всего узлов: {len(graph_data)}"
            
        elif action_type == "visit":
            node = data.get('node', '')
            description = f"Посещение узла: {node}"
            
        elif action_type == "discover":
            from_node = data.get('from_node', '')
            to_node = data.get('node', '')
            description = f"Обнаружение связи: узел {from_node} → узел {to_node}"
            
        elif action_type == "update_distance":
            node = data.get('node', '')
            new_distance = data.get('new_distance', '')
            old_distance = data.get('old_distance', 'неизвестно')
            description = f"Обновление расстояния до узла {node}: {old_distance} → {new_distance}"
            
        elif action_type == "compare":
            indices = data.get('indices', [])
            if len(indices) == 2:
                description = f"Сравнение элементов: индекс {indices[0]} и индекс {indices[1]}"
            
        elif action_type == "swap":
            indices = data.get('indices', [])
            if len(indices) == 2:
                description = f"Обмен элементов: индекс {indices[0]} и индекс {indices[1]}"
            
        elif action_type == "tree":
            description = "Обновление структуры дерева"
            
        elif action_type == "traversal":
            nodes = data.get('nodes', [])
            description = f"Обход дерева: {len(nodes)} узлов"
            
        elif action_type == "info" and "hash_index" in data:
            key = data.get('key', '')
            hash_idx = data.get('hash_index', '')
            description = f"Вычисление хэша: ключ {key} → индекс {hash_idx}"
            
        elif action_type == "collision" and "chain_length" in data:
            key = data.get('key', '')
            idx = data.get('index', '')
            chain_length = data.get('chain_length', 0)
            description = f"Коллизия: ключ {key} в индекс {idx} (цепочка: {chain_length} элементов)"
            
        elif action_type == "collision":
            key = data.get('key', '')
            idx = data.get('index', '')
            occupied_key = data.get('occupied_key', '')
            description = f"Коллизия: ключ {key} в занятый индекс {idx} (занят {occupied_key})"
            
        elif action_type == "probing_step":
            step = data.get('step', 0)
            idx = data.get('index', '')
            key = data.get('key', '')
            description = f"Пробирование: шаг {step}, индекс {idx}, ключ {key}"
            
        elif action_type == "duplicate":
            key = data.get('key', '')
            idx = data.get('index', '')
            description = f"Дубликат: ключ {key} уже существует в индексе {idx}"
            
        elif action_type == "insert" and "table" in data:
            key = data.get('key', '')
            idx = data.get('index', '')
            probed_idx = data.get('probed_index')
            probing_steps = data.get('probing_steps_count', 0)
            
            if probed_idx is not None and probed_idx != idx:
                description = f"Вставка: ключ {key} в индекс {probed_idx} (изначально {idx}, шагов: {probing_steps})"
            else:
                description = f"Вставка: ключ {key} в индекс {idx}"
            
        elif action_type == "complete" and "hash_function" in data:
            collisions = data.get('collisions', 0)
            load_factor = data.get('load_factor', 0)
            table_size = data.get('table_size', 0)
            description = f"✅ Хэш-таблица построена! Коллизий: {collisions}, Заполнение: {load_factor:.2f}"
            
        # Операции со стеком, очередью и деком
        elif action_type == "push":
            description = f"📥 В стек добавлен элемент: {data.get('value')}"
        elif action_type == "pop":
            value = data.get('value', '')
            description = f"📤 Из стека извлечен элемент: {value}" if value else "📤 Попытка извлечь из пустого стека"
        elif action_type == "peek":
            value = data.get('value', '')
            description = f"👁 Верхний элемент стека: {value}" if value else "👁 Стек пуст"
        elif action_type == "enqueue":
            description = f"📥 В очередь добавлен элемент: {data.get('value')}"
        elif action_type == "dequeue":
            value = data.get('value', '')
            description = f"📤 Из очереди извлечен элемент: {value}" if value else "📤 Очередь пуста"
        elif action_type == "front":
            value = data.get('value', '')
            description = f"👁 Передний элемент очереди: {value}" if value else "👁 Очередь пуста"
        elif action_type == "back":
            value = data.get('value', '')
            description = f"👁 Задний элемент очереди: {value}" if value else "👁 Очередь пуста"
        elif action_type == "push_front":
            description = f"⬅️ В начало дека добавлен элемент: {data.get('value')}"
        elif action_type == "push_back":
            description = f"➡️ В конец дека добавлен элемент: {data.get('value')}"
        elif action_type == "pop_front":
            value = data.get('value', '')
            description = f"⬅️ Из начала дека извлечен элемент: {value}" if value else "⬅️ Дек пуст"
        elif action_type == "pop_back":
            value = data.get('value', '')
            description = f"➡️ Из конца дека извлечен элемент: {value}" if value else "➡️ Дек пуст"
        elif action_type == "size":
            size = data.get('size', 0)
            description = f"📊 Размер контейнера: {size}"
        elif action_type == "is_empty":
            is_empty = data.get('empty', True)
            status = "пуст" if is_empty else "не пуст"
            description = f"📋 Контейнер {status}"
            
        elif action_type == "complete":
            description = "✅ Алгоритм успешно завершён!"
            
        # Добавляем описание в данные
        if description:
            enhanced_data = data.copy()
            enhanced_data['_description'] = description
            return enhanced_data
        
        return data