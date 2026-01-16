"""
Алгоритм Дейкстры для поиска кратчайших путей - исправленная версия.
"""
import heapq
import math
from PyQt6.QtCore import pyqtSignal, QObject

class Dijkstra(QObject):
    """Класс алгоритма Дейкстры с поддержкой пошаговой визуализации."""
    
    # Сигналы для безопасного взаимодействия с GUI потоком
    step_generated = pyqtSignal(dict)
    
    def __init__(self, graph, start_node):
        super().__init__()
        self.graph = graph
        self.start_node = start_node
        self.distances = {}
        self.previous = {}
        self.visited = set()
        self.priority_queue = []
        self.current_node = None
        self.is_initialized = False
        
    def _initialize_dijkstra(self):
        """Инициализация алгоритма."""
        # Если стартовый узел не существует в графе
        if self.start_node not in self.graph:
            yield {
                "type": "complete",
                "distances": {},
                "description": f"Стартовый узел {self.start_node} не найден в графе."
            }
            return
        
        # Инициализация расстояний
        for node in self.graph:
            self.distances[node] = math.inf
        self.distances[self.start_node] = 0
        
        # Приоритетная очередь
        heapq.heappush(self.priority_queue, (0, self.start_node))
        
        # Шаг 1: Инициализация графа
        yield {
            "type": "graph_init",
            "graph": self.graph,
            "start_node": self.start_node,
            "algorithm": "Dijkstra"
        }
        
        # Шаг 2: Посещение стартового узла
        yield {
            "type": "visit",
            "node": self.start_node,
            "distance": 0,
            "description": f"Начинаем с узла {self.start_node}, расстояние = 0"
        }
        
        self.is_initialized = True
    
    def step(self):
        """Выполняет один шаг алгоритма."""
        if not self.is_initialized:
            # Инициализируем при первом вызове
            return next(self._initialize_dijkstra())
        
        if not self.priority_queue:
            # Алгоритм завершен
            return {
                "type": "complete",
                "distances": self.distances,
                "description": f"Алгоритм Дейкстры завершен. Найдены кратчайшие пути из узла {self.start_node}"
            }
        
        # Извлекаем узел с наименьшим расстоянием
        current_distance, self.current_node = heapq.heappop(self.priority_queue)
        
        # Если узел уже посещен, пропускаем
        if self.current_node in self.visited:
            # Продолжаем со следующим шагом
            return self.step()
        
        # Помечаем узел как посещенный
        self.visited.add(self.current_node)
        
        # Шаг 3: Посещение узла
        action = {
            "type": "visit",
            "node": self.current_node,
            "distance": current_distance,
            "description": f"Посещаем узел {self.current_node}, расстояние = {current_distance}"
        }
        
        # Обрабатываем соседей
        self._process_neighbors(current_distance)
        
        return action
    
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
    
    def _process_neighbors(self, current_distance):
        """Обрабатывает соседей текущего узла."""
        neighbor_items = self._get_neighbors_with_weights(self.current_node)
        
        for neighbor, weight in neighbor_items:
            if neighbor not in self.graph:
                continue
                
            distance = current_distance + weight
            
            # Если нашли более короткий путь
            if distance < self.distances[neighbor]:
                old_distance = self.distances[neighbor]
                self.distances[neighbor] = distance
                self.previous[neighbor] = self.current_node
                
                # Добавляем действие обновления расстояния
                # Вместо непосредственной отправки, сохраняем в списке действий
                self.step_generated.emit({
                    "type": "update_distance",
                    "node": neighbor,
                    "old_distance": old_distance if old_distance != math.inf else "∞",
                    "new_distance": distance,
                    "description": f"Обновляем расстояние до узла {neighbor}: {old_distance if old_distance != math.inf else '∞'} -> {distance}"
                })
                
                heapq.heappush(self.priority_queue, (distance, neighbor))
    
    def get_generator(self):
        """Возвращает генератор шагов."""
        yield from self._initialize_dijkstra()
        
        while self.priority_queue:
            yield self.step()
        
        yield {
            "type": "complete",
            "distances": self.distances,
            "description": f"Алгоритм Дейкстры завершен. Найдены кратчайшие пути из узла {self.start_node}"
        }
    
    def step_generator(self):
        """Генератор шагов для движка."""
        return self.get_generator()