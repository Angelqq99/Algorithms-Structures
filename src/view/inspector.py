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
                parsed = json.loads(info)
            else:
                parsed = info
            
            # Добавляем человеко-читаемое описание
            enhanced_info = self._enhance_with_description(parsed)
            
            # Форматируем JSON
            formatted_info = json.dumps(enhanced_info, indent=2, ensure_ascii=False)
            self.setPlainText(formatted_info)
        except:
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
            
        elif action_type == "complete":
            description = "✅ Алгоритм завершен"
            
        elif action_type == "collision":
            description = "⚡ Обнаружена коллизия в хэш-таблице"
            
        elif action_type == "insert":
            description = "📥 Вставка нового элемента"
        
        # Добавляем описание в данные
        if description:
            enhanced_data = data.copy()
            enhanced_data['_description'] = description
            return enhanced_data
        
        return data