from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5 import uic


class EdgeData(QDialog):
    """Класс формы для добавления ребра или изменения его данных"""
    def __init__(self, n1, n2, rib=None):
        super().__init__()
        uic.loadUi('UI/edge_data.ui', self)
        self.setLayout(self.vl)
        self.radio1.setText(f'{n1.node_name}-{n2.node_name}')
        self.radio2.setText(f'{n2.node_name}-{n1.node_name}')
        if rib is None:
            return
        self.weight.setValue(rib.weight)
        if rib.is_directed:
            if str(n1.nodes[0]) == n1.node_name:
                self.radio1.setChecked(True)
            else:
                self.radio2.setChecked(True)
