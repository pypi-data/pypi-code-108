__title__ = 'echome-cli'
__version__ = '0.3.0'
__author__ = 'Marcus Gutierrez'

import sys
import argparse
import logging
from identity import IdentityService
from keys import KeysService
from kube import KubeService
from network import NetworkService
from vm import VmService
from defaults import APP_NAME

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

services = {
    "vm": VmService,
    "keys": KeysService,
    "network": NetworkService,
    "identity": IdentityService,
    "kube": KubeService,
}

class ecHomeCli:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='ecHome CLI',
            usage=f'''{APP_NAME} [service] [command] [subcommands] <options>

The most commonly used ecHome service commands are:
   vm         Create and manage with ecHome virtual machines and images.
   keys       Create and manage SSH keys used for virtual machines.
   network    Create and manage virtual networks.
   kube       Create and manage Kubernetes clusters.
   identity   Create and manage User accounts, tokens, and policies.
''')
        parser.add_argument('service', help='Service to interact with')

        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])

        if args.service == "version":
            print(__version__)
            exit()

        if args.service not in services.keys():
            print('Unrecognized service')
            parser.print_help()
            exit(1)

        services[args.service]()


if __name__ == "__main__":
    ecHomeCli()
