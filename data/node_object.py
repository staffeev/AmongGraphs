import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Vertex(SqlAlchemyBase, SerializerMixin):
    """Класс таблицы для вершин графа в БД"""
    __tablename__ = 'vertexes'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    is_cutpoint = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    graph = sqlalchemy.Column(sqlalchemy.Integer,
                              sqlalchemy.ForeignKey("graphs.id"))
    rib = sqlalchemy.Column(sqlalchemy.Integer,
                            sqlalchemy.ForeignKey("ribs.id"))
    cycle = sqlalchemy.Column(sqlalchemy.Integer,
                            sqlalchemy.ForeignKey("cycles.id"))
    component = sqlalchemy.Column(sqlalchemy.Integer,
                            sqlalchemy.ForeignKey("components.id"))


class Rib(SqlAlchemyBase, SerializerMixin):
    """Класс таблицы для ребер графа в БД"""
    __tablename__ = 'ribs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    start_node = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("vertexes.id"))
    end_node = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("vertexes.id"))
    rib_weight = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    is_bridge = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    graph = sqlalchemy.Column(sqlalchemy.Integer,
                              sqlalchemy.ForeignKey("graphs.id"))


class Cycle(SqlAlchemyBase, SerializerMixin):
    """Класс """
    __tablename__ = 'cycles'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    num_of_vertexes = sqlalchemy.Column(sqlalchemy.Integer)
    graph = sqlalchemy.Column(sqlalchemy.Integer,
                              sqlalchemy.ForeignKey("graphs.id"))
    vertexes = orm.relation("Vertex", backref='cycles')


class Component(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'components'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    num_of_vertexes = sqlalchemy.Column(sqlalchemy.Integer)
    graph = sqlalchemy.Column(sqlalchemy.Integer,
                              sqlalchemy.ForeignKey("graphs.id"))
    vertexes = orm.relation("Vertex", backref='components')


class Graphs(SqlAlchemyBase, SerializerMixin):
    """Класс таблицы для графов в БД"""
    __tablename__ = 'graphs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    is_directed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    vertexes = orm.relation("Vertex", backref='graphs')
    ribs = orm.relation("Rib", backref='graphs')
    cycles = orm.relation("Cycle", backref='graphs')
    components = orm.relation("Component", backref='graphs')