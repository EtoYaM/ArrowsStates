from pyvis.network import Network
from arrows import arrows
import networkx as nx
from creation import create_edges, create_nodes
import matplotlib.pyplot as plt

MATPOT = True

# ar_map_raw = ""
with open("file_str") as f:
    ar_map_raw = f.read()
ar_map = arrows.Map(ar_map_raw)

graph = nx.DiGraph()

create_nodes(ar_map, graph)
create_edges(graph)





if MATPOT:
    pos = {node: (node[0], -node[1]) for node in graph.nodes}
    colors = [data.get("color", "black") for posit, data in graph.nodes(data=True)]
    nx.draw_networkx_edges(graph, pos, arrows=True, arrowsize=10, edge_color='gray', width=2,
                           connectionstyle='arc3,rad=-0.2')
    nx.draw_networkx_nodes(graph, pos, node_color=colors, node_size=50)
    nx.draw_networkx_labels(graph, pos, font_size=7)
    plt.axis('off')
    plt.show()
else:
    net = Network(height='800px', width='100%', notebook=False, directed=True, cdn_resources='in_line')

    net.set_options("""
    var options = {
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
      }
    }
    """)
    print("Переименование")
    graph = nx.relabel_nodes(graph, {n: f"{n[0]}_{n[1]}" for n in graph.nodes()})
    print("Расположение вершин")
    net.from_nx(graph)

    # for node in net.get_nodes():
    #     net.get_node(node)['label'] = ''  # Отключает подписи

    print("Показ")
    with open('graph.html', 'w', encoding='utf-8') as f:
        f.write(net.generate_html(notebook=False))
