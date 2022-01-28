from argparse import Namespace

from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import pre_migrate, post_migrate
from django.db.migrations import RunSQL, RunPython, AddField, RemoveField, RenameField, AlterField, DeleteModel, RenameModel, AlterModelTable
from django.contrib.contenttypes.management import RenameContentType

from .libgraph import unmanaged_refs, depsort_with_sidekicks, sanity_check, subtree_depends
from .loader import get_samizdats
from .runner import cmd_sync, cmd_nuke, txstyle, get_cursor
from .libdb import dbstate_equals_definedstate
from .util import fqify_node

DBCONN = 'default'  # Only migrations on the default DB connections are supported. For now.
SMART_MIGRATIONS = getattr(settings, 'DBSAMIZDAT_SMART_MIGRATIONS', False)  # Don't use with custom Operations!


def get_cmd_args(**kwargs):
    return Namespace(
        printprogress=True,
        verbosity=kwargs['verbosity'],
        dbconn=DBCONN,
        txdiscipline=txstyle.JUMBO.value,
        in_django=True,
        samizdatmodules=tuple(),
        log_rather_than_print=not kwargs.get('interactive'),
    )


def sync(**kwargs):
    cmd_sync(get_cmd_args(**kwargs))


def nuke(samizdats=None, **kwargs):
    cmd_nuke(get_cmd_args(**kwargs), samizdats=samizdats)


def get_django_cursor():
    return get_cursor(
        Namespace(
            in_django=True,
            dbconn=DBCONN,
        )
    )


def tables_affected_by(apps, plan):
    """
    Returns tables potentially affected by a migration plan.
    There are false positives, because we don't know what a view depending on a table exactly reads from that table.
    Worse, there may be false negatives, as we may not understand all types of migrations, and the migration plan is not a public API.
    """
    tables_affected = set()
    for mig, reverse in plan:
        if reverse:
            return (True, tables_affected)  # Too hard to think about, not too common, just nuke & recreate
        for operation in mig.operations:
            if isinstance(operation, RenameContentType):
                break  # sidekick operation of RenameModel, which we've already handled
            if isinstance(operation, (RunSQL, RunPython)):
                # Those could affect anything. We'll have to remove all our state.
                # No sense in analyzing any other migrations then, either; return early.
                return (True, tables_affected)
            try:
                model_meta = apps.get_model(mig.app_label, getattr(operation, 'model_name', getattr(operation, 'old_name', getattr(operation, 'name'))))._meta
            except (AttributeError, LookupError):
                break
            if not model_meta.managed:
                break  # as then the migration will not actually do anything
            if isinstance(operation, (AddField, RemoveField, RenameField, AlterField, DeleteModel, RenameModel, AlterModelTable)):
                tables_affected.add(fqify_node(model_meta.db_table))
    return (False, tables_affected)


def premigrate_handler(sender, **kwargs):
    if not (kwargs.get('plan')) or (kwargs['using'] != DBCONN):
        return

    if not SMART_MIGRATIONS:
        # Make no effort to determine whether we can be selective in which state we'll remove.
        nuke(**kwargs)
        return

    samizdats = depsort_with_sidekicks(sanity_check(get_samizdats()))
    is_synced, *_whatevs = dbstate_equals_definedstate(get_django_cursor(), samizdats)
    if not is_synced:
        # There's unsynced samizdat state, and we can't tell if
        # a) new state depends on the post-migrate state or the pre-migrate state
        # b) old state will get in the way of the migrations
        # (or both.) Therefor, we can't sync, but neither can we leave any stuff lying around.
        # Thus we'll have to nuke DB state.
        nuke(**kwargs)
        return

    needs_wipe, tables_affected = tables_affected_by(kwargs['apps'], kwargs['plan'])
    if needs_wipe:
        nuke(**kwargs)
        return

    deps_affected = tables_affected & unmanaged_refs(samizdats)
    sds_affected = subtree_depends(samizdats, deps_affected)
    nuke(samizdats=sds_affected, **kwargs)


def postmigrate_handler(sender, **kwargs):
    if kwargs.get('plan') and kwargs['using'] == DBCONN:
        # Stuff went down, we may have dropped some things, sync will figure it out
        if kwargs.get('interactive'):
            print("Syncing DBSamizdat:")
        sync(**kwargs)


class DBSamizdatConfig(AppConfig):
    name = 'dbsamizdat'

    def ready(self):
        pre_migrate.connect(premigrate_handler, sender=self)
        post_migrate.connect(postmigrate_handler, sender=self)
