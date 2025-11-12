from model.base_algorithm import BaseAlgorithm

class RedBlackTree(BaseAlgorithm):
    """Красно-черное дерево с поддержкой визуализации и правильной балансировкой."""
    
    class Node:
        def __init__(self, value, color='RED'):
            self.value = value
            self.left = None
            self.right = None
            self.parent = None
            self.color = color  # 'RED' or 'BLACK'

    def __init__(self, data):
        super().__init__(data)
        self.root = None
        self.NIL = self.Node(None, 'BLACK')  # NIL лист

    def step_generator(self):
        """Генератор шагов для красно-черного дерева с детальной балансировкой."""
        for val in self.data:
            # Вставка нового узла
            new_node = self.Node(val, 'RED')
            new_node.left = self.NIL
            new_node.right = self.NIL
            
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure(self.root),
                "description": f"Начинаем вставку узла: {val} (красный)"
            }
            
            # BST вставка
            self._bst_insert(new_node)
            
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure(self.root),
                "description": f"Узел {val} вставлен (красный), начинаем балансировку"
            }
            
            # Балансировка
            yield from self._fix_insert(new_node)
            
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure(self.root),
                "description": f"Балансировка после вставки {val} завершена"
            }
        
        # Обход inorder для демонстрации
        if self.root:
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

    def _bst_insert(self, new_node):
        """BST вставка нового узла."""
        if self.root is None:
            self.root = new_node
            self.root.color = 'BLACK'  # Корень всегда черный
            return
            
        current = self.root
        parent = None
        
        while current != self.NIL:
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
        """Балансировка после вставки с yield для визуализации."""
        while node != self.root and node.parent.color == 'RED':
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                
                # Случай 1: дядя красный
                if uncle.color == 'RED':
                    yield {
                        "type": "tree",
                        "tree_data": self._get_tree_structure(self.root),
                        "description": f"Случай 1: Дядя узла {node.value} красный - перекрашиваем"
                    }
                    
                    node.parent.color = 'BLACK'
                    uncle.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    node = node.parent.parent
                    
                    yield {
                        "type": "tree",
                        "tree_data": self._get_tree_structure(self.root),
                        "description": f"Перекрашены: родитель и дядя в черный, дедушка в красный"
                    }
                else:
                    # Случай 2: узел - правый ребенок
                    if node == node.parent.right:
                        yield {
                            "type": "tree",
                            "tree_data": self._get_tree_structure(self.root),
                            "description": f"Случай 2: Узел {node.value} - правый ребенок, левый поворот"
                        }
                        
                        node = node.parent
                        self._left_rotate(node)
                        
                        yield {
                            "type": "tree",
                            "tree_data": self._get_tree_structure(self.root),
                            "description": f"Выполнен левый поворот вокруг узла {node.value}"
                        }
                    
                    # Случай 3: узел - левый ребенок
                    yield {
                        "type": "tree",
                        "tree_data": self._get_tree_structure(self.root),
                        "description": f"Случай 3: Узел {node.value} - левый ребенок, правый поворот и перекрашивание"
                    }
                    
                    node.parent.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    self._right_rotate(node.parent.parent)
                    
                    yield {
                        "type": "tree",
                        "tree_data": self._get_tree_structure(self.root),
                        "description": f"Выполнен правый поворот и перекрашивание"
                    }
            else:
                # Симметричный случай для правого поддерева
                uncle = node.parent.parent.left
                
                # Случай 1: дядя красный
                if uncle.color == 'RED':
                    yield {
                        "type": "tree",
                        "tree_data": self._get_tree_structure(self.root),
                        "description": f"Случай 1 (симметричный): Дядя узла {node.value} красный - перекрашиваем"
                    }
                    
                    node.parent.color = 'BLACK'
                    uncle.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    node = node.parent.parent
                    
                    yield {
                        "type": "tree",
                        "tree_data": self._get_tree_structure(self.root),
                        "description": f"Перекрашены: родитель и дядя в черный, дедушка в красный"
                    }
                else:
                    # Случай 2: узел - левый ребенок
                    if node == node.parent.left:
                        yield {
                            "type": "tree",
                            "tree_data": self._get_tree_structure(self.root),
                            "description": f"Случай 2 (симметричный): Узел {node.value} - левый ребенок, правый поворот"
                        }
                        
                        node = node.parent
                        self._right_rotate(node)
                        
                        yield {
                            "type": "tree",
                            "tree_data": self._get_tree_structure(self.root),
                            "description": f"Выполнен правый поворот вокруг узла {node.value}"
                        }
                    
                    # Случай 3: узел - правый ребенок
                    yield {
                        "type": "tree",
                        "tree_data": self._get_tree_structure(self.root),
                        "description": f"Случай 3 (симметричный): Узел {node.value} - правый ребенок, левый поворот и перекрашивание"
                    }
                    
                    node.parent.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    self._left_rotate(node.parent.parent)
                    
                    yield {
                        "type": "tree",
                        "tree_data": self._get_tree_structure(self.root),
                        "description": f"Выполнен левый поворот и перекрашивание"
                    }
        
        # Гарантируем, что корень черный
        if self.root.color != 'BLACK':
            self.root.color = 'BLACK'
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure(self.root),
                "description": "Корень перекрашен в черный цвет"
            }

    def _left_rotate(self, x):
        """Левый поворот вокруг узла x."""
        y = x.right
        x.right = y.left
        
        if y.left != self.NIL:
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
        x = y.left
        y.left = x.right
        
        if x.right != self.NIL:
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

    def _get_tree_structure(self, node):
        """Преобразует дерево в структуру для визуализации."""
        if node is None or node == self.NIL:
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
        if node is None or node == self.NIL:
            return []
        
        result = []
        result.extend(self._inorder_traversal(node.left))
        result.append(node.value)
        result.extend(self._inorder_traversal(node.right))
        
        return result

    def _estimate_total_steps(self):
        """Оценка общего количества шагов."""
        n = len(self.data)
        return n * 8  # Вставка + несколько шагов балансировки на каждый узел