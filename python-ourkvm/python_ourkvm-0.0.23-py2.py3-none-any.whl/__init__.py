"""
Our KVM solution, clulstered and self hosted
"""
import json
import sys
from argparse import ArgumentParser
from .lib.helpers.exceptions import (
	RequirementError,
	NamespaceError,
	NamespaceNotFound,
	UnsupportedHardware,
	InterfaceNotFound,
	ResourceNotFound,
	ResourceError,
	ConfigurationError,
	InterfaceError,
	SysCallError
)
from .storage import storage
from .lib.helpers.dupedict import DupeDict, JSON
from .lib.helpers.paths import secure_filename

__author__ = 'Anton Hvornum'
__version__ = '0.0.23'
__description__ = "Our KVM solution, clulstered and self hosted"

# TODO: https://stackoverflow.com/questions/15889621/sphinx-how-to-exclude-imports-in-automodule

# Parse arguments early, so that following imports can
# gain access to the arguments without parsing on their own.
parser = ArgumentParser()
# API arguments
parser.add_argument("--api", default=False, action="store_true", help="Enable API functionality")
parser.add_argument("--auth-server", default="127.0.0.1", nargs="?", help="Which authentication server to use", type=str)
parser.add_argument("--auth-realm", default="home", nargs="?", help="Which authentication realm to use", type=str)
parser.add_argument("--auth-schema", default="Keycloak", nargs="?", help="Which authentication realm to use", type=str)

# Cluster arguments
parser.add_argument("--cluster", default=False, action="store_true", help="Enable API functionality")
parser.add_argument("--cluster-addr", default="127.0.0.1", nargs="?", help="Which address to listen on, set to '' (empty) to listen on all addresses.", type=str)
parser.add_argument("--cluster-port", default=8050, nargs="?", help="Which port to listen on for cluster communication.", type=int)
parser.add_argument("--cluster-nodes", default="[]", nargs="?", help="A JSON list of known nodes (node sharing will occur, so one is minimum to enable) using the format: [{\"ip\": port}, {\"ip\": port}]", type=str)

# KVM helper arguments for creating machines
parser.add_argument("--machine-name", default="", nargs="?", help="Creates a new virtual machine with the given name", type=str)
parser.add_argument("--cpu", default="host", nargs="?", help="Which CPU type/parameters to give the new machine", type=str)
parser.add_argument("--bios", default=False, action="store_true", help="Disables UEFI and enables legacy BIOS for the machine")
parser.add_argument("--memory", default=8192, nargs="?", help="Defines the amount of memory to allocate to the new machine", type=str)
parser.add_argument("--harddrives", default=None, nargs="?", help="A comma-separated list of harddrives using the format 'image.qcow2:10G[,image2.qcow2:40G]'", type=str)
parser.add_argument("--cdroms", default=None, nargs="?", help="A comma-separated list of ISO/cdrom images using the format 'image.iso[,image2.iso]'", type=str)
parser.add_argument("--no-namespace", default=False, action="store_true", help="This will disable namespace-creation for the machine and by default for network intrastructure")
parser.add_argument("--graphics", default=False, action="store_true", help="This will turn on default graphics output (gtk) for qemu, the oposit of headless (default)")
parser.add_argument("--namespace", default=None, nargs="?", help="Tells --machine-name or --new-netdev which namespace the machine or interface should be in.", type=str)
parser.add_argument("--network", default=None, nargs="?", help="Defaults to using NAT. The syntax is a bit complex, refer to the man pages for information.", type=str)
parser.add_argument("--uefi-vars", default='/usr/share/ovmf/x64/OVMF_VARS.fd', nargs="?", help="Defines the path to the EFI variables (defaults to using find -iname for the vars)", type=str)
parser.add_argument("--uefi-code", default='/usr/share/ovmf/x64/OVMF_CODE.fd', nargs="?", help="Defines the path to the EFI code (defaults to using find -iname for the code)", type=str)
parser.add_argument("--service", default=None, nargs="?", help="Tells ourkvm to create a service script for the newly created machine at the given location. For instance --service ./machine.service", type=str)
parser.add_argument("--depends-on", default="", nargs="?", help="A list of comma separated systemd service names that this machine is dependent on. Will create After= declarations in the .service file.")
parser.add_argument("--config", default='/etc/qemu.d', nargs="?", help="Tells ourkvm where to store the environment configuration for the newly created machine. Default is /etc/qemu.d/", type=str)
parser.add_argument("--force", default=False, action="store_true", help="Will overwrite any existing service file or images")
parser.add_argument("--stop", default=False, action="store_true", help="Will gracefully stop the given machine if it's running (a helper flag for usage with systemd)")
parser.add_argument("--qemu-string", nargs="?", default="", help="Takes a path of a ourkvm .cfg and converts it to a qemu string that can be executed.")
parser.add_argument("--debug", default=False, action="store_true", help="Turns out an excessive ammount of output and logs every command to {storage['LOG_PATH']}/cmd_history.txt")
parser.add_argument("--serial", default=None, nargs="?", help="Will redirect monitor and stdio serial device to a unix socket and a log-file for easier log analytics")
parser.add_argument("--bring-online", nargs="?", default="", help="Takes a path of a ourkvm .cfg and takes any post boot network interfaces online (tap interfaces).")
parser.add_argument("--graceful-shutdown", nargs="?", default=30, help="Sets the grace period in seconds before a forceful shutdown is done with --stop", type=int)
parser.add_argument("--add-netdev", nargs="?", default=None, help="Adds a netdev interface to a running or turned off virtual machine", type=str)
parser.add_argument("--nocreate", default=False, action="store_true", help="Disables creation of the new --add-netdev interface. Defaults to create it.")
parser.add_argument("--network-id", nargs="?", default=None, help="Adds optional network id to --add-netdev interface. Defaults to current-ids+1", type=str)
parser.add_argument("--mac", nargs="?", default=None, help="Adds optional MAC address to new --add-netdev. Defaults to auto-generated one.", type=str)
parser.add_argument("--bridge", nargs="?", default=None, help="Adds optional bridge attachment to the new --add-netdev. Defaults to None.", type=str)
parser.add_argument("--snapshot", default=False, action="store_true", help="Snapshots a --machine-name and all of it's resources (running or hybernated)")
parser.add_argument("--norecurse", default=False, action="store_true", help="Blocks --snapshot from recursing down in to namespaces (used internally mainly)")

# ourkvm agent arguments
parser.add_argument("--report-health", default=False, action="store_true", help="Reports this machines health to the --health-server")
parser.add_argument("--health-schema", default="http", nargs="?", help="Which server to report health status to", type=str)
parser.add_argument("--health-server", default="127.0.0.1", nargs="?", help="Which server to report health status to", type=str)
parser.add_argument("--health-port", default=8000, nargs="?", help="Which port to connect to the health server on", type=int)
parser.add_argument("--health-base-url", default="", nargs="?", help="(optional) base URL of the API in case it's behind a proxy", type=str)
parser.add_argument("--health-token", default=None, nargs="?", help="(optional) access token that allows this agent to report it's data", type=str)

# Store the arguments in a "global" storage variable
args, unknowns = parser.parse_known_args()
storage['arguments'] = args
storage['arguments'].cluster_nodes = json.loads(storage['arguments'].cluster_nodes)

# Expose API calls for when the user does `import ourkvm`:
if args.api or 'sphinx' in sys.modules:
	from .api import app, User, process_user_claim, get_current_user_information, list_all_known_cluster_nodes

from .lib.helpers.logger import log
from .lib.helpers.syscalls import SysCommand, SysCommandWorker
from .lib.networking import (
	load_network_info,
	get_interface_info,
	get_namespace_info,
	del_namespace,
	add_namespace,
	ip,
	generate_mac,
	get_all_mac_addresses_in_use,
	get_namespaces,
	curate_interfaces,
	ifup,
	InterfaceStruct,
	NamespaceStruct
)
from .lib.qemu import (
	qemu_img,
	create_qemu_string,
	verify_qemu_resources,
	write_qemu_service_file,
	get_machine_disk_information,
	get_diskimage_information,
	get_harddrives,
	get_machine_status,
	QMP
)
from .lib.qemu.environment import (
	load_environment,
	dismantle_environment,
	load_conf,
	load_network_cards_from_env,
	get_network_cards_from_env,
	get_network_card_info_from_env
)
from .lib.qemu.snapshots import take_snapshot

# --dluster-nodes implicitly enables --cluster
if storage['arguments'].cluster_nodes:
	args.cluster = True

if args.cluster or 'sphinx' in sys.modules:
	from .cluster import SimplifiedServerSocket as SimplifiedServerSocket
	from .cluster import ClusterServer as ClusterServer

	if 'sphinx' not in sys.modules:
		cluster = ClusterServer()
		cluster.listen()

		while True:
			for fileno, data in cluster.recv():
				cluster.process(fileno, data)