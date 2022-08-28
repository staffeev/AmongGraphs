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


def get_graph_by_name(session: Session, name: str) -> Graph:
    """Функция для получения графа по имени"""
    graph = session.query(Graph).filter(Graph.name == name).first()
    return graph


def create_ribs(graph: Graph) -> dict:
    """Функция, создающая словарь (список) ребер графа"""
    ribs = {}
    for rib in graph.ribs:
        ribs[rib.points[0].name, rib.points[1].name] = rib.weight
        ribs[rib.points[1].name, rib.points[0].name] = rib.weight
    return ribs