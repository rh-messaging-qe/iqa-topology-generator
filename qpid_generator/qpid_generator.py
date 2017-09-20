#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

from arg_parser import Config
from generate import get_conf
from topology import Topology

GEN_PATH = 'generated'

config = Config()
config.args_parse()

# inputs
graph_type = 'complete_graph'
args = [config.routers]
machines = config.machines

print "Router: " + str(config.router_names)
print "Broker: " + str(config.broker_names)

# New instance of topology
topology = Topology()

if config.graph_file:
    topology.load_graph_from_json(config.graph_file)
else:
    topology.create_graph(config.router_names, config.broker_names, config.graph_type)

confs = get_conf(topology.graph)


def main():
    # output
    params = "-".join([str(x) for x in args])
    basename = "%s_%s_on_%s" % (graph_type, params, config.machines)
    directory = os.path.join(GEN_PATH, basename)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, "confs.json")
    # Export graph
    topology.export_graph(os.path.join(directory, "topology.svg"))
    # Export variables
    with open(filename, 'w') as f:
        f.write(json.dumps({'confs': confs.values()}))
