#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

from arg_parser import Config
from load_graph import export_graph, load_graph_from_json
from generate import get_conf

GEN_PATH = 'generated'

config = Config()
config.args_parse()

# inputs
graph_type = 'complete_graph'
args = [config.routers]
machines = config.machines


graph = load_graph_from_json(config.graph_file)

load_graph_from_json(config.graph_file)
# export_graph(graph)

machines = ["machine%s" % m for m in range(machines)]

# @TODO - generate topology without graph_file
# confs = get_conf(graph, machines, round_robin)


confs = get_conf(graph)

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