import json

import networkx as nx
import yaml
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph


def load_graph_from_json(filename):
    with open(filename, 'r') as stream:
        try:
            graph_json = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # debug_print_graph_file(graph_json)

    return json_graph.node_link_graph(graph_json)


# @TODO - update legend for graph
def export_graph(graph):
    color_map = []
    for n in graph.nodes():
        if graph.node[n]['type'] == 'router':
            color_map.append('yellow')
        else:
            color_map.append('#BBF94B')

    pos = nx.spring_layout(graph)

    plt.figure(1, figsize=(14, 14))
    # nodes
    nx.draw(graph, pos=pos, node_size=2500, node_color=color_map)
    # nx.draw_networkx_nodes(graph, pos, node_size=1500, node_color=color_map)
    # edges
    nx.draw_networkx_edges(graph, pos=pos, edge_color='black')
    edge_labels = nx.get_edge_attributes(graph, 'value')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels, font_size=15)
    # labels
    # pos = nx.spectral_layout(graph, scale=1)
    nx.draw_networkx_labels(graph, pos=pos, font_size=10, alpha=0.5, label_pos=100, font_family='sans-serif',
                            with_labes=True)

    plt.title('Topology')
    plt.savefig("topology.svg", format='svg')
    plt.show()  # TODO remove show, it's just for debug


def debug_print_graph_file(graph_json):
    print "*********JSON**********\n"
    print json.dumps(graph_json, sort_keys=True, indent=2)
    print "*********JSON**********\n"
