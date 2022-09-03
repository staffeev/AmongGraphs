import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt
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
        self.move_canvas = False
        self.dif_x = self.dif_y = 0
        self.x = self.y = 0

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
            qp.drawLine(self.x, self.y + i * self.dist,
                        self.x + self.getWidth(), self.y + i * self.dist)
        for i in range(self.cols + 1):
            qp.drawLine(self.x + i * self.dist, self.y,
                        self.x + i * self.dist, self.y + self.getHeight())

    def checkBorders(self) -> None:
        """Проверка на то, находится ли холст в границах виджета"""
        self.x = max(self.x, 0)
        self.y = max(self.y, 0)
        if self.x + self.getWidth() > self.size().width():
            self.x = self.size().width() - self.getWidth()
        if self.y + self.getHeight() > self.size().height():
            self.y = self.size().height() - self.getHeight()

    def getWidth(self) -> int:
        """Возвращает ширину холста"""
        return self.dist * self.cols

    def getHeight(self) -> int:
        """Возвращает высоту холста"""
        return self.dist * self.rows

    def calcDist(self) -> None:
        """Пересчёт расстояния между линиями сетки"""
        self.dist = DEFAULT_DIST * self.zoom

    def wheelEvent(self, event) -> None:
        """Изменение масштаба холста посредством кручения колеса мыши"""
        if event.angleDelta().y() > 0:
            self.zoom = min(self.zoom * ZOOM_STEP, 32)
        else:
            self.zoom = max(self.zoom / ZOOM_STEP, 0.1)
        self.calcDist()
        self.checkBorders()
        self.repaint()

    def mousePressEvent(self, event) -> None:
        """Обработка нажатия кнопки мыши"""
        if event.button() == Qt.LeftButton:
            self.move_canvas = True
            self.dif_x = self.x - event.x()
            self.dif_y = self.y - event.y()

    def mouseReleaseEvent(self, event) -> None:
        """Отпускание кнопки мыши"""
        if event.button() == Qt.LeftButton:
            self.move_canvas = False

    def mouseMoveEvent(self, event) -> None:
        """Обработка перемещения холста с зажатой кнопкой мыши"""
        if self.move_canvas:
            self.x = event.x() + self.dif_x
            self.y = event.y() + self.dif_y
            self.checkBorders()
            self.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Canvas(*map(int, input().split()))
    ex.show()
    sys.exit(app.exec())
