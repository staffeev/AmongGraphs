from PyQt5.QtWidgets import QWidget, QHeaderView, QMessageBox, \
    QTableWidgetItem as QItem
from PyQt5 import uic
from functions import str_is_float, get_graph_by_name, create_ribs, \
    get_graph_nodes
from settings import ARE_YOU_SURE
from forms.add_new_data_form import AddNewData
from models import db_session
from models.elements import Graph, Rib, Vertex


class GraphMatrix(QWidget):
    """Класс для окна с матрицей смежности графа"""
    def __init__(self, graph_name: str, parent=None) -> None:
        super().__init__()
        uic.loadUi("UI/matrix.ui", self)
        self.parent = parent
        self.graph_name = graph_name
        self.modified = {}
        self.initUI()
        self.loadTable()

    def initUI(self) -> None:
        """Метод для установки UI и привязки событий"""
        self.setLayout(self.vl)
        self.addBtn.clicked.connect(self.addNode)
        self.deleteBtn.clicked.connect(self.deleteNode)
        self.saveChanges.clicked.connect(self.save)
        self.matrix.itemChanged.connect(self.changeItem)
        self.matrix.selectionModel().selectionChanged.connect(
            self.checkUnselected)

    def stretchTable(self) -> None:
        """Метод, растягивающий таблицу на всю допустимую ширину и высоту"""
        h_header = self.matrix.horizontalHeader()
        v_header = self.matrix.verticalHeader()
        for i in range(self.matrix.columnCount()):
            h_header.setSectionResizeMode(i, QHeaderView.Stretch)
            v_header.setSectionResizeMode(i, QHeaderView.Stretch)

    def nameHeaders(self) -> None:
        """Метод, переименовывающий заголовки таблицы"""
        session = db_session.create_session()
        nodes = get_graph_nodes(session, self.graph_name)
        self.matrix.setHorizontalHeaderLabels(nodes)
        self.matrix.setVerticalHeaderLabels(nodes)
        session.close()

    def changeItem(self, item) -> None:
        """Метод для сохранения изменений в таблице"""
        data = '' if not item.text() else float(item.text())
        self.modified[item.row(), item.column()] = data

    def checkUnselected(self, selected, unselected) -> bool:
        """Обработчик валидности невыделенных ячеек"""
        if len(unselected.indexes()) != 1:
            return True
        last_cell = unselected.indexes()[0]
        return self.validCell(last_cell.row(), last_cell.column())

    def validCell(self, row: int, col: int) -> bool:
        """Проверка валидности значения ячейки таблицы"""
        if self.validEmpty(row, col):
            return True
        return self.validNumber(row, col)

    def validEmpty(self, row: int, col: int) -> bool:
        """Проверка отсутствия значения в ячейке"""
        try:
            # if row > self.get_last_row():
            #     return True
            if not self.table.item(row, col).text():
                raise AttributeError
            return False
        except AttributeError:
            return True

    def validNumber(self, row: int, col: int) -> bool:
        """Проверка числового значения в ячейке"""
        return str_is_float(self.matrix.item(row, col))

    def loadTable(self) -> None:
        """Метод, загружащий данные в таблицу"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        ribs = create_ribs(graph)
        nodes = get_graph_nodes(session, self.graph_name)
        self.matrix.setRowCount(len(nodes))
        self.matrix.setColumnCount(len(nodes))
        self.nameHeaders()
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes):
                self.matrix.setItem(
                    i, j, QItem(str(ribs.get((str(node1), str(node2)), '')))
                )
        self.matrix.resizeRowsToContents()
        self.matrix.resizeColumnsToContents()
        self.stretchTable()
        session.close()

    def getSelectedRowsOrCols(self) -> set[int]:
        """Метод, возвращающий индексы выделенных строк (столбов)"""
        sel_rows = {}
        sel_cols = {}
        for el in self.matrix.selectedIndexes():
            sel_rows[el.row()] = sel_rows.get(el.row(), 0) + 1
            sel_cols[el.column()] = sel_cols.get(el.column(), 0) + 1
        return self.countSelected(sel_rows) | self.countSelected(sel_cols)

    def countSelected(self, values: dict[int]) -> set[int]:
        """Метод, возвращающий полностью выделенные строки (столбцы) таблицы"""
        num_cols = self.get_cols()
        return set(filter(lambda x: values[x] == num_cols, values.keys()))

    def addNode(self) -> None:
        """Метод для добавления вершины в граф"""
        # TODO: addNode

    def deleteNode(self) -> None:
        """Метод для удаления вершины из графа"""
        selected = self.getSelectedRowsOrCols()
        if not selected:
            return
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        nodes = [graph.nodes[i] for i in selected]
        flag = QMessageBox.question(
            self, "Delete ribs",
            f"{ARE_YOU_SURE} nodes {', '.join(map(str, nodes))}"
        )
        if flag == QMessageBox.No:
            session.close()
            return
        [session.delete(node) for node in nodes]
        session.commit()
        session.close()
        self.loadTable()

    def save(self) -> None:
        """Метод для сохранения изменений"""
        #TODO: save
        pass

    def get_cols(self) -> int:
        """Метод, возвращающий количество столбцов в таблице"""
        return self.matrix.columnCount()
