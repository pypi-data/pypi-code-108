import logging

from django.apps import apps

from mayan.celery import app

from .classes import ModelFiler

logger = logging.getLogger(name=__name__)


@app.task(ignore_result=True)
def task_import_setup_process(import_setup_id):
    ImportSetup = apps.get_model(
        app_label='importer', model_name='ImportSetup'
    )

    import_setup = ImportSetup.objects.get(pk=import_setup_id)
    import_setup.process()


@app.task(ignore_result=True)
def task_import_setup_item_process(import_setup_item_id):
    ImportSetupItem = apps.get_model(
        app_label='importer', model_name='ImportSetupItem'
    )

    import_setup_item = ImportSetupItem.objects.get(pk=import_setup_item_id)
    import_setup_item.process()


@app.task(ignore_result=True)
def task_import_setup_populate(import_setup_id):
    ImportSetup = apps.get_model(
        app_label='importer', model_name='ImportSetup'
    )

    import_setup = ImportSetup.objects.get(pk=import_setup_id)
    import_setup.populate()


@app.task(ignore_result=True)
def task_model_filer_load(
    full_model_name, shared_upload_file_id, field_defaults=None
):
    SharedUploadedFile = apps.get_model(
        app_label='common', model_name='SharedUploadedFile'
    )

    shared_upload_file = SharedUploadedFile.objects.get(
        pk=shared_upload_file_id
    )

    model_filer = ModelFiler.get(full_model_name=full_model_name)

    model_filer.load(
        field_defaults=field_defaults, shared_upload_file=shared_upload_file
    )


@app.task
def task_model_filer_save(full_model_name, filter_kwargs=None):
    model_filer = ModelFiler.get(full_model_name=full_model_name)

    return model_filer.save(filter_kwargs=filter_kwargs).pk
