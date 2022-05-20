from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QPushButton, QDialog, QDialogButtonBox


class GetRibs(QDialog):
    """Окно для ввода списка ребер графа"""
    def __init__(self):
        """Функция-инициализатор класса GetRibs"""
        super().__init__()
        uic.loadUi('UI/get_a_lot_ribs.ui', self)
        self.setWindowIcon(QIcon('imgs/icon3.png'))
        self.setFixedSize(self.size())
        # Создадим кнопки для отправки данных и для отмены
        self.btn_app = QPushButton('OK', self)
        self.btn_app.clicked.connect(self.check_and_return)
        self.btn_app.move(85, 325)
        self.box.clear()
        self.box.addButton(QDialogButtonBox.Cancel)
        # Создадим переменную, где будем хранить данные о ребрах графа
        self.data = None

    def check_and_return(self):
        """Функция, проверяющая введенные данные. Если данные корректны, они
        отправляются, иначе выводится сообщение об ошибке."""
        try:
            # Предусмотрим случай, если пользователь вместо пробелов
            # поставил символы табуляции
            new_ribs = self.field.toPlainText().replace('\t', ' ').replace(
                ',', '.').split('\n')
            self.data = []
            # Заполним массив полученными данными
            for i in filter(lambda x: x, new_ribs):
                s, e, v = i.split()
                v = int(v) if int(v) == float(v) else float(v)
                self.data.append((s, e, v))
            self.accept()
        except:
            self.data = None
            QMessageBox.critical(self, 'Ошибка', 'Данные введены '
                                                 'некорректно!')
