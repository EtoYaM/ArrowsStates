from pyvis.network import Network
from arrows import arrows
from arrows.arrows import ArrowType
import networkx as nx
from creation import create_edges, create_nodes
import matplotlib.pyplot as plt
from collections import defaultdict
from processing import process
import pygraphviz as pgv

MATPOT = False
GRAPH_VIS = False  # Через pygraphviz
PROCESS = True  # Округлять 2-степенные связи
PYVIS_SHOW = False
GRAPH_SHOW = True  # Отображать без учёта координат
SAVE_ONLY_BIGGEST = True  # Оставляет только самый большой граф

# ar_map_raw = ""
with open("file_str") as f:
    ar_map_raw = f.read()
ar_map = arrows.Map(ar_map_raw)

graph = nx.MultiDiGraph()

create_nodes(ar_map, graph)
create_edges(graph)

if PROCESS:
    process(graph)


if SAVE_ONLY_BIGGEST:
    components = list(nx.weakly_connected_components(graph))
    largest = max(components, key=len)
    print(f"Узлов в большой компоненте: {len(largest)} из {graph.number_of_nodes()}")
    nodes_to_remove = set(graph.nodes()) - largest
    graph.remove_nodes_from(nodes_to_remove)


if MATPOT:
    pos = {node: (node[0], -node[1]) for node in graph.nodes}
    colors = [data.get("color", "black") for posit, data in graph.nodes(data=True)]
    nx.draw_networkx_edges(graph, pos, arrows=True, arrowsize=10, edge_color='gray', width=2,
                           connectionstyle='arc3,rad=-0.2')
    nx.draw_networkx_nodes(graph, pos, node_color=colors, node_size=50)
    nx.draw_networkx_labels(graph, pos, font_size=7)
    if PROCESS:
        edge_labels = {edge: "1" for edge in graph.edges}
        nx.draw_networkx_edge_labels(
            graph, pos, edge_labels=edge_labels,
            label_pos=0.5,  # 0.5 — середина ребра
            font_size=7,
            font_color='darkred',
            rotate=False,  # не поворачивать вдоль ребра
            bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.7),
        )
    plt.axis('off')
    plt.show()
elif GRAPH_VIS:
    pos = {node: f"{node[0]},{node[1]}!" for node in graph.nodes}
    nx.set_node_attributes(graph, pos, "pos")

    graph_pgv = nx.nx_agraph.to_agraph(graph)
    graph_pgv.node_attr['shape'] = 'circle'
    graph_pgv.edge_attr['color'] = 'red'
    graph_pgv.node_attr['width'] = '0.5'
    graph_pgv.node_attr['height'] = '0.5'
    graph_pgv.node_attr['fixedsize'] = 'true'
    graph_pgv.node_attr['fontsize'] = 8

    graph_pgv.graph_attr['rankdir'] = 'TB'
    graph_pgv.graph_attr['rankdir'] = 'LR'
    graph_pgv.graph_attr['splines'] = 'ortho'

    # 4. Рисуем
    if GRAPH_SHOW:
        graph_pgv.layout(prog='dot')
    else:
        graph_pgv.layout(prog='neato')
    graph_pgv.draw('nx_to_pgv.png')
else:
    net = Network(height='800px', width='100%', notebook=False, directed=True, cdn_resources='in_line')

    net.set_options("""
    {
      "physics": { "enabled": false },
      "edges": {
        "arrows": { "to": { "enabled": true, "scaleFactor": 0.8 } },
        "color": { "inherit": false },
        "smooth": {
          "enabled": true,
          "type": "curvedCW",
          "roundness": 0.1
        },
        "width": 2
      }""" + (''',"layout": {
        "hierarchical": {
          "enabled": true,
          "direction": "UD",
          "sortMethod": "directed",
          "levelSeparation": 100,
          "nodeSpacing": 200,
          "treeSpacing": 180,
          "blockShifting": true,
          "edgeMinimization": true,
          "parentCentralization": false
        }
      }''' if GRAPH_SHOW else "") + "}")

    # if GRAPH_SHOW:
    #     for node in graph.nodes:
    #         node["level"] = node[0] + node[1]
    levels = {}
    sources = [n for n in graph.nodes() if graph.in_degree(n) == 0]

    for src in sources:
        dist = nx.single_source_dijkstra_path_length(graph, src, weight="length")
        for node, d in dist.items():
            levels[node] = max(levels.get(node, 0), d)
    for node in graph.nodes():
        levels.setdefault(node, 0)
    for node, data in graph.nodes(data=True):
        data["level"] = levels[node]

    print("Переименование")
    graph = nx.relabel_nodes(graph, {n: f"{n[0]}_{n[1]}" for n in graph.nodes()})
    if PROCESS:
        edges = defaultdict(int)
        for edge in graph.edges:
            graph.edges[edge]["label"] = str(graph.edges[edge]["length"])
            graph.edges[edge]["smooth"] = {
                # 'roundness': (1 if edges[edge[0]] % 2 else -1) * (edges[edge[0]] / 100
                #                                                    + 0.5 / graph.edges[edge]["length"]),
                # 'type': 'curvedCCW',
                "type": "cubicBezier",
                "forceDirection": "horizontal",
                "roundness": 1
            }
            edges[edge[0]] += 1
    print("Расположение вершин")
    net.from_nx(graph)

    # for node in net.get_nodes():
    #     net.get_node(node)['label'] = ''  # Отключает подписи
    if PYVIS_SHOW:
        net.show('graph.html', notebook=False)
    print("Показ")
    with open('graph.html', 'w', encoding='utf-8') as f:
        f.write(net.generate_html(notebook=False))
