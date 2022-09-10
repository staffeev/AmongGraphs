from models.edge import Rib
from PyQt5.QtGui import QPainter, QPen, QFont, QPolygon
from PyQt5.QtCore import Qt
from settings import BLACK, WHITE
from math import atan2, cos, sin
from functions import rotate_figure, get_equilateral_triangle


class CanvasEdge:
    """Класс для ребра на холсте"""
    def __init__(self, n1, n2, rib: Rib, parent):
        self.parent = parent
        self.weight = rib.weight
        self.is_directed = rib.is_directed
        self.start = n1
        self.end = n2

    def draw(self, qp: QPainter, dist: int):
        """Рисование ребра"""
        qp.setPen(QPen(BLACK, dist // 10, Qt.SolidLine))
        x1, y1 = self.parent.getPoint(self.start.row, self.start.col)
        x1 += dist // 2
        y1 += dist // 2

        x2, y2 = self.parent.getPoint(self.end.row, self.end.col)
        x2 += dist // 2
        y2 += dist // 2

        # x1, y1 = p1[0] + dist // 2, p1[1] + dist // 2
        # x2, y2 = p2[0] + dist // 2, p2[1] + dist // 2
        qp.drawLine(x1, y1, x2, y2)
        self.draw_label(qp, x1, y1, x2, y2, dist)
        # if self.is_directed:
        #     self.draw_arrow(qp, x1, y1, x2, y2, dist)

    # def draw(self, qp: QPainter, p1: tuple[int, int], p2: tuple[int, int], dist: int):
    #     """Рисование ребра"""
    #     qp.setPen(QPen(BLACK, dist // 10, Qt.SolidLine))
    #     x1, y1 = self.parent.getPoint(self.start.row, self.start.col)
    #     x1 += dist // 2
    #     y1 += dist // 2
    #
    #     x2, y2 = self.parent.getPoint(self.end.row, self.end.col)
    #     x2 += dist // 2
    #     y2 += dist // 2
    #
    #     # x1, y1 = p1[0] + dist // 2, p1[1] + dist // 2
    #     # x2, y2 = p2[0] + dist // 2, p2[1] + dist // 2
    #     qp.drawLine(x1, y1, x2, y2)
    #     self.draw_label(qp, x1, y1, x2, y2, dist)
    #     # if self.is_directed:
    #     #     self.draw_arrow(qp, x1, y1, x2, y2, dist)

    def draw_arrow(self, qp: QPainter, x1, y1, x2, y2, dist):
        """Рисование стрелки с направлением ребра"""
        side = dist // 2
        x, y = self.get_intersect_point(x1, y1, x2, y2, dist)
        alpha = atan2(y2 - y1, x2 - x1)
        points = get_equilateral_triangle(x, y, side)
        rotated_points = rotate_figure(points, alpha, x2, y2)
        # rotated_points = points
        qp.setBrush(BLACK)
        qp.drawPolygon(QPolygon([j for i in rotated_points for j in i]))


    def draw_label(self, qp: QPainter, x1, y1, x2, y2, dist):
        """Рисование метки с весом ребра"""
        qp.setPen(QPen(BLACK, dist // 20, Qt.SolidLine))
        qp.setBrush(WHITE)
        font = QFont()
        font.setPixelSize(dist // 5)
        qp.setFont(font)
        xm = (x1 + x2) // 2
        ym = (y1 + y2) // 2
        r_x, r_y, r_w, r_h = xm - dist // 3, ym - dist // 4, dist // 1.5, dist // 2
        qp.drawRect(r_x, r_y, r_w, r_h)
        qp.drawText(r_x, r_y, r_w, r_h, Qt.AlignCenter, str(self.weight))

    def get_intersect_point(self, x1, y1, x2, y2, dist):
        """Нахождение точки пересечения окружности вершины с ребром"""
        alpha = atan2(y2 - y1, x2 - x1)
        side = dist // 3
        x = side * cos(alpha)
        y = side * sin(alpha)
        return x2 + x, y2 - y




        pass
        pass