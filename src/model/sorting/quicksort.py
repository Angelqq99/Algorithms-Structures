from ..base_algorithm import BaseAlgorithm

class QuickSort(BaseAlgorithm):
    """Пошаговый QuickSort с генерацией сравнений и обменов."""
    def step_generator(self):
        arr = self.data
        stack = [(0, len(arr) - 1)]

        while stack:
            low, high = stack.pop()
            if low < high:
                pivot = arr[high]
                i = low
                for j in range(low, high):
                    yield {"type": "compare", "indices": (j, high), "array": arr.copy()}
                    if arr[j] < pivot:
                        arr[i], arr[j] = arr[j], arr[i]
                        yield {"type": "swap", "indices": (i, j), "array": arr.copy()}
                        i += 1

                arr[i], arr[high] = arr[high], arr[i]
                yield {"type": "swap", "indices": (i, high), "array": arr.copy()}
                stack.append((low, i - 1))
                stack.append((i + 1, high))

        yield {"type": "complete", "array": arr.copy()}
