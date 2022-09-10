from models.elements import Vertex
from settings import RED, BLACK
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtCore import Qt


class CanvasNode:
    """Класс для вершины на холсте"""
    def __init__(self, node: Vertex):
        self.node_id = node.id
        self.node_name = node.name
        self.row, self.col = node.cell

    def setName(self, name: str):
        """Установка нового имени"""
        self.node_name = name

    def setColor(self) -> None:
        """Установка цвета в зависимости от количества сязаннных ребер"""
        # TODO

    def draw(self, qp: QPainter, p: tuple[int, int], dist: int, color=RED) -> None:
        """Рисование вершины"""
        # TODO
        font = QFont()
        font.setPixelSize(dist // 2)
        qp.setBrush(color)
        qp.setPen(BLACK)
        qp.setFont(font)
        qp.drawEllipse(*p, dist, dist)
        qp.drawText(*p, dist, dist, Qt.AlignCenter, self.node_name)

    def checkCollide(self) -> None:
        # TODO
        pass

    def select(self) -> None:
        """Метод для выделения вершины"""
        # TODO
        pass


