"""
Алгоритмы для расчета расположения узлов дерева.
"""
from PyQt6.QtCore import QPointF, QTimer
import math


class TreeLayout:
    """Базовый класс для алгоритмов расположения деревьев."""
    
    def __init__(self, x_spacing=180, y_spacing=150):  # Увеличены расстояния для больших узлов
        self.x_spacing = x_spacing
        self.y_spacing = y_spacing
    
    def calculate_layout(self, root_node):
        raise NotImplementedError("Subclasses must implement this method")


class CenteredTreeLayout(TreeLayout):
    """Вертикальное центрированное дерево."""
    
    def calculate_layout(self, root_node):
        """Вычисляет позиции для центрированного дерева."""
        # Сначала вычисляем размеры поддеревьев
        self._calculate_subtree_sizes(root_node)
        
        # Затем вычисляем позиции
        initial_x = 0
        initial_y = 0
        self._layout_subtree(root_node, initial_x, initial_y)
    
    def _calculate_subtree_sizes(self, node):
        """Рекурсивно вычисляет размеры поддеревьев."""
        if not node.children:
            node.subtree_width = 1
            return 1
        
        total_width = 0
        for child in node.children:
            child_width = self._calculate_subtree_sizes(child)
            total_width += child_width
        
        node.subtree_width = total_width
        return total_width
    
    def _layout_subtree(self, node, center_x, y):
        """Рекурсивно располагает узлы поддерева."""
        node.setPos(center_x, y)
        
        if not node.children:
            return
        
        # Вычисляем начальную позицию для детей
        total_child_width = node.subtree_width * self.x_spacing
        start_x = center_x - total_child_width / 2 + self.x_spacing / 2
        
        current_x = start_x
        for child in node.children:
            child_center = current_x + (child.subtree_width * self.x_spacing) / 2 - self.x_spacing / 2
            self._layout_subtree(child, child_center, y + self.y_spacing)
            current_x += child.subtree_width * self.x_spacing


class CompactTreeLayout(TreeLayout):
    """Компактное расположение дерева."""
    
    def calculate_layout(self, root_node):
        """Вычисляет позиции для компактного дерева."""
        positions = {}
        levels = {}
        
        # Сначала собираем узлы по уровням
        self._collect_nodes_by_level(root_node, 0, levels)
        
        # Вычисляем позиции для каждого уровня
        max_level = max(levels.keys()) if levels else 0
        
        for level in range(max_level + 1):
            nodes_in_level = levels.get(level, [])
            level_width = len(nodes_in_level) * self.x_spacing
            start_x = -level_width / 2
            
            for i, node in enumerate(nodes_in_level):
                x = start_x + i * self.x_spacing
                y = level * self.y_spacing
                positions[node] = QPointF(x, y)
        
        # Устанавливаем позиции
        for node, pos in positions.items():
            node.setPos(pos)
    
    def _collect_nodes_by_level(self, node, level, levels_dict):
        """Рекурсивно собирает узлы по уровням."""
        if level not in levels_dict:
            levels_dict[level] = []
        levels_dict[level].append(node)
        
        for child in node.children:
            self._collect_nodes_by_level(child, level + 1, levels_dict)