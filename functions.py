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
        if not rib.is_directed:
            ribs[rib.points[1].name, rib.points[0].name] = rib.weight
    return ribs