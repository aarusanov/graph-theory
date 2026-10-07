from collections import deque
from dataclasses import dataclass

import numpy as np

INF = float("inf")


@dataclass(frozen=True)
class Segment:
    """Сегмент - связная компонента неуложенных рёбер."""

    edges: frozenset[frozenset[int]]
    vertices: frozenset[int]
    embedded: frozenset[int]


def _augmenting_path(
    cost: list[list[float]],
    u: tuple[float, ...],
    v: tuple[float, ...],
    row_of: tuple[int | None, ...],
    i: int,
) -> tuple[int | None, float, tuple[int, ...], tuple[float, ...], tuple[int, ...]]:
    """Ищет кратчайший увеличивающий путь из свободной строки i
    (Дейкстра по столбцам в приведённых стоимостях cost - u - v).

    :return: (sink, min_val, parent, slack, tree_cols); sink - свободный столбец,
        конец пути (None - пути нет), min_val - длина пути, parent[j] - строка-
        предшественник, slack[j] - длина пути до столбца j, tree_cols - столбцы дерева
    """
    m = len(v)
    slack = (INF,) * m
    parent = (-1,) * m
    live = tuple(range(m))
    tree_cols = ()
    min_val = 0.0

    while True:
        row, ui = cost[i], u[i]

        dist = {j: min_val + row[j] - ui - v[j] for j in live}
        shorter = {j for j in live if dist[j] < slack[j]}
        slack = tuple(dist[j] if j in shorter else s for j, s in enumerate(slack))
        parent = tuple(i if j in shorter else p for j, p in enumerate(parent))

        min_val, _, j = min((slack[c], row_of[c] is not None, c) for c in live)
        if min_val == INF:
            return None, min_val, parent, slack, tree_cols

        tree_cols += (j,)
        if row_of[j] is None:
            return j, min_val, parent, slack, tree_cols

        live = tuple(c for c in live if c != j)
        i = row_of[j]


def linear_sum_assignment(w: list[list[float]], maximize: bool = False) -> tuple[float, list[int]]:
    """Венгерский алгоритм: полное паросочетание минимального (или максимального)
    веса в двудольном графе. Сложность O(n^2 * m).

    :param w: матрица весов, w[i][j] - вес ребра из i-й вершины левой доли в j-ю правой;
        строк не больше, чем столбцов; отсутствующее ребро - INF
    :param maximize: True - искать максимум веса
    :return: (оптимальный вес, matching); matching[i] - вершина правой доли, сопоставленная i-й левой
    """
    n, m = len(w), len(w[0])
    if n > m:
        raise ValueError("полного паросочетания нет: вершин в левой доле больше, чем в правой")

    sgn = -1 if maximize else 1
    cost = [[INF if x == INF else sgn * x for x in row] for row in w]

    u = (.0,) * n              # потенциалы строк
    v = (.0,) * m              # потенциалы столбцов
    row_of = (None,) * m   # row_of[j] - строка, сопоставленная столбцу j
    col_of = (None,) * n   # col_of[i] - столбец, сопоставленный строке i

    for i in range(n):
        sink, min_val, parent, slack, tree_cols = _augmenting_path(cost, u, v, row_of, i)
        if sink is None:
            raise ValueError("полного паросочетания конечного веса нет")

        tree = set(tree_cols)
        shift = {i: min_val} | {row_of[j]: min_val - slack[j] for j in tree if row_of[j] is not None}
        u = tuple(x + shift.get(k, 0.0) for k, x in enumerate(u))
        v = tuple(x + slack[k] - min_val if k in tree else x for k, x in enumerate(v))

        j = sink
        while True:
            row = parent[j]
            old = col_of[row]
            row_of, col_of = (
                row_of[:j] + (row,) + row_of[j + 1:],
                col_of[:row] + (j,) + col_of[row + 1:],
            )
            j = old
            if row == i:
                break

    weight = sum(w[r][col_of[r]] for r in range(n))
    return weight, list(col_of)


def check_planarity(graph: list[list[int]]) -> bool:
    """Проверяет планарность связного графа гамма-алгоритмом.

    :param graph: список смежности неориентированного связного графа
    :return: True - граф планарен; False - не планарен
    """

    cycle = find_cycle(graph)
    if cycle is None:
        return True

    _, laid = embed_cycle(cycle, len(graph))
    faces = [cycle[:-1], cycle[:-1][::-1]]

    while True:
        segments = [s for s in build_segments(graph, laid) if len(s.embedded) >= 2]
        if not segments:
            return True

        admissible = [
            [k for k, face in enumerate(faces) if segment.embedded <= set(face)]
            for segment in segments
        ]
        count, k = min((len(a), i) for i, a in enumerate(admissible))
        if count == 0:
            return False

        chain = find_chain(segments[k], graph)
        faces = embed_chain(faces, admissible[k][0], chain)
        laid |= { frozenset(edge) for edge in zip(chain, chain[1:]) }


def find_cycle(graph: list[list[int]]) -> list[int] | None:
    """Ищет цикл в неориентированном графе.

    :param graph: список смежности неориентированного графа
    :return: цикл списком вершин [w, ..., w] либо None, если граф - лес
    """

    vertices = frozenset(range(len(graph)))

    while pendant := frozenset(
        v for v in vertices if sum(u in vertices for u in graph[v]) < 2
    ):
        vertices -= pendant

    if not vertices:
        return None

    walk = [next(iter(vertices))]
    visited = { walk[0] }
    previous = None

    while True:
        vertex = walk[-1]
        previous, neighbor = vertex, next(
            (u for u in graph[vertex] if u in vertices and u != previous),
        )

        walk.append(neighbor)

        if neighbor in visited:
            return walk[walk.index(neighbor):]

        visited.add(neighbor)


def embed_cycle(cycle: list[int], n: int) -> tuple[list[list[int]], set[frozenset[int]]]:
    """Укладывает цикл на плоскость: система обходов + рёбра.

    :param cycle: цикл из find_cycle - [w, ..., w]
    :param n: число вершин графа
    :return: (rotation, edges); rotation[v] - соседи v по часовой стрелке,
        edges - рёбра укладки
    """

    rotation = [[] for _ in range(n)]
    edges = set()

    for u, v in zip(cycle, cycle[1:]):
        rotation[u].append(v)
        rotation[v].append(u)
        edges.add(frozenset((u, v)))

    return rotation, edges


def get_faces(rotation: list[list[int]]) -> list[list[int]]:
    """Возвращает все грани укладки.

    :param rotation: система обходов, rotation[v] - соседи v по часовой стрелке
    :return: список граней; грань - контур [w, ..., w]
    """

    arcs = set((u, v) for u, neighbors in enumerate(rotation) for v in neighbors)
    faces = []

    while arcs:
        u, v = min(arcs)
        walk = [u]
        previous, vertex = u, v

        while (previous, vertex) in arcs:
            arcs.remove((previous, vertex))
            walk.append(vertex)

            around = rotation[vertex]
            neighbor = around[(around.index(previous) + 1) % len(around)]
            previous, vertex = vertex, neighbor

        faces.append(walk)

    return faces


def build_segments(graph: list[list[int]], embedded_edges: set[frozenset[int]]) -> list[Segment]:
    """Разбивает неуложенные рёбра на сегменты - связные компоненты по общим вершинам.

    :param graph: список смежности неориентированного графа
    :param embedded_edges: рёбра уложенной части
    :return: список сегментов
    """

    edges = { frozenset((u, v)) for u, neighbors in enumerate(graph) for v in neighbors if u < v }

    remaining = edges - embedded_edges
    embedded_vertices = { v for edge in embedded_edges for v in edge }

    components = []
    for edge in remaining:
        touching = [component for component in components if component & edge]
        components = [component for component in components if not component & edge]
        components.append(set(edge) | set().union(*touching))

    return [
        Segment(
            edges=frozenset(edge for edge in remaining if edge <= vertices),
            vertices=frozenset(vertices),
            embedded=frozenset(vertices & embedded_vertices),
        )
        for vertices in components
    ]


def embed_chain(faces: list[list[int]], face_idx: int, chain: list[int]) -> list[list[int]]:
    """Вставляет цепь в грань (контур без замыкающей вершины), разбивая её на две."""

    face = faces[face_idx]
    i, j = face.index(chain[0]), face.index(chain[-1])

    if i > j:
        i, j = j, i
        chain = chain[::-1]

    mid = chain[1:-1]

    return [
        *faces[:face_idx],
        face[i:j + 1] + mid[::-1],
        face[j:] + face[:i + 1] + mid,
        *faces[face_idx + 1:],
    ]


def find_chain(segment: Segment, graph: list[list[int]]) -> list[int]:
    """Ищет кратчайший путь между контактными вершинами сегмента."""

    if len(segment.embedded) < 2:
        return []

    start = min(segment.embedded)
    contacts = segment.embedded - { start }
    parent = { start: None }
    queue = deque([start])

    while queue and not (contacts & parent.keys()):
        vertex = queue.popleft()
        neighbors = [
            u for u in graph[vertex]
            if u not in parent and frozenset((vertex, u)) in segment.edges
        ]
        parent |= {u: vertex for u in neighbors}
        queue.extend(neighbors)

    end = min(contacts & parent.keys(), default=None)
    chain = []

    while end is not None:
        chain.append(end)
        end = parent[end]

    return chain[::-1]


def tutte_embedding(graph: list[list[int]], outer: list[int]) -> np.ndarray:
    """Укладка Тутте: внешняя грань - правильный многоугольник,
    каждая внутренняя вершина - барицентр соседей (уравнения Лапласа).

    :param outer: контур внешней грани без замыкающей вершины
    :return: координаты вершин
    """

    angles = 2 * np.pi * np.arange(len(outer)) / len(outer)
    ring = np.column_stack([np.cos(angles), np.sin(angles)])

    lap = np.zeros((len(graph),) * 2)
    for v, neighbors in enumerate(graph):
        lap[v, neighbors] = -1.0
        lap[v, v] = len(neighbors)

    lap[outer] = 0.0
    lap[outer, outer] = 1.0
    rhs = np.zeros((len(graph), 2))
    rhs[outer] = ring

    return np.linalg.solve(lap, rhs)
