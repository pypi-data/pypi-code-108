from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import socket
import desert
from marshmallow import Schema
from socket import SocketKind

import psutil
import typer
from edr_agent_validator.activity import Activity, ActivityType


class NetworkProtocol(Enum):
    UDP = "udp"
    TCP = "tcp"


@dataclass
class NetworkActivity(Activity):
    data_sent_length_bytes: int
    data_sent_protocol: SocketKind
    dest_addr: str
    dest_port: int
    source_addr: str
    source_port: int


schema: Schema = desert.schema(NetworkActivity)


def send_data(
    local_host: str,
    local_port: int,
    dest_host: str,
    dest_port: int,
    protocol: NetworkProtocol,
    data: str,
):
    connect_protocol: SocketKind = SocketKind.SOCK_STREAM
    match protocol:
        case NetworkProtocol.UDP:
            connect_protocol = SocketKind.SOCK_DGRAM
        case NetworkProtocol.TCP:
            connect_protocol = SocketKind.SOCK_STREAM

    with socket.socket(socket.AF_INET, connect_protocol) as s:
        try:
            s.bind((local_host, local_port))
            s.settimeout(3.0)
            s.connect((dest_host, dest_port))
        except OSError as e:
            typer.echo(f"Error opening connection: {e}")
            raise typer.Exit(1) from e

        s.sendall(data.encode())

    proc = psutil.Process()
    return NetworkActivity(
        datetime.utcnow(),
        proc.username(),
        proc.name(),
        proc.cmdline(),
        proc.pid,
        ActivityType.NETWORK_ACTIVITY,
        len(data.encode()),
        connect_protocol,
        dest_host,
        dest_port,
        local_host,
        local_port,
    )
