import sys
from PyQt5.QtWidgets import QWidget, QApplication, QMenu
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from settings import DEFAULT_DIST, ZOOM_STEP, RED, DARK_GRAY, MIN_ZOOM, \
    MAX_ZOOM, MAX_CANVAS_SIZE, BLUE, SELECTED_ITEM, MOVE_UP, MOVE_DOWN, \
    MOVE_LEFT, MOVE_RIGHT
from models import db_session
from functions import get_graph_by_name, add_node, delete_node, rename_node
from canvas.node import CanvasNode


class Canvas(QWidget):
    """Класс холста для рисования графов"""

    def __init__(self, rows=MAX_CANVAS_SIZE, cols=MAX_CANVAS_SIZE, graph=None, parent=None):
        super().__init__()
        self.qp = QPainter()
        self.graph_name = graph
        self.prnt = parent
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.zoom = 1
        self.dist = DEFAULT_DIST * self.zoom
        self.move_canvas = False
        self.dif_x = self.dif_y = 0
        self.node_selected = False
        self.x = self.y = 0
        self.graph_elements = {}
        self.selected_item = None
        self.last_cell = None

    def loadGraph(self, name) -> None:
        """Загрузка данных из графа"""
        # TODO
        if name is None:
            return
        self.graph_elements = {}
        self.graph_name = name
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        for node in graph.nodes:
            self.graph_elements[node.cell] = CanvasNode(node)
            self.grid[node.row][node.col] = node
        session.close()

    def paintEvent(self, event) -> None:
        """Событие отрисовки графа"""
        if self.graph_name is None:
            return
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
        for cell, el in self.graph_elements.items():
            # color = SELECTED_ITEM if cell in self.selected_items else RED
            el.draw(self.qp, self.getPoint(el.row, el.col), self.dist)

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
            self.zoom = min(self.zoom * ZOOM_STEP, MAX_ZOOM)
        else:
            self.zoom = max(self.zoom / ZOOM_STEP, MIN_ZOOM)
        self.calcDist()
        self.checkBorders()
        self.repaint()

    def canvasIsBiggerThanWidget(self) -> bool:
        """Возвращает истину, если холст больше своего виджета"""
        return self.getWidth() > self.size().width() and \
            self.getHeight() > self.size().height()

    def moveNode(self, row, col) -> None:
        """Метод для перемещения вершины по холсту"""
        old_row, old_col = self.selected_item
        self.grid[row][col] = self.grid[old_row][old_col]
        self.grid[old_row][old_col] = None
        self.graph_elements[col, row] = self.graph_elements.pop((old_row, old_col))
        self.graph_elements[col, row].setCell(col, row)
        self.selected_item = (col, row)
        self.repaint()

    def mousePressEvent(self, event) -> None:
        """Обработка нажатия кнопки мыши"""
        if event.button() == Qt.LeftButton:
            col, row = self.getCell(event.x(), event.y())
            if self.graph_elements.get((row, col), 0):
                self.selected_item = (row, col)
                self.node_selected = True
                return
            self.move_canvas = True
            self.dif_x = self.x - event.x()
            self.dif_y = self.y - event.y()

    def mouseReleaseEvent(self, event) -> None:
        """Отпускание кнопки мыши"""
        if event.button() == Qt.LeftButton:
            self.move_canvas = False
            self.node_selected = False

    def mouseMoveEvent(self, event) -> None:
        """Обработка перемещения холста с зажатой кнопкой мыши"""
        if self.move_canvas and not self.node_selected:
            self.x = event.x() + self.dif_x
            self.y = event.y() + self.dif_y
            self.checkBorders()
            self.repaint()
        elif self.node_selected:
            self.moveNode(*self.getCell(event.x(), event.y()))
            print(self.selected_item)



    def resizeEvent(self, event) -> None:
        """Проверка границы при изменении размера виджета"""
        self.checkBorders()
        # self.repaint()

    def contextMenuEvent(self, event) -> None:
        """Открытие контекстного меню"""
        row, col = self.getCell(event.x(), event.y())
        self.last_cell = row, col
        if not (0 <= row < self.rows) or not (0 <= col < self.cols) or self.graph_name is None:
            return
        menu = QMenu(self)
        if not self.grid[col][row]:
            menu.addAction('Add node', self.addNode)
        else:
            menu.addAction('Rename', self.renameNode)
            menu.addAction('Delete', self.deleteNode)
        menu.exec_(self.mapToGlobal(event.pos()))
        # TODO

    def getCell(self, x: int, y: int) -> tuple[int, int]:
        """Возвращает индекс клетки в сетке по координатам"""
        return int((y - self.y) // self.dist), int((x - self.x) // self.dist)

    def addNode(self) -> None:
        """Метод для добавления вершины на холст"""
        add_node(self.graph_name, self.last_cell[::-1])
        self.loadGraph(self.graph_name)
        self.repaint()

    def deleteNode(self) -> None:
        """Метод для удаления вершины с холста"""
        # TODO
        col, row = self.last_cell
        if not delete_node(self, self.graph_name, (row, col)):
            return
        self.graph_elements.pop((row, col))
        self.grid[row][col] = None
        self.repaint()

    def renameNode(self) -> None:
        """Переименование вершины"""
        col, row = self.last_cell
        new_name = rename_node(self.graph_name, (row, col))
        if new_name is None:
            return
        self.graph_elements[row, col].setName(new_name)
        self.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Canvas(*map(int, input().split()))
    ex.show()
    sys.exit(app.exec())
