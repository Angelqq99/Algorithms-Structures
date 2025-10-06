from ..base_algorithm import BaseAlgorithm
import heapq

class Dijkstra(BaseAlgorithm):
    """Dijkstra с генератором шагов"""
    def __init__(self, graph, start):
        super().__init__(graph)
        self.start = start

    def step_generator(self):
        graph = self.data
        dist = {node: float('inf') for node in graph}
        dist[self.start] = 0
        heap = [(0, self.start)]

        while heap:
            d, u = heapq.heappop(heap)
            yield {"type": "visit", "node": u, "distance": d}
            for v, w in graph.get(u, []):
                if dist[v] > dist[u] + w:
                    dist[v] = dist[u] + w
                    heapq.heappush(heap, (dist[v], v))
