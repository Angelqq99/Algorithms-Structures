# view/huffman_visualizer.py
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QColor, QFont, QPen, QBrush, QPainterPath


class HuffmanVisualizer:
    """Визуализатор для алгоритма Хаффмана."""
    
    def __init__(self, scene):
        self.scene = scene
        self.color_palette = {
            # Основные цвета
            "primary": "#5A9BD5",
            "secondary": "#4ECDC4",
            "accent": "#FF6B6B",
            "success": "#2ECC71",
            "warning": "#FFD166",
            "info": "#3498DB",
            "dark": "#2c3e50",
            "light": "#f8f9fa",
            "gray": "#95A5A6",
            
            # Специфичные для Хаффмана
            "huffman_leaf": "#FF6B6B",      # Красный для листьев (символов)
            "huffman_internal": "#4ECDC4",  # Бирюзовый для внутренних узлов
            "huffman_root": "#9B59B6",      # Фиолетовый для корня
            
            # Для диаграмм
            "bar_chart": "#5A9BD5",
            "code_short": "#2ECC71",        # Зеленый для коротких кодов
            "code_medium": "#FFD166",       # Желтый для средних кодов
            "code_long": "#FF6B6B",         # Красный для длинных кодов
            
            # Для сравнения размеров
            "original": "#FF6B6B",          # Красный для оригинального размера
            "compressed": "#4ECDC4",        # Бирюзовый для сжатого размера
        }
        
        self.fonts = {
            "title": QFont("Arial", 20, QFont.Weight.Bold),
            "subtitle": QFont("Arial", 16, QFont.Weight.Bold),
            "normal": QFont("Arial", 12),
            "small": QFont("Arial", 10),
            "code": QFont("Courier", 11, QFont.Weight.Bold)
        }
    
    def clear_scene(self):
        """Очищает сцену безопасным способом."""
        try:
            # Безопасная очистка сцены
            if self.scene:
                # Сначала удаляем все элементы
                items = self.scene.items()
                for item in items:
                    try:
                        self.scene.removeItem(item)
                        # Для элементов QGraphicsItem лучше явно удалить
                        if hasattr(item, 'deleteLater'):
                            item.deleteLater()
                    except:
                        pass
                self.scene.clear()
                # Принудительно обновляем сцену
                self.scene.update()
        except Exception as e:
            print(f"Warning: error clearing scene: {e}")
    
    # ==================== ОСНОВНЫЕ МЕТОДЫ ВИЗУАЛИЗАЦИИ ====================
    
    def visualize_frequencies(self, frequencies, title="📊 Частоты символов"):
        """Визуализирует частоты символов в виде столбчатой диаграммы."""
        try:
            self.clear_scene()
            
            if not frequencies:
                self._create_text("Нет данных для отображения", 0, 0, self.fonts["normal"], self.color_palette["gray"])
                return
            
            # Сортируем частоты по убыванию
            sorted_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
            num_chars = len(frequencies)
            # Параметры отрисовки
            bar_width = 35
            spacing = 20
            max_bar_height = 200
            total_width = num_chars * (bar_width + spacing)
            start_x = -(total_width / 2)
            start_y = 50
            max_freq = max(frequencies.values())
            
            # Заголовок
            self._create_text(title, start_x-100, start_y-300, self.fonts["title"], self.color_palette["dark"])
            
            # Рисуем столбцы
            for i, (char, freq) in enumerate(sorted_freq):
                x = start_x + i * (bar_width + spacing)
                bar_height = (freq / max_freq) * max_bar_height if max_freq > 0 else 0
                
                # Столбец
                self._create_rectangle(x, start_y - bar_height, bar_width, bar_height,
                                     self.color_palette["bar_chart"], self.color_palette["dark"], 2)
                
                # Частота
                freq_text = self._create_text(str(freq), 
                                            x + bar_width/2, start_y - bar_height - 25,
                                            self.fonts["small"], self.color_palette["dark"])
                self._center_text_horizontally(freq_text, x, bar_width)
                
                # Символ
                char_display = self._format_char_display(char)
                char_text = self._create_text(char_display, 
                                            x + bar_width/2, start_y + 10,
                                            self.fonts["normal"], self.color_palette["dark"])
                char_text.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                self._center_text_horizontally(char_text, x, bar_width)
                
                # Процент от общего числа
                if max_freq > 0:
                    percentage = (freq / sum(frequencies.values())) * 100
                    percent_text = self._create_text(f"{percentage:.1f}%", 
                                                   x + bar_width/2, start_y - bar_height - 45,
                                                   self.fonts["small"], self.color_palette["info"])
                    self._center_text_horizontally(percent_text, x, bar_width)
            
            # Статистика
            total_chars = sum(frequencies.values())
            unique_chars = len(frequencies)
            most_common_char, most_common_freq = sorted_freq[0] if sorted_freq else ("-", 0)
            
            stats_text = (
                f"📈 Статистика частот:\n\n"
                f"• Всего символов: {total_chars}\n"
                f"• Уникальных символов: {unique_chars}\n"
                f"• Коэффициент разнообразия: {unique_chars/total_chars:.2%}\n"
                f"• Самый частый символ: '{self._format_char_display(most_common_char)}' ({most_common_freq} раз, {most_common_freq/total_chars:.1%})"
            )
            
            stats_box = self._create_rectangle(start_x - 10, start_y + 100, 550, 130,
                                             "#f0f8ff", self.color_palette["info"], 1)
            stats_box.setZValue(-1)
            
            self._create_text(stats_text, start_x, start_y + 60, self.fonts["small"], self.color_palette["dark"])
            
            # Обновляем сцену
            self.scene.update()
            
        except Exception as e:
            print(f"Error visualizing frequencies: {e}")
            self.clear_scene()
            self._create_text(f"Ошибка визуализации частот: {str(e)}", -100, 0, 
                            self.fonts["normal"], self.color_palette["accent"])
    
    def visualize_huffman_tree(self, tree_structure, tree_visualizer=None):
        """Визуализирует дерево Хаффмана."""
        try:
            self.clear_scene()
            
            if not tree_structure:
                self._create_text("Дерево пустое", 0, 0, self.fonts["normal"], self.color_palette["gray"])
                return False
            
            # Заголовок
            self._create_text("🌳 Дерево Хаффмана", -150, -220, self.fonts["title"], self.color_palette["dark"])
            
            # Проверяем глубину дерева
            tree_height = self._calculate_tree_height(tree_structure)
            if tree_height > 20:
                self._create_text("⚠️ Дерево слишком глубокое для детальной визуализации", 
                                -200, -140, self.fonts["small"], self.color_palette["warning"])
                # Показываем только корень
                self._create_text(f"Корень: {tree_structure.get('frequency', 0)}", 
                                -50, -100, self.fonts["subtitle"], self.color_palette["huffman_root"])
                return True
            
            # Используем встроенную отрисовку дерева
            self._draw_huffman_tree(tree_structure, 0, -180, 350, is_root=True)
            
            self._add_tree_legend(-550, -150)
            
            # Информация о дереве
            root_freq = tree_structure.get("frequency", 0)
            tree_info = f"Корень: {root_freq} | Узлов: {self._count_tree_nodes(tree_structure)} | Высота: {tree_height}"
            self._create_text(tree_info, -150, 180, self.fonts["small"], self.color_palette["info"])
            
            # Обновляем сцену
            self.scene.update()
            
            return True
                
        except Exception as e:
            print(f"Error visualizing tree: {e}")
            self.clear_scene()
            self._create_text(f"❌ Ошибка: {str(e)}", -150, 0, 
                            self.fonts["normal"], self.color_palette["accent"])
            return False
    
    def _draw_huffman_tree(self, node, x, y, x_offset, is_root=False):
        """Рекурсивная отрисовка узла дерева Хаффмана с кодами 0/1."""
        if not node:
            return

        try:
            # Определяем цвет узла
            if is_root:
                color = self.color_palette["huffman_root"]
            elif node.get("is_leaf", False):
                color = self.color_palette["huffman_leaf"]
            else:
                color = self.color_palette["huffman_internal"]

            # Рисуем связи к детям
            child_y = y + 80
            
            # Левый ребенок (код 0)
            if node.get("left"):
                child_x = x - x_offset
                # Линия к левому ребенку
                self._create_line(x, y + 20, child_x, child_y - 20, 
                               self.color_palette["dark"], 2)
                
                # Подпись "0" на линии
                self._create_text("0", (x + child_x)/2 - 15, (y + child_y)/2 - 10, 
                                 self.fonts["small"], self.color_palette["info"])
                
                self._draw_huffman_tree(node["left"], child_x, child_y, x_offset / 1.8)

            # Правый ребенок (код 1)
            if node.get("right"):
                child_x = x + x_offset
                # Линия к правому ребенку
                self._create_line(x, y + 20, child_x, child_y - 20, 
                               self.color_palette["dark"], 2)
                
                # Подпись "1" на линии
                self._create_text("1", (x + child_x)/2 + 5, (y + child_y)/2 - 10, 
                                 self.fonts["small"], self.color_palette["info"])
                
                self._draw_huffman_tree(node["right"], child_x, child_y, x_offset / 2.0)

            # Рисуем сам узел (круг)
            radius = 20
            ellipse = self.scene.addEllipse(x - radius, y - radius, radius * 2, radius * 2)
            ellipse.setBrush(QBrush(QColor(color)))
            ellipse.setPen(QPen(QColor(self.color_palette["dark"]), 2))
            
            # Текст внутри узла
            if node.get("is_leaf", False):
                symbol = node.get("symbol", "")
                display_text = f"'{self._format_char_display(symbol)}'\n{node.get('frequency', '')}"
                text_color = "#FFFFFF"
            else:
                display_text = str(node.get("frequency", ""))
                text_color = "#FFFFFF"
                
            text_item = self._create_text(display_text, x, y, 
                                         self.fonts["small"], text_color)
            text_rect = text_item.boundingRect()
            text_item.setPos(x - text_rect.width()/2, y - text_rect.height()/2)
            
        except Exception as e:
            print(f"Error drawing node: {e}")
    
    def _calculate_tree_height(self, node):
        """Вычисляет высоту дерева."""
        if not node or node.get("is_leaf", False):
            return 1
        
        left_height = self._calculate_tree_height(node.get("left")) if node.get("left") else 0
        right_height = self._calculate_tree_height(node.get("right")) if node.get("right") else 0
        
        return 1 + max(left_height, right_height)
    
    def visualize_codes_table(self, codes_table):
        """Визуализирует таблицу кодов Хаффмана."""
        try:
            self.clear_scene()
            
            if not codes_table:
                self._create_text("Нет кодов для отображения", 0, 0, 
                                self.fonts["normal"], self.color_palette["gray"])
                return
            
            # Сортируем по длине кода
            sorted_codes = sorted(codes_table, key=lambda x: (len(x["code"]), x["code"]))
            
            # Параметры отрисовки
            start_x = -320
            start_y = 50
            row_height = 45
            col_widths = [70, 100, 90, 130, 100]
            
            # Заголовок
            self._create_text("🔤 Таблица кодов Хаффмана", start_x, start_y - 90, 
                             self.fonts["title"], self.color_palette["dark"])
            
            # Заголовки столбцов
            headers = ["Символ", "Код", "Частота", "Бит/символ", "Экономия"]
            for i, header in enumerate(headers):
                x = start_x + sum(col_widths[:i]) + 10
                
                # Фон заголовка
                self._create_rectangle(x - 5, start_y - 5, col_widths[i], row_height,
                                     self.color_palette["dark"], "#ffffff", 0)
                
                # Текст заголовка
                header_text = self._create_text(header, x, start_y, 
                                              self.fonts["normal"], "#ffffff")
                header_text.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            
            # Данные таблицы
            current_y = start_y + row_height
            total_savings = 0
            total_freq = 0
            
            for idx, item in enumerate(sorted_codes):
                # Цвет фона строки
                row_color = "#f8f9fa" if idx % 2 == 0 else "#ffffff"
                
                # Фон строки
                row_bg = self._create_rectangle(start_x - 5, current_y - 5, 
                                              sum(col_widths), row_height,
                                              row_color, "#e0e0e0", 1)
                row_bg.setZValue(-1)
                
                # Символ
                char_display = self._format_char_display(item["symbol"])
                char_text = self._create_text(char_display, start_x + 10, current_y,
                                            self.fonts["normal"], self.color_palette["dark"])
                
                # Код
                code_len = len(item["code"])
                if code_len <= 3:
                    code_color = self.color_palette["code_short"]
                elif code_len <= 6:
                    code_color = self.color_palette["code_medium"]
                else:
                    code_color = self.color_palette["code_long"]
                
                code_text = self._create_text(item["code"], 
                                            start_x + col_widths[0] + 10, current_y,
                                            self.fonts["code"], code_color)
                
                # Частота
                freq_text = self._create_text(str(item["frequency"]), 
                                            start_x + col_widths[0] + col_widths[1] + 10, current_y,
                                            self.fonts["normal"], self.color_palette["dark"])
                
                # Бит на символ
                bits_text = f"8 → {code_len} бит"
                bits_color = self.color_palette["success"] if code_len < 8 else self.color_palette["accent"]
                bits_text_item = self._create_text(bits_text,
                                                 start_x + col_widths[0] + col_widths[1] + col_widths[2] + 10,
                                                 current_y, self.fonts["small"], bits_color)
                
                # Экономия
                savings = item.get("savings", 0)
                savings_color = self.color_palette["success"] if savings > 0 else self.color_palette["accent"]
                savings_text = f"{savings:+d} бит"
                savings_text_item = self._create_text(savings_text,
                                                    start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + 10,
                                                    current_y, self.fonts["small"], savings_color)
                savings_text_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
                
                # Накопительная статистика
                total_savings += savings * item["frequency"]
                total_freq += item["frequency"]
                
                current_y += row_height
            
            # Статистика под таблицей
            avg_code_length = sum(len(item["code"]) * item["frequency"] for item in sorted_codes) / total_freq if total_freq > 0 else 0
            
            stats_text = (
                f"📊 Статистика кодирования:\n\n"
                f"• Средняя длина кода: {avg_code_length:.2f} бит/символ\n"
                f"• Общая экономия: {total_savings} бит\n"
                f"• Макс. длина кода: {max(len(item['code']) for item in sorted_codes)} бит\n"
                f"• Мин. длина кода: {min(len(item['code']) for item in sorted_codes)} бит\n"
                f"• Энтропия (теоретический минимум): {avg_code_length:.2f} бит/символ"
            )
            
            stats_y = current_y + 20
            stats_bg = self._create_rectangle(start_x - 10, stats_y - 10, sum(col_widths) + 20, 150,
                                            "#f0f8ff", self.color_palette["info"], 2)
            stats_bg.setZValue(-1)
            
            self._create_text(stats_text, start_x, stats_y, self.fonts["small"], self.color_palette["dark"])
            
            # Обновляем сцену
            self.scene.update()
            
        except Exception as e:
            print(f"Error visualizing codes table: {e}")
            self.clear_scene()
            self._create_text(f"Ошибка визуализации таблицы кодов: {str(e)}", -100, 0, 
                            self.fonts["normal"], self.color_palette["accent"])
    
    def visualize_encoding_result(self, stats):
        """Визуализирует результат кодирования."""
        try:
            self.clear_scene()
            
            # Заголовок
            self._create_text("✅ Результат кодирования Хаффмана", -220, -180, 
                             self.fonts["title"], self.color_palette["dark"])
            
            # Разделитель
            self._create_horizontal_line(-350, -140, 700, self.color_palette["gray"], 1)
            
            # Панель исходного текста
            self._create_text("📝 Исходный текст:", -350, -100, 
                             self.fonts["subtitle"], self.color_palette["dark"])
            
            original_preview = stats.get("original_text", "")
            if len(original_preview) > 100:
                original_preview = original_preview[:97] + "..."
            
            original_bg = self._create_rectangle(-360, -70, 340, 100,
                                               "#f8f9fa", self.color_palette["gray"], 1)
            
            original_text = self._create_text(original_preview, -350, -60,
                                            QFont("Courier", 11), "#666666")
            original_text.setTextWidth(330)
            
            original_stats = f"Длина: {len(stats.get('original_text', ''))} символов, {stats.get('original_size_bits', 0)} бит"
            self._create_text(original_stats, -350, 40, 
                             self.fonts["small"], self.color_palette["info"])
            
            # Панель закодированного текста
            self._create_text("🔒 Закодированный текст:", 10, -100, 
                             self.fonts["subtitle"], self.color_palette["dark"])
            
            encoded_preview = stats.get("encoded_text", "")
            if len(encoded_preview) > 150:
                encoded_preview = encoded_preview[:147] + "..."
            
            encoded_bg = self._create_rectangle(0, -70, 340, 100,
                                              "#f0f8ff", self.color_palette["info"], 1)
            
            encoded_text = self._create_text(encoded_preview, 10, -60,
                                           QFont("Courier", 11), self.color_palette["info"])
            encoded_text.setTextWidth(330)
            
            encoded_stats = f"Длина: {len(stats.get('encoded_text', ''))} бит, {len(stats.get('encoded_text', ''))/8:.1f} байт"
            self._create_text(encoded_stats, 10, 40, 
                             self.fonts["small"], self.color_palette["info"])
            
            # Диаграмма сравнения размеров
            self._visualize_size_comparison(stats, -50, 120)
            
            # Статистика сжатия
            stats_x = 100
            stats_y = 100
            
            original_len = len(stats.get('original_text', ''))
            compressed_bits = stats.get('compressed_size_bits', 0)
            compression_ratio = stats.get('compression_ratio', 1.0)
            savings_percentage = stats.get('savings_percentage', 0.0)
            
            compression_stats = (
                f"📊 Итоговая статистика сжатия:\n\n"
                f"• Коэффициент сжатия: {compression_ratio:.2f}:1\n"
                f"• Экономия: {savings_percentage:.1f}%\n"
                f"• Уникальных символов: {len(stats.get('codes', []))}\n"
                f"• Средняя длина кода: {compressed_bits / original_len:.2f} бит/символ" if original_len > 0 else "• Средняя длина кода: N/A"
            )
            
            stats_bg = self._create_rectangle(stats_x - 15, stats_y - 15, 330, 180,
                                            "#e8f4fd", self.color_palette["primary"], 2)
            stats_bg.setZValue(-1)
            
            self._create_text(compression_stats, stats_x, stats_y, 
                             self.fonts["small"], self.color_palette["dark"])
            
            # Обновляем сцену
            self.scene.update()
            
        except Exception as e:
            print(f"Error visualizing encoding result: {e}")
            self.clear_scene()
            self._create_text(f"Ошибка визуализации результата: {str(e)}", -100, 0, 
                            self.fonts["normal"], self.color_palette["accent"])
    
    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================
    
    def _visualize_size_comparison(self, stats, center_x, y):
        """Визуализирует сравнение размеров в виде диаграммы."""
        try:
            original_bits = stats.get("original_size_bits", 0)
            compressed_bits = stats.get("compressed_size_bits", 0)
            
            if original_bits == 0:
                return
            
            max_bits = max(original_bits, compressed_bits)
            scale_factor = min(250 / max_bits, 1.0)  # Максимальная высота 250
            bar_width = 70
            
            # Оригинальный размер
            original_height = original_bits * scale_factor
            original_bar = self._create_rectangle(center_x - 120 - bar_width/2, y, 
                                                bar_width, original_height,
                                                self.color_palette["original"],
                                                self.color_palette["dark"], 2)
            
            # Метка оригинального размера
            original_label = self._create_text(f"ДО\n{original_bits} бит",
                                             center_x - 120, y + original_height + 20,
                                             self.fonts["small"], self.color_palette["original"])
            original_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self._center_text_horizontally(original_label, center_x - 120 - bar_width/2, bar_width)
            
            # Сжатый размер
            compressed_height = compressed_bits * scale_factor
            compressed_bar = self._create_rectangle(center_x + 60 - bar_width/2, y,
                                                  bar_width, compressed_height,
                                                  self.color_palette["compressed"],
                                                  self.color_palette["dark"], 2)
            
            # Метка сжатого размера
            compressed_label = self._create_text(f"ПОСЛЕ\n{compressed_bits} бит",
                                               center_x + 60, y + compressed_height + 20,
                                               self.fonts["small"], self.color_palette["compressed"])
            compressed_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self._center_text_horizontally(compressed_label, center_x + 60 - bar_width/2, bar_width)
            
            # Стрелка сжатия (если есть экономия)
            if original_bits > compressed_bits:
                arrow_y = y + max(original_height, compressed_height) / 2
                
                # Линия стрелки
                arrow_line = self._create_line(center_x - 60, arrow_y-150, center_x + 30, arrow_y-150,
                                             self.color_palette["warning"], 3, Qt.PenStyle.SolidLine)
                
                # Наконечник стрелки
                arrow_head = self._create_arrow_head(center_x + 30, arrow_y-150, 10, 
                                                   self.color_palette["warning"])
                
                # Текст экономии
                savings = original_bits - compressed_bits
                savings_percentage = stats.get('savings_percentage', 0.0)
                savings_text = f"Экономия:\n{savings} бит ({savings_percentage:.1f}%)"
                savings_label = self._create_text(savings_text,
                                                center_x - 15, arrow_y - 200,
                                                self.fonts["small"], self.color_palette["warning"])
                savings_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                self._center_text_horizontally(savings_label, center_x - 15, 30)
                
        except Exception as e:
            print(f"Error in size comparison: {e}")
    
    def _add_tree_legend(self, x, y):
        """Добавляет легенду для дерева Хаффмана."""
        try:
            legend_title = "🎨 Легенда дерева Хаффмана:"
            self._create_text(legend_title, x, y, 
                             self.fonts["normal"], self.color_palette["dark"])
            
            # Элементы легенды
            items = [
                ("Корень дерева", self.color_palette["huffman_root"]),
                ("Внутренние узлы", self.color_palette["huffman_internal"]),
                ("Листья (символы)", self.color_palette["huffman_leaf"])
            ]
            
            for i, (text, color) in enumerate(items):
                item_y = y + 30 + i * 25
                
                # Цветной квадрат
                self._create_rectangle(x, item_y, 15, 15, color, self.color_palette["dark"], 1)
                
                # Текст
                self._create_text(text, x + 20, item_y, 
                                self.fonts["small"], self.color_palette["dark"])
            
            # Обозначения ребер
            edge_y = y + 110
            self._create_text("Обозначения ребер:", x, edge_y,
                             self.fonts["small"], self.color_palette["dark"])
            
            self._create_text("0 → левое ребро", x + 10, edge_y + 25,
                             self.fonts["small"], self.color_palette["info"])
            self._create_text("1 → правое ребро", x + 10, edge_y + 45,
                             self.fonts["small"], self.color_palette["info"])
                             
        except Exception as e:
            print(f"Error adding tree legend: {e}")
    
    def _count_tree_nodes(self, tree_structure):
        """Подсчитывает количество узлов в дереве."""
        if not tree_structure:
            return 0
        
        count = 1
        if tree_structure.get("left"):
            count += self._count_tree_nodes(tree_structure["left"])
        if tree_structure.get("right"):
            count += self._count_tree_nodes(tree_structure["right"])
        
        return count
    
    # ==================== БАЗОВЫЕ МЕТОДЫ СОЗДАНИЯ ЭЛЕМЕНТОВ ====================
    
    def _create_text(self, text, x, y, font, color):
        """Создает текстовый элемент на сцене."""
        try:
            text_item = QGraphicsTextItem(text)
            text_item.setPos(x, y)
            text_item.setFont(font)
            text_item.setDefaultTextColor(QColor(color))
            self.scene.addItem(text_item)
            return text_item
        except Exception as e:
            print(f"Error creating text: {e}")
            return None
    
    def _create_rectangle(self, x, y, width, height, fill_color, border_color, border_width=1):
        """Создает прямоугольник на сцене."""
        try:
            rect = QGraphicsRectItem(x, y, width, height)
            rect.setBrush(QBrush(QColor(fill_color)))
            rect.setPen(QPen(QColor(border_color), border_width))
            self.scene.addItem(rect)
            return rect
        except Exception as e:
            print(f"Error creating rectangle: {e}")
            return None
    
    def _create_line(self, x1, y1, x2, y2, color, width=1, style=Qt.PenStyle.SolidLine):
        """Создает линию на сцене."""
        try:
            line = QGraphicsLineItem(x1, y1, x2, y2)
            line.setPen(QPen(QColor(color), width, style))
            self.scene.addItem(line)
            return line
        except Exception as e:
            print(f"Error creating line: {e}")
            return None
    
    def _create_horizontal_line(self, x, y, length, color, width=1):
        """Создает горизонтальную линию."""
        return self._create_line(x, y, x + length, y, color, width)
    
    def _create_arrow_head(self, x, y, size, color):
        """Создает наконечник стрелки."""
        try:
            path = QPainterPath()
            path.moveTo(x, y)
            path.lineTo(x - size, y - size/2)
            path.lineTo(x - size, y + size/2)
            path.closeSubpath()
            
            arrow = self.scene.addPath(path)
            arrow.setBrush(QBrush(QColor(color)))
            arrow.setPen(QPen(Qt.PenStyle.NoPen))
            return arrow
        except Exception as e:
            print(f"Error creating arrow: {e}")
            return None
    
    def _center_text_horizontally(self, text_item, x, width):
        """Центрирует текст горизонтально в пределах ширины."""
        if text_item:
            try:
                text_rect = text_item.boundingRect()
                text_item.setPos(x + (width - text_rect.width()) / 2, text_item.y())
            except Exception as e:
                print(f"Error centering text: {e}")
    
    def _format_char_display(self, char):
        """Форматирует символ для отображения."""
        if char == " ":
            return "␣"
        elif char == "\n":
            return "↵"
        elif char == "\t":
            return "→"
        elif char == "\r":
            return "⏎"
        elif isinstance(char, str) and len(char) > 0 and ord(char[0]) < 32:  # Управляющие символы
            return f"\\x{ord(char[0]):02x}"
        else:
            return char
    
    def get_scene_rect_for_content(self):
        """Возвращает рекомендуемый размер сцены для содержимого."""
        try:
            items_rect = self.scene.itemsBoundingRect()
            if items_rect.isValid():
                return items_rect.adjusted(-50, -50, 50, 50)
            return QRectF(-400, -300, 800, 600)
        except Exception as e:
            print(f"Error getting scene rect: {e}")
            return QRectF(-400, -300, 800, 600)


    def visualize_tree_building_step(self, action, step_number=None, total_steps=None):
        """Визуализирует шаг построения дерева Хаффмана."""
        try:
            self.clear_scene()  # Всегда очищаем сцену перед отрисовкой шага
            
            action_type = action.get("type", "")
            
            # Используем переданный номер шага или берем из action
            if step_number is None:
                step_number = action.get("step", 0)
            
            # Заголовок шага
            step_title = f"Шаг {step_number}: {action_type.replace('_', ' ').title()}"
            
            # Отображаем информацию о шаге
            self._create_text(step_title, -300, -220, 
                            self.fonts["subtitle"], self.color_palette["info"])
            
            # Описание шага
            description = action.get("description", "")
            if description:
                self._create_text(description, -300, -190, 
                                self.fonts["small"], self.color_palette["dark"])
            
            # Отображение общего прогресса
            if total_steps:
                progress_text = f"Прогресс: {step_number}/{total_steps}"
                self._create_text(progress_text, 200, -220,
                                self.fonts["small"], self.color_palette["info"])
                
                # Простая прогресс-бар
                progress_width = 300
                progress_filled = (step_number / total_steps) * progress_width
                self._create_rectangle(-150, -200, progress_width, 10,
                                    "#e0e0e0", self.color_palette["gray"], 1)
                self._create_rectangle(-150, -200, progress_filled, 10,
                                    self.color_palette["success"], self.color_palette["success"], 1)
            
            # Специфичная визуализация для разных типов действий
            start_y = -150
            
            if action_type == "heap_initialized":
                self._visualize_heap_initialized(action, -300, start_y)
            elif action_type == "nodes_selected":
                self._visualize_nodes_selected(action, -300, start_y)
            elif action_type == "nodes_merged":
                self._visualize_nodes_merged(action, -300, start_y)
            elif action_type == "heap_updated":
                self._visualize_heap_updated(action, -300, start_y)
            elif action_type == "tree_built":
                self._visualize_tree_built(action, -300, start_y)
            elif action_type == "code_assigned":
                self._visualize_code_assigned(action, -300, start_y)
            
            # Добавляем легенду
            self._add_step_legend(-300, start_y + 120)
            
            # Обновляем сцену
            self.scene.update()
            
        except Exception as e:
            print(f"Error in visualize_tree_building_step: {e}")
            # В случае ошибки просто логируем шаг
            self.clear_scene()
            self._create_text(f"Ошибка на шаге {action.get('step', '?')}: {str(e)}", -300, -100, 
                            self.fonts["small"], self.color_palette["accent"])

    def _visualize_heap_initialized(self, action, x, y):
        """Визуализирует инициализацию кучи."""
        try:
            heap_items = action.get("heap_items", [])
            
            self._create_text("Инициализация кучи:", x, y, 
                            self.fonts["normal"], self.color_palette["dark"])
            
            # Отображаем элементы кучи
            heap_y = y + 30
            items_per_row = 5
            
            for i, item in enumerate(heap_items):
                symbol = item.get("symbol", "")
                frequency = item.get("frequency", 0)
                
                row = i // items_per_row
                col = i % items_per_row
                
                # Блок элемента
                elem_x = x + col * 60
                elem_y = heap_y + row * 40
                
                # Цвет в зависимости от типа
                if symbol:
                    color = self.color_palette["huffman_leaf"]
                    text = f"'{self._format_char_display(symbol)}'\n{frequency}"
                else:
                    color = self.color_palette["huffman_internal"]
                    text = str(frequency)
                
                # Прямоугольник элемента
                self._create_rectangle(elem_x, elem_y, 50, 30, color, self.color_palette["dark"], 1)
                
                # Текст элемента
                self._create_text(text, elem_x + 25, elem_y + 15, 
                                self.fonts["small"], "#FFFFFF")
                
            # Статистика кучи
            stats_y = heap_y + ((len(heap_items) + items_per_row - 1) // items_per_row) * 40 + 20
            self._create_text(f"Всего элементов в куче: {len(heap_items)}", 
                            x, stats_y, self.fonts["small"], self.color_palette["info"])
            
        except Exception as e:
            print(f"Error in _visualize_heap_initialized: {e}")

    def _visualize_nodes_selected(self, action, x, y):
        """Визуализирует выбор узлов для объединения."""
        try:
            left_node = action.get("left_node", {})
            right_node = action.get("right_node", {})
            
            self._create_text("Выбор узлов для объединения:", x, y, 
                            self.fonts["normal"], self.color_palette["dark"])
            
            # Отображаем выбранные узлы
            nodes_y = y + 30
            
            if left_node:
                left_freq = left_node.get("frequency", 0)
                left_sym = left_node.get("symbol", "")
                
                # Рисуем левый узел
                self._create_rectangle(x, nodes_y, 60, 40, 
                                    self.color_palette["huffman_leaf"], self.color_palette["dark"], 2)
                
                if left_sym:
                    left_text = f"'{self._format_char_display(left_sym)}'\n{left_freq}"
                else:
                    left_text = str(left_freq)
                    
                self._create_text(left_text, x + 30, nodes_y + 20, 
                                self.fonts["small"], "#FFFFFF")
                
                self._create_text("Левый", x, nodes_y + 45, 
                                self.fonts["small"], self.color_palette["dark"])
            
            if right_node:
                right_freq = right_node.get("frequency", 0)
                right_sym = right_node.get("symbol", "")
                
                # Рисуем правый узел
                self._create_rectangle(x + 100, nodes_y, 60, 40, 
                                    self.color_palette["huffman_leaf"], self.color_palette["dark"], 2)
                
                if right_sym:
                    right_text = f"'{self._format_char_display(right_sym)}'\n{right_freq}"
                else:
                    right_text = str(right_freq)
                    
                self._create_text(right_text, x + 130, nodes_y + 20, 
                                self.fonts["small"], "#FFFFFF")
                
                self._create_text("Правый", x + 100, nodes_y + 45, 
                                self.fonts["small"], self.color_palette["dark"])
            
            # Знак сложения между узлами
            self._create_text("+", x + 75, nodes_y + 20, 
                            self.fonts["normal"], self.color_palette["dark"])
            
            # Стрелка
            self._create_text("↓", x + 75, nodes_y + 60, 
                            self.fonts["normal"], self.color_palette["success"])
            
        except Exception as e:
            print(f"Error in _visualize_nodes_selected: {e}")

    def _visualize_nodes_merged(self, action, x, y):
        """Визуализирует объединение узлов."""
        try:
            merged_freq = action.get("merged_frequency", 0)
            left_freq = action.get("left_frequency", 0)
            right_freq = action.get("right_frequency", 0)
            
            self._create_text("Объединение узлов:", x, y, 
                            self.fonts["normal"], self.color_palette["dark"])
            
            # Показываем операцию
            operation_y = y + 30
            self._create_text(f"{left_freq} + {right_freq} = {merged_freq}", 
                            x, operation_y, self.fonts["normal"], self.color_palette["dark"])
            
            # Рисуем новый узел
            node_y = y + 60
            self._create_rectangle(x, node_y, 80, 40, 
                                self.color_palette["huffman_internal"], self.color_palette["dark"], 2)
            
            self._create_text(str(merged_freq), x + 40, node_y + 20, 
                            self.fonts["normal"], "#FFFFFF")
            
            self._create_text("Новый внутренний узел", x, node_y + 45, 
                            self.fonts["small"], self.color_palette["dark"])
            
        except Exception as e:
            print(f"Error in _visualize_nodes_merged: {e}")

    def _visualize_heap_updated(self, action, x, y):
        """Визуализирует обновление кучи."""
        try:
            heap_size = action.get("heap_size", 0)
            heap_items = action.get("heap_items", [])
            
            self._create_text("Куча после обновления:", x, y, 
                            self.fonts["normal"], self.color_palette["dark"])
            
            # Отображаем состояние кучи
            heap_y = y + 30
            self._create_text(f"Размер кучи: {heap_size}", x, heap_y, 
                            self.fonts["small"], self.color_palette["info"])
            
            # Визуализируем элементы кучи
            if heap_items:
                items_y = heap_y + 30
                items_per_row = 6
                
                for i, item in enumerate(heap_items):
                    symbol = item.get("symbol", "")
                    frequency = item.get("frequency", 0)
                    
                    row = i // items_per_row
                    col = i % items_per_row
                    
                    elem_x = x + col * 50
                    elem_y = items_y + row * 35
                    
                    if symbol:
                        color = self.color_palette["huffman_leaf"]
                        text = self._format_char_display(symbol)
                    else:
                        color = self.color_palette["huffman_internal"]
                        text = str(frequency)
                    
                    # Квадрат элемента
                    self._create_rectangle(elem_x, elem_y, 40, 25, color, self.color_palette["dark"], 1)
                    
                    # Текст
                    self._create_text(text, elem_x + 20, elem_y + 12, 
                                    self.fonts["small"], "#FFFFFF")
                    
        except Exception as e:
            print(f"Error in _visualize_heap_updated: {e}")

    def _visualize_tree_built(self, action, x, y):
        """Визуализирует построенное дерево."""
        try:
            root_frequency = action.get("root_frequency", 0)
            
            self._create_text("Дерево построено!", x, y, 
                            self.fonts["subtitle"], self.color_palette["success"])
            
            self._create_text(f"Частота корня: {root_frequency}", x, y + 30, 
                            self.fonts["normal"], self.color_palette["dark"])
            
            # Простая схема дерева
            self._create_text("   🌳   ", x, y + 70, 
                            QFont("Arial", 30), self.color_palette["huffman_root"])
            
            # Ветви
            self._create_text("  /   \\  ", x, y + 110, 
                            QFont("Arial", 20), self.color_palette["dark"])
            
        except Exception as e:
            print(f"Error in _visualize_tree_built: {e}")

    def _add_step_legend(self, x, y):
        """Добавляет легенду для шагов построения."""
        try:
            self._create_text("🎨 Обозначения:", x, y, 
                            self.fonts["small"], self.color_palette["dark"])
            
            # Элементы легенды
            items = [
                ("Лист (символ)", self.color_palette["huffman_leaf"]),
                ("Внутренний узел", self.color_palette["huffman_internal"]),
                ("Корень", self.color_palette["huffman_root"])
            ]
            
            for i, (text, color) in enumerate(items):
                item_y = y + 20 + i * 20
                
                # Цветной квадрат
                self._create_rectangle(x, item_y, 12, 12, color, self.color_palette["dark"], 1)
                
                # Текст
                self._create_text(text, x + 15, item_y, 
                                self.fonts["small"], self.color_palette["dark"])
                
        except Exception as e:
            print(f"Error in _add_step_legend: {e}")