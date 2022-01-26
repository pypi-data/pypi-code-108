import sys
import argparse
import json
from echome import Session
from echome.network import Network
from .base_service import BaseService
from .defaults import APP_NAME

class NetworkService(BaseService):

    description = "Create and manage virtual networks."

    def __init__(self):
        self.parent_service = "network"
        self.parent_full_name = "Network"

        self.table_headers = ["Name", "Network Id", "Type", "CIDR"]
        self.data_columns=["name", "network_id", "type", "cidr"]

        self.extra_table_headers = ["Interface", "DNS Servers"] 
        self.extra_data_columns = [["config", "bridge_interface"], ["config", "dns_servers"]]

        self.session = Session()
        self.client:Network = self.session.client("Network")

        self.parent_service_argparse()


    def describe(self):
        parser = argparse.ArgumentParser(description='Describe a virtual network', prog=f"{APP_NAME} {self.parent_service} describe")
        parser.add_argument('network_id',  help='Network Id', metavar="<network-id>")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        parser.add_argument(*self.wide_flag_args, **self.wide_flags_kwargs)
        args = parser.parse_args(sys.argv[3:])

        networks = self.client.describe_network(args.network_id)
        networks = networks['results']
        if args.output == "table":
            i=0
            for network in networks:
                networks[i]["cidr"] = f"{network['config']['network']}/{network['config']['prefix']}"
                networks[i]["dns_servers"] = ",".join(network['config']['dns_servers'])
                i += 1
            self.print_table(networks, wide=args.wide)
        elif args.output == "json":
            print(json.dumps(networks, indent=4))
        
        #TODO: Return exit value if command does not work
        exit()
    

    def describe_all(self):
        parser = argparse.ArgumentParser(description='Describe all virtual networks', prog=f"{APP_NAME} {self.parent_service} describe-all")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        parser.add_argument('--wide', '-w', help='More descriptive output when in Table view', action='store_true', default=False)
        args = parser.parse_args(sys.argv[3:])

        networks = self.client.describe_all_networks()
        networks = networks['results']
        i=0
        for network in networks:
            networks[i]["cidr"] = f"{network['config']['network']}/{network['config']['prefix']}"
            i += 1
        # if args.output == "table":
        #     i=0
        #     for network in networks:
        #         networks[i]["cidr"] = f"{network['config']['network']}/{network['config']['prefix']}"
        #         i += 1
        #     self.print_table(networks, wide=args.wide)
        # elif args.output == "json":
        #     print(json.dumps(networks, indent=4))

        self.print_output(networks, args.output, wide=args.wide)
        
        #TODO: Return exit value if command does not work
        exit()
