from PyQt5 import uic
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QToolBar
from functions import screen_size
import pyperclip

WIDTH, HEIGHT = screen_size()


class GraphProperties(QWidget):
    """Окно со свойствами графа, представленными в удобной форме."""
    def __init__(self, name):
        """Функция-инициализатор класса GraphProperties. При вызове принимет
        имя графа."""
        super().__init__()
        uic.loadUi('UI/graph_prop.ui', self)
        self.setWindowTitle(f'{name}: свойства')
        self.setWindowIcon(QIcon('imgs/icon3.png'))
        self.setGeometry(WIDTH // 2 - 275, HEIGHT // 2 - 200, 550, 400)
        self.toolbar = QToolBar('Свойства графа', self)
        self.toolbar.setStyleSheet('QToolButton {width: 150px};')
        self.toolbar.setOrientation(Qt.Vertical)
        self.toolbar.move(0, 10)
        self.var = {'Ребра': 0, 'Смежность': 1, 'Матрица': 2, 'Мосты': 3,
                    'Точки сочленения': 4, 'Циклы': 5, 'Компоненты': 6,
                    'Минимальные пути': 7}
        self.toolbar.addAction('Статистика', self.show_stats)
        self.toolbar.addSeparator()
        for i in self.var:
            self.toolbar.addAction(i, self.show_on_field)

        self.copy_btn.clicked.connect(self.copy)
        self.copy_btn.setShortcut(QKeySequence('Ctrl+C'))

        self.lcdS = [self.lcd1, self.lcd2, self.lcd3, self.lcd4, self.lcd5,
                     self.lcd6]

        self.data = None

    def set_data(self, data):
        """Фукнция для загрузки свойств графа"""
        self.data = data

    def show_on_field(self):
        """Фунция для вывода данных о графе (т..е переключения на первый
        виджет из стэка виджетов и вывода одного из свойств в заивисмости от
        выбранного пункат на панели инструментов)"""
        self.stack.setCurrentIndex(0)
        num_from_var = self.var[self.sender().text()]
        to_print = self.data[num_from_var]
        if num_from_var == 7:
            to_print = '\n\n'.join([f'{i[0]}-{i[1]}: ({to_print[i][0]}; ' +
                                    '-'.join(to_print[i][1]) + ')' for i in
                                    to_print])
        elif num_from_var == 5 or num_from_var == 6:
            to_print = '\n\n'.join(['-'.join(map(str, i)) for i in to_print])
        elif num_from_var == 4:
            to_print = ', '.join(map(str, to_print))
        elif num_from_var == 3:
            to_print = '\n'.join([f'{i[0]}-{i[1]}' for i in to_print])
        elif num_from_var == 2:
            to_print = '\n'.join([' '.join([f'{j:4}' for j in map(str, i)])
                                  for i in to_print])
        elif num_from_var == 1:
            to_print = '\n'.join([f'{i}: ' + ', '.join(map(str, to_print[i]))
                                  for i in to_print])
        else:
            to_print = '\n'.join([f'{i[0]}-{i[1]}: {to_print[i]}'
                                  for i in to_print])

        self.field.clear()
        if to_print:
            self.field.setPlainText(f'''{to_print}''')
        else:
            self.field.setPlainText('Отсутствуют')

    def show_stats(self):
        """Функция для вывода статистичеких данных о графе (т.е. переключения
        на второй виджет из стэка виджетов)"""
        self.stack.setCurrentIndex(1)

    def copy(self):
        """Функция для копирования данных из текстового поля в буфер обмена."""
        pyperclip.copy(self.field.toPlainText())

    def display_on_lcd(self, data):
        """Функция вывода в поля для чисел количества вершин, ребер, мостов,
        точек сочленения, циклов и компонент сильной связности. Прнимает
        список с числовыми значениями"""
        for i in range(len(self.lcdS)):
            self.lcdS[i].display(data[i])
