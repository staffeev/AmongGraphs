import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


association_table = sqlalchemy.Table(
    'vertex_to_rib',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('vertexes', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('vertexes.id')),
    sqlalchemy.Column('ribs', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('ribs.id')))


class Vertex(SqlAlchemyBase):
    __tablename__ = 'vertexes'
    serialize_rules = ('-ribs',)
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    ribs_ = orm.relation("Rib", secondary="vertex_to_rib", backref="vertexes")


class Rib(SqlAlchemyBase):
    __tablename__ = "ribs"
    serialize_rules = ('-points',)
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    weigth = sqlalchemy.Column(sqlalchemy.Integer)
    is_directed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    points = orm.relation("Vertex", secondary="vertex_to_rib", backref="ribs")