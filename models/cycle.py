from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relation
from .db_session import SqlAlchemyBase
from models.edge import Rib


class Cycle(SqlAlchemyBase):
    """Класс для модели цепи в графе"""
    __tablename__ = "cycles"
    serialize_rules = ('-ribs', '-graph')
    id = Column(Integer, primary_key=True, autoincrement=True)
    length = Column(Integer)
    is_cycle = Column(Boolean, default=False)
    is_component = Column(Boolean, default=False)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    ribs = relation("Rib", secondary="rib_to_chain", backref="cycles",
                    cascade="all, delete")

    def add_ribs(self, *ribs: Rib) -> None:
        """Метод добавления ребер в цепь"""
        [self.ribs.append(rib) for rib in ribs if rib not in self.ribs]