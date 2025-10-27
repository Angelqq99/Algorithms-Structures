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
        """Загрузка алгоритма и инициализация генератора."""
        self.algorithm = algorithm
        if hasattr(algorithm, 'step_generator'):
            self.generator = algorithm.step_generator()
        else:
            self.generator = None

    def step(self):
        """Выполняет один шаг алгоритма."""
        if not self.generator:
            return
            
        try:
            action = next(self.generator)
            self.step_ready.emit(action)
        except StopIteration:
            self.pause()
            self.step_ready.emit({"type": "complete", "message": "Algorithm finished"})

    def run(self, interval_ms=300):
        """Запуск автоматического выполнения."""
        if self.generator:
            self.running = True
            self.timer.start(interval_ms)

    def pause(self):
        """Пауза выполнения."""
        self.running = False
        if self.timer.isActive():
            self.timer.stop()

    def _on_tick(self):
        """Обработчик таймера для автоматического режима."""
        if self.running:
            self.step()