"""Command-line options for the backend module."""
import argparse
from typing import Optional

from demessaging.config import ModuleConfig

UNKNOWN_TOPIC = "__NOTSET"
UNKNOWN_MODULE = "__NOTSET"


def get_parser(
    module_name: str = "__main__", config: Optional[ModuleConfig] = None
) -> argparse.ArgumentParser:
    """Generate the command line parser."""
    if config is None:
        config = ModuleConfig(topic=UNKNOWN_TOPIC)

    conf_dict = config.dict()

    parser = argparse.ArgumentParser()

    add = parser.add_argument

    def desc(name):
        field = ModuleConfig.__fields__[name]
        desc = field.field_info.description or ""
        if field.default:
            desc += " Default: %(default)s"
        return desc

    topic_help = desc("topic")
    if config.topic == UNKNOWN_TOPIC:
        topic_help += " This option is required!"
    else:
        topic_help += " Default: %(default)s"

    add(
        "-t",
        "--topic",
        help=topic_help,
        required=config.topic == UNKNOWN_TOPIC,
        default=conf_dict["topic"],
    )

    module_help = "Name of the backend module."
    if module_name == UNKNOWN_MODULE:
        module_help += " This option is required!"
    else:
        module_help += " Default: %(default)s"

    add(
        "-m",
        "--module",
        default=module_name,
        required=module_name == UNKNOWN_MODULE,
        dest="module_name",
        help=module_help,
    )

    add(
        "-d",
        "--description",
        help=desc("doc"),
        default=conf_dict["doc"],
        dest="doc",
    )

    add("-H", "--host", help=desc("host"), default=conf_dict["host"])

    add("-p", "--port", help=desc("port"), default=conf_dict["port"])

    add(
        "--persistent",
        help=desc("persistent"),
        default=conf_dict["persistent"],
    )

    add("--tenant", help=desc("tenant"), default=conf_dict["tenant"])

    add("--namespace", help=desc("namespace"), default=conf_dict["namespace"])

    add(
        "--max_workers",
        help=desc("max_workers"),
        default=conf_dict["max_workers"],
    )

    add(
        "--queue_size",
        help=desc("queue_size"),
        default=conf_dict["queue_size"],
    )

    add(
        "--members",
        help=desc("members"),
        nargs="+",
        metavar="member",
        default=conf_dict["members"],
    )

    # ----------------------------- Subparsers --------------------------------
    subparsers = parser.add_subparsers(dest="command", title="Commands")

    # subparser for testing the connection
    sp = subparsers.add_parser(
        "test-connect",
        help="Connect the backend module to the pulsar message handler.",
    )
    sp.set_defaults(method_name="test_connect")

    # connect subparser (to connect to the pulsar messaging system)
    subparsers.add_parser(
        "listen",
        help="Connect the backend module to the pulsar message handler.",
    )

    # schema subparser (to print the module schema)
    sp = subparsers.add_parser(
        "schema", help="Print the schema for the backend module."
    )
    sp.add_argument("-i", "--indent", help="Indent the JSON dump.", type=int)
    sp.set_defaults(method_name="schema_json", command_params=["indent"])

    # test subparser (to test the connection to the connect to the pulsar
    # messaging system)
    sp = subparsers.add_parser(
        "send-request", help="Test a request via the pulsar messaging system."
    )
    sp.add_argument(
        "request",
        help="A JSON-formatted file with the request.",
        type=argparse.FileType("r"),
    )
    sp.set_defaults(method_name="send_request", command_params=["request"])

    # shell parser. This parser opens a shell to work with the generated Model
    subparsers.add_parser(
        "shell",
        help="Start an IPython shell",
        description=(
            "This command starts an IPython shell where you can access and "
            "work with the generated pydantic Model. This model class is "
            "available via the ``Model`` variable in the shell."
        ),
    )

    # generate parser. This parser renders the backend module and generates a
    # *frontend* API
    sp = subparsers.add_parser(
        "generate",
        help="Generate an API module",
        description=(
            "This command generates an API module that connects to the "
            "backend module via the pulsar and can be used on the client side."
            " We use isort and black to format the generated python file."
        ),
    )

    sp.add_argument(
        "-l",
        "--line-length",
        default=79,
        type=int,
        help=("The line-length for the output API. " "Default: %(default)s"),
    )

    sp.add_argument(
        "--no-formatters",
        action="store_false",
        dest="use_formatters",
        help=(
            "Do not use any formatters (isort, black or autoflake) for the "
            " generated code."
        ),
    )

    sp.add_argument(
        "--no-isort",
        action="store_false",
        dest="use_isort",
        help="Do not use isort for formatting.",
    )

    sp.add_argument(
        "--no-black",
        action="store_false",
        dest="use_black",
        help="Do not use black for formatting.",
    )

    sp.add_argument(
        "--no-autoflake",
        action="store_false",
        dest="use_autoflake",
        help="Do not use autoflake for formatting.",
    )

    sp.set_defaults(
        command_params=[
            "line_length",
            "use_formatters",
            "use_autoflake",
            "use_black",
            "use_isort",
        ]
    )

    return parser


if __name__ == "__main__":
    parser = get_parser()
    parser.parse_args()
