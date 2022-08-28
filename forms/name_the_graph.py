from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, \
    QLineEdit, QMessageBox
from settings import ALREADY_EXISTS


class CreateGraphForm(QDialog):
    """Класс диалогового окна для получения имени нового графа"""
    def __init__(self, existing_names: list, parent=None) -> None:
        super().__init__(parent)
        self.names = existing_names
        self.setWindowTitle("Enter data")
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Enter the name of the graph:"))
        self.inputData = QLineEdit()
        self.layout.addWidget(self.inputData)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def accept(self) -> None:
        """Обработчик события нажатия на кнопку ОК"""
        if self.inputData.text() in self.names:
            QMessageBox.critical(self, "Error", ALREADY_EXISTS)
        else:
            self.done(1)