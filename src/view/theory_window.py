"""
Окно для отображения теории алгоритмов и структур данных
"""

import os
import json
import math
from html import escape
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QListWidget, QSplitter, QPushButton, QLabel, QTabWidget, 
    QScrollArea, QFrame, QTreeWidget, QTreeWidgetItem, QStackedWidget,
    QGroupBox, QTextEdit, QSizePolicy, QMessageBox, QLineEdit,
    QPlainTextEdit, QApplication
)
from PyQt6.QtCore import Qt, QSize, QUrl, QRegularExpression, QRect
from PyQt6.QtGui import (
    QFont, QColor, QTextCursor, QDesktopServices, QTextDocument, 
    QAction, QTextCharFormat, QBrush, QPalette, QSyntaxHighlighter,
    QPainter, QTextFormat, QFontDatabase, QTextOption
)


class CodeHighlighter(QSyntaxHighlighter):
    """Подсветка синтаксиса для псевдокода"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Ключевые слова (зеленый)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#007ACC"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "function", "procedure", "return", "if", "else", "endif", "then",
            "for", "while", "do", "end", "repeat", "until", "foreach", "in",
            "switch", "case", "default", "break", "continue", "true", "false",
            "null", "nil", "and", "or", "not", "var", "let", "const"
        ]
        
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            rule = (pattern, keyword_format)
            self.highlighting_rules.append(rule)
        
        # Строки (оранжевый)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#A31515"))
        pattern = QRegularExpression("\".*\"")
        rule = (pattern, string_format)
        self.highlighting_rules.append(rule)
        
        # Комментарии (серый)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#008000"))
        comment_format.setFontItalic(True)
        pattern = QRegularExpression("#[^\n]*")
        rule = (pattern, comment_format)
        self.highlighting_rules.append(rule)
        
        pattern = QRegularExpression("//[^\n]*")
        rule = (pattern, comment_format)
        self.highlighting_rules.append(rule)
        
        # Функции (фиолетовый)
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#795E26"))
        pattern = QRegularExpression("\\b[A-Za-z0-9_]+(?=\\()")
        rule = (pattern, function_format)
        self.highlighting_rules.append(rule)
        
        # Числа (темно-синий)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#098658"))
        pattern = QRegularExpression("\\b\\d+\\b")
        rule = (pattern, number_format)
        self.highlighting_rules.append(rule)
    
    def highlightBlock(self, text):
        """Подсветка блока текста"""
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class LineNumberArea(QWidget):
    """Область для отображения номеров строк"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
    
    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Продвинутый редактор кода с номерами строк"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        
        # Настройка внешнего вида
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 5px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
                selection-background-color: #264F78;
            }
        """)
        
        # Настройка шрифта
        font = QFont("Consolas", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Подсветка синтаксиса
        self.highlighter = CodeHighlighter(self.document())
        
        # Соединяем сигналы
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.update_line_number_area_width(0)
        self.highlight_current_line()
    
    def line_number_area_width(self):
        """Вычисляет ширину области номеров строк"""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, _):
        """Обновляет отступы для области номеров строк"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """Обновляет область номеров строк"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                        self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """Обработчик изменения размера"""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            cr.left(), cr.top(),
            self.line_number_area_width(), cr.height()
        )
    
    def line_number_area_paint_event(self, event):
        """Отрисовка номеров строк"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#2D2D30"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(
            self.contentOffset()).top())
        bottom = int(top + self.blockBoundingRect(block).height())
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                
                # Исправленный вызов drawText с целыми числами
                painter.drawText(
                    0,  # x
                    top,  # y (теперь int)
                    self.line_number_area.width() - 5,  # width
                    self.fontMetrics().height(),  # height
                    Qt.AlignmentFlag.AlignRight,  # flags
                    number  # text
                )
            
            block = block.next()
            top = bottom
            bottom = int(top + self.blockBoundingRect(block).height())
            block_number += 1
    
    def highlight_current_line(self):
        """Подсветка текущей строки"""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            
            line_color = QColor("#2D2D30")
            line_color.setAlpha(100)
            
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def setReadOnly(self, read_only):
        """Установка режима только для чтения"""
        super().setReadOnly(read_only)
        if not read_only:
            self.highlight_current_line()


class TheoryWindow(QMainWindow):
    """Главное окно теории алгоритмов"""
    
    def __init__(self, theory_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📚 Теория алгоритмов и структур данных")
        self.setGeometry(200, 200, 1400, 900)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f4f9;
            }
        """)
        
        # Сохраняем загруженные данные теории
        self.theory_data = theory_data
        
        # Настройка интерфейса
        self._setup_ui()
        
        # Выбираем первую категорию по умолчанию
        if self.category_tree.topLevelItemCount() > 0:
            self.category_tree.setCurrentItem(self.category_tree.topLevelItem(0))
        
        # Создаем меню
        self._create_menu()
    
    def _create_menu(self):
        """Создает меню окна"""
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)      
        
        # Меню Вид
        view_menu = menubar.addMenu("Вид")
        
        zoom_in_action = QAction("Увеличить", self)
        zoom_in_action.triggered.connect(self._zoom_in)
        zoom_in_action.setShortcut("Ctrl++")
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Уменьшить", self)
        zoom_out_action.triggered.connect(self._zoom_out)
        zoom_out_action.setShortcut("Ctrl+-")
        view_menu.addAction(zoom_out_action)
        
        # Меню Справка
        help_menu = menubar.addMenu("Справка")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _zoom_in(self):
        """Увеличивает текст"""
        for widget in [self.general_text, self.math_text, 
                      self.links_text]:
            current_font = widget.font()
            current_font.setPointSize(current_font.pointSize() + 1)
            widget.setFont(current_font)
        
        # Для редактора кода
        current_font = self.code_editor.font()
        current_font.setPointSize(current_font.pointSize() + 1)
        self.code_editor.setFont(current_font)
        self.example_editor.setFont(current_font)
    
    def _zoom_out(self):
        """Уменьшает текст"""
        for widget in [self.general_text, self.math_text, 
                      self.links_text]:
            current_font = widget.font()
            if current_font.pointSize() > 8:
                current_font.setPointSize(current_font.pointSize() - 1)
                widget.setFont(current_font)
        
        # Для редактора кода
        current_font = self.code_editor.font()
        if current_font.pointSize() > 8:
            current_font.setPointSize(current_font.pointSize() - 1)
            self.code_editor.setFont(current_font)
            self.example_editor.setFont(current_font)
    
    def _show_about(self):
        """Показывает информацию о программе"""
        QMessageBox.about(
            self,
            "О программе",
            "<h2>Теория алгоритмов и структур данных</h2>"
            "<p>Программа для изучения алгоритмов и структур данных.</p>"
            "<p>Версия 1.0</p>"
            "<p>© 2024 Все права защищены.</p>"
        )
    
    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Заголовок
        title = QLabel("📚 ТЕОРИЯ АЛГОРИТМОВ И СТРУКТУР ДАННЫХ")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                background-color: #e8f4fd;
                border-radius: 8px;
                border: 2px solid #5A9BD5;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Основной разделитель
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель: навигация
        left_panel = self._create_navigation_panel()
        
        # Правая панель: содержимое
        right_panel = self._create_content_panel()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 1050])
        
        layout.addWidget(splitter, 1)
        
    
    def _create_navigation_panel(self):
        """Создает панель навигации с деревом категорий"""
        panel = QWidget()
        panel.setMinimumWidth(300)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Поиск
        search_label = QLabel("🔍 Поиск по теории:")
        search_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Введите название алгоритма...")
        self.search_edit.textChanged.connect(self._on_search_text_changed)
        self.search_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #5A9BD5;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498DB;
            }
        """)
        layout.addWidget(self.search_edit)
        
        # Дерево категорий
        tree_label = QLabel("📁 Категории алгоритмов:")
        tree_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-top: 10px;")
        layout.addWidget(tree_label)
        
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabel("Алгоритмы и структуры данных")
        self.category_tree.setStyleSheet("""
            QTreeWidget {
                border: 2px solid #5A9BD5;
                border-radius: 5px;
                background-color: white;
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTreeWidget::item:selected {
                background-color: #e0f0ff;
                color: #2c3e50;
                font-weight: bold;
            }
        """)
        
        # Заполняем дерево данными
        self._populate_category_tree()
        
        self.category_tree.itemClicked.connect(self._on_tree_item_clicked)
        layout.addWidget(self.category_tree, 1)
        
        # Статистика
        stats_label = QLabel(f"📊 Всего алгоритмов: {self._count_total_algorithms()}")
        stats_label.setStyleSheet("color: #666; font-size: 12px; margin-top: 10px;")
        layout.addWidget(stats_label)
        
        return panel
    
    def _on_search_text_changed(self, text):
        """Обработка изменения текста в поле поиска"""
        search_text = text.lower().strip()
        
        # Ищем во всех элементах дерева
        root = self.category_tree.invisibleRootItem()
        self._search_in_tree(root, search_text)
        
        # Если поиск пустой, показываем все элементы и раскрываем первые уровни
        if not search_text:
            self._show_all_items_and_expand()
    def _show_all_items_and_expand(self):
        """Показывает все элементы дерева и раскрывает первые уровни"""
        root = self.category_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setHidden(False)
            item.setExpanded(True)  # Раскрываем категории
            
            # Показываем все алгоритмы внутри категорий
            for j in range(item.childCount()):
                child = item.child(j)
                child.setHidden(False)
    def _search_in_tree(self, parent_item, search_text):
        """Рекурсивный поиск в дереве"""
        if not search_text:
            return True
        
        # Флаг, показывающий, есть ли совпадения в поддереве
        has_match_in_subtree = False
        
        # Проверяем все дочерние элементы
        for i in range(parent_item.childCount()):
            item = parent_item.child(i)
            
            # Рекурсивно ищем в дочерних элементах
            child_has_match = False
            if item.childCount() > 0:
                child_has_match = self._search_in_tree(item, search_text)
            
            # Проверяем сам элемент
            item_text = item.text(0).lower()
            is_item_match = search_text in item_text
            
            # Показываем элемент если:
            # 1. Он сам содержит искомый текст
            # 2. Или хотя бы один из его потомков содержит текст
            should_show = is_item_match or child_has_match
            
            item.setHidden(not should_show)
            
            # Раскрываем элемент, если он не скрыт и есть дочерние элементы
            if not item.isHidden() and item.childCount() > 0:
                item.setExpanded(True)
            
            # Обновляем флаг совпадения в поддереве
            if should_show:
                has_match_in_subtree = True
                
        return has_match_in_subtree
    
    def _show_all_items(self):
        """Показывает все элементы дерева"""
        root = self.category_tree.invisibleRootItem()
        self._show_all_in_tree(root)
    
    def _show_all_in_tree(self, parent_item):
        """Рекурсивно показывает все элементы дерева"""
        for i in range(parent_item.childCount()):
            item = parent_item.child(i)
            item.setHidden(False)
            if item.childCount() > 0:
                self._show_all_in_tree(item)
    
    def _populate_category_tree(self):
        """Заполняет дерево категорий данными из theory_data"""
        # Маппинг категорий для отображения
        category_names = {
            "hash_tables": "🔑 Хэш-таблицы",
            "probabilistic": "🎲 Вероятностные структуры",
            "search": "🔍 Алгоритмы поиска",
            "sorting": "🎲 Сортировки",
            "trees": "🌳 Деревья", 
            "compression": "🔤 Сжатие данных",
            "data_structures": "📦 Структуры данных",
            "graphs": "🕸️ Графы"
        }
        
        for category_key, category_display in category_names.items():
            if category_key in self.theory_data and self.theory_data[category_key]:
                category_item = QTreeWidgetItem(self.category_tree)
                category_item.setText(0, category_display)
                category_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "category", "key": category_key})
                
                # Добавляем алгоритмы в категорию
                for algo_key, algo_data in self.theory_data[category_key].items():
                    algo_item = QTreeWidgetItem(category_item)
                    algo_item.setText(0, algo_data.get("name", algo_key))
                    algo_item.setData(0, Qt.ItemDataRole.UserRole, {
                        "type": "algorithm",
                        "category": category_key,
                        "key": algo_key
                    })
                
                # Разворачиваем категорию
                category_item.setExpanded(True)
    
    def _count_total_algorithms(self):
        """Подсчитывает общее количество алгоритмов"""
        count = 0
        for category in self.theory_data.values():
            if isinstance(category, dict):
                count += len(category)
        return count
    
    def _create_content_panel(self):
        """Создает панель с отображением содержимого"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Заголовок темы
        self.topic_title = QLabel("Выберите алгоритм или структуру данных")
        self.topic_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.topic_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 10px;
                background-color: #f0f8ff;
                border-radius: 6px;
                border: 1px solid #d0e0ff;
                margin-bottom: 10px;
            }
        """)
        self.topic_title.setWordWrap(True)
        layout.addWidget(self.topic_title)
        
        # Вкладки с разными разделами теории
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #5A9BD5;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 8px 15px;
                margin-right: 2px;
                border-radius: 4px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #5A9BD5;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #d0e0ff;
            }
        """)
        
        # Создаем вкладки
        self._create_content_tabs()
        
        layout.addWidget(self.tab_widget, 1)
        
        return panel
    
    def _create_content_tabs(self):
        """Создает вкладки для отображения контента"""
        # Вкладка 1: Общая информация
        self.general_tab = QWidget()
        self.general_layout = QVBoxLayout(self.general_tab)
        self.general_text = QTextBrowser()
        self.general_text.setOpenExternalLinks(True)
        self.general_text.setStyleSheet("""
            QTextBrowser {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        self.general_layout.addWidget(self.general_text)
        
        # Вкладка 2: Математическая формализация
        self.math_tab = QWidget()
        self.math_layout = QVBoxLayout(self.math_tab)
        self.math_text = QTextBrowser()
        self.math_text.setStyleSheet("""
            QTextBrowser {
                background-color: #f0fff0;
                border: 1px solid #a0d0a0;
                border-radius: 5px;
                padding: 15px;
                font-family: 'Times New Roman', serif;
                font-size: 14px;
            }
        """)
        self.math_layout.addWidget(self.math_text)
        
        # Вкладка 3: Псевдокод и реализация (УЛУЧШЕННАЯ)
        self.code_tab = QWidget()
        self.code_layout = QVBoxLayout(self.code_tab)
        
        # Контейнер для кода
        code_container = QWidget()
        code_container_layout = QVBoxLayout(code_container)
        code_container_layout.setContentsMargins(0, 0, 0, 0)
        code_container_layout.setSpacing(10)
        
        # Заголовок раздела кода
        code_header = QLabel("💻 Реализация алгоритма")
        code_header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        code_header.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        code_container_layout.addWidget(code_header)
        
        # Основной редактор кода с номерами строк
        self.code_editor = CodeEditor()
        self.code_editor.setReadOnly(True)
        code_container_layout.addWidget(self.code_editor, 3)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #5A9BD5; margin: 15px 0;")
        code_container_layout.addWidget(separator)
        
        # Пример работы алгоритма
        example_header = QLabel("📊 Пример работы алгоритма")
        example_header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        example_header.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        code_container_layout.addWidget(example_header)
        
        # Редактор для примера (без номеров строк для простоты)
        self.example_editor = QPlainTextEdit()
        self.example_editor.setReadOnly(True)
        self.example_editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0C2D48;
                color: #B1D4E0;
                border: 1px solid #145DA0;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        code_container_layout.addWidget(self.example_editor, 2)
        
        # Прокручиваемая область для контейнера кода
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(code_container)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #F0F0F0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #5A9BD5;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #3498DB;
            }
        """)
        
        self.code_layout.addWidget(scroll_area)
        
        # Вкладка 4: Применение и ссылки
        self.links_tab = QWidget()
        self.links_layout = QVBoxLayout(self.links_tab)
        self.links_text = QTextBrowser()
        self.links_text.setOpenExternalLinks(True)
        self.links_text.setStyleSheet("""
            QTextBrowser {
                background-color: #f0f8ff;
                border: 1px solid #b0d0ff;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
            }
        """)
        self.links_layout.addWidget(self.links_text)
        
        # Добавляем вкладки
        self.tab_widget.addTab(self.general_tab, "📝 Общее описание")
        self.tab_widget.addTab(self.math_tab, "🧮 Математика")
        self.tab_widget.addTab(self.code_tab, "💻 Алгоритм")
        self.tab_widget.addTab(self.links_tab, "🔗 Применение и ссылки")
    
    
    def _on_tree_item_clicked(self, item, column):
        """Обработка клика по элементу дерева"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
            
        if data["type"] == "algorithm":
            self._display_algorithm_theory(data["category"], data["key"])
    
    def _display_algorithm_theory(self, category_key, algo_key):
        """Отображает теорию выбранного алгоритма"""
        if (category_key not in self.theory_data or 
            not self.theory_data[category_key] or
            algo_key not in self.theory_data[category_key]):
            self._show_no_data_message()
            return
            
        algo_data = self.theory_data[category_key][algo_key]
        
        # Обновляем заголовок
        self.topic_title.setText(f"📚 {algo_data.get('name', algo_key)}")
        
        # === ВКЛАДКА 1: Общее описание ===
        general_html = self._create_general_html(algo_data)
        self.general_text.setHtml(general_html)
        
        # === ВКЛАДКА 2: Математическая формализация ===
        math_html = self._create_math_html(algo_data)
        self.math_text.setHtml(math_html)
        
        # === ВКЛАДКА 3: Алгоритм и псевдокод ===
        self._display_code(algo_data)
        
        # === ВКЛАДКА 4: Применение и ссылки ===
        links_html = self._create_links_html(algo_data)
        self.links_text.setHtml(links_html)
        
        # Переходим на первую вкладку
        self.tab_widget.setCurrentIndex(0)
    
    def _display_code(self, algo_data):
        """Отображает код алгоритма в улучшенном редакторе"""
        # Основной алгоритм
        algorithm = algo_data.get('algorithm', '')
        if algorithm:
            self.code_editor.setPlainText(algorithm)
        else:
            self.code_editor.setPlainText("# Алгоритм не предоставлен")
        
        # Пример работы алгоритма
        example = algo_data.get('example', '')
        if example:
            self.example_editor.setPlainText(example)
        else:
            self.example_editor.setPlainText("# Пример не предоставлен")
    
    def _show_no_data_message(self):
        """Показывает сообщение об отсутствии данных"""
        html = """
        <html>
        <head>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                color: #666; 
                text-align: center; 
                padding: 50px;
            }
            h2 { color: #e74c3c; }
        </style>
        </head>
        <body>
            <h2>⚠️ Данные не найдены</h2>
            <p>Теория для выбранного алгоритма отсутствует в базе данных.</p>
            <p>Попробуйте выбрать другой алгоритм или категорию.</p>
        </body>
        </html>
        """
        
        self.topic_title.setText("Данные не найдены")
        self.general_text.setHtml(html)
        self.math_text.setHtml(html)
        self.code_editor.setPlainText("# Данные не найдены")
        self.example_editor.setPlainText("# Данные не найдены")
        self.links_text.setHtml(html)
    
    def _create_general_html(self, algo_data):
        """Создает HTML для вкладки общего описания"""
        return f"""
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498DB; padding-bottom: 10px; }}
            h2 {{ color: #3498DB; margin-top: 25px; }}
            h3 {{ color: #5A9BD5; }}
            .complexity-box {{ 
                background-color: #e8f4fd; 
                padding: 15px; 
                border-radius: 8px; 
                border: 2px solid #3498DB;
                margin: 20px 0;
            }}
            .formula {{ 
                font-family: 'Times New Roman', serif; 
                font-size: 16px; 
                margin: 10px 0;
                padding-left: 20px;
            }}
            .property-list {{ padding-left: 20px; }}
            .property-list li {{ margin-bottom: 8px; }}
            a {{ color: #3498DB; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
        </head>
        <body>
        
        <h1>{algo_data.get('name', 'Алгоритм')}</h1>
        
        <div class="complexity-box">
            <h3 style='margin-top: 0; color: #3498DB;'>📊 Сложность алгоритма:</h3>
            <p style='font-size: 16px; font-weight: bold; color: #2c3e50;'>
                {algo_data.get('complexity', 'Не указана')}
            </p>
        </div>
        
        <h2>📖 Описание алгоритма</h2>
        <p>{algo_data.get('description', 'Описание отсутствует')}</p>
        """ + (f"""
        <h2>🔑 Ключевые свойства</h2>
        <ul class='property-list'>
        {''.join(f'<li>{prop}</li>' for prop in algo_data.get('properties', []))}
        </ul>
        """ if algo_data.get('properties') else "") + """
        </body></html>"""
    
    def _create_math_html(self, algo_data):
        """Создает HTML для математической вкладки"""
        formulas = algo_data.get('formulas', [])
        
        formulas_html = ""
        if formulas and isinstance(formulas, list) and len(formulas) > 0:
            formulas_html = f"""
            <div class='formula-box'><h3>📐 Формулы и уравнения:</h3>
            {''.join(f'<div class="formula-item"><b>•</b> {formula}</div>' for formula in formulas)}
            </div>
            """
        else:
            formulas_html = "<p style='color: #666; font-style: italic;'>Математическая формализация отсутствует</p>"
        
        return f"""
        <html>
        <head>
        <style>
            body {{ font-family: 'Times New Roman', serif; color: #2c3e50; line-height: 1.6; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #27AE60; margin-top: 25px; }}
            h3 {{ color: #229954; }}
            .formula-box {{ 
                background-color: #f0fff0; 
                padding: 15px; 
                border-radius: 8px; 
                border: 2px solid #27AE60;
                margin: 20px 0;
                font-family: 'Cambria Math', serif;
            }}
            .formula-item {{ 
                margin: 15px 0; 
                padding-left: 20px;
                border-left: 3px solid #27AE60;
            }}
            .complexity-analysis {{ 
                background-color: #e8f6f3; 
                padding: 15px; 
                border-radius: 8px; 
                margin: 20px 0;
            }}
        </style>
        </head>
        <body>
        <h2>🧮 Математическая формализация</h2>
        {formulas_html}
        <div class='complexity-analysis'>
        <h3>📈 Анализ сложности</h3>
        <p>{algo_data.get('complexity_analysis', algo_data.get('complexity', 'Анализ сложности не предоставлен'))}</p>
        </div>
        </body></html>"""
    
    def _create_links_html(self, algo_data):
        """Создает HTML для вкладки со ссылками"""
        applications = algo_data.get('applications', [])
        links = algo_data.get('links', {})
        
        applications_html = ""
        if applications and isinstance(applications, list) and len(applications) > 0:
            applications_html = f"""
            <div class='applications-box'>
            <h3>💡 Практическое применение</h3>
            {''.join(f'<div class="application-item"><b>•</b> {app}</div>' for app in applications)}
            </div>
            """
        
        links_html = ""
        if links and isinstance(links, dict) and len(links) > 0:
            links_html = "<div class='links-box'><h3>🌐 Дополнительные ресурсы</h3>"
            
            for link_name, link_url in links.items():
                # Определяем отображаемое имя и иконку
                icon = "🔗"
                display_name = link_name
                
                if link_name.lower() == "wikipedia":
                    icon = "📖"
                    display_name = "Wikipedia (русский)"
                elif link_name.lower() == "visualgo":
                    icon = "👁️"
                    display_name = "VisualGo (визуализация алгоритмов)"
                elif link_name.lower() == "geeksforgeeks":
                    icon = "💻"
                    display_name = "GeeksForGeeks (английский)"
                elif "youtube" in link_name.lower():
                    icon = "📺"
                elif "github" in link_name.lower():
                    icon = "🐙"
                
                links_html += f"""
                <div class='link-item'>
                    <b>{icon} {display_name}:</b><br>
                    <a href='{link_url}'>{link_url}</a>
                </div>
                """
            
            links_html += "</div>"
        
        # Если нет ни применений, ни ссылок
        if not applications_html and not links_html:
            content = "<p style='color: #666; font-style: italic;'>Информация о применении и ссылки отсутствуют</p>"
        else:
            content = applications_html + links_html
        
        return f"""
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
            h2 {{ color: #E67E22; margin-top: 25px; }}
            h3 {{ color: #D35400; }}
            .applications-box {{ 
                background-color: #fef9e7; 
                padding: 15px; 
                border-radius: 8px; 
                border: 1px solid #f1c40f;
                margin: 20px 0;
            }}
            .links-box {{ 
                background-color: #eaf2f8; 
                padding: 15px; 
                border-radius: 8px; 
                border: 1px solid #3498DB;
                margin: 20px 0;
            }}
            .application-item {{ margin: 10px 0; padding-left: 20px; }}
            .link-item {{ 
                margin: 15px 0; 
                padding: 10px;
                background-color: white;
                border-radius: 5px;
                border-left: 4px solid #3498DB;
            }}
            a {{ 
                color: #3498DB; 
                text-decoration: none;
                font-weight: bold;
            }}
            a:hover {{ 
                text-decoration: underline;
                color: #2980b9;
            }}
        </style>
        </head>
        <body>
        <h2>🔗 Применение и дополнительные ресурсы</h2>
        {content}
        </body></html>"""
    
    def _create_links_section(self, algo_data):
        """Создает секцию со ссылками"""
        links_html = "<div class='links-box'><h3>🌐 Дополнительные ресурсы</h3>"
        
        for link_name, link_url in algo_data.get('links', {}).items():
            if link_name == "wikipedia":
                display_name = "📖 Wikipedia (русский)"
                icon = "📖"
            elif link_name == "visualgo":
                display_name = "👁️ VisualGo (визуализация алгоритмов)"
                icon = "👁️"
            elif link_name == "geeksforgeeks":
                display_name = "💻 GeeksForGeeks (английский)"
                icon = "💻"
            else:
                display_name = link_name
                icon = "🔗"
            
            links_html += f"""
            <div class='link-item'>
                <b>{icon} {display_name}:</b><br>
                <a href='{link_url}'>{link_url}</a>
            </div>
            """
        
        links_html += "</div>"
        return links_html
    

    
    def _save_code(self):
        """Сохраняет код в файл"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить код", "", "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.code_editor.toPlainText())
                QMessageBox.information(self, "Успех", f"Код сохранен в файл:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    
    
    def show_category(self, category_name, algorithm_name=None):
        """Показывает конкретную категорию и алгоритм"""
        # Находим категорию
        for i in range(self.category_tree.topLevelItemCount()):
            item = self.category_tree.topLevelItem(i)
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and data.get("key") == category_name:
                self.category_tree.setCurrentItem(item)
                
                # Находим алгоритм, если указан
                if algorithm_name:
                    for j in range(item.childCount()):
                        child = item.child(j)
                        child_data = child.data(0, Qt.ItemDataRole.UserRole)
                        if child_data and child_data.get("key") == algorithm_name:
                            self.category_tree.setCurrentItem(child)
                            self._display_algorithm_theory(category_name, algorithm_name)
                            return
                
                return