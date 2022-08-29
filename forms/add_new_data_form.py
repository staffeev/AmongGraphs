from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, \
    QLineEdit, QMessageBox
from settings import ALREADY_EXISTS, EMPTY


class AddNewData(QDialog):
    """Класс диалогового окна для добавленния новой информации"""
    def __init__(self, existing_names: list, text=None, parent=None) -> None:
        super().__init__(parent)
        self.names = existing_names
        self.setWindowTitle("Enter data")
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        self.label = QLabel(text)
        self.layout.addWidget(self.label)
        self.inputData = QLineEdit()
        self.layout.addWidget(self.inputData)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def accept(self) -> None:
        """Обработчик события нажатия на кнопку ОК"""
        if not self.inputData.text():
            QMessageBox.warning(self, "Warning", EMPTY)
        elif self.inputData.text() in self.names:
            QMessageBox.critical(self, "Error", ALREADY_EXISTS)
        else:
            self.done(1)