import sys
from forms.name_the_graph import CreateGraphForm
from forms.choose_graph import ChooseGraphForm
from models.elements import Graph
from functions import get_graph_names
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QResizeEvent, QCloseEvent
from models import db_session


def except_hook(cls, exception, traceback):
    """Функция для отлова возможных исключений, вознкающих при работе с Qt"""
    sys.__excepthook__(cls, exception, traceback)


class Mentor(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('UI/main.ui', self)
        self.graph = None
        self.splitter.setSizes([200, 600])
        self.widget.setLayout(self.hl)
        self.setCentralWidget(self.widget)
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
        # Остальные события

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
        if form.exec():
            self.graph = session.query(Graph).filter(
                Graph.name == form.name_to_return
            ).first()
        session.close()

    def deleteGraph(self) -> None:
        """Метод для удаления графа"""
        session = db_session.create_session()
        form = ChooseGraphForm(get_graph_names(session), True, self)
        if form.exec():
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



if __name__ == '__main__':
    db_session.global_init('graphs.db')
    app = QApplication(sys.argv)
    programme = Mentor()
    programme.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
