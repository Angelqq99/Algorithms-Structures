"""
Алгоритм Крускала для поиска минимального остовного дерева (MST).
"""

class GraphKruskal:
    def __init__(self, graph):
        self.graph = graph  # Формат: {u: {v: weight, ...}, ...}
        self.steps = []
        self._parent = {}
        self._rank = {}
        self.mst_edges = []  # Ребра, вошедшие в MST
        self.total_weight = 0

    def _find(self, i):
        if self._parent[i] == i:
            return i
        self._parent[i] = self._find(self._parent[i])
        return self._parent[i]

    def _union(self, i, j):
        root_i = self._find(i)
        root_j = self._find(j)
        if root_i != root_j:
            if self._rank[root_i] < self._rank[root_j]:
                self._parent[root_i] = root_j
            elif self._rank[root_i] > self._rank[root_j]:
                self._parent[root_j] = root_i
            else:
                self._parent[root_i] = root_j
                self._rank[root_j] += 1
            return True
        return False

    def _initialize_kruskal(self):
        self.steps = []
        edges = []
        nodes = set()

        # Извлекаем все уникальные ребра
        for u, neighbors in self.graph.items():
            nodes.add(u)
            for v, weight in neighbors.items():
                nodes.add(v)
                # Для неориентированного графа берем ребро один раз
                if u < v:
                    edges.append((u, v, weight))
        
        # Сортируем ребра по весу
        edges.sort(key=lambda x: x[2])
        
        # Инициализация DSU
        for node in nodes:
            self._parent[node] = node
            self._rank[node] = 0

        self.mst_edges = []
        self.total_weight = 0
        edges_count = 0

        for u, v, weight in edges:
            # Шаг: рассматриваем ребро
            self.steps.append({
                "type": "consider_edge",
                "u": u, "v": v,
                "weight": weight,
                "description": f"Рассматриваем ребро {u}-{v} с весом {weight}"
            })

            if self._find(u) != self._find(v):
                self._union(u, v)
                self.total_weight += weight
                edges_count += 1
                self.mst_edges.append((u, v, weight))
                
                # Шаг: добавляем в MST
                self.steps.append({
                    "type": "accept_edge",
                    "u": u, "v": v,
                    "weight": weight,
                    "description": f"Ребро {u}-{v} добавлено в MST (цикл не образуется)"
                })
                
                # Если построили остовное дерево (n-1 ребер), останавливаемся
                if edges_count == len(nodes) - 1:
                    break
            else:
                # Шаг: пропускаем (образует цикл)
                self.steps.append({
                    "type": "reject_edge",
                    "u": u, "v": v,
                    "weight": weight,
                    "description": f"Ребро {u}-{v} пропущено (образует цикл)"
                })

        self.steps.append({
            "type": "complete",
            "description": f"Алгоритм завершен. Вес MST: {self.total_weight}",
            "mst_weight": self.total_weight,
            "mst_edges": self.mst_edges,
            "mst_edge_count": len(self.mst_edges)
        })

    def step_generator(self):
        if not self.steps:
            self._initialize_kruskal()
        for step in self.steps:
            yield step

    def get_generator(self):
        return self.step_generator()