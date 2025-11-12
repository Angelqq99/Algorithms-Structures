import random
from model.base_algorithm import BaseAlgorithm

class Treap(BaseAlgorithm):
    """Treap (дерево + куча) с поддержкой визуализации."""
    
    class Node:
        def __init__(self, value, priority):
            self.value = value
            self.priority = priority
            self.left = None
            self.right = None
            self.parent = None

    def __init__(self, data):
        super().__init__(data)
        self.root = None

    def step_generator(self):
        """Генератор шагов для Treap."""
        for val in self.data:
            priority = random.randint(1, 100)
            self.root = self._insert(self.root, val, priority)
            
            tree_structure = self._get_tree_structure(self.root)
            yield {
                "type": "tree",
                "tree_data": tree_structure,
                "description": f"Вставлен узел: {val} (приоритет: {priority})"
            }
        
        if self.root:
            inorder_values = self._inorder_traversal(self.root)
            yield {
                "type": "traversal",
                "nodes": inorder_values,
                "description": "In-order обход Treap",
                "traversal_type": "inorder"
            }

        yield {
            "type": "complete",
            "description": "Построение Treap завершено"
        }

    def _insert(self, node, value, priority, parent=None):
        """Вставка в Treap."""
        if node is None:
            new_node = self.Node(value, priority)
            new_node.parent = parent
            return new_node
            
        if value <= node.value:
            node.left = self._insert(node.left, value, priority, node)
            if node.left.priority > node.priority:
                node = self._rotate_right(node)
        else:
            node.right = self._insert(node.right, value, priority, node)
            if node.right.priority > node.priority:
                node = self._rotate_left(node)
                
        return node

    def _rotate_left(self, x):
        """Левый поворот."""
        y = x.right
        x.right = y.left
        if y.left:
            y.left.parent = x
        y.parent = x.parent
        y.left = x
        x.parent = y
        return y

    def _rotate_right(self, y):
        """Правый поворот."""
        x = y.left
        y.left = x.right
        if x.right:
            x.right.parent = y
        x.parent = y.parent
        x.right = y
        y.parent = x
        return x

    def _get_tree_structure(self, node):
        """Преобразует дерево в структуру для визуализации."""
        if node is None:
            return None
            
        node_data = {
            'value': f"{node.value}(p:{node.priority})",
            'children': []
        }
        
        if node.left:
            left_data = self._get_tree_structure(node.left)
            if left_data:
                node_data['children'].append(left_data)
                
        if node.right:
            right_data = self._get_tree_structure(node.right)
            if right_data:
                node_data['children'].append(right_data)
                
        return node_data

    def _inorder_traversal(self, node):
        """In-order обход дерева."""
        if node is None:
            return []
        
        result = []
        result.extend(self._inorder_traversal(node.left))
        result.append(node.value)
        result.extend(self._inorder_traversal(node.right))
        
        return result

    def _estimate_total_steps(self):
        """Оценка общего количества шагов."""
        n = len(self.data)
        return n * 4  # Вставка + балансировка

