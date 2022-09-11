from models.edge import Rib
from PyQt5.QtGui import QPainter, QPen, QFont, QPolygon
from PyQt5.QtCore import Qt
from settings import BLACK, WHITE
from math import atan2, cos, sin, degrees
from functions import get_equilateral_triangle, \
    get_intersect_point, get_angle, get_triangle_center


class CanvasEdge:
    """Класс для ребра на холсте"""
    def __init__(self, n1, n2, rib: Rib, parent):
        self.parent = parent
        self.weight = rib.weight
        self.is_directed = rib.is_directed
        self.start = n1
        self.end = n2

    def draw(self):
        """Рисование ребра"""
        self.parent.qp.setPen(QPen(BLACK, self.parent.dist // 10, Qt.SolidLine))
        x1, y1 = self.parent.getPointCenter(self.start.row, self.start.col)
        x2, y2 = self.parent.getPointCenter(self.end.row, self.end.col)
        self.parent.qp.drawLine(x1, y1, x2, y2)
        self.draw_label()
        if self.is_directed:
            self.draw_arrow()

    def draw_arrow(self):
        """Рисование стрелки с направлением ребра"""
        dist = self.parent.dist
        side = dist // 2
        xc, yc = self.parent.getPointCenter(self.end.row, self.end.col)
        angle = get_angle(self.start.row, self.start.col,
                          self.end.row, self.end.col)
        x, y = get_intersect_point(xc, yc, dist, angle)
        print((xc, yc), (x, y), degrees(angle))
        points = get_equilateral_triangle(x, y, side, angle)
        self.parent.qp.setBrush(BLACK)
        self.parent.qp.drawPolygon(QPolygon([j for i in points for j in i]))
    def draw_label(self):
        """Рисование метки с весом ребра"""
        dist = self.parent.dist
        x1, y1 = self.parent.getPointCenter(self.start.row, self.start.col)
        x2, y2 = self.parent.getPointCenter(self.end.row, self.end.col)
        self.parent.qp.setPen(QPen(BLACK, dist // 20, Qt.SolidLine))
        self.parent.qp.setBrush(WHITE)
        font = QFont()
        font.setPixelSize(dist // 5)
        self.parent.qp.setFont(font)
        xm = (x1 + x2) // 2
        ym = (y1 + y2) // 2
        r_x, r_y, r_w, r_h = xm - dist // 3, ym - dist // 4, dist // 1.5, dist // 2
        self.parent.qp.drawRect(r_x, r_y, r_w, r_h)
        self.parent.qp.drawText(r_x, r_y, r_w, r_h, Qt.AlignCenter, str(self.weight))