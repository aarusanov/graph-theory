def parse_tree_from_bits(bits: list[int]) -> list[list[int]]:
    """Восстановление дерева из битовой последовательности.

    :param bits: последовательность битов (0 - спуск к новому ребёнку, 1 - подъём к родителю)
    :return: список смежности, children[u] - список детей вершины u
    """
    children, stack = [[]], [0]

    for bit in bits:
        if bit:
            stack.pop()
            continue
        children.append([])
        children[stack[-1]].append(len(children) - 1)
        stack.append(len(children) - 1)

    return children


def parse_graph_to_dot(children: list[list[int]], name: str = "tree", positions=None) -> str:
    """Построение DOT-описания неориентированного графа без петель.

    :param children: список смежности, children[u] - список соседей вершины u
    :param name: имя графа в DOT
    :param positions: координаты вершин
    :return: строка с DOT-описанием
    """
    lines = [f"graph {name} {{", "  rankdir=TB;"]
    if positions is not None:
        lines += ["  layout=neato;", "  node [shape=circle, fixedsize=true, width=0.25, fontsize=10];"]
        lines += [
            f'  {v} [pos="{2.5 * x},{2.5 * y}!"];' for v, (x, y) in enumerate(positions)
        ]
    lines += [
        f"  {u} -- {v};"
        for u, neighbors in enumerate(children)
        for v in neighbors
        if u < v
    ]
    lines.append("}")
    return "\n".join(lines)
