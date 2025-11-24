"""
Алгоритм поиска в ширину (BFS) для графов.
"""
from collections import deque

class GraphBFS:
    def __init__(self, graph, start_node):
        self.graph = graph
        self.start_node = start_node
        self.visited = set()
        self.queue = deque()
        self.steps = []
        
    def step(self):
        """Выполняет один шаг алгоритма и возвращает действие."""
        if not self.steps:
            self._initialize_bfs()
            
        if self.steps:
            action = self.steps.pop(0)
            return action
        else:
            return {
                "type": "complete",
                "visited_order": list(self.visited),
                "description": f"BFS завершен. Посещено {len(self.visited)} узлов."
            }
    
    def step_generator(self):
        """Генератор шагов для движка."""
        if not self.steps:
            self._initialize_bfs()
        
        for step in self.steps:
            yield step
        
        yield {
            "type": "complete", 
            "visited_order": list(self.visited),
            "description": f"BFS завершен. Посещено {len(self.visited)} узлов."
        }
    
    def get_generator(self):
        """Возвращает генератор шагов."""
        if not self.steps:
            self._initialize_bfs()
        for step in self.steps:
            yield step
        yield {
            "type": "complete",
            "visited_order": list(self.visited),
            "description": f"BFS завершен. Посещено {len(self.visited)} узлов."
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
    
    def _initialize_bfs(self):
        """Инициализирует BFS и генерирует все шаги."""
        # Шаг 1: Инициализация графа
        self.steps.append({
            "type": "graph_init",
            "graph": self.graph,
            "start_node": self.start_node,
            "algorithm": "BFS"
        })
        
        # Если стартовый узел не существует в графе
        if self.start_node not in self.graph:
            self.steps.append({
                "type": "complete",
                "visited_order": [],
                "description": f"Стартовый узел {self.start_node} не найден в графе."
            })
            return
        
        # Шаг 2: Посещение стартового узла
        self.visited.add(self.start_node)
        self.queue.append(self.start_node)
        
        self.steps.append({
            "type": "visit",
            "node": self.start_node,
            "description": f"Посещаем стартовый узел {self.start_node}"
        })
        
        # Основной цикл BFS
        while self.queue:
            current_node = self.queue.popleft()
            
            # Получаем соседей текущего узла
            neighbors = self._get_neighbors(current_node)
            
            # Обходим всех соседей
            for neighbor in neighbors:
                if neighbor not in self.visited:
                    # Шаг 3: Обнаружение нового узла
                    self.steps.append({
                        "type": "discover",
                        "from_node": current_node,
                        "node": neighbor,
                        "description": f"Обнаружен узел {neighbor} из узла {current_node}"
                    })
                    
                    # Шаг 4: Посещение нового узла
                    self.visited.add(neighbor)
                    self.queue.append(neighbor)
                    
                    self.steps.append({
                        "type": "visit",
                        "node": neighbor,
                        "description": f"Посещаем узел {neighbor}"
                    })
        
        # Шаг 5: Завершение
        self.steps.append({
            "type": "complete",
            "visited_order": list(self.visited),
            "description": f"BFS завершен. Посещено {len(self.visited)} узлов."
        })