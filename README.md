# Messaging topology generator (msg_topgen)

Package for generatate/load topology defined by graph/hosts. Also generate global variables for topology.

## Build/Test Status
[![Build Status](https://travis-ci.org/rh-messaging-qe/iqa-topology-generator.svg?branch=master)](https://travis-ci.org/rh-messaging-qe/iqa-topology-generator)
[![GitHub Issues](https://img.shields.io/github/issues/rh-messaging-qe/iqa-topology-generator.svg)](https://github.com/rh-messaging-qe/iqa-topology-generator/issues)
[![GitHub Issues](https://img.shields.io/github/issues-pr/rh-messaging-qe/iqa-topology-generator.svg)](https://github.com/rh-messaging-qe/iqa-topology-generator/pulls)
[![pypi](https://img.shields.io/pypi/v/msg_topgen.svg)](https://github.com/rh-messaging-qe/iqa-topology-generator)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


## Configs
`config` dir contains two type of files:

- inventory (hosts with IP addresses and hostnames)
- graph.yml (graph of topology in yml format)

Root dir contains file `config.yml` with following informations:
- hostfile: configs/inventory

and one of these:
- graph_type: line_graph
- graph_file: configs/ref_graph_file.yml

Default graph types values:

| Name              | Description          |
|-------------------|----------------------|
| `line_graph` | Routers/broker are in one line (routers are in the middle of line) |
| `line_mix_graph` | Routers/broker are in one line (brokers are interleaved by routers) |
| `complete_graph` | Each node is connected with all other nodes |
| `bus_graph` | Routers are in line ad brokers are evenly distributed to routers |
| `circle_graph` | Line_mix_graph with connected border nodes |

You can see an examples of config file in `config.yml` in root directory. Examples of graph file are in `tests/items`.

`--help` provide you more information.

## Requirements
Python >= 2.7

## Install & Run
```bash
$ pip install msg-topgen
```

```bash
$ msg_topgen -c <CONFIG_FILE_PATH>
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

Matthieu Simonin [(msimonin/qpid-dispatch-generator)](https://github.com/msimonin/qpid-dispatch-generator)
