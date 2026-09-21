import subprocess
from itertools import permutations
from pathlib import Path

from algo import hungarian
from parser import parse_tree_from_bits, parse_graph_to_dot

INF = float("inf")


def render(dot: str, name: str) -> None:
  Path(f"out/{name}.dot").write_text(dot, encoding="utf-8")
  subprocess.run(["dot", "-Tpng", f"out/{name}.dot", "-o", f"out/{name}.png"], check=True)


class Solution:
  @classmethod
  def solve_task_1(cls) -> None:
    """Задание 1: восстановление дерева из битовой последовательности и визуализация графов."""
    tree = parse_tree_from_bits([0, 0, 1, 0, 1, 1, 0, 1])
    assert tree == [[1, 4], [2, 3], [], [], []]

    render(parse_graph_to_dot(tree), "tree")
    render(parse_graph_to_dot([[2, 3, 4], [2, 3, 4, 5], [0, 1, 3, 4], [0, 1, 2, 5], [0, 1, 2], [1, 3]], "example_graph"), "graph")

  @classmethod
  def solve_task_2(cls) -> None:
    """Задание 2: венгерский алгоритм — оптимальное полное паросочетание на двудольном графе."""
    w = [[4, 1, 3], [2, 0, 5], [3, 2, 2]]
    brute = [sum(w[i][p[i]] for i in range(3)) for p in permutations(range(3))]

    assert hungarian(w) == (5, [1, 0, 2])
    assert hungarian(w, maximize=True)[0] == max(brute) == 11
    assert hungarian([[1, 2, 3], [3, 2, 1]]) == (2, [0, 2])
    assert hungarian([[1, INF], [2, 1]]) == (2, [0, 1])

    print("hungarian: ok")


if __name__ == '__main__':
  Solution.solve_task_1()
  Solution.solve_task_2()
