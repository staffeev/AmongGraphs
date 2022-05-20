from csv import reader
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QDialog


class GetCsv(QDialog):
    """Окно для выбора csv-таблицы со списком ребер графа и разделителя
    csv-таблицы."""
    def __init__(self):
        """Функция-инициализатор класса GetCsv"""
        super().__init__()
        uic.loadUi('UI/get_csv.ui', self)
        self.setWindowIcon(QIcon('imgs/icon3.png'))
        self.setFixedSize(self.size())
        self.radio = [self.r1, self.r2, self.r3]
        self.name = self.data = None
        self.box.buttons()[0].setEnabled(False)
        self.choose_btn.clicked.connect(self.open_csv)
        [r.clicked.connect(self.open_csv) for r in self.radio]

    def open_csv(self):
        """Функция для выбора csv-таблицы для открытия."""
        sender = self.sender()
        checked = [i for i in self.radio if i.isChecked()]
        # Проверка данных идет только в том случае, когда выбран и файл,
        # и разделитель
        if checked and self.name is not None and sender != self.choose_btn:
            delimiter = ';' if sender == self.r2 else '\t' if \
                sender == self.r3 else ','
            self.check_data(delimiter)
        # Запросим у пользователя имя файла
        elif sender == self.choose_btn:
            name, ok = QFileDialog.getOpenFileName(self, 'Открыть csv-таблицу',
                                                   '', 'Таблица (*.csv)')
            if not ok:
                return
            # Если пользователь нажал на ОК, идет открытие
            self.name = name
            if checked:
                delimiter = ';' if sender == self.r2 else '\t' if \
                    sender == self.r3 else ','
                self.check_data(delimiter)

    def check_data(self, delimiter):
        """Функция для проверки корректности данных из csv-таблицы.
        Принимает строку-разделитель. Если данные из таблицы корректны, в
        атрибут класса создается список ребер грфа, иначе выводится сообщение
        об ошибке."""
        try:
            # Обработаем данные из таблицы
            with open(self.name, encoding='utf8') as ribs:
                new_ribs = reader(ribs, delimiter=delimiter,
                                  quotechar='"')
                self.data = []
                for i in filter(lambda x: x, new_ribs):
                    s, e, v = i
                    v = int(v) if float(v) == int(v) else float(v)
                    self.data.append((s, e, v))
                self.box.buttons()[0].setEnabled(True)
        except ValueError:  # Если данные некорректны
            self.data = None
            QMessageBox.critical(self, 'Ошибка', 'Данные введены '
                                                 'некорректно!')
