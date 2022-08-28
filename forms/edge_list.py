from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5 import uic
from models.elements import Graph, Rib, Vertex
from sqlalchemy.orm import Session
from settings import CANNOT_ADD
from functions import get_new_rib


class EdgeList(QWidget):
    """Класс для окна со списком ребер"""
    def __init__(self, graph: Graph, session: Session, parent=None) -> None:
        super().__init__()
        uic.loadUi("UI/edge_list.ui", self)
        self.parent = parent
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
        self.modified[item.row(), item.column()] = item.text()

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

    def addRow(self) -> None:
        """Метод для добавления ребра в таблицу"""
        if not self.checkComplete():
            return
        self.table.insertRow(self.table.rowCount())
        v1, v2, rib = get_new_rib()
        self.graph.add_ribs(rib)
        self.session.add_all([v1, v2, rib])
        self.session.commit()

    def deleteRow(self):
        """Метод для удаления ребра из таблицы"""

        pass

    def save(self) -> None:
        """Метод сохранения изменений в БД"""
        if not self.checkComplete():
            return
        print(self.modified)
        print(self.graph.ribs)
        for i, j in self.modified:
            if j < 2:
                self.graph.ribs[i].points[j].name = self.modified[i, j]
            else:
                self.graph.ribs[i].weight = self.modified[i, j]
        self.session.commit()
        # self.modified = {}

    def checkComplete(self) -> bool:
        """Метод проверки заполненности полей последней строки таблицы"""
        idx = self.table.rowCount()
        if not idx:
            return True
        if any(self.table.item(idx - 1, i) is None for i in range(4)):
            QMessageBox.critical(self, "Error", CANNOT_ADD)
            return False
        return True
