"""
Визуализатор деревьев с анимациями.
"""
from cmath import rect
from PyQt6.QtCore import QTimer, QPropertyAnimation, pyqtProperty, QEasingCurve, QRectF,Qt
from PyQt6.QtGui import QColor
from view.scene_items import TreeNodeItem, TreeConnectionItem
from view.tree_layout import CenteredTreeLayout, CompactTreeLayout


class TreeVisualizer:
    """Класс для визуализации деревьев с анимациями."""
    
    def __init__(self, scene):
        self.scene = scene
        self.nodes = []
        self.connections = []
        # Увеличены расстояния для больших узлов
        self.layout_algorithm = CenteredTreeLayout(x_spacing=850, y_spacing=850)
        self.value_to_node = {}  # Словарь для сопоставления значений и узлов
        self.current_tree_type = "BST"  # Тип текущего дерева
        self._auto_fit_view()
    
    def clear(self):
        """Очищает сцену от всех элементов дерева безопасно."""
        # Удаляем соединения
        for connection in self.connections:
            try:
                if connection and connection.scene():
                    self.scene.removeItem(connection)
            except RuntimeError:
                pass  # Объект уже удален
        
        # Удаляем узлы
        for node in self.nodes:
            try:
                if node and node.scene():
                    self.scene.removeItem(node)
            except RuntimeError:
                pass  # Объект уже удален
        
        self.nodes.clear()
        self.connections.clear()
        self.value_to_node.clear()
    
    def set_tree_type(self, tree_type):
        """Устанавливает тип дерева для цветового кодирования."""
        self.current_tree_type = tree_type
    
    def create_tree_from_structure(self, tree_structure, animate=True):
        """Создает дерево из структуры данных."""
        self.clear()
        
        if not tree_structure:
            return None
        
        try:
            # Устанавливаем большой размер сцены для больших узлов
            rect = self.scene.itemsBoundingRect()
            self.scene.setSceneRect(rect.adjusted(-500, -500, 500, 500))
            
            # Создаем корневой узел
            root = self._create_node_from_data(tree_structure, 0, 0)
            if not root:
                return None
                
            self.nodes.append(root)
            self.value_to_node[tree_structure['value']] = root
            
            # Рекурсивно создаем остальные узлы
            self._build_tree_recursive(root, tree_structure)
            
            # Вычисляем расположение
            self.layout_algorithm.calculate_layout(root)
            
            # Добавляем соединения
            self._create_connections(root)
            
            # Анимируем построение
            if animate:
                self.animate_tree_construction(root)
            else:
                self._add_all_to_scene()
            
            return root
        except Exception as e:
            print(f"Ошибка при создании дерева: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_node_from_data(self, node_data, x, y):
        """Создает TreeNodeItem из данных узла."""
        try:
            value = node_data.get('value', '?')
            
            # Определяем цвет в зависимости от типа дерева и данных узла
            tree_type = self.current_tree_type
            if "(" in str(value) and ")" in str(value):
                # Для узлов с дополнительной информацией (AVL, RBT и т.д.)
                if "R)" in str(value) or "(R" in str(value):
                    tree_type = "RedBlackTree_RED"
                elif "B)" in str(value) or "(B" in str(value):
                    tree_type = "RedBlackTree_BLACK"
                elif "h:" in str(value):
                    tree_type = "AVL"
                elif "p:" in str(value):
                    tree_type = "Treap"
            
            # Создаем узел с увеличенным радиусом
            node = TreeNodeItem(x, y, value, radius=95)
            
            # Устанавливаем цвет в зависимости от типа дерева
            node.set_tree_type_color(tree_type)
            
            # Сохраняем узел в словарь по значению
            self.value_to_node[value] = node
            return node
        except Exception as e:
            print(f"Ошибка при создании узла: {e}")
            return None
    
    def _build_tree_recursive(self, parent_node, parent_data):
        """Рекурсивно строит дерево из данных."""
        if not parent_node:
            return
            
        children_data = parent_data.get('children', [])
        
        for child_data in children_data:
            child_node = self._create_node_from_data(child_data, 0, 0)
            if child_node:
                parent_node.add_child(child_node)
                self.nodes.append(child_node)
                
                # Рекурсивно строим поддерево
                self._build_tree_recursive(child_node, child_data)
    
    def _create_connections(self, node):
        """Рекурсивно создает соединения между узлами."""
        if not node:
            return
            
        for child in node.children:
            if child and hasattr(child, 'scenePos'):  # Проверяем, что child не None и валиден
                try:
                    connection = TreeConnectionItem(node, child)
                    # начинаем с нулевой непрозрачности
                    connection.setOpacity(0.0)
                    self.connections.append(connection)
                    self._create_connections(child)
                except Exception as e:
                    print(f"Ошибка при создании соединения: {e}")
    
    def _add_all_to_scene(self):
        """Добавляет все узлы и соединения на сцену."""
        # Сначала добавляем все узлы
        for node in self.nodes:
            try:
                if node and node.scene() != self.scene and hasattr(node, 'setVisible'):
                    self.scene.addItem(node)
                    node.setVisible(True)
            except Exception:
                # безопасно продолжаем
                pass
        
        # Затем добавляем соединения
        for connection in self.connections:
            try:
                if connection and connection.scene() != self.scene:
                    self.scene.addItem(connection)
                    connection.setVisible(True)
                    connection.setOpacity(1.0)
            except Exception:
                pass
    
    def animate_tree_construction(self, root, delay=360):
        """Анимирует построение дерева."""
        if not root or not hasattr(root, 'setVisible'):
            return
            
        # Сначала добавляем все элементы на сцену невидимыми
        for node in self.nodes:
            try:
                if node and hasattr(node, 'setVisible'):
                    node.setVisible(False)
                    if node.scene() != self.scene:
                        self.scene.addItem(node)
            except Exception:
                pass
        
        for connection in self.connections:
            try:
                connection.setVisible(False)
                if connection.scene() != self.scene:
                    self.scene.addItem(connection)
            except Exception:
                pass
        
        # Анимируем появление узлов и соединений
        self._animate_nodes_appearance(root, delay)
    
    def _animate_nodes_appearance(self, node, delay, current_delay=0):
        """Рекурсивно анимирует появление узлов."""
        if not node or not hasattr(node, 'setVisible'):
            return
        
        # Анимация появления узла
        QTimer.singleShot(current_delay, lambda n=node: self._safe_animate_node_appearance(n))
        
        # Анимация соединений с детьми
        for child in node.children:
            if child and hasattr(child, 'scenePos'):  # Проверяем, что child валиден
                connection_delay = current_delay + int(delay * 0.5)
                QTimer.singleShot(connection_delay, 
                                lambda n=node, c=child: self._safe_animate_connection_appearance(n, c))
                
                # Рекурсивно анимируем детей
                self._animate_nodes_appearance(child, delay, current_delay + delay)
    
    def _safe_animate_node_appearance(self, node):
        """Безопасная анимация появления узла."""
        try:
            self._animate_node_appearance(node)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                print("Предупреждение: узел был удален до анимации")
                return
            raise e
    
    def _animate_node_appearance(self, node):
        """Анимирует появление узла."""
        if not node:
            return
            
        try:
            # Проверяем, что объект еще существует
            if not hasattr(node, 'setVisible'):
                return
                
            node.setVisible(True)
            node.setScale(0.1)
            node.setOpacity(0.0)
            
            # Храним анимации в самом узле, чтобы GC их не удалил
            scale_anim = QPropertyAnimation(node, b"scale")
            scale_anim.setDuration(700)
            scale_anim.setStartValue(0.1)
            scale_anim.setEndValue(1.0)
            scale_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            opacity_anim = QPropertyAnimation(node, b"opacity")
            opacity_anim.setDuration(700)
            opacity_anim.setStartValue(0.0)
            opacity_anim.setEndValue(1.0)
            opacity_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            
            # сохраняем ссылки
            if not hasattr(node, "_entry_anims"):
                node._entry_anims = []
            node._entry_anims.extend([scale_anim, opacity_anim])
            
            scale_anim.start()
            opacity_anim.start()
            
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                print("Предупреждение: попытка анимировать удаленный объект")
                return
            raise e
        except Exception as e:
            print(f"Ошибка при анимации узла: {e}")
    
    def _safe_animate_connection_appearance(self, parent, child):
        """Безопасная анимация появления соединения."""
        try:
            self._animate_connection_appearance(parent, child)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                print("Предупреждение: соединение было удалено до анимации")
                return
            raise e
    
    def _animate_connection_appearance(self, parent, child):
        """Анимирует появление соединения (fade-in)."""
        if not parent or not child or not hasattr(parent, 'scenePos') or not hasattr(child, 'scenePos'):
            return
            
        # Находим соединение между родителем и ребенком
        connection = None
        for conn in self.connections:
            if (conn and conn.start_node == parent and conn.end_node == child and
                hasattr(conn, 'setVisible')):
                connection = conn
                break
        
        if connection:
            try:
                connection.setVisible(True)
                # плавный fade-in
                anim = QPropertyAnimation(connection, b"opacity")
                anim.setDuration(520)
                anim.setStartValue(0.0)
                anim.setEndValue(1.0)
                anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
                # сохраняем в объекте connection, чтобы анимация не уничтожилась
                if not hasattr(connection, "_fade_anims"):
                    connection._fade_anims = []
                connection._fade_anims.append(anim)
                anim.start()
            except RuntimeError as e:
                if "wrapped C/C++ object" in str(e):
                    print("Предупреждение: соединение удалено")
                    return
                raise e
            except Exception as e:
                print(f"Ошибка при показе соединения: {e}")
    
    def highlight_traversal(self, node_values, delay=900):
        """Подсвечивает последовательность узлов по их значениям."""
        for i, value in enumerate(node_values):
            QTimer.singleShot(i * delay, lambda v=value: self._safe_highlight_node_by_value(v))
    
    def _safe_highlight_node_by_value(self, value):
        """Безопасная подсветка узла по значению."""
        try:
            self._highlight_node_by_value(value)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                print("Предупреждение: узел удален до подсветки")
                return
            raise e
    
    def _highlight_node_by_value(self, value):
        """Подсвечивает узел по значению."""
        try:
            node = self.value_to_node.get(value)
            if node and node.scene() and hasattr(node, 'highlight'):  # Проверяем, что узел все еще на сцене
                original_color = node.circleColor
                node.highlight(QColor("#FFD700"))
                
                # Возвращаем исходный цвет через некоторое время
                QTimer.singleShot(600, lambda: self._safe_reset_node_color(node, original_color))
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                return
            raise e
        except Exception as e:
            print(f"Ошибка при подсветке узла: {e}")
    
    def _safe_reset_node_color(self, node, color):
        """Безопасный сброс цвета узла."""
        try:
            self._reset_node_color(node, color)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                return
            raise e
    
    def _reset_node_color(self, node, color):
        """Сбрасывает цвет узла."""
        try:
            if node and node.scene() and hasattr(node, 'highlight'):  # Проверяем, что узел все еще на сцене
                node.highlight(color)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                return
            raise e
        except Exception as e:
            print(f"Ошибка при сбросе цвета узла: {e}")
    
    def _auto_fit_view(self):
        """Автоматическое подгонка вида (вызывается только при инициализации)."""
        view = self.scene.views()[0] if self.scene.views() else None
        if not view:
            return
        
        rect = self.scene.itemsBoundingRect()
        if rect.isValid():
            rect.adjust(-200, -200, 200, 200)  # небольшой паддинг
            view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)