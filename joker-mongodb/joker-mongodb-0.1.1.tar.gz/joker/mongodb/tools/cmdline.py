#!/usr/bin/env python3
# coding: utf-8

import argparse


class ArgumentParserMongoish(argparse.ArgumentParser):
    def add_argument_mongoi_host(self):
        self.add_argument('-H', '--host', help='host as in MongoInterface')

    def add_arguments_host_port(self, hostname='127.0.0.1'):
        add = self.add_argument
        add('-H', '--hostname', default=hostname, help='hostname')
        add('-p', '--port', type=int, default=27017, help='port number')

    def add_argument_db_name(self):
        self.add_argument('-d', '--db-name', help='database name')

    def add_argument_coll_name(self):
        self.add_argument('-c', '--coll-name', help='collection name')
