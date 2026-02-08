import random
from model.base_algorithm import BaseAlgorithm
from collections import deque

class Treap(BaseAlgorithm):
    """Treap (дерево + куча) с поддержкой интерактивных операций."""
    
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
        self._build_tree()

    def _build_tree(self):
        """Строит Treap из начальных данных."""
        for val in self.data:
            self.insert(val)

    def step_generator(self):
        """Генератор шагов для Treap."""
        yield {
            "type": "tree",
            "tree_data": self._get_tree_structure(self.root),
            "description": "Инициализация Treap",
            "tree_type": "Treap"
        }
        
        for i, val in enumerate(self.data):
            priority = random.randint(1, 100)
            self.root = self._insert_silent(self.root, val, priority, None)
            
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure(self.root),
                "description": f"Вставлен узел: {val} (приоритет: {priority})",
                "tree_type": "Treap"
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
            "description": "Построение Treap завершено",
            "tree_data": self._get_tree_structure(self.root)
        }

    def _insert_silent(self, node, value, priority, parent):
        """Вставка в Treap."""
        if node is None:
            new_node = self.Node(value, priority)
            new_node.parent = parent
            return new_node
            
        # Исправлено: строгое меньше для предотвращения дубликатов
        if value < node.value:  # Было value <= node.value
            node.left = self._insert_silent(node.left, value, priority, node)
            if node.left.priority > node.priority:
                node = self._rotate_right(node)
        else:
            # Если значение равно существующему, игнорируем дубликат
            if value == node.value:
                return node
            node.right = self._insert_silent(node.right, value, priority, node)
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
            'value': f"{node.value}\n[p:{node.priority}]",
            'children': [],
            'properties': {
                'value': node.value,
                'priority': node.priority,
                'node_type': 'TreapNode'
            }
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
        priority = random.randint(1, 100)
        self.root = self._insert_silent(self.root, value, priority, None)
    
    def search(self, value):
        """Поиск значения в Treap."""
        return self._search_recursive(self.root, value)
    
    def _search_recursive(self, node, value):
        """Рекурсивный поиск значения."""
        if node is None or node.value == value:
            return node
            
        if value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)
    
    def delete(self, value):
        """Удаление значения из Treap."""
        self.root = self._delete_treap(self.root, value)
    
    def _delete_treap(self, node, key):
        """Рекурсивное удаление из Treap."""
        if not node:
            return None
            
        if key < node.value:
            node.left = self._delete_treap(node.left, key)
        elif key > node.value:
            node.right = self._delete_treap(node.right, key)
        else:
            # Удаляем текущий узел
            return self._merge(node.left, node.right)
        return node
    
    def _merge(self, left, right):
        """Слияние двух поддеревьев."""
        if not left or not right:
            return left or right
            
        if left.priority > right.priority:
            left.right = self._merge(left.right, right)
            if left.right:
                left.right.parent = left
            return left
        else:
            right.left = self._merge(left, right.left)
            if right.left:
                right.left.parent = right
            return right
    
    # ОБХОДЫ ДЕРЕВА
    def get_preorder(self):
        """Прямой обход (КЛП)."""
        return self._preorder_recursive(self.root)
    
    def _preorder_recursive(self, node):
        if node is None:
            return []
        return [node.value] + self._preorder_recursive(node.left) + self._preorder_recursive(node.right)
    
    def get_inorder(self):
        """Центральный обход (ЛКП)."""
        return self._inorder_traversal(self.root)
    
    def get_postorder(self):
        """Обратный обход (ЛПК)."""
        return self._postorder_recursive(self.root)
    
    def _postorder_recursive(self, node):
        if node is None:
            return []
        return self._postorder_recursive(node.left) + self._postorder_recursive(node.right) + [node.value]
    
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
        """Находит минимальное значение в Treap."""
        if not self.root:
            return None
            
        current = self.root
        while current.left:
            current = current.left
        return current.value
    
    def get_max(self):
        """Находит максимальное значение в Treap."""
        if not self.root:
            return None
            
        current = self.root
        while current.right:
            current = current.right
        return current.value
    
    def get_height(self):
        """Возвращает высоту Treap."""
        def calculate_height(node):
            if not node:
                return 0
            return 1 + max(calculate_height(node.left), calculate_height(node.right))
        
        return calculate_height(self.root)

    def _estimate_total_steps(self):
        """Оценка общего количества шагов."""
        n = len(self.data)
        return n * 2
    def _search_with_path(self, node, value, path=None):
        """Рекурсивный поиск с отслеживанием пути."""
        if path is None:
            path = []
        
        if node is None:
            path.append("Достигнут лист - значение не найдено")
            return None, path
        
        path.append(f"Узел: {node.value}")
        
        if value == node.value:
            return node, path
        
        elif value < node.value:
            path.append("Идем в левое поддерево")
            return self._search_with_path(node.left, value, path)
        
        else:
            path.append("Идем в правое поддерево")
            return self._search_with_path(node.right, value, path)