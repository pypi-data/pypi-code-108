# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import argparse
import logging
import os
from pprint import PrettyPrinter

from arbiterd import dispatcher
from arbiterd.common import cpu
from arbiterd.common import libvirt
from arbiterd.common import nova
from arbiterd.objects import context
from arbiterd.objects import hardware_thread
from arbiterd.objects import instance

LOG = logging.getLogger(__name__)
PRINTER = PrettyPrinter()
pprint = PRINTER.pprint
pformat = PRINTER.pformat

DISPATCHER = None

# TODO: decide on output convention.
# currently normal out is reported with pprint but
# errors, warnings and debug info will be logged.
# The default logging config logs at warn level and above.
# The default handler of last resort writes to sys.stderr


def list_command(args):

    if args.available_cpus:
        pprint(f'Available CPUs: {cpu.get_available_cpus()}')
    elif args.online_cpus:
        pprint(f'Online CPUs: {cpu.get_online_cpus()}')
    elif args.offline_cpus:
        pprint(f'Offline CPUs: {cpu.get_offline_cpus()}')
    elif args.dedicated_cpus:
        pprint(f'Dedicated CPUs: {nova.get_dedicated_cpus(args.nova_config)}')
    elif args.shared_cpus:
        pprint(f'Shared CPUs: {nova.get_shared_cpus(args.nova_config)}')
    elif args.domains:
        libvirt.init_libvirt()
        domains = [
            (dom.name(), dom.UUIDString())
            for dom in libvirt.libvirt_obj.list_domains()
        ]
        pprint(f'Libvirt Domains: {domains}')
    elif args.nova_domains:
        libvirt.init_libvirt()
        instances = []
        for dom in libvirt.libvirt_obj.list_domains():
            inst = instance.Instance.from_domain(dom)
            if inst.is_nova_instance:
                instances.append((inst.name, inst.uuid))
        pprint(f'Libvirt Domains: {instances}')
    else:
        # TBD: add support for listing  vcpu_pin_set from nova.conf.
        # TODO: add summary view.
        # TODO: add support for displaying pinned cpus currenly in used by
        # VMs on the host.
        # TODO: add support for listing kernel and userspace isolated cpus
        LOG.error(pformat(f'list was called with unsupported agrs: {args}'))
        fail(args)


def show_command(args):
    try:
        if args.domain_by_name:
            libvirt.init_libvirt()
            obj = instance.Instance(name=args.domain_by_name)
            print(f'Libvirt Domains:\n{obj.xml_str}')
        elif args.domain_by_uuid:
            libvirt.init_libvirt()
            obj = instance.Instance(uuid=args.domain_by_uuid)
            print(f'Libvirt Domains:\n{obj.xml_str}')
        elif args.domain_affinity:
            libvirt.init_libvirt()
            obj = instance.Instance(name=args.domain_affinity)
            print(f'Libvirt Domains:\n{obj.cpu_affinities}')
        elif args.cpu_state is not None:
            path = cpu.gen_cpu_path(args.cpu_state)
            online = cpu.get_online(path)
            print('ONLINE' if online else 'OFFLINE')
        else:
            LOG.error(
                pformat(f'show was called with unsupported agrs: {args}'))
            fail(args)
    except ValueError as e:
        LOG.error(e)
        fail(args)


def set_command(args):
    try:
        if args.cpu_online is not None:
            path = cpu.gen_cpu_path(args.cpu_online)
            if not cpu.set_online(path):
                fail(args)
        elif args.cpu_offline is not None:
            path = cpu.gen_cpu_path(args.cpu_offline)
            if not cpu.set_offline(path):
                fail(args)
        else:
            LOG.error(
                pformat(f'show was called with unsupported agrs: {args}'))
    except ValueError as e:
        LOG.error(e)
        fail(args)


def arbitrate_command(args):
    try:
        ctx = context.Context()
        ctx.dry_run = not args.apply
        if args.cpu_state:
            ctx.managed_hardware_threads = [
                hardware_thread.HardwareThread(ident=core)
                for core in nova.get_dedicated_cpus(args.nova_config)
            ]
            ctx.instances = []
            libvirt.init_libvirt()
            for dom in libvirt.libvirt_obj.list_domains():
                inst = instance.Instance.from_domain(dom)
                if inst.is_nova_instance:
                    ctx.instances.append(inst)
            print(DISPATCHER.arbitrate('cpu-state', ctx))
        else:
            LOG.error(
                pformat(f'show was called with unsupported agrs: {args}'))
    except ValueError as e:
        LOG.error(e)
        fail(args)


def revoke_command(args):
    try:
        ctx = context.Context()
        ctx.dry_run = not args.apply
        if args.cpu_state:
            print(DISPATCHER.revoke('cpu-state', ctx))
        else:
            LOG.error(
                pformat(f'show was called with unsupported agrs: {args}'))
    except ValueError as e:
        LOG.error(e)
        fail(args)


def validate_gobal_configs(args):
    result = os.path.exists(args.nova_config)
    if not result:
        err = pformat(
            'Config validation is enabled but the nova config file cannot '
            'be found at {args.nova_config}. Pass --no-config to disable '
            'validation or --nova-config <path> if it exits at a non default '
            'location.'
        )
        LOG.error(err)
    return result


def fail(args, code=1):
    LOG.debug(f'Command Failed {args}')
    exit(code)


def run():

    parser = argparse.ArgumentParser(description='Static CPU Arbiter')

    parser.add_argument(
        '--nova-config', dest='nova_config',
        default='/etc/nova/nova.conf', help='Path to nova config.')
    parser.add_argument(
        '--no-config', dest='no_config', action='store_true', default=False,
        help='skip config loading')
    parser.add_argument(
        '--debug', dest='debug', action='store_true', default=False,
        help='enable debug_logging')

    sub_commands = parser.add_subparsers()

    list_parser = sub_commands.add_parser('list')
    list_group = list_parser.add_mutually_exclusive_group(required=True)
    list_group.add_argument('--available-cpus', action='store_true')
    list_group.add_argument('--online-cpus', action='store_true')
    list_group.add_argument('--offline-cpus', action='store_true')
    list_group.add_argument('--dedicated-cpus', action='store_true')
    list_group.add_argument('--shared-cpus', action='store_true')
    list_group.add_argument('--domains', action='store_true')
    list_group.add_argument('--nova-domains', action='store_true')
    list_parser.set_defaults(func=list_command)

    show_parser = sub_commands.add_parser('show')
    show_group = show_parser.add_mutually_exclusive_group(required=True)
    show_group.add_argument(
        '--domain-by-name', type=str, help='The libvirt instance name')
    show_group.add_argument(
        '--domain-by-uuid', type=str, help='The libvirt instance uuid')
    show_group.add_argument(
        '--domain-affinity', type=str,
        help='The cpu of the libvirt instance by name')
    show_group.add_argument(
        '--cpu-state', type=int, help='The online state of  cpu #',
        default=None
    )
    show_parser.set_defaults(func=show_command)

    set_parser = sub_commands.add_parser('set')
    set_group = set_parser.add_mutually_exclusive_group(required=True)
    set_group.add_argument(
        '--cpu-online', type=int, help='The online state of  cpu #',
        default=None
    )
    set_group.add_argument(
        '--cpu-offline', type=int, help='The online state of  cpu #',
        default=None
    )
    set_parser.set_defaults(func=set_command)

    arbitrate_parser = sub_commands.add_parser(
        'arbitrate', help=(
            'The arbitrte command will execute the selected arbiter '
            'In dry run mode by default unless --apply is specified.'
        ))
    arbitrate_group = arbitrate_parser.add_mutually_exclusive_group(
        required=True)
    arbitrate_group.add_argument(
        '--cpu-state', action='store_true', default=False,
        help='Automatically manage the cpu online state'
    )
    arbitrate_parser.add_argument(
        '--apply', action='store_true', default=False,
        help='apply the changes to the host.'
    )

    arbitrate_parser.set_defaults(func=arbitrate_command)
    revoke_parser = sub_commands.add_parser(
        'revoke', help=(
            'The revoke command will execute the selected arbiter '
            'In dry run mode by default unless --apply is specified.'
        ))

    revoke_group = revoke_parser.add_mutually_exclusive_group(required=True)
    revoke_group.add_argument(
        '--cpu-state', action='store_true', default=False,
        help='revoke management of the cpu online state'
    )
    revoke_parser.add_argument(
        '--apply', action='store_true', default=False,
        help='apply the changes to the host.'
    )
    revoke_parser.set_defaults(func=revoke_command)

    args = parser.parse_args()
    # TODO: support external log config.
    if args.debug:
        logging.basicConfig(
            format=(
                '%(asctime)s,%(msecs)d %(levelname)-8s '
                '[%(filename)s:%(lineno)d] %(message)s'
            ),
            datefmt='%Y-%m-%d:%H:%M:%S', level=logging.DEBUG)
    if not args.no_config and not validate_gobal_configs(args):
        return

    # we initalise DISPATCHER after parsing so we can account
    # for the --debug flag.
    # TODO move this to separate function
    global DISPATCHER
    DISPATCHER = dispatcher.Dispatcher()

    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()
