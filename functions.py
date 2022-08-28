from models.elements import Graph, Vertex, Rib
from sqlalchemy.orm import Session


def get_graph_names(session: Session) -> list:
    """Функция для получения имен всех графов в БД"""
    return [graph.name for graph in session.query(Graph).all()]


def get_new_rib() -> [Vertex, Vertex, Rib]:
    """Функция, возвращающая элементы ребра графа"""
    v1, v2, r = Vertex(), Vertex(), Rib()
    r.add_vertexes(v1, v2)
    return v1, v2, r


def create_ribs(graph: Graph) -> dict:
    """Функция, создающая словарь (список) ребер графа"""
    ribs = {}
    for rib in graph.ribs:
        ribs[rib.points[0].name, rib.points[1].name] = rib.weigth
        ribs[rib.points[1].name, rib.points[0].name] = rib.weigth
    return ribs