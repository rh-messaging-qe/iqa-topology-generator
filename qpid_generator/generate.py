#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import networkx as nx
import yaml

DEFAULT_PORT = 5672


def get_conf2(graph):
    confs = {}
    node_type = nx.get_node_attributes(graph, 'type')

    for node, nbrdict in graph.adjacency_iter():
        if node_type[node] == 'broker' or node_type[node] == 'router-global':
            continue
        # init
        confs.setdefault(node, {})
        # Generate router info
        confs[node].update(generate_router_info(graph, node))
        # Generate listeners
        confs[node].update({'listener': generate_listeners(graph, node)})
        # Generate connectors with link-routes
        connectors, link_routes = generate_connectors(graph, node, nbrdict, node_type)
        confs[node].update({'connector': connectors})
        if link_routes:
            confs[node].update({'linkRoute': link_routes})

    return confs


def generate_listeners(graph, node):
    list_vars = nx.get_node_attributes(graph, 'listener')

    listeners = []

    if node in list_vars:
        listeners = list_vars[node]
    else:
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
    conn_vars = nx.get_node_attributes(graph, 'connector')
    link_vars = nx.get_node_attributes(graph, 'linkRoute')
    if node in conn_vars:
        connectors = conn_vars[node]
        if node in link_vars:
            # TODO - check hosts in connector and linkRoute (should be equal)
            # if link_vars[node]['host'] == conn_vars[node]['host']:
            link_route = link_vars[node]
    else:
        # outgoing links
        connectors = []
        link_route = []
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
                link_route.append(
                    {
                        'prefix': 'TODO',
                        'connection': out,
                        'dir': 'in'
                    })
                link_route.append({
                    'prefix': 'TODO',
                    'connection': out,
                    'dir': 'out'
                })

    return connectors, link_route


def generate_router_info(graph, node):
    rout_vars = nx.get_node_attributes(graph, 'router')
    # router_id = node        # TODO - problem ve vasrs pro ansible (jedna masina, jeden router - vymyslet a vyzkouset moznosti pro vice routru na masine)
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

