from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QPushButton, QDialog, QDialogButtonBox


class GetGraphName(QDialog):
    """Окно, позволяющее пользователю указать имя графа для открытия.
    Пользователь может выполнять поиск графа по имени."""
    def __init__(self, names, flag=False):
        """Инициализатор класса"""
        super().__init__()
        uic.loadUi('UI/get_graph_name.ui', self)
        self.setWindowIcon(QIcon('imgs/icon3.png'))
        self.setFixedSize(self.size())
        self.names = names
        self.gr = None
        self.list.addItems(sorted(self.names))
        self.list.itemClicked.connect(self.save_name)
        self.list.itemDoubleClicked.connect(self.accept_)
        self.find_.textChanged.connect(self.find_names)
        self.list.setCurrentRow(0)
        if flag:  # Добавим предупреждение пользователя, если он удаляет граф
            self.list.itemDoubleClicked.connect(self.check)
            self.box.clear()
            self.btn_acc = QPushButton('OK', self)
            self.btn_acc.clicked.connect(self.check)
            self.btn_acc.move(120, 285)
            self.box.addButton(QDialogButtonBox.Cancel)

    def keyPressEvent(self, event):
        """Функция для обработки нажатий на клавиатуру. Если пользователь
        нажал на стрелку вверх или вниз, выбранный элемент в списке поменяется
        на вышестоящий или нижестоящий."""
        if not self.find_.hasFocus():
            if event.key() == Qt.Key_Up or event.key() == Qt.Key_W:
                row = self.list.currentRow() - 1
                self.list.setCurrentRow(row % self.list.count())
            elif event.key() == Qt.Key_Down or event.key() == Qt.Key_S:
                row = self.list.currentRow() + 1
                self.list.setCurrentRow(row % self.list.count())
        if event.key() == Qt.Key_Return:
            self.accept_()

    def save_name(self):
        """Фукнция для сохранения в атрибуте класса имени графа для удаления"""
        self.gr = self.list.currentItem().text()

    def accept_(self):
        """Функция, завершающая работу диалогового окна по двойному нажатию на
        элемент в списке."""
        if self.list.currentItem():
            self.accept()

    def find_names(self):
        """Функция для фильтрации имен в списке по введеннйо пользователем
        строке"""
        string = self.find_.text()
        self.list.clear()
        to_show = sorted([i for i in self.names if string in i])
        to_show = to_show if to_show else ['Графы с таким именем в базе '
                                           'данных отсутствуют.']
        self.list.addItems(to_show)

    def check(self):
        """Функция для подтверждения удаления графа."""
        do_or_not = QMessageBox.question(
            self, 'Удалить элемент', "Удалить выбранный граф?",
            QMessageBox.Yes, QMessageBox.No)
        if do_or_not == QMessageBox.Yes:
            self.accept()
