from model.base_algorithm import BaseAlgorithm
from collections import deque

class SplayTree(BaseAlgorithm):
    """Splay-дерево с поддержкой интерактивных операций."""
    
    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None
            self.parent = None

    def __init__(self, data):
        super().__init__(data)
        self.root = None
        self._build_tree()

    def _build_tree(self):
        """Строит Splay-дерево из начальных данных."""
        for val in self.data:
            self.insert(val)

    def step_generator(self):
        """Генератор шагов для Splay-дерева."""
        yield {
            "type": "tree",
            "tree_data": self._get_tree_structure(self.root),
            "description": "Инициализация Splay-дерева",
            "tree_type": "SplayTree"
        }
        
        for i, val in enumerate(self.data):
            self.root = self._insert_silent(self.root, val)
            
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure(self.root),
                "description": f"Вставлен узел: {val} (Splay)",
                "tree_type": "SplayTree"
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
            "description": "Построение Splay-дерева завершено",
            "tree_data": self._get_tree_structure(self.root)
        }

    def _insert_silent(self, node, value, parent=None):
        """Вставка в Splay-дерево."""
        if node is None:
            new_node = self.Node(value)
            new_node.parent = parent
            return new_node
            
        # Проверка на дубликат
        if value == node.value:
            return node  # Игнорируем дубликат
            
        if value < node.value:
            node.left = self._insert_silent(node.left, value, node)
        elif value > node.value:
            node.right = self._insert_silent(node.right, value, node)
        
        # Splay операция для вставленного узла
        # Проверяем наличие детей перед сравнением
        if node.left and node.left.value == value:
            return self._rotate_right(node)
        elif node.right and node.right.value == value:
            return self._rotate_left(node)
            
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

    # ИНТЕРАКТИВНЫЕ ОПЕРАЦИИ
    
    def insert(self, value):
        """Публичный метод для интерактивной вставки."""
        self.root = self._insert_silent(self.root, value)
        # Поднимаем вставленный узел в корень
        node = self.search(value)
        if node:
            self.root = self._splay(node)
    
    def search(self, value):
        """Поиск значения в Splay-дереве с поднятием найденного узла в корень."""
        node = self._search_recursive(self.root, value)
        if node:
            self.root = self._splay(node)
        return node
    
    def _search_recursive(self, node, value):
        """Рекурсивный поиск значения."""
        if node is None or node.value == value:
            return node
            
        if value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)
    
    def _splay(self, x):
        """Поднимает узел x в корень дерева."""
        while x.parent:
            if not x.parent.parent:
                # Zig
                if x == x.parent.left:
                    self._rotate_right(x.parent)
                else:
                    self._rotate_left(x.parent)
            elif x == x.parent.left and x.parent == x.parent.parent.left:
                # Zig-Zig
                self._rotate_right(x.parent.parent)
                self._rotate_right(x.parent)
            elif x == x.parent.right and x.parent == x.parent.parent.right:
                # Zig-Zig
                self._rotate_left(x.parent.parent)
                self._rotate_left(x.parent)
            elif x == x.parent.right and x.parent == x.parent.parent.left:
                # Zig-Zag
                self._rotate_left(x.parent)
                self._rotate_right(x.parent)
            else:
                # Zig-Zag
                self._rotate_right(x.parent)
                self._rotate_left(x.parent)
        return x
    
    def delete(self, value):
        """Удаление значения из Splay-дерева."""
        node = self.search(value)
        if not node or node.value != value:
            return
            
        # Разделяем дерево
        left_tree = node.left
        right_tree = node.right
        
        if left_tree:
            left_tree.parent = None
        if right_tree:
            right_tree.parent = None
            
        if not left_tree:
            self.root = right_tree
        else:
            # Находим максимум в левом поддереве и поднимаем его
            max_left = left_tree
            while max_left.right:
                max_left = max_left.right
            self.root = self._splay(max_left)
            self.root.right = right_tree
            if right_tree:
                right_tree.parent = self.root
    
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
        """Находит минимальное значение в Splay-дереве."""
        if not self.root:
            return None
            
        current = self.root
        while current.left:
            current = current.left
        return current.value
    
    def get_max(self):
        """Находит максимальное значение в Splay-дереве."""
        if not self.root:
            return None
            
        current = self.root
        while current.right:
            current = current.right
        return current.value
    
    def get_height(self):
        """Возвращает высоту Splay-дерева."""
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