from model.base_algorithm import BaseAlgorithm
from collections import deque

class BTree(BaseAlgorithm):
    """B-дерево с поддержкой интерактивных операций."""
    
    class Node:
        def __init__(self, t, leaf=False, node_id=0):
            self.t = t  # минимальная степень (порядок = 2t)
            self.keys = []
            self.children = []
            self.leaf = leaf
            self.parent = None
            self.id = node_id  # Уникальный ID
            
            # Для визуализации
            self.x = 0
            self.y = 0
            self.width = 0
            self.height = 0
            self.level = 0
            
        def is_full(self):
            """Проверяет, заполнен ли узел."""
            return len(self.keys) >= 2 * self.t - 1
        
        def is_minimal(self):
            """Проверяет, имеет ли узел минимальное количество ключей."""
            return len(self.keys) <= self.t - 1
        
        def __str__(self):
            return f"Node(id={self.id}, keys={self.keys}, leaf={self.leaf}, children={len(self.children)})"

    def __init__(self, data, t=2):
        super().__init__(data)
        self.t = t  # минимальная степень
        self.root = None
        self.node_id_counter = 0
        self.nodes_by_id = {}
        self._build_tree()

    def _build_tree(self):
        """Строит B-дерево из начальных данных."""
        if not self.data:
            return
            
        # Удаляем дубликаты перед построением
        unique_data = list(dict.fromkeys(self.data))
        self.data = unique_data  # Обновляем данные
        
        for val in self.data:
            self.insert_value(val)
    
    def insert_value(self, key):
        """Публичный метод для интерактивной вставки значения."""
        # Сначала проверяем, нет ли уже такого ключа
        if self.search(key) is not None:
            return  # Игнорируем дубликат
            
        if self.root is None:
            self.root = self.Node(self.t, True, self.node_id_counter)
            self.nodes_by_id[self.node_id_counter] = self.root
            self.node_id_counter += 1
            self.root.keys.append(key)
        else:
            self._insert_nonfull(self.root, key)
            
            # Проверяем, нужно ли разделить корень
            if len(self.root.keys) >= 2 * self.t:
                self._split_root()
        
        self._update_tree_structure()
    
    def _insert_nonfull(self, node, key):
        """Вставка в неполный узел."""
        i = len(node.keys) - 1
        
        if node.leaf:
            # Вставляем ключ в листовой узел
            while i >= 0 and key < node.keys[i]:
                i -= 1
            node.keys.insert(i + 1, key)
        else:
            # Находим правильного ребенка
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            # Проверяем, полон ли ребенок
            if node.children[i].is_full():
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            
            # Рекурсивно вставляем в ребенка
            self._insert_nonfull(node.children[i], key)
    
    def _split_root(self):
        """Разделяет корневой узел."""
        t = self.t
        old_root = self.root
        
        # Создаем новый корень
        new_root = self.Node(t, False, self.node_id_counter)
        self.nodes_by_id[self.node_id_counter] = new_root
        self.node_id_counter += 1
        
        # Старый корень становится дочерним
        new_root.children.append(old_root)
        old_root.parent = new_root
        self.root = new_root
        
        # Разделяем старый корень
        self._split_child(new_root, 0)
    
    def _split_child(self, parent, child_idx):
        """Разделение дочернего узла."""
        t = self.t
        child = parent.children[child_idx]  # Полный узел
        
        # Создаем новый узел
        new_node = self.Node(t, child.leaf, self.node_id_counter)
        self.nodes_by_id[self.node_id_counter] = new_node
        self.node_id_counter += 1
        new_node.parent = parent
        
        # Ключ, который поднимется в родителя
        median_key = child.keys[t - 1]
        
        # Перемещаем ключи из child в new_node
        new_node.keys = child.keys[t:(2 * t - 1)].copy()
        child.keys = child.keys[0:(t - 1)].copy()
        
        # Если не лист, перемещаем детей
        if not child.leaf:
            new_node.children = child.children[t:(2 * t)].copy()
            child.children = child.children[0:t].copy()
            
            # Обновляем родителей детей
            for c in new_node.children:
                c.parent = new_node
        
        # Вставляем новый узел и ключ в родителя
        parent.children.insert(child_idx + 1, new_node)
        parent.keys.insert(child_idx, median_key)
    
    def step_generator(self):
        """Генератор шагов для B-дерева."""
        yield {
            "type": "tree",
            "tree_data": self._get_tree_structure_list(),
            "description": f"Инициализация B-дерева порядка {2*self.t} (t={self.t})",
            "tree_type": "BTree"
        }
        
        # Создаем временный корень для пошаговой визуализации
        if not self.root:
            self.root = self.Node(self.t, True, self.node_id_counter)
            self.nodes_by_id[self.node_id_counter] = self.root
            self.node_id_counter += 1
        
        processed_keys = set()
        
        for i, val in enumerate(self.data):
            # Пропускаем дубликаты
            if val in processed_keys:
                continue
            processed_keys.add(val)
            
            # Вставляем ключ
            self.insert_value(val)
            
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure_list(),
                "description": f"Вставлен ключ {val} ({len(processed_keys)}/{len(set(self.data))})",
                "tree_type": "BTree"
            }
        
        yield {
            "type": "complete",
            "description": f"Построение B-дерева завершено. Порядок дерева: {2*self.t}. Уникальных ключей: {len(processed_keys)}",
            "tree_data": self._get_tree_structure_list()
        }
    
    def _update_tree_structure(self):
        """Обновляет позиции узлов для визуализации."""
        if not self.root:
            return
            
        # Назначаем уровни
        self._assign_levels(self.root, 0)
        
        # Вычисляем позиции
        self._calculate_positions(self.root, 0, 0, 1)
    
    def _assign_levels(self, node, level):
        """Назначает уровни узлам."""
        if node is None:
            return
            
        node.level = level
        for child in node.children:
            self._assign_levels(child, level + 1)
    
    def _calculate_positions(self, node, x, y, width_factor):
        """Вычисляет позиции узлов рекурсивно."""
        if node is None:
            return
            
        # Устанавливаем позицию текущего узла
        node.x = x
        node.y = y * 150  # Вертикальный отступ
        
        # Вычисляем ширину узла
        node.width = max(150, len(node.keys) * 50 + 50)
        node.height = 60
        
        # Если есть дети, рекурсивно вычисляем их позиции
        if node.children:
            child_width = width_factor / len(node.children)
            for i, child in enumerate(node.children):
                child_x = x + (i - len(node.children)/2 + 0.5) * child_width * 250
                self._calculate_positions(child, child_x, y + 1, child_width)
    
    def _get_tree_structure_list(self):
        """Преобразует B-дерево в список узлов для визуализации."""
        nodes_list = []
        if self.root:
            self._collect_nodes(self.root, nodes_list)
        return nodes_list
    
    def _collect_nodes(self, node, nodes_list):
        """Собирает все узлы в список."""
        if node is None:
            return
            
        # Создаем данные узла
        node_data = {
            'id': node.id,
            'keys': node.keys.copy(),
            'is_leaf': node.leaf,
            'key_count': len(node.keys),
            'children': [c.id for c in node.children],
            'visual_type': 'btree_node',
            'pos_x': node.x,
            'pos_y': node.y,
            'width': node.width,
            'height': node.height,
            'level': node.level
        }
        
        nodes_list.append(node_data)
        
        # Рекурсивно собираем детей
        for child in node.children:
            self._collect_nodes(child, nodes_list)
    
    # ИНТЕРАКТИВНЫЕ ОПЕРАЦИИ
    
    def search(self, key):
        """Поиск ключа в B-дереве. Возвращает (узел, индекс) или None."""
        return self._search_recursive(self.root, key)
    
    def _search_recursive(self, node, key):
        """Рекурсивный поиск ключа."""
        if node is None:
            return None
            
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
            
        if i < len(node.keys) and key == node.keys[i]:
            return node, i
            
        if node.leaf:
            return None
            
        return self._search_recursive(node.children[i], key)
    
    def delete(self, key):
        """Удаление ключа из B-дерева."""
        if not self.root:
            return
            
        self._delete_recursive(self.root, key)
        
        # Если корень пуст после удаления
        if len(self.root.keys) == 0:
            if self.root.leaf:
                self.root = None
            else:
                self.root = self.root.children[0]
                self.root.parent = None
        
        self._update_tree_structure()
    
    def _delete_recursive(self, node, key):
        """Рекурсивное удаление ключа."""
        t = self.t
        i = 0
        
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
            
        # Ключ найден в текущем узле
        if i < len(node.keys) and node.keys[i] == key:
            if node.leaf:
                # Просто удаляем из листа
                node.keys.pop(i)
            else:
                # Узел не лист
                # Находим предшественника
                if len(node.children[i].keys) >= t:
                    predecessor = self._get_predecessor(node, i)
                    node.keys[i] = predecessor
                    self._delete_recursive(node.children[i], predecessor)
                # Или находим преемника
                elif len(node.children[i+1].keys) >= t:
                    successor = self._get_successor(node, i)
                    node.keys[i] = successor
                    self._delete_recursive(node.children[i+1], successor)
                else:
                    # Сливаем детей
                    self._merge_children(node, i)
                    self._delete_recursive(node.children[i], key)
        else:
            # Ключ не в текущем узле
            if node.leaf:
                return  # Ключа нет в дереве
                
            # Проверяем, достаточно ли ключей в дочернем узле
            if len(node.children[i].keys) < t:
                self._fill_child(node, i)
                
            # Рекурсивно продолжаем поиск
            if i > len(node.keys):
                self._delete_recursive(node.children[i-1], key)
            else:
                self._delete_recursive(node.children[i], key)
    
    def _get_predecessor(self, node, idx):
        """Находит наибольший ключ в левом поддереве."""
        current = node.children[idx]
        while not current.leaf:
            current = current.children[len(current.keys)]
        return current.keys[-1]
    
    def _get_successor(self, node, idx):
        """Находит наименьший ключ в правом поддереве."""
        current = node.children[idx+1]
        while not current.leaf:
            current = current.children[0]
        return current.keys[0]
    
    def _merge_children(self, parent, idx):
        """Сливает двух детей родителя."""
        t = self.t
        child = parent.children[idx]
        sibling = parent.children[idx+1]
        
        # Перемещаем ключ из родителя в ребенка
        child.keys.append(parent.keys[idx])
        
        # Копируем ключи и детей из sibling
        child.keys.extend(sibling.keys)
        if not child.leaf:
            child.children.extend(sibling.children)
            
        # Удаляем ключ из родителя и sibling
        parent.keys.pop(idx)
        parent.children.pop(idx+1)
        
        # Удаляем sibling из nodes_by_id
        if sibling.id in self.nodes_by_id:
            del self.nodes_by_id[sibling.id]
    
    def _fill_child(self, parent, idx):
        """Заполняет дочерний узел, если в нем мало ключей."""
        t = self.t
        
        if idx != 0 and len(parent.children[idx-1].keys) >= t:
            # Берем у левого соседа
            self._borrow_from_left(parent, idx)
        elif idx != len(parent.keys) and len(parent.children[idx+1].keys) >= t:
            # Берем у правого соседа
            self._borrow_from_right(parent, idx)
        else:
            # Сливаем с соседом
            if idx != len(parent.keys):
                self._merge_children(parent, idx)
            else:
                self._merge_children(parent, idx-1)
    
    def _borrow_from_left(self, parent, idx):
        """Заимствует ключ у левого соседа."""
        child = parent.children[idx]
        sibling = parent.children[idx-1]
        
        # Перемещаем ключ из родителя в ребенка
        child.keys.insert(0, parent.keys[idx-1])
        
        if not sibling.leaf:
            child.children.insert(0, sibling.children.pop())
            
        # Перемещаем ключ из sibling в родителя
        parent.keys[idx-1] = sibling.keys.pop()
    
    def _borrow_from_right(self, parent, idx):
        """Заимствует ключ у правого соседа."""
        child = parent.children[idx]
        sibling = parent.children[idx+1]
        
        # Перемещаем ключ из родителя в ребенка
        child.keys.append(parent.keys[idx])
        
        if not sibling.leaf:
            child.children.append(sibling.children.pop(0))
            
        # Перемещаем ключ из sibling в родителя
        parent.keys[idx] = sibling.keys.pop(0)
    
    # ОБХОДЫ ДЕРЕВА
    
    def get_bfs(self):
        """Поиск в ширину (BFS) для B-дерева. Возвращает список уровней."""
        return self.bfs_btree()
    
    def bfs_btree(self):
        """Поиск в ширину (BFS) для B-дерева."""
        if not self.root:
            return []
        
        result = []
        queue = deque([self.root])
        
        while queue:
            level_size = len(queue)
            level_nodes = []
            
            for _ in range(level_size):
                node = queue.popleft()
                level_nodes.append(node.keys.copy())
                
                # Добавляем детей в очередь
                for child in node.children:
                    queue.append(child)
            
            result.append(level_nodes)
        
        return result
    
    def get_preorder(self):
        """Прямой обход B-дерева."""
        result = []
        self._preorder_recursive(self.root, result)
        return result
    
    def _preorder_recursive(self, node, result):
        if node is None:
            return
        result.append(node.keys.copy())
        for child in node.children:
            self._preorder_recursive(child, result)
    
    def get_inorder(self):
        """In-order обход B-дерева (последовательный обход ключей)."""
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def _inorder_recursive(self, node, result):
        if node is None:
            return
            
        if node.leaf:
            result.extend(node.keys)
        else:
            for i in range(len(node.keys)):
                self._inorder_recursive(node.children[i], result)
                result.append(node.keys[i])
            self._inorder_recursive(node.children[-1], result)
    
    def get_postorder(self):
        """Обратный обход B-дерева."""
        result = []
        self._postorder_recursive(self.root, result)
        return result
    
    def _postorder_recursive(self, node, result):
        if node is None:
            return
            
        for child in node.children:
            self._postorder_recursive(child, result)
        result.append(node.keys.copy())
    
    # ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ
    
    def insert(self, value):
        """Алиас для insert_value для совместимости с другими деревьями."""
        self.insert_value(value)
    
    def get_min(self):
        """Находит минимальный ключ в B-дереве."""
        if not self.root:
            return None
            
        node = self.root
        while not node.leaf:
            node = node.children[0]
        
        return node.keys[0] if node.keys else None
    
    def get_max(self):
        """Находит максимальный ключ в B-дереве."""
        if not self.root:
            return None
            
        node = self.root
        while not node.leaf:
            node = node.children[-1]
        
        return node.keys[-1] if node.keys else None
    
    def get_height(self):
        """Возвращает высоту B-дерева."""
        if not self.root:
            return 0
            
        height = 0
        node = self.root
        while not node.leaf:
            height += 1
            node = node.children[0]
        
        return height + 1
    
    def is_balanced(self):
        """Проверяет, сбалансировано ли B-дерево."""
        if not self.root:
            return True
            
        # В B-дереве все листья должны быть на одном уровне
        leaf_levels = set()
        
        def check_levels(node, level):
            if node.leaf:
                leaf_levels.add(level)
            else:
                for child in node.children:
                    check_levels(child, level + 1)
        
        check_levels(self.root, 0)
        return len(leaf_levels) == 1
    
    def _get_tree_structure(self, node=None):
        """Возвращает структуру дерева для визуализации (для совместимости)."""
        # Игнорируем параметр node для совместимости
        return self._get_tree_structure_list()
    
    def _estimate_total_steps(self):
        """Оценка общего количества шагов."""
        return len(self.data) * 3