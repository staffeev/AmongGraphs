import networkx.exception

from functions import create_ribs, get_graph_by_name
from models import db_session
from networkx import DiGraph, simple_cycles, articulation_points, bridges, \
    strongly_connected_components, is_strongly_connected
from models.cycle import Cycle
from models.component import Component


class PropertyDefiner:
    """Класс определителя свойств графа"""
    def __init__(self):
        self.graph_name = None
        self.graph = None

    def create_nx_graph(self):
        """Создает граф из библиотеки Networkx для определения свойств"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        ribs = create_ribs(graph)
        ribs = [(i, j, ribs[i, j]) for i, j in ribs]
        self.graph = DiGraph()
        self.graph.add_weighted_edges_from(ribs)
        session.close()

    def change_graph(self, name: str):
        """Меняет граф"""
        self.graph_name = name
        self.create_nx_graph()

    def define_all(self):
        """Определение сех свойств графа"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        graph.clear_props()
        session.commit()
        session.close()
        self.check_directed()
        self.check_connected()
        self.find_cutpoints()
        self.find_bridges()
        self.find_cycles()
        self.find_components()

    def check_directed(self):
        """Определение того, является ли граф ориентированным"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        graph.check_directed()
        session.commit()
        session.close()

    def check_connected(self):
        """Определение того, является ли граф сильно связным"""
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        try:
            graph.is_connected = is_strongly_connected(self.graph)
        except networkx.exception.NetworkXPointlessConcept:
            pass
        session.commit()
        session.close()

    def find_bridges(self):
        """Определение мостов"""
        graph_bridges = list(bridges(self.graph.to_undirected()))
        if not graph_bridges:
            return
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        for bridge in graph_bridges:
            n1, n2 = bridge
            rib = graph.get_rib_by_nodes(n1, n2)
            if rib is None:
                rib = graph.get_rib_by_nodes(n2, n1)
            rib.set_bridge(True)
        session.commit()
        session.close()

    def find_cutpoints(self):
        """Определение точек сочленения"""
        cutpoints = list(articulation_points(self.graph.to_undirected()))
        if not cutpoints:
            return
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        nodes = graph.get_nodes_by_name(*cutpoints)
        [n.set_cutpoint(True) for n in nodes]
        session.commit()
        session.close()

    def find_cycles(self):
        """Определение циклов"""
        cycles = list(simple_cycles(self.graph))
        if not cycles:
            return
        print(cycles)
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        g_cycles = graph.cycles
        [session.delete(c) for c in g_cycles]
        for c in filter(lambda x: len(x) > 2, cycles):
            cycle = Cycle()
            for j in range(1, len(c)):
                rib = graph.get_rib_by_nodes(c[j - 1], c[j])
                if rib is None:
                    rib = graph.get_rib_by_nodes(c[j], c[j - 1])
                cycle.add_ribs(rib)
            graph.add_cycles(cycle)
            session.add(cycle)
        session.commit()
        session.close()

    def find_components(self):
        """Определение компонент сильной связности"""
        comps = list(strongly_connected_components(self.graph))
        if not comps:
            return
        session = db_session.create_session()
        graph = get_graph_by_name(session, self.graph_name)
        g_comps = graph.components
        [session.delete(c) for c in g_comps]
        for c in comps:
            comp = Component()
            nodes = graph.get_nodes_by_name(*c)
            comp.add_nodes(nodes)
            graph.add_comps(comp)
            session.add(comp)
        session.commit()
        session.close()

        print(comps)
        # TODO

    def find_min_path(self):
        """Нахождение минимального пути между двумя вершинами"""
        # TODO