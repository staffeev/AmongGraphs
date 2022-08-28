import sqlalchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relation
from .db_session import SqlAlchemyBase
from math import inf


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
    name = Column(String)
    is_cutpoint = Column(Boolean, default=False)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    ribs = relation("Rib", secondary="vertex_to_rib",
                    back_populates="points", cascade="all, delete")

    def rename(self, name: str) -> None:
        """Метод для переименования вершины"""
        self.name = name


class Rib(SqlAlchemyBase):
    """Класс для модели ребра графа"""
    __tablename__ = "ribs"
    serialize_rules = ('-points', '-graph')
    id = Column(Integer, primary_key=True, autoincrement=True)
    weight = Column(Integer, default=1)
    is_directed = Column(Boolean, default=False)
    is_bridge = Column(Boolean, default=False)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    points = relation("Vertex", secondary="vertex_to_rib",
                      back_populates="ribs")

    def add_vertexes(self, start: Vertex, end: Vertex) -> None:
        """Метод добавления начальной и конечной вершины ребра"""
        self.points.append(start)
        self.points.append(end)

    def change_weight(self, value: int) -> None:
        """Метод для изменения веса ребра"""
        self.weight = value

    def __str__(self):
        return f"{self.points[0].name}-{self.points[1].name}"


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
    serialize_rules = ('-ribs', '-points', '-chains')
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, index=True)
    num_of_vertex = Column(Integer)
    num_of_ribs = Column(Integer)
    num_of_cutpoints = Column(Integer)
    num_of_bridges = Column(Integer)
    num_of_cycles = Column(Integer)
    num_of_strong_components = Column(Integer)
    min_cost_way = Column(Integer, default=inf)
    is_directed = Column(Boolean, default=False)
    is_connected = Column(Boolean, default=False)
    points = relation("Vertex", backref="graph", cascade="all, delete-orphan")
    ribs = relation("Rib", backref="graph", cascade="all, delete-orphan")
    chains = relation("Chain", backref="graph", cascade="all, delete-orphan")

    def add_vertexes(self, *vertexes: Vertex) -> None:
        """Метод добавления вершин в граф"""
        [self.points.append(vert) for vert in vertexes if vert not in self.points]

    def add_ribs(self, *ribs: Rib) -> None:
        """Метод добавления ребер в граф"""
        [self.ribs.append(rib) for rib in ribs if rib not in self.ribs]
        self.add_vertexes(*[
            vert for vert in {j for i in ribs for j in i.points}
            if vert not in self.points
        ])

    def add_chains(self, *chains: Chain) -> None:
        """Метод добавления цепей в граф"""
        [self.chains.append(chain) for chain in chains if chain not in self.chains]
        self.add_ribs(*[
            rib for rib in {j for i in chains for j in i.ribs}
            if rib not in self.ribs
        ])