import sys
from canvas.canvas import Canvas
from forms.add_new_data_form import AddNewData
from forms.choose_graph import ChooseGraphForm
from forms.add_from_csv import AddFromCsv
from forms.tree_element import TreeItem
from forms.edge_list import EdgeList
from forms.matrix import GraphMatrix
from properties_definer import PropertyDefiner
from models.graph import Graph
from functions import get_graph_names, get_graph_by_name
from PyQt5.Qt import QStandardItemModel, QAbstractItemView
from PyQt5 import uic
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtCore import QItemSelectionModel, QModelIndex
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from models import db_session
from settings import NOT_OPEN, ENTER_GRAPH
from typing import Union


def except_hook(cls, exception, traceback):
    """Функция для отлова возможных исключений, вознкающих при работе с Qt"""
    sys.__excepthook__(cls, exception, traceback)


class Mentor(QMainWindow):
    """Класс основного окна программы"""
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('UI/main.ui', self)
        self.graph_name = None
        self.window = None
        self.image = None
        self.canvas = Canvas(parent=self)
        self.definer = PropertyDefiner()
        self.initUI()

    def initUI(self) -> None:
        """Настройка UI и привязка событий к обработчикам"""
        self.setWindowIcon(QIcon('images/icon.png'))
        self.treeModel = QStandardItemModel()
        self.rootNode = self.treeModel.invisibleRootItem()
        self.graph_list.setModel(self.treeModel)
        self.graph_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.graph_list.selectionModel().selectionChanged.connect(self.selectFromTree)
        # Настройка относительного позиционирования элементов главного окна
        self.splitter.addWidget(self.canvas)
        self.splitter.setSizes([100, 700])
        self.widget.setLayout(self.hl)
        self.setCentralWidget(self.widget)
        # События меню
        self.actionCreate.triggered.connect(self.createGraph)
        self.actionOpen.triggered.connect(self.openGraph)
        self.actionDelete.triggered.connect(self.deleteGraph)
        self.actionExit.triggered.connect(self.close)
        self.actionEdit_matrix.triggered.connect(self.openWindow)
        self.actionEdit_list.triggered.connect(self.openWindow)
        self.actionDraw.triggered.connect(self.draw)
        self.actionLoad_csv.triggered.connect(self.addCsv)
        # Остальные события

    def draw(self):
        """Вызывает отрисовку холста с графом"""
        if self.graph_name is not None:
            self.canvas.loadGraph(self.graph_name)
        else:
            QMessageBox.warning(self, "Warning", NOT_OPEN)

    def openWindow(self) -> None:
        """Обработчик открытия новых окон"""
        if self.graph_name is None:
            QMessageBox.warning(self, "Open graph", NOT_OPEN)
            return
        if self.window is not None:
            self.window.close()
        if self.sender() == self.actionEdit_list:
            self.window = EdgeList(self.graph_name, self)
        elif self.sender() == self.actionEdit_matrix:
            self.window = GraphMatrix(self.graph_name, self)
        self.window.show()

    def createGraph(self, name=None) -> Union[str, None]:
        """Метод для создания графа"""
        session = db_session.create_session()
        if name is not None and name:
            graph = Graph(name=name)
        else:
            form = AddNewData(get_graph_names(session), ENTER_GRAPH, self)
            if not form.exec():
                session.close()
                return
            graph = Graph(name=form.inputData.text())
        session.add(graph)
        session.commit()
        session.close()
        return name if name is not None else form.inputData.text()

    def openGraph(self, name=None) -> None:
        """Метод для открытия графа"""
        session = db_session.create_session()
        if name is not None and name:
            graph = session.query(Graph).filter(Graph.name == name).first()
        else:
            form = ChooseGraphForm(get_graph_names(session), False, self)
            if not form.exec():
                session.close()
                return
            graph = session.query(Graph).filter(
                Graph.name == form.name_to_return
            ).first()
        self.graph_name = graph.name
        self.showTreeOfElements()
        self.canvas.loadGraph(graph.name)
        self.definer.change_graph(graph.name)
        if self.window is not None and not self.window.isHidden():
            self.window.changeGraph(self.graph_name)
        session.close()

    def deleteGraph(self, name=None) -> None:
        """Метод для удаления графа"""
        session = db_session.create_session()
        if name is not None and name:
            graph = session.query(Graph).filter(Graph.name == name).first()
        else:
            form = ChooseGraphForm(get_graph_names(session), True, self)
            if not form.exec():
                session.close()
                return
            graph = session.query(Graph).filter(
                Graph.name == form.name_to_return
            ).first()
        session.delete(graph)
        session.commit()
        if graph.name == self.graph_name:
            self.clearTree()
            self.canvas.clear()
        if self.window is not None:
            self.window.close()
        session.close()

    def iterTree(self):
        return
        model = self.graph_list.model()
        # model = QStandardItemModel()
        for i in range(model.rowCount()):
            item = model.item(i)
            print(item.text())
            for j in range(item.rowCount()):
                item_child = item.child(j, 0)
                print('\t' + item_child.text())

    def selectChildren(self, index: QModelIndex):
        """Выделение всех детей поддерева"""
        selection_model = self.graph_list.selectionModel()
        model = index.model()
        item = model.itemFromIndex(index)
        for i in range(item.rowCount()):
            child = model.index(i, 0, index)
            selection_model.select(child, QItemSelectionModel.Select)

    def selectFromTree(self) -> None:
        """Выделение тех элементов на холсте, которые были выделены в дереве"""
        self.canvas.unselect()
        names = set()
        for ix in self.graph_list.selectedIndexes():
            item = ix.model().itemFromIndex(ix)
            parent = ix.parent().row()
            if parent == -1:  # Root node
                self.selectChildren(ix)
                continue
            names.add(item.text())
        self.canvas.select(names)

    def showTreeOfElements(self) -> None:
        """Метод для построения дерева элементов графа"""
        self.clearTree()
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        self.treeModel.setHorizontalHeaderItem(
            0, TreeItem(self.graph_name, bold=True)
        )
        nodes = TreeItem("Nodes")
        nodes.appendRows([TreeItem(str(v), 8) for v in graph.nodes])
        ribs = TreeItem("Ribs")
        ribs.appendRows([TreeItem(str(r), 8) for r in graph.ribs.values()])
        cutpoints = TreeItem("Cutpoints")
        cutpoints.appendRows([TreeItem(str(c), 8) for c in graph.get_cutpoints()])
        bridges = TreeItem("Bridges")
        bridges.appendRows([TreeItem(str(b), 8) for b in graph.get_bridges()])
        cycles = TreeItem("Cycles")
        cycles.appendRows([TreeItem(str(cy), 8) for cy in graph.cycles])
        components = TreeItem("Components")
        components.appendRows([TreeItem(str(cmp), 8) for cmp in graph.components])
        self.rootNode.appendRows([nodes, ribs, cutpoints, bridges, cycles, components])
        session.close()

    def clearTree(self) -> None:
        """Метод очистки дерева элементов графа"""
        self.treeModel.clear()
        self.rootNode = self.treeModel.invisibleRootItem()

    def addCsv(self) -> None:
        """Метод для добавления данных в граф из csv-таблицы"""
        form = AddFromCsv()
        if not form.exec():
            return
        self.reloadGraph()
        if form.dataType == 'list':
            edge_list = EdgeList(self.graph_name, self)
            edge_list.setModified(form.modified)
            edge_list.save()
        elif form.dataType == 'matrix':
            matrix = GraphMatrix(self.graph_name, self)
            matrix.addCoupleNodes(form.data.get('nodes', []))
            matrix.setModified(form.modified)
            matrix.save()

    def reloadGraph(self) -> None:
        """Если граф существует, его данные будут удалены.
        Иначе будет создан новый граф"""
        if self.graph_name is not None:
            name = self.graph_name
            self.deleteGraph(name)
            self.openGraph(name=self.createGraph(name))
        else:
            name = self.createGraph()
            if name is None:
                return
            self.openGraph(name=name)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Обработка закрытия программы"""
        self.window.close() if self.window is not None else None


if __name__ == '__main__':
    db_session.global_init('graphs.db')
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    programme = Mentor()
    programme.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
