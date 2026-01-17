"""
Алгоритм обхода графа в глубину (DFS) - рекурсивная версия.
"""

class GraphDFS:
    def __init__(self, graph, start_node):
        self.graph = graph
        self.start = start_node
        self.steps = []
        self.visited = set()
        self._recursive_dfs(start_node, 0)

    def _recursive_dfs(self, node, depth):
        """Рекурсивный DFS с отслеживанием глубины."""
        # Шаг: вход в узел
        self.steps.append({
            "type": "visit",
            "node": node,
            "description": f"📍 Вход в узел {node} (глубина: {depth})",
            "depth": depth
        })
        
        self.visited.add(node)
        
        # Ищем соседей
        neighbors = self.graph.get(node, {})
        for neighbor in neighbors:
            # Шаг: проверка соседа
            self.steps.append({
                "type": "discover",
                "from_node": node,
                "node": neighbor,
                "description": f"🔍 Проверка соседа {neighbor}",
                "weight": neighbors.get(neighbor, 1)
            })
            
            if neighbor not in self.visited:
                # Рекурсивный вызов
                self._recursive_dfs(neighbor, depth + 1)
                
                # Шаг: возврат из рекурсии (опционально)
                self.steps.append({
                    "type": "info",
                    "description": f"↩️ Возврат к узлу {node}"
                })
            else:
                # Шаг: уже посещен
                self.steps.append({
                    "type": "info",
                    "description": f"⏭️ Сосед {neighbor} уже посещен"
                })
        
        # Шаг: выход из узла
        self.steps.append({
            "type": "info",
            "description": f"⬅️ Выход из узла {node}"
        })

    def step_generator(self):
        # Добавляем финальный шаг
        final_steps = self.steps.copy()
        final_steps.append({
            "type": "complete",
            "description": f"✅ Рекурсивный DFS завершен!",
            "visited_nodes": sorted(self.visited),
            "total_nodes": len(self.visited)
        })
        
        for step in final_steps:
            yield step

    def get_generator(self):
        """Возвращает генератор шагов."""
        return self.step_generator()
    