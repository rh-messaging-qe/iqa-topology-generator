import itertools
import networkx as nx
import sys
import yaml
import matplotlib.pyplot as plt

from networkx.readwrite import json_graph


class Topology:
    """
    Class representing generated topology.
    """
    # Default value for edge weight
    DEFAULT_COST = 1
    ERR_GRAPH_FORMAT = 99
    ERR_OPEN_FILE = 98
    ERR_CREATE_GRAPH = 97

    def __init__(self):
        self.graph = None

    def load_graph_from_json(self, filename):
        """
        Method for load graph data from file.
        :param filename: path to file with graph data
        """

        try:
            with open(filename, 'r') as stream:
                graph_json = yaml.load(stream)
        except Exception as exc:
            sys.stdout.write("Exception: {}\nFile {} doesn't exists.\n".format(exc, filename))
            # raise Exception
            sys.exit(self.ERR_OPEN_FILE)

        try:
            self.graph = json_graph.node_link_graph(graph_json)
        except Exception as exc:
            sys.stdout.write("Exception: {}\nLoaded file isn't contain valid graph.\n".format(exc))
            # raise Exception
            sys.exit(self.ERR_GRAPH_FORMAT)

    def export_graph(self, path, title, graph_type):
        """
        Method for export networkx graph into svg file.
        :param title: Title of graph
        :param path: Path to output file
        :param graph_type: Graph type
        """

        color_map = []
        for n in self.graph.nodes():
            if self.graph.node[n]['type'] == 'router':
                color_map.append('yellow')
            else:
                color_map.append('#BBF94B')

        if graph_type == 'complete_graph':
            pos = nx.shell_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph)

        plt.figure(1, figsize=(14, 14))
        # nodes
        nx.draw_networkx(self.graph, pos=pos, node_size=2500, node_color=color_map, font_size=12)
        # edges
        nx.draw_networkx_edges(self.graph, pos=pos, edge_color='black')
        edge_labels = nx.get_edge_attributes(self.graph, 'value')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels, font_size=14)

        plt.axis('off')
        plt.title(title)
        plt.savefig(path, format='svg')
        # plt.show()  # TODO remove show, it's just for debug

    def create_graph(self, routers, brokers, graph_type):
        """
        Method for create new graph only from nodes names and graph type (complete, bus, line, line-mixed)
        :param routers: List of routers ID
        :param brokers: List of brokers ID
        :param graph_type: Type of graph
        :return:
        """
        sys.stderr.write("Graph_type: " + str(graph_type)+"\n")  # @TODO remove this
        self.graph = nx.Graph()

        self.graph.add_nodes_from(routers, type='router')
        self.graph.add_nodes_from(brokers, type='broker')

        try:
            getattr(self, graph_type)(self.graph, routers, brokers)
        except AttributeError:
            sys.stdout.write(
                "No method for create '{}' in class Topology!\nUse: 'bus_graph', 'line_graph', 'line_mix_graph', "
                "'complete_graph' or 'cycle_graph' in config file as graph type.\n".format(
                    graph_type))
            sys.exit(self.ERR_CREATE_GRAPH)

    def complete_graph(self, graph, *_):
        """
        Method for create complete graph.
        :param graph: Graph
        :param _: unused parameters (called by getattr())
        """
        if graph.is_directed():
            edges = itertools.permutations(self.graph.nodes(), 2)       # For future using
        else:
            edges = itertools.combinations(self.graph.nodes(), 2)

        graph.add_edges_from(edges, value=self.DEFAULT_COST)

        self.graph = graph

    def line_graph(self, graph, routers, brokers):
        """
        Method for create line graph (BBRRRRBB...).
        :param graph: Graph
        :param routers: List of routers ID
        :param brokers: List of brokers ID
        """
        start_idx = 0
        last_b = len(brokers)
        last_r = len(routers) - 1

        for x in range(start_idx, last_r):
            graph.add_edge(routers[x], routers[x + 1])

        for x in range(start_idx, last_b / 2 - 1):
            graph.add_edge(brokers[x], brokers[x + 1])

        for x in range(last_b - 1, last_b / 2, -1):
            graph.add_edge(brokers[x], brokers[x - 1])

        if brokers and routers:
            graph.add_edge(brokers[start_idx], routers[start_idx])
            graph.add_edge(brokers[last_b - 1], routers[last_r])
        nx.set_edge_attributes(graph, 'value', self.DEFAULT_COST)

        self.graph = graph

    def line_mix_graph(self, graph, routers, brokers, complete=False):
        """
        Method for create line-mixed graph (BRBRBRBR...).
        :param complete: Flag of line/complete graph
        :param graph: Graph
        :param routers: List of routers ID
        :param brokers: List of brokers ID
        """

        nodes = []
        len_b = len(brokers)
        len_r = len(routers)

        # @TODO add broker/routers better (2R1B2R1B...)
        if len_b > len_r:
            multiplier = len_b / len_r + 1
            for x in range(1, len(brokers) + len(routers) + 1):
                if x % multiplier == 0 and routers:
                    nodes.append(routers.pop())
                else:
                    nodes.append(brokers.pop())
        else:
            multiplier = len_r / len_b + 1
            for x in range(1, len(brokers) + len(routers) + 1):
                if x % multiplier == 0 and brokers:
                    nodes.append(brokers.pop())
                else:
                    nodes.append(routers.pop())

        for x in range(0, len(nodes) - 1):
            graph.add_edge(nodes[x], nodes[x + 1])

        if complete:
            graph.add_edge(nodes[0], nodes[len(nodes) - 1])

        nx.set_edge_attributes(graph, 'value', self.DEFAULT_COST)

        self.graph = graph

    def cycle_graph(self, graph, routers, brokers):
        """
        Method for create cycle graph.
        :param graph: Graph
        :param routers: List of routers ID
        :param brokers: List of brokers ID
        """
        self.line_mix_graph(graph, routers, brokers, True)

    def bus_graph(self, graph, routers, brokers):
        """
        Method for create bus graph.
        :param graph: Graph
        :param routers: List of routers ID
        :param brokers: List of brokers ID
        """
        start_idx = 0
        y = 0
        last_b = len(brokers) - 1
        last_r = len(routers) - 1

        for x in range(start_idx, last_r):
            graph.add_edge(routers[x], routers[x + 1])

        for x in range(start_idx, len(brokers)):
            if last_b <= last_r:
                graph.add_edge(brokers[x], routers[x])
            else:
                # @TODO - update looping over routers with brokers-edge (loop 0-n, multiple: brokers/router)
                if y > last_r:
                    y = 0
                graph.add_edge(brokers[x], routers[y])
                y += 1

        nx.set_edge_attributes(graph, 'value', self.DEFAULT_COST)

        self.graph = graph
