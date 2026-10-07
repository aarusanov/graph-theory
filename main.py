import graphviz
from itertools import permutations
from pathlib import Path

from algorithm import INF, check_planarity, linear_sum_assignment, tutte_embedding
from parser import parse_tree_from_bits, parse_graph_to_dot


def render(dot: str, name: str) -> None:
  Path(f"out/{name}.dot").write_text(dot, encoding="utf-8")
  Path(f"out/{name}.png").write_bytes(graphviz.Source(dot).pipe("png"))


class Solution:
  @classmethod
  def solve_task_1(cls) -> None:
    """Задание 1: восстановление дерева из битовой последовательности и визуализация графов."""
    tree = parse_tree_from_bits([0, 0, 1, 0, 1, 1, 0, 1])
    assert tree == [[1, 4], [2, 3], [], [], []]

    render(parse_graph_to_dot(tree), "tree")

    graph = [[2, 3, 4], [2, 3, 4, 5], [0, 1, 3, 4], [0, 1, 2, 5], [0, 1, 2], [1, 3]]
    render(parse_graph_to_dot(graph, "example_graph"), "graph")

  @classmethod
  def solve_task_2(cls) -> None:
    """Задание 2: венгерский алгоритм - оптимальное полное паросочетание на двудольном графе."""
    graph = [[4, 1, 3], [2, 0, 5], [3, 2, 2]]
    brute = [sum(graph[i][p[i]] for i in range(3)) for p in permutations(range(3))]

    assert linear_sum_assignment(graph) == (5, [1, 0, 2])
    assert linear_sum_assignment(graph, maximize=True)[0] == max(brute) == 11
    assert linear_sum_assignment([[1, 2, 3], [3, 2, 1]]) == (2, [0, 2])
    assert linear_sum_assignment([[1, INF], [2, 1]]) == (2, [0, 1])
    assert linear_sum_assignment([[1, INF], [2, 1]], maximize=True) == (2, [0, 1])

    print("hungarian: ok")

  @classmethod
  def solve_task_3(cls) -> None:
    """Задание 3: гамма-алгоритм - проверка планарности графов."""

    assert check_planarity([[1, 2], [0, 2], [0, 1]])                # треугольник
    assert check_planarity([[1], [0]])                              # лес без циклов
    assert check_planarity([[1, 3, 2], [0, 2], [0, 1, 3], [0, 2]])  # K4
    assert check_planarity([[1, 2, 4], [0, 3, 5], [0, 3, 6], [1, 2, 7],
                            [0, 5, 6], [1, 4, 7], [2, 4, 7], [3, 5, 6]])  # куб Q3

    assert not check_planarity([[1, 2, 3, 4], [0, 2, 3, 4], [0, 1, 3, 4],
                                [0, 1, 2, 4], [0, 1, 2, 3]])              # K5
    assert not check_planarity([[3, 4, 5], [3, 4, 5], [3, 4, 5],
                                [0, 1, 2], [0, 1, 2], [0, 1, 2]])         # K3,3
    assert not check_planarity([[1, 4, 5], [0, 2, 6], [1, 3, 7], [2, 4, 8], [0, 3, 9],
                                [0, 7, 8], [1, 8, 9], [2, 5, 9], [3, 5, 6], [4, 6, 7]])  # Петерсен

    print("planarity: ok")

  @classmethod
  def solve_task_4(cls) -> None:
    """Задание 4: геометрическая укладка Тутте планарного графа."""

    cube = [[1, 2, 4], [0, 3, 5], [0, 3, 6], [1, 2, 7],
            [0, 5, 6], [1, 4, 7], [2, 4, 7], [3, 5, 6]]
    octahedron = [[1, 2, 4, 5], [0, 2, 3, 5], [0, 1, 3, 4],
                  [1, 2, 4, 5], [0, 2, 3, 5], [0, 1, 3, 4]]
    wheel = [[1, 2, 3, 4, 5, 6], [0, 2, 6], [0, 1, 3],
             [0, 2, 4], [0, 3, 5], [0, 4, 6], [0, 5, 1]]

    for graph, name, outer in [
      (cube, "tutte_cube", [0, 1, 3, 2]),          # внешняя грань - квадрат
      (octahedron, "tutte_octahedron", [0, 1, 2]),  # - треугольник
      (wheel, "tutte_wheel", [1, 2, 3, 4, 5, 6]),   # - шестиугольник, центр в барицентре
    ]:
      assert check_planarity(graph)
      render(parse_graph_to_dot(graph, name, tutte_embedding(graph, outer)), name)

    print("tutte: ok")


if __name__ == "__main__":
  Solution.solve_task_1()
  Solution.solve_task_2()
  Solution.solve_task_3()
  Solution.solve_task_4()
