from ..base_algorithm import BaseAlgorithm

class MergeSort(BaseAlgorithm):
    """MergeSort с генератором шагов"""
    def step_generator(self):
        arr = self.data

        def merge_sort(arr, left, right):
            if left < right:
                mid = (left + right) // 2
                yield from merge_sort(arr, left, mid)
                yield from merge_sort(arr, mid + 1, right)
                # слияние
                merged = []
                i, j = left, mid + 1
                while i <= mid and j <= right:
                    yield {"type": "compare", "indices": (i, j)}
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
                    yield {"type": "insert", "index": left + k, "value": val, "array": arr.copy()}

        yield from merge_sort(arr, 0, len(arr) - 1)
