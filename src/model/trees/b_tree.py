from model.base_algorithm import BaseAlgorithm

class BTree(BaseAlgorithm):
    """B-дерево с поддержкой визуализации."""
    
    class Node:
        def __init__(self, t, leaf=False):
            self.t = t  # минимальная степень
            self.keys = []
            self.children = []
            self.leaf = leaf
            self.parent = None

    def __init__(self, data, t=2):
        super().__init__(data)
        self.t = t  # минимальная степень
        self.root = None

    def step_generator(self):
        """Генератор шагов для B-дерева."""
        for val in self.data:
            if self.root is None:
                self.root = self.Node(self.t, True)
                self.root.keys.append(val)
            else:
                self._insert_non_full(self.root, val)
                
            tree_structure = self._get_tree_structure(self.root)
            yield {
                "type": "tree",
                "tree_data": tree_structure,
                "description": f"Вставлен узел: {val} (B-дерево)"
            }
        
        yield {
            "type": "complete",
            "description": "Построение B-дерева завершено"
        }

    def _insert_non_full(self, node, key):
        """Вставка в неполный узел."""
        i = len(node.keys) - 1
        
        if node.leaf:
            node.keys.append(0)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == 2 * self.t - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)

    def _split_child(self, parent, i):
        """Разделение дочернего узла."""
        t = self.t
        y = parent.children[i]
        z = self.Node(t, y.leaf)
        
        parent.children.insert(i + 1, z)
        parent.keys.insert(i, y.keys[t - 1])
        
        z.keys = y.keys[t:(2 * t - 1)]
        y.keys = y.keys[0:(t - 1)]
        
        if not y.leaf:
            z.children = y.children[t:(2 * t)]
            y.children = y.children[0:t]

    def _get_tree_structure(self, node):
        """Преобразует B-дерево в структуру для визуализации."""
        if node is None:
            return None
            
        node_data = {
            'value': f"B-узел: {node.keys}",
            'children': []
        }
        
        for child in node.children:
            child_data = self._get_tree_structure(child)
            if child_data:
                node_data['children'].append(child_data)
                
        return node_data

    def _estimate_total_steps(self):
        """Оценка общего количества шагов."""
        n = len(self.data)
        return n * 3  # Вставка