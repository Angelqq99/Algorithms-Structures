"""
Команды управления (Command pattern): шаг вперёд, назад, установка брейкпоинтов.
"""


class Command:
    def execute(self):
        raise NotImplementedError


class StepForward(Command):
    def __init__(self, engine):
        self.engine = engine

    def execute(self):
        self.engine.step()


class StepBackward(Command):
    """Пока не реализовано (понадобится Memento)."""
    def __init__(self, engine):
        self.engine = engine

    def execute(self):
        pass


class BreakpointCommand(Command):
    def __init__(self, engine, index):
        self.engine = engine
        self.index = index

    def execute(self):
        print(f"Установлен брейкпоинт на шаге {self.index}")
