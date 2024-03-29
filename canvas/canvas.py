import sys
from colour import Color
from PyQt5.QtWidgets import QWidget, QApplication, QMenu, QMessageBox
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt
from settings import DEFAULT_DIST, ZOOM_STEP, DARK_GRAY, MIN_ZOOM, \
    MAX_ZOOM, MAX_CANVAS_SIZE, ARE_YOU_SURE, RED, SELECTED_ITEM_COLOR, BLACK
from models import db_session
from models.edge import Rib
from forms.edge_data import EdgeData
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
        self.bool_draw_grid = True
        self.move_canvas = False
        self.dif_x = self.dif_y = 0
        self.node_selected = False
        self.x = self.y = 0
        self.center = [self.size().width() // 2, self.size().height() // 2]
        self.graph_nodes = {}
        self.graph_ribs = {}
        self.selected_item = None
        self.ctrl_nodes = []
        self.last_cell = None

    def centerCanvas(self, x: int, y: int):
        """Центрирование холста"""
        self.x = x - self.dist * self.rows // 2
        self.y = y - self.dist * self.cols // 2

    def clear(self):
        """Очистка холста"""
        self.graph_nodes = {}
        self.graph_name = None
        self.graph_ribs = {}
        self.node_selected = False
        self.last_cell = None
        self.ctrl_nodes = []
        self.selected_item = None
        self.move_canvas = False
        self.repaint()

    def loadGraph(self, name) -> None:
        """Загрузка данных из графа"""
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
            self.graph_ribs[n1, n2] = CanvasEdge(n1, n2, rib, self)
        session.close()
        self.unselect()
        self.colorizeNodes()
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
        if not self.bool_draw_grid:
            return
        self.qp.setPen(DARK_GRAY)
        for i in range(self.rows + 1):
            self.qp.drawLine(int(self.x), int(self.y + i * self.dist),
                             int(self.x + self.getWidth()), int(self.y + i * self.dist))
        for i in range(self.cols + 1):
            self.qp.drawLine(int(self.x + i * self.dist), int(self.y),
                             int(self.x + i * self.dist), int(self.y + self.getHeight()))

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
        x, y = self.x + self.getWidth() // 2, self.y + self.getHeight() // 2
        if event.angleDelta().y() > 0:
            self.zoom = min(self.zoom * ZOOM_STEP, MAX_ZOOM)
        else:
            self.zoom = max(self.zoom / ZOOM_STEP, MIN_ZOOM)
        self.calcDist()
        self.centerCanvas(x, y)
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

    def unselectPath(self):
        """Отменяет выделение ребер пути"""
        [i.setColor(BLACK) for i in self.graph_ribs.values()]

    def selectPathRibs(self, names: list[str]):
        """Выделяет ребра, принадлежащие пути"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        for i in range(1, len(names)):
            n1 = self.graph_nodes[graph.get_node_by_name(names[i - 1]).cell]
            n2 = self.graph_nodes[graph.get_node_by_name(names[i]).cell]
            rib = self.graph_ribs.get((n1, n2), self.graph_ribs.get((n2, n1), None))
            if rib is not None:
                rib.setColor(SELECTED_ITEM_COLOR)
        session.close()

    def select(self, names: set[str]):
        """Выделение элементов графа по их именам (вершины, ребра)"""
        nodes = []
        ribs = []
        cycles = []
        for el in names:
            if el.count('"') == 2:
                nodes.append(el)
            if ', ' in el:
                nodes.extend(el.split(', '))
            elif el.count('-') > 1:
                spl = el.split('-')
                ribs.extend([spl[i - 1] + '-' + spl[i] for i in range(1, len(spl))])
                cycles.append(el)
            elif el.count('-') == 1:
                ribs.append(el)
            else:
                nodes.append(el)
        nodes = [i for i in self.graph_nodes.values() if i.node_name in nodes]
        ribs = [i for i in self.graph_ribs.values() if i.get_name() in ribs or i.get_inv_name() in ribs]
        self.ctrl_nodes.extend([i for i in nodes if i not in self.ctrl_nodes])
        for i in ribs:
            if i.start not in self.ctrl_nodes:
                self.ctrl_nodes.append(i.start)
            if i.end not in self.ctrl_nodes:
                self.ctrl_nodes.append(i.end)
        [i.select() for i in self.ctrl_nodes]
        self.repaint()

    def unselect(self):
        """Отмена выделения элементов"""
        [i.unselect() for i in self.ctrl_nodes]
        self.ctrl_nodes = []
        self.repaint()

    def mouseDoubleClickEvent(self, event):
        self.unselectPath()
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
    
    def change_grid_condition(self):
        """Изменение флага отрисовки сетки"""
        self.bool_draw_grid = not self.bool_draw_grid
        self.repaint()

    def change_node_color_condition(self):
        """Изменение флага отрисовки вершин"""
        for node in self.graph_nodes.values():
            node.change_color_condition()
        self.repaint()

    def contextMenuEvent(self, event) -> None:
        """Открытие контекстного меню"""
        self.unselectPath()
        self.repaint()
        x, y = event.x(), event.y()
        row, col = self.getCell(x, y)
        self.last_cell = col, row
        if not self.checkInBorders(x, y) or self.graph_name is None or self.node_selected:
            return
        len_selected = len(self.ctrl_nodes)
        menu = QMenu(self)
        menu.addAction("Disable/enable grid", self.change_grid_condition)
        menu.addAction("Disable/enable node color", self.change_node_color_condition)
        if len_selected > 2:
            arg = [(i.row, i.col) for i in self.ctrl_nodes]
            edges = [i for i in self.graph_ribs.values() if i.start in
                     self.ctrl_nodes and i.end in self.ctrl_nodes]
            if edges:
                menu.addAction('Delete edges', lambda: self.deleteEdge(edges))
            menu.addAction('Delete nodes', lambda: self.deleteNode(arg))
        elif len_selected == 2:
            n1, n2 = self.ctrl_nodes
            edge = self.getEdge(n1, n2)
            menu.addAction('Find minimum cost path', lambda: self.findPath(n1, n2))
            if edge is None:
                menu.addAction('Add edge', lambda: self.addEdge(n1, n2))
            else:
                menu.addAction('Delete edge', lambda: self.deleteEdge([edge]))
                menu.addAction('Change edge', lambda: self.changeEdge(edge))
            arg = [(i.row, i.col) for i in self.ctrl_nodes]
            menu.addAction('Delete nodes', lambda: self.deleteNode(arg))
        elif len_selected == 1 or self.graph_nodes.get((col, row), 0):
            if len_selected == 1:
                self.last_cell = self.ctrl_nodes[0].row, self.ctrl_nodes[0].col
            menu.addAction('Rename', self.renameNode)
            menu.addAction('Delete', lambda: self.deleteNode([self.last_cell]))
        else:
            menu.addAction('Add node', self.addNode)
        menu.exec_(self.mapToGlobal(event.pos()))

    def getEdge(self, n1: CanvasNode, n2: CanvasNode) -> CanvasEdge:
        """Возвращает ребро по координатам"""
        return self.graph_ribs.get((n1, n2), self.graph_ribs.get((n2, n1), None))

    def addEdge(self, n1: CanvasNode, n2: CanvasNode):
        """Добавление ребра"""
        form = EdgeData((n1, n2))
        if not form.exec():
            return
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        nodes = graph.get_nodes_by_name(n1.node_name, n2.node_name)
        rib = Rib(weight=form.weight.value())
        if form.radio2.isChecked():
            rib.add_nodes(nodes[1], nodes[0])
        else:
            rib.add_nodes(nodes[0], nodes[1])
        if not form.radio0.isChecked():
            rib.is_directed = True
        graph.add_ribs(rib)
        session.add(rib)
        session.commit()
        if form.radio2.isChecked():
            self.graph_ribs[n2, n1] = CanvasEdge(n2, n1, rib, self)
        else:
            self.graph_ribs[n1, n2] = CanvasEdge(n1, n2, rib, self)
        self.colorizeNodes()
        session.close()
        self.repaint()
        self.update_mentor()

    def changeEdge(self, edge: CanvasEdge):
        """Изменение параметров ребра"""
        form = EdgeData(edge)
        if not form.exec():
            return
        session = db_session.create_session()
        rib = session.query(Rib).filter(Rib.id == edge.id).first()
        rib.change_weight(form.weight.value())
        edge.weight = form.weight.value()
        if form.radio0.isChecked():
            rib.change_dir(False)
            edge.is_directed = False
        elif form.radio1.isChecked():
            rib.change_dir(True)
            edge.is_directed = True
        elif form.radio2.isChecked():
            rib.change_dir(True)
            rib.swap_nodes()
            edge.swap_nodes()
            edge.is_directed = True
        session.commit()
        session.close()
        self.unselect()
        self.repaint()
        self.update_mentor()

    def deleteEdge(self, edges: list[CanvasEdge]):
        """Удаление ребра с холста и из БД по id (берется из edge)"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        ribs = [i for i in graph.ribs.values() if i.id in map(lambda x: x.id, edges)]
        flag = QMessageBox.question(
            self, 'Delete edge', f'{ARE_YOU_SURE} edges {", ".join(map(str, ribs))}')
        if flag != QMessageBox.Yes:
            session.close()
            return
        [session.delete(rib) for rib in ribs]
        session.commit()
        session.close()
        to_pop = [i for i in self.graph_ribs if self.graph_ribs[i] in edges]
        [self.graph_ribs.pop(i, None) for i in to_pop]
        self.colorizeNodes()
        self.repaint()
        self.update_mentor()

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
        self.update_mentor()

    def deleteNode(self, nodes) -> None:
        """Метод для удаления вершины с холста"""
        if not delete_node(self, self.graph_name, nodes):
            return
        self.loadGraph(self.graph_name)
        self.repaint()
        self.update_mentor()

    def renameNode(self) -> None:
        """Переименование вершины"""
        row, col = self.last_cell
        new_name = rename_node(self.graph_name, (row, col))
        if new_name is None:
            return
        self.graph_nodes[row, col].setName(new_name)
        self.repaint()
        self.update_mentor()

    def colorizeNodes(self):
        """Раскрашивание вершин в зависимости от количества связей"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        d_colors = {}
        for node in graph.nodes:
            d_colors[node.cell] = len(node.ribs)
        if not d_colors:
            return
        colors = list(Color('green').range_to(Color('red'),
                                              max(d_colors.values()) + 1))
        for cell in self.graph_nodes:
            num = d_colors[cell]
            self.graph_nodes[cell].setColor(QColor(colors[num].hex))
        session.close()

    def findPath(self, n1, n2):
        """Определение минимального по стоимости пути между двумя вершинами"""
        path = self.prnt.definer.find_min_path(n1.node_name, n2.node_name)
        print(path)
        if path is not None:
            self.selectPathRibs(path)

    def update_mentor(self) -> None:
        """Обновление родительского класса"""
        if self.prnt.window is not None:
            self.prnt.window.loadTable()
        self.prnt.definer.create_nx_graph()
        self.prnt.definer.define_all()
        self.prnt.showTreeOfElements()
        self.prnt.graph_list.expandAll()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Canvas(*map(int, input().split()))
    ex.show()
    sys.exit(app.exec())
