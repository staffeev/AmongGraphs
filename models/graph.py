from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relation
from sqlalchemy.orm.collections import attribute_mapped_collection
from .db_session import SqlAlchemyBase
from math import inf
from typing import Union
from models.node import Vertex
from models.edge import Rib
from models.chain import Chain


class Graph(SqlAlchemyBase):
    """Классс для модели графа"""
    __tablename__ = "graphs"
    serialize_rules = ('-ribs', '-nodes', '-chains')
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, index=True)
    is_directed = Column(Boolean, default=False)
    is_connected = Column(Boolean, default=False)
    nodes = relation("Vertex", backref="graph", cascade="all, delete-orphan")
    ribs = relation("Rib", backref="graph", cascade="all, delete-orphan",
                    collection_class=attribute_mapped_collection("key"))
    chains = relation("Chain", backref="graph", cascade="all, delete-orphan")

    def add_nodes(self, *vertexes: Vertex) -> None:
        """Метод добавления вершин в граф"""
        for vert in vertexes:
            if vert in self.nodes:
                continue
            self.nodes.append(vert)
            self.nodes[-1].set_random_cell()

    def add_ribs(self, *ribs: Rib) -> None:
        """Метод добавления ребер в граф"""
        for rib in ribs:
            self.ribs[rib.key] = rib
        self.add_nodes(*[
            vert for vert in {j for i in ribs for j in i.nodes}
            if vert not in self.nodes
        ])

    def add_chains(self, *chains: Chain) -> None:
        """Метод добавления цепей в граф"""
        [self.chains.append(chain) for chain in chains if chain not in self.chains]
        self.add_ribs(*[
            rib for rib in {j for i in chains for j in i.ribs}
            if rib not in self.ribs
        ])

    def get_nodes(self) -> list[str]:
        """Метод, возвращающий список имен вершин графа"""
        return list(map(str, self.nodes))

    def get_nodes_by_name(self, *names: str) -> list[Vertex]:
        """Метод, возвращающий список вершин графа по их именам"""
        return [i for i in self.nodes if i.name in names]

    def get_nodes_by_index(self, *indexes: int) -> list[Vertex]:
        """Метод, возвращающий список вершин графа по их именам"""
        return [self.nodes[i] for i in indexes]

    def get_nodes_by_id(self, *ids: int) -> list[Vertex]:
        """Возвращает вершины по их id"""
        return [i for i in self.nodes if i in ids]

    def get_nodes_by_cell(self, *cells: tuple[int]) -> list[Vertex]:
        """Возвращает вершины по координаатм их ячеек"""
        return [i for i in self.nodes if i in cells]

    def get_rib_by_id(self, idx: int) -> Union[Rib, None]:
        """Возвращает ребро по id"""
        rib = [i for i in self.ribs.values() if i.id == idx]
        if not rib:
            return None
        return rib[0]

    def get_rib_by_nodes(self, node1: Union[str, int, Vertex], node2: Union[str, int, Vertex]) -> Union[Rib, None]:
        """Метод, возвращающий ребро по именам его вершин"""
        if isinstance(node1, str):
            v1, v2 = self.get_nodes_by_name(node1, node2)
        elif isinstance(node1, int):
            v1, v2 = self.get_nodes_by_index(node1, node2)
        else:
            v1, v2 = node1, node2
        return self.ribs.get((v1, v2), None)

    def get_ordered_ribs(self) -> list[Rib]:
        """Метод, возвращающий список ребер, сортированнных по id"""
        return sorted(self.ribs.values(), key=lambda x: x.id)

    def get_occupied_cells(self) -> set[tuple[int, int]]:
        """Возвращает список занятых в холсте клеток"""
        return {i.cell for i in self.nodes}

    def get_cutpoints(self) -> list[Vertex]:
        """Возвращает все точки сочленения"""
        return [i for i in self.nodes if i.is_cutpoint]

    def get_bridges(self) -> list[Rib]:
        """Возвращает все мосты"""
        return [i for i in self.ribs.values() if i.is_bridge]

    def get_cycles(self) -> list[Chain]:
        """Возвращает все циклы"""
        return [i for i in self.chains if i.is_cycle]

    def get_components(self) -> list[Chain]:
        """Возвращает все компоненты сильной связности"""
        return [i for i in self.chains if i.is_component]

    def check_directed(self):
        """Определение того, является ли граф ориентированным"""
        if any([x.is_directed for x in self.ribs.values()]):
            self.is_directed = True
        else:
            self.is_directed = False

    def clear_cutpoints(self):
        """Убирает метку точки сочленения со всех таковых вершин"""
        [i.set_cutpoint(False) for i in self.get_cutpoints()]

    def clear_bridges(self):
        """Убирает метку моста со всех таковых ребер"""
        [i.set_bridge(False) for i in self.get_bridges()]

    def clear_cycles(self):
        """Убирает метку цикла с таковых цепей"""
        [i.set_cycle(False) for i in self.get_cycles()]

    def clear_components(self):
        """Убирает метку компоненты с таковых цепей"""
        [i.set_component(False) for i in self.get_components()]

    def clear_props(self):
        """Убирает свойства цепей, вершин и ребер"""
        self.clear_cutpoints()
        self.clear_bridges()
        self.clear_cycles()
        self.clear_components()