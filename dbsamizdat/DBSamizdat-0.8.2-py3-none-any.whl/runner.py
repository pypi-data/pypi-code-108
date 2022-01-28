import argparse
import sys
from time import monotonic
from logging import getLogger
from enum import Enum

import psycopg2

from .libdb import dbinfo_to_class, dbstate_equals_definedstate, get_dbstate, DBObjectType
from .libgraph import depsort_with_sidekicks, node_dump, sanity_check, subtree_depends
from .graphvizdot import dot
from .loader import get_samizdats
from . import entitypes
from .exceptions import SamizdatException, DatabaseError, FunctionSignatureError
from .util import fqify_node, nodenamefmt, sqlfmt


class txstyle(Enum):
    CHECKPOINT = 'checkpoint'
    JUMBO = 'jumbo'
    DRYRUN = 'dryrun'


logger = getLogger(__name__)
PRINTKWARGS = dict(file=sys.stderr, flush=True)


def timer():
    last = monotonic()
    while True:
        cur = monotonic()
        yield (cur - last)
        last = cur


def vprint(args: argparse.Namespace, *pargs, **pkwargs):
    if args.log_rather_than_print:
        logger.info(' '.join(map(str, pargs)))
    elif args.verbosity:
        print(*pargs, **{**PRINTKWARGS, **pkwargs})


def vvprint(args: argparse.Namespace, *pargs, **pkwargs):
    if args.log_rather_than_print:
        logger.debug(' '.join(map(str, pargs)))
    elif args.verbosity > 1:
        print(*pargs, **{**PRINTKWARGS, **pkwargs})


def get_cursor(args):
    cursor = None
    if args.in_django:
        from django.db import connections
        cursor = connections[args.dbconn].cursor().cursor
    else:
        cursor = psycopg2.connect(args.dburl).cursor()
    cursor.execute('BEGIN;')  # And so it begins…
    return cursor


def txi_finalize(cursor, args):
    do_what = {txstyle.JUMBO.value: 'COMMIT;', txstyle.DRYRUN.value: 'ROLLBACK;'}.get(args.txdiscipline)
    if do_what:
        cursor.execute(do_what)


def cmd_refresh(args):
    cursor = get_cursor(args)
    samizdats = depsort_with_sidekicks(sanity_check(get_samizdats(args.samizdatmodules)))
    matviews = [sd for sd in samizdats if sd.entity_type == entitypes.MATVIEW]

    if args.belownodes:
        rootnodes = {fqify_node(rootnode) for rootnode in args.belownodes}
        allnodes = node_dump(samizdats)
        if rootnodes - allnodes:
            raise ValueError('''Unknown rootnodes:\n\t- %s''' % '\n\t- '.join([nodenamefmt(rootnode) for rootnode in rootnodes - allnodes]))
        subtree_bundle = subtree_depends(samizdats, rootnodes)
        matviews = [sd for sd in matviews if sd in subtree_bundle]

    max_namelen = max(len(str(ds)) for ds in matviews)

    def refreshes():
        for sd in matviews:
            yield 'refresh', sd, sd.refresh(concurrent_allowed=True)
    executor(refreshes(), args, cursor, max_namelen=max_namelen, timing=True)
    txi_finalize(cursor, args)


def cmd_sync(args):
    cursor = get_cursor(args)
    samizdats = depsort_with_sidekicks(sanity_check(get_samizdats(args.samizdatmodules)))
    issame, excess_dbstate, excess_definedstate = dbstate_equals_definedstate(cursor, samizdats)
    if issame:
        vprint(args, "No differences, nothing to do.")
        return
    max_namelen = max(len(str(ds)) for ds in excess_dbstate | excess_definedstate)
    if excess_dbstate:
        def drops():
            for sd in excess_dbstate:
                yield 'drop', sd, sd.drop(if_exists=True)  # we don't know the deptree; so they may have vanished through a cascading drop of a previous object
        executor(drops(), args, cursor, max_namelen=max_namelen, timing=True)
        issame, excess_dbstate, excess_definedstate = dbstate_equals_definedstate(cursor, samizdats)  # again, we don't know the in-db deptree, so we need to re-read DB state as the rug may have been pulled out from under us with cascading drops
    if excess_definedstate:
        def creates():
            to_create_ids = {sd.head_id() for sd in excess_definedstate}
            for sd in samizdats:  # iterate in proper creation order
                if sd.head_id() in to_create_ids:
                    yield 'create', sd, sd.create()
                    yield 'sign', sd, sd.sign(cursor)
        executor(creates(), args, cursor, max_namelen=max_namelen, timing=True)

        matviews_to_refresh = {sd.head_id() for sd in excess_definedstate if sd.entity_type == entitypes.MATVIEW}
        if matviews_to_refresh:
            def refreshes():
                for sd in samizdats:  # iterate in proper creation order
                    if sd.head_id() in matviews_to_refresh:
                        yield 'refresh', sd, sd.refresh(concurrent_allowed=False)
            executor(refreshes(), args, cursor, max_namelen=max_namelen, timing=True)
    txi_finalize(cursor, args)


def cmd_diff(args):
    cursor = get_cursor(args)
    samizdats = depsort_with_sidekicks(sanity_check(get_samizdats(args.samizdatmodules)))
    issame, excess_dbstate, excess_definedstate = dbstate_equals_definedstate(cursor, samizdats)
    if issame:
        vprint(args, "No differences.")
        exit(0)

    max_namelen = max(len(str(ds)) for ds in excess_dbstate | excess_definedstate)

    def statefmt(state, prefix):
        return '\n'.join(f'%s%-17s\t%-{max_namelen}s\t%s' % (prefix, sd.entity_type.value, sd, sd.definition_hash()) for sd in sorted(state, key=lambda sd: str(sd)))
    if excess_dbstate:
        vprint(args, statefmt(excess_dbstate, 'Not in samizdats:\t'), file=sys.stdout)
    if excess_definedstate:
        vprint(args, statefmt(excess_definedstate, 'Not in database:   \t'), file=sys.stdout)
    exit(100 + (1 if excess_dbstate else 0 | 2 if excess_definedstate else 0))


def cmd_printdot(args):
    print('\n'.join(dot(depsort_with_sidekicks(sanity_check(get_samizdats(args.samizdatmodules))))))


def cmd_nuke(args, samizdats=None):
    cursor = get_cursor(args)

    def nukes():
        nonlocal samizdats
        if samizdats is None:
            samizdats = map(dbinfo_to_class, filter(lambda a: a[-1] is not None, get_dbstate(cursor)))
        for sd in samizdats:
            yield ("nuke", sd, sd.drop(if_exists=True))

    executor(nukes(), args, cursor)
    txi_finalize(cursor, args)


def executor(yielder, args, cursor, max_namelen=0, timing=False):

    action_timer = timer()

    def progressprint(ix, action_totake, sd, sql):
        if args.verbosity:
            if ix:
                # print the processing time of the *previous* action
                vprint(args, '%.2fs' % next(action_timer) if timing else '')
            vprint(args, f'%-7s %-17s %-{max_namelen}s ...' % (action_totake, sd.entity_type.value, sd), end='')
            vvprint(args, f'\n\n{sqlfmt(sql)}\n\n')

    action_cnt = 0
    for ix, progress in enumerate(yielder):
        action_cnt += 1
        progressprint(ix, *progress)
        action_totake, sd, sql = progress
        try:
            try:
                cursor.execute("BEGIN;")  # harmless if already in a tx
                cursor.execute(f"SAVEPOINT action_{action_totake};")
                cursor.execute(sql)
            except psycopg2.errors.UndefinedFunction as ouch:
                if action_totake == 'sign':
                    cursor.execute(f"ROLLBACK TO SAVEPOINT action_{action_totake};")  # get back to a non-error state
                    candidate_args = [c[3] for c in get_dbstate(cursor, which=DBObjectType.FOREIGN, entity_types=(entitypes.FUNCTION,)) if c[:2] == (sd.schema, sd.function_name)]
                    raise FunctionSignatureError(sd, candidate_args)
                raise ouch
        except psycopg2.Error as dberr:
            raise DatabaseError(f"{action_totake} failed", dberr, sd, sql)
        cursor.execute(f'RELEASE SAVEPOINT action_{action_totake};')
        if args.txdiscipline == txstyle.CHECKPOINT.value and action_totake != 'create':
            # only commit *after* signing, otherwise if later the signing somehow fails we'll have created an orphan DB object that we don't recognize as ours
            cursor.execute("COMMIT;")

    if action_cnt:
        vprint(args, '%.2fs' % next(action_timer) if timing else '')


def augment_argument_parser(p, in_django=False, log_rather_than_print=True):

    def perhaps_add_modules_argument(parser):
        if not in_django:
            parser.add_argument('samizdatmodules', nargs='+', help="Names of modules containing Samizdat subclasses")

    def add_dbarg_argument(parser):
        if in_django:
            parser.add_argument('dbconn', nargs='?', default='default', help="Django DB connection key (default:'default'). If you don't know what this is, then you don't need it.")
        else:
            parser.add_argument('dburl', help="PostgreSQL DB connection string. Trivially, this might be 'postgresql:///mydbname'. See https://www.postgresql.org/docs/14/static/libpq-connect.html#id-1.7.3.8.3.6 .")

    def add_txdiscipline_argument(parser):
        parser.add_argument('--txdiscipline', '-t', choices=(txstyle.CHECKPOINT.value, txstyle.JUMBO.value, txstyle.DRYRUN.value), default=txstyle.CHECKPOINT.value, help=f"""Transaction discipline. The "{txstyle.CHECKPOINT.value}" level commits after every dbsamizdat-level action. The safe default of "{txstyle.JUMBO.value}" creates one large transaction. "{txstyle.DRYRUN.value}" also creates one large transaction, but rolls it back.""")

    p.set_defaults(
        **dict(
            func=lambda whatevs: p.print_help(),
            in_django=in_django,
            log_rather_than_print=log_rather_than_print,
            samizdatmodules=[],
            verbosity=1,
        )
    )
    if not in_django:
        p.add_argument('--quiet', '-q', help="Be quiet (minimal output)", action="store_const", const=0, dest='verbosity')
        p.add_argument('--verbose', '-v', help="Be verbose (on stderr).", action="store_const", const=2, dest='verbosity')
    else:
        p.add_argument('-v', '--verbosity', default=1, type=int)
    subparsers = p.add_subparsers(title='commands')

    p_nuke = subparsers.add_parser('nuke', help='Drop all dbsamizdat database objects.')
    p_nuke.set_defaults(func=cmd_nuke)
    add_txdiscipline_argument(p_nuke)
    add_dbarg_argument(p_nuke)

    p_printdot = subparsers.add_parser('printdot', help='Print DB object dependency tree in GraphViz format.')
    p_printdot.set_defaults(func=cmd_printdot)
    perhaps_add_modules_argument(p_printdot)

    p_diff = subparsers.add_parser('diff', help='Show differences between dbsamizdat state and database state. Exits nonzero if any are found: 101 when there are excess DB-side objects, 102 if there are excess python-side objects, 103 if both sides have excess objects.')
    p_diff.set_defaults(func=cmd_diff)
    add_dbarg_argument(p_diff)
    perhaps_add_modules_argument(p_diff)

    p_refresh = subparsers.add_parser('refresh', help='Refresh materialized views, in dependency order')
    p_refresh.set_defaults(func=cmd_refresh)
    add_txdiscipline_argument(p_refresh)
    add_dbarg_argument(p_refresh)
    perhaps_add_modules_argument(p_refresh)
    p_refresh.add_argument('--belownodes', '-b', nargs='*', help="Limit to views that depend on ENTITYNAMES (usually, specific tables)", metavar='ENTITYNAMES')

    p_sync = subparsers.add_parser('sync', help='Make it so!')
    p_sync.set_defaults(func=cmd_sync)
    add_txdiscipline_argument(p_sync)
    add_dbarg_argument(p_sync)
    perhaps_add_modules_argument(p_sync)


def main():
    p = argparse.ArgumentParser(description='dbsamizdat, the blissfully naive PostgreSQL database object manager.')
    augment_argument_parser(p, log_rather_than_print=False)
    args = p.parse_args()
    try:
        args.func(args)
    except SamizdatException as argh:
        exit(f'\n\n\nFATAL: {argh}')
    except KeyboardInterrupt:
        exit('\nInterrupted.')


if __name__ == '__main__':
    main()
