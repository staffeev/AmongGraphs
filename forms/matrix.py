from PyQt5.QtWidgets import QWidget, QHeaderView, QMessageBox, \
    QTableWidgetItem as QItem
from PyQt5 import uic
from PyQt5.QtCore import Qt
from functions import str_is_float, get_graph_by_name, create_ribs
from settings import ARE_YOU_SURE, ENTER_NODE, GRAY, NOT_NUMBER, NTET
from forms.add_new_data_form import AddNewData
from models import db_session
from models.elements import Rib, Vertex
from typing import Union


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
        self.matrix.horizontalHeader().sectionDoubleClicked.connect(self.renameNode)
        self.matrix.verticalHeader().sectionDoubleClicked.connect(self.renameNode)

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
        nodes = get_graph_by_name(session, self.graph_name).get_nodes()
        self.matrix.setHorizontalHeaderLabels(nodes)
        self.matrix.setVerticalHeaderLabels(nodes)
        session.close()

    def renameNode(self, index: int) -> None:
        """Метод для переименования вершины графа"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        form = AddNewData(graph.get_nodes(), ENTER_NODE)
        if not form.exec():
            session.close()
            return
        new_name = form.inputData.text()
        self.setLabelText(index, new_name)
        graph.nodes[index].rename(new_name)
        session.commit()
        session.close()

    def setLabelText(self, index: int, text: str) -> None:
        """Метод, устаналивающий текст в заголовок таблицы"""
        self.matrix.horizontalHeaderItem(index).setText(text)
        self.matrix.verticalHeaderItem(index).setText(text)

    def getLabels(self) -> list[str]:
        """Метод, возвращающий заголовки таблицы"""
        return [self.matrix.horizontalHeaderItem(x).text()
                for x in range(self.get_cols())]
        
    def changeItem(self, item) -> None:
        """Метод для сохранения изменений в таблице"""
        if item.row() != item.column():
            self.modified[item.row(), item.column()] = item.text()

    def checkUnselected(self, _, unselected) -> bool:
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
            if not self.matrix.item(row, col).text():
                raise AttributeError
            return False
        except AttributeError:
            return True

    def validNumber(self, row: int, col: int) -> bool:
        """Проверка числового значения в ячейке"""
        if str_is_float(self.matrix.item(row, col).text()):
            return True
        QMessageBox.critical(self, "Error", NOT_NUMBER)
        return False

    def loadTable(self) -> None:
        """Метод, загружащий данные в таблицу"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        ribs = create_ribs(graph)
        nodes = graph.get_nodes()
        self.matrix.setRowCount(len(nodes))
        self.matrix.setColumnCount(len(nodes))
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes):
                self.matrix.setItem(
                    i, j, QItem(str(ribs.get((str(node1), str(node2)), '')))
                )
        self.updateTableForm()
        self.modified = {}
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
        return set(filter(lambda x: values[x] == num_cols - 1, values.keys()))

    def addNode(self) -> None:
        """Метод для добавления вершины в граф"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        form = AddNewData(graph.get_nodes(), ENTER_NODE)
        if not form.exec():
            session.close()
            return
        v = Vertex(name=form.inputData.text())
        graph.add_nodes(v)
        session.add(v)
        session.commit()
        session.close()
        self.expandTable()
        self.updateTableForm()

    def addCoupleNodes(self, names) -> None:
        """Добавления нескольких вершин в граф"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        nodes = [Vertex(name=i) for i in names]
        graph.add_nodes(*nodes)
        session.add_all(nodes)
        session.commit()
        session.close()
        self.expandTable(len(nodes))
        self.updateTableForm()

    def expandTable(self, cnt=1) -> None:
        """Метод, расширяющий матрицу на одну строку и один столбец"""
        for _ in range(cnt):
            cols = self.get_cols()
            self.matrix.insertRow(cols)
            self.matrix.insertColumn(cols)

    def deleteNode(self) -> None:
        """Метод для удаления вершины из графа"""
        selected = self.getSelectedRowsOrCols()
        if not selected:
            return
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        nodes = [graph.nodes[i] for i in selected]
        flag = QMessageBox.question(
            self, "Delete nodes",
            f"{ARE_YOU_SURE} nodes {', '.join(map(str, nodes))}"
        )
        if flag == QMessageBox.No:
            session.close()
            return
        [session.delete(node) for node in nodes]
        session.commit()
        session.close()
        self.loadTable()

    def save(self):
        """Метод для сохранения изменений"""
        if not self.checkComplete():
            return
        for i, j in self.modified:
            if self.modified[i, j] == NTET:
                continue
            self.processRib(i, j)
        self.modified = {}
        self.parent.showTreeOfElements()
        self.parent.canvas.repaint()

    def processRib(self, row: int, col: int) -> None:
        """Метод, обрабаотывающий измененное ребро"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        nodes = graph.get_nodes_by_index(row, col)
        rib = graph.get_rib_by_nodes(row, col)
        inv_rib = graph.get_rib_by_nodes(col, row)
        item1, item2 = self.get_item(row, col), self.get_item(col, row)
        if rib is not None:
            session.delete(rib)
        if inv_rib is not None:
            session.delete(inv_rib)
        if item1:
            r1 = Rib(weight=float(item1), is_directed=bool(item2 != item1))
            r1.add_nodes(*nodes)
            graph.add_ribs(r1)
            session.add(r1)
        if item1 != item2 and item2:
            r2 = Rib(weight=float(item2), is_directed=True)
            r2.add_nodes(nodes[1], nodes[0])
            graph.add_ribs(r2)
            session.add(r2)
        if self.modified.get((col, row), 0):
            self.modified[col, row] = NTET
        session.commit()
        session.close()

    def checkComplete(self) -> bool:
        """Метод проверки корректности измененных данных"""
        if self.get_cols() < 1:
            return True
        return all(self.validCell(i, j) for i, j in self.modified)

    def get_cols(self) -> int:
        """Метод, возвращающий количество столбцов в таблице"""
        return self.matrix.columnCount()

    def updateTableForm(self) -> None:
        """Метод, обновляющий заголовки и размеры таблицы"""
        self.nameHeaders()
        self.matrix.resizeRowsToContents()
        self.matrix.resizeColumnsToContents()
        self.editMainDiagonal()
        self.stretchTable()

    def editMainDiagonal(self) -> None:
        """Метод, изменяющий главную диагональ матрицы (добавление цвета и
        невозможность редактирования)"""
        for i in range(self.get_cols()):
            self.matrix.setItem(i, i, QItem(''))
            item = self.matrix.item(i, i)
            item.setFlags(Qt.ItemFlag(False))
            item.setBackground(GRAY)

    def get_item(self, row: int, col: int) -> Union[str, None]:
        """Метод, возвращающий значение ячейки таблицы"""
        item = self.matrix.item(row, col)
        if item is None:
            return None
        return item.text()

    def setModified(self, val_dict: dict) -> None:
        """Учстановка нового словаря изменений"""
        for i, j in val_dict:
            self.matrix.setItem(i, j, QItem(str(val_dict[i, j])))
        self.modified = val_dict