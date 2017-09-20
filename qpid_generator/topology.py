import itertools
import networkx as nx
import yaml
import matplotlib.pyplot as plt

from networkx.readwrite import json_graph


class Topology():
    """

    """
    DEFAULT_COST = 1

    def __init__(self):
        self.graph = None

    def load_graph_from_json(self, filename):
        """
        Function for load graph data from file.
        :param filename: path to file with graph data
        :return: networkx graph
        """

        with open(filename, 'r') as stream:
            try:
                graph_json = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.graph = json_graph.node_link_graph(graph_json)

    def export_graph(self, path):
        """
        Function for export networkx graph into svg file.
        :param path:
        :param graph: networkx graph
        """

        color_map = []
        for n in self.graph.nodes():
            if self.graph.node[n]['type'] == 'router':
                color_map.append('yellow')
            else:
                color_map.append('#BBF94B')

        pos = nx.spring_layout(self.graph)

        plt.figure(1, figsize=(14, 14))
        # nodes
        nx.draw_networkx(self.graph, pos=pos, node_size=2500, node_color=color_map, font_size=12)
        # edges
        nx.draw_networkx_edges(self.graph, pos=pos, edge_color='black')
        edge_labels = nx.get_edge_attributes(self.graph, 'value')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels, font_size=14)

        plt.axis('off')
        # plt.title('Topology')
        plt.savefig(path, format='svg')
        # plt.show()  # TODO remove show, it's just for debug

    def create_graph(self, routers, brokers, graph_type):
        """

        :param routers:
        :param brokers:
        :param graph_type:
        :return:
        """
        print "Graph_type: " + str(graph_type)
        self.graph = nx.Graph()

        self.graph.add_nodes_from(routers, type='router')
        self.graph.add_nodes_from(brokers, type='broker')

        getattr(self, graph_type)(self.graph, routers, brokers)

    def complete_graph(self, graph, *_):
        """

        :param graph:
        :param _:
        :return:
        """
        if graph.is_directed():
            edges = itertools.permutations(nx.nodes_iter(graph), 2)
        else:
            edges = itertools.combinations(nx.nodes_iter(graph), 2)

        graph.add_edges_from(edges, value=self.DEFAULT_COST)

        return graph

    def line_graph(self, graph, routers, brokers):
        """

        :param graph:
        :param routers:
        :param brokers:
        :return:
        """
        start_idx = 0
        last_b = len(brokers) - 1
        last_r = len(routers) - 1

        for x in xrange(start_idx, last_r):
            graph.add_edge(routers[x], routers[x + 1])

        for x in xrange(start_idx, last_b / 2 - 1):
            graph.add_edge(brokers[x], brokers[x + 1])

        for x in xrange(last_b, last_b / 2, -1):
            graph.add_edge(brokers[x], brokers[x - 1])

        graph.add_edge(brokers[start_idx], routers[start_idx])
        graph.add_edge(brokers[last_b], routers[last_r])
        nx.set_edge_attributes(graph, 'value', self.DEFAULT_COST)

        return graph

    def line_mix_graph(self, graph, routers, brokers, complete=False):
        """

        :param complete:
        :param graph:
        :param routers:
        :param brokers:
        :return:
        """

        nodes = []
        len_b = len(brokers)
        len_r = len(routers)

        if len_b > len_r:
            multiplier = len_b / len_r + 1
            for x in xrange(1, len(brokers) + len(routers) + 1):
                if x % multiplier == 0 and routers:
                    nodes.append(routers.pop())
                else:
                    nodes.append(brokers.pop())
        else:
            multiplier = len_r / len_b + 1
            for x in xrange(1, len(brokers) + len(routers) + 1):
                if x % multiplier == 0 and brokers:
                    nodes.append(brokers.pop())
                else:
                    nodes.append(routers.pop())

        for x in xrange(0, len(nodes) - 1):
            graph.add_edge(nodes[x], nodes[x + 1])

        if complete:
            graph.add_edge(nodes[0], nodes[len(nodes) - 1])

        nx.set_edge_attributes(graph, 'value', self.DEFAULT_COST)

        return graph

    def cycle_graph(self, graph, routers, brokers):
        """

        :param graph:
        :param routers:
        :param brokers:
        :return:
        """
        graph = self.line_mix_graph(graph, routers, brokers, True)

        return graph

    def bus_graph(self, graph, routers, brokers):
        """

        :param graph:
        :param routers:
        :param brokers:
        :return:
        """
        start_idx = 0
        y = 0
        last_b = len(brokers) - 1
        last_r = len(routers) - 1

        for x in xrange(start_idx, last_r):
            graph.add_edge(routers[x], routers[x + 1])

        for x in xrange(start_idx, len(brokers)):
            if last_b <= last_r:
                graph.add_edge(brokers[x], routers[x])
            else:
                # @TODO - update looping over routers with brokers-edge (loop 0-n, multiple: brokers/router)
                if y > last_r:
                    y = 0
                graph.add_edge(brokers[x], routers[y])
                y += 1

        nx.set_edge_attributes(graph, 'value', self.DEFAULT_COST)

        return graph
