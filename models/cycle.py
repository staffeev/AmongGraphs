from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relation
from .db_session import SqlAlchemyBase
from models.edge import Rib


class Cycle(SqlAlchemyBase):
    """Класс для модели цикла в графе"""
    __tablename__ = "cycles"
    serialize_rules = ('-ribs', '-graph')
    id = Column(Integer, primary_key=True, autoincrement=True)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    ribs = relation("Rib", secondary="rib_to_cycle", backref="cycles",
                    cascade="all, delete")

    def add_ribs(self, *ribs: Rib) -> None:
        """Метод добавления ребер в цикл"""
        [self.ribs.append(rib) for rib in ribs if rib not in self.ribs]

    def __str__(self):
        return '-'.join(map(str, self.ribs))

    def __repr__(self):
        return f"Cycle({str(self)})"