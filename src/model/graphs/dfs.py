"""
Алгоритм поиска в глубину (DFS) для графов.
"""

class GraphDFS:
    def __init__(self, graph, start_node):
        self.graph = graph
        self.start_node = start_node
        self.visited = set()
        self.stack = []
        self.steps = []
        
    def step(self):
        """Выполняет один шаг алгоритма и возвращает действие."""
        if not self.steps:
            self._initialize_dfs()
            
        if self.steps:
            action = self.steps.pop(0)
            return action
        else:
            return {
                "type": "complete",
                "visited_order": list(self.visited),
                "description": f"DFS завершен. Посещено {len(self.visited)} узлов."
            }
    
    def step_generator(self):
        """Генератор шагов для движка."""
        if not self.steps:
            self._initialize_dfs()
        
        for step in self.steps:
            yield step
        
        yield {
            "type": "complete",
            "visited_order": list(self.visited),
            "description": f"DFS завершен. Посещено {len(self.visited)} узлов."
        }
    
    def get_generator(self):
        """Возвращает генератор шагов."""
        if not self.steps:
            self._initialize_dfs()
        for step in self.steps:
            yield step
        yield {
            "type": "complete",
            "visited_order": list(self.visited),
            "description": f"DFS завершен. Посещено {len(self.visited)} узлов."
        }
    
    def _get_neighbors(self, node):
        """Унифицированное получение соседей для любого формата графа."""
        if node not in self.graph:
            return []
        
        neighbors = self.graph[node]
        
        if isinstance(neighbors, dict):
            return list(neighbors.keys())
        elif isinstance(neighbors, list):
            neighbor_nodes = []
            for neighbor in neighbors:
                if isinstance(neighbor, tuple):
                    neighbor_nodes.append(neighbor[0])  # Берем только ID узла
                else:
                    neighbor_nodes.append(neighbor)
            return neighbor_nodes
        else:
            return []
    
    def _initialize_dfs(self):
        """Инициализирует DFS и генерирует все шаги."""
        # Шаг 1: Инициализация графа
        self.steps.append({
            "type": "graph_init",
            "graph": self.graph,
            "start_node": self.start_node,
            "algorithm": "DFS"
        })
        
        # Если стартовый узел не существует в графе
        if self.start_node not in self.graph:
            self.steps.append({
                "type": "complete",
                "visited_order": [],
                "description": f"Стартовый узел {self.start_node} не найден в графе."
            })
            return
        
        # Используем стек для классического DFS
        stack = [self.start_node]
        
        while stack:
            current_node = stack.pop()
            
            if current_node not in self.visited:
                # Посещение узла
                self.visited.add(current_node)
                self.steps.append({
                    "type": "visit",
                    "node": current_node,
                    "description": f"Посещаем узел {current_node}"
                })
                
                # Получаем соседей в обратном порядке для правильного обхода
                neighbors = self._get_neighbors(current_node)
                # Добавляем в обратном порядке чтобы сохранить порядок обхода
                for neighbor in reversed(neighbors):
                    if neighbor not in self.visited:
                        # Обнаружение связи
                        self.steps.append({
                            "type": "discover",
                            "from_node": current_node,
                            "node": neighbor,
                            "description": f"Обнаружен узел {neighbor} из узла {current_node}"
                        })
                        stack.append(neighbor)
        
        # Шаг 5: Завершение
        self.steps.append({
            "type": "complete",
            "visited_order": list(self.visited),
            "description": f"DFS завершен. Посещено {len(self.visited)} узлов."
        })