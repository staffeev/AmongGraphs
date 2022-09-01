from PyQt5.QtWidgets import QWidget, QTableWidgetItem as QItem, QHeaderView, \
    QMessageBox, QTableWidgetSelectionRange
from forms.table_checkbox import TableCheckbox
from PyQt5 import uic
from models.elements import Rib
from settings import ARE_YOU_SURE, NOT_NUMBER, EMPTY
from functions import get_graph_by_name, str_is_float
from models import db_session


class EdgeList(QWidget):
    """Класс для окна со списком ребер"""
    def __init__(self, graph_name: str, parent=None) -> None:
        super().__init__()
        uic.loadUi("UI/edge_list.ui", self)
        self.parent = parent
        self.graph_name = graph_name
        self.modified = {}
        self.initUI()
        self.loadTable()

    def initUI(self) -> None:
        """Метод для установки UI и привязки событий"""
        self.setLayout(self.vl)
        self.addEdge.clicked.connect(self.addRow)
        self.deleteEdge.clicked.connect(self.deleteRow)
        self.saveChanges.clicked.connect(self.save)
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        self.table.itemChanged.connect(self.changeItem)
        self.table.selectionModel().selectionChanged.connect(
            self.checkUnselected)

    def checkUnselected(self, _, unselected) -> bool:
        """Обработчик валидности невыделенных ячеек"""
        if len(unselected.indexes()) != 1:
            return True
        last_cell = unselected.indexes()[0]
        return self.validCell(last_cell.row(), last_cell.column())

    def validCell(self, row: int, col: int) -> bool:
        """Проверка валидности значения ячейки таблицы"""
        if col != self.get_last_col() and not self.validEmpty(row, col):
            return False
        if col == self.get_last_col() - 1:
            return self.validNumber(row, col)
        return True

    def validEmpty(self, row: int, col: int) -> bool:
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

    def validNumber(self, row: int, col: int):
        """Проверка числового значения в ячейке"""
        if str_is_float(self.table.item(row, col).text()):
            return True
        QMessageBox.critical(self, "Error", NOT_NUMBER)
        return False

    def changeItem(self, item) -> None:
        """Метод для сохранения изменений в таблице"""
        if str_is_float(item.text()) and item.column() == 2:
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
        for i, rib in enumerate(graph.get_ordered_ribs()):
            self.ribPresentation(i, rib)
        self.table.resizeRowsToContents()
        self.modified = {}
        session.close()

    def ribPresentation(self, row: int, rib: Rib) -> None:
        """"Метод для занесения ребра в таблицу"""
        self.table.setItem(row, 0, QItem(str(rib.nodes[0])))
        self.table.setItem(row, 1, QItem(str(rib.nodes[1])))
        self.table.setItem(row, 2, QItem(str(rib.weight)))
        item = self.get_table_checkbox(row, rib.is_directed)
        self.table.setCellWidget(row, 3, item)

    def addRow(self) -> None:
        """Метод для добавления ребра в таблицу"""
        if not self.checkComplete():
            return
        last_row, last_col = self.get_last_indexes()
        last_row += 1
        self.table.insertRow(last_row)
        self.table.setRangeSelected(QTableWidgetSelectionRange(
            last_row, 0, last_row, last_col), True
        )
        item = self.get_table_checkbox(last_row, False)
        self.table.setCellWidget(last_row, last_col, item)
        rib = Rib()
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        [self.modified.update({(last_row, i): ''}) for i in range(3)]
        graph.add_ribs(rib)
        session.add(rib)
        session.commit()
        session.close()

    def deleteRow(self) -> None:
        """Метод для удаления ребра из таблицы"""
        idx = {i.row() for i in self.table.selectedIndexes()}
        if not idx:
            return
        session = db_session.create_session()
        ribs = get_graph_by_name(session, self.graph_name).get_ordered_ribs()
        ribs = [ribs[i] for i in idx]
        flag = QMessageBox.question(
            self, "Delete ribs", f"{ARE_YOU_SURE} ribs {', '.join(map(str, ribs))}"
        )
        if flag == QMessageBox.No:
            session.close()
            return
        [session.delete(rib) for rib in ribs]
        [self.modified.pop((i, j), None) for i in idx for j in range(self.table.columnCount())]
        session.commit()
        session.close()
        self.loadTable()

    def save(self) -> None:
        """Метод сохранения изменений в БД"""
        if not self.checkComplete():
            return
        print(self.modified)
        session = db_session.create_session()
        ribs = get_graph_by_name(session, self.graph_name).get_ordered_ribs()
        [ribs[i].change_attrs(j, self.modified[i, j]) for i, j in self.modified]
        session.commit()
        session.close()
        self.modified = {}
        self.parent.showTreeOfElements()
        self.parent.draw_graph()

    def checkComplete(self) -> bool:
        """Метод проверки корректности измененных данных"""
        if self.get_last_row() < 0:
            return True
        return all(self.validCell(i, j) for i, j in self.modified)

    def get_last_row(self):
        """Метод, возвращающий индекс последней строки таблицы"""
        return self.table.rowCount() - 1

    def get_last_col(self):
        """Метод, возвращающий индекс последнего столбца таблицы"""
        return self.table.columnCount() - 1

    def get_last_indexes(self):
        """Метод, возвращающий индекс правого нижнего элемента таблицы"""
        return self.get_last_row(), self.get_last_col()

    def get_table_checkbox(self, row: int, value: bool) -> TableCheckbox:
        """Метод, возвращающий флажок для ячейки таблицы"""
        item = TableCheckbox(row)
        item.setState(value)
        item.checkbox.clicked.connect(self.changeCheckbox)
        return item

