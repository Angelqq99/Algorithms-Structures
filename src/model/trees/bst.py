from model.base_algorithm import BaseAlgorithm
from collections import deque

class BST(BaseAlgorithm):
    """Бинарное дерево поиска с поддержкой интерактивных операций."""
    
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
        self._build_tree()

    def _build_tree(self):
        """Строит BST из начальных данных."""
        for val in self.data:
            self.insert(val)

    def step_generator(self):
        """Генератор шагов для BST с визуализацией."""
        yield {
            "type": "tree",
            "tree_data": self._get_tree_structure(self.root),
            "description": "Инициализация бинарного дерева поиска",
            "tree_type": "BST"
        }
        
        for i, val in enumerate(self.data):
            self.root = self._insert_silent(self.root, val, None)
            self._insertion_order.append(val)
            
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure(self.root),
                "description": f"Вставлен узел: {val}",
                "tree_type": "BST"
            }
        
        # Обход inorder для демонстрации
        if self.root:
            inorder_values = self._inorder_traversal(self.root)
            yield {
                "type": "traversal",
                "nodes": inorder_values,
                "description": "In-order обход дерева",
                "traversal_type": "inorder"
            }

        yield {
            "type": "complete",
            "description": "Построение BST завершено",
            "tree_data": self._get_tree_structure(self.root)
        }

    def _insert_silent(self, node, value, parent):
        """Рекурсивная вставка в BST."""
        if node is None:
            new_node = self.Node(value)
            new_node.parent = parent
            return new_node
            
        # Проверка на дубликат
        if value == node.value:
            return node  # Игнорируем дубликат
            
        if value < node.value:
            node.left = self._insert_silent(node.left, value, node)
        else:
            node.right = self._insert_silent(node.right, value, node)
            
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
        result.append(node.value)
        result.extend(self._inorder_traversal(node.right))
        
        return result

    # ИНТЕРАКТИВНЫЕ ОПЕРАЦИИ
    
    def insert(self, value):
        """Публичный метод для интерактивной вставки."""
        self.root = self._insert_silent(self.root, value, None)
        self._insertion_order.append(value)
    
    def search(self, value):
        """Поиск значения в дереве."""
        return self._search(self.root, value)

    def _search(self, node, value):
        """Рекурсивный поиск значения."""
        if node is None or node.value == value:
            return node
            
        if value < node.value:
            return self._search(node.left, value)
        else:
            return self._search(node.right, value)

    def delete(self, value):
        """Удаление значения из BST."""
        self.root = self._delete_recursive(self.root, value)
    
    def _delete_recursive(self, node, key):
        """Рекурсивное удаление значения."""
        if not node:
            return node
            
        if key < node.value:
            node.left = self._delete_recursive(node.left, key)
        elif key > node.value:
            node.right = self._delete_recursive(node.right, key)
        else:
            # Узел с одним или без детей
            if not node.left:
                return node.right
            if not node.right:
                return node.left
            # Узел с двумя детьми
            temp = self._min_value_node(node.right)
            node.value = temp.value
            node.right = self._delete_recursive(node.right, temp.value)
        return node
    
    def _min_value_node(self, node):
        """Находит узел с минимальным значением."""
        current = node
        while current.left:
            current = current.left
        return current
    
    # ОБХОДЫ ДЕРЕВА
    def get_preorder(self):
        """Прямой обход (КЛП)."""
        return self._preorder_traversal(self.root)
    
    def _preorder_traversal(self, node):
        if node is None:
            return []
        
        result = [node.value]
        result.extend(self._preorder_traversal(node.left))
        result.extend(self._preorder_traversal(node.right))
        
        return result
    
    def get_inorder(self):
        """Центральный обход (ЛКП)."""
        return self._inorder_traversal(self.root)
    
    def get_postorder(self):
        """Обратный обход (ЛПК)."""
        return self._postorder_traversal(self.root)
    
    def _postorder_traversal(self, node):
        if node is None:
            return []
        
        result = []
        result.extend(self._postorder_traversal(node.left))
        result.extend(self._postorder_traversal(node.right))
        result.append(node.value)
        
        return result
    
    def get_bfs(self):
        """Поиск в ширину (BFS)."""
        if not self.root:
            return []
        
        result = []
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            result.append(node.value)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        return result
    
    # ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ
    
    def get_min(self):
        """Находит минимальное значение в дереве."""
        if not self.root:
            return None
        return self._min_value_node(self.root).value
    
    def get_max(self):
        """Находит максимальное значение в дереве."""
        if not self.root:
            return None
            
        current = self.root
        while current.right:
            current = current.right
        return current.value
    
    def get_height(self):
        """Возвращает высоту дерева."""
        def calculate_height(node):
            if not node:
                return 0
            return 1 + max(calculate_height(node.left), calculate_height(node.right))
        
        return calculate_height(self.root)
    
    def is_bst(self):
        """Проверяет, является ли дерево BST."""
        def is_bst_util(node, min_val, max_val):
            if not node:
                return True
            
            if node.value < min_val or node.value > max_val:
                return False
            
            return (is_bst_util(node.left, min_val, node.value - 1) and
                    is_bst_util(node.right, node.value + 1, max_val))
        
        return is_bst_util(self.root, float('-inf'), float('inf'))

    def _estimate_total_steps(self):
        """Оценка общего количества шагов."""
        n = len(self.data)
        return n * 3