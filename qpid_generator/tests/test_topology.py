import unittest

import networkx as nx
from nose.tools import assert_equals

from ..topology import Topology


class TopologyTest(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        print "Create topology instance..."
        cls.topology = Topology()
        cls.graph = nx.Graph()

        cls.graph.add_nodes('router1', type='router')
        cls.graph.add_nodes('broker1', type='broker')
        cls.graph.add_edge('router1', 'broker1', value=10)

    @classmethod
    def teardown_class(cls):
        print "Konec testu"

    def test_load_graph_1(self):
        self.topology.load_graph_from_json('/items/graph_test.yml')
        assert_equals(self.graph, self.topology.graph)