# Messaging topology generator (msg_topgen)

Package for generatate/load topology defined by graph/hosts. Also generate global variables for topology.

## Build/Test Status
[![Build Status](https://travis-ci.org/rh-messaging-qe/iqa-topology-generator.svg?branch=master)](https://travis-ci.org/rh-messaging-qe/iqa-topology-generator)

## Configs
`config` dir contains two type of files:

- inventory (hosts with IP addresses and hostnames)
- graph.yml (graph of topology in yml format)

Root dir contains file `config.yml` with following informations:
- hostfile: configs/inventory

and one of these:
- graph_type: line_graph
- graph_file: configs/ref_graph_file.yml

Use `--help` for more information.

## Requirements
None

## Run
```bash
$ make
```

## Tests

### Requirements
[tox](https://tox.readthedocs.io/en/latest/)

### How to run tests
```bash
$ tox
```

## License
Apache 2.0

## Author Information
Messaging QE team @ redhat.com