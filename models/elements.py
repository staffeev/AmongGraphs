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
    'vertex_to_chain',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('vertexes', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('vertexes.id')),
    sqlalchemy.Column('chains', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('chains.id')))


class Vertex(SqlAlchemyBase):
    """Класс для модели вершины графа"""
    __tablename__ = 'vertexes'
    serialize_rules = ('-ribs_', '-chains_', '-graph')
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    is_cutpoint = Column(Boolean, default=False)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    graph = relation("Graph")


class Rib(SqlAlchemyBase):
    """Класс для модели ребра графа"""
    __tablename__ = "ribs"
    serialize_rules = ('-points', '-graph')
    id = Column(Integer, primary_key=True, autoincrement=True)
    weigth = Column(Integer, default=1)
    is_directed = Column(Boolean, default=False)
    is_bridge = Column(Boolean, default=False)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    graph = relation("Graph")
    points = relation("Vertex", secondary="vertex_to_rib", backref="ribs")

    def add_points(self, start: Vertex, end: Vertex) -> None:
        """Метод добавления начальной и конечной вершины ребра"""
        self.points.append(start)
        self.points.append(end)


class Chain(SqlAlchemyBase):
    """Класс для модели цепи в графе"""
    __tablename__ = "chains"
    serialize_rules = ('-points', '-graph')
    id = Column(Integer, primary_key=True, autoincrement=True)
    length = Column(Integer)
    is_cycle = Column(Boolean, default=False)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    graph = relation("Graph")
    points = relation("Vertex", secondary="vertex_to_chain", backref="chains")


class Graph(SqlAlchemyBase):
    """Классс для модели графа"""
    __tablename__ = "graphs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    num_of_vertex = Column(Integer)
    num_of_ribs = Column(Integer)
    num_of_cutpoints = Column(Integer)
    num_of_bridges = Column(Integer)
    num_of_cycles = Column(Integer)
    num_of_strong_components = Column(Integer)
    min_cost_way = Column(Integer, default=inf)
    is_directed = Column(Boolean, default=False)
    is_connected = Column(Boolean, default=False)
    points = relation("Vertex", back_populates='graph')
    ribs = relation("Rib", back_populates='graph')
    chains = relation("Chain", back_populates='graph')

    def add_vertexes(self, *vertexes: Vertex) -> None:
        """Метод добавления вершин в граф"""
        [self.points.append(vert) for vert in vertexes]

    def add_ribs(self, *ribs: Rib) -> None:
        """Метод добавления ребер в граф"""
        [self.ribs.append(rib) for rib in ribs]

    def add_chains(self, *chains: Chain) -> None:
        """Метод добавления цепей в граф"""
        [self.chains.append(chain) for chain in chains]