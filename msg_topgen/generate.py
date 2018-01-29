#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx

# Default start port-value for  listeners/connectors
# ATTENTION: be sure that ports [5672 - 5672+router_count] are free to use!
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

    for node, nbrdict in graph.adjacency():
        if node_type[node] == 'broker':
            continue
        # init
        confs.setdefault(node, {})
        # Generate router info
        confs[node].update(generate_router_info(graph, node, nbrdict, node_type))
        # Generate listeners
        confs[node].update({'listener': generate_listeners(graph, node, nbrdict, node_type)})
        # Generate addresses
        confs[node].update({'address': generate_addresses(graph, node, nbrdict, node_type)})
        # Generate sslProfile and other connection settings
        confs[node].update(generate_connection_settings(graph, node))

    # Generate connectors according of listeners
    for node, nbrdict in graph.adjacency():
        if node_type[node] == 'broker':
            continue
        # Generate connectors with link-routes
        connectors, link_routes = generate_connectors(graph, node, nbrdict, node_type)
        if connectors:
            confs[node].update({'connector': connectors})
        if link_routes:
            confs[node].update({'linkRoute': link_routes})

    return confs


def generate_listeners(graph, node, nbrdict, node_type):
    """
    Function for generate information about listeners.
    Generate default or self-defined values.
    :param graph: networkx graph of topology
    :param node: current processing node
    :param nbrdict: list of neighbors
    :param node_type: type of nodes
    :return: listeners variables in json
    """
    list_vars = nx.get_node_attributes(graph, 'listener')

    listeners = []
    neighbours = []

    port = DEFAULT_PORT

    if node in list_vars:
        if isinstance(list_vars[node], list):
            listeners = list_vars[node]
        else:
            listeners = [list_vars[node]]
    if node not in nx.get_node_attributes(graph, 'def_list') or listeners == []:
        listeners.append(
            {
                'host': '0.0.0.0',
                'port': str(port),
                'role': 'normal',
                'authenticatePeer': 'no',
                'saslMechanisms': 'ANONYMOUS'
            }
        )
        port += 1
        for out in nbrdict.keys():
            if node_type[out] == 'router':
                listeners.append(
                    {
                        'host': '0.0.0.0',
                        'port': str(port),
                        'role': 'inter-router',
                        'authenticatePeer': 'no',
                        'saslMechanisms': 'ANONYMOUS'
                    }
                )
                port += 1
                break

        for out in nbrdict.keys():
            if node_type[out] == 'broker':
                listeners.append(
                    {
                        'host': '0.0.0.0',
                        'port': str(port),
                        'role': 'route-container',
                        'authenticatePeer': 'no',
                        'saslMechanisms': 'ANONYMOUS'
                    }
                )
                port += 1
                break

    # nx.set_node_attributes(graph, 'listener', 'test' )

    graph.add_node(node, listener=listeners)

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

    if node in conn_vars:
        if node in link_vars:
            for confs in conn_vars[node]:
                if isinstance(confs, dict):
                    for route in link_vars[node]:
                        if confs.get('name') == route['connection']:
                            link_route.append(route)
                            connectors = conn_vars[node]

        if not connectors:
            connectors = append_defined_component(conn_vars, node)

    if node not in nx.get_node_attributes(graph, 'def_conn'):
        # outgoing
        for out in nbrdict.keys():
            if node_type[out] == 'router':
                connectors.append({
                    'name': out,
                    'host': out,
                    'port': get_neighbor_port(graph, out),  # same rule as above
                    'role': 'inter-router'
                })
            elif node_type[out] == 'broker':
                connectors.append({
                    'name': out,
                    'host': out,
                    'port': str(DEFAULT_PORT),  # same rule as above
                    'role': 'route-container'
                })
                link_route.append({
                    'prefix': node + '_queue',
                    'connection': out,
                    'dir': 'in'
                })
                link_route.append({
                    'prefix': node + '_queue',
                    'connection': out,
                    'dir': 'out'
                })

    graph.add_node(node, connectors=connectors)
    graph.add_node(node, linkRoutes=link_route)

    return connectors, link_route


def generate_router_info(graph, node, nbrdict, node_type):
    """
    Function for generate information about router itself.
    :param graph: networkx graph of topology
    :param node: current processing node
    :param nbrdict: list of neighbors
    :param node_type: type of nodes
    :return: router variables in json
    """
    router = {}
    mode = 'standalone'
    rout_vars = nx.get_node_attributes(graph, 'router')

    if node in rout_vars:
        router = rout_vars[node][0]
    else:
        for out in nbrdict.keys():
            if node_type[out] == 'router' or node_type[out] == 'broker':
                mode = 'interior'
                break
        router['mode'] = mode

    # Add router ID
    router['id'] = node

    # Create complete router info
    router_info = {
        'machine': node,
        'router': [
            router
        ]
    }

    graph.add_node(node, router=router_info)

    return router_info


def generate_addresses(graph, node, nbrdict, node_type):
    """
    Function for generate information about addresses.
    Generate default or self-defined values.
    :param graph: networkx graph of topology
    :param node: current processing node
    :param nbrdict: list of neighbors
    :param node_type: type of nodes
    :return: listeners variables in json
    """
    address_vars = nx.get_node_attributes(graph, 'address')

    address = []
    neighbours = []

    if node in address_vars:
        address = append_defined_component(address_vars, node)
    if node not in nx.get_node_attributes(graph, 'def_addr') or address == []:
        item = {'prefix': 'closest', 'distribution': 'closest'}

        if item not in address:
            address.append(item)

        item = {'prefix': 'multicast', 'distribution': 'multicast'}
        if item not in address:
            address.append(item)

        item = {'prefix': 'unicast', 'distribution': 'closest'}
        if item not in address:
            address.append(item)

        item = {'prefix': 'exclusive', 'distribution': 'closest'}
        if item not in address:
            address.append(item)

        item = {'prefix': 'broadcast', 'distribution': 'multicast'}
        if item not in address:
            address.append(item)

    graph.add_node(node, addresses=address)
    return address


def generate_connection_settings(graph, node):
    """
    Function for parse other dispatch options such as sslProfile, etc.
    :param graph: networkx graph of topology
    :param node: current processing node
    :return:
    """
    conn_sett = {}
    component_sett = {}
    node_attributes = graph.node[node]
    if isinstance(node_attributes, dict):
        for component, attributes in node_attributes.items():
            if isinstance(attributes, list) and attributes \
                    and component not in ['listener', 'address', 'connector',
                                          'linkRoute',
                                          'router']:
                for attr_name, attr_value in attributes[0].items():
                    component_sett[attr_name] = attr_value

                conn_sett[component] = [component_sett]
                component_sett = {}

    return conn_sett


def get_neighbor_port(graph, neighbor):
    """
    Function for get port for connector according neighbor listener port.
    :param graph: graph
    :param neighbor: neighbor name
    :return: port number
    """
    test = graph.nodes(data=True)[neighbor]

    try:
        if 'listener' in test:
            for item in test['listener']:

                if 'role' in item:

                    if 'inter-route' in item['role']:
                        return item['port']

                else:
                    raise AttributeError
    except AttributeError:
        raise AttributeError("Listener doesn't contains role!")


def append_defined_component(component, node):
    """
    Function for append components defined by user from graph metadata.
    :param component: component list
    :param node: node name
    :return: list specific components for specific node
    """
    if isinstance(component[node], list):
        return component[node]
    else:
        return [component[node]]
