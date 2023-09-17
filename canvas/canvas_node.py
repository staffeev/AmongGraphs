from models.node import Vertex
from settings import RED, BLACK, SELECTED_ITEM_COLOR, WHITE
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class CanvasNode:
    """Класс для вершины на холсте"""
    def __init__(self, node: Vertex, parent):
        self.parent = parent
        self.node_id = node.id
        self.node_name = node.name
        self.node_name_stipped = self.node_name.strip('"')
        self.color = RED
        self.row, self.col = node.cell
        self.selected = False
        self.bool_colorize = True
        self.bool_draw_textbox = False

    def __str__(self):
        return self.node_name_stipped

    def setColor(self, color):
        self.color = color
    
    def change_color_condition(self):
        self.bool_colorize = not self.bool_colorize

    def setName(self, name: str):
        """Установка нового имени"""
        self.node_name = name
        self.node_name_stipped = name.strip('"')

    def setCell(self, row, col):
        """Установка новых координат"""
        self.row, self.col = row, col

    def select(self):
        self.selected = True

    def unselect(self):
        self.selected = False
    
    def get_text_rect(self, font_size: int, dist: int, x: int, y: int) -> tuple[int]:
        """Возвращает параметры прямоугольника, в котором расположено имя вершины"""
        text_width = font_size * len(self.node_name_stipped)
        new_x = x + dist // 2 - text_width // 2
        return new_x, y, text_width, dist

    def draw(self):
        """Рисование вершины"""
        dist = self.parent.dist
        x, y = self.parent.getPoint(self.row, self.col)
        font_size = int(dist // 2)
        font = QFont()
        font.setPixelSize(font_size)
        self.parent.qp.setBrush(SELECTED_ITEM_COLOR if self.selected else self.color)
        self.parent.qp.setPen(BLACK)
        self.parent.qp.setFont(font)
        if self.bool_colorize:
            self.parent.qp.drawEllipse(int(x), int(y), int(dist), int(dist))
        text_rect = self.get_text_rect(font_size, int(dist), int(x), int(y))
        if self.bool_draw_textbox:
            self.parent.qp.setBrush(WHITE)
            self.parent.qp.setPen(WHITE)
            self.parent.qp.drawRect(*text_rect)
        self.parent.qp.setPen(BLACK)
        self.parent.qp.drawText(*text_rect, Qt.AlignCenter, self.node_name_stipped)

