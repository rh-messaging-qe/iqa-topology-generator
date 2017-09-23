#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

from arg_parser import Config
from generate import get_conf
from topology import Topology

GEN_PATH = 'generated'


def main():
    config = Config()
    config.args_parse()

    # New instance of topology
    topology = Topology()
    # Create graph by defined input
    if config.graph_file:
        topology.load_graph_from_json(config.graph_file)
    else:
        topology.create_graph(config.router_names, config.broker_names, config.graph_type)
    # Generate variables
    configs = get_conf(topology.graph)

    # output
    basename = "%s_R%s_B%s" % (config.graph_type, config.routers, config.brokers)
    directory = os.path.join(GEN_PATH, basename)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, "confs.json")
    # Export graph
    topology.export_graph(os.path.join(directory, "topology.svg"), basename, config.graph_type)
    # Export variables
    with open(filename, 'w') as f:
        f.write(json.dumps({'confs': configs.values()}))
