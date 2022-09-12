from PyQt5.QtWidgets import QMenu


class CanvasMenu(QMenu):
    """Класс для контекстного меню в холсте"""

    def __init__(self, parent=None):
        super().__init__(parent)
