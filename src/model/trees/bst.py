from model.base_algorithm import BaseAlgorithm

class BST(BaseAlgorithm):
    """BST с поддержкой визуализации дерева."""
    
    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None
            self.parent = None

    def __init__(self, data):
        super().__init__(data)
        self.root = None
        self._insertion_order = []

    def step_generator(self):
        """Генератор шагов для BST с визуализацией."""
        for val in self.data:
            self.root = self._insert(self.root, val, None)
            self._insertion_order.append(val)
            
            # Возвращаем текущее состояние дерева
            tree_structure = self._get_tree_structure(self.root)
            yield {
                "type": "tree",
                "tree_data": tree_structure,
                "description": f"Вставлен узел: {val}"
            }
        
        # Обход inorder для демонстрации
        inorder_values = self._inorder_traversal(self.root)
        yield {
            "type": "traversal",
            "nodes": inorder_values,  # Передаем значения, а не узлы
            "description": "In-order обход дерева",
            "traversal_type": "inorder"
        }

        yield {
            "type": "complete",
            "description": "Построение BST завершено"
        }

    def _insert(self, node, value, parent):
        """Рекурсивная вставка в BST."""
        if node is None:
            new_node = self.Node(value)
            new_node.parent = parent
            return new_node
            
        if value < node.value:
            node.left = self._insert(node.left, value, node)
        else:
            node.right = self._insert(node.right, value, node)
            
        return node

    def _get_tree_structure(self, node):
        """Преобразует BST в структуру для визуализации."""
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
        result.append(node.value)  # Возвращаем значения, а не узлы
        result.extend(self._inorder_traversal(node.right))
        
        return result

    def _estimate_total_steps(self):
        """Оценка общего количества шагов."""
        n = len(self.data)
        return n * 3  # Вставка + обход