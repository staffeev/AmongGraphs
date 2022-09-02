from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, \
    QDialogButtonBox
from PyQt5 import uic
from settings import NOT_CHOSEN_FILE, NOT_CHOSEN_TYPE, NOT_CHOSEN_DEL
from csv import reader, DictReader


class AddFromCsv(QDialog):
    """Класс формы для добавления данных из csv-таблицы"""
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('UI/add_csv.ui', self)
        self.file = None
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.vl.addWidget(self.buttonBox)
        self.setLayout(self.vl)
        self.fileBtn.clicked.connect(self.chooseFile)
        self.radioMatrix.toggled.connect(self.setDataType)
        self.radioList.toggled.connect(self.setDataType)
        self.radioComma.toggled.connect(self.setDelimier)
        self.radioSemicolon.toggled.connect(self.setDelimier)
        self.radioTab.toggled.connect(self.setDelimier)
        self.dataType = None
        self.delimiter = None

    def setDataType(self) -> None:
        """Установка типа входных данных"""
        if self.sender() == self.radioMatrix:
            self.dataType = 'matrix'
        else:
            self.dataType = 'list'

    def setDelimiter(self) -> None:
        """Установка типа разделителя данных"""
        if self.sender() == self.radioComma:
            self.delimiter = ','
        elif self.sender() == self.radioSemicolon:
            self.delimiter = ';'
        else:
            self.delimiter = '\t'

    def chooseFile(self) -> None:
        """Выбор файла с таблицей"""
        file = QFileDialog.getOpenFileName(
            self, 'Choose CSV', '', 'CSV (*.csv)'
        )[0]
        if not file:
            return
        self.file = file

    def accept(self) -> None:
        """Проверка входных данных"""
        if not self.valid():
            return
        # TODO
        pass


    def valid(self) -> bool:
        """Проверка того, что все параметры для данных указаны"""
        if self.file is None:
            QMessageBox.warning(self, 'Warning', NOT_CHOSEN_FILE)
            return False
        if self.dataType is None:
            QMessageBox.warning(self, "Warning", NOT_CHOSEN_TYPE)
            return False
        if self.delimiter is None:
            QMessageBox.warning(self, "Warning", NOT_CHOSEN_DEL)
            return False
        return True

