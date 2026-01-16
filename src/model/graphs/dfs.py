
"""
Алгоритм обхода графа в глубину (DFS).
"""


class GraphDFS:
    def __init__(self, graph, start_node):
        self.graph = graph
        self.start = start_node
        self.steps = []
        self.visited = set()
        self.stack = []

    def _initialize_dfs(self):
        """Инициализация DFS."""
        self.steps = []
        self.visited = set()
        self.stack = []
        
        # Инициализация
        self.visited.add(self.start)
        self.stack.append(self.start)
        
        # Шаг: инициализация
        self.steps.append({
            "type": "info",
            "description": f"Инициализация DFS: начальный узел {self.start}"
        })
        
        # Шаг: посещение начального узла
        self.steps.append({
            "type": "visit",
            "node": self.start,
            "description": f"Посещен начальный узел {self.start}"
        })

    def _perform_dfs(self):
        """Выполнение DFS с использованием стека."""
        iteration = 0
        
        while self.stack:
            current = self.stack.pop()
            iteration += 1
            
            # Шаг: обработка текущего узла
            self.steps.append({
                "type": "info",
                "description": f"Итерация {iteration}: обработка узла {current}"
            })
            
            # Получаем соседей
            neighbors = list(self.graph.get(current, {}).keys())
            
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
                    self.stack.append(neighbor)
                    
                    self.steps.append({
                        "type": "visit",
                        "node": neighbor,
                        "description": f"Найден новый узел {neighbor}, добавлен в стек"
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
            "description": f"DFS завершен. Посещено узлов: {len(self.visited)}",
            "visited_count": len(self.visited),
            "visited_nodes": list(self.visited)
        })

    def step_generator(self):
        """Генератор шагов DFS."""
        if not self.steps:
            self._initialize_dfs()
            self._perform_dfs()
        
        for step in self.steps:
            yield step

    def get_generator(self):
        """Возвращает генератор шагов."""
        return self.step_generator()
