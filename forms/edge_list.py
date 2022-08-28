from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView
from PyQt5 import uic
from models.elements import Graph
from sqlalchemy.orm import Session


class EdgeList(QWidget):
    """Класс для окна со списком ребер"""
    def __init__(self, graph: Graph, session: Session) -> None:
        super().__init__()
        uic.loadUi("UI/edge_list.ui", self)
        self.graph = graph
        self.session = session
        self.modified = {}
        self.setLayout(self.vl)
        self.addEdge.clicked.connect(self.addRow)
        self.deleteEdge.clicked.connect(self.deleteRow)
        self.saveChanges.clicked.connect(self.save)
        self.table.itemChanged.connect(self.changeItem)
        self.loadTable()

    def changeItem(self, item) -> None:
        """Метод для сохранения изменений в таблице"""
        pass

    def loadTable(self) -> None:
        """Метод для загрузки данных в таблицу"""
        self.table.setRowCount(len(self.graph.ribs))
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        for i, rib in enumerate(self.graph.ribs):
            self.table.setItem(i, 0, QTableWidgetItem(rib.points[0].name))
            self.table.setItem(i, 1, QTableWidgetItem(rib.points[1].name))
            self.table.setItem(i, 2, QTableWidgetItem(str(rib.weigth)))
            self.table.setItem(i, 3, QTableWidgetItem(str(int(rib.is_directed))))
        self.modified = {}

    def addRow(self):
        """Метод для добавления ребра в таблицу"""
        pass

    def deleteRow(self):
        """Метод для удаления ребра из таблицы"""
        pass

    def save(self) -> None:
        """Метод сохранения изменений в БД"""

