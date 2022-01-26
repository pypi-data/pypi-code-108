import json
import subprocess
from dataclasses import dataclass
from itertools import chain
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.validation import Validator
from returns.result import safe
from rich import inspect
from rich.console import Console


@dataclass
class PublicIpAddress:
    ipAddress: str
    name: str
    resourceGroup: str


@dataclass
class Network:
    privateIpAddresses: Optional[List[str]]
    publicIpAddresses: Optional[List[PublicIpAddress]]


@dataclass
class VirtualMachine:
    name: str
    network: Network
    resourceGroup: str


@dataclass
class VirtualMachineEntry(DataClassJsonMixin):
    virtualMachine: VirtualMachine


@safe(exceptions=(KeyboardInterrupt,))  # type: ignore # KeyboardInterrupt(BaseException)
def public_ip_safe(command: Optional[List[str]] = None) -> int:
    if command is None:
        command = ["az", "vm", "list-ip-addresses", "--output", "json"]

    console = Console(stderr=True)
    with console.status("Collecting IP addresses from all VMs using Azure CLI"):
        completed_process = subprocess.run(
            args=command,
            text=True,
            capture_output=True,
        )
        if completed_process.returncode != 0:
            inspect(
                completed_process,
                console=console,
                title="Command failed",
                docs=False,
                value=False,
            )
            return 1

    all_virtual_machines: List[VirtualMachineEntry] = [
        VirtualMachineEntry.from_dict(entry)
        for entry in json.loads(completed_process.stdout)
    ]

    all_ip_addresses = list(
        chain.from_iterable(
            public_ip_addresses
            for entry in all_virtual_machines
            if (public_ip_addresses := entry.virtualMachine.network.publicIpAddresses)
            is not None
        )
    )

    console.log(
        f"Found {len(all_virtual_machines)} virtual machines, and {len(all_ip_addresses)} public ip addresses"
    )

    name_to_ip_address = {
        ip_address.name: ip_address for ip_address in all_ip_addresses
    }

    if (discarded := len(all_ip_addresses) - len(name_to_ip_address)) != 0:
        console.log(
            f"{discarded} ip addresses have the same name, and have been discarded"
        )

    def get_matching_vm_names(ip_address: PublicIpAddress) -> List[str]:
        return [
            entry.virtualMachine.name
            for entry in all_virtual_machines
            if (public_ip_addresses := entry.virtualMachine.network.publicIpAddresses)
            is not None
            and ip_address in public_ip_addresses
        ]

    helptext = {
        name: FormattedText(
            [
                ("", "Resource group: "),
                ("bold", ip_address.resourceGroup),
                ("", ", VMs: "),
                ("bold", " ".join(get_matching_vm_names(ip_address))),
            ]
        )
        for name, ip_address in name_to_ip_address.items()
    }

    try:
        selected_name = prompt(
            message="Select an IP address: ",
            completer=FuzzyCompleter(
                WordCompleter(
                    sorted(helptext.keys()),
                    sentence=True,
                    match_middle=True,
                    meta_dict=helptext,
                )
            ),
            validator=Validator.from_callable(
                lambda s: s in helptext.keys(),
                error_message="You must select from one of the suggestions",
            ),
            complete_while_typing=True,
        )
    except KeyboardInterrupt:
        return 1

    selected_ip_address = name_to_ip_address[selected_name]
    inspect(
        selected_ip_address,
        console=console,
        value=False,
        docs=False,
        title="Selection",
    )
    print(selected_ip_address.ipAddress)

    return 0


def public_ip(command: Optional[List[str]] = None) -> int:
    return public_ip_safe(command=command).value_or(1)
