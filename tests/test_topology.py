import itertools
import os
import unittest

import networkx as nx
from nose.tools import assert_equals, raises

from msg_topgen.topology import Topology


class LoadTopologyTest(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.topology = Topology()
        cls.graph = nx.Graph()

        cls.graph.add_node('router1', type='router')
        cls.graph.add_node('router2', type='router')
        cls.graph.add_node('broker1', type='broker')
        cls.graph.add_node('broker2', type='broker')
        cls.graph.add_node('broker3', type='broker')
        cls.graph.add_edge('router2', 'router1', value=10)
        cls.graph.add_edge('router2', 'broker2', value=5)
        cls.graph.add_edge('router2', 'broker3', value=6)
        cls.graph.add_edge('router1', 'broker1', value=7)

    @raises(SystemExit)
    def test_load_empty_graph(self):
        self.topology.load_graph_from_json('tests/items/empty_graph_test.yml')

    @raises(SystemExit)
    def test_load_wrong_graph(self):
        self.topology.load_graph_from_json('tests/items/wrong_graph_test.yml')

    @raises(SystemExit)
    def test_load_non_exists_graph(self):
        self.topology.load_graph_from_json('tests/items/no_graph_test.yml')

    def test_load_ref_graph(self):
        self.topology.load_graph_from_json('tests/items/ref_graph_test.yml')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)


class SmallTopologyTest(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.topology = Topology()
        cls.graph = nx.Graph()

        cls.graph.add_node('router1', type='router')
        cls.graph.add_node('broker1', type='broker')
        cls.graph.add_node('broker2', type='broker')

        cls.routers = ['router1']
        cls.brokers = ['broker1', 'broker2']

    def setUp(self):
        self.graph.add_edge('router1', 'broker1', value=1)
        self.graph.add_edge('router1', 'broker2', value=1)

    def tearDown(self):
        self.graph.clear()

    def test_load_graph(self):
        self.topology.load_graph_from_json('tests/items/graph_test.yml')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_create_line(self):
        self.topology.create_graph(self.routers, self.brokers, 'line_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_create_line_mixed(self):
        self.topology.create_graph(self.routers, self.brokers, 'line_mix_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_create_bus(self):
        self.topology.create_graph(self.routers, self.brokers, 'bus_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_create_complete(self):
        self.graph.add_edge('broker1', 'broker2', value=1)
        self.topology.create_graph(self.routers, self.brokers, 'complete_graph')

        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    @raises(SystemExit)
    def test_create_non_exists_graph(self):
        self.topology.create_graph(self.routers, self.brokers, 'none_exists')


class BiggerTopologyTest(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.topology = Topology()
        cls.graph = nx.Graph()

        cls.routers = ['router1', 'router2']
        cls.brokers = ['broker1', 'broker2', 'broker3']

    def setUp(self):
        self.graph.add_node('router1', type='router')
        self.graph.add_node('router2', type='router')
        self.graph.add_node('broker1', type='broker')
        self.graph.add_node('broker2', type='broker')
        self.graph.add_node('broker3', type='broker')

    def tearDown(self):
        # for edge in self.graph.edges():
        self.graph.clear()

    def test_crete_line_mix(self):
        self.graph.add_edge('router1', 'broker1', value=1)
        self.graph.add_edge('router1', 'broker2', value=1)
        self.graph.add_edge('broker2', 'router2', value=1)
        self.graph.add_edge('router2', 'broker3', value=1)

        self.topology.create_graph(self.routers, self.brokers, 'line_mix_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_create_bus(self):
        self.graph.add_edge('router1', 'broker1', value=1)
        self.graph.add_edge('router1', 'router2', value=1)
        self.graph.add_edge('router2', 'broker2', value=1)
        self.graph.add_edge('router1', 'broker3', value=1)

        self.topology.create_graph(self.routers, self.brokers, 'bus_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_create_line_1(self):
        self.graph.add_edge('router1', 'router2', value=1)
        self.graph.add_edge('broker2', 'broker3', value=1)
        self.graph.add_edge('broker3', 'router2', value=1)
        self.graph.add_edge('router1', 'broker1', value=1)

        self.topology.create_graph(self.routers, self.brokers, 'line_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_create_line_2(self):
        self.graph.add_node('broker4', type='broker')

        self.graph.add_edge('router1', 'router2', value=1)
        self.graph.add_edge('broker1', 'router1', value=1)
        self.graph.add_edge('broker1', 'broker2', value=1)
        self.graph.add_edge('broker3', 'broker4', value=1)
        self.graph.add_edge('broker4', 'router2', value=1)

        brokers = ['broker1', 'broker2', 'broker3', 'broker4']

        self.topology.create_graph(self.routers, brokers, 'line_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_crete_complete(self):
        edges = itertools.permutations(self.graph.nodes(), 2)
        self.graph.add_edges_from(edges, value=1)

        self.topology.create_graph(self.routers, self.brokers, 'complete_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)


class HugeBrokerTopologyTest(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.topology = Topology()
        cls.graph = nx.Graph()

        cls.routers = ['router1', 'router2']
        cls.brokers = ['broker1', 'broker2', 'broker3', 'broker4', 'broker5', 'broker6', 'broker7']

    def setUp(self):
        self.graph.add_node('router1', type='router')
        self.graph.add_node('router2', type='router')
        self.graph.add_node('broker1', type='broker')
        self.graph.add_node('broker2', type='broker')
        self.graph.add_node('broker3', type='broker')
        self.graph.add_node('broker4', type='broker')
        self.graph.add_node('broker5', type='broker')
        self.graph.add_node('broker6', type='broker')
        self.graph.add_node('broker7', type='broker')

    def tearDown(self):
        # for edge in self.graph.edges():
        self.graph.clear()

    def test_create_line(self):
        self.graph.add_edge('router1', 'router2', value=1)
        self.graph.add_edge('broker1', 'router1', value=1)
        self.graph.add_edge('broker1', 'broker2', value=1)
        self.graph.add_edge('broker3', 'broker2', value=1)
        self.graph.add_edge('broker7', 'router2', value=1)
        self.graph.add_edge('broker6', 'broker5', value=1)
        self.graph.add_edge('broker5', 'broker4', value=1)
        self.graph.add_edge('broker7', 'broker6', value=1)

        self.topology.create_graph(self.routers, self.brokers, 'line_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_create_line_mix(self):
        self.graph.add_edge('broker1', 'broker2', value=1)
        self.graph.add_edge('broker2', 'router1', value=1)
        self.graph.add_edge('router1', 'broker3', value=1)
        self.graph.add_edge('broker3', 'broker4', value=1)
        self.graph.add_edge('broker4', 'router2', value=1)
        self.graph.add_edge('router2', 'broker5', value=1)
        self.graph.add_edge('broker5', 'broker6', value=1)
        self.graph.add_edge('broker6', 'broker7', value=1)

        self.topology.create_graph(self.routers, self.brokers, 'line_mix_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_create_bus(self):
        self.graph.add_edge('router1', 'router2', value=1)
        self.graph.add_edge('router1', 'broker1', value=1)
        self.graph.add_edge('router1', 'broker3', value=1)
        self.graph.add_edge('router1', 'broker5', value=1)
        self.graph.add_edge('router1', 'broker7', value=1)
        self.graph.add_edge('router2', 'broker2', value=1)
        self.graph.add_edge('router2', 'broker4', value=1)
        self.graph.add_edge('router2', 'broker6', value=1)

        self.topology.create_graph(self.routers, self.brokers, 'bus_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_create_complete(self):
        edges = itertools.permutations(self.graph.nodes(), 2)
        self.graph.add_edges_from(edges, value=1)

        self.topology.create_graph(self.routers, self.brokers, 'complete_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)


class HugeRouterTopologyTest(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.topology = Topology()
        cls.graph = nx.Graph()

        cls.routers = ['router1', 'router2', 'router3', 'router4', 'router5', 'router6', 'router7']
        cls.brokers = ['broker1', 'broker2']

    def setUp(self):
        self.graph.add_node('router1', type='router')
        self.graph.add_node('router2', type='router')
        self.graph.add_node('router3', type='broker')
        self.graph.add_node('router4', type='broker')
        self.graph.add_node('router5', type='broker')
        self.graph.add_node('router6', type='broker')
        self.graph.add_node('router7', type='broker')
        self.graph.add_node('broker1', type='broker')
        self.graph.add_node('broker2', type='broker')

    def tearDown(self):
        # for edge in self.graph.edges():
        self.graph.clear()

    def test_create_line(self):
        self.graph.add_edge('router1', 'router2', value=1)
        self.graph.add_edge('router2', 'router3', value=1)
        self.graph.add_edge('router3', 'router4', value=1)
        self.graph.add_edge('router4', 'router5', value=1)
        self.graph.add_edge('router5', 'router6', value=1)
        self.graph.add_edge('router6', 'router7', value=1)
        self.graph.add_edge('broker1', 'router1', value=1)
        self.graph.add_edge('broker2', 'router7', value=1)

        self.topology.create_graph(self.routers, self.brokers, 'line_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_create_line_mix(self):
        self.graph.add_edge('router1', 'router2', value=1)
        self.graph.add_edge('router2', 'broker1', value=1)
        self.graph.add_edge('broker1', 'router3', value=1)
        self.graph.add_edge('router3', 'router4', value=1)
        self.graph.add_edge('router4', 'broker2', value=1)
        self.graph.add_edge('broker2', 'router5', value=1)
        self.graph.add_edge('router5', 'router6', value=1)
        self.graph.add_edge('router6', 'router7', value=1)

        self.topology.create_graph(self.routers, self.brokers, 'line_mix_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_create_bus(self):
        self.graph.add_edge('router1', 'router2', value=1)
        self.graph.add_edge('router2', 'router3', value=1)
        self.graph.add_edge('router3', 'router4', value=1)
        self.graph.add_edge('router4', 'router5', value=1)
        self.graph.add_edge('router5', 'router6', value=1)
        self.graph.add_edge('router6', 'router7', value=1)
        self.graph.add_edge('router1', 'broker1', value=1)
        self.graph.add_edge('router2', 'broker2', value=1)

        self.topology.create_graph(self.routers, self.brokers, 'bus_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)

    def test_create_complete(self):
        edges = itertools.permutations(self.graph.nodes(), 2)
        self.graph.add_edges_from(edges, value=1)

        self.topology.create_graph(self.routers, self.brokers, 'complete_graph')
        assert_equals(nx.is_isomorphic(self.graph, self.topology.graph), True)