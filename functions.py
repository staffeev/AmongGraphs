from models.elements import Graph
from sqlalchemy.orm import Session


def str_is_float(s: str) -> bool:
    """Функция, проверяющая, является ли строка вещественным числом"""
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_graph_names(session: Session) -> list:
    """Функция для получения имен всех графов в БД"""
    return [graph.name for graph in session.query(Graph).all()]


def get_graph_by_name(session: Session, name: str) -> Graph:
    """Функция для получения графа по имени"""
    return session.query(Graph).filter(Graph.name == name).first()


def create_ribs(graph: Graph) -> dict:
    """Функция, создающая словарь (список) ребер графа"""
    ribs = {}
    for rib in graph.ribs.values():
        ribs[rib.nodes[0].name, rib.nodes[1].name] = rib.weight
        if not rib.is_directed:
            ribs[rib.nodes[1].name, rib.nodes[0].name] = rib.weight
    return ribs


def create_matrix(graph: Graph) -> list[list]:
    # TODO: create matrix
    pass