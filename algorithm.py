INF = float("inf")


def _augmenting_path(
    cost: list[list[float]],
    u: tuple[float, ...],
    v: tuple[float, ...],
    row_of: tuple[int | None, ...],
    i: int,
) -> tuple[int | None, float, tuple[int, ...], tuple[float, ...], tuple[int, ...]]:
    """Ищет кратчайший увеличивающий путь из свободной строки i
    (Дейкстра по столбцам в приведённых стоимостях cost - u - v).

    :return: (sink, min_val, parent, slack, tree_cols); sink — свободный столбец,
        конец пути (None — пути нет), min_val — длина пути, parent[j] — строка-
        предшественник, slack[j] — длина пути до столбца j, tree_cols — столбцы дерева
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

    :param w: матрица весов, w[i][j] — вес ребра из i-й вершины левой доли в j-ю правой;
        строк не больше, чем столбцов; отсутствующее ребро — INF
    :param maximize: True — искать максимум веса
    :return: (оптимальный вес, matching); matching[i] — вершина правой доли, сопоставленная i-й левой
    """
    n, m = len(w), len(w[0])
    if n > m:
        raise ValueError("полного паросочетания нет: вершин в левой доле больше, чем в правой")

    sgn = -1 if maximize else 1
    cost = [[INF if x == INF else sgn * x for x in row] for row in w]

    u = (.0,) * n              # потенциалы строк
    v = (.0,) * m              # потенциалы столбцов
    row_of = (None,) * m   # row_of[j] — строка, сопоставленная столбцу j
    col_of = (None,) * n   # col_of[i] — столбец, сопоставленный строке i

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
