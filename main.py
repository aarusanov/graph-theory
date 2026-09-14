from graphviz import Source

from parser import parse_tree_from_bits, parse_graph_to_dot

def save_graph(graph_dot: str, filename: str = "graph.dot"):
  with open(filename, "w", encoding="utf-8") as f:
    f.write(graph_dot)

if __name__ == '__main__':
  tree = parse_tree_from_bits([0, 0, 1, 0, 1, 1, 0, 1])

  tree_dot = parse_graph_to_dot(tree)

  save_graph(tree_dot, "out/tree.dot")
  Source(tree_dot).render("out/tree", format="png", view=True, cleanup=True)

  graph_dot = parse_graph_to_dot([[2, 3, 4], [2, 3, 4, 5], [0, 1, 3, 4], [0, 1, 2, 5], [0, 1, 2], [1, 3]], "example_graph")

  save_graph(graph_dot, "out/graph.dot")
  Source(graph_dot).render("out/graph", format="png", view=True, cleanup=True)
