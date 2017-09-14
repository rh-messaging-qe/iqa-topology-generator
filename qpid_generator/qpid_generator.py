#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

import networkx as nx

from distribute import round_robin
from configurations import get_conf
from arg_parser import Config
from load_graph import export_graph, load_graph_from_json
from generate import get_conf2

GEN_PATH = 'generated'

config = Config()
config.args_parse()

# inputs
graph_type = 'complete_graph'
args = [config.routers]
machines = config.machines

# graph = nx.Graph()
# graph.add_node('router1', type='router')
# graph.add_node('router2', type='router')
# graph.add_node('broker1', type='broker')
# graph.add_node('broker2', type='broker')
# graph.add_node('broker3', type='broker')
# graph.add_node('broker4', type='broker')
# graph.add_node('broker5', type='broker')
# graph.add_node('broker6', type='broker')
# graph.add_node('broker7', type='broker')
#
# graph.add_edge('router1', 'router2')
# graph.add_edge('router1', 'broker1')
# graph.add_edge('router2', 'broker2')
# graph.add_edge('router2', 'broker3')
# graph.add_edge('broker2', 'broker4')
# graph.add_edge('router2', 'broker5')
# graph.add_edge('broker5', 'broker6')
# graph.add_edge('broker6', 'broker7')


graph = load_graph_from_json(config.graph_file)
# export_graph(graph)

load_graph_from_json(config.graph_file)

machines = ["machine%s" % m for m in range(machines)]
# confs = get_conf(graph, machines, round_robin)


confs = get_conf2(graph)


def main():
    # output
    params = "-".join([str(x) for x in args])
    basename = "%s_%s_on_%s" % (graph_type, params, len(machines))
    directory = os.path.join(GEN_PATH, basename)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, "confs.json")
    with open(filename, 'w') as f:
        f.write(json.dumps({'confs': confs.values()}))

    print 'FINAL CONFS:'
    print json.dumps({'confs': confs.values()}, sort_keys=True, indent=2)