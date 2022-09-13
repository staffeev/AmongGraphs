from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relation
from .db_session import SqlAlchemyBase
from itertools import product
from settings import MAX_CANVAS_SIZE
from random import choice


association_table_3 = Table(
    'vertex_to_component',
    SqlAlchemyBase.metadata,
    Column('vertexes', Integer, ForeignKey('vertexes.id')),
    Column('components', Integer, ForeignKey('components.id'))
)


class Vertex(SqlAlchemyBase):
    """Класс для модели вершины графа"""
    __tablename__ = 'vertexes'
    serialize_rules = ('-ribs_', '-graph')
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    is_cutpoint = Column(Boolean, default=False)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    ribs = relation("Rib", secondary="vertex_to_rib",
                    back_populates="nodes", cascade="all, delete")
    row = Column(Integer, default=0)  # Адрес в сетке холста
    col = Column(Integer, default=0)

    @property
    def cell(self):
        return self.row, self.col

    def set_random_cell(self) -> None:
        """Установка вершины в случайную клетку холста"""
        cells = self.graph.get_occupied_cells()
        free_cells = set(product(range(MAX_CANVAS_SIZE), repeat=2)) - cells
        self.row, self.col = choice(list(free_cells))

    def set_cell(self, cell):
        """Установка вершины в ячейку"""
        self.row, self.col = cell

    def shift_cell(self, shift):
        """Смещение вершины"""
        self.row += shift[0]
        self.col += shift[1]

    def rename(self, name: str) -> None:
        """Метод для переименования вершины"""
        self.name = name.strip()

    def set_cutpoint(self, value: bool):
        """Установка флага точки сочленения"""
        self.is_cutpoint = value

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Node({self.name})"