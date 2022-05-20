import io
import sqlite3
import sys
import webbrowser
from colour import Color
from math import inf
from os import getcwd
from csv import DictWriter, QUOTE_MINIMAL

import networkx as nx
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, \
    QMenuBar, QAction, QMessageBox, QFileDialog, QInputDialog, \
    QTableWidgetItem, QWidget
from matplotlib import pyplot as plt

from forms.get_graph_name import GetGraphName
from forms.get_csv import GetCsv
from forms.get_ribs import GetRibs
from GraphProperties import GraphProperties
from forms.save_as_form import SaveAsForm
from functions import ford_algorithm, dfs_time_out, dfs_create_comp, \
    dfs_bridges, screen_size


WIDTH, HEIGHT = screen_size()
sdvig = 50 if HEIGHT % 100 else 70
WIDTH_MAIN_WINDOW, HEIGHT_MAIN_WINDOW = WIDTH // 2, \
                                        (HEIGHT - HEIGHT % 100) // 2 - sdvig
if HEIGHT_MAIN_WINDOW % 50:
    HEIGHT_MAIN_WINDOW = HEIGHT_MAIN_WINDOW - HEIGHT_MAIN_WINDOW % 50
PROPS = {'Вершины': ['NumOfVert', 'Vertex'], 'Ребра': ['NumOfRibs'],
         'Мосты': ['NumOfBridges', 'Bridges'],
         'Точки сочленения': ['NumOfArtP', 'ArtP'],
         'Циклы': ['NumOfCycles', 'Cycles'],
         'Компоненты': ['NumOfStrongComps', 'StrongComps'],
         'Минимальные пути': ['MinWays']}


def except_hook(cls, exception, traceback):
    """Функция для отлова возможных исключений, вознкающих при работе с Qt"""
    sys.__excepthook__(cls, exception, traceback)


class Graph(QWidget):
    """Граф, то есть таблица из базы данных, представленный в удобной форме.
    Имеется возможность редкатировать данные графа."""
    def __init__(self, name, con):
        """Функция-инициализатор класса Graph.
        При инициализации принимает имя графа и подключение к базе даннных."""

        super().__init__()
        # Настроим приложение (размер, иконка, заголовок)
        uic.loadUi('UI/graph.ui', self)
        self.name = name
        self.move(WIDTH // 2 - 250, HEIGHT // 2 - 200)
        self.setFixedSize(self.size())
        self.setWindowIcon(QIcon('imgs/icon2.png'))
        self.setWindowTitle(name)
        # Подключимся к БД
        self.con = con
        # Создадим таблицу с ребрами графа
        self.tableWidget.setColumnCount(4)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.titles = ['id', 'Начало ребра', 'Конец ребра', 'Вес ребра']
        self.tableWidget.setHorizontalHeaderLabels(self.titles)
        # Создадим очередь изменений
        self.modified = {}

        # Создадим кнопки для добавления элемента, сохранения таблциы и
        # удаления элемента
        self.btn_add.clicked.connect(self.add)
        self.btn_add.setShortcut(QKeySequence('Ctrl+N'))

        self.btn_save.clicked.connect(self.save)
        self.btn_save.setShortcut(QKeySequence('Ctrl+S'))

        self.btn_del.clicked.connect(self.delete)
        self.btn_del.setShortcut(QKeySequence('Del'))

        # Создадим граф, изначально - None
        self.fig = None
        self.graph = None
        # Определим вершины, компоненты сильной связности, мосты, точки
        # сочленения и циыл графа, изначально отсутствуют
        self.nodes = []
        self.comps = []
        self.cycles = []
        self.bridges = []
        self.art_p = []
        self.ways = {}

    def item_changed(self, item):
        """Функция, отслеживающая изменения в таблице ребер графа.
        Изменения (строка и название столбца) заносятся в очередь.
        Изменения и новые даннеы заносятся в словарь изменений."""
        # Если элемент таблицы изменен, строка, столбец изменений и новое
        # значение сохраняется в очереди изменений
        self.modified[item.row() + 1, self.titles[item.column()]] = \
            item.text()

    def save(self):
        """Функция, сохраняющая изменения в таблице ребер графа. Вызывается
        нажатием соответствующйе кнопки"""

        cur = self.con.cursor()
        for i in self.modified:
            idx, col = i  # Получаем измененную строку и столбец
            if col != 'id':
                # Обновляем данные в БД
                cur.execute(f'''UPDATE {self.name} SET 
                [{col}] = '{self.modified[i]}' WHERE id = {idx}''')
        self.con.commit()  # Подтверждаем изменения
        self.modified.clear()  # Очистка очереди изменений
        self.load_table(self.con)
        self.create_graph()

    def add(self):
        """Функция для добавления ребра в таблицу ребер графа.
        Вызывается нажатием соответствующей кнопки."""
        # Вставляем в таблицу из БД новую строку, изначально заполненную нулями
        self.con.cursor().execute(
            f'INSERT INTO {self.name} VALUES ('
            f'{self.tableWidget.rowCount() + 1}, 0, 0, 0)')
        self.con.commit()  # Подтверждение изменений в БД
        self.save()
        self.load_table(self.con)  # Обновляем таблицу

    def add_a_lot(self):
        """Функция добавления нескольких ребер в граф. Добавление
        осуществляется в новом окне."""
        # Получим новые ребра и результат нажатия пользователя на кнопку
        QMessageBox.warning(self, 'Добавление ребер',
                            'Напишите данные о ребрах графа в формате "Начало '
                            'ребра Конец ребра Вес ребра" через пробел. Вес '
                            'ребра является числом.')
        ch = GetRibs()
        res = ch.exec_()
        # Если пользователь нажал на кнопку ОК, ребра будут добавлены
        if res:
            new_ribs = ch.data
            cur = self.con.cursor()
            # Для новых id нам нужно узнать количество строк в таблице
            n = self.tableWidget.rowCount() + 1
            for i in new_ribs:
                s, e, v = i
                # Добавляем в таблицу в БД новые данные
                cur.execute(f'INSERT INTO {self.name} '
                            f'VALUES ({n}, "{s}", "{e}", {v})')
                # Увеличим id на единицу
                n += 1
            # Подтвердим изменения в БД
            self.con.commit()
            # Обновим таблицу
            self.load_table(self.con)

    def add_from_csv(self):
        """Фукнция добавления ребер в граф из csv-таблицы. Для добавления
        необходимо указать файл с таблицей и разделитель в новом окне."""
        # Получим имя файла для открытия и кнопку, на которую нажал
        # пользователь
        ch = GetCsv()
        res = ch.exec_()
        if res:
            new_ribs = ch.data
            n = self.tableWidget.rowCount() + 1
            cur = self.con.cursor()
            for i in new_ribs:
                s, e, v = i
                cur.execute(f'INSERT INTO {self.name} VALUES '
                            f'({n}, "{s}", "{e}", {v})')
                n += 1
            self.con.commit()
            self.load_table(self.con)

    def delete(self):
        """Функция для удаления выделенной строки в таблице ребер графа.
        Вызывается нажатием соответствующей кнопки."""
        # Получаем индексы строк, которые необходимо удалить
        ids = [self.tableWidget.item(i, 0).text() for i in list(set(
            [i.row() for i in self.tableWidget.selectedItems()]))]
        # Запрашиваем подтверждение у пользователя на удаление
        do_or_not = QMessageBox.question(
            self, 'Удалить элементы', "Удалить выбранные элементы?",
            QMessageBox.Yes, QMessageBox.No)
        if do_or_not == QMessageBox.Yes:  # Выполняется, если пользователь
            # нажал на ОК
            cur = self.con.cursor()
            cur.execute(f"DELETE FROM {self.name} WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids)  # Удаление выделенных строк из БД
            self.con.commit()  # Подтверждение изменений
        self.save()
        self.load_table(self.con)  # Обновляем таблицу

    def load_table(self, con):
        """Функция для загрузки списка ребер графа в таблицу"""
        self.con = con  # Подключение к БД
        cur = self.con.cursor()
        self.tableWidget.setRowCount(0)  # Мы не знаем, сколько всего ребер
        # в графе, поэтому изначальное количество строк в таблице равно 0
        res = cur.execute(
            f'SELECT * FROM {self.name}').fetchall()  # Получение всех ребер
        # графа
        res = [i for i in res if not i[0] is None]  # Оставляем только
        # непустые ребра
        if not all(isinstance(i[3], float) or isinstance(i[3], int)
                   for i in res):
            QMessageBox.warning(self, 'Неправильынй вес ребра',
                                'Внимание! Вы указали нечисловое значение веса'
                                ' ребра. Все неправильные веса будут заменены '
                                'на 1.')
            weights = [i[3] if isinstance(i[3], float) or isinstance(
                i[3], int) else 1 for i in res]
            res = [list(res[i][:3]) + [weights[i]] for i in range(len(res))]
        for i in range(len(res)):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j in range(4):
                # Заносим информацию о ребре (id, начало, конец, вес) в таблицу
                self.tableWidget.setItem(i, j, QTableWidgetItem(
                    str(res[i][j])))
                if not j:
                    # Запрет на изменение колонки с id
                    self.tableWidget.item(i, j).setFlags(Qt.ItemFlag(False))

    def create_table(self):
        """Функция, создающая и возвращающая таблицу смежности графа. Может
        использоваться для алгоритмов обхода/поиска оптимального пути."""

        num_of_vertexes = self.get_num_of_vertex()  # Получаем количество
        # вершин в графе
        matrix = [[0 if i == j else inf for j in range(num_of_vertexes)]
                  for i in range(num_of_vertexes)]  # Создаем матрциу смежности
        # графа, изначально пустую
        for i in range(self.tableWidget.rowCount()):
            #  Получение информации о ребре из таблицы, занесение
            #  информации в матрицу смежности
            start = self.tableWidget.item(i, 1).text()
            end = self.tableWidget.item(i, 2).text()
            start, end = self.nodes.index(start), self.nodes.index(end)
            value = float(self.tableWidget.item(i, 3).text())
            if int(value) == value:
                matrix[start][end] = int(value)
            else:
                matrix[start][end] = value
        return matrix

    def create_list(self):
        """Функция, создающая и вовращающая список смежности графа. Может
        использоваться для алгоритмов обхода/поиска оптимального пути."""

        my_dict = {}
        for i in range(self.tableWidget.rowCount()):
            #  Получение информации о ребре из таблицы, занесение
            #  информации в список смежности
            start = self.tableWidget.item(i, 1).text()
            end = self.tableWidget.item(i, 2).text()
            my_dict[start] = my_dict.get(start, []) + [end]
        return my_dict

    def create_ribs(self):
        """Функция, создающая и возвращающая список ребер графа. Может
        использоваться для алгоритмов обхода/поиска оптимального пути."""

        my_dict = {}
        for i in range(self.tableWidget.rowCount()):
            #  Получение информации о ребре из таблицы, занесение
            #  информации в список ребер
            start = self.tableWidget.item(i, 1).text()
            end = self.tableWidget.item(i, 2).text()
            value = float(self.tableWidget.item(i, 3).text())
            if value == int(value):
                my_dict[start, end] = int(value)
            else:
                my_dict[start, end] = value
        return my_dict

    def create_graph(self):
        """Функция, создающая граф на основе списка ребер"""
        # Получаем списки ребер графа
        ribs = self.create_ribs()
        if ribs:
            plt.clf()
            self.graph = nx.DiGraph()  # Создаем ориентированный граф
            self.graph.add_edges_from(ribs)  # Добавляем в граф ребра
            self.nodes = list(self.graph.nodes)  # Определим вершны графа

            # Раскрасим вершины графа в зависимости от количества связей с
            # другими вершинами
            adj_list = self.create_list()  # Получим список смежности графа
            max_connections = {i: 0 for i in self.nodes}  # Словарь для
            # подсчета количества связей
            # Количество связей вершины составим из количества вершин, в
            # которые можно попасть из данной, и количества вершина, из
            # которых можно попасть в данную
            for i in self.nodes:
                # Найдем количества вершина, в которые можно попасть из
                # данной
                if i in adj_list:
                    max_connections[i] = len(adj_list[i])
                else:
                    max_connections[i] = 0
                for j in adj_list:
                    # Проверим, можно ли в данную вершину попасть из
                    # других, причем мы не будем учитывать пути из данной
                    # вершины рассматриваемую и из рассматриваемой в
                    # данную (т.е. случай, когда между двумя вершинами
                    # есть путь и туда, и обратно)
                    if i in adj_list[j] and j not in adj_list.get(i, []):
                        max_connections[i] = max_connections.get(i, 0) + 1
            # Создадим градиент цветов от зеленого до красного с
            # количеством цветов, равному максимальному количеству связей
            # у вершины
            colors = list(Color('green').range_to(Color('red'), max(
                max_connections.values())))
            # Дял каждой вершинны определим ее цвет в зависимости от
            # количества связей
            node_color = [colors[max_connections[i] - 1].get_hex()
                          for i in self.nodes]

            pos = nx.spring_layout(self.graph)  # Создаем слой, на котором
            # будут располагаться ребра и их веса
            self.fig = plt.figure(2, figsize=(
                HEIGHT_MAIN_WINDOW * 2 // 100,
                HEIGHT_MAIN_WINDOW * 2 // 100))
            # Рисование весов ребер
            nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=ribs,
                                         font_size=7)
            # Рисование ребер и вершин
            nx.draw(self.graph, pos, nodelist=self.nodes, node_size=175,
                    node_color=node_color, with_labels=True)
            self.find_properties()

    def get_num_of_vertex(self):
        """Функция, возвращающая количество вершин в графе"""
        v1 = {self.tableWidget.item(i, 1).text() for i in range(
            self.get_num_of_ribs())}
        v2 = {self.tableWidget.item(i, 2).text() for i in range(
            self.get_num_of_ribs())}
        return len(v1 | v2)

    def get_num_of_ribs(self):
        """Фукнция, возвращающая количество ребер графа"""
        return self.tableWidget.rowCount()

    def find_comps(self):
        """Функция для нахождения компонент сильной связности в графе,
        основанная на алгоритме Косарайю. Одновременно выполняется проверка
        на наличие циклов."""
        n = self.nodes
        # Создадим два списка смежности графа, причем второй является списком
        # смежности инвертированного графа, то есть того, в котором
        # направления ребер изменены на противоположные
        g = self.create_list()
        g = {n.index(i): [n.index(j) for j in g[i]] for i in g}
        invert_g = {}
        for i in g:
            for j in g[i]:
                invert_g[j] = invert_g.get(j, []) + [i]
        # Создадим список посещенных вершин и список, хранящий информацию о
        # времени выхода из вершины
        order = []
        visited = [False] * (len(n) + 1)
        # Отсортируем вершины по времени выхода из них
        for i in range(self.get_num_of_vertex()):
            if not visited[i]:
                dfs_time_out(i, g, visited, order)
        order.reverse()
        visited = [False] * (len(n) + 1)
        comps = []
        # Найдем компоненты сильной связности
        for i in order:
            if not visited[i]:
                comp = []
                dfs_create_comp(i, invert_g, visited, comp)
                if [n[i] for i in comp] not in comps:
                    comps.append([n[i] for i in comp])
        self.comps = comps

    def calc_min_cost_ways(self):
        """Фукнция для определения минимальной стоимости пути в графе
        (между любыми двумя вершинами), сами эти вершины и путь. Также функция
        выполняет проверку наличия циклов отрицательной длины в графе. При
        наличии цикла отрицателньой длины считается, что минимальный путь в
        графе отсутствует."""
        n = {i: self.nodes.index(i) for i in self.nodes}
        inverted_n = {self.nodes.index(i): i for i in self.nodes}
        num = self.get_num_of_vertex()
        g = self.create_ribs()
        g = {(n[i[0]], n[i[1]]): g[i] for i in g}
        ways = {}
        paths = {}
        for i in range(num):
            way, p, c = ford_algorithm(num, i, g)
            if not c:
                ways[inverted_n[i]] = {inverted_n[x]: way[x] for x in range(
                    len(n))}
                path = []
                for t in range(num):
                    if way[t] != inf and t != i:
                        cur = t
                        while cur != -1:
                            path.append(cur)
                            cur = p[cur]
                        paths[inverted_n[i], inverted_n[t]] = [
                            inverted_n[x] for x in path[::-1][
                                                   :path[::-1].index(t) + 1]]
        for i in ways:
            for j in ways[i]:
                if ways[i][j] != 0 and ways[i][j] != inf:
                    self.ways[i, j] = [ways[i][j], paths[i, j]]

    def find_properties(self):
        """Функция для определения всех добавленных свойств графов"""
        d = {i: self.nodes.index(i) + 1 for i in self.nodes}
        invert_d = {self.nodes.index(i) + 1: i for i in self.nodes}
        ribs_list = self.create_list()
        # Переделаем граф в неориентированный с и числами вместо названий
        # вершин
        g = {d[i]: [d[j] for j in ribs_list[i]] for i in ribs_list}
        for i in ribs_list:
            for j in ribs_list[i]:
                g[d[j]] = g.get(d[j], []) + [d[i]]

        enum_graph_ribs = [(d[i[0]], d[i[1]]) for i in self.create_ribs()]
        enum_graph_ribs = enum_graph_ribs + [(d[i[1]], d[i[0]]) for i in
                                             self.create_ribs()]

        self.find_comps()  # Найдем комопненты связности
        self.cycles = list(nx.simple_cycles(self.graph))  # Найдем циклы
        self.calc_min_cost_ways()  # Найдем минимальные пути
        # Найдем мосты
        # Проведем операцию несколько раз от существующих и несуществующих
        # ребер, чтобы найти все мосты
        n = self.get_num_of_vertex()
        res = []
        for x in range(len(enum_graph_ribs) + 2):
            timer = 0
            tin = [0] * (n + 1)
            tup = [0] * (n + 1)
            visited = [False] * (n + 1)
            if x == 0:
                res2 = dfs_bridges(1, 0, g, tin, tup, visited, [], timer)
            elif x == len(enum_graph_ribs) + 1:
                res2 = dfs_bridges(enum_graph_ribs[-1][1],
                                   enum_graph_ribs[-1][1] + 1, g, tin, tup,
                                   visited, [], timer)
            else:
                i, j = enum_graph_ribs[x - 1]
                res2 = dfs_bridges(j, i, g, tin, tup, visited, [], timer)
            for j in res2:
                if j not in res and (j[1], j[0]) not in res:
                    res.append(j)
        self.bridges = [[invert_d[i[0]], invert_d[i[1]]] for i in res]
        # Найдем точки сочленения
        graph_for_art_p = nx.Graph()
        graph_for_art_p.add_edges_from(enum_graph_ribs)
        self.art_p = [invert_d[i] for i in list(nx.articulation_points(
            graph_for_art_p))]
        self.insert_or_update_data()

    def contextMenuEvent(self, event):
        """Функция создания контекстного меню, появляющего после нажатия
        правой кнопки мыны в поле кнопки "Добавить"."""
        # Проверим, находится ли курсор пользователя в области кнопки Добавить
        if self.btn_add.x() <= event.x() <= self.btn_add.x(
        ) + self.btn_add.width():
            if self.btn_add.y() <= event.y() <= self.btn_add.y(
            ) + self.btn_add.height():
                menu = QMenu(self)
                menu.addAction('Добавить ребро', self.add)
                menu.addAction('Добавить несколько ребер', self.add_a_lot)
                menu.addAction('Добавить из csv-таблицы', self.add_from_csv)
                # Сделаем так, чтобы меню появлялось возле курсора пользователя
                menu.exec_(event.globalPos())

    def insert_or_update_data(self):
        """Функция для добавления данных о графе в таблицу в базе данных или
        их обновления"""
        cur = self.con.cursor()
        # Получим свойства графа
        num_vertex = self.get_num_of_vertex()
        vertex = self.nodes
        num_ribs = self.get_num_of_ribs()
        bridges = self.bridges
        num_of_bridges = len(bridges)
        art_p = self.art_p
        num_of_art_p = len(art_p)
        cycles = self.cycles
        num_of_cycles = len(cycles)
        comps = self.comps
        num_of_comps = len(comps)
        min_ways = self.ways

        cur.execute(f'''UPDATE some_info SET NumOfVert = ?, NumOfRibs = ?, 
        NumOfBridges = ?, NumOfArtP = ?, NumOfCycles = ?, NumOfStrongComps = ?
        WHERE GraphName = "{self.name}"''', (
            num_vertex, num_ribs, num_of_bridges, num_of_art_p,
            num_of_cycles, num_of_comps,))

        cur.execute(f'''UPDATE some_info SET Vertex = ?, Bridges = ?,
               ArtP = ?, Cycles = ?, StrongComps = ?, MinWays = ?
               WHERE GraphName = "{self.name}"''', (
            ', '.join(vertex), ', '.join(
                ['-'.join(map(str, i)) for i in bridges]), ', '.join(art_p),
            ', '.join(['-'.join(map(str, i)) for i in cycles]),
            ', '.join(['-'.join(map(str, i)) for i in comps]), ', '.join(
                [f'{i[0]}-{i[1]}: ({min_ways[i][0]}; ' + '-'.join(
                    min_ways[i][1]) + ')' for i in min_ways]),))
        self.con.commit()


class GraphViz(QMainWindow):
    """Визуализатор графов и среда для работы с ними"""
    def __init__(self):
        """Функция - инициализатор класса GraphViz"""
        super().__init__()
        # Настроим приложение (размер, иконка, заголовок)
        uic.loadUi('UI/graph_viz.ui', self)
        self.setGeometry(WIDTH // 2 - HEIGHT_MAIN_WINDOW,
                         HEIGHT // 2 - HEIGHT_MAIN_WINDOW,
                         HEIGHT_MAIN_WINDOW * 2, HEIGHT_MAIN_WINDOW * 2)
        self.setMinimumSize(HEIGHT_MAIN_WINDOW * 2, HEIGHT_MAIN_WINDOW * 2)
        self.setWindowIcon(QIcon('imgs/icon.png'))
        self.statusbar.messageChanged.connect(self.message_changed)
        # Создадим список доступных графов (изначально пустой) и подключенный
        # граф (изначально отсутствует - None)
        self.table_names = []
        self.cur_graph = None
        # Создадим виджет со свойствами графа, изначально None
        self.prop = None
        # Создадим кнопки для рисования графа и определения его параметров
        self.btn_close.setEnabled(False)
        self.btn_close.clicked.connect(self.hide_image)
        self.btn_close.setShortcut(QKeySequence('H'))

        self.btn_draw.clicked.connect(self.draw_graph)
        self.btn_draw.setEnabled(False)
        self.btn_draw.setShortcut(QKeySequence('R'))

        self.btn_find.clicked.connect(self.find_data)
        self.btn_find.setShortcut(QKeySequence('O'))
        self.btn_find.setEnabled(False)

        self.btn_save.clicked.connect(self.save_image)
        self.btn_save.setEnabled(False)

        # Создадим меню, изначально None, потом в функции определим, и
        # некоторые пункты меню
        self.help_content_action = QAction('Посмотреть справку', self)
        self.help_content_action.triggered.connect(self.give_help)

        self.about_action = QAction('О программе', self)
        self.about_action.triggered.connect(self.about_programme)

        self.manual_action = QAction('Руководство', self)
        self.manual_action.triggered.connect(self.give_manual)
        self.file_menu = None
        self.help_menu = None
        # Создадим меню
        self.create_menu_bar()
        # Создаем изображение, изначально - None
        self.image = None
        # Создаем метку, в которой будет храниться изображение графа
        self.im_lab.move(0, 40)
        self.im_lab.resize(self.width(), self.height() - 18)
        # Подлючаемся к БД, изначально подключение отсутствует
        self.con = None
        # Будем запоминать высоту окна, когда пользователь нажимает на H
        self.prev_height = None

    def resizeEvent(self, event):
        """Функция, сдвигающая status bar и метку в зависимости от
        размера окна"""
        self.statusbar.move(0, self.height() - 18)
        self.statusbar.resize(self.width(), 18)
        self.im_lab.move(self.width() // 2 - self.im_lab.width() // 2,
                         self.height() // 2 - self.im_lab.height() // 2 + 18)

    def create_menu_bar(self, flag=False):
        """Функция создания меню в окне приложения"""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        self.file_menu = QMenu("Файл", self)
        menu_bar.addMenu(self.file_menu)
        self.file_menu.addAction('Создать', self.make_db,
                                 shortcut=QKeySequence('Ctrl+N'))
        self.file_menu.addAction('Открыть', self.open_db,
                                 shortcut=QKeySequence('Ctrl+O'))
        if flag:  # Следующие пункты в меню создаются тольок после открытия БД
            self.file_menu.addSeparator()
            self.file_menu.addAction('Открыть граф', self.open_graph,
                                     shortcut=QKeySequence('Ctrl+Shift+O'))
            self.file_menu.addAction('Добавить граф', self.add_graph,
                                     shortcut=QKeySequence('Ctrl+Shift+A'))
            self.file_menu.addAction('Удалить граф', self.del_graph,
                                     shortcut=QKeySequence('Ctrl+Shift+Del'))
            self.file_menu.addSeparator()
        self.file_menu.addAction('Сохранить', self.save_db,
                                 shortcut=QKeySequence('Ctrl+S'))
        menu_for_save = QMenu('Сохранить как', self)
        menu_for_save.addAction('csv-таблицу', self.save_to_csv,
                                shortcut=QKeySequence('Ctrl+Shift+S'))
        menu_for_save.addAction('текстовый файл', self.save_to_txt,
                                shortcut=QKeySequence('Ctrl+Alt+S'))
        self.file_menu.addMenu(menu_for_save)
        self.file_menu.addSeparator()
        self.file_menu.addAction('Выход', self.exit,
                                 shortcut=QKeySequence('Alt+F4'))

        self.help_menu = QMenu('Справка', self)
        menu_bar.addMenu(self.help_menu)
        self.help_menu.addAction(self.help_content_action)
        self.help_menu.addAction(self.manual_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.about_action)

    def add_required_table(self):
        """Функция, создающая таблицу в базе данных, которая хранит
        определенную информацию о каждом графе (наличие циклов, количество
        компонент связности и т.д.)"""
        # Создадим таблицу с id графов и их именами
        self.con.cursor().execute('''CREATE TABLE IF NOT EXISTS graphs_ids (
            id   INTEGER UNIQUE
                         PRIMARY KEY AUTOINCREMENT,
            name STRING);''')
        # Создадим таблицу со свойствми графов
        self.con.cursor().execute('''CREATE TABLE IF NOT EXISTS some_info (
    GraphID          INTEGER UNIQUE
                             REFERENCES graphs_ids (id) ON DELETE CASCADE
                                                        ON UPDATE CASCADE
                             PRIMARY KEY AUTOINCREMENT,
    GraphName        STRING,
    NumOfVert        INTEGER,
    Vertex           TEXT,
    NumOfRibs        INTEGER,
    NumOfBridges     INTEGER,
    Bridges          TEXT,
    NumOfArtP        INTEGER,
    ArtP             TEXT,
    NumOfCycles      INTEGER,
    Cycles           TEXT,
    NumOfStrongComps INTEGER,
    StrongComps      TEXT,
    MinWays          TEXT);''')  # Создание таблицы some_info в БД, если
        # она на существует
        self.con.commit()

    def connect_to_database(self, name):
        """Функция подключения к базе данных с графами.
        При инициализации принимает название базы данных.
        Если база данных не выбрана или выбран некорректный файл, выводится
        соответствующее сообщение"""

        try:
            if not name.endswith('.sqlite'):  # За БД примем только тот файл,
                # который имеет расширение sqlite
                raise AttributeError
            self.con = sqlite3.connect(name)
            self.con.execute("PRAGMA foreign_keys = ON")  # Подключение к БД
            self.table_names = [i[0] for i in self.con.cursor().execute(
                "SELECT name FROM sqlite_master WHERE "
                "type='table';").fetchall()[1:]]  # Получение имен всех
            # таблиц в БД
            self.table_names = sorted(set(self.table_names) -
                                      {'some_info', 'sqlite_sequence',
                                       'graphs_ids'})
            # Если таблица с информацией о каждом графе или таблица с графами
            # и их id отсутствует в БД, она создается
            self.add_required_table()
            self.file_menu.clear()  # Очистка меню с целью его повторного
            # заполнения, но уже с дополнительными возможностями
            self.create_menu_bar(flag=True)
        except AttributeError:  # Если файл не выбран или не является БД
            self.statusbar.showMessage('Файл не выбран или файл не является '
                                       'базой данных', 4000)

    def about_programme(self):
        """Функция, вызывающая окно с информацией о программе. Выполянется при
        нажатии соответствующей кнопки в меню"""
        # Вывод сведений о приложении на экран
        QMessageBox.about(self, 'Визуализатор графов: сведения',
                          'AMOGUS Corp.\nВерсия 1.0\n©Корпорация AMOGUS, '
                          '2021. Все права защищены.\n')

    def give_help(self):
        """Фуцнкция-вызов окна с информацией о предназначении программы.
        Выполянется при нажатии соответствующей кнопки в меню"""
        # Вывод справки о приложении на экран
        QMessageBox.information(self, 'Визаулизатор графов: справка',
                                'Вас приветстсвует утилита "Визуализатор '
                                'графов". С ее поомщью вы можете создавать, '
                                'изменять, удалять, рисовать графы, а также '
                                'находить некоторые параметры графа ('
                                'количество компонент связности, наличие '
                                'циклов и т.п.).')

    def give_manual(self):
        """Функция открывает в браузере сайт с руководством пользования"""
        webbrowser.open(getcwd() + '\\docs\\manual.html')

    def exit(self):
        """Функция для выхода из приложения при нажатии соответствующего
        сочетания клавиш или нажатия соответствующей кнопки в меню"""
        QApplication.quit()  # Закрытие приложения

    def save_db(self):
        """Фунция для сохранения данных в базе данных при нажатии
        соотсетствующего сочетния клавиш или соответствующей кнопки в меню.
        Если базы данных нет, выводится соответствующее сообщение"""

        try:
            self.con.commit()  # Подтверждаем изменения в БД
        except AttributeError:
            # Если БД не обнаружена, сохранения не происходит
            self.statusbar.showMessage('База данных не обнаружена', 4000)

    def open_db(self):
        """Функция выбора базы данных для открытия. Выполянется при нажатии
        соответствующего сочетения клавиш или кнопки в меню"""
        # Получим имя БД для открытия и результат нажатия пользователя на
        # кнопку ОК
        name, ok = QFileDialog.getOpenFileName(
            self, 'Выбрать базу данных', '', '')
        if ok:
            self.cur_graph = None
            if self.image is not None:
                self.im_lab.setPixmap(QPixmap(''))
            self.btn_draw.setEnabled(False)
            self.btn_find.setEnabled(False)
            self.btn_save.setEnabled(False)
            self.btn_close.setEnabled(False)
            # После получения имени БД для открытия, происходит
            # Подключение к этой БД
            self.connect_to_database(name)

    def make_db(self):
        """Функция для создания базы данных, хранящей информацию о графе.
        Выполянется при нажатии соответствующего сочетания клавиш или
        кнопки в меню"""
        # Получаем абсолютный путь сохранения новой базы данных
        name = QFileDialog.getSaveFileName(
            self, 'Создать базу данных', f'{getcwd()}\\db\\database1.sqlite',
            'База данных (*.sqlite)')[0]
        if name:  # Если пользователь нажал на кнопку сохранения,
            # идет дальнейшее создание
            if self.image is None:
                self.cur_graph = None
                self.btn_draw.setEnabled(False)
                self.btn_find.setEnabled(False)
                self.btn_save.setEnabled(False)
                self.btn_close.setEnabled(False)
            self.connect_to_database(name)

    def open_graph(self):
        """Функция для открытия данных графа (списка ребер). Выполняется при
        нажатии соответствующего сочетния клавиш или кнопки в меню"""
        if self.table_names:
            # Получение имени графа для открытия
            ch = GetGraphName(sorted(set(self.table_names) - {'some_info',
                                                              'graphs_ids'}))
            res = ch.exec_()
            if res:  # Если пользователь нажал на кнопку ОК,
                # идет дальнейшее открытие
                ch = ch.list.currentItem().text()
                if ch is not None:
                    self.cur_graph = Graph(ch, self.con)
                    self.cur_graph.load_table(self.con)
                    self.cur_graph.show()
                    # Сделаем активными кнопки для рисования
                    self.btn_draw.setEnabled(True)
                    self.btn_find.setEnabled(False)
                    self.im_lab.resize(0, 0)
                    if self.prop is not None:
                        self.prop.close()
                    self.cur_graph.create_graph()
        else:
            # Если в БД отсутствуют графы, вместо открытия
            # какого-либо графа он создается
            QMessageBox.warning(self, 'Ошибка',
                                      'В базе данных отсутствуют графы. ' 
                                      'Сейчас будет создан новый граф.')
            self.add_graph()

    def add_graph(self):
        """Функция для создания графа в базе данных. Выполняется при нажатии
        соответсвующего сочетания клавиш или нажатии соответствующей кнопки"""
        # Получаем имя графа и резульатт нажатия на кнопку ОК
        name, ok = QInputDialog.getText(self, 'Введите название',
                                        'Как назвать граф?')
        if ok:  # Если пользоаватель нажал на ОК, идет создание графа
            if name:
                try:
                    self.con.cursor().execute(f'''CREATE TABLE IF NOT 
        EXISTS {name} (id             INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE 
        NOT NULL, [Начало ребра] STRING, [Конец ребра]  STRING,
        [Вес ребра]    INTEGER);''')  # Создание таблицы графа в БД
                    self.table_names.append(name)
                    self.con.cursor().execute(f'INSERT INTO graphs_ids (name) '
                                              f'VALUES ("{name}")')
                    self.con.commit()
                    res = self.con.cursor().execute('''SELECT name FROM 
                    graphs_ids WHERE id = (SELECT MAX(id) FROM 
                    graphs_ids)''').fetchone()
                    self.con.cursor().execute(
                        f'''INSERT INTO some_info (GraphName) VALUES 
                        ("{res[0]}")''')
                    self.con.commit()  # Подтверждение изменений  в БД
                except sqlite3.OperationalError:
                    self.statusbar.showMessage('Недопустимое имя графа.', 4000)
            else:
                self.statusbar.showMessage('Имя графа не может быть пустой '
                                           'строкой.', 4000)

    def del_graph(self):
        """Фукнция для удаления графа из БД. Выполняется при
        нажатии соответствующего пункта в меню или соответствующего
        сочетания клавиш."""
        if self.table_names:
            # Получение имени графа для удаления
            ch = GetGraphName(sorted(set(self.table_names) - {'some_info',
                                                              'graphs_ids'}),
                              flag=True)
            res = ch.exec_()
            if res:  # Если пользователь нажал на кнопку ОК,
                # идет дальнейшее удаление
                ch = ch.gr
                if ch is not None:
                    cur = self.con.cursor()
                    cur.execute(f'DROP TABLE IF EXISTS {ch}')
                    cur.execute(f'DELETE FROM graphs_ids WHERE name = "{ch}"')
                    self.con.commit()
                    if self.cur_graph is not None:
                        self.cur_graph.close()
                    self.table_names = [i for i in self.table_names if i != ch]
                if ch == self.cur_graph.name:
                    self.cur_graph = None
                    self.btn_draw.setEnabled(False)
                    self.btn_find.setEnabled(False)
                    self.btn_save.setEnabled(False)
                    self.im_lab.resize(0, 0)
        else:
            # Если в БД отсутствуют графы, выводистя соответствующее сообщение
            QMessageBox.warning(self, 'Ошибка',
                                'В базе данных отсутствуют графы.')

    def closeEvent(self, event):
        """Функция, автоматически закрывающая соединение с базой данных,
        если пользователь закрыл приложение"""
        try:
            self.cur_graph.close()
            self.prop.close()
            self.con.close()  # Закрытие соединения
        except AttributeError:
            pass  # Соединение с БД закрывается, только если
            # оно было до этого установлено

    def plt_figure_to_pil_image(self, fig):
        """Функция принимает фигуру в pyplot и конвертирует
        ее в объект Image"""
        buf = io.BytesIO()  # Создание потока байтов
        fig.savefig(buf)  # Сохранение фигуры как потока байтов
        self.image = Image.open(buf)  # Создание изображение PIL

    def draw_graph(self):
        """Функиця для рисования графа в окне приложения"""
        self.cur_graph.create_graph()
        if self.cur_graph.graph is not None and self.cur_graph.create_ribs():
            self.plt_figure_to_pil_image(plt)
            self.btn_find.setEnabled(True)  # СОздаем возможность определить
            # свойства графа
            self.btn_save.setEnabled(True)  # Создаем возможность сохранить
            # изображение
            self.btn_close.setEnabled(True)  # Создаем возможность спрятать
            # изобржение
            p = ImageQt(self.image)
            # Устанавливаем в метку изображение
            self.im_lab.setPixmap(QPixmap.fromImage(p))
            self.im_lab.resize(self.width(), self.height() - 68)
            self.resizeEvent(None)
        else:
            self.statusbar.showMessage('Граф пустой', 4000)

    def hide_image(self):
        """Функция, скрывающая или показывающая изображение графа. Вызывается
        нажатием соответствующей кнопки"""
        if self.btn_close.text() == '-':
            # Спрятать изображение
            self.prev_height = self.height()
            self.setMinimumSize(HEIGHT_MAIN_WINDOW * 2, 80)
            self.resize(self.width(), 80)
            self.im_lab.hide()
            self.btn_close.setText('+')
        else:
            # Показать изображение
            self.setMinimumSize(HEIGHT_MAIN_WINDOW * 2, HEIGHT_MAIN_WINDOW * 2)
            self.resize(self.width(), self.prev_height)
            self.im_lab.show()
            self.btn_close.setText('-')
        self.btn_close.setShortcut(QKeySequence('H'))

    def save_image(self):
        """Фукнция для сохранения изображения графа в память компьютера.
        Если имя или расширение файла указано неверно, выводится
        соответствующее сообщение"""
        try:
            # Получим от пользователя иям файла и директорию сохранения
            name, ok = QFileDialog.getSaveFileName(
                self, 'Сохранить изображение', f'{getcwd()}\\untitled.png',
                'Изображение PNG (*.png);;Изображение JPG (*.jpg);;'
                'Изображение BMP (*.bmp);;Все файлы (*)', )
            # Сохраняем изображение графа
            if ok:
                if name.endswith('.jpg'):  # Если выбрано изображение jpg,
                    # нужно перевести изображение в RGB модель, так как у
                    # jpg-изображений нет альфа-канала
                    rgb_im = self.image.convert('RGB')
                    rgb_im.save(name)
                else:
                    self.image.save(name)
                self.statusbar.showMessage('Успешно', 4000)
        except ValueError:
            self.statusbar.showMessage('Имя файла указано неверно', 4000)

    def find_data(self):
        """Функия для определения параметров (свойств) графа и открытия окна
        с ними. """
        self.cur_graph.find_properties()
        g = self.cur_graph
        data_to_nums = [g.nodes, g.graph.edges, g.bridges, g.art_p, g.cycles,
                        g.comps]
        self.prop = GraphProperties(self.cur_graph.name)
        self.prop.show()
        self.prop.display_on_lcd([len(i) for i in data_to_nums])
        data_to_print = [g.create_ribs(), g.create_list(),
                         g.create_table()] + data_to_nums[-4:] + [g.ways]
        self.prop.set_data(data_to_print)

    def get_graphs_and_props(self, flag=True):
        """Функия для получения списка имен графов, свойства которых нужно
        сохранить, и сами сохраняемые свойства"""
        try:
            if self.con is None:
                raise AttributeError
            if not self.table_names:
                raise AttributeError
            ch = SaveAsForm(self.table_names, flag)
            res = ch.exec_()
            if res:
                return ch.chosen_graphs, ch.chosen_prop, ch.folder
        except AttributeError:
            self.statusbar.showMessage('База данных не обнаружена или в ней '
                                       'отсутствуют графы', 4000)

    def save_to_csv(self):
        """Функция, сохраняющая данные о графах в csv-таблицу. Выполняется
        при нажатии соответствующего сочетания клавиш или кнопки в меню"""
        res = self.get_graphs_and_props()
        if res is not None:
            graphs, props, folder = res
            headers = ['GraphName'] + [j for i in props for j in PROPS[i]]
            cur = self.con.cursor()
            data = cur.execute(
                f'''SELECT {", ".join(headers)} FROM some_info WHERE 
                    GraphName in 
                ({", ".join([f'"{i}"' for i in graphs])})''').fetchall()
            with open(folder, 'w', newline='', encoding='utf8') as csv_props:
                writer = DictWriter(
                    csv_props, fieldnames=headers,
                    delimiter=';', quoting=QUOTE_MINIMAL)
                writer.writeheader()
                for d in data:
                    row = {headers[i]: d[i] for i in range(len(headers))}
                    writer.writerow(row)

    def save_to_txt(self):
        """Функция, сохраняющая данные о графах txt-файл. Выполняется
        при нажатии соответствующего сочетания клавиш или кнопки в меню"""
        res = self.get_graphs_and_props(flag=False)
        if res is not None:
            graphs, props, folder = res
            headers = ['GraphName'] + [j for i in props for j in PROPS[i]]
            cur = self.con.cursor()
            data = cur.execute(
                f'''SELECT {", ".join(headers)} FROM some_info WHERE 
                            GraphName in (
                {", ".join([f'"{i}"' for i in graphs])})''').fetchall()
            with open(folder, 'w', encoding='utf8') as txt_file:
                for i in range(len(graphs)):
                    if i:
                        txt_file.write('\n')
                    txt_file.write(f'Граф: {data[i][0]}\n')
                    for j in range(len(props)):
                        txt_file.write(f'{props[j]}:\n')
                        if props[j] != 'Минимальные пути':
                            txt_file.write(f'Количество: '
                                           f'{data[i][1 + j * 2]}\n')
                            txt_file.write(data[i][2 + j * 2])
                        else:
                            txt_file.write('\n'.join(data[i][-1].split(', ')))
                        txt_file.write('\n\n')

    def message_changed(self):
        """Функция для изменения цвета status bar'а в случае ошибок"""
        if self.statusbar.currentMessage() == 'Успешно':
            self.statusbar.setStyleSheet('background: green;')
        elif self.statusbar.currentMessage():
            self.statusbar.setStyleSheet('background:red;')
        else:
            self.statusbar.setStyleSheet('')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    programme = GraphViz()
    programme.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
