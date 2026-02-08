from model.base_algorithm import BaseAlgorithm
from collections import deque

class AVLTree(BaseAlgorithm):
    """AVL дерево с поддержкой интерактивных операций."""
    
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
        self._build_tree()

    def _build_tree(self):
        """Строит AVL дерево из начальных данных."""
        for val in self.data:
            self.insert(val)

    def step_generator(self):
        """Генератор шагов для AVL дерева."""
        yield {
            "type": "tree",
            "tree_data": self._get_tree_structure(self.root),
            "description": "Инициализация AVL дерева",
            "tree_type": "AVL"
        }
        
        for i, val in enumerate(self.data):
            self.root = self._insert_silent(self.root, val, None)
            
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure(self.root),
                "description": f"Вставлен узел: {val} (AVL, высота: {self._get_height(self.root)})",
                "tree_type": "AVL"
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
            "description": "Построение AVL дерева завершено",
            "tree_data": self._get_tree_structure(self.root)
        }

    def _insert_silent(self, node, value, parent):
        """Рекурсивная вставка в AVL дерево."""
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

    # ИНТЕРАКТИВНЫЕ ОПЕРАЦИИ
    
    def insert(self, value):
        """Публичный метод для интерактивной вставки."""
        self.root = self._insert_silent(self.root, value, None)
    
    def search(self, value):
        """Поиск значения в AVL дереве."""
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
        """Удаление значения из AVL дерева."""
        self.root = self._delete_recursive(self.root, value)
    
    def _delete_recursive(self, node, key):
        """Рекурсивное удаление с балансировкой."""
        if not node:
            return node
            
        if key < node.value:
            node.left = self._delete_recursive(node.left, key)
        elif key > node.value:
            node.right = self._delete_recursive(node.right, key)
        else:
            # Узел с одним или без детей
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            # Узел с двумя детьми
            temp = self._min_value_node(node.right)
            node.value = temp.value
            node.right = self._delete_recursive(node.right, temp.value)
        
        # Обновляем высоту и балансируем
        if node is None:
            return node
            
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)
        
        return self._rebalance_after_delete(node, balance)
    
    def _rebalance_after_delete(self, node, balance):
        """Балансировка после удаления."""
        # Левый левый случай
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._rotate_right(node)
        
        # Левый правый случай
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        
        # Правый правый случай
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._rotate_left(node)
        
        # Правый левый случай
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
            
        return node
    
    def _min_value_node(self, node):
        """Находит узел с минимальным значением."""
        current = node
        while current.left is not None:
            current = current.left
        return current
    
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
    
    def _find_min(self, node):
        """Находит минимальный узел в поддереве."""
        current = node
        while current.left is not None:
            current = current.left
        return current
    
    def _find_max(self, node):
        """Находит максимальный узел в поддереве."""
        current = node
        while current.right is not None:
            current = current.right
        return current
    
    def get_min(self):
        """Находит минимальное значение в дереве."""
        if not self.root:
            return None
        return self._find_min(self.root).value
    
    def get_max(self):
        """Находит максимальное значение в дереве."""
        if not self.root:
            return None
        return self._find_max(self.root).value
    
    def get_tree_height(self):
        """Возвращает высоту дерева."""
        return self._get_height(self.root)
    
    def is_balanced(self):
        """Проверяет, сбалансировано ли дерево."""
        def check_balance(node):
            if not node:
                return True, 0
            
            left_balanced, left_height = check_balance(node.left)
            right_balanced, right_height = check_balance(node.right)
            
            balanced = (left_balanced and right_balanced and 
                       abs(left_height - right_height) <= 1)
            height = 1 + max(left_height, right_height)
            
            return balanced, height
        
        balanced, _ = check_balance(self.root)
        return balanced

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