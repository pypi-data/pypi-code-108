"""
Command line application for working with ONTAP REST APIs
"""

# pylint: disable=no-name-in-module,bad-continuation

from getpass import getpass
import sys

try:
    import cliche  # type: ignore
    from cliche.commands import ClicheCommandError  # type: ignore
except ImportError:
    print(
        "The cliche library is required to run the CLI. Use 'pip install netapp-ontap[cli]'"
        " or 'pip install cliche' to get it."
    )
    sys.exit(1)

from netapp_ontap import config, HostConnection, NetAppRestError
from netapp_ontap.resources import Cluster  # type: ignore


def main():
    """Main entry point to run the CLI"""

    @cliche.command(atstart=True)
    def connect(  # pylint: disable=unused-variable
        host: str,
        username: str,
        password: str = None,
        verify_ssl: bool = False
    ) -> None:
        """Connect to the Cluster or SVM specified by hostname or ip address.

        Args:
            host: The name (usually a DNS hostname or IP address) where the ONTAP
                system lives. All commands after this will be directed to this cluster
                until a new connection is made.
            username: The login username for the cluster (or SVM)
            password: The password for the cluster or SVM user
        """

        if password is None:
            password = getpass()

        config.CONNECTION = HostConnection(
            host, username=username, password=password, verify=verify_ssl,
        )

        # try to verify the connection
        cluster = Cluster()
        try:
            cluster.get(fields="version")
        except NetAppRestError:
            config.CONNECTION = None
            raise ClicheCommandError(
                "Unable to connect to the Cluster or SVM with the given credentials"
            )

    cliche.run(program_name="netapp_ontap", history_file=".netapp_ontap_history")


if __name__ == "__main__":
    main()
