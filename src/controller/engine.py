from PyQt6.QtCore import QObject, pyqtSignal, QTimer

class Engine(QObject):
    """Контроллер для управления выполнением алгоритмов."""
    
    step_ready = pyqtSignal(dict)  # Сигнал с действием для визуализации
    
    def __init__(self):
        super().__init__()
        self.generator = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_tick)
        self.speed_multiplier = 1.0
        self.is_paused = False
        
    def load_algorithm(self, algorithm):
        """Загрузка алгоритма и его генератора."""
        self.algorithm = algorithm
        self.generator = algorithm.step_generator()
        self.is_paused = False
        
    def set_speed(self, multiplier):
        """Установка множителя скорости."""
        self.speed_multiplier = multiplier
        
    def run(self, interval_ms=500):
        """Запуск автоматического выполнения."""
        if self.generator and not self.timer.isActive():
            interval = max(50, int(interval_ms / self.speed_multiplier))
            self.timer.start(interval)
            self.is_paused = False
            
    def pause(self):
        """Пауза выполнения."""
        if self.timer.isActive():
            self.timer.stop()
        self.is_paused = True
            
    def step(self):
        """Выполнение одного шага вручную."""
        if self.is_paused or not self.generator:
            return False
            
        try:
            action = next(self.generator)
            self.step_ready.emit(action)
            return True
        except StopIteration:
            return False
            
    def _on_tick(self):
        """Обработчик таймера для автоматического режима."""
        if not self.step():
            self.timer.stop()