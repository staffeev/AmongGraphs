from models.elements import Graph, Vertex
from models import db_session
from forms.add_new_data_form import AddNewData
from sqlalchemy.orm import Session
from settings import ENTER_NODE


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


def add_node(graph_name: str) -> None:
    """Функция для создания новой вершины в графе"""
    session = db_session.create_session()
    graph = get_graph_by_name(session, graph_name)
    form = AddNewData(graph.get_nodes(), ENTER_NODE)
    if not form.exec():
        session.close()
        return
    v = Vertex(name=form.inputData.text())
    graph.add_nodes(v)
    session.add(v)
    session.commit()
    session.close()


def create_matrix(graph: Graph) -> list[list]:
    # TODO: create matrix
    pass