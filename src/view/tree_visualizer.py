"""
Визуализатор деревьев с анимациями.
"""
from PyQt6.QtCore import QTimer, QPropertyAnimation, pyqtProperty, QEasingCurve
from PyQt6.QtGui import QColor
from view.scene_items import TreeNodeItem, TreeConnectionItem
from view.tree_layout import CenteredTreeLayout, CompactTreeLayout


class TreeVisualizer:
    """Класс для визуализации деревьев с анимациями."""
    
    def __init__(self, scene):
        self.scene = scene
        self.nodes = []
        self.connections = []
        self.layout_algorithm = CenteredTreeLayout()
        self.value_to_node = {}  # Словарь для сопоставления значений и узлов
    
    def clear(self):
        """Очищает сцену от всех элементов дерева."""
        for connection in self.connections:
            self.scene.removeItem(connection)
        for node in self.nodes:
            self.scene.removeItem(node)
        
        self.nodes.clear()
        self.connections.clear()
        self.value_to_node.clear()  # Очищаем словарь
    
    def create_tree_from_structure(self, tree_structure, animate=True):
        """Создает дерево из структуры данных."""
        self.clear()
        
        if not tree_structure:
            return None
        
        # Создаем корневой узел
        root = self._create_node_from_data(tree_structure, 0, 0)
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
    
    def _create_node_from_data(self, node_data, x, y):
        """Создает TreeNodeItem из данных узла."""
        value = node_data.get('value', '?')
        node = TreeNodeItem(x, y, value)
        self.value_to_node[value] = node  # Сохраняем в словарь
        return node
    
    def _build_tree_recursive(self, parent_node, parent_data):
        """Рекурсивно строит дерево из данных."""
        children_data = parent_data.get('children', [])
        
        for child_data in children_data:
            child_node = self._create_node_from_data(child_data, 0, 0)
            parent_node.add_child(child_node)
            self.nodes.append(child_node)
            
            # Рекурсивно строим поддерево
            self._build_tree_recursive(child_node, child_data)
    
    def _create_connections(self, node):
        """Рекурсивно создает соединения между узлами."""
        for child in node.children:
            connection = TreeConnectionItem(node, child)
            self.connections.append(connection)
            self._create_connections(child)
    
    def _add_all_to_scene(self):
        """Добавляет все узлы и соединения на сцену."""
        for node in self.nodes:
            self.scene.addItem(node)
        for connection in self.connections:
            self.scene.addItem(connection)
    
    def animate_tree_construction(self, root, delay=300):
        """Анимирует построение дерева."""
        # Сначала добавляем все элементы на сцену невидимыми
        for node in self.nodes:
            node.setVisible(False)
            self.scene.addItem(node)
        
        for connection in self.connections:
            connection.setVisible(False)
            self.scene.addItem(connection)
        
        # Анимируем появление узлов и соединений
        self._animate_nodes_appearance(root, delay)
    
    def _animate_nodes_appearance(self, node, delay, current_delay=0):
        """Рекурсивно анимирует появление узлов."""
        if not node:
            return
        
        # Анимация появления узла
        QTimer.singleShot(current_delay, lambda n=node: self._animate_node_appearance(n))
        
        # Анимация соединений с детьми
        for child in node.children:
            connection_delay = current_delay + delay // 2
            QTimer.singleShot(connection_delay, 
                            lambda n=node, c=child: self._animate_connection_appearance(n, c))
            
            # Рекурсивно анимируем детей
            self._animate_nodes_appearance(child, delay, current_delay + delay)
    
    def _animate_node_appearance(self, node):
        """Анимирует появление узла."""
        node.setVisible(True)
        node.setScale(0.1)
        node.setOpacity(0.3)
        
        scale_anim = QPropertyAnimation(node, b"scale")
        scale_anim.setDuration(500)
        scale_anim.setStartValue(0.1)
        scale_anim.setEndValue(1.0)
        scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        
        opacity_anim = QPropertyAnimation(node, b"opacity")
        opacity_anim.setDuration(400)
        opacity_anim.setStartValue(0.3)
        opacity_anim.setEndValue(1.0)
        
        scale_anim.start()
        opacity_anim.start()
    
    def _animate_connection_appearance(self, parent, child):
        """Анимирует появление соединения."""
        # Находим соединение между родителем и ребенком
        connection = None
        for conn in self.connections:
            if conn.start_node == parent and conn.end_node == child:
                connection = conn
                break
        
        if connection:
            connection.setVisible(True)
    
    def highlight_traversal(self, node_values, delay=800):
        """Подсвечивает последовательность узлов по их значениям."""
        for i, value in enumerate(node_values):
            QTimer.singleShot(i * delay, lambda v=value: self._highlight_node_by_value(v))
    
    def _highlight_node_by_value(self, value):
        """Подсвечивает узел по значению."""
        node = self.value_to_node.get(value)
        if node:
            original_color = node.circleColor
            node.highlight(QColor("#FFD700"))
            
            # Возвращаем исходный цвет через некоторое время
            QTimer.singleShot(500, lambda: node.highlight(original_color))