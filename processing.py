from arrows import arrows
from arrows.arrows import ArrowType
import networkx as nx


def process(graph: nx.MultiDiGraph) -> int:
    deleted = 0
    nx.set_edge_attributes(graph, 1, 'length')
    for node, data in list(graph.nodes(data=True)):
        if data["type"] in (ArrowType.Arrow, ArrowType.Detector, ArrowType.BlueArrow, ArrowType.DirectoinalButton,
                            ArrowType.BlueSplitterUpUp, ArrowType.Diagonal, ArrowType.SplitterUpDown,
                            ArrowType.SplitterUpRight, ArrowType.SplitterUpRightLeft, ArrowType.BlueSplitterRightUp,
                            ArrowType.BlueSplitterUpDiagonal):
            if (graph.in_degree(node) != 1) or (graph.out_degree(node) < 1):
                continue
            u = next(graph.predecessors(node))
            if u == node:
                continue
            data["color"] = "black"
            in_len = graph.edges[u, node, 0].get("length", 1)
            for v in graph.out_edges(node, keys=True):
                new_len = in_len + graph.edges[v].get("length", 1)
                graph.add_edge(u, v[1], length=new_len)
            graph.remove_node(node)
            deleted += 1
    return deleted
