from __future__ import division, absolute_import, print_function

import sys
import argparse
import textwrap

from yams_cli.utils import get_version

MAIN_DESCRIPTION = '''YAMS CLI\nhttps://yams.mpi-internal.com\n#yams @ Slack'''

# Common arguments
distribution_id = {
    'args': ['--distribution-id'],
    'required': True,
    'help': "ID of the distribution (UUIDv4)",
}
domain_id = {
    'args': ['--domain-id'],
    'required': True,
    'help': "ID of the domain (UUIDv4)",
}
bucket_id = {
    'args': ['--bucket-id'],
    'required': True,
    'help': "ID of the bucket (UUIDv4)",
}
bucket_alias = {
    'args': ['--bucket-alias'],
    'required': True,
    'help': "bucket alias (instead of --domain-id and --bucket-id)",
}
object_id = {
    'args': ['--object-id'],
    'required': True,
    'help': "ID of the object (UUIDv4)",
}
processing_id = {
    'args': ['--processing-id'],
    'required': True,
    'help': "ID of the processing job"
}
policy_id = {
    'args': ['--policy-id'],
    'required': True,
    'help': "ID of the policy (UUIDv4 or alias)",
}
rule_id_or_alias = {
    'args': ['--rule-id'],
    'required': True,
    'help': "ID of the rule (UUIDv4 or alias)",
}

rule_id = {
    'args': ['--rule-id'],
    'required': True,
    'help': "ID of the rule (UUIDv4)",
}

rule_json = {
    'args': ['--rule-json'],
    'required': True,
    'help': "rule definition in JSON format",
}
expiration = {
    'args': ['--expiration'],
    'metavar': 'TIMESTAMP',
    'help': "date, expressed as seconds after the epoch, in which the object will be removed",
}


class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, *args, **kwargs):
        super(CustomHelpFormatter, self).__init__(*args, **kwargs)
        self._width = 1024

    def _fill_text(self, text, width, indent):
        return textwrap.fill(
            text,
            width,
            initial_indent=indent,
            subsequent_indent=indent,
            replace_whitespace=False,
        )


class CustomArgParser(argparse.ArgumentParser):
    def add_subcommands(self, dest, subcommands):
        subparsers = self.add_subparsers(title='actions', required=True, dest=dest, metavar='COMMAND')

        commands = {}
        for command, help_msg, example in subcommands:
            description = help_msg
            if example is not None:
                description += '\n\nexample:\n  %(prog)s ' + example

            commands[command] = subparsers.add_parser(
                command,
                help=help_msg,
                description=description,
                formatter_class=CustomHelpFormatter,
            )

        return commands

    def error(self, message):
        sys.stderr.write('error: {}\n\n'.format(message))
        self.print_help()
        sys.exit(2)


def add_argument_as_dict(self, options, **extras):
    '''Helper method to add arguments as dict templates'''
    kwargs = options.copy()
    args = kwargs.pop('args', [])
    kwargs.update(extras)
    self.add_argument(*args, **kwargs)


# Add helper to the libraries
CustomArgParser.add_argument_as_dict = add_argument_as_dict
argparse._MutuallyExclusiveGroup.add_argument_as_dict = add_argument_as_dict


def add_subcommands_to_description(command):
    if not command._subparsers:
        return

    command.description += '\n\n'
    for action, parser in command._subparsers._group_actions[0].choices.items():
        usage = parser.format_usage()[7:]
        command.description += usage


def add_yams_global_options(parser):
    parser.add_argument(
        '--version', action='version', version="%(prog)s {}".format(get_version()), help="show current version")
    parser.add_argument(
        '--debug', action='store_true', help="debug mode")
    parser.add_argument(
        '-a', '--api-version', default='api/v1', help="API version. Default: %(default)s")
    parser.add_argument(
        '-m', '--management-url', default='https://mgmt-yams.mpi-internal.com',
        help="management URL. Default: %(default)s"
    )
    parser.add_argument(
        '-f', '--fetch-url', default='https://fetch-yams.mpi-internal.com', help="fetch URL. Default: %(default)s")
    parser.add_argument(
        '-j', '--jwt-algorithm', default='RS512', help="JWT algorithm. Default: %(default)s")
    parser.add_argument(
        '-p', '--profile', default='yams-default',
        help="profile name as defined in ~/.yams/credentials. Default: %(default)s"
    )


def setup_yams_tenant(command):
    command.add_subcommands('action', [
        ('list', "list tenants (you need super admin credentials)", ""),
        ('info', "get tenant details", ""),
        ('delete', "delete tenant pointed by your profile", ""),
    ])


def setup_yams_distribution(command):
    commands = command.add_subcommands('action', [
        ('list', "list distributions", ""),
        ('info', "show info for a distribution",
            "--distribution-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca"),
        ('create', "create a distribution",
            "--dns-name my-subdomain.domain.com --auto-format false"),
        ('update', "update a distribution",
            "--distribution-id 9981f9ab-3e39-4472-b89b-825104822efa --auto-format true"),
        ('delete', "delete a distribution",
            "--distribution-id 9981f9ab-3e39-4472-b89b-825104822efa")
    ])

    commands['info'].add_argument_as_dict(distribution_id)
    commands['create'].add_argument('--dns-name', required=True, help="dns to use for the distribution")
    commands['create'].add_argument('--auto-format', required=False, default=False, help="Enable auto format (default: false)")

    commands['delete'].add_argument_as_dict(distribution_id)

    commands['update'].add_argument_as_dict(distribution_id)
    commands['update'].add_argument('--auto-format', required=False, default=None, help="Enable|Disable auto format. Do nothing if not set")

def setup_yams_domain(command):
    commands = command.add_subcommands('action', [
        ('list', "list domains", ""),
        ('info', "show info for a domain",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca"),
        ('create', "create a domain",
            "--domain-name documentation-cli"),
        ('delete', "delete a domain",
            "--domain-id 9981f9ab-3e39-4472-b89b-825104822efa"),
    ])

    commands['info'].add_argument_as_dict(domain_id)

    commands['create'].add_argument(
        '--domain-name', required=True, help="name of the domain")
    commands['create'].add_argument(
        '--domain-status', default='active', help="status of the domain. Default: %(default)s"
    )

    commands['delete'].add_argument_as_dict(domain_id)


def setup_yams_bucket(command):
    commands = command.add_subcommands('action', [
        ('list', "list buckets",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca"),
        ('info', "show info for a bucket",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c"),
        ('create', "create a bucket",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-name my-new-bucket"),
        ('update', "update a bucket",
            "--domain-id 562086c3-e4bf-4cd6-af13-e45d85575db5 --bucket-id c28e5c04-8b27-4ddb-8b64-d1cc3d689e2c" +
            " --bucket-statics true --bucket-cache-max-age 86400"),
        ('delete', "delete a bucket",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id ba094694-a7c6-4185-886b-b89e0075c2a2"),
    ])

    bucket_name = {
        'args': ['--bucket-name'],
        'required': True,
        'help': "name of the bucket",
    }
    bucket_statics = {
        'args': ['--bucket-statics'],
        'const': 'true',
        'nargs': '?',
        'help': "allow retrieval of static files without bucket credentials. Default: %(default)s",
    }
    bucket_cache_max_age = {
        'args': ['--bucket-cache-max-age'],
        'type': int,
        'help': "max age of cached value in seconds. Default: %(default)s (31 days)",
    }

    commands['list'].add_argument_as_dict(domain_id)

    commands['info'].add_argument_as_dict(domain_id)
    commands['info'].add_argument_as_dict(bucket_id)

    commands['create'].add_argument_as_dict(domain_id)
    commands['create'].add_argument_as_dict(bucket_name)
    commands['create'].add_argument(
        '--bucket-continent', default='europe', choices=["europe", "america"], help="AWS region of the bucket. Default: %(default)s")
    commands['create'].add_argument_as_dict(bucket_statics)
    commands['create'].add_argument_as_dict(bucket_cache_max_age)

    commands['update'].add_argument_as_dict(domain_id)
    commands['update'].add_argument_as_dict(bucket_id)
    commands['update'].add_argument_as_dict(bucket_name, required=False)
    commands['update'].add_argument_as_dict(bucket_statics)
    commands['update'].add_argument_as_dict(bucket_cache_max_age)

    commands['delete'].add_argument_as_dict(domain_id)
    commands['delete'].add_argument_as_dict(bucket_id)


def setup_yams_object(command):
    commands = command.add_subcommands('action', [
        ('list', "list objects in bucket",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c"),
        ('describe', "describes an object",
         "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
         " --object-id 31/31b02d22-6086-44dc-882d-74cbc3400ec6"),
        ('fetch', "fetch an object",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
            " --object-id 31/31b02d22-6086-44dc-882d-74cbc3400ec6 --directory /tmp"),
        ('push', "push an object",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
            " --object /tmp/file.jpg"),
        ('remove', "remove an object",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
            " --object-id 31/31b02d22-6086-44dc-882d-74cbc3400ec6"),
        ('restore', "restore a recently removed object (up to 1 month ago)",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
            " --object-id 31/31b02d22-6086-44dc-882d-74cbc3400ec6"),
        ('uncache', "YAMS managed cdn and caches invalidation",
         "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
         " --object-id some-object-id"),
    ])

    commands['list'].add_argument_as_dict(domain_id)
    commands['list'].add_argument_as_dict(bucket_id)
    commands['list'].add_argument('--long', action='store_true', help="long listing format")
    commands['list'].add_argument('--with-headers', action='store_true', help="print object field names")
    commands['list'].add_argument('--show-recoverable', action='store_true',
                                  help="the list will contain which objects has been deleted and are recoverable")
    commands['list'].add_argument('--list-backup', action='store_true',
                                  help="the list will contain objects from the backup bucket")
    commands['list'].add_argument('--start-date', help="Epoch in seconds timestamp of the starting date to list objects or Date in UTC 2021-01-27, 2021-01-27T10:00:00")
    commands['list'].add_argument('--end-date', help="Epoch in seconds timestamp of the ending date to list objects or Date in UTC 2021-01-27, 2021-01-27T10:00:00")
    commands['list'].add_argument(
        '--prefix', required=False, help="prefix to list objects from, Default: /")

    commands['fetch'].add_argument_as_dict(domain_id)
    commands['fetch'].add_argument_as_dict(bucket_id)
    commands['fetch'].add_argument_as_dict(object_id)
    commands['fetch'].add_argument(
        '--directory', default='./', help="directory to store the object. Default: %(default)s")

    commands['push'].add_argument_as_dict(domain_id)
    commands['push'].add_argument_as_dict(bucket_id)
    commands['push'].add_argument(
        '--object', required=True, metavar='OBJECT_FILE_OR_DIRECTORY',
        help="absolute path to the file or directory to upload"
    )
    group = commands['push'].add_mutually_exclusive_group(required=False)
    group.add_argument(
        '--recursive', action='store_true', help="upload all the files in a directory, recursively")
    group.add_argument(
        '--object-name', help="name of the object. Default: Object ID's UUIDv4")
    group.add_argument_as_dict(expiration)

    commands['remove'].add_argument_as_dict(domain_id)
    commands['remove'].add_argument_as_dict(bucket_id)
    commands['remove'].add_argument_as_dict(object_id)
    commands['remove'].add_argument(
        '--force', action='store_true', help="object will be completely removed (non recoverable)")

    commands['restore'].add_argument_as_dict(domain_id)
    commands['restore'].add_argument_as_dict(bucket_id)
    commands['restore'].add_argument_as_dict(object_id)

    commands['describe'].add_argument_as_dict(domain_id)
    commands['describe'].add_argument_as_dict(bucket_id)
    commands['describe'].add_argument_as_dict(object_id)

    commands['uncache'].add_argument_as_dict(domain_id)
    commands['uncache'].add_argument_as_dict(bucket_id)
    commands['uncache'].add_argument_as_dict(object_id)


def setup_yams_object_metadata(command):
    commands = command.add_subcommands('action', [
        ('info', "get object's metadata",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
            " --object-id 31/31b02d22-6086-44dc-882d-74cbc3400ec6"),
        ('update', "update object's metadata",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
            " --object-id 31/31b02d22-6086-44dc-882d-74cbc3400ec6 --expiration 1515769200"),

    ])

    commands['info'].add_argument_as_dict(domain_id)
    commands['info'].add_argument_as_dict(bucket_id)
    commands['info'].add_argument_as_dict(object_id)

    commands['update'].add_argument_as_dict(domain_id)
    commands['update'].add_argument_as_dict(bucket_id)
    commands['update'].add_argument_as_dict(object_id)
    commands['update'].add_argument_as_dict(expiration)


def setup_yams_image(command):
    commands = command.add_subcommands('action', [
        ('fetch', "get image applying a transformation rule",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
            " --object-id 51/51151eef-0f94-4e9a-b22c-5d6666546666 --rule-id 73cfa229-946b-4c3b-9b49-84b7eb358de0" +
            "\n  %(prog)s" +
            " --domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
            " --object-id 51/51151eef-0f94-4e9a-b22c-5d6666546666 --rule-json " +
            '\'{"format":"jpg","name":"my-rule-2","actions":' +
            '[{"resize":{"width":200,"fit":{"type":"clip"}}}],"version":"2017-06","quality":90}\'' +
             "\n  %(prog)s" +
             " --bucket-alias my-bucket-alias" +
             " --object-id 51/51151eef-0f94-4e9a-b22c-5d6666546666 --rule-id 73cfa229-946b-4c3b-9b49-84b7eb358de0" +
             "\n  %(prog)s" +
             " --bucket-alias my-bucket-alias" +
             " --object-id 51/51151eef-0f94-4e9a-b22c-5d6666546666 --rule-json " +
             '\'{"format":"jpg","name":"my-rule-2","actions":' +
             '[{"resize":{"width":200,"fit":{"type":"clip"}}}],"version":"2017-06","quality":90}\'' +
            "\n\nWhenever --bucket-alias is used, it will have precedence over --domain-id and --bucket-id (if present)."),
    ])

    commands['fetch'].add_argument_as_dict(domain_id, required=False)

    group_alias = commands['fetch'].add_mutually_exclusive_group(required=True)
    group_alias.add_argument_as_dict(bucket_id, required=False)
    group_alias.add_argument_as_dict(bucket_alias, required=False)

    commands['fetch'].add_argument_as_dict(object_id)

    group = commands['fetch'].add_mutually_exclusive_group(required=True)
    group.add_argument_as_dict(rule_id_or_alias, required=False)
    group.add_argument_as_dict(rule_json, required=False)


def setup_yams_document(command):
    commands = command.add_subcommands('action', [
        ('fetch', "get document applying a transformation rule",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
            " --object-id 51/51151eef-0f94-4e9a-b22c-5d6666546666 --rule-id 73cfa229-946b-4c3b-9b49-84b7eb358de0" +
            "\n  %(prog)s" +
            " --domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
            " --object-id 51/51151eef-0f94-4e9a-b22c-5d6666546666 --rule-json " +
            '\'{"format":"pdf", "version":"2018-08"}\'' +
             "\n  %(prog)s" +
             " --bucket-alias my-bucket-alias" +
             " --object-id 51/51151eef-0f94-4e9a-b22c-5d6666546666 --rule-id 73cfa229-946b-4c3b-9b49-84b7eb358de0"
             "\n  %(prog)s" +
             " --bucket-alias my-bucket-alias" +
             " --object-id 51/51151eef-0f94-4e9a-b22c-5d6666546666 --rule-json " +
             '\'{"format":"pdf", "version":"2018-08"}\'' +
             "\n\nWhenever --bucket-alias is used, it will have precedence over --domain-id and --bucket-id (if present).")
    ])

    commands['fetch'].add_argument_as_dict(domain_id, required=False)

    group_alias = commands['fetch'].add_mutually_exclusive_group(required=True)
    group_alias.add_argument_as_dict(bucket_id, required=False)
    group_alias.add_argument_as_dict(bucket_alias, required=False)

    commands['fetch'].add_argument_as_dict(object_id)

    group = commands['fetch'].add_mutually_exclusive_group(required=True)
    group.add_argument_as_dict(rule_id_or_alias, required=False)
    group.add_argument_as_dict(rule_json, required=False)


def setup_yams_static(command):
    commands = command.add_subcommands('action', [
        ('fetch', "get a stored media file",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
            " --object-id 51/51151eef-0f94-4e9a-b22c-5d6666546666" +
            "\n  %(prog)s" +
            " --bucket-alias my_bucket_alias --object-id 51/51151eef-0f94-4e9a-b22c-5d6666546666" +
            "\n\nWhenever --bucket-alias is used, it will have precedence over --domain-id and --bucket-id (if present)."
         ),
    ])
    commands['fetch'].add_argument_as_dict(domain_id, required=False)

    group = commands['fetch'].add_mutually_exclusive_group(required=True)
    group.add_argument_as_dict(bucket_id, required=False)
    group.add_argument_as_dict(bucket_alias, required=False)

    commands['fetch'].add_argument_as_dict(object_id)

def setup_yams_rule(command):
    commands = command.add_subcommands('action', [
        ('list', "list rules",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca"),
        ('info', "show info for a rule",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --rule-id 77cde1ac-8c21-4726-aa90-e9cfb31ac8d1"),
        ('create', "create a rule",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --rule-json " +
            '\'{"format":"jpg","name":"my-rule","actions"' +
            ':[{"resize":{"width":200,"fit":{"type":"clip"}}}],"version":"2017-06","quality":90}\''),
        ('update', "update a rule",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --rule-id 77cde1ac-8c21-4726-aa90-e9cfb31ac8d1"
            '--rule-json \'{"format":"jpg","name":"my-rule","description":"desc","actions"' +
            ':[{"resize":{"width":200,"fit":{"type":"clip"}}}],"version":"2017-06","quality":90}\''),
        ('delete', "delete a rule",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --rule-id 77cde1ac-8c21-4726-aa90-e9cfb31ac8d1"),
    ])

    commands['list'].add_argument_as_dict(domain_id)

    commands['info'].add_argument_as_dict(domain_id)
    commands['info'].add_argument_as_dict(rule_id)

    commands['create'].add_argument_as_dict(domain_id)
    commands['create'].add_argument_as_dict(rule_json)

    commands['update'].add_argument_as_dict(domain_id)
    commands['update'].add_argument_as_dict(rule_id)
    commands['update'].add_argument_as_dict(rule_json)

    commands['delete'].add_argument_as_dict(domain_id)
    commands['delete'].add_argument_as_dict(rule_id)


def setup_yams_accesskey(command):
    commands = command.add_subcommands('action', [
        ('list', "list access keys", ""),
        ('info', "show info for an access key",
            "--accesskey-id 9c366ba874a5f698"),
        ('create', "generate and upload access key", ""),
        ('provide', "upload an access key",
            "--public-key 4a5f69c366b6ba874..."),
        ('update', "update an access key",
            "--accesskey-id 9c366ba874a5f698 --enable"),
        ('delete', "revoke an access key",
            "--accesskey-id 73ac4943bfda18e5"),
        ('list-policies', "list policies attached to an access key",
            "--accesskey-id 73ac4943bfda18e5"),
        ('attach-policy', "attach policy to an access key",
            "--accesskey-id 9c366ba874a5f698 --policy-id 833f2746-7554-47d6-b337-43e1fb5cee61"),
        ('detach-policy', "detach policy from an access key",
            "--accesskey-id 9c366ba874a5f698 --policy-id 833f2746-7554-47d6-b337-43e1fb5cee61"),
    ])

    accesskey_id = {
        'args': ['--accesskey-id'],
        'required': True,
        'help': "ID of the access key (UUIDv4)",
    }
    description = {
        'args': ['--description'],
        'help': "access key description",
    }

    commands['info'].add_argument_as_dict(accesskey_id)

    commands['create'].add_argument_as_dict(description)

    commands['provide'].add_argument(
        '--public-key', required=True, help="public part of the access key")
    commands['provide'].add_argument_as_dict(description)

    commands['update'].add_argument_as_dict(accesskey_id)
    commands['update'].add_argument_as_dict(description)
    group = commands['update'].add_mutually_exclusive_group(required=False)
    group.add_argument(
        '--enable', action='store_true', help="enable access key")
    group.add_argument(
        '--disable', action='store_true', help="disable access key")

    commands['delete'].add_argument_as_dict(accesskey_id)

    commands['list-policies'].add_argument_as_dict(accesskey_id)

    commands['attach-policy'].add_argument_as_dict(accesskey_id)
    commands['attach-policy'].add_argument_as_dict(policy_id)

    commands['detach-policy'].add_argument_as_dict(accesskey_id)
    commands['detach-policy'].add_argument_as_dict(policy_id)


def setup_yams_policy(command):
    commands = command.add_subcommands('action', [
        ('list', "list policies", ""),
        ('info', "show info for a policy",
            "--policy-id default-admin"),
        ('create', "create a policy",
            '--policy-json \'{"alias":"my-policy","policy":{"statements":[{"actions":["yams:*:*"],"effect":"Allow"' +
            ',"resources":["yams:30f0d95a-8eca-4637-85e0-79b08b4be45a:domain:6fe01664-47a0-41db-be82-7120ea503dca"]}]' +
            ',"version":"2017-04-04"}}\''),
        ('update', "update a policy",
            '--policy-id my-policy --policy-json \'{"alias":"my-policy","policy":{"statements":[{"actions":' +
            '["yams:*:*"],"effect":"Allow","resources":["yams:30f0d95a-8eca-4637-85e0-79b08b4be45a:domain:*"]}]' +
            ',"version":"2017-04-04"}}\''),
        ('delete', "delete a policy",
            "--policy-id my-policy"),
    ])

    policy_json = {
        'args': ['--policy-json'],
        'required': True,
        'help': "policy definition in JSON format",
    }

    commands['info'].add_argument_as_dict(policy_id)

    commands['create'].add_argument_as_dict(policy_json)

    commands['update'].add_argument_as_dict(policy_id)
    commands['update'].add_argument_as_dict(policy_json)

    commands['delete'].add_argument_as_dict(policy_id)


def setup_yams_watermark(command):
    commands = command.add_subcommands('action', [
        ('list', "list watermarks",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca"),
        ('fetch', "download a watermark",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --watermark-id 71e20289-c0d9-487b-86ee-87829e97afef" +
            " --store-file"),
        ('create', "create a watermark",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --watermark-file /tmp/file.jpg --alias my-alias"),
        ('update', "update a watermark",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --watermark-id 71e20289-c0d9-487b-86ee-87829e97afefi" +
            " --alias new-alias"),
        ('delete', "delete a watermark",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --watermark-id 71e20289-c0d9-487b-86ee-87829e97afef"),
    ])

    watermark_id = {
        'args': ['--watermark-id'],
        'required': True,
        'help': "ID of the watermark (UUIDv4)",
    }
    watermark_file = {
        'args': ['--watermark-file'],
        'required': True,
        'help': "absolute path to watermark",
    }
    alias = {
        'args': ['--alias'],
        'help': "watermark alias",
    }

    commands['list'].add_argument_as_dict(domain_id)

    commands['fetch'].add_argument_as_dict(domain_id)
    commands['fetch'].add_argument_as_dict(watermark_id)
    commands['fetch'].add_argument(
        '--store-file', action='store_true', help="store the watermark file in /tmp")
    commands['fetch'].add_argument_as_dict(watermark_file, required=False)

    commands['create'].add_argument_as_dict(domain_id)
    commands['create'].add_argument_as_dict(watermark_file)
    commands['create'].add_argument_as_dict(alias)

    commands['update'].add_argument_as_dict(domain_id)
    commands['update'].add_argument_as_dict(watermark_id)
    commands['update'].add_argument_as_dict(alias)

    commands['delete'].add_argument_as_dict(domain_id)
    commands['delete'].add_argument_as_dict(watermark_id)


def setup_yams_metrics(command):
    commands = command.add_subcommands('action', [
        ('list', "show all available metric names",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c"),
        ('info', "show usage metrics (CDN, API requests, storage)",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c" +
            " --metric-name yams.metrics.s3.bucket.size --year-month 2017-06"),
    ])

    commands['list'].add_argument_as_dict(domain_id)
    commands['list'].add_argument_as_dict(bucket_id)

    commands['info'].add_argument_as_dict(domain_id)
    commands['info'].add_argument_as_dict(bucket_id)
    commands['info'].add_argument(
        '--metric-name', required=True, help="name of the metric")
    commands['info'].add_argument(
        '--year-month', required=True, help="year and month of the metrics. Format: YYYY-MM")


def setup_video_processing(command):
    commands = command.add_subcommands('action', [
        ('start', "start processing video to different codecs and resolutions",
         "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c " +
         "--object-id some-object-id"),
        ('status', "Get video processing job status",
         "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c " +
         "--processing-id some-processing-id")
    ])

    commands['start'].add_argument_as_dict(domain_id)
    commands['start'].add_argument_as_dict(bucket_id)
    commands['start'].add_argument_as_dict(object_id)

    commands['status'].add_argument_as_dict(domain_id)
    commands['status'].add_argument_as_dict(bucket_id)
    commands['status'].add_argument_as_dict(processing_id)


def setup_yams_processing(command):
    commands = command.add_subcommands('action', [
        ('sync', "sync processing",
         "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c " +
         "--object-id some-object-id --models background-removal-preview"),
        ('start', "start processing",
         "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c " +
         "--object-id some-object-id --models generic-car-plates")
    ])
    commands['sync'].add_argument_as_dict(domain_id)
    commands['sync'].add_argument_as_dict(bucket_id)
    commands['sync'].add_argument_as_dict(object_id)
    commands['sync'].add_argument('--models', required=True, help="models to apply, comma separated")

    commands['start'].add_argument_as_dict(domain_id)
    commands['start'].add_argument_as_dict(bucket_id)
    commands['start'].add_argument_as_dict(object_id)
    commands['start'].add_argument('--models', required=True, help="models to apply, comma separated")


def setup_yams_ml_models(command):
    commands = command.add_subcommands('action', [
        ('list', "list models ready to be used by this tenant", ""),
    ])


def setup_yams_ml_models_config(command):
    commands = command.add_subcommands('action', [
        ('list', "list all existing ml-model configurations for this tenant", ""),
        ('info', "show the details of the selected ml-model configuration",
         "--config-id car-plates-asUn34"),
        ('create', "create a new ml-model configuration for this tenant",
         "--config \"{'modelId': 'generic-car-plates'}\""),
        ('delete', "delete an existing ml-model configuration for this tenant",
         "--config-id car-plates-asUn34"),
        ('list-attached', "list attached configs to bucket",
         "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c"),
        ('attach', "attach an existing ml-model configuration to a bucket",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c " +
            "--config-id car-plates-asUn34"),
        ('detach', "detach an existing ml-model configuration from a bucket",
            "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c " +
            "--config-id car-plates-asUn34"),
        ('replace', "replace a configuration attached to the bucket with another configuration belonging to the same ml model",
         "--domain-id 5adcb26c-92fe-4f83-afb5-bf2322c0bfca --bucket-id 04760f77-da25-4de1-adde-bdfe62337c3c " +
         "--config-id-from car-plates-asUn34 --config-id-to car-plates-bdLu45"),
    ])

    ml_model_config_id = {
        'args': ['--config-id'],
        'required': True,
        'help': "ID of the ml model configuration",
    }

    ml_model_config = {
        'args': ['--config'],
        'required': True,
        'help': "model configuration as JSON string",
    }

    commands['info'].add_argument_as_dict(ml_model_config_id)

    commands['create'].add_argument_as_dict(ml_model_config)

    commands['delete'].add_argument_as_dict(ml_model_config_id)

    commands['list-attached'].add_argument_as_dict(domain_id)
    commands['list-attached'].add_argument_as_dict(bucket_id)

    commands['attach'].add_argument_as_dict(domain_id)
    commands['attach'].add_argument_as_dict(bucket_id)
    commands['attach'].add_argument_as_dict(ml_model_config_id)

    commands['detach'].add_argument_as_dict(domain_id)
    commands['detach'].add_argument_as_dict(bucket_id)
    commands['detach'].add_argument_as_dict(ml_model_config_id)

    commands['replace'].add_argument_as_dict(domain_id)
    commands['replace'].add_argument_as_dict(bucket_id)
    commands['replace'].add_argument_as_dict({
        'args': ['--config-id-from'],
        'required': True,
        'help': "ID of the ml model configuration to replace",
    })
    commands['replace'].add_argument_as_dict({
        'args': ['--config-id-to'],
        'required': True,
        'help': "ID of the ml model configuration to replace the existing one with",
    })


def setup_yams_help(command):
    command.add_argument(
        'help_command', nargs='?', metavar='COMMAND')

def parse_cli_arguments(argv=None):
    argv = sys.argv[1:] if not argv else argv
    parser = CustomArgParser(description=MAIN_DESCRIPTION, formatter_class=CustomHelpFormatter)

    add_yams_global_options(parser)

    # Replace help subcommand by --help at the end, makes it possible to use:
    # yams help, yams helps command, yams help command subcommand...
    if len(argv) > 0 and argv[0] == 'help':
        argv.pop(0)
        argv.append('--help')

    # Parse global options first so they can be placed anywhere, unless the --help/-h flag is set
    parsed_args, rest = None, argv
    if '-h' not in rest and '--help' not in rest:
        parsed_args, rest = parser.parse_known_args(rest)

    # Add commands
    commands = parser.add_subcommands('command', [
        ('configure', "create credential files", ""),
        ('tenant', "get tenant info or delete tenant", None),
        ('distribution', "list, create or delete distributions", None),
        ('domain', "list, create or delete domains", None),
        ('bucket', "list, create, update or delete buckets", None),
        ('object', "list, fetch, upload, delete, restore media files or uncache", None),
        ('object-metadata', "get or update object metadata", None),
        ('image', "get an image applying a transformation rule", None),
        ('document', "get a document applying a transformation rule", None),
        ('video-processing', "Process video features", None),
        ('static', "get the original-stored file", None),
        ('rule', "list, create, update or delete transformation rules", None),
        ('accesskey', "list, create, update, provide or revoke access keys. Also, attach or detach policies", None),
        ('policy', "list, create, update or delete policies", None),
        ('watermark', "list, fetch, create, update or delete watermarks", None),
        ('metrics', "show usage metrics", None),
        ('processing', "ML processing", None),
        ('ml-models', "list ml models ready to be used by this tenant", None),
        ('ml-models-config', "list, get info, create, update or delete tenant ml models configurations", None),
        ('help', "show this message", "bucket create"),
    ])

    setup_yams_tenant(commands['tenant'])
    setup_yams_distribution(commands['distribution'])
    setup_yams_domain(commands['domain'])
    setup_yams_bucket(commands['bucket'])
    setup_yams_object(commands['object'])
    setup_yams_object_metadata(commands['object-metadata'])
    setup_yams_image(commands['image'])
    setup_yams_document(commands['document'])
    setup_yams_static(commands['static'])
    setup_yams_rule(commands['rule'])
    setup_yams_accesskey(commands['accesskey'])
    setup_yams_policy(commands['policy'])
    setup_yams_watermark(commands['watermark'])
    setup_yams_metrics(commands['metrics'])
    setup_yams_processing(commands['processing'])
    setup_yams_ml_models(commands['ml-models'])
    setup_yams_ml_models_config(commands['ml-models-config'])
    setup_video_processing(commands['video-processing'])

    setup_yams_help(commands['help'])

    for command in commands.values():
        add_subcommands_to_description(command)

    # Finish parsing args
    parsed_args = parser.parse_args(rest, parsed_args)
    return parsed_args.__dict__
