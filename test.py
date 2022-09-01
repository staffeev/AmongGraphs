from sqlalchemy import event
import sqlalchemy
from sqlalchemy.orm import attributes, relationship, declarative_base
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm.collections import attribute_mapped_collection, InstrumentedList
from models import db_session
from models.elements import Rib, Vertex, Graph

db_session.global_init('graphs.db')
session = db_session.create_session()
v1 = Vertex(name="A")
v2 = Vertex(name="B")
v3 = Vertex(name="C")
r = Rib()
r.add_nodes(v1, v2)
g = Graph()
g.add_ribs(r)
print(g.ribs)
r.replace_nodes(p1=v3)
print(g.ribs)
r.replace_nodes(p1=v2, p2=v3)
print(g.ribs)

# Base = declarative_base()
#
#
# association_table = sqlalchemy.Table(
#     'p_to_note',
#     Base.metadata,
#     sqlalchemy.Column('p', sqlalchemy.Integer,
#                       sqlalchemy.ForeignKey('p.id')),
#     sqlalchemy.Column('note', sqlalchemy.Integer,
#                       sqlalchemy.ForeignKey('note.id')))
#
#
# class Item(Base):
#     __tablename__ = "item"
#     id = Column(Integer, primary_key=True)
#     notes = relationship(
#         "Note",
#         collection_class=attribute_mapped_collection("note_key"),
#         backref="item",
#         cascade="all, delete-orphan",
#     )
#
#     def __init__(self):
#         self.inv_notes = {}
#
#
# class Note(Base):
#     __tablename__ = "note"
#     serialize_rules = ('-ps',)
#     id = Column(Integer, primary_key=True)
#     item_id = Column(Integer, ForeignKey("item.id"), nullable=False)
#     keyword = Column(String)
#     text = Column(String)
#     ps = relationship("P", secondary="p_to_note", backref="note")
#
#     def __init__(self):
#         self.old_key = None
#
#     @property
#     def note_key(self):
#         return (self.ps[0], self.ps[1])
#
#     def change_p(self, p1=None, p2=None):
#         self.old_key = self.note_key
#         self.ps[0] = self.ps[0] if p1 is None else p1
#         self.ps[1] = self.ps[1] if p2 is None else p2
#         item = self.item
#         item.notes[self.note_key] = self
#         item.notes.pop(self.old_key)
#         self.item = item
#
#     def add_p(self, p1, p2):
#         self.ps.append(p1)
#         self.ps.append(p2)
#
# class P(Base):
#     __tablename__ = "p"
#     serialize_rules = ('-note',)
#     id = Column(Integer, primary_key=True)
#     name = String()
#
#     def __repr__(self):
#         return f'P({self.name})'




# @event.listens_for(Note.ps, 'append')
# def receive_append(obj, value, initiator):
#     print(len(obj.ps))
#     if len(obj.ps) == 1 and obj.item is not None:
#         print('aaa')
#         obj.item.notes[obj.note_key] = obj
#         obj.item.notes.pop(obj.old_key)


#
#
# @event.listens_for(Item.notes, 'modified')
# def receive_modified(obj, initiator):
#     if obj.item is not None and len(obj.ps) == 2:
#         obj.item.notes[obj.note_key] = obj
#         obj.item.notes.pop(obj.old_key)
#         print(obj.item)

#
# @event.listens_for(Note.ps, 'dispose_collection')
# def receive_dispose_collection(obj, collection, collection_adapter):
#     obj.item.notes.pop((collection[0], collection[1]))
#     print('dispose', [i for i in collection])
#     "listen for the 'dispose_collection' event"



# item = Item()
# v1, v2, v3 = P(name="A"), P(name='B'), P(name="C")
# n1 = Note()
# print(n1.ps.pop(0))
# n1.add_p(v1, v2)
# n1.item = item
# print(item.notes)
# n1.change_p(p1=v3)
# print(item.notes)
# n1.change_p(p1=v2, p2=v1)
# print(item.notes)
# n1.ps.remove(v1)
# v3 = P(name="C")
# n1.ps.insert(0, v3)
# n1.ps[0] = v3
# print(n1.ps)
# item.notes[v3, v2] = n1
# item.notes.pop((v1, v2))
# print(item.notes)