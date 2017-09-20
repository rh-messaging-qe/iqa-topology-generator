import itertools
import networkx as nx
import matplotlib.pyplot as plt
from random import shuffle

from load_graph import export_graph


class Topology:
    DEFAULT_COST = 1

    def __init__(self):
        pass

    def create_graph(self, routers, brokers, graph_type):
        """

        :param routers:
        :param brokers:
        :param graph_type:
        :return:
        """
        print "Graph_type: " + str(graph_type)
        graph = nx.Graph()

        graph.add_nodes_from(routers, type='router')
        graph.add_nodes_from(brokers, type='broker')

        graph = getattr(self, graph_type)(graph, routers, brokers)

        # export_graph(graph, "topology.svg")

        return graph

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
            print brokers[x]
            if last_b <= last_r:
                graph.add_edge(brokers[x], routers[x])
            else:
                # @TODO - update looping over routers with brokers-edge (loop 0-n, multiple: brokers/router)
                if x > last_r:
                    y = 0
                graph.add_edge(brokers[x], routers[y])
                y += 1


        nx.set_edge_attributes(graph, 'value', self.DEFAULT_COST)

        return graph