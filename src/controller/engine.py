"""Контроллер (Engine) — управляет связью между моделью и визуализацией."""
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
        self.current_interval = 300
        self.manual_mode = False

    def load_algorithm(self, algorithm):
        """Загрузка алгоритма и инициализация генератора."""
        self.algorithm = algorithm
        if hasattr(algorithm, 'step_generator'):
            self.generator = algorithm.step_generator()
        else:
            self.generator = None

    def step(self):
        """Выполняет один шаг алгоритма в ручном режиме."""
        if not self.generator:
            return False
            
        try:
            action = next(self.generator)
            self.step_ready.emit(action)
            return True
        except StopIteration:
            self.pause()
            self.step_ready.emit({"type": "complete", "message": "Algorithm finished"})
            return False

    def run(self, interval_ms=300):
        """Запуск автоматического выполнения."""
        if self.generator:
            self.running = True
            self.manual_mode = False
            self.current_interval = interval_ms
            self.timer.start(interval_ms)

    def pause(self):
        """Пауза выполнения."""
        self.running = False
        if self.timer.isActive():
            self.timer.stop()

    def set_speed(self, speed_multiplier):
        """Установка скорости выполнения."""
        new_interval = max(50, int(600 / speed_multiplier))
        self.current_interval = new_interval
        
        if self.timer.isActive():
            self.timer.setInterval(new_interval)

    def _on_tick(self):
        """Обработчик таймера для автоматического режима."""
        if self.running and self.generator:
            try:
                action = next(self.generator)
                self.step_ready.emit(action)
            except StopIteration:
                self.pause()
                self.step_ready.emit({"type": "complete", "message": "Algorithm finished"})