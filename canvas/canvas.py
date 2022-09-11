import sys
from PyQt5.QtWidgets import QWidget, QApplication, QMenu
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from settings import DEFAULT_DIST, ZOOM_STEP, DARK_GRAY, MIN_ZOOM, \
    MAX_ZOOM, MAX_CANVAS_SIZE
from models import db_session
from functions import get_graph_by_name, add_node, delete_node, rename_node
from canvas.canvas_node import CanvasNode
from canvas.canvas_edge import CanvasEdge


class Canvas(QWidget):
    """Класс холста для рисования графов"""

    def __init__(self, rows=MAX_CANVAS_SIZE, cols=MAX_CANVAS_SIZE, graph=None, parent=None):
        super().__init__()
        self.qp = QPainter()
        self.graph_name = graph
        self.prnt = parent
        self.rows = rows
        self.cols = cols
        self.zoom = 1
        self.dist = DEFAULT_DIST * self.zoom
        self.move_canvas = False
        self.dif_x = self.dif_y = 0
        self.node_selected = False
        self.x = self.y = 0
        self.graph_nodes = {}
        self.graph_ribs = {}
        self.selected_item = None
        self.ctrl_nodes = []
        self.last_cell = None

    def loadGraph(self, name) -> None:
        """Загрузка данных из графа"""
        # TODO
        if name is None:
            return
        self.selected_item = None
        self.graph_nodes = {}
        self.graph_ribs = {}
        self.graph_name = name
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        for node in graph.nodes:
            self.graph_nodes[node.cell] = CanvasNode(node, self)
        for rib in graph.ribs.values():
            n1 = self.graph_nodes[rib.nodes[0].cell]
            n2 = self.graph_nodes[rib.nodes[1].cell]
            self.graph_ribs[rib.get_crds()] = CanvasEdge(n1, n2, rib, self)
        session.close()
        self.repaint()

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
        self.drawRibs()
        self.drawPoints()

    def drawRibs(self) -> None:
        """Вызов отрисовки каждого ребра"""
        for el in self.graph_ribs.values():
            el.draw()

    def drawPoints(self) -> None:
        """Вызов отрисовки каждой вершины"""
        for el in self.graph_nodes.values():
            el.draw()

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

    def getPointCenter(self, row: int, col: int) -> tuple[int, int]:
        x, y = self.getPoint(row, col)
        return x + self.dist // 2, y + self.dist // 2

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
        if (col, row) in self.graph_nodes:
            return
        self.graph_nodes[col, row] = self.graph_nodes.pop((old_row, old_col))
        self.graph_nodes[col, row].setCell(col, row)
        self.selected_item = (col, row)
        self.repaint()

    def unselect(self):
        [i.unselect() for i in self.ctrl_nodes]
        self.ctrl_nodes = []
        self.repaint()

    def mousePressEvent(self, event) -> None:
        """Обработка нажатия кнопки мыши"""
        if event.button() != Qt.LeftButton:
            return
        col, row = self.getCell(event.x(), event.y())
        if self.graph_nodes.get((row, col), 0) and event.modifiers() & Qt.ControlModifier:
            self.ctrl_nodes.append(self.graph_nodes[row, col])
            self.graph_nodes[row, col].select()
            self.repaint()
            return
        elif self.graph_nodes.get((row, col), 0):
            self.unselect()
            self.selected_item = (row, col)
            self.node_selected = True
            return
        self.unselect()
        self.move_canvas = True
        self.dif_x = self.x - event.x()
        self.dif_y = self.y - event.y()

    def mouseReleaseEvent(self, event) -> None:
        """Отпускание кнопки мыши"""
        if event.button() != Qt.LeftButton:
            return
        self.move_canvas = False
        self.node_selected = False
        if not self.selected_item:
            return
        self.processNodeShift()

    def processNodeShift(self) -> None:
        """Сохранение изменения положения вершины"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        row, col = self.selected_item
        selected_node = self.graph_nodes[row, col]
        graph_node = graph.get_nodes_by_name(selected_node.node_name)[0]
        graph_node.set_cell((row, col))
        session.commit()
        session.close()

    def mouseMoveEvent(self, event) -> None:
        """Обработка перемещения холста с зажатой кнопкой мыши"""
        if self.node_selected:
            self.moveNode(*self.getCell(event.x(), event.y()))
        elif self.move_canvas:
            self.x = event.x() + self.dif_x
            self.y = event.y() + self.dif_y
            self.checkBorders()
            self.repaint()

    def resizeEvent(self, event) -> None:
        """Проверка границы при изменении размера виджета"""
        self.checkBorders()

    def checkInBorders(self, x: int, y: int) -> bool:
        """Проверка на то, что курсор находистя в сетке"""
        row = int((y - self.y) // self.dist)
        col = int((x - self.x) // self.dist)
        return 0 <= row < self.rows and 0 <= col < self.cols

    def contextMenuEvent(self, event) -> None:
        """Открытие контекстного меню"""
        x, y = event.x(), event.y()
        row, col = self.getCell(x, y)
        self.last_cell = col, row
        if not self.checkInBorders(x, y) or self.graph_name is None or self.node_selected:
            return
        len_selected = len(self.ctrl_nodes)
        menu = QMenu(self)
        if len_selected > 2:
            arg = [(i.row, i.col) for i in self.ctrl_nodes]
            menu.addAction('Delete nodes', lambda: self.deleteNode(arg))
        elif len_selected == 2:
            pass
            # TODO: ADD/DELETE RIB
        elif len_selected == 1 or self.graph_nodes.get((col, row), 0):
            if len_selected == 1:
                self.last_cell = self.ctrl_nodes[0].row, self.ctrl_nodes[0].col
            menu.addAction('Rename', self.renameNode)
            menu.addAction('Delete', lambda: self.deleteNode([self.last_cell]))
        else:
            menu.addAction('Add node', self.addNode)
        menu.exec_(self.mapToGlobal(event.pos()))
        # TODO

    def getCell(self, x: int, y: int) -> tuple[int, int]:
        """Возвращает индекс клетки в сетке по координатам"""
        row = min(max(int((y - self.y) // self.dist), 0), self.rows - 1)
        col = min(max(int((x - self.x) // self.dist), 0), self.cols - 1)
        return row, col

    def addNode(self) -> None:
        """Метод для добавления вершины на холст"""
        add_node(self.graph_name, self.last_cell)
        self.loadGraph(self.graph_name)
        self.repaint()

    def deleteNode(self, nodes) -> None:
        """Метод для удаления вершины с холста"""
        if not delete_node(self, self.graph_name, nodes):
            return
        for el in nodes:
            self.graph_nodes.pop(el)
        self.repaint()

    def renameNode(self) -> None:
        """Переименование вершины"""
        row, col = self.last_cell
        new_name = rename_node(self.graph_name, (row, col))
        if new_name is None:
            return
        self.graph_nodes[row, col].setName(new_name)
        self.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Canvas(*map(int, input().split()))
    ex.show()
    sys.exit(app.exec())
