from model.base_algorithm import BaseAlgorithm

class SplayTree(BaseAlgorithm):
    """Splay-дерево с поддержкой визуализации."""
    
    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None
            self.parent = None

    def __init__(self, data):
        super().__init__(data)
        self.root = None

    def step_generator(self):
        """Генератор шагов для Splay-дерева."""
        for val in self.data:
            self.root = self._insert(self.root, val)
            self.root = self._splay(self.root, val)
            
            tree_structure = self._get_tree_structure(self.root)
            yield {
                "type": "tree",
                "tree_data": tree_structure,
                "description": f"Вставлен узел: {val} (Splay)"
            }
        
        if self.root:
            inorder_values = self._inorder_traversal(self.root)
            yield {
                "type": "traversal",
                "nodes": inorder_values,
                "description": "In-order обход Splay-дерева",
                "traversal_type": "inorder"
            }

        yield {
            "type": "complete",
            "description": "Построение Splay-дерева завершено"
        }

    def _insert(self, node, value, parent=None):
        """Вставка в Splay-дерево."""
        if node is None:
            new_node = self.Node(value)
            new_node.parent = parent
            return new_node
            
        if value < node.value:
            node.left = self._insert(node.left, value, node)
        elif value > node.value:
            node.right = self._insert(node.right, value, node)
            
        return node

    def _splay(self, node, value):
        """Splay операция - перемещает узел с заданным значением в корень."""
        if node is None or node.value == value:
            return node
            
        if value < node.value:
            if node.left is None:
                return node
                
            if value < node.left.value:
                node.left.left = self._splay(node.left.left, value)
                node = self._rotate_right(node)
            elif value > node.left.value:
                node.left.right = self._splay(node.left.right, value)
                if node.left.right:
                    node.left = self._rotate_left(node.left)
                    
            if node.left:
                return self._rotate_right(node)
            else:
                return node
                
        else:
            if node.right is None:
                return node
                
            if value < node.right.value:
                node.right.left = self._splay(node.right.left, value)
                if node.right.left:
                    node.right = self._rotate_right(node.right)
            elif value > node.right.value:
                node.right.right = self._splay(node.right.right, value)
                node = self._rotate_left(node)
                
            if node.right:
                return self._rotate_left(node)
            else:
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
            'value': node.value,
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
        return n * 6  # Вставка + splay операции