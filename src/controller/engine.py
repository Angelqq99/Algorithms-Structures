"""
Контроллер (Engine) — управляет связью между моделью и визуализацией.
"""
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class Engine(QObject):
    step_ready = pyqtSignal(dict)  # сигнал с действием от модели

    def __init__(self):
        super().__init__()
        self.algorithm = None
        self.generator = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_tick)
        self.running = False

    def load_algorithm(self, algorithm):
        self.algorithm = algorithm
        self.generator = algorithm.step_generator()

    def step(self):
        """Выполняет один шаг алгоритма."""
        if not self.generator:
            return
        try:
            action = next(self.generator)
            self.step_ready.emit(action)
        except StopIteration:
            self.pause()

    def run(self, interval_ms=300):
        self.running = True
        self.timer.start(interval_ms)

    def pause(self):
        self.running = False
        self.timer.stop()

    def _on_tick(self):
        self.step()
