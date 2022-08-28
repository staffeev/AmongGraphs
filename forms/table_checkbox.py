from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, \
    QMessageBox, QCheckBox, QHBoxLayout
from PyQt5.QtCore import Qt


class TableCheckbox(QWidget):
    """Класс для флажка в ячейке таблицы"""
    def __init__(self):
        super().__init__()
        self.checkbox = QCheckBox()
        hl = QHBoxLayout()
        hl.setAlignment(Qt.AlignCenter)
        hl.addWidget(self.checkbox)
        hl.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hl)

    def setState(self, value: bool) -> None:
        """Метод переключения флажка в зависимости от логического знчения"""
        self.checkbox.setCheckState(Qt.Checked if value else Qt.Unchecked)