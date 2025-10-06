from ..base_algorithm import BaseAlgorithm

class GraphBFS(BaseAlgorithm):
    """BFS с генератором шагов"""
    def __init__(self, graph, start):
        super().__init__(graph)
        self.queue = [start]
        self.visited = set([start])

    def step_generator(self):
        while self.queue:
            node = self.queue.pop(0)
            yield {"type": "visit", "node": node}
            for neighbor in self.data[node]:
                if neighbor not in self.visited:
                    self.queue.append(neighbor)
                    self.visited.add(neighbor)
