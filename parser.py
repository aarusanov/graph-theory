from bitarray import bitarray

def parse_tree_from_bits(bits: bitarray) -> list[list[int]]:
    """Восстановление дерева из битовой последовательности.

    :param bits: последовательность битов (0 — спуск к новому ребёнку, 1 — подъём к родителю)
    :return: список смежности, children[u] — список детей вершины u
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


def parse_graph_to_dot(children: list[list[int]], name: str = "tree") -> str:
    """Построение DOT-описания неориентированного графа без петель.

    :param children: список смежности, children[u] — список соседей вершины u
    :param name: имя графа в DOT
    :return: строка с DOT-описанием
    """
    lines = [f"graph {name} {{", "  rankdir=TB;"]
    lines += [
        f"  {u} -- {v};"
        for u, neighbors in enumerate(children)
        for v in neighbors
        if u < v
    ]
    lines.append("}")
    return "\n".join(lines)
