import matplotlib.pyplot as plt
import networkx as nx
import yaml
from networkx.readwrite import json_graph


def load_graph_from_json(filename='random'):
    """
    Function for load graph data from file.
    :param filename: path to file with graph data
    :return: networkx graph
    """

    if filename == 'random':
        # @TODO - create random graph generation just based on inventory file
        print "TODO: random graph"
        exit(0)

    with open(filename, 'r') as stream:
        try:
            graph_json = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return json_graph.node_link_graph(graph_json)


def export_graph(graph, path):
    """
    Function for export networkx graph into svg file.
    :param graph: networkx graph
    """

    color_map = []
    for n in graph.nodes():
        if graph.node[n]['type'] == 'router':
            color_map.append('yellow')
        else:
            color_map.append('#BBF94B')

    pos = nx.spring_layout(graph)

    plt.figure(1, figsize=(14, 14))
    # nodes
    nx.draw_networkx(graph, pos=pos, node_size=2500, node_color=color_map, font_size=12)
    # edges
    nx.draw_networkx_edges(graph, pos=pos, edge_color='black')
    edge_labels = nx.get_edge_attributes(graph, 'value')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels, font_size=14)

    plt.axis('off')
    # plt.title('Topology')
    plt.savefig(path, format='svg')
    # plt.show()  # TODO remove show, it's just for debug
