import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from settings import DEFAULT_DIST, ZOOM_STEP, RED, DARK_GRAY


class Canvas(QWidget):
    """Класс холста для рисования графов"""

    def __init__(self, rows=50, cols=50, parent=None):
        super().__init__()
        self.qp = QPainter()
        self.prnt = parent
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.zoom = 1
        self.dist = DEFAULT_DIST * self.zoom
        self.setGeometry(300, 300, self.dist * cols, self.dist * rows)
        self.move_canvas = False
        self.can_move = True
        self.dif_x = self.dif_y = 0
        self.x = self.y = 0

    def paintEvent(self, event) -> None:
        """Событие отрисовки графа"""
        self.qp = QPainter()
        self.qp.begin(self)
        self.drawGrid()
        self.drawElements()
        self.qp.end()

    def drawElements(self) -> None:
        """Отрисовка элементов графа"""

        self.drawPoints()
        # TODO

    def drawPoints(self) -> None:
        """Вызов отрисовки каждой вершины"""
        for i, row in enumerate(self.grid):
            for j, el in enumerate(row):
                if el == 1:
                    self.drawPoint(j, i)

    def drawPoint(self, row: int, col: int) -> None:
        """Метод для рисования вершины графа на клетчатом поле"""
        self.qp.setBrush(RED)
        self.qp.drawEllipse(*self.getPoint(row, col), self.dist, self.dist)

    def drawGrid(self) -> None:
        """Отрисовка сетки"""
        self.qp.setPen(DARK_GRAY)
        for i in range(self.rows + 1):
            self.qp.drawLine(self.x, self.y + i * self.dist,
                             self.x + self.getWidth(), self.y + i * self.dist)
        for i in range(self.cols + 1):
            self.qp.drawLine(self.x + i * self.dist, self.y,
                             self.x + i * self.dist, self.y + self.getHeight())

    def checkBorders(self) -> None:
        """Проверка на то, находится ли холст в границах виджета"""
        if not self.canvasIsBiggerThanWidget():
            self.x = min(max(self.x, 0), self.size().width() - self.getWidth())
            self.y = min(max(self.y, 0), self.size().height() - self.getHeight())
        else:
            self.x = max(min(self.x, 0), self.size().width() - self.getWidth())
            self.y = max(min(self.y, 0), self.size().height() - self.getHeight())

    def getWidth(self) -> int:
        """Возвращает ширину холста"""
        return self.dist * self.cols

    def getHeight(self) -> int:
        """Возвращает высоту холста"""
        return self.dist * self.rows

    def getPoint(self, row: int, col: int) -> tuple[int, int]:
        """Возвращает координаты ячейки клетчатого поля"""
        return self.x + row * self.dist, self.y + col * self.dist

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

    def canvasIsBiggerThanWidget(self) -> bool:
        """Возвращает истину, если холст больше своего виджета"""
        return self.getWidth() > self.size().width() and \
            self.getHeight() > self.size().height()

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

    def resizeEvent(self, event) -> None:
        """Проверка границы при изменении размера виджета"""
        self.checkBorders()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Canvas(*map(int, input().split()))
    ex.show()
    sys.exit(app.exec())
