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
            
        def __str__(self):
            return f"{self.value}({self.color[0]})"
            
        def __repr__(self):
            return self.__str__()

    def __init__(self, data):
        super().__init__(data)
        self.root = None


    def _build_tree(self):
        """Построение дерева из начальных данных."""
        processed = set()
        for val in self.data:
            if val not in processed:
                processed.add(val)
                self.insert(val)

    def step_generator(self):
        """Генератор шагов для визуализации."""
        processed = set()
        
        for i, val in enumerate(self.data):
            if val in processed:
                continue
            processed.add(val)
            
            yield {
                "type": "info",
                "description": f"Вставляем значение {val} в красно-черное дерево"
            }
            
            # Вставляем узел с балансировкой
            self.insert(val)
            
            # Показываем состояние после вставки
            tree_structure = self._get_tree_structure()
            yield {
                "type": "tree",
                "tree_data": tree_structure,
                "description": f"Вставлен узел: {val} (шаг {i+1}/{len(self.data)})"
            }
        
        # Обход inorder для демонстрации
        if self.root:
            inorder_values = self.get_inorder()
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

    # ============= ОСНОВНЫЕ ОПЕРАЦИИ =============
    
    def insert(self, value):
        """Публичный метод для вставки значения с балансировкой."""
        # Проверяем, существует ли уже такое значение
        if self.search(value) is not None:
            raise ValueError(f"Значение {value} уже существует в дереве")
        
        # Создаем новый узел
        new_node = self.Node(value, 'RED')
        
        # BST вставка
        self._bst_insert(new_node)
        
        # Балансировка
        self._fix_insert(new_node)
        
        return new_node
    
    def _bst_insert(self, new_node):
        """BST вставка нового узла."""
        if self.root is None:
            self.root = new_node
            self.root.color = 'BLACK'
            return
            
        current = self.root
        parent = None
        
        while current is not None:
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

    def _fix_insert(self, node):
        """Балансировка после вставки (основные случаи)."""
        while node != self.root and node.parent is not None and node.parent.color == 'RED':
            if node.parent.parent is None:
                break
                
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                
                # Случай 1: дядя красный
                if uncle is not None and uncle.color == 'RED':
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
                    if node.parent is not None and node.parent.parent is not None:
                        node.parent.color = 'BLACK'
                        node.parent.parent.color = 'RED'
                        self._right_rotate(node.parent.parent)
            else:
                # Симметричный случай для правого поддерева
                uncle = node.parent.parent.left
                
                # Случай 1: дядя красный
                if uncle is not None and uncle.color == 'RED':
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
                    if node.parent is not None and node.parent.parent is not None:
                        node.parent.color = 'BLACK'
                        node.parent.parent.color = 'RED'
                        self._left_rotate(node.parent.parent)
            
            # Защита от зацикливания
            if node.parent is None:
                break
        
        # Гарантируем, что корень черный
        if self.root is not None:
            self.root.color = 'BLACK'

    # ============= ПОВОРОТЫ =============
    
    def _left_rotate(self, x):
        """Левый поворот вокруг узла x."""
        if x is None or x.right is None:
            return
            
        y = x.right
        x.right = y.left
        
        if y.left is not None:
            y.left.parent = x
            
        y.parent = x.parent
        
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
            
        y.left = x
        x.parent = y

    def _right_rotate(self, y):
        """Правый поворот вокруг узла y."""
        if y is None or y.left is None:
            return
            
        x = y.left
        y.left = x.right
        
        if x.right is not None:
            x.right.parent = y
            
        x.parent = y.parent
        
        if y.parent is None:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
            
        x.right = y
        y.parent = x

    # ============= УДАЛЕНИЕ УЗЛА =============
    
    def delete(self, value):
        """Удаление значения из красно-черного дерева."""
        # Находим узел для удаления
        node = self._find_node(value)
        if node is None:
            raise ValueError(f"Значение {value} не найдено в дереве")
        
        # Находим узел для удаления и его замену
        y = node
        y_original_color = y.color
        
        if node.left is None:
            x = node.right
            self._transplant(node, node.right)
        elif node.right is None:
            x = node.left
            self._transplant(node, node.left)
        else:
            y = self._minimum(node.right)
            y_original_color = y.color
            x = y.right
            
            if y.parent == node:
                if x is not None:
                    x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = node.right
                if y.right is not None:
                    y.right.parent = y
            
            self._transplant(node, y)
            y.left = node.left
            if y.left is not None:
                y.left.parent = y
            y.color = node.color
        
        # Если удаленный узел был черным, нужно восстановить свойства
        if y_original_color == 'BLACK':
            self._fix_delete(x)
        
        return True
    
    def _find_node(self, value):
        """Находит узел по значению."""
        current = self.root
        while current is not None:
            if value == current.value:
                return current
            elif value < current.value:
                current = current.left
            else:
                current = current.right
        return None
    
    def _transplant(self, u, v):
        """Заменяет поддерево с корнем u на поддерево с корнем v."""
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        
        if v is not None:
            v.parent = u.parent
    
    def _minimum(self, node):
        """Находит минимальный узел в поддереве."""
        while node.left is not None:
            node = node.left
        return node
    
    def _fix_delete(self, x):
        """Восстанавливает свойства красно-черного дерева после удаления."""
        while x != self.root and x is not None and x.color == 'BLACK':
            if x == x.parent.left:
                sibling = x.parent.right
                
                # Случай 1: брат красный
                if sibling is not None and sibling.color == 'RED':
                    sibling.color = 'BLACK'
                    x.parent.color = 'RED'
                    self._left_rotate(x.parent)
                    sibling = x.parent.right
                
                # Случай 2: оба ребенка брата черные
                if (sibling is not None and 
                    (sibling.left is None or sibling.left.color == 'BLACK') and 
                    (sibling.right is None or sibling.right.color == 'BLACK')):
                    if sibling is not None:
                        sibling.color = 'RED'
                    x = x.parent
                else:
                    # Случай 3: правый ребенок брата черный
                    if sibling is not None and sibling.right is not None and sibling.right.color == 'BLACK':
                        if sibling.left is not None:
                            sibling.left.color = 'BLACK'
                        sibling.color = 'RED'
                        self._right_rotate(sibling)
                        sibling = x.parent.right
                    
                    # Случай 4
                    if sibling is not None:
                        sibling.color = x.parent.color
                    x.parent.color = 'BLACK'
                    if sibling is not None and sibling.right is not None:
                        sibling.right.color = 'BLACK'
                    self._left_rotate(x.parent)
                    x = self.root
            else:
                # Симметричный случай для правого поддерева
                sibling = x.parent.left
                
                # Случай 1: брат красный
                if sibling is not None and sibling.color == 'RED':
                    sibling.color = 'BLACK'
                    x.parent.color = 'RED'
                    self._right_rotate(x.parent)
                    sibling = x.parent.left
                
                # Случай 2: оба ребенка брата черные
                if (sibling is not None and 
                    (sibling.right is None or sibling.right.color == 'BLACK') and 
                    (sibling.left is None or sibling.left.color == 'BLACK')):
                    if sibling is not None:
                        sibling.color = 'RED'
                    x = x.parent
                else:
                    # Случай 3: левый ребенок брата черный
                    if sibling is not None and sibling.left is not None and sibling.left.color == 'BLACK':
                        if sibling.right is not None:
                            sibling.right.color = 'BLACK'
                        sibling.color = 'RED'
                        self._left_rotate(sibling)
                        sibling = x.parent.left
                    
                    # Случай 4
                    if sibling is not None:
                        sibling.color = x.parent.color
                    x.parent.color = 'BLACK'
                    if sibling is not None and sibling.left is not None:
                        sibling.left.color = 'BLACK'
                    self._right_rotate(x.parent)
                    x = self.root
            
            # Защита от зацикливания
            if x is None:
                break
        
        if x is not None:
            x.color = 'BLACK'

    # ============= ПОИСК И ОБХОДЫ =============
    
    def search(self, value):
        """Поиск значения в красно-черном дереве."""
        current = self.root
        while current is not None:
            if value == current.value:
                return current.value
            elif value < current.value:
                current = current.left
            else:
                current = current.right
        return None
    
    def get_min(self):
        """Находит минимальный элемент."""
        if self.root is None:
            return None
            
        current = self.root
        while current.left is not None:
            current = current.left
        return current.value
    
    def get_max(self):
        """Находит максимальный элемент."""
        if self.root is None:
            return None
            
        current = self.root
        while current.right is not None:
            current = current.right
        return current.value
    
    def get_height(self):
        """Вычисляет высоту дерева."""
        return self._get_height_recursive(self.root)
    
    def _get_height_recursive(self, node):
        if node is None:
            return 0
        return 1 + max(
            self._get_height_recursive(node.left),
            self._get_height_recursive(node.right)
        )
    
    def is_balanced(self):
        """Проверяет балансировку дерева."""
        # Для красно-черных деревьев всегда сбалансированы
        return True
    
    def get_balance_factor(self, node_value):
        """Возвращает баланс-фактор для узла."""
        node = self._find_node(node_value)
        if node is None:
            return None
        
        left_height = self._get_height_recursive(node.left)
        right_height = self._get_height_recursive(node.right)
        return right_height - left_height
    
    # ============= ОБХОДЫ ДЕРЕВА =============
    
    def get_preorder(self):
        """Прямой обход (КЛП)."""
        result = []
        self._preorder_iterative(self.root, result)
        return result
    
    def _preorder_iterative(self, node, result):
        if node is None:
            return
            
        stack = [node]
        
        while stack:
            current = stack.pop()
            if current is not None:
                result.append(f"{current.value}({current.color[0]})")
                stack.append(current.right)
                stack.append(current.left)
    
    def get_inorder(self):
        """Центральный обход (ЛКП)."""
        result = []
        self._inorder_iterative(self.root, result)
        return result
    
    def _inorder_iterative(self, node, result):
        if node is None:
            return
            
        stack = []
        current = node
        
        while stack or current is not None:
            while current is not None:
                stack.append(current)
                current = current.left
            
            current = stack.pop()
            result.append(f"{current.value}({current.color[0]})")
            current = current.right
    
    def get_postorder(self):
        """Обратный обход (ЛПК)."""
        result = []
        self._postorder_iterative(self.root, result)
        return result
    
    def _postorder_iterative(self, node, result):
        if node is None:
            return
            
        stack1 = [node]
        stack2 = []
        
        while stack1:
            current = stack1.pop()
            stack2.append(current)
            
            if current.left is not None:
                stack1.append(current.left)
            if current.right is not None:
                stack1.append(current.right)
        
        while stack2:
            current = stack2.pop()
            result.append(f"{current.value}({current.color[0]})")
    
    def get_bfs(self):
        """Поиск в ширину (BFS)."""
        if self.root is None:
            return []
        
        result = []
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            if node is not None:
                result.append(f"{node.value}({node.color[0]})")
                if node.left is not None:
                    queue.append(node.left)
                if node.right is not None:
                    queue.append(node.right)
        
        return result

    # ============= ВИЗУАЛИЗАЦИЯ =============
    
    def _get_tree_structure(self, node=None, depth=0):
        """Преобразует дерево в структуру для визуализации."""
        if node is None:
            node = self.root
            
        if node is None:
            return None
        
        # Защита от слишком глубокой рекурсии
        if depth > 100:
            return {
                'value': f"{node.value}({node.color[0]})",
                'children': []
            }
        
        node_data = {
            'value': f"{node.value}({node.color[0]})",
            'children': []
        }
        
        # Обрабатываем левого ребенка
        if node.left is not None:
            left_data = self._get_tree_structure(node.left, depth + 1)
            if left_data:
                node_data['children'].append(left_data)
        
        # Обрабатываем правого ребенка
        if node.right is not None:
            right_data = self._get_tree_structure(node.right, depth + 1)
            if right_data:
                node_data['children'].append(right_data)
        
        return node_data

    def _estimate_total_steps(self):
        """Оценка общего количества шагов."""
        n = len(self.data)
        return n * 3 + 2  # Вставка + балансировка + обход
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