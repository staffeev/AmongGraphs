import sqlalchemy
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relation
from .db_session import SqlAlchemyBase


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
    serialize_rules = ('-ribs',)
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    is_cutpoint = Column(Boolean, default=False)
    ribs_ = relation("Rib", secondary="vertex_to_rib", backref="vertexes")
    chains_ = relation("Chain", secondary="vertex_to_chain", backref="vertexes")


class Rib(SqlAlchemyBase):
    """Класс для модели ребра графа"""
    __tablename__ = "ribs"
    serialize_rules = ('-points',)
    id = Column(Integer, primary_key=True, autoincrement=True)
    weigth = Column(Integer)
    is_directed = Column(Boolean, default=False)
    is_bridge = Column(Boolean, default=False)
    points = relation("Vertex", secondary="vertex_to_rib", backref="ribs")


class Chain(SqlAlchemyBase):
    """Класс для модели цепи в графе"""
    __tablename__ = "chains"
    id = Column(Integer, primary_key=True, autoincrement=True)
    length = Column(Integer)
    is_cycle = Column(Boolean, default=False)
    points = relation("Vertex", secondary="vertex_to_chain", backref="chains")