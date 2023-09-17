from models.node import Vertex
from settings import RED, BLACK, SELECTED_ITEM_COLOR
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class CanvasNode:
    """Класс для вершины на холсте"""
    def __init__(self, node: Vertex, parent):
        self.parent = parent
        self.node_id = node.id
        self.node_name = node.name
        self.color = RED
        self.row, self.col = node.cell
        self.selected = False

    def __str__(self):
        return self.node_name

    def setColor(self, color):
        self.color = color

    def setName(self, name: str):
        """Установка нового имени"""
        self.node_name = name

    def setCell(self, row, col):
        """Установка новых координат"""
        self.row, self.col = row, col

    def select(self):
        self.selected = True

    def unselect(self):
        self.selected = False

    def draw(self):
        """Рисование вершины"""
        dist = self.parent.dist
        x, y = self.parent.getPoint(self.row, self.col)
        font = QFont()
        font.setPixelSize(int(dist // 2))
        self.parent.qp.setBrush(SELECTED_ITEM_COLOR if self.selected else self.color)
        self.parent.qp.setPen(BLACK)
        self.parent.qp.setFont(font)
        self.parent.qp.drawEllipse(int(x), int(y), int(dist), int(dist))
        self.parent.qp.drawText(int(x), int(y), int(dist), int(dist), Qt.AlignCenter, self.node_name)

