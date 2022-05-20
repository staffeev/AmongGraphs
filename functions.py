from math import inf
from ctypes import windll


def screen_size():
    """Функция, возвращающая размер экрана пользователя.
    Необходима, чтобы окно приложения открывалось ровно посередине экрана
    :return Размер экрана пользователя"""
    size = windll.user32
    return size.GetSystemMetrics(0), size.GetSystemMetrics(1)


def ford_algorithm(n, start, g):
    """Функция, реализующая алгоритм Форда-Беллмана для поиска минимальных
    путей в графе от одной вершины до остальных. Принимает количество вершин,
    стартовую вершину и список ребер графа. Возвращает список расстояний до
    каждой из вершин и список предков, необходимый для востановления пути"""
    f = [inf] * n
    p = [-1] * n
    f[start] = 0
    stop = False
    k = 1
    while k < n and not stop:
        k += 1
        stop = True
        for j, i in g.keys():
            if f[j] + g[j, i] < f[i]:
                f[i] = f[j] + g[j, i]
                p[i] = j
                stop = False
    cycle = False
    for j, i in g.keys():
        if f[j] + g[j, i] < f[i]:
            cycle = True
    return f, p, cycle


def dfs_time_out(v, g, visited, order):
    """Функция обхода графа в глубину с сортировкой вершин по времени
    выхода из них (т.е. топологическая сортировка). Принимает вершину, которая
    рассматрвиается в данный момент, список ребер графа, список посещенных
    вершинн и список времени выхода из вершины."""
    visited[v] = True
    for to in g.get(v, []):
        if not visited[to]:
            dfs_time_out(to, g, visited, order)
    order.append(v)


def dfs_create_comp(v, g, visited, comp):
    """Фукнция обхода графа в глубину с построением компоненты сильной
    связности. Принимает вершину, которая
    рассматрвиается в данный момент, список ребер графа, список посещенных
    вершинн и список компоненты."""
    visited[v] = True
    comp.append(v)
    for to in g.get(v, []):
        if not visited[to]:
            dfs_create_comp(to, g, visited, comp)


def dfs_bridges(v, p, g, tin, tup, visited, bridges, timer=0):
    """Функция обхода графа в глубину с выделением мостов."""
    visited[v] = True
    tin[v] = timer
    timer += 1
    tup[v] = tin[v]
    for to in g.get(v, []):
        if to == p:
            continue
        if visited[to]:
            tup[v] = min(tup[v], tin[to])
        else:
            dfs_bridges(to, v, g, tin, tup, visited, bridges, timer)
            tup[v] = min(tup[v], tup[to])
            if tup[to] > tin[v]:
                bridges.append((v, to))
    return bridges
