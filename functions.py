from models.elements import Graph, Vertex, Rib
from sqlalchemy.orm import Session
from models import db_session
from typing import Union


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


def get_graph_nodes(session: Session, graph_name: str) -> list[str]:
    """Функция, возвращающая все вершины графа"""
    graph = session.query(Graph).filter(Graph.name == graph_name).first()
    return list(map(str, graph.nodes))


def get_new_rib() -> [Vertex, Vertex, Rib]:
    """Функция, возвращающая элементы ребра графа"""
    v1, v2, r = Vertex(), Vertex(), Rib()
    r.add_nodes(v1, v2)
    return v1, v2, r


def get_graph_by_name(session: Session, name: str) -> Graph:
    """Функция для получения графа по имени"""
    return session.query(Graph).filter(Graph.name == name).first()


def get_node_by_name(session: Session, name: str) -> Vertex:
    """Функция для получения вершины по имени"""
    return session.query(Vertex).filter(Vertex.name == name).first()


def create_ribs(graph: Graph) -> dict:
    """Функция, создающая словарь (список) ребер графа"""
    ribs = {}
    for rib in graph.ribs:
        ribs[rib.nodes[0].name, rib.nodes[1].name] = rib.weight
        if not rib.is_directed:
            ribs[rib.nodes[1].name, rib.nodes[0].name] = rib.weight
    return ribs