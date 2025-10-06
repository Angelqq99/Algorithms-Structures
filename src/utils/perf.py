"""
Инструменты производительности: профилирование и троттлинг.
"""
import time
from functools import wraps

def profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"[PROFILE] {func.__name__}: {elapsed:.2f} ms")
        return result
    return wrapper
