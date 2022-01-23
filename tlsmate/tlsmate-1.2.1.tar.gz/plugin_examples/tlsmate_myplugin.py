from tlsmate.plugin import Worker, Plugin, Args, BaseCommand
from tlsmate import tls
from tlsmate.plugins.scan import ArgPort, ArgSni, ArgHost
from tlsmate.structs import ConfigItem


class CipherPrinterWorker(Worker):
    name = "cipher printer"
    descr = "executing a single handshake and print the negotiated cipher suite"
    prio = 100

    def run(self):
        # Let's use a default client profile which has a high probability to
        # successfully interoperate with a typical web server.
        self.client.set_profile(tls.Profile.INTEROPERABILITY)

        # Now open a TLS connection and execute a typical TLS handshake. Print the
        # cipher suite selected by the server.
        with self.client.create_connection() as conn:
            conn.handshake()
            print(f"{self.config.get('text')}: {conn.msg.server_hello.cipher_suite}")


class ArgText(Plugin):
    """Argument for the text
    """

    config = ConfigItem("text", type=str, default="cipher suite")
    cli_args = Args(
        "--text",
        help="the text used to print the negotiated cipher suite",
        default=None,
    )


@BaseCommand.extend
class SubcommandCipherPrinter(Plugin):
    subcommand = Args("cipher-printer", help="prints the negotiated cipher suite")
    plugins = [ArgPort, ArgSni, ArgText, ArgHost]
    workers = [CipherPrinterWorker]
