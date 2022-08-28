import sys

import networkx as nx
from PIL.ImageQt import ImageQt
from matplotlib import pyplot as plt

from forms.name_the_graph import CreateGraphForm
from forms.choose_graph import ChooseGraphForm
from forms.tree_element import TreeItem
from forms.edge_list import EdgeList
from models.elements import Graph
from functions import get_graph_names, create_ribs, get_graph_by_name
from PyQt5.Qt import QStandardItemModel
from PyQt5 import uic
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPixmap, QKeyEvent
from models import db_session
import io
from PIL import Image


def except_hook(cls, exception, traceback):
    """Функция для отлова возможных исключений, вознкающих при работе с Qt"""
    sys.__excepthook__(cls, exception, traceback)


class Mentor(QMainWindow):
    """Класс основного окна программы"""
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('UI/main.ui', self)
        self.graph_name = None
        # self.graph = None
        self.splitter.setSizes([200, 600])
        self.widget.setLayout(self.hl)
        self.setCentralWidget(self.widget)
        self.treeModel = QStandardItemModel()
        self.rootNode = self.treeModel.invisibleRootItem()
        self.graph_list.setModel(self.treeModel)
        self.window = None
        self.initUI()

    def initUI(self) -> None:
        """Настройка UI и привязка событий к обработчикам"""
        # Настройка относительного позиционирования элементов главного окна
        self.splitter.setSizes([200, 600])
        self.widget.setLayout(self.hl)
        self.setCentralWidget(self.widget)
        # События меню
        self.actionCreate.triggered.connect(self.createGraph)
        self.actionOpen.triggered.connect(self.openGraph)
        self.actionDelete.triggered.connect(self.deleteGraph)
        self.actionSave.triggered.connect(self.saveChanges)
        self.actionExit.triggered.connect(self.close)
        self.actionEdit_matrix.triggered.connect(self.openWindow)
        self.actionEdit_list.triggered.connect(self.openWindow)
        self.actionDraw.triggered.connect(self.draw_graph)
        # Остальные события

    def openWindow(self) -> None:
        """Обработчик открытия новых окон"""
        if self.sender() == self.actionEdit_list:
            self.window = EdgeList(self.graph_name, self)
            self.window.show()

    def createGraph(self) -> None:
        """Метод для создания графа"""
        session = db_session.create_session()
        form = CreateGraphForm(get_graph_names(session), self)
        if form.exec():  # Создание графа
            graph = Graph(name=form.inputData.text())
            session.add(graph)
            session.commit()
        session.close()

    def openGraph(self) -> None:
        """Метод для открытия графа"""
        session = db_session.create_session()
        form = ChooseGraphForm(get_graph_names(session), False, self)
        if form.exec():  # Открытие графа
            graph = session.query(Graph).filter(
                Graph.name == form.name_to_return
            ).first()
            self.graph_name = graph.name
            self.showTreeOfElements()
        session.close()

    def deleteGraph(self) -> None:
        """Метод для удаления графа"""
        session = db_session.create_session()
        form = ChooseGraphForm(get_graph_names(session), True, self)
        if form.exec():  # Удаление графа
            graph = session.query(Graph).filter(
                Graph.name == form.name_to_return
            ).first()
            session.delete(graph)
            session.commit()
        session.close()

    def saveChanges(self) -> None:
        """Метод для сохранения изменений"""
        # TODO: save changes
        pass

    def showTreeOfElements(self) -> None:
        """Метод для построения дерева элементов графа"""
        self.treeModel.clear()
        self.rootNode = self.treeModel.invisibleRootItem()
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        self.treeModel.setHorizontalHeaderItem(
            0, TreeItem(self.graph_name, bold=True)
        )
        vertexes = TreeItem("Vertexes")
        vertexes.appendRows([TreeItem(v.name, 8) for v in graph.points])
        ribs = TreeItem("Ribs")
        ribs.appendRows([TreeItem(str(r), 8) for r in graph.ribs])
        self.rootNode.appendRows([vertexes, ribs])
        session.close()

    def create_graph(self):
        """Функция, создающая граф на основе списка ребер"""
        # Получаем списки ребер графа
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        ribs = create_ribs(graph)
        if ribs:
            plt.clf()
            fig_graph = nx.DiGraph()  # Создаем ориентированный граф
            fig_graph.add_edges_from(ribs)  # Добавляем в граф ребра
            nodes = [i.name for i in graph.points]
            # nodes = list(self.graph.nodes)  # Определим вершны графа
            pos = nx.spring_layout(fig_graph)  # Создаем слой, на котором
            # будут располагаться ребра и их веса
            fig = plt.figure(2, figsize=(
                self.canvas.size().width() // 100,
                self.canvas.size().height() // 100))
            # Рисование весов ребер
            nx.draw_networkx_edge_labels(fig_graph, pos, edge_labels=ribs,
                                         font_size=7)
            # Рисование ребер и вершин
            nx.draw(fig_graph, pos, nodelist=nodes, node_size=175,
                    with_labels=True)

    def plt_figure_to_pil_image(self, fig):
        """Функция принимает фигуру в pyplot и конвертирует
        ее в объект Image"""
        buf = io.BytesIO()  # Создание потока байтов
        fig.savefig(buf)  # Сохранение фигуры как потока байтов
        self.image = Image.open(buf)  # Создание изображение PIL
        self.image.resize((self.canvas.size().width(), self.canvas.size().height()))

    def draw_graph(self):
        """Функиця для рисования графа в окне приложения"""
        self.create_graph()
        self.plt_figure_to_pil_image(plt)
        p = ImageQt(self.image)
        # Устанавливаем в метку изображение
        self.canvas.setPixmap(QPixmap.fromImage(p))

    def closeEvent(self, event: QCloseEvent) -> None:
        """Обработка закрытия программы"""
        self.window.close() if self.window is not None else None


if __name__ == '__main__':
    db_session.global_init('graphs.db')
    app = QApplication(sys.argv)
    programme = Mentor()
    programme.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
