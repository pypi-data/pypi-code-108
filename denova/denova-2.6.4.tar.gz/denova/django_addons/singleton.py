'''
    Get and save a singleton record.

    Copyright 2015-2021 DeNova
    Last modified: 2021-06-17

    This file is open source, licensed under GPLv3 <http://www.gnu.org/licenses/>.
'''

from time import sleep
from traceback import format_exc

try:
    from django.db import transaction
    from django.db.utils import OperationalError
except ModuleNotFoundError:
    import sys
    sys.exit('Django required')

from denova.python.log import Log

log = Log()

def get_singleton(model, db=None):
    '''
        Get a singleton record.

        >>> from django.contrib.auth.models import Group
        >>> records = Group.objects.all()
        >>> for record in records:
        ...     __ = record.delete()
        >>> record = Group(name='special')
        >>> save_singleton(Group, record)
        >>> singleton_record = get_singleton(Group)
        >>> record == singleton_record
        True
    '''

    record = None

    with transaction.atomic():
        if db is None:
            records = model.objects.all()
        else:
            records = model.objects.using(db).all()

        if records.count() == 1:
            for r in records:
                record = r
        elif records.count() > 1:
            for r in records:
                if record is None:
                    record = r
                else:
                    log(f'deleted extra record: {r.pk}')
                    r.delete()

        if record is None:
            # the higher level must handle this case
            raise model.DoesNotExist()

    return record


def save_singleton(model, record, db=None, maxtries=3):
    '''
        Save a singleton record.

        >>> from django.contrib.auth.models import Group
        >>> records = Group.objects.all()
        >>> for record in records:
        ...     __ = record.delete()
        >>> record = Group(name='special')
        >>> save_singleton(Group, record)
        >>> singleton_record = get_singleton(Group)
        >>> record == singleton_record
        True
    '''

    def save(using=None):
        try:
            record.save(using=using)

        except:
            log.exception_only()

            retries = maxtries - 1
            retrying = True
            while retrying:
                retries = retries - 1
                try:
                    record.save(using=using)

                except OperationalError:
                    if retries > 0:
                        sleep(1)
                    else:
                        log('save_singleton(): too many retries')
                        raise

                else:
                    retrying = False

    try:
        with transaction.atomic():
            save(using=db)

        # get the singleton again to insure there's only 1 record
        get_singleton(model, db=db)
    except Exception:
        log(f'tried to save {model}')
        log(format_exc())
        raise
