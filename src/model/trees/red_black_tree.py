from model.base_algorithm import BaseAlgorithm
from collections import deque

class RedBlackTree(BaseAlgorithm):
    """Красно-черное дерево с поддержкой визуализации и правильной балансировкой."""
    
    class Node:
        def __init__(self, value, color='RED'):
            self.value = value
            self.left = None
            self.right = None
            self.parent = None
            self.color = color  # 'RED' or 'BLACK'
            
        def is_nil(self):
            return self.value is None

    def __init__(self, data):
        super().__init__(data)
        # Используем один NIL-узел для всех листьев
        self.NIL = self.Node(None, 'BLACK')
        self.NIL.left = self.NIL
        self.NIL.right = self.NIL
        self.NIL.parent = self.NIL
        
        self.root = self.NIL
        if data:
            self._build_tree()

    def _build_tree(self):
        """Строит красно-черное дерево из начальных данных."""
        processed = set()
        for val in self.data:
            if val in processed:
                continue
            processed.add(val)
            
            new_node = self.Node(val, 'RED')
            new_node.left = self.NIL
            new_node.right = self.NIL
            new_node.parent = self.NIL
            
            self._bst_insert_silent(new_node)
            self._fix_insert_silent(new_node)

    def step_generator(self):
        """Генератор шагов для красно-черного дерева с детальной балансировкой."""
        processed = set()
        
        for val in self.data:
            if val in processed:
                continue
            processed.add(val)
            
            # Создаем новый узел
            new_node = self.Node(val, 'RED')
            new_node.left = self.NIL
            new_node.right = self.NIL
            new_node.parent = self.NIL
            
            # Показываем начальное состояние
            yield {
                "type": "info",
                "description": f"Вставляем значение {val} в красно-черное дерево"
            }
            
            # BST вставка
            self._bst_insert_silent(new_node)
            
            # Показываем дерево после вставки
            tree_structure = self._get_tree_structure(self.root)
            yield {
                "type": "tree",
                "tree_data": tree_structure,
                "description": f"BST вставка: {val}"
            }
            
            # Балансировка
            self._fix_insert_silent(new_node)
            
            # Показываем финальное состояние после балансировки
            tree_structure = self._get_tree_structure(self.root)
            yield {
                "type": "tree",
                "tree_data": tree_structure,
                "description": f"Балансировка: {val}"
            }
        
        # Обход inorder для демонстрации
        if self.root != self.NIL:
            inorder_values = self._inorder_traversal(self.root)
            yield {
                "type": "traversal",
                "nodes": inorder_values,
                "description": "In-order обход красно-черного дерева",
                "traversal_type": "inorder"
            }

        yield {
            "type": "complete",
            "description": "Построение красно-черного дерева завершено"
        }

    def _bst_insert_silent(self, new_node):
        """BST вставка нового узла (без yield для генератора)."""
        if self.root == self.NIL:
            self.root = new_node
            self.root.color = 'BLACK'
            return
            
        current = self.root
        parent = self.NIL
        
        while current != self.NIL:
            # Проверка на дубликат
            if new_node.value == current.value:
                return  # Игнорируем дубликат
                
            parent = current
            if new_node.value < current.value:
                current = current.left
            else:
                current = current.right
                
        new_node.parent = parent
        
        if new_node.value < parent.value:
            parent.left = new_node
        else:
            parent.right = new_node

    def _fix_insert_silent(self, node):
        """Балансировка после вставки (без yield для генератора)."""
        while node != self.root and node.parent.color == 'RED':
            # Проверяем, что parent.parent существует
            if node.parent.parent == self.NIL:
                break
                
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                
                # Случай 1: дядя красный
                if uncle.color == 'RED':
                    node.parent.color = 'BLACK'
                    uncle.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    node = node.parent.parent
                else:
                    # Случай 2: узел - правый ребенок
                    if node == node.parent.right:
                        node = node.parent
                        self._left_rotate(node)
                    
                    # Случай 3: узел - левый ребенок
                    node.parent.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    self._right_rotate(node.parent.parent)
            else:
                # Симметричный случай для правого поддерева
                uncle = node.parent.parent.left
                
                # Случай 1: дядя красный
                if uncle.color == 'RED':
                    node.parent.color = 'BLACK'
                    uncle.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    node = node.parent.parent
                else:
                    # Случай 2: узел - левый ребенок
                    if node == node.parent.left:
                        node = node.parent
                        self._right_rotate(node)
                    
                    # Случай 3: узел - правый ребенок
                    node.parent.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    self._left_rotate(node.parent.parent)
        
        # Гарантируем, что корень черный
        self.root.color = 'BLACK'

    def _left_rotate(self, x):
        """Левый поворот вокруг узла x."""
        if x == self.NIL or x.right == self.NIL:
            return
        
        y = x.right
        x.right = y.left
        
        if y.left != self.NIL:
            y.left.parent = x
            
        y.parent = x.parent
        
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
            
        y.left = x
        x.parent = y

    def _right_rotate(self, y):
        """Правый поворот вокруг узла y."""
        if y == self.NIL or y.left == self.NIL:
            return
        
        x = y.left
        y.left = x.right
        
        if x.right != self.NIL:
            x.right.parent = y
            
        x.parent = y.parent
        
        if y.parent == self.NIL:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
            
        x.right = y
        y.parent = x

    def _get_tree_structure(self, node):
        """Преобразует дерево в структуру для визуализации."""
        if node == self.NIL:
            return None
            
        node_data = {
            'value': f"{node.value}({node.color[0]})",  # Показываем значение и первую букву цвета
            'children': []
        }
        
        if node.left != self.NIL:
            left_data = self._get_tree_structure(node.left)
            if left_data:
                node_data['children'].append(left_data)
                
        if node.right != self.NIL:
            right_data = self._get_tree_structure(node.right)
            if right_data:
                node_data['children'].append(right_data)
                
        return node_data

    def _inorder_traversal(self, node):
        """In-order обход дерева."""
        if node == self.NIL:
            return []
        
        result = []
        result.extend(self._inorder_traversal(node.left))
        result.append(node.value)
        result.extend(self._inorder_traversal(node.right))
        
        return result

    # ============= ИНТЕРАКТИВНЫЕ МЕТОДЫ =============
    
    def search(self, value):
        """Поиск значения в красно-черном дереве."""
        return self._search_recursive(self.root, value)
    
    def _search_recursive(self, node, value):
        """Рекурсивный поиск значения."""
        if node == self.NIL or node.value == value:
            return node
            
        if value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)
    
    def get_min(self):
        """Находит минимальный элемент."""
        if self.root == self.NIL:
            return None
            
        current = self.root
        while current.left != self.NIL:
            current = current.left
        return current.value
    
    def get_max(self):
        """Находит максимальный элемент."""
        if self.root == self.NIL:
            return None
            
        current = self.root
        while current.right != self.NIL:
            current = current.right
        return current.value
    
    def get_height(self):
        """Вычисляет высоту дерева."""
        return self._get_height_recursive(self.root)
    
    def _get_height_recursive(self, node):
        if node == self.NIL:
            return 0
        return 1 + max(
            self._get_height_recursive(node.left),
            self._get_height_recursive(node.right)
        )
    
    def is_balanced(self):
        """Проверяет балансировку дерева."""
        # Для красно-черных деревьев всегда сбалансированы
        return True
    
    # ОБХОДЫ ДЕРЕВА
    def get_preorder(self):
        """Прямой обход (КЛП)."""
        return self._preorder_recursive(self.root)
    
    def _preorder_recursive(self, node):
        if node == self.NIL:
            return []
        return [node.value] + self._preorder_recursive(node.left) + self._preorder_recursive(node.right)
    
    def get_inorder(self):
        """Центральный обход (ЛКП)."""
        return self._inorder_traversal(self.root)
    
    def get_postorder(self):
        """Обратный обход (ЛПК)."""
        return self._postorder_recursive(self.root)
    
    def _postorder_recursive(self, node):
        if node == self.NIL:
            return []
        return self._postorder_recursive(node.left) + self._postorder_recursive(node.right) + [node.value]
    
    def get_bfs(self):
        """Поиск в ширину (BFS)."""
        if self.root == self.NIL:
            return []
        
        result = []
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            if node != self.NIL:
                result.append(node.value)
                
                if node.left != self.NIL:
                    queue.append(node.left)
                if node.right != self.NIL:
                    queue.append(node.right)
        
        return result

    def _estimate_total_steps(self):
        """Оценка общего количества шагов."""
        n = len(self.data)
        return n * 3 + 1  # +1 для финального обхода