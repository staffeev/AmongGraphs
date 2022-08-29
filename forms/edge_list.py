from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, \
    QMessageBox, QCheckBox, QTableWidgetSelectionRange
from forms.table_checkbox import TableCheckbox
from PyQt5 import uic
from PyQt5.QtCore import Qt
from settings import CANNOT_ADD, ARE_YOU_SURE, NOT_NUMBER, EMPTY
from functions import get_new_rib, get_graph_by_name, str_is_float
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
        self.table.selectionModel().selectionChanged.connect(self.checkUnselected)
        self.loadTable()

    def checkUnselected(self, selected, unselected):
        """Обработчик валидности невыделенных ячеек"""
        for ix in unselected.indexes():
            if not self.validCell(ix.row(), ix.column()):
                return False
        return True

    def validCell(self, row, col):
        """Проверка валидности значения ячейки таблицы"""
        if col != self.get_last_col() and not self.validEmpty(row, col):
            return False
        if col == self.get_last_col() - 1:
            return self.validNumber(row, col)
        return True

    def validEmpty(self, row, col):
        """Проверка наличия значения в ячейке"""
        try:
            if row > self.get_last_row():
                return True
            if not self.table.item(row, col).text():
                raise AttributeError
            return True
        except AttributeError:
            QMessageBox.warning(self, "Error", EMPTY)
            return False

    def validNumber(self, row, col):
        """Проверка числового значения в ячейке"""
        try:
            return bool(float(self.table.item(row, col).text()))
        except ValueError:
            QMessageBox.critical(self, "Error", NOT_NUMBER)
            return

    def changeItem(self, item) -> None:
        """Метод для сохранения изменений в таблице"""
        if str_is_float(item.text()):
            self.modified[item.row(), item.column()] = float(item.text())
        else:
            self.modified[item.row(), item.column()] = item.text()

    def changeCheckbox(self) -> None:
        """Метод для сохранения изменения состояния флажков"""
        sender = self.sender()
        self.modified[sender.index, self.get_last_col()] = sender.isChecked()

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
            item = TableCheckbox(i)
            item.setState(rib.is_directed)
            item.checkbox.clicked.connect(self.changeCheckbox)
            self.table.setCellWidget(i, 3, item)
        self.table.resizeRowsToContents()
        self.modified = {}
        session.close()

    def addRow(self) -> None:
        """Метод для добавления ребра в таблицу"""
        if not self.checkComplete():
            return
        last_row, last_col = self.get_last_indexes()
        self.table.insertRow(last_row + 1)
        self.table.setRangeSelected(QTableWidgetSelectionRange(
            last_row + 1, 0, last_row + 1, last_col), True
        )
        item = TableCheckbox(last_row + 1)
        item.setState(False)
        item.checkbox.clicked.connect(self.changeCheckbox)
        self.table.setCellWidget(last_row + 1, last_col, item)
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
        self.loadTable()

    def save(self) -> None:
        """Метод сохранения изменений в БД"""
        if not self.checkComplete():
            return
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        [graph.ribs[i].change_attrs(j, self.modified[i, j]) for i, j in self.modified]
        session.commit()
        self.modified = {}
        self.parent.showTreeOfElements()
        self.parent.draw_graph()

    def checkComplete(self) -> bool:
        """Метод проверки заполненности полей последней строки таблицы"""
        idx = self.get_last_row()
        if idx <= 0:
            return True
        return all(self.validCell(idx, i) for i in range(3))

    def get_last_row(self):
        """Метод, возвращающий индекс последней строки таблицы"""
        return self.table.rowCount() - 1

    def get_last_col(self):
        """Метод, возвращающий индекс последнего столбца таблицы"""
        return self.table.columnCount() - 1

    def get_last_indexes(self):
        """Метод, возвращающий индекс правого нижнего элемента таблицы"""
        return self.get_last_row(), self.get_last_col()
