import csv
import os
import sys
from typing import List, Optional

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import color_style
from edc_constants.constants import FEMALE, MALE
from edc_model.stubs import BaseUuidModelStub
from tqdm import tqdm

from mocca_lists.models import MoccaOriginalSites

style = color_style()


class ImportMoccaError(Exception):
    pass


def birthyear_in_range(x: int) -> int:
    if not (1900 <= x <= 2003):
        raise TypeError(f"Birth year out of range. Got {x}")
    return x


def import_mocca_register(
    path: Optional[str] = None,
    verbose: bool = None,
    force_delete: Optional[bool] = None,
):
    model_cls = django_apps.get_model("mocca_screening.moccaregister")
    fieldnames = [
        "country",
        "site",
        "screening_id",
        "study_id",
        "initials",
        "birth_year",
        "age_in_years",
        "gender",
    ]
    path = os.path.expanduser(path or settings.MOCCA_REGISTER_FILE)
    try:
        if not os.path.exists(path):
            raise ImportMoccaError(path)
    except TypeError:
        raise ImportMoccaError(f"Invalid path. Got {path}.")
    if verbose:
        sys.stdout.write(
            f"\nImporting MOCCA register from '{path}' "
            f"into {model_cls._meta.label_lower}\n"
        )

    if model_cls.objects.all().count() > 0:
        if force_delete:
            model_cls.objects.all().delete()
        else:
            raise ImportMoccaError(
                "Unable to continue. Not deleting existing records. "
                "Use `force_delete` to override"
            )

    import_file(path, model_cls, fieldnames)

    if verbose:
        sys.stdout.write("Done.\n")


def import_file(
    path: str,
    model_cls: BaseUuidModelStub,
    fieldnames: List[str],
) -> None:
    sys.stdout.write(style.MIGRATE_HEADING("\n Importing mocca register.\n"))
    with open(path, "r") as f:
        reader = csv.DictReader(f, fieldnames=fieldnames)
        total = len([row for row in reader])
    with open(path, "r") as f:
        reader = csv.DictReader(f, fieldnames=fieldnames)
        for index, row in tqdm(enumerate(reader), total=total):
            if index == 0:
                continue
            try:
                model_cls.objects.get(mocca_study_identifier=row["study_id"])
            except ObjectDoesNotExist:
                mocca_site = MoccaOriginalSites.objects.get(name=row["site"].lower())
                model_cls.objects.create(
                    mocca_country=row["country"].lower(),
                    mocca_site=mocca_site,
                    mocca_screening_identifier=row["screening_id"],
                    mocca_study_identifier=row["study_id"],
                    initials=(row["initials"] or "").upper(),
                    birth_year=birthyear_in_range(int(row["birth_year"])),
                    age_in_years=row["age_in_years"],
                    gender=MALE if row["gender"].lower() == "male" else FEMALE,
                )
