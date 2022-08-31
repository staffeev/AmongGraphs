import sqlalchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relation
from .db_session import SqlAlchemyBase
from math import inf
from typing import Union


association_table = sqlalchemy.Table(
    'vertex_to_rib',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('vertexes', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('vertexes.id')),
    sqlalchemy.Column('ribs', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('ribs.id')))


association_table_2 = sqlalchemy.Table(
    'rib_to_chain',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('ribs', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('ribs.id')),
    sqlalchemy.Column('chains', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('chains.id')))


class Vertex(SqlAlchemyBase):
    """Класс для модели вершины графа"""
    __tablename__ = 'vertexes'
    serialize_rules = ('-ribs_', '-chains_', '-graph')
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    is_cutpoint = Column(Boolean, default=False)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    ribs = relation("Rib", secondary="vertex_to_rib",
                    back_populates="nodes", cascade="all, delete")

    def rename(self, name: str) -> None:
        """Метод для переименования вершины"""
        self.name = name.strip()

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Node({self.name})"


class Rib(SqlAlchemyBase):
    """Класс для модели ребра графа"""
    __tablename__ = "ribs"
    serialize_rules = ('-nodes', '-graph')
    id = Column(Integer, primary_key=True, autoincrement=True)
    weight = Column(Float, default=1)
    is_directed = Column(Boolean, default=False)
    is_bridge = Column(Boolean, default=False)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    nodes = relation("Vertex", secondary="vertex_to_rib",
                      back_populates="ribs")

    def add_nodes(self, start: Vertex, end: Vertex) -> None:
        """Метод добавления начальной и конечной вершины ребра"""
        self.nodes.append(start)
        self.nodes.append(end)

    def change_weight(self, value: float) -> None:
        """Метод для изменения веса ребра"""
        self.weight = value

    def change_dir(self, value: bool) -> None:
        """Метод для создания (удаления) направления ребра"""
        self.is_directed = int(value)

    def change_attrs(self, idx: int, arg: Union[str, float, bool]) -> None:
        """Метод для изменения атрибутов объекта"""
        if isinstance(arg, float):
            self.change_weight(arg)
        elif isinstance(arg, bool):
            self.change_dir(arg)
        elif isinstance(arg, str):
            self.replace_node(idx, arg)
            # self.nodes[idx].rename(arg)

    def replace_node(self, idx, node_name: str) -> None:
        """Метод для замены вершин графа"""
        try:
            node = [i for i in self.graph.nodes if i.name == node_name][0]
        except IndexError:
            node = Vertex()
            node.rename(node_name)
        try:
            self.nodes.pop(idx)
            self.nodes.insert(idx, node)
        except IndexError:
            self.nodes.append(node)
        self.graph.add_nodes(node)

    def __str__(self):
        return f"{self.nodes[0].name}-{self.nodes[1].name}"

    def __repr__(self):
        return f"Rib({str(self)})"


class Chain(SqlAlchemyBase):
    """Класс для модели цепи в графе"""
    __tablename__ = "chains"
    serialize_rules = ('-ribs', '-graph')
    id = Column(Integer, primary_key=True, autoincrement=True)
    length = Column(Integer)
    is_cycle = Column(Boolean, default=False)
    is_component = Column(Boolean, default=False)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    ribs = relation("Rib", secondary="rib_to_chain", backref="chains",
                    cascade="all, delete")

    def add_ribs(self, *ribs: Rib) -> None:
        """Метод добавления ребер в цепь"""
        [self.ribs.append(rib) for rib in ribs if rib not in self.ribs]


class Graph(SqlAlchemyBase):
    """Классс для модели графа"""
    __tablename__ = "graphs"
    serialize_rules = ('-ribs', '-nodes', '-chains')
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, index=True)
    num_of_vertexes = Column(Integer)
    num_of_ribs = Column(Integer)
    num_of_cutpoints = Column(Integer)
    num_of_bridges = Column(Integer)
    num_of_cycles = Column(Integer)
    num_of_strong_components = Column(Integer)
    min_cost_way = Column(Integer, default=inf)
    is_directed = Column(Boolean, default=False)
    is_connected = Column(Boolean, default=False)
    nodes = relation("Vertex", backref="graph", cascade="all, delete-orphan")
    ribs = relation("Rib", backref="graph", cascade="all, delete-orphan")
    chains = relation("Chain", backref="graph", cascade="all, delete-orphan")

    def add_nodes(self, *vertexes: Vertex) -> None:
        """Метод добавления вершин в граф"""
        [self.nodes.append(vert) for vert in vertexes if vert not in self.nodes]

    def add_ribs(self, *ribs: Rib) -> None:
        """Метод добавления ребер в граф"""
        [self.ribs.append(rib) for rib in ribs if rib not in self.ribs]
        self.add_nodes(*[
            vert for vert in {j for i in ribs for j in i.nodes}
            if vert not in self.nodes
        ])

    def add_chains(self, *chains: Chain) -> None:
        """Метод добавления цепей в граф"""
        [self.chains.append(chain) for chain in chains if chain not in self.chains]
        self.add_ribs(*[
            rib for rib in {j for i in chains for j in i.ribs}
            if rib not in self.ribs
        ])

    def get_nodes(self) -> list[str]:
        """Метод, возвращающий список имен вершин графа"""
        return list(map(str, self.nodes))

    def get_nodes_by_name(self, *names: str) -> list[Vertex]:
        """Метод, возвращающий список вершин графа по их именам"""
        return [i for i in self.nodes if i.name in names]

    def get_nodes_by_index(self, *indexes: int) -> list[Vertex]:
        """Метод, возвращающий список вершин графа по их именам"""
        return [self.nodes[i] for i in indexes]

    def get_rib_by_nodes(self, node1: Union[str, int], node2: Union[str, int]) -> Union[Rib, None]:
        """Метод, возвращающий ребро по именам его вершин"""
        if isinstance(node1, str):
            v1, v2 = self.get_nodes_by_name(node1, node2)
        else:
            v1, v2 = self.get_nodes_by_index(node1, node2)
        rib = [i for i in self.ribs if i.points[0] == v1 and i.points[1] == v2]
        if not rib:
            return
        return rib[0]
