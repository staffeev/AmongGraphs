from models import db_session
from models.elements import *


db_session.global_init('graphs.db')
session = db_session.create_session()
# v = Vertex(name="a")
# v2 = Vertex(name="b")
# v3 = Vertex(name="c")
# r = Rib()
# r2 = Rib()
# r.add_vertexes(v, v2)
# r2.add_vertexes(v2, v3)
# session.add_all([v, v2, v3, r, r2])
v = session.query(Vertex).first()
print(session.query(Rib).all())
print(session.query(Vertex).all())
session.delete(v)
print(session.query(Rib).all())
print(session.query(Vertex).all())
# print(session.query(Vertex).all())
# r = session.query(Rib).first()
# session.delete(r)
# print(session.query(Vertex).all())


# print(session.query(Vertex).all())
# session.query(Graph).delete()
# print(session.query(Vertex).all())
# v1 = Vertex(name="A")
# v2 = Vertex(name="B")
# v3 = Vertex(name="C")
# v4 = Vertex(name="D")
# v5 = Vertex(name="E")
#
# r1 = Rib()
# r2 = Rib()
# r3 = Rib()
# r4 = Rib()
# r5 = Rib()
#
# r1.add_vertexes(v1, v2)
# r2.add_vertexes(v2, v3)
# r3.add_vertexes(v3, v1)
# r4.add_vertexes(v3, v4)
# r5.add_vertexes(v4, v5)
#
# c = Chain()
# c.add_ribs(r1, r2, r3)
#
# g = Graph(name="test1")
# g.add_chains(c)
# g.add_ribs(r4, r5)
#
# session.add_all([v1, v2, v3, v4, v5, r1, r2, r3, r4, r5, c, g])
# session.commit()
# session.close()
