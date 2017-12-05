#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import shlex
import sys

import yaml


# @TODO - create package from this function
def parse_inventory(filename):
    """
    Function for parse inventory file for ansible into JSON format.
    :param filename: path to inventory file
    :return: JSON struct with parsed inventory
    """
    data = {}
    group = None
    state = None

    try:
        inventory = open(filename)
    except Exception as e:
        msg('E', 'Cannot open inventory file %s. %s' % (filename, str(e)))

    # Walk through the file and build the data structure
    for line in inventory:
        line = line.strip()

        # Skip comments and blank lines
        if line.startswith('#') or line.startswith(';') or len(line) == 0:
            continue

        if line.startswith('['):
            # Get group name
            section = line[1:-1]

            # Parse subsection
            if ':' in line:
                group, state = line[1:-1].split(':')
            else:
                group = section
                state = 'hosts'

            if group not in data:
                data[group] = {}

            if state not in data[group]:
                if 'children' not in state:
                    data[group][state] = {}
                else:
                    data[group][state] = []
        else:
            # Parse hosts or group members/vars
            try:
                tokens = shlex.split(line, comments=True)
            except ValueError as e:
                msg('E', "Error parsing host definition '%s': %s" % (line, e))

            # Create 'all' group if no group was defined yet
            if group is None:
                group = 'all'
                state = 'hosts'
                data['all'] = {
                    'hosts': []
                }

            # Get parsed hostname
            hostname = tokens[0]

            # Parse variables
            variables = []
            if state == 'hosts':
                variables = tokens[1:]
            elif state == 'vars':
                variables = tokens

            if 'hosts' in state:
                data[group][state].update({hostname: {}})

            if 'children' in state:
                data[group][state].append(hostname)

            for var in variables:
                if '=' not in var:
                    msg(
                        'E',
                        "Expected key=value host variable assignment, "
                        "got: %s" % var)

                (key, val) = var.split('=', 1)

                if 'hosts' in state:
                    data[group][state][hostname].update({key: val})
                if 'vars' in state:
                    data[group][state].update({key: val})
    # Close file
    try:
        inventory.close()
    except IOError as e:
        msg('E', 'Cannot close inventory file %s. %s' % (filename, str(e)))

    return data


def msg(_type, text, exit=0):
    """
    Function for report exception error.
    :param _type: exception
    :param text: exit text
    :param exit: exit number
    :return:
    """
    sys.stderr.write("%s: %s\n" % (_type, text))
    sys.exit(exit)


class Config:
    """
    Class for create object with all necessary config values:
            path to graph file
            path to inventory
            number of machines
            number of routers/brokers
            list of names for routers/brokers
    """

    def __init__(self):
        self.graph_file = ''
        self.graph_type = 'user_defined'
        self.path_inventory = ''
        self.machines = 2
        self.routers = 1
        self.brokers = 1
        self.router_names = []
        self.broker_names = []
        self.out_dir = ""

    def args_parse(self):
        """
        Method for check command-line arguments and parse config files:
                config for this package
                inventory with hosts
        :return: self
        """

        # parse arguments
        parser = argparse.ArgumentParser(description='Qpid-dispatch facts generator.')
        parser.add_argument('-o', '--output-dir', action="store", dest="out_dir", help='Path to output dir',
                            required=False)
        required = parser.add_argument_group('required arguments')
        required.add_argument('-c', '--config-file', action="store", dest="config_file", help='Path to config file',
                              required=True)
        results = parser.parse_args()

        with open(results.config_file, 'r') as stream:
            try:
                config = yaml.load(stream)
                if 'hostfile' in config:
                    self.path_inventory = config['hostfile']
                else:
                    self.path_inventory = input("Enter path to inventory: ")
                if 'graph_file' in config:
                    self.graph_file = config['graph_file']
                elif 'graph_type' in config:
                    self.graph_type = config['graph_type']
                else:
                    self.graph_type = input("Enter graph type for generator: ")
            except yaml.YAMLError as exc:
                print(exc)

        self.get_hosts(self.path_inventory)
        self.routers = len(self.router_names)
        self.brokers = len(self.broker_names)
        self.machines = self.routers + self.brokers
        self.out_dir = results.out_dir if results.out_dir else "/tmp/generated/"

        if self.routers <= 0:
            raise Exception(
                "You're trying to create topology without router and this is useless.\nPlease check documentation on https://github.com/rh-messaging-qe/iqa-topology-generator .")

    def get_hosts(self, filename):
        """
        Method for parsing inventory with hosts.
        It's able to parse any amount of groups.
        For proper functionality of this package, inventory has to have groups [routers] and [brokers] like this:

                [routers:children]
                group1
                group2
                router4

                [group1]
                router1

                [group2]
                router2
                router3

        Same for example is for brokers.
        Using Python API 2.0 for parse inventory.
        :param filename: path to inventory file
        :return: self
        """

        data = parse_inventory(filename)

        for host in data['routers']['hosts']:
            self.router_names.append(str(host))
        for host in data['brokers']['hosts']:
            self.broker_names.append(str(host))
