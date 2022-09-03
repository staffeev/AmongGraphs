import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor
from settings import BLACK, DEFAULT_DIST, ZOOM_STEP


class Canvas(QWidget):
    """Класс холста для рисования графов"""

    def __init__(self, rows, cols):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.zoom = 1
        self.dist = DEFAULT_DIST * self.zoom
        self.setGeometry(300, 300, self.dist * cols, self.dist * rows)

    def wheelEvent(self, event) -> None:
        """Изменение масштаба холста посредством кручения колеса мыши"""
        if event.angleDelta().y() > 0:
            self.zoom = min(self.zoom * ZOOM_STEP, 32)
        else:
            self.zoom = max(self.zoom / ZOOM_STEP, 0.1)

        self.calc_dist()
        self.repaint()

    def paintEvent(self, event) -> None:
        """Событие отрисовки графа"""
        qp = QPainter()
        qp.begin(self)
        self.drawGrid(qp)
        qp.end()

    def drawGrid(self, qp) -> None:
        """Отрисовка сетки"""
        qp.setPen(BLACK)
        for i in range(self.rows + 1):
            qp.drawLine(0, i * self.dist, self.get_width(), i * self.dist)
        for i in range(self.cols + 1):
            qp.drawLine(i * self.dist, 0, i * self.dist, self.get_height())

    def get_width(self) -> int:
        """Возвращает ширину виджета"""
        return self.dist * self.cols

    def get_height(self) -> int:
        """Возвращает высоту виджета"""
        return self.dist * self.rows

    def calc_dist(self) -> None:
        """Пересчёт расстояния между линиями сетки"""
        self.dist = DEFAULT_DIST * self.zoom


        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Canvas(*map(int, input().split()))
    ex.show()
    sys.exit(app.exec())
