from PyQt5.QtGui import QFont
from settings import BLACK
from PyQt5.Qt import QStandardItem


class TreeItem(QStandardItem):
    """Класс для элемента в дереве элементов графа"""
    def __init__(self, text="", font=10, bold=False, color=BLACK):
        super().__init__()
        fnt = QFont("Open Sans", font)
        fnt.setBold(bold)
        self.setFont(fnt)
        self.setEditable(False)
        self.setForeground(color)
        self.setText(text)
