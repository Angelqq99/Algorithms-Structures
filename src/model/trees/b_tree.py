from model.base_algorithm import BaseAlgorithm

class BTree(BaseAlgorithm):
    """B-дерево с правильной реализацией свойств."""
    
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

    def __init__(self, data, t=2):
        super().__init__(data)
        self.t = t  # минимальная степень
        self.root = None
        self.node_id_counter = 0
        self.nodes_by_id = {}

    def step_generator(self):
        """Генератор шагов для B-дерева."""
        yield {
            "type": "tree",
            "tree_data": self._get_tree_structure_list(),
            "description": f"Инициализация B-дерева порядка {2*self.t} (t={self.t})",
            "tree_type": "BTree"
        }
        
        for i, val in enumerate(self.data):
            if self.root is None:
                # Создаем корневой узел (лист)
                self.root = self.Node(self.t, True, self.node_id_counter)
                self.nodes_by_id[self.node_id_counter] = self.root
                self.node_id_counter += 1
                self.root.keys.append(val)
                
                yield {
                    "type": "tree",
                    "tree_data": self._get_tree_structure_list(),
                    "description": f"Создан корневой узел с ключом: {val}",
                    "tree_type": "BTree"
                }
            else:
                # Вставляем значение
                yield from self._insert_with_steps(val)
            
            # Обновляем структуру для визуализации
            self._update_tree_structure()
            
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure_list(),
                "description": f"Вставлен ключ {val} ({i+1}/{len(self.data)})",
                "tree_type": "BTree"
            }
        
        yield {
            "type": "complete",
            "description": f"Построение B-дерева завершено. Порядок дерева: {2*self.t}",
            "tree_data": self._get_tree_structure_list()
        }

    def _insert_with_steps(self, key):
        """Вставка с шагами для визуализации."""
        root = self.root
        
        if root.is_full():
            # Создаем новый корень
            new_root = self.Node(self.t, False, self.node_id_counter)
            self.nodes_by_id[self.node_id_counter] = new_root
            self.node_id_counter += 1
            
            # Старый корень становится дочерним
            new_root.children.append(root)
            root.parent = new_root
            self.root = new_root
            
            # Разделяем старый корень
            self._split_child(new_root, 0)
            
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure_list(),
                "description": f"Корень полный, создан новый корень",
                "tree_type": "BTree"
            }
            
            # Вставляем в новый корень
            yield from self._insert_nonfull(new_root, key)
        else:
            yield from self._insert_nonfull(root, key)

    def _insert_nonfull(self, node, key):
        """Вставка в неполный узел."""
        i = len(node.keys) - 1
        
        if node.leaf:
            # Вставляем ключ в листовой узел
            while i >= 0 and key < node.keys[i]:
                i -= 1
            node.keys.insert(i + 1, key)
            
            yield {
                "type": "tree",
                "tree_data": self._get_tree_structure_list(),
                "description": f"Вставка {key} в листовой узел",
                "tree_type": "BTree"
            }
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
            yield from self._insert_nonfull(node.children[i], key)

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

    def _estimate_total_steps(self):
        """Оценка общего количества шагов."""
        return len(self.data) * 3  # Примерная оценка

    # Операции поиска (опционально)
    def search(self, key):
        """Поиск ключа в B-дереве."""
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