"""
Алгоритм Дейкстры для поиска кратчайших путей.
"""
import heapq
import math

class Dijkstra:
    def __init__(self, graph, start_node):
        self.graph = graph
        self.start_node = start_node
        self.distances = {}
        self.previous = {}
        self.visited = set()
        self.steps = []
        
    def step(self):
        """Выполняет один шаг алгоритма и возвращает действие."""
        if not self.steps:
            self._initialize_dijkstra()
            
        if self.steps:
            action = self.steps.pop(0)
            return action
        else:
            return {
                "type": "complete",
                "distances": self.distances,
                "description": f"Алгоритм Дейкстры завершен."
            }
    
    def step_generator(self):
        """Генератор шагов для движка."""
        if not self.steps:
            self._initialize_dijkstra()
        
        for step in self.steps:
            yield step
        
        yield {
            "type": "complete",
            "distances": self.distances,
            "description": f"Алгоритм Дейкстры завершен."
        }
    
    def get_generator(self):
        """Возвращает генератор шагов."""
        if not self.steps:
            self._initialize_dijkstra()
        for step in self.steps:
            yield step
        yield {
            "type": "complete",
            "distances": self.distances,
            "description": f"Алгоритм Дейкстры завершен."
        }
    
    def _get_neighbors_with_weights(self, node):
        """Унифицированное получение соседей с весами."""
        if node not in self.graph:
            return []
        
        neighbors = self.graph[node]
        
        if isinstance(neighbors, dict):
            return list(neighbors.items())
        elif isinstance(neighbors, list):
            neighbor_items = []
            for neighbor in neighbors:
                if isinstance(neighbor, tuple):
                    neighbor_items.append((neighbor[0], neighbor[1]))
                else:
                    neighbor_items.append((neighbor, 1))  # Вес по умолчанию
            return neighbor_items
        else:
            return []
    
    def _initialize_dijkstra(self):
        """Инициализирует алгоритм Дейкстры и генерирует все шаги."""
        # Шаг 1: Инициализация графа
        self.steps.append({
            "type": "graph_init",
            "graph": self.graph,
            "start_node": self.start_node,
            "algorithm": "Dijkstra"
        })
        
        # Если стартовый узел не существует в графе
        if self.start_node not in self.graph:
            self.steps.append({
                "type": "complete",
                "distances": {},
                "description": f"Стартовый узел {self.start_node} не найден в графе."
            })
            return
        
        # Инициализация расстояний
        for node in self.graph:
            self.distances[node] = math.inf
        self.distances[self.start_node] = 0
        
        # Приоритетная очередь
        priority_queue = [(0, self.start_node)]
        
        # Шаг 2: Посещение стартового узла
        self.steps.append({
            "type": "visit",
            "node": self.start_node,
            "distance": 0,
            "description": f"Начинаем с узла {self.start_node}, расстояние = 0"
        })
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            # Если узел уже посещен, пропускаем
            if current_node in self.visited:
                continue
                
            # Помечаем узел как посещенный
            self.visited.add(current_node)
            
            # Шаг 3: Посещение узла
            if current_node != self.start_node:
                self.steps.append({
                    "type": "visit",
                    "node": current_node,
                    "distance": current_distance,
                    "description": f"Посещаем узел {current_node}, расстояние = {current_distance}"
                })
            
            # Получаем соседей текущего узла
            neighbor_items = self._get_neighbors_with_weights(current_node)
            
            # Обновляем расстояния до соседей
            for neighbor, weight in neighbor_items:
                if neighbor not in self.graph:
                    continue
                    
                distance = current_distance + weight
                
                # Если нашли более короткий путь
                if distance < self.distances[neighbor]:
                    old_distance = self.distances[neighbor]
                    self.distances[neighbor] = distance
                    self.previous[neighbor] = current_node
                    
                    # Шаг 4: Обновление расстояния
                    self.steps.append({
                        "type": "update_distance",
                        "node": neighbor,
                        "old_distance": old_distance if old_distance != math.inf else "∞",
                        "new_distance": distance,
                        "description": f"Обновляем расстояние до узла {neighbor}: {old_distance if old_distance != math.inf else '∞'} -> {distance}"
                    })
                    
                    heapq.heappush(priority_queue, (distance, neighbor))
        
        # Шаг 5: Завершение
        self.steps.append({
            "type": "complete",
            "distances": self.distances,
            "description": f"Алгоритм Дейкстры завершен. Найдены кратчайшие пути из узла {self.start_node}"
        })