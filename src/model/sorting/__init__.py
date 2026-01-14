"""
Пакет сортировок для визуализатора алгоритмов.
"""

from .quicksort import QuickSort
from .mergesort import MergeSort
from .bubblesort import BubbleSort
from .insertionsort import InsertionSort
from .selectionsort import SelectionSort
from .shellsort import ShellSort

__all__ = [
    'QuickSort',
    'MergeSort', 
    'BubbleSort',
    'InsertionSort',
    'SelectionSort',
    'ShellSort'
]