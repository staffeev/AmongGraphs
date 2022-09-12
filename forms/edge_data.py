from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from canvas.canvas_edge import CanvasEdge
from typing import Union


class EdgeData(QDialog):
    """Класс формы для добавления ребра или изменения его данных"""
    def __init__(self, rib: Union[tuple, CanvasEdge]):
        super().__init__()
        uic.loadUi('UI/edge_data.ui', self)
        self.setLayout(self.vl)
        if isinstance(rib, CanvasEdge):
            start, end = str(rib.start.node_name), str(rib.end.node_name)
            self.radio1.setText(f'{start}-{end}')
            self.radio2.setText(f'{end}-{start}')
            self.weight.setValue(rib.weight)
            if rib.is_directed:
                self.radio1.setChecked(True)
        else:
            n1, n2 = rib
            self.radio1.setText(f'{n1.node_name}-{n2.node_name}')
            self.radio2.setText(f'{n2.node_name}-{n1.node_name}')
