INF = float("inf")


def hungarian(w: list[list[float]], maximize: bool = False) -> tuple[float, list[int]]:
    """Венгерский алгоритм: полное паросочетание минимального (или максимального,
    если maximize=True) веса в двудольном графе. Сложность O(n^2 * m).

    :param w: матрица весов, w[i][j] — вес ребра из i-й вершины левой доли в j-ю правой;
        строк не больше, чем столбцов; отсутствующее ребро — INF (при maximize — -INF)
    :param maximize: True — искать максимум веса
    :return: (оптимальный вес, matching); matching[i] — вершина правой доли, сопоставленная i-й левой
    :raises ValueError: если строк больше столбцов (полного паросочетания не существует)
    """
    n, m = len(w), len(w[0])
    if n > m:
        raise ValueError("полного паросочетания нет: вершин в левой доле больше, чем в правой")

    sgn = -1 if maximize else 1
    a = [[0] * (m + 1)] + [[0] + [sgn * x for x in row] for row in w]

    u = [0] * (n + 1)
    v = [0] * (m + 1)
    p = [0] * (m + 1)
    way = [0] * (m + 1)

    for i in range(1, n + 1):
        p[0], j0 = i, 0
        minv = [INF] * (m + 1)
        used = [False] * (m + 1)

        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], INF, 0
            for j in range(1, m + 1):
                if not used[j]:
                    cur = a[i0][j] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1

    matching, weight = [0] * n, 0
    for j in range(1, m + 1):
        if p[j]:
            matching[p[j] - 1] = j - 1
            weight += w[p[j] - 1][j - 1]
    return weight, matching
