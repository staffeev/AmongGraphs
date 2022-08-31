from models.elements import Graph
from models import db_session
from sqlalchemy.orm.collections import InstrumentedList

# db_session.global_init('graphs.db')
# session = db_session.create_session()
# print(type(session.query(Graph).first().nodes))
help(InstrumentedList)
# a = [1, 2, 3]
# idx = a.index(2)
# a.pop(idx)
# a.insert(idx, 4)
# print(a)