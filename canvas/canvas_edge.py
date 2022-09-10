from models.edge import Rib
from PyQt5.QtGui import QPainter, QPen, QTextItem, QFont
from PyQt5.QtCore import Qt
from settings import BLACK, WHITE


class CanvasEdge:
    """Класс для ребра на холсте"""
    def __init__(self, rib: Rib):
        self.rib_id = rib.id
        self.weight = rib.weight
        self.is_directed = rib.is_directed
        self.start_cell = rib.nodes[0].cell
        self.end_cell = rib.nodes[1].cell

    def draw(self, qp: QPainter, p1: tuple[int, int], p2: tuple[int, int], dist: int):
        """Рисование ребра"""
        qp.setPen(QPen(BLACK, dist // 10, Qt.SolidLine))
        x1, y1 = p1[0] + dist // 2, p1[1] + dist // 2
        x2, y2 = p2[0] + dist // 2, p2[1] + dist // 2
        qp.drawLine(x1, y1, x2, y2)
        self.draw_label(qp, x1, y1, x2, y2, dist)

    def draw_label(self, qp: QPainter, x1, y1, x2, y2, dist):
        """Рисование метки с весом ребра"""
        qp.setPen(QPen(BLACK, dist // 20, Qt.SolidLine))
        qp.setBrush(WHITE)
        font = QFont()
        font.setPixelSize(dist // 20)
        xm = (x1 + x2) // 2
        ym = (y1 + y2) // 2
        r_x, r_y, r_w, r_h = xm - dist // 2, ym - dist // 4, dist, dist // 2
        qp.drawRect(r_x, r_y, r_w, r_h)
        qp.drawText(r_x, r_y, r_w, r_h, Qt.AlignCenter, str(self.weight))