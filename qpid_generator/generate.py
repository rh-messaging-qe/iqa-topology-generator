#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx

# Default port-value for  listeners/connectors
DEFAULT_PORT = 5672
# Default queue name for linkRoutes
DEFAULT_QUEUE = 'default_queue'


def get_conf(graph):
    """
    Function for start generating config variables for routers.
    :param graph: networkx graph of topology
    :return: config variables in json
    """

    confs = {}
    node_type = nx.get_node_attributes(graph, 'type')

    for node, nbrdict in graph.adjacency_iter():
        if node_type[node] == 'broker':
            continue
        # init
        confs.setdefault(node, {})
        # Generate router info
        confs[node].update(generate_router_info(graph, node))
        # Generate listeners
        confs[node].update({'listener': generate_listeners(graph, node)})
        # Generate connectors with link-routes
        connectors, link_routes = generate_connectors(graph, node, nbrdict, node_type)
        if connectors:
            confs[node].update({'connector': connectors})
        if link_routes:
            confs[node].update({'linkRoute': link_routes})

    return confs


def generate_listeners(graph, node):
    """
    Function for generate information about listeners.
    Generate default or self-defined values.
    :param graph: networkx graph of topology
    :param node: current processing node
    :return: listeners variables in json
    """
    list_vars = nx.get_node_attributes(graph, 'listener')

    listeners = []

    if node in list_vars:
        listeners = list_vars[node]
    if node not in nx.get_node_attributes(graph, 'def_list'):
        listeners.append(
            {
                'host': '0.0.0.0',
                'port': DEFAULT_PORT,
                'role': 'inter-router'
            }
        )
        listeners.append(
            {
                'host': '0.0.0.0',
                'port': DEFAULT_PORT,
                'role': 'normal',
                'authenticatePeer': 'no',
                'saslMechanisms': 'ANONYMOUS'
            }
        )

    return listeners


def generate_connectors(graph, node, nbrdict, node_type):
    """
    Function for generate connectors.
    Connector for router is specified in graph_file: create it
    Connector for router is not specified in graph_file: create default connector with specific role 'inter-router'
    Connector for broker is specified in graph_file: check connector 'host' and linkRoute 'connection'
            if:     connector without linkRoute isn't created
            elif:   linkRoute without connector aren't created
            else:   create both
    Connector for broker is not specified: create default connector and linkRoutes with default queue
    :param graph: networkx graph of topology
    :param node: current processing node
    :param nbrdict: dict of outgoing edges from processing node
    :param node_type: type of all nodes
    :return: connectors and linkRoutes variables in json
    """

    conn_vars = nx.get_node_attributes(graph, 'connector')
    link_vars = nx.get_node_attributes(graph, 'linkRoute')
    connectors = []
    link_route = []

    # @TODO - reformat this BORDEL (7 rows)
    if node in conn_vars:
        if node in link_vars:
            for host in conn_vars:
                for route in link_vars[node]:
                    if host == route['connection']:
                        link_route.append(route)
                        connectors = conn_vars[node]

    if node not in nx.get_node_attributes(graph, 'def_conn'):
        # outgoing links
        for out in nbrdict.keys():
            if node_type[out] == 'router':
                connectors.append({
                    'host': out,
                    'port': DEFAULT_PORT,  # same rule as above
                    'role': 'inter-router'
                })
            elif node_type[out] == 'broker':
                connectors.append({
                    'host': out,
                    'port': DEFAULT_PORT,  # same rule as above
                    'role': 'route-container'
                })
                link_route.append({
                    'prefix': DEFAULT_QUEUE,
                    'connection': out,
                    'dir': 'in'
                })
                link_route.append({
                    'prefix': DEFAULT_QUEUE,
                    'connection': out,
                    'dir': 'out'
                })

    return connectors, link_route


def generate_router_info(graph, node):
    """
    Function for generate information about router itself.
    :param graph: networkx graph of topology
    :param node: current processing node
    :return: router variables in json
    """

    rout_vars = nx.get_node_attributes(graph, 'router')
    # TODO - problem ve vasrs pro ansible (jedna masina, jeden router - vymyslet a vyzkouset moznosti pro vice routru na masine) a upravit dle toho generovani
    mode = rout_vars[node] if node in rout_vars else 'standalone'

    router_info = {
        'machine': node,
        'router': [
            {
                'id': node,
                'mode': mode
            }
        ]
    }

    return router_info
