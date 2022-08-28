import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QResizeEvent, QCloseEvent
from models import db_session


def except_hook(cls, exception, traceback):
    """Функция для отлова возможных исключений, вознкающих при работе с Qt"""
    sys.__excepthook__(cls, exception, traceback)


class Mentor(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('UI/main.ui', self)
        self.splitter.setSizes([200, 600])
        self.widget.setLayout(self.hl)
        self.setCentralWidget(self.widget)
        self.initUI()

    def initUI(self) -> None:
        """Настройка UI и привязка событий к обработчикам"""
        # Настройка относительного позиционирования элементов главного окна
        self.splitter.setSizes([200, 600])
        self.widget.setLayout(self.hl)
        self.setCentralWidget(self.widget)
        # События меню
        self.actionCreate.triggered.connect(self.createGraph)
        self.actionOpen.triggered.connect(self.openGraph)
        self.actionSave.triggered.connect(self.saveChanges)
        self.actionExit.triggered.connect(self.close)
        # Остальные события

    def createGraph(self) -> None:
        """Метод для создания графа"""
        # TODO: create graph
        pass

    def openGraph(self) -> None:
        """Метод для откытия графа"""
        # TODO: open graph
        pass

    def saveChanges(self) -> None:
        """Метод для сохранения изменений"""
        # TODO: save changes
        pass


    def resizeEvent(self, event: QResizeEvent) -> None:
        """Обработчик изменения размера окна"""
        # TODO: resize event
        pass

    def closeEvent(self, event: QCloseEvent) -> None:
        """Событие закрытия приложения"""
        # TODO: close DB
        print('Bye')


if __name__ == '__main__':
    db_session.global_init('graphs.db')
    app = QApplication(sys.argv)
    programme = Mentor()
    programme.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())

