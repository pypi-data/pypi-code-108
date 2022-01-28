import csv
import io
from urllib.request import urlopen

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, models
from django.db.models import QuerySet
from model_utils import Choices

STANDARDS = Choices(
    (0, "unspecified", "Unspecified"),
    (1, "nace", "NACE"),
    (2, "ateco", "ATECO"),
    (3, "gics", "GICS"),
    (4, "isic", "ISIC"),  # rev4
    (5, "naics", "NAICS"),  # 2022
    (6, "sic", "SIC"),
    (7, "sae", "SAE"),
)


def get_or_none(queryset: QuerySet, *args, **kwargs):
    try:
        return queryset.get(*args, **kwargs)
    except ObjectDoesNotExist:
        return None


def get_csv_reader_from_remote(remote_path: str):
    """
    Read a csv file from a remote server and return a DictReader object
    """
    with urlopen(remote_path) as file:
        mycsv = io.StringIO(file.read().decode())
        return csv.DictReader(mycsv)


@transaction.atomic()
def bulk_create_update_from_csv(model: models.Model.__class__, csv_reader: csv.DictReader, batch_size=500):
    """
    1. Read model records from a given csv_reader and
    2. Form two lists with objects to create and update
    3. Use bulk_create and bulk_update to commit to the database
    """
    records_to_create = []
    records_to_update = []
    _ids = set(model.objects.values_list('id', flat=True))
    for row in csv_reader:
        if int(row['id']) in _ids:
            records_to_update.append(model(**row))
        else:
            records_to_create.append(model(**row))

    csv_reader.fieldnames.remove('id')

    model.objects.bulk_create(
        records_to_create,
        batch_size=batch_size
    )
    model.objects.bulk_update(
        records_to_update,
        fields=csv_reader.fieldnames,
        batch_size=batch_size
    )
