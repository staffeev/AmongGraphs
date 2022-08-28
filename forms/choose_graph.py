from PyQt5.QtWidgets import QDialog, QLabel, QDialogButtonBox, QLineEdit, \
    QVBoxLayout, QListWidget, QMessageBox
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt


class ChooseGraphForm(QDialog):
    """Класс формы для выбора графа"""
    def __init__(self, names: list, to_delete: bool, parent=None) -> None:
        super().__init__(parent)
        self.names = names
        self.name_to_return = None
        self.to_delete = to_delete
        print(to_delete)
        self.setWindowTitle("Choose graph")
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.inputData = QLineEdit()
        self.inputData.textChanged.connect(self.findNames)
        self.list = QListWidget()
        self.list.addItems(names)
        self.list.itemClicked.connect(self.saveName)
        self.list.itemDoubleClicked.connect(self.accept)
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Choose the graph:"))
        self.layout.addWidget(self.inputData)
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def saveName(self) -> None:
        """Метод установки имени выбранного графа в строку поиска"""
        if self.list.currentItem() is not None:
            self.name_to_return = self.list.currentItem().text()

    def findNames(self) -> None:
        """Метод поиска графов по имени и вывода их в списке"""
        self.list.setEnabled(True)
        self.list.clear()
        text = self.inputData.text()
        found_names = [name for name in self.names if text in name]
        if found_names:
            self.list.addItems(found_names)
        else:
            self.list.addItems(["There are no graphs with this name"])
            self.list.setEnabled(False)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Обработчик нажатия на клавиатуру
        (переключение между элементами списка"""
        if self.inputData.hasFocus():
            return
        if event.key() in (Qt.Key_Up, Qt.Key_W):
            self.list.setCurrentRow(
                (self.list.currentRow() - 1) % self.list.count()
            )
        elif event.key() in (Qt.Key_Down, Qt.Key_S):
            self.list.setCurrentRow(
                (self.list.currentRow() + 1) % self.list.count()
            )
        self.saveName()

    def accept(self) -> None:
        """Метод обработки события нажатия на кнопку ОК"""
        flag = QMessageBox.Yes
        if self.name_to_return not in self.names:
            QMessageBox.critical(
                self, "Error", "There are no graphs with this name"
            )
            return
        elif self.name_to_return is None:
            QMessageBox.warning(
                self, "Warning", "You have not selected the graph"
            )
            return
        if self.to_delete:
            flag = QMessageBox.question(
                self, "Delete",
                f"Are you sure you want to delete graph {self.name_to_return}"
            )
        if flag == QMessageBox.Yes:
            self.done(1)

