#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse

import yaml
from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager


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
        self.path_inventory = '~/inventory'
        self.machines = 2
        self.routers = 1
        self.brokers = 1
        self.router_names = []
        self.broker_names = []


    def args_parse(self):
        """
        Method for check command-line arguments and parse config files:
                config for this package
                inventory with hosts
        :return: self
        """

        # parse arguments
        parser = argparse.ArgumentParser(description='Qpid-dispatch facts generator.')
        required = parser.add_argument_group('required arguments')
        required.add_argument('-c', '--config-file', action="store", dest="config_file", help='Path to config file',
                              required=True)
        results = parser.parse_args()

        with open(results.config_file, 'r') as stream:
            try:
                config = yaml.load(stream)
                if 'hostfile' in config:    # @TODO - create error function for unset inventory path
                    self.path_inventory = config['hostfile']
                if 'graph_type' in config:
                    self.graph_file = config['graph_type']
            except yaml.YAMLError as exc:
                print(exc)

        with open(self.path_inventory, 'r') as f:
            try:
                read_data = f.read()
            except IOError as exc:
                print(exc)
        f.closed

        self.parse_inventory(self.path_inventory)

        self.routers = len(self.router_names)
        self.brokers = len(self.broker_names)
        self.machines = self.routers + self.brokers


    def parse_inventory(self, filename):
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

        variable_manager = VariableManager()
        loader = DataLoader()

        # Ansible: Load inventory
        inventory = Inventory(
            loader=loader,
            variable_manager=variable_manager,
            host_list=filename,  # Substitute your filename here
        )

        for host in inventory.get_hosts():
            groups_of_hosts = map(str, inventory.groups_for_host(str(host)))
            if 'routers' in groups_of_hosts:
                self.router_names.append(str(host))
            elif 'brokers' in groups_of_hosts:
                self.broker_names.append(str(host))
