from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QComboBox, QFileDialog, \
    QPushButton, QMessageBox
from os import getcwd


class ComboBoxWithCheckBoxes(QComboBox):
    """Класс выпадающего списка значений с возможностью отметить несколько
    значений"""
    def __init__(self, names=None):
        """Функция-инициализатор"""
        super().__init__()
        self.changed_value = False
        if names is not None:
            self.names = names
        self.view().pressed.connect(self.press_item)

    def hidePopup(self):
        """Функция, которая будет прятать выпадающий список или
        оставлять открытым"""
        if not self.changed_value:
            super().hidePopup()
        self.changed_value = False

    def if_item_checked(self, i):
        """Функция, возвращающая истину, если элемент с некоторым индексом
        отмечен, иначе ложь"""
        item = self.model().item(i, self.modelColumn())
        if item is not None:
            return item.checkState() == Qt.Checked

    def press_item(self, i):
        """Функция замены отметки на ее отсутствие у элемента или наоборот"""
        item = self.model().itemFromIndex(i)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
            if item.text() == 'Все':
                for x in range(1, self.count()):
                    it = self.model().item(x, self.modelColumn())
                    it.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
            if item.text() == 'Все':
                for x in range(1, self.count()):
                    it = self.model().item(x, self.modelColumn())
                    it.setCheckState(Qt.Checked)
        self.changed_value = True

    def check_item(self, i):
        """Функция для создания отметки у элемента (пустой)"""
        new_item = self.model().item(i, self.modelColumn())
        new_item.setCheckState(Qt.Unchecked)


class SaveAsForm(QDialog):
    """Окно, позваоляющее пользователю выбрать графы для сохранения и
    сохраняемые свойства."""
    def __init__(self, names, flag=True):
        """Функция-инициализатор класса SaveAsForm"""
        super().__init__()
        uic.loadUi('UI/save_as_form.ui', self)
        self.setWindowIcon(QIcon('imgs/icon3.png'))
        self.setFixedSize(self.size())
        self.folder = None
        self.flag = flag
        self.btn_folder.clicked.connect(self.get_folder)
        self.names = ['Все'] + names
        self.btn_accept = QPushButton('OK', self)
        self.btn_accept.move(150, 145)
        self.btn_accept.clicked.connect(self.check)
        self.box.removeButton(self.box.buttons()[0])
        self.combo1 = ComboBoxWithCheckBoxes(names)
        for i in range(len(self.names)):
            self.combo1.addItem(self.names[i])
            self.combo1.check_item(i)

        self.combo2 = ComboBoxWithCheckBoxes()
        self.opt = ['Все', 'Вершины', 'Мосты', 'Точки сочленения',
                    'Циклы', 'Компоненты', 'Минимальные пути']
        for i in range(7):
            self.combo2.addItem(self.opt[i])
            self.combo2.check_item(i)

        self.grid.addWidget(self.combo1, 1, 0, 1, 1)
        self.grid.addWidget(self.combo2, 1, 1, 1, 1)

        self.chosen_graphs = []
        self.chosen_prop = []

    def get_value(self):
        """Функция для получения выбранных элементов в выпадающих списках."""
        for i in range(1, self.combo1.count()):
            if self.combo1.if_item_checked(i):
                self.chosen_graphs.append(self.names[i])
        for i in range(1, 8):
            if self.combo2.if_item_checked(i):
                self.chosen_prop.append(self.opt[i])

    def get_folder(self):
        if self.flag:
            name, ok = QFileDialog.getSaveFileName(
                self, 'Сохранить csv-таблицу', f'{getcwd()}\\untitled.csv',
                'CSV-таблица (*.csv);;Все файлы (*)')
        else:
            name, ok = QFileDialog.getSaveFileName(
                self, 'Сохранить txt-файл', f'{getcwd()}\\untitled.txt',
                'Текстовый файл (*.txt);;Все файлы (*)')
        if ok:
            self.folder = name

    def check(self):
        if all(x is False for x in [self.combo1.if_item_checked(i) for i in
                                    range(1, self.combo2.count())]) or all(
            x is False for x in [self.combo2.if_item_checked(i) for i in range(
                1, self.combo2.count())]):
            QMessageBox.critical(self, 'Ошибка', 'Вы не выбрали опции для '
                                                 'сохранения!')
        elif self.folder is None:
            QMessageBox.critical(self, 'Ошибка', 'Вы не выбрали директорию '
                                                 'сохранения и имя файла!')
        else:
            self.get_value()
            self.accept()
