from ..base_algorithm import BaseAlgorithm

class GraphDFS(BaseAlgorithm):
    """DFS с генератором шагов"""
    def __init__(self, graph, start):
        super().__init__(graph)
        self.start = start

    def step_generator(self):
        visited = set()
        stack = [self.start]

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                yield {"type": "visit", "node": node}
                # Добавляем соседей в стек
                for neighbor in reversed(self.data[node]):
                    if neighbor not in visited:
                        stack.append(neighbor)
