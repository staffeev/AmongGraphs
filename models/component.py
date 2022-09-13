from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relation
from .db_session import SqlAlchemyBase
from models.node import Vertex


class Component(SqlAlchemyBase):
    """Класс для модели цепи в графе"""
    __tablename__ = "components"
    serialize_rules = ('-nodes', '-graph')
    id = Column(Integer, primary_key=True, autoincrement=True)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    nodes = relation("Vertex", secondary="vertex_to_component", backref="components")

    def add_nodes(self, *nodes: Vertex) -> None:
        """Метод добавления ребер в цепь"""
        [self.nodes.append(node) for node in nodes if node not in self.nodes]

    def __str__(self):
        return ', '.join(sorted(map(str, self.nodes)))

    def __repr__(self):
        return f"Component({str(self)})"