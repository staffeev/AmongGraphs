from data import db_session
from data.node_object import *


if __name__ == '__main__':
    db_session.global_init('database.db')
    sess = db_session.create_session()
    v = Vertex()
    v.name = 'A'
    c1 = Cycle()
    c1.vertexes.append(v)
    c2 = Cycle()
    c2.vertexes.append(v)
    sess.add(v)
    sess.add(c1)
    sess.add(c2)
    sess.commit()