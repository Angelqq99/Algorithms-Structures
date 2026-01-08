"""
Визуализатор для стека, очереди и дека с анимациями.
"""
from PyQt6.QtWidgets import QGraphicsObject, QGraphicsRectItem, QGraphicsTextItem, QGraphicsSimpleTextItem
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QPen, QBrush, QFont, QPainter, QLinearGradient, QPainterPath
import math


class ContainerElement(QGraphicsObject):
    """Графический элемент контейнера с анимациями и стилем как в хэш-таблице"""
    
    def __init__(self, value, x, y, width, height, container_type="stack", index=0, operation_color=None):
        super().__init__()
        self.value = value
        self.width = width
        self.height = height
        self.container_type = container_type
        self.index = index
        self.is_highlighted = False
        self.is_operating = False
        self.operation_color = operation_color
        
        # Стиль как в хэш-таблице - разделенная ячейка
        self.setPos(x, y)
        self.setAcceptHoverEvents(True)
        self.setZValue(1)
        
        # Создаем подэлементы
        self._create_subitems()
        
    def _create_subitems(self):
        """Создает все графические элементы ячейки"""
        # Размеры областей
        self.index_width = 60
        self.value_width = self.width - self.index_width
        
        # 1. ОБЛАСТЬ ИНДЕКСА (левая часть)
        self.index_rect = QGraphicsRectItem(0, 0, self.index_width, self.height, self)
        self.index_rect.setBrush(self._get_index_brush())
        self.index_rect.setPen(QPen(QColor("#7f8c8d"), 2))
        
        # Текст индекса
        self.index_text = QGraphicsTextItem(str(self.index), self)
        self.index_text.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.index_text.setDefaultTextColor(QColor("#2c3e50"))
        # Центрирование
        text_rect = self.index_text.boundingRect()
        text_x = (self.index_width - text_rect.width()) / 2
        self.index_text.setPos(text_x, self.height/2 - text_rect.height()/2)
        
        # 2. ОБЛАСТЬ ЗНАЧЕНИЯ (правая часть)
        self.value_rect = QGraphicsRectItem(self.index_width, 0, self.value_width, self.height, self)
        self.value_rect.setBrush(self._get_value_brush())
        self.value_rect.setPen(QPen(QColor("#7f8c8d"), 2))
        
        # Текст значения
        self.value_text = QGraphicsTextItem(str(self.value), self)
        self.value_text.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.value_text.setDefaultTextColor(QColor("#2c3e50"))
        # Центрирование
        value_text_rect = self.value_text.boundingRect()
        value_x = self.index_width + (self.value_width - value_text_rect.width()) / 2
        self.value_text.setPos(value_x, self.height/2 - value_text_rect.height()/2)
        
        # 3. ИНФОРМАЦИЯ О ТИПЕ
        type_text = QGraphicsTextItem(self._get_type_symbol(), self)
        type_text.setFont(QFont("Arial", 10))
        type_text.setDefaultTextColor(QColor("#666"))
        type_text.setPos(self.index_width + 5, 5)
        
    def _get_index_brush(self):
        """Кисть для области индекса"""
        if self.is_operating:
            return QBrush(QColor("#FFA500"))
        elif self.is_highlighted:
            return QBrush(QColor("#FFD700"))
        else:
            # Зебрирование как в хэш-таблице
            return QBrush(QColor("#ecf0f1") if self.index % 2 == 0 else QColor("#bdc3c7"))
    
    def _get_value_brush(self):
        """Кисть для области значения"""
        if self.operation_color:
            return QBrush(QColor(self.operation_color))
        elif self.is_operating:
            return QBrush(QColor("#FFA500"))
        elif self.is_highlighted:
            return QBrush(QColor("#FFD700"))
        else:
            # Цвет зависит от типа контейнера
            colors = {
                "stack": "#4ECDC4",
                "queue": "#FF6B6B",
                "deque": "#5A9BD5"
            }
            color = colors.get(self.container_type, "#5A9BD5")
            return QBrush(QColor(color))
    
    def _get_type_symbol(self):
        """Символ типа операции"""
        symbols = {
            "stack": "📚",
            "queue": "📥",
            "deque": "🔄"
        }
        return symbols.get(self.container_type, "🔹")
    
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget):
        """Пустая реализация - все рисуется дочерними элементами"""
        pass
    
    def highlight(self, color=None):
        """Подсвечивает элемент"""
        self.is_highlighted = True
        if color:
            self.operation_color = color
        self._update_appearance()
    
    def set_operating(self, is_operating=True, color="#FFA500"):
        """Устанавливает состояние операции"""
        self.is_operating = is_operating
        if is_operating:
            self.operation_color = color
        else:
            self.operation_color = None
        self._update_appearance()
        
        # Автосброс через 1 секунду
        if is_operating:
            QTimer.singleShot(1000, lambda: self.set_operating(False))
    
    def _update_appearance(self):
        """Обновляет внешний вид всех элементов"""
        if hasattr(self, 'index_rect'):
            self.index_rect.setBrush(self._get_index_brush())
        if hasattr(self, 'value_rect'):
            self.value_rect.setBrush(self._get_value_brush())
    
    def bounce_animation(self):
        """Анимация подпрыгивания"""
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(400)
        
        current_pos = self.pos()
        anim.setKeyValues([
            (0.0, current_pos),
            (0.3, QPointF(current_pos.x(), current_pos.y() - 15)),
            (0.7, QPointF(current_pos.x(), current_pos.y() - 7)),
            (1.0, current_pos)
        ])
        
        anim.setEasingCurve(QEasingCurve.Type.OutBounce)
        anim.start()
        return anim
    
    def move_animation(self, new_x, new_y, duration=500):
        """Анимация перемещения"""
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(self.pos())
        anim.setEndValue(QPointF(new_x, new_y))
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        return anim
    
    def fade_in_animation(self, duration=300):
        """Анимация появления"""
        self.setOpacity(0)
        anim = QPropertyAnimation(self, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start()
        return anim
    
    def fade_out_animation(self, duration=300):
        """Анимация исчезновения"""
        anim = QPropertyAnimation(self, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.finished.connect(lambda: self.scene().removeItem(self))
        anim.start()
        return anim
    
    def hoverEnterEvent(self, event):
        """Обработка наведения мыши"""
        self.highlight()
        self.setToolTip(f"Индекс: {self.index}\nЗначение: {self.value}\nТип: {self.container_type}")
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Обработка ухода мыши"""
        self.is_highlighted = False
        self.operation_color = None
        self._update_appearance()
        super().hoverLeaveEvent(event)


class ContainerVisualizer:
    """Визуализатор контейнеров с полной анимацией и стилем как хэш-таблица"""
    
    def __init__(self, scene, container_type="stack"):
        self.scene = scene
        self.container_type = container_type
        self.elements = []  # Список графических элементов
        self.animations = []  # Активные анимации
        self.operations_log = []
        
        # Константы для отрисовки (как в хэш-таблице)
        self.ELEMENT_WIDTH = 300
        self.ELEMENT_HEIGHT = 70
        self.SPACING = 20
        
        # Позиционирование - теперь ближе к центру
        self.START_X = -150  # Ближе к центру
        self.START_Y = -150  # Ближе к центру
        
        # Цвета интерфейса
        self.BG_COLOR = QColor("#F8F9FA")
        self.TEXT_COLOR = QColor("#2c3e50")
        
        # Текстовые элементы
        self.title_text = None
        self.status_text = None
        self.info_text = None
        self.header_text = None
        
        # Создаем заголовок и таблицу
        self._create_interface()
    
    def _create_interface(self):
        """Создает интерфейс контейнера"""
        # Заголовок
        titles = {
            "stack": "📚 СТЕК (LIFO)",
            "queue": "📥 ОЧЕРЕДЬ (FIFO)",
            "deque": "🔄 ДЕК (Double Ended Queue)"
        }
        
        self.title_text = QGraphicsTextItem(titles[self.container_type])
        self.title_text.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.title_text.setDefaultTextColor(QColor("#2c3e50"))
        self.title_text.setPos(self.START_X, self.START_Y - 100)
        self.scene.addItem(self.title_text)
        
        # Заголовок таблицы
        self.header_text = QGraphicsTextItem("Структура данных:")
        self.header_text.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.header_text.setDefaultTextColor(QColor("#2c3e50"))
        self.header_text.setPos(self.START_X, self.START_Y - 50)
        self.scene.addItem(self.header_text)
        
        # Статусная строка
        self.status_text = QGraphicsTextItem("Готов к операциям...")
        self.status_text.setFont(QFont("Arial", 14))
        self.status_text.setDefaultTextColor(QColor("#5A9BD5"))
        self.status_text.setPos(self.START_X, self.START_Y + 350)  # Ниже
        self.scene.addItem(self.status_text)
        
        # Создаем начальную таблицу заголовков
        self._create_table_header()
        
        # Устанавливаем размер сцены для видимости
        self.scene.setSceneRect(-400, -300, 800, 600)
    
    def _create_table_header(self):
        """Создает заголовок таблицы"""
        index_width = 60
        value_width = self.ELEMENT_WIDTH - index_width
        
        # Фон шапки Индекс
        header_idx = QGraphicsRectItem(self.START_X, self.START_Y, index_width, 40)
        header_idx.setBrush(QBrush(QColor("#2c3e50")))
        header_idx.setPen(QPen(QColor("#ffffff"), 2))
        self.scene.addItem(header_idx)
        
        text_idx = QGraphicsTextItem("№")
        text_idx.setDefaultTextColor(Qt.GlobalColor.white)
        text_idx.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        text_idx.setPos(self.START_X + 15, self.START_Y + 10)
        self.scene.addItem(text_idx)
        
        # Фон шапки Значение
        header_val = QGraphicsRectItem(self.START_X + index_width, self.START_Y, value_width, 40)
        header_val.setBrush(QBrush(QColor("#34495e")))
        header_val.setPen(QPen(QColor("#ffffff"), 2))
        self.scene.addItem(header_val)
        
        text_val = QGraphicsTextItem("ЗНАЧЕНИЕ")
        text_val.setDefaultTextColor(Qt.GlobalColor.white)
        text_val.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        text_val.setPos(self.START_X + index_width + 100, self.START_Y + 10)
        self.scene.addItem(text_val)
    
    def clear(self):
        """Очищает визуализацию"""
        # Останавливаем анимации
        for anim in self.animations:
            try:
                anim.stop()
            except:
                pass
        self.animations.clear()
        
        # Удаляем элементы
        for elem in self.elements:
            try:
                self.scene.removeItem(elem)
            except:
                pass
        self.elements.clear()
        
        self._update_status("Структура очищена")
    
    def _update_status(self, message, is_error=False):
        """Обновляет статусную строку"""
        if self.status_text:
            self.status_text.setPlainText(message)
            color = QColor("#FF6B6B") if is_error else QColor("#5A9BD5")
            self.status_text.setDefaultTextColor(color)
    
    def _get_element_position(self, index):
        """Вычисляет позицию элемента по индексу"""
        x = self.START_X
        y = self.START_Y + 50 + index * (self.ELEMENT_HEIGHT + self.SPACING)  # +50 чтобы начать после заголовка
        return x, y
    
    def _animate_all_elements(self, start_index=0):
        """Анимирует перемещение всех элементов, начиная с start_index"""
        for i in range(start_index, len(self.elements)):
            elem = self.elements[i]
            target_x, target_y = self._get_element_position(i)
            
            if abs(elem.x() - target_x) > 1 or abs(elem.y() - target_y) > 1:
                anim = elem.move_animation(target_x, target_y, 300)
                self.animations.append(anim)
    
    def get_element_at_position(self, position="back"):
        """Возвращает элемент по позиции (для подсветки)"""
        if not self.elements:
            return None
        
        if position == "front":
            return self.elements[0]
        elif position == "back" or self.container_type == "stack":
            return self.elements[-1]
        
        return None
    
    def highlight_operation(self, operation_type, value=None, position="back"):
        """Подсвечивает операцию"""
        element = None
        
        if operation_type in ["push", "enqueue", "push_back"]:
            # Для добавления подсвечиваем последний элемент
            if self.elements:
                element = self.elements[-1] if position == "back" else self.elements[0]
        elif operation_type in ["pop", "dequeue", "pop_front", "pop_back"]:
            # Для удаления подсвечиваем элемент
            if self.elements:
                if position == "front":
                    element = self.elements[0]
                else:  # back
                    element = self.elements[-1]
        elif operation_type in ["peek", "front", "back"]:
            # Для просмотра
            if self.elements:
                if operation_type == "peek" or operation_type == "back":
                    element = self.elements[-1]
                else:  # front
                    element = self.elements[0]
        
        if element:
            color = {
                "push": "#4ECDC4",
                "pop": "#FF6B6B",
                "peek": "#FFD700",
                "enqueue": "#FF6B6B",
                "dequeue": "#5A9BD5",
                "front": "#FFD700",
                "back": "#FFA500"
            }.get(operation_type, "#FFA500")
            
            element.set_operating(True, color)
            element.bounce_animation()
            return True
        
        return False
    
    def push(self, value, position="back"):
        """Добавляет элемент в контейнер с анимацией"""
        # if len(self.elements) >= 8:  # Ограничение для визуализации
        #     self._update_status("❌ Контейнер переполнен!", True)
        #     return None
        
        # Определяем индекс для нового элемента
        if self.container_type == "stack" or position == "back":
            index = len(self.elements)  # В стек/очередь/конец дека - в конец
        else:  # push_front для дека
            index = 0
            # Сдвигаем все элементы вниз
            for elem in self.elements:
                elem.index += 1
                elem.index_text.setPlainText(str(elem.index))
        
        # Финальная позиция
        target_x, target_y = self._get_element_position(index)
        
        # Начальная позиция для анимации - видимая на экране
        if self.container_type == "stack":
            start_x, start_y = target_x, target_y - 200  # Сверху для стека
        elif position == "front":
            start_x, start_y = target_x - 200, target_y  # Слева для push_front
        else:
            start_x, start_y = target_x + 200, target_y  # Справа для очереди и push_back
        
        # Создаем элемент
        operation_color = {
            "stack": "#4ECDC4",
            "queue": "#FF6B6B",
            "deque": "#5A9BD5"
        }.get(self.container_type, "#5A9BD5")
        
        element = ContainerElement(
            value, start_x, start_y, 
            self.ELEMENT_WIDTH, self.ELEMENT_HEIGHT,
            self.container_type, index, operation_color
        )
        
        self.scene.addItem(element)
        
        if position == "front" and self.container_type == "deque":
            self.elements.insert(0, element)
        else:
            self.elements.append(element)
        
        # Обновляем индексы после вставки
        for i, elem in enumerate(self.elements):
            if elem != element:
                elem.index = i
                elem.index_text.setPlainText(str(i))
        
        # Анимация появления
        element.setOpacity(0)  # Начальная прозрачность
        element.set_operating(True, "#FFA500")
        
        # Сначала делаем элемент видимым
        fade_anim = element.fade_in_animation(300)
        
        # Затем анимация движения
        move_anim = element.move_animation(target_x, target_y, 600)
        move_anim.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        # Наконец подпрыгивание
        QTimer.singleShot(800, lambda: element.bounce_animation())
        
        self.animations.append(fade_anim)
        self.animations.append(move_anim)
        
        # Обновляем позиции других элементов
        QTimer.singleShot(300, lambda: self._animate_all_elements(0 if position == "front" else len(self.elements)-1))
        
        # Обновляем статус
        operations = {
            "stack": f"📥 Push({value}) - элемент добавлен сверху",
            "queue": f"📥 Enqueue({value}) - элемент добавлен в конец",
            "deque": f"➡️ Push_{position}({value})" if position == "back" else f"⬅️ Push_{position}({value})"
        }
        self._update_status(operations[self.container_type])
        
        # Центрируем вид
        QTimer.singleShot(900, self._center_view)
        
        return element
    
    def _center_view(self):
        """Центрирует вид на содержимом"""
        if self.scene:
            # Находим область с элементами
            items = [elem for elem in self.elements]
            if items:
                # Вычисляем bounding rect всех элементов
                rect = items[0].boundingRect()
                rect.translate(items[0].pos())
                for elem in items[1:]:
                    r = elem.boundingRect()
                    r.translate(elem.pos())
                    rect = rect.united(r)
                
                # Добавляем заголовок
                if self.title_text:
                    r = self.title_text.boundingRect()
                    r.translate(self.title_text.pos())
                    rect = rect.united(r)
                
                # Добавляем отступы
                rect.adjust(-100, -100, 100, 100)
                
                # Получаем view из сцены (нужно передавать view отдельно)
                # Эта функция будет вызываться из MainWindow
            
    def pop(self, position="back"):
        """Удаляет элемент из контейнера с анимацией"""
        if not self.elements:
            self._update_status("❌ Контейнер пуст!", True)
            return None
        
        # Определяем какой элемент удалять
        if self.container_type == "stack" or position == "back":
            index = len(self.elements) - 1
            element = self.elements.pop()
            value = element.value
        else:  # pop_front для дека или dequeue для очереди
            index = 0
            element = self.elements.pop(0)
            value = element.value
        
        # Подсвечиваем удаляемый элемент
        element.set_operating(True, "#FF6B6B")
        element.bounce_animation()
        
        # Определяем направление анимации исчезновения
        if self.container_type == "stack":
            target_x, target_y = element.x(), element.y() - 200  # Вверх для стека
        elif position == "front" or self.container_type == "queue":
            target_x, target_y = element.x() - 200, element.y()  # Влево
        else:
            target_x, target_y = element.x() + 200, element.y()  # Вправо
        
        # Ждем анимации подсветки, затем удаляем
        def perform_pop():
            # Анимация движения
            anim = element.move_animation(target_x, target_y, 500)
            anim.setEasingCurve(QEasingCurve.Type.InBack)
            self.animations.append(anim)
            
            # Анимация исчезновения
            fade_anim = element.fade_out_animation(400)
            self.animations.append(fade_anim)
            
            # Обновляем индексы оставшихся элементов
            for i, elem in enumerate(self.elements):
                elem.index = i
                elem.index_text.setPlainText(str(i))
            
            # Обновляем позиции оставшихся элементов
            QTimer.singleShot(100, lambda: self._animate_all_elements(0))
            
            # Обновляем статус
            operations = {
                "stack": f"📤 Pop() → {value} - элемент удален сверху",
                "queue": f"📤 Dequeue() → {value} - элемент удален из начала",
                "deque": f"➡️ Pop_{position}() → {value}" if position == "back" else f"⬅️ Pop_{position}() → {value}"
            }
            self._update_status(operations[self.container_type])
        
        # Запускаем удаление с задержкой
        QTimer.singleShot(500, perform_pop)
        
        return value
    
    def peek(self, position="front"):
        """Подсвечивает элемент для просмотра"""
        if not self.elements:
            self._update_status("❌ Контейнер пуст!", True)
            return None
        
        if self.container_type == "stack":
            element = self.elements[-1]
            value = element.value
            operation = "Peek (верхний)"
        elif self.container_type == "queue":
            if position == "front":
                element = self.elements[0]
                value = element.value
                operation = "Front (первый)"
            else:
                element = self.elements[-1]
                value = element.value
                operation = "Back (последний)"
        else:  # deque
            if position == "front":
                element = self.elements[0]
                value = element.value
                operation = "Front (начало)"
            else:
                element = self.elements[-1]
                value = element.value
                operation = "Back (конец)"
        
        # Подсвечиваем элемент
        element.set_operating(True, "#FFD700")
        element.bounce_animation()
        
        # Обновляем статус
        self._update_status(f"👁 {operation}: {value}")
        
        return value
    
    def get_size(self):
        """Возвращает размер контейнера"""
        size = len(self.elements)
        self._update_status(f"📊 Размер: {size} элементов")
        
        # Анимация всех элементов
        for elem in self.elements:
            elem.bounce_animation()
        
        return size
    
    def is_empty(self):
        """Проверяет, пуст ли контейнер"""
        is_empty = len(self.elements) == 0
        status = "пуст" if is_empty else "не пуст"
        self._update_status(f"📋 Контейнер {status}")
        
        if is_empty and self.title_text:
            # Анимация заголовка
            from PyQt6.QtCore import QPropertyAnimation
            anim = QPropertyAnimation(self.title_text, b"scale")
            anim.setDuration(500)
            anim.setStartValue(1.0)
            anim.setKeyValueAt(0.5, 1.1)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            anim.start()
            self.animations.append(anim)
        
        return is_empty
    
    def process_action(self, action):
        """Обрабатывает действие из алгоритма"""
        action_type = action.get("type", "")
        
        if action_type == "push":
            value = action.get("value")
            self.push(value)
            
        elif action_type == "pop":
            self.pop()
            
        elif action_type == "peek":
            self.peek()
            
        elif action_type == "enqueue":
            value = action.get("value")
            self.push(value)
            
        elif action_type == "dequeue":
            self.pop("front")
            
        elif action_type == "front":
            self.peek("front")
            
        elif action_type == "back":
            self.peek("back")
            
        elif action_type == "push_front":
            value = action.get("value")
            self.push(value, "front")
            
        elif action_type == "push_back":
            value = action.get("value")
            self.push(value, "back")
            
        elif action_type == "pop_front":
            self.pop("front")
            
        elif action_type == "pop_back":
            self.pop("back")
            
        elif action_type == "size":
            self.get_size()
            
        elif action_type == "is_empty":
            self.is_empty()
            
        elif action_type == "complete":
            self._update_status("✅ Все операции выполнены!")
            
        return True
    
    def get_container_info(self):
        """Возвращает информацию о контейнере"""
        values = [elem.value for elem in self.elements]
        
        info = {
            "type": self.container_type,
            "values": values,
            "size": len(values),
            "empty": len(values) == 0
        }
        
        if values:
            if self.container_type == "stack":
                info["top"] = values[-1]
            else:
                info["front"] = values[0]
                info["back"] = values[-1]
        
        return info
    
    def update_scene(self):
        """Обновляет сцену после операций."""
        if self.scene:
            self.scene.update()