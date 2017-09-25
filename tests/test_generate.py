import unittest

from nose.tools import assert_equals

from qpid_generator.generate import *


class GenerateRouterInfo(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.graph = nx.Graph()

        cls.graph.add_node('router1', type='router', mode='inter-router')
        cls.graph.add_node('router2', type='router')

    def test_generate_router_1(self):
        router = {
            'machine': 'router1',
            'router': [
                {
                    'id': 'router1',
                    'mode': 'inter-router'
                }
            ]
        }

        generated = generate_router_info(self.graph, 'router1')
        assert_equals(router, generated)

    def test_generate_router_2(self):
        router = {
            'machine': 'router2',
            'router': [
                {
                    'id': 'router2',
                    'mode': 'standalone'
                }
            ]
        }

        generated = generate_router_info(self.graph, 'router2')
        assert_equals(router, generated)


class GenerateListeners(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.graph = nx.Graph()

        cls.graph.add_node('router1', type='router', listener={'host': '1.1.1.1', 'port': '666'}, def_list='no')
        cls.graph.add_node('router2', type='router', listener={'host': '0.0.0.0', 'port': '777'})
        cls.graph.add_node('router3', type='router', def_list='no')
        cls.graph.add_node('router4', type='router')

    def test_generate_listeners_1(self):
        listener = [
            {
                'host': '1.1.1.1',
                'port': '666'
            }
        ]

        generated = generate_listeners(self.graph, 'router1')
        assert_equals(listener, generated)

    def test_generate_listeners_2(self):
        listener = [
            {
                'host': '0.0.0.0',
                'port': '777'},
            {
                'host': '0.0.0.0',
                'port': '5672',
                'role': 'inter-router'},
            {
                'host': '0.0.0.0',
                'port': '5672',
                'role': 'normal',
                'authenticatePeer': 'no',
                'saslMechanisms': 'ANONYMOUS'
            }
        ]

        generated = generate_listeners(self.graph, 'router2')
        assert_equals(listener, generated)

    def test_generate_listeners_3(self):
        listener = [
            {
                'host': '0.0.0.0',
                'port': '5672',
                'role': 'inter-router'},
            {
                'host': '0.0.0.0',
                'port': '5672',
                'role': 'normal',
                'authenticatePeer': 'no',
                'saslMechanisms': 'ANONYMOUS'
            }
        ]

        generated = generate_listeners(self.graph, 'router3')
        assert_equals(listener, generated)

    def test_generate_listeners_4(self):
        listener = [
            {
                'host': '0.0.0.0',
                'port': '5672',
                'role': 'inter-router'},
            {
                'host': '0.0.0.0',
                'port': '5672',
                'role': 'normal',
                'authenticatePeer': 'no',
                'saslMechanisms': 'ANONYMOUS'
            }
        ]

        generated = generate_listeners(self.graph, 'router4')
        assert_equals(listener, generated)


class GenerateConnectors(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.graph = nx.Graph()

        cls.graph.add_node('router1', type='router',
                           connector=[{'host': 'router2', 'port': '5672'}, {'host': 'router3', 'port': '5672'}],
                           def_conn='no')
        cls.graph.add_node('router2', type='router',
                           connector=[{'host': 'router1', 'port': '5672'}, {'host': 'router3', 'port': '5672'}])
        cls.graph.add_node('router3', type='router', connector={'host': 'router2', 'port': '5672'})
        cls.graph.add_node('router4', type='router', def_conn='no')
        cls.graph.add_node('router5', type='router')

        cls.graph.add_node('broker1', type='broker')

    def test_generate_connector_1(self):
        connector = [
            {
                'host': 'router2',
                'port': '5672'
            },
            {
                'host': 'router3',
                'port': '5672'
            }]

        link_routes = []

        nbrdict = {'router1': {u'value': 10}, 'broker2': {u'value': 5}}
        node_types = {'router1': 'router', 'router2': 'router', 'router3': 'router', 'router4': 'router',
                      'router5': 'router'}

        generated = generate_connectors(self.graph, 'router1', nbrdict, node_types)
        assert_equals((connector, link_routes), generated)

    def test_generate_connector_2(self):
        connector = [
            {
                'host': 'router1',
                'port': '5672'
            },
            {
                'host': 'router3',
                'port': '5672'
            },
            {
                'host': 'router1',
                'port': '5672',
                'role': 'inter-router'
            },
            {
                'host': 'router3',
                'port': '5672',
                'role': 'inter-router'
            }
        ]

        link_routes = []

        nbrdict = {'router1': {u'value': 10}, 'router3': {u'value': 5}}
        node_types = {'router1': 'router', 'router2': 'router', 'router3': 'router', 'router4': 'router',
                      'router5': 'router'}

        gen_conn, gen_link = generate_connectors(self.graph, 'router2', nbrdict, node_types)

        assert_equals(sorted(connector), sorted(gen_conn))
        assert_equals(sorted(link_routes), sorted(gen_link))

    def test_generate_connector_3(self):
        connector = [
            {
                'host': 'router2',
                'port': '5672'
            },
            {
                'host': 'router1',
                'port': '5672',
                'role': 'inter-router'
            },
            {
                'host': 'router2',
                'port': '5672',
                'role': 'inter-router'
            }
        ]

        link_routes = []

        nbrdict = {'router2': {u'value': 10}, 'router1': {u'value': 5}}
        node_types = {'router1': 'router', 'router2': 'router', 'router3': 'router', 'router4': 'router',
                      'router5': 'router'}

        gen_conn, gen_link = generate_connectors(self.graph, 'router3', nbrdict, node_types)

        assert_equals(sorted(connector), sorted(gen_conn))
        assert_equals(sorted(link_routes), sorted(gen_link))

    def test_generate_connector_4(self):
        connector = []

        link_routes = []

        nbrdict = {'router2': {u'value': 10}, 'router1': {u'value': 5}}
        node_types = {'router1': 'router', 'router2': 'router', 'router3': 'router', 'router4': 'router',
                      'router5': 'router'}

        gen_conn, gen_link = generate_connectors(self.graph, 'router4', nbrdict, node_types)

        assert_equals(sorted(connector), sorted(gen_conn))
        assert_equals(sorted(link_routes), sorted(gen_link))

    def test_generate_connector_5(self):
        connector = [
            {
                'host': 'router4',
                'port': '5672',
                'role': 'inter-router'
            },
            {
                'host': 'router3',
                'port': '5672',
                'role': 'inter-router'
            }
        ]

        link_routes = []

        nbrdict = {'router4': {u'value': 10}, 'router3': {u'value': 5}}
        node_types = {'router1': 'router', 'router2': 'router', 'router3': 'router', 'router4': 'router',
                      'router5': 'router'}

        gen_conn, gen_link = generate_connectors(self.graph, 'router5', nbrdict, node_types)

        assert_equals(sorted(connector), sorted(gen_conn))
        assert_equals(sorted(link_routes), sorted(gen_link))

    def test_generate_connector_6(self):
        connector = [
            {
                'host': 'router1',
                'port': '5672',
                'role': 'inter-router'
            },
            {
                'host': 'router3',
                'port': '5672',
                'role': 'inter-router'
            },
            {
                'host': 'broker1',
                'port': '5672',
                'role': 'route-container'
            }
        ]

        link_routes = [
            {
                'prefix': 'default_queue',
                'connection': 'broker1',
                'dir': 'in'
            },
            {
                'prefix': 'default_queue',
                'connection': 'broker1',
                'dir': 'out'
            }
        ]

        nbrdict = {'router1': {u'value': 10}, 'router3': {u'value': 5}, 'broker1': {u'value': 7}}
        node_types = {'router1': 'router', 'router2': 'router', 'router3': 'router', 'router4': 'router',
                      'router5': 'router', 'broker1': 'broker'}

        gen_conn, gen_link = generate_connectors(self.graph, 'router5', nbrdict, node_types)

        print connector
        print gen_conn

        assert_equals(sorted(connector), sorted(gen_conn))
        assert_equals(sorted(link_routes), sorted(gen_link))


class GenerateFullConfig(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.graph = nx.Graph()

        cls.graph.add_node('router1', type='router',
                           connector=[{'host': 'router2', 'port': '5675', 'mode': 'inter-router'}], def_conn='no')
        cls.graph.add_node('router2', type='router',
                           connector=[{'host': 'router1', 'port': '5678', 'mode': 'inter-router'}], def_conn='no')

        cls.graph.add_node('broker1', type='broker')
        cls.graph.add_node('broker2', type='broker')
        cls.graph.add_node('broker3', type='broker')

        cls.graph.add_edge('router2', 'router1', value=10)
        cls.graph.add_edge('router2', 'broker2', value=5)
        cls.graph.add_edge('router2', 'broker3', value=6)
        cls.graph.add_edge('router1', 'broker1', value=7)


    def test_generate_configs_1(self):
        # @TODO comparasion between two dictionary with different posiiton of values
        config = {
                "router1":
                    {
                        "machine": "router1",
                        "router": [
                            {
                                "id": "router2",
                                "mode": "standalone"
                            }
                        ],
                        "listener": [
                            {

                                'host': '0.0.0.0',
                                'port': '5672',
                                'role': 'inter-router'
                            },
                            {
                                'host': '0.0.0.0',
                                'port': '5672',
                                'role': 'normal',
                                'authenticatePeer': 'no',
                                'saslMechanisms': 'ANONYMOUS'
                            }
                        ],
                        "connector": [
                            {
                                "host": "router2",
                                "port": '5675',
                                'mode': 'inter-router'
                            },
                            {
                                "host": "broker1",
                                "port": '5672',
                                'mode': 'route-container'
                            }
                        ],
                        "linkRoute": [
                            {
                                "prefix": "default_queue",
                                "connection": "broker1",
                                "dir": "in"
                            },
                            {
                                "prefix": "default_queue",
                                "connection": "broker1",
                                "dir": "out"
                            }
                        ]
                    },
                'router2':
                    {
                        "machine": "router2",
                        "router": [
                            {
                                "id": "router1",
                                "mode": "standalone"
                            }
                        ],
                        "listener": [
                            {
                                "host": "0.0.0.0",
                                "role": "inter-router",
                                "port": "5672"
                            },
                            {
                                "host": "0.0.0.0",
                                "authenticatePeer": "no",
                                "role": "normal",
                                "port": "5672",
                                "saslMechanisms": "ANONYMOUS"
                            }
                        ],
                        "connector": [
                            {
                                "host": "router1",
                                "role": "inter-router",
                                "port": "5678"
                            },
                            {
                                "host": "broker2",
                                "role": "route-container",
                                "port": "5672"
                            },
                            {
                                "host": "broker3",
                                "role": "route-container",
                                "port": "5672"
                            }
                        ],
                        "linkRoute": [
                            {
                                "prefix": "default_queue",
                                "connection": "broker2",
                                "dir": "in"
                            },
                            {
                                "prefix": "default_queue",
                                "connection": "broker2",
                                "dir": "out"
                            },
                            {
                                "prefix": "default_queue",
                                "connection": "broker3",
                                "dir": "in"
                            },
                            {
                                "prefix": "default_queue",
                                "connection": "broker3",
                                "dir": "out"
                            }
                        ]
                    }
            }

        # assert_equals(get_conf(self.graph), config)
        pass
