from models.node import Vertex
from models.graph import Graph
from models import db_session
from forms.add_new_data_form import AddNewData
from sqlalchemy.orm import Session
from settings import ENTER_NODE, ARE_YOU_SURE
from PyQt5.QtWidgets import QMessageBox
from typing import Union
from math import cos, sin, radians, atan2


def get_angle(x1, y1, x2, y2) -> float:
    """Возвращает угол прямой"""
    return radians(180) - atan2(y2 - y1, x2 - x1)


def get_intersect_point(xc: float, yc: float, r: float, alpha: float) -> tuple[float, float]:
    """Возвращает точку пересечения окружности и прямой,
    выходящей из центра окружности"""
    return xc + r * cos(alpha), yc + r * sin(-alpha)


def get_equilateral_triangle(x, y, side, alpha):
    """Функция, возвращающая координаты вершин равностороннего треугольника
    по одной из его вершин"""
    x2 = x + side * cos(radians(-30) - alpha)
    y2 = y + side * sin(radians(-30) - alpha)
    x3 = x + side * cos(radians(30) - alpha)
    y3 = y + side * sin(radians(30) - alpha)
    return (x, y), (x2, y2), (x3, y3)


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


def rename_node(graph_name: str, idx: Union[int, tuple]) -> Union[str, None]:
    """Переименование вершиены по индексу или ячейке, в которой она находится"""
    session = db_session.create_session()
    graph = get_graph_by_name(session, graph_name)
    form = AddNewData(graph.get_nodes(), ENTER_NODE)
    if not form.exec():
        session.close()
        return
    new_name = form.inputData.text()
    if isinstance(idx, int):
        graph.nodes[idx].rename(new_name)
    elif isinstance(idx, tuple):
        node = [i for i in graph.nodes if i.cell == idx][0]
        node.rename(new_name)
    session.commit()
    session.close()
    return new_name


def add_node(graph_name: str, cell=None) -> None:
    """Функция для создания новой вершины в графе"""
    session = db_session.create_session()
    graph = get_graph_by_name(session, graph_name)
    form = AddNewData(graph.get_nodes(), ENTER_NODE)
    if not form.exec():
        session.close()
        return
    v = Vertex(name=form.inputData.text())
    graph.add_nodes(v)
    if cell is not None:
        v.set_cell(cell)
    session.add(v)
    session.commit()
    session.close()


def delete_node(parent, graph_name: str, selected: Union[list[tuple], set[int]]) -> bool:
    """Функция для удаления вершин из графа"""
    session = db_session.create_session()
    graph = get_graph_by_name(session, graph_name)
    if isinstance(selected, set):
        nodes = [graph.nodes[i] for i in selected]
    else:
        nodes = [i for i in graph.nodes if i.cell in selected]
    flag = QMessageBox.question(
        parent, "Delete nodes",
        f"{ARE_YOU_SURE} nodes {', '.join(map(str, nodes))}"
    )
    if flag == QMessageBox.No:
        session.close()
        return False
    [session.delete(node) for node in nodes]
    session.commit()
    session.close()
    return True