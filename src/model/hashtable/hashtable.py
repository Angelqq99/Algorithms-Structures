from ..base_algorithm import BaseAlgorithm

class HashTable(BaseAlgorithm):
    """Простая хэш-таблица с генератором операций"""
    def __init__(self, data, size=10):
        super().__init__(data)
        self.size = size
        self.table = [None] * size

    def _hash(self, key):
        return key % self.size

    def step_generator(self):
        for key in self.data:
            idx = self._hash(key)
            # Простое линейное пробирование
            original_idx = idx
            while self.table[idx] is not None:
                yield {"type": "collision", "index": idx, "key": key}
                idx = (idx + 1) % self.size
                if idx == original_idx:
                    break
            self.table[idx] = key
            yield {"type": "insert", "index": idx, "key": key, "table": self.table.copy()}
