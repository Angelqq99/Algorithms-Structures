from model.base_algorithm import BaseAlgorithm

class AVLTree(BaseAlgorithm):
    """AVL дерево (сбалансированное бинарное дерево поиска) с поддержкой визуализации."""
    
    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None
            self.height = 1
            self.parent = None

    def __init__(self, data):
        super().__init__(data)
        self.root = None

    def step_generator(self):
        """Генератор шагов для AVL дерева."""
        for val in self.data:
            self.root = self._insert(self.root, val, None)
            
            # Возвращаем текущее состояние дерева
            tree_structure = self._get_tree_structure(self.root)
            yield {
                "type": "tree",
                "tree_data": tree_structure,
                "description": f"Вставлен узел: {val} (AVL)"
            }
        
        # Обход inorder для демонстрации
        if self.root:
            inorder_values = self._inorder_traversal(self.root)
            yield {
                "type": "traversal",
                "nodes": inorder_values,
                "description": "In-order обход AVL дерева",
                "traversal_type": "inorder"
            }

        yield {
            "type": "complete",
            "description": "Построение AVL дерева завершено"
        }

    def _insert(self, node, value, parent):
        """Рекурсивная вставка в AVL дерево."""
        if node is None:
            new_node = self.Node(value)
            new_node.parent = parent
            return new_node
            
        if value < node.value:
            node.left = self._insert(node.left, value, node)
        else:
            node.right = self._insert(node.right, value, node)
            
        # Обновляем высоту
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        
        # Балансировка
        balance = self._get_balance(node)
        
        # Левый левый случай
        if balance > 1 and value < node.left.value:
            return self._rotate_right(node)
        
        # Правый правый случай
        if balance < -1 and value > node.right.value:
            return self._rotate_left(node)
        
        # Левый правый случай
        if balance > 1 and value > node.left.value:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        
        # Правый левый случай
        if balance < -1 and value < node.right.value:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
            
        return node

    def _get_height(self, node):
        if not node:
            return 0
        return node.height

    def _get_balance(self, node):
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _rotate_left(self, z):
        y = z.right
        T2 = y.left
        
        y.left = z
        z.right = T2
        
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        
        return y

    def _rotate_right(self, z):
        y = z.left
        T3 = y.right
        
        y.right = z
        z.left = T3
        
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        
        return y

    def _get_tree_structure(self, node):
        """Преобразует AVL дерево в структуру для визуализации."""
        if node is None:
            return None
            
        node_data = {
            'value': f"{node.value}(h:{node.height})",
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

