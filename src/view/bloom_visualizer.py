from PyQt6.QtWidgets import (
    QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, 
    QGraphicsSimpleTextItem, QGraphicsEllipseItem
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty, QRectF
from PyQt6.QtGui import QColor, QFont, QPen, QBrush, QLinearGradient, QRadialGradient
import math


class BloomCellItem(QGraphicsRectItem):
    """Визуализация ячейки (бита) фильтра Блума"""
    
    def __init__(self, x, y, width, height, index, bit_value=0):
        super().__init__(0, 0, width, height)
        # А теперь двигаем ВСЮ ячейку в нужные координаты x, y
        self.setPos(x, y) 
        
        self.index = index
        self.bit_value = bit_value
        self.width = width
        self.height = height

        # Настройки внешнего вида
        self.default_color = QColor("#ecf0f1")
        self.set_color = QColor("#2ecc71")
        self.highlight_color = QColor("#3498db")
        self.collision_color = QColor("#e74c3c")
        
        self.is_highlighted = False
        self.is_collision = False
        
        self._update_appearance()
        
        # Добавляем текст индекса
        self.index_text = QGraphicsTextItem(str(index), self)
        self.index_text.setDefaultTextColor(QColor("#7f8c8d"))
        self.index_text.setFont(QFont("Arial", 10))
        
        # Центрируем текст
        text_rect = self.index_text.boundingRect()
        text_x = (width - text_rect.width()) / 2
        self.index_text.setPos(text_x, 5)
        
        # Текст значения бита
        self.value_text = QGraphicsTextItem("0", self)
        self.value_text.setDefaultTextColor(QColor("#2c3e50"))
        self.value_text.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        value_rect = self.value_text.boundingRect()
        value_x = (width - value_rect.width()) / 2
        self.value_text.setPos(value_x, height / 2 - value_rect.height() / 2)
        
        # Таймер для анимации
        self.scale_timer = QTimer()
        self.scale_timer.setSingleShot(True)
        self.scale_timer.timeout.connect(self._reset_scale)
        self.current_scale = 1.0
    
    def _update_appearance(self):
        """Обновляет внешний вид ячейки"""
        if self.is_collision:
            color = self.collision_color
            border_color = QColor("#c0392b")
            border_width = 3
        elif self.is_highlighted:
            color = self.highlight_color
            border_color = QColor("#2980b9")
            border_width = 2
        elif self.bit_value == 1:
            color = self.set_color
            border_color = QColor("#27ae60")
            border_width = 2
        else:
            color = self.default_color
            border_color = QColor("#bdc3c7")
            border_width = 1
        
        gradient = QLinearGradient(0, 0, 0, self.height)
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color.darker(120))
        
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(border_color, border_width))
    
    def set_bit_value(self, value: int):
        """Устанавливает значение бита"""
        self.bit_value = value
        self.value_text.setPlainText(str(value))
        
        # Центрируем текст
        value_rect = self.value_text.boundingRect()
        value_x = (self.width - value_rect.width()) / 2
        self.value_text.setPos(value_x, self.height / 2 - value_rect.height() / 2)
        
        self._update_appearance()
    
    def set_highlighted(self, highlighted=True, is_collision=False):
        """Подсвечивает ячейку"""
        self.is_highlighted = highlighted
        self.is_collision = is_collision
        self._update_appearance()
        
        if highlighted:
            # Анимация подсветки
            self.animate_highlight()
    
    def animate_highlight(self):
        """Анимация подсветки ячейки"""
        # Используем таймеры вместо QPropertyAnimation
        self._scale_up()
    
    def _scale_up(self):
        """Увеличивает масштаб ячейки"""
        self.setScale(1.1)
        self.scale_timer.start(150)  # Подождем немного
    
    def _reset_scale(self):
        """Сбрасывает масштаб ячейки"""
        self.setScale(1.0)


class BloomHashFunctionItem(QGraphicsEllipseItem):
    """Визуализация хэш-функции"""
    
    def __init__(self, x, y, radius, hash_num):
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.setPos(x, y)
        self.hash_num = hash_num
        self.radius = radius
        
        # Настройки внешнего вида
        colors = [
            QColor("#3498db"),  # синий
            QColor("#2ecc71"),  # зеленый
            QColor("#e74c3c"),  # красный
            QColor("#f39c12"),  # оранжевый
            QColor("#9b59b6"),  # фиолетовый
            QColor("#1abc9c")   # бирюзовый
        ]
        
        color_index = (hash_num - 1) % len(colors)
        self.color = colors[color_index]
        
        gradient = QRadialGradient(0, 0, radius)
        gradient.setColorAt(0, self.color.lighter(150))
        gradient.setColorAt(1, self.color.darker(150))
        
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(self.color.darker(200), 2))
        
        # Текст с номером хэш-функции
        self.text = QGraphicsTextItem(f"H{hash_num}", self)
        self.text.setDefaultTextColor(Qt.GlobalColor.white)
        self.text.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        text_rect = self.text.boundingRect()
        self.text.setPos(-text_rect.width() / 2, -text_rect.height() / 2)
        
        # Таймер для анимации
        self.opacity_timer = QTimer()
        self.opacity_timer.setSingleShot(True)
        self.opacity_timer.timeout.connect(self._reset_opacity)
    
    def animate_calculation(self):
        """Анимация расчета хэша"""
        self._pulse_opacity()
    
    def _pulse_opacity(self):
        """Пульсация прозрачности"""
        # Устанавливаем высокую прозрачность
        self.setOpacity(0.3)
        self.opacity_timer.start(500)
    
    def _reset_opacity(self):
        """Сбрасывает прозрачность к нормальному состоянию"""
        self.setOpacity(1.0)


class BloomVisualizer:
    """Визуализатор фильтра Блума с отображением индексов"""
    
    def __init__(self, scene):
        self.scene = scene
        self.cells = []
        self.hash_functions = []
        self.current_item = None
        self.stats_text = None
        self.info_labels = []  # Для хранения временных меток информации
        
        # Цвета для разных состояний
        self.colors = {
            "default": "#ecf0f1",
            "set": "#2ecc71",
            "highlight": "#3498db",
            "collision": "#e74c3c",
            "text": "#2c3e50",
            "background": "#f8f9fa"
        }
    
    def create_bloom_filter(self, size, num_hashes):
        """Создает визуализацию фильтра Блума"""
        # ОЧИЩАЕМ СЦЕНУ ПОЛНОСТЬЮ перед созданием
        self.clear()
        
        # Параметры отображения
        cell_width = 60
        cell_height = 80
        cell_spacing = 10
        hash_radius = 30
        
        # Рассчитываем позиционирование
        cells_per_row = min(10, size)  # Не больше 10 в строке
        rows = math.ceil(size / cells_per_row)
        
        start_x = - (cells_per_row * (cell_width + cell_spacing)) / 2
        start_y = 50
        
        # Создаем ячейки битового массива
        for i in range(size):
            row = i // cells_per_row
            col = i % cells_per_row
            
            x = start_x + col * (cell_width + cell_spacing)
            y = start_y + row * (cell_height + cell_spacing)
            
            cell = BloomCellItem(x, y, cell_width, cell_height, i)
            self.scene.addItem(cell)
            self.cells.append(cell)
        
        # Создаем визуализацию хэш-функций (если num_hashes > 0)
        if num_hashes > 0:
            hash_start_x = start_x - 150
            hash_y = start_y + rows * (cell_height + cell_spacing) + 100
            
            for i in range(num_hashes):
                x = hash_start_x + i * (hash_radius * 2 + 40)
                hash_func = BloomHashFunctionItem(x, hash_y, hash_radius, i + 1)
                self.scene.addItem(hash_func)
                self.hash_functions.append(hash_func)
        
        # Создаем заголовок
        title = self.scene.addText("Фильтр Блума")
        title.setDefaultTextColor(QColor("#2c3e50"))
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setPos(-50, -150)
        
        # Создаем панель для статистики
        stats_bg = QGraphicsRectItem(-180, -90, 360, 70)
        stats_bg.setBrush(QBrush(QColor("#f8f9fa")))
        stats_bg.setPen(QPen(QColor("#bdc3c7"), 1))
        self.scene.addItem(stats_bg)
        
        self.stats_text = self.scene.addText("Статистика будет обновляться...")
        self.stats_text.setDefaultTextColor(QColor("#2c3e50"))
        self.stats_text.setFont(QFont("Arial", 10))
        self.stats_text.setPos(-170, -85)
        
        # Устанавливаем размер сцены
        total_height = start_y + rows * (cell_height + cell_spacing) + 200
        if num_hashes > 0:
            total_height += 150  # Дополнительное место для хэш-функций
        
        self.scene.setSceneRect(-400, -200, 800, total_height)
        
        return True
    
    def _create_info_label(self, text, x, y, color="#2c3e50", duration=3000):
        """Создает временную информационную метку"""
        label = QGraphicsTextItem(text)
        label.setDefaultTextColor(QColor(color))
        label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        label.setPos(x, y)
        label.setZValue(100)  # На переднем плане
        self.scene.addItem(label)
        self.info_labels.append(label)
        
        # Удаляем метку через указанное время
        QTimer.singleShot(duration, lambda: self._remove_info_label(label))
        return label
    
    def _remove_info_label(self, label):
        """Удаляет информационную метку"""
        if label in self.info_labels:
            self.info_labels.remove(label)
            if label in self.scene.items():
                self.scene.removeItem(label)
    
    def _show_indices_info(self, indices, value, row_height=80, col_width=60, spacing=10):
        """Показывает информацию об индексах, куда добавляется значение"""
        # Рассчитываем позиции для каждого индекса
        for idx in indices:
            if 0 <= idx < len(self.cells):
                cell = self.cells[idx]
                # Позиция ячейки
                cell_pos = cell.pos()
                cell_x = cell_pos.x()
                cell_y = cell_pos.y()
                
                # Определяем цвет в зависимости от состояния бита
                if cell.bit_value == 1:
                    # Коллизия - бит уже был установлен
                    color = "#e74c3c"
                    status = "уже установлен"
                else:
                    # Новый бит
                    color = "#2ecc71"
                    status = "новый"
                
                # Создаем метку над ячейкой
                info_text = f"{value} → idx{idx}\n({status})"
                label = self._create_info_label(
                    info_text, 
                    cell_x + col_width/2 - 30,  # Центрируем
                    cell_y - 40, 
                    color=color,
                    duration=2500
                )
                
                # Добавляем стрелку для наглядности
                arrow = QGraphicsTextItem("↓", label)
                arrow.setDefaultTextColor(QColor(color))
                arrow.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                arrow.setPos(20, -15)
    
    def update_bit_array(self, bit_array):
        """Обновляет отображение битового массива"""
        for i, cell in enumerate(self.cells):
            if i < len(bit_array):
                cell.set_bit_value(bit_array[i])
    
    def highlight_indices(self, indices, is_collision=False, value=None, duration=2000):
        """Подсвечивает указанные индексы и показывает информацию"""
        # Сбрасываем предыдущую подсветку
        for cell in self.cells:
            cell.set_highlighted(False)
        
        # Подсвечиваем новые индексы
        for idx in indices:
            if 0 <= idx < len(self.cells):
                self.cells[idx].set_highlighted(True, is_collision)
        
        # Показываем информацию об индексах если есть значение
        if value is not None:
            self._show_indices_info(indices, value)
        
        # Сбрасываем подсветку через duration миллисекунд
        if duration > 0:
            QTimer.singleShot(duration, lambda: self._reset_highlight())
    
    def _reset_highlight(self):
        """Сбрасывает подсветку всех ячеек"""
        for cell in self.cells:
            cell.set_highlighted(False)
    
    def animate_hash_calculation(self, hash_num):
        """Анимирует расчет хэш-функции"""
        if 0 <= hash_num - 1 < len(self.hash_functions):
            self.hash_functions[hash_num - 1].animate_calculation()
            
            # Показываем информацию о хэш-функции
            hash_func = self.hash_functions[hash_num - 1]
            pos = hash_func.pos()
            self._create_info_label(
                f"Хэш-функция H{hash_num}\nвычисляет индекс...",
                pos.x() - 50,
                pos.y() - 60,
                color="#3498db",
                duration=1500
            )
    
    def update_stats(self, stats):
        """Обновляет статистику с учетом исправленных метрик"""
        if not self.stats_text:
            return
        
        stats_text = (
            f"📊 Статистика (исправленная):\n"
            f"• Уникальных элементов: {stats.get('items_added', 0)}\n"
            f"• Установлено битов: {stats.get('bits_set', 0)}/{stats.get('size', 0)} "
            f"({stats.get('fill_percentage', 0):.1%})\n"
            f"• Перезаписей битов: {stats.get('bit_overwrites', 0)}\n"
            f"• Вероятность FP: {stats.get('false_positive_rate', 0):.4%}\n"
            f"• Хэш-функций: {stats.get('actual_hashes', 0)}\n"
            f"• Теор. оптимально хэшей: {stats.get('theoretical_optimal_hashes', 0)}"
        )
        
        self.stats_text.setPlainText(stats_text)
    
    def show_check_result(self, result):
        """Показывает результат проверки элемента (упрощенная версия)"""
        indices = result.get("indices", [])
        bit_checks = result.get("bit_checks", [])
        item_value = result.get("item", "")
        
        # Показываем информацию о каждом проверяемом индексе
        for i, idx in enumerate(indices):
            if 0 <= idx < len(self.cells):
                is_set = bit_checks[i] == 1
                color = "#2ecc71" if is_set else "#e74c3c"
                status = "✓" if is_set else "✗"
                
                cell = self.cells[idx]
                cell_pos = cell.pos()
                
                self._create_info_label(
                    f"{status} idx{idx}",
                    cell_pos.x() + 65,
                    cell_pos.y() + 20,
                    color=color,
                    duration=3000
                )
        
        # Создаем текстовый результат
        result_y = self.stats_text.pos().y() + 150 if self.stats_text else 300
        
        if result.get("likely_present", False):
            probability = result.get("false_positive_probability", 0)
            result_text = (
                f"🔍 Результат проверки '{item_value}':\n"
                f"⚠️ ВОЗМОЖНО ПРИСУТСТВУЕТ\n"
                f"Вероятность ложного срабатывания: {probability:.4%}"
            )
            text_color = "#e74c3c"
        else:
            result_text = f"🔍 Результат проверки '{item_value}':\n✅ ТОЧНО ОТСУТСТВУЕТ"
            text_color = "#2ecc71"
        
        # Показываем метку с результатом
        self._create_info_label(
            result_text,
            -200,
            result_y,
            color=text_color,
            duration=5000
        )
    
    def clear(self):
        """Очищает визуализацию"""
        self.cells.clear()
        self.hash_functions.clear()
        self.current_item = None
        
        # Удаляем только элементы визуализатора
        items_to_remove = []
        for item in self.scene.items():
            if isinstance(item, (BloomCellItem, BloomHashFunctionItem)):
                items_to_remove.append(item)
            elif isinstance(item, QGraphicsTextItem) and (
                "Фильтр Блума" in item.toPlainText() or 
                "Статистика" in item.toPlainText() or
                item in self.info_labels
            ):
                items_to_remove.append(item)
        
        for item in items_to_remove:
            self.scene.removeItem(item)
        
        # Очищаем список информационных меток
        self.info_labels.clear()
    
    def process_action(self, action):
        """Обрабатывает действие для визуализации"""
        action_type = action.get("type", "")
        
        if action_type == "bloom_init":
            size = action.get("size", 100)
            num_hashes = action.get("num_hashes", 3)
            self.create_bloom_filter(size, num_hashes)
            return True
            
        elif action_type == "bloom_hash_calc":
            item = action.get("item", "")
            indices = action.get("indices", [])
            
            # Показываем информацию о вычислении
            self._create_info_label(
                f"Вычисление хэшей для '{item}'...",
                -150,
                -120,
                color="#3498db",
                duration=2000
            )
            
            # Анимируем хэш-функции
            for i in range(len(indices)):
                QTimer.singleShot(i * 300, lambda idx=i: self.animate_hash_calculation(idx + 1))
            
            return True
            
        elif action_type == "bloom_bit_set":
            bit_array = action.get("bit_array", [])
            indices = action.get("indices", [])
            new_indices = action.get("new_indices", [])
            item_value = action.get("item", "")
            stats = action.get("stats", {})
            
            # Показываем информацию о добавлении
            collision_count = len(indices) - len(new_indices)
            if collision_count > 0:
                self._create_info_label(
                    f"Добавление '{item_value}': {collision_count} коллизий",
                    -150,
                    -120,
                    color="#e74c3c",
                    duration=2000
                )
            else:
                self._create_info_label(
                    f"Добавление '{item_value}': все индексы новые",
                    -150,
                    -120,
                    color="#2ecc71",
                    duration=2000
                )
            
            # Обновляем битовый массив
            self.update_bit_array(bit_array)
            
            # Подсвечиваем индексы с информацией о значении
            is_collision = len(new_indices) < len(indices)
            self.highlight_indices(indices, is_collision, item_value)
            
            # Обновляем статистику
            self.update_stats(stats)
            
            return True
            
        elif action_type == "bloom_complete":
            stats = action.get("stats", {})
            bit_array = action.get("bit_array", [])
            
            # Обновляем финальное состояние
            self.update_bit_array(bit_array)
            self.update_stats(stats)
            
            # Показываем финальную информацию
            self._create_info_label(
                f"✅ Фильтр Блума построен!\n"
                f"Размер: {stats.get('size', 0)}, Хэш-функций: {len(self.hash_functions)}\n"
                f"Элементов: {stats.get('items_added', 0)}",
                -200,
                -120,
                color="#2ecc71",
                duration=5000
            )
            
            # Сбрасываем подсветку
            for cell in self.cells:
                cell.set_highlighted(False)
            
            return True
            
        elif action_type.startswith("bloom_check"):
            if action_type == "bloom_check_hash":
                indices = action.get("indices", [])
                item_value = action.get("item", "")
                
                # Показываем информацию о проверке
                self._create_info_label(
                    f"Проверка '{item_value}'...\n"
                    f"Вычисление {len(indices)} хэшей",
                    -150,
                    -120,
                    color="#3498db",
                    duration=2000
                )
                
                # Анимируем хэш-функции
                for i in range(len(indices)):
                    QTimer.singleShot(i * 300, lambda idx=i: self.animate_hash_calculation(idx + 1))
                
                # Показываем информацию о проверяемых индексах
                if item_value:
                    self._show_indices_info(indices, f"Проверка: {item_value}")
            
            elif action_type == "bloom_check_bit":
                index = action.get("index", 0)
                value = action.get("value", 0)
                item_value = action.get("item", "")
                
                # Подсвечиваем проверяемый бит
                if 0 <= index < len(self.cells):
                    self.cells[index].set_highlighted(True, value == 0)
                    
                    # Показываем информацию о бите
                    if item_value:
                        bit_status = "УСТАНОВЛЕН (1)" if value == 1 else "НЕ УСТАНОВЛЕН (0)"
                        color = "#2ecc71" if value == 1 else "#e74c3c"
                        
                        cell = self.cells[index]
                        cell_pos = cell.pos()
                        
                        self._create_info_label(
                            f"Бит idx{index}: {bit_status}",
                            cell_pos.x() + 65,
                            cell_pos.y() + 20,
                            color=color,
                            duration=2000
                        )
            
            elif action_type == "bloom_check_result":
                # Показываем финальный результат с деталями
                result = action.get("result", {})
                item_value = action.get("item", "")
                
                # Создаем детализированный текст результата
                result_text = f"🔍 Результат проверки '{item_value}':\n"
                
                if result.get("likely_present", False):
                    result_text += f"✅ ВОЗМОЖНО ПРИСУТСТВУЕТ в фильтре\n"
                    result_text += f"⚠️ Вероятность ложного срабатывания: {result.get('false_positive_probability', 0):.2%}"
                    text_color = "#e74c3c"
                else:
                    result_text += f"✅ ТОЧНО ОТСУТСТВУЕТ в фильтре"
                    text_color = "#2ecc71"
                
                # Показываем метку с деталями
                self._create_info_label(
                    result_text,
                    -200,
                    self.stats_text.pos().y() + 150 if self.stats_text else 300,
                    color=text_color,
                    duration=5000
                )
            
            return True
        
        return False