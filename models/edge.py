from sqlalchemy import Column, Integer, Boolean, ForeignKey, Float, Table
from sqlalchemy.orm import relation
from .db_session import SqlAlchemyBase
from models.node import Vertex
from typing import Union


association_table = Table(
    'vertex_to_rib',
    SqlAlchemyBase.metadata,
    Column('vertexes', Integer, ForeignKey('vertexes.id')),
    Column('ribs', Integer, ForeignKey('ribs.id'))
)


association_table_2 = Table(
    'rib_to_chain',
    SqlAlchemyBase.metadata,
    Column('ribs', Integer, ForeignKey('ribs.id')),
    Column('chains', Integer, ForeignKey('chains.id'))
)


class Rib(SqlAlchemyBase):
    """Класс для модели ребра графа"""
    __tablename__ = "ribs"
    serialize_rules = ('-nodes', '-graph')
    id = Column(Integer, primary_key=True, autoincrement=True)
    weight = Column(Float, default=1.0)
    is_directed = Column(Boolean, default=False)
    is_bridge = Column(Boolean, default=False)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    nodes = relation("Vertex", secondary="vertex_to_rib",
                      back_populates="ribs")
    old_key = None  # Значение прошлого ключа для словаря графа

    @property
    def key(self):
        try:
            return self.nodes[0], self.nodes[1]
        except IndexError:
            return self.id

    def get_crds(self) -> tuple[int, int, int, int]:
        """Возвращает екоординаты начала и конца ребра"""
        start = self.nodes[0].cell
        end = self.nodes[1].cell
        return start[0], start[1], end[0], end[1]

    def add_nodes(self, start: Vertex, end: Vertex) -> None:
        """Метод добавления начальной и конечной вершины ребра"""
        self.nodes.append(start)
        self.nodes.append(end)

    def clear_nodes(self):
        """Убирает вершины из ребра"""
        n1, n2 = self.nodes
        self.nodes.remove(n1)
        self.nodes.remove(n2)

    def swap_nodes(self) -> None:
        """Меняет местами вершины ребра"""
        n1, n2 = self.nodes
        self.replace_nodes(p1=n2, p2=n1)

    def change_weight(self, value: float) -> None:
        """Метод для изменения веса ребра"""
        self.weight = value

    def change_dir(self, value=None) -> None:
        """Метод для создания (удаления) направления ребра"""
        if value is None:
            self.is_directed = not self.is_directed
        else:
            self.is_directed = int(value)

    def change_attrs(self, idx: int, arg: Union[str, float, bool]) -> None:
        """Метод для изменения атрибутов объекта"""
        if isinstance(arg, float):
            self.change_weight(arg)
        elif isinstance(arg, bool):
            self.change_dir(arg)
        elif isinstance(arg, str):
            self.replace_node(idx, arg)

    def replace_nodes(self, p1=None, p2=None) -> None:
        """Метод для замены вершин графа"""
        if p1 is not None:
            self.replace_node(0, p1)
        if p2 is not None:
            self.replace_node(1, p2)

    def replace_node(self, idx, node: Union[str, Vertex]) -> None:
        """Метод для замены вершины графа"""
        self.old_key = self.key
        if isinstance(node, str):
            node_name = node
            try:
                node = self.graph.get_nodes_by_name(node)[0]
            except IndexError:
                node = Vertex()
                node.rename(node_name)
        try:
            self.nodes.pop(idx)
            self.nodes.insert(idx, node)
        except IndexError:
            self.nodes.append(node)
        self.graph.add_nodes(node)
        self.update_graph_collection()

    def __str__(self):
        return f"{self.nodes[0].name}-{self.nodes[1].name}"

    def __repr__(self):
        return f"Rib({str(self)}; {self.weight})"

    def update_graph_collection(self) -> None:
        """Метод для обновления словаря графа"""
        if self.key is None:
            return
        graph = self.graph
        graph.ribs[self.key] = self
        graph.ribs.pop(self.old_key, None)
        self.graph = graph

    def set_bridge(self, value: bool):
        """Устаналивает метку моста"""
        self.is_bridge = value