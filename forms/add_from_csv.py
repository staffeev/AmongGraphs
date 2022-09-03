from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, \
    QDialogButtonBox
from PyQt5 import uic
from settings import NOT_CHOSEN_FILE, NOT_CHOSEN_TYPE, NOT_CHOSEN_DEL, ALERT_CSV
from csv import DictReader
from collections import OrderedDict


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
        self.radioComma.toggled.connect(self.setDelimiter)
        self.radioSemicolon.toggled.connect(self.setDelimiter)
        self.radioTab.toggled.connect(self.setDelimiter)
        self.dataType = None
        self.delimiter = None
        self.data = OrderedDict()
        self.modified = {}

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

    def unpackValuesFromList(self) -> None:
        """Распаковка данных из списка-таблицы"""
        self.data = OrderedDict()
        with open(self.file) as file:
            read = DictReader(file, delimiter=self.delimiter, quotechar='"')
            [self.unpackEdge(el) for el in read]
        self.createModified()

    def unpackEdge(self, el) -> None:
        """Распаковка данных одного ребра"""
        try:
            n1, n2 = el['start'], el['end']
            if not n1 or not n2:
                raise ValueError
            if n1 == n2:
                raise KeyError
            w, is_d = int(el['weight']), bool(int(el['is_directed']))
            self.data[n1, n2] = (w, is_d)
        except (KeyError, ValueError, TypeError):
            return

    def accept(self) -> None:
        """Проверка входных данных"""
        if not self.validParameters():
            return
        self.unpackValuesFromList()
        qst = QMessageBox.question(self, "Accept changes", ALERT_CSV)
        if qst == QMessageBox.No:
            return
        self.done(1)
        # TODO
        pass

    def validParameters(self) -> bool:
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

    def createModified(self) -> None:
        """Создание словаря изменений в графе"""
        self.modified = {}
        for i, el in enumerate(self.data):
            self.modified[i, 0] = el[0]
            self.modified[i, 1] = el[1]
            self.modified[i, 2] = self.data[el][0]
            self.modified[i, 3] = self.data[el][1]
        print(self.modified)
        # TODO
        pass


