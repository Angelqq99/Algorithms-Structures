
"""
Алгоритм обхода графа в ширину (BFS).
"""
from collections import deque


class GraphBFS:
    def __init__(self, graph, start_node):
        self.graph = graph
        self.start = start_node
        self.steps = []
        self.visited = set()
        self.queue = deque()

    def _initialize_bfs(self):
        """Инициализация BFS."""
        self.steps = []
        self.visited = set()
        self.queue = deque()
        
        # Инициализация
        self.visited.add(self.start)
        self.queue.append(self.start)
        
        # Шаг: инициализация
        self.steps.append({
            "type": "info",
            "description": f"Инициализация BFS: начальный узел {self.start}"
        })
        
        # Шаг: посещение начального узла
        self.steps.append({
            "type": "visit",
            "node": self.start,
            "description": f"Посещен начальный узел {self.start}"
        })

    def _perform_bfs(self):
        """Выполнение BFS."""
        iteration = 0
        
        while self.queue:
            current = self.queue.popleft()
            iteration += 1
            
            # Шаг: обработка текущего узла
            self.steps.append({
                "type": "info",
                "description": f"Итерация {iteration}: обработка узла {current}"
            })
            
            # Получаем соседей
            neighbors = self.graph.get(current, {})
            
            for neighbor in neighbors:
                # Шаг: проверка соседа
                self.steps.append({
                    "type": "discover",
                    "from_node": current,
                    "node": neighbor,
                    "description": f"Проверка соседа {neighbor} из узла {current}"
                })
                
                if neighbor not in self.visited:
                    # Шаг: посещение нового узла
                    self.visited.add(neighbor)
                    self.queue.append(neighbor)
                    
                    self.steps.append({
                        "type": "visit",
                        "node": neighbor,
                        "description": f"Найден новый узел {neighbor}, добавлен в очередь"
                    })
                else:
                    # Шаг: узел уже посещен
                    self.steps.append({
                        "type": "info",
                        "description": f"Узел {neighbor} уже посещен ранее"
                    })
            
            # Шаг: завершение обработки узла
            self.steps.append({
                "type": "info",
                "description": f"Завершена обработка узла {current}"
            })
        
        # Шаг: завершение алгоритма
        self.steps.append({
            "type": "complete",
            "description": f"BFS завершен. Посещено узлов: {len(self.visited)}",
            "visited_count": len(self.visited),
            "visited_nodes": list(self.visited)
        })

    def step_generator(self):
        """Генератор шагов BFS."""
        if not self.steps:
            self._initialize_bfs()
            self._perform_bfs()
        
        for step in self.steps:
            yield step

    def get_generator(self):
        """Возвращает генератор шагов."""
        return self.step_generator()
