from ..base_algorithm import BaseAlgorithm

class MergeSort(BaseAlgorithm):
    """Пошаговый MergeSort для визуализации."""
    def step_generator(self):
        arr = self.data

        def merge_sort(left, right):
            if left < right:
                mid = (left + right) // 2
                yield from merge_sort(left, mid)
                yield from merge_sort(mid + 1, right)

                # Слияние
                merged = []
                i, j = left, mid + 1
                while i <= mid and j <= right:
                    yield {"type": "compare", "indices": (i, j), "array": arr.copy()}
                    if arr[i] <= arr[j]:
                        merged.append(arr[i])
                        i += 1
                    else:
                        merged.append(arr[j])
                        j += 1

                while i <= mid:
                    merged.append(arr[i])
                    i += 1
                while j <= right:
                    merged.append(arr[j])
                    j += 1

                for k, val in enumerate(merged):
                    arr[left + k] = val
                    yield {"type": "insert", "indices": (left + k,), "array": arr.copy()}

        yield from merge_sort(0, len(arr) - 1)
        yield {"type": "complete", "array": arr.copy()}
