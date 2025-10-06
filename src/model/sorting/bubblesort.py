from ..base_algorithm import BaseAlgorithm

class BubbleSort(BaseAlgorithm):
    """BubbleSort с генератором шагов"""
    def step_generator(self):
        arr = self.data
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                yield {"type": "compare", "indices": (j, j+1)}
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                    yield {"type": "swap", "indices": (j, j+1), "array": arr.copy()}
