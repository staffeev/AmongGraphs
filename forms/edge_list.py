from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5 import uic
from settings import CANNOT_ADD, ARE_YOU_SURE
from functions import get_new_rib, get_graph_by_name
from models import db_session


class EdgeList(QWidget):
    """Класс для окна со списком ребер"""
    def __init__(self, graph_name: str, parent=None) -> None:
        super().__init__()
        uic.loadUi("UI/edge_list.ui", self)
        self.parent = parent
        self.graph_name = graph_name
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
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        self.table.setRowCount(len(graph.ribs))
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        for i, rib in enumerate(graph.ribs):
            self.table.setItem(i, 0, QTableWidgetItem(rib.points[0].name))
            self.table.setItem(i, 1, QTableWidgetItem(rib.points[1].name))
            self.table.setItem(i, 2, QTableWidgetItem(str(rib.weight)))
            self.table.setItem(i, 3, QTableWidgetItem(str(int(rib.is_directed))))
        self.modified = {}
        session.close()

    def addRow(self) -> None:
        """Метод для добавления ребра в таблицу"""
        if not self.checkComplete():
            return
        self.table.insertRow(self.table.rowCount())
        v1, v2, rib = get_new_rib()
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        graph.add_ribs(rib)
        session.add_all([v1, v2, rib])
        session.commit()
        session.close()

    def deleteRow(self) -> None:
        """Метод для удаления ребра из таблицы"""
        idx = {i.row() for i in self.table.selectedIndexes()}
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        ribs = [graph.ribs[i] for i in idx]
        flag = QMessageBox.question(
            self, "Delete ribs", f"{ARE_YOU_SURE} ribs {', '.join(map(str, ribs))}"
        )
        if flag == QMessageBox.No:
            return
        [session.delete(rib) for rib in ribs]
        session.commit()
        session.close()

    def save(self) -> None:
        """Метод сохранения изменений в БД"""
        if not self.checkComplete():
            return
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        for i, j in self.modified:
            if j < 2:
                graph.ribs[i].points[j].rename(self.modified[i, j])
            else:
                graph.ribs[i].change_weight(int(self.modified[i, j]))
        session.commit()
        self.modified = {}
        self.parent.showTreeOfElements()
        self.parent.draw_graph()

    def checkComplete(self) -> bool:
        """Метод проверки заполненности полей последней строки таблицы"""
        idx = self.table.rowCount()
        if not idx:
            return True
        if any(self.table.item(idx - 1, i) is None for i in range(4)):
            QMessageBox.critical(self, "Error", CANNOT_ADD)
            return False
        return True
