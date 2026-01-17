"""
Алгоритм обхода графа в ширину (BFS).
"""
from collections import deque


class GraphBFS:
    def __init__(self, graph, start_node):
        self.graph = graph
        self.start = start_node
        self.steps = []
        self._create_compact_steps()

    def _create_compact_steps(self):
        """Создает компактные шаги для быстрой визуализации."""
        visited = {self.start}
        queue = deque([self.start])
        level = 0
        
        # Шаг 1: Старт
        self.steps.append({
            "type": "visit",
            "node": self.start,
            "description": f"🚀 Начальный узел: {self.start}"
        })
        
        while queue:
            level_size = len(queue)
            level_nodes = []
            
            for _ in range(level_size):
                current = queue.popleft()
                level_nodes.append(current)
                
                # Находим всех новых соседей
                neighbors = self.graph.get(current, {})
                new_neighbors = []
                
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        new_neighbors.append(neighbor)
                
                # Если есть новые соседи, добавляем ОДИН шаг для них всех
                if new_neighbors:
                    for neighbor in new_neighbors:
                        self.steps.append({
                            "type": "discover",
                            "from_node": current,
                            "node": neighbor,
                            "description": f"🔍 {current} → {neighbor}",
                            "weight": neighbors.get(neighbor, 1)
                        })
                        
                        self.steps.append({
                            "type": "visit",
                            "node": neighbor,
                            "description": f"✅ Посещен: {neighbor}"
                        })
            
            # Шаг: завершение уровня (опционально, можно убрать для скорости)
            if level_nodes:
                self.steps.append({
                    "type": "info",
                    "description": f"📊 Уровень {level} завершен: {len(level_nodes)} узлов"
                })
            
            level += 1
        
        # Финальный шаг
        self.steps.append({
            "type": "complete",
            "description": f"✅ BFS завершен!",
            "visited_nodes": sorted(visited),
            "total_nodes": len(visited),
            "total_levels": level - 1
        })

    def step_generator(self):
        for step in self.steps:
            yield step
    