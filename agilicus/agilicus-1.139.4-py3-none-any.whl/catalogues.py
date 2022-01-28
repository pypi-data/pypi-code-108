import agilicus
from . import context
from .input_helpers import build_updated_model
from .input_helpers import pop_item_if_none
from .input_helpers import strip_none


def query(ctx, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    kwargs = strip_none(kwargs)
    result = apiclient.catalogues_api.list_catalogues(**kwargs)
    if result:
        return result.catalogues


def add(ctx, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    model = agilicus.Catalogue(**kwargs)
    return apiclient.catalogues_api.create_catalogue(model).to_dict()


def show(ctx, catalogue_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    return apiclient.catalogues_api.get_catalogue(catalogue_id).to_dict()


def _build_updated_catalogue(catalogue):
    new_catalogue_dict = catalogue.to_dict()
    new_catalogue_dict.pop("catalogue_entries", [])
    return agilicus.Catalogue(**new_catalogue_dict)


def update(ctx, catalogue_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    catalogue = apiclient.catalogues_api.get_catalogue(catalogue_id)
    catalogue = _build_updated_catalogue(catalogue)
    catalogue = build_updated_model(agilicus.Catalogue, catalogue, kwargs)
    return apiclient.catalogues_api.replace_catalogue(catalogue_id, catalogue).to_dict()


def delete(ctx, catalogue_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    return apiclient.catalogues_api.delete_catalogue(catalogue_id)


def query_entries(ctx, catalogue_id=None, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    kwargs = strip_none(kwargs)
    if catalogue_id:
        # The id and category are tied as a result this method doesn't take a category
        kwargs.pop("catalogue_category", None)
        result = apiclient.catalogues_api.list_catalogue_entries(catalogue_id, **kwargs)
    else:
        result = apiclient.catalogues_api.list_all_catalogue_entries(**kwargs)

    if result:
        return result.catalogue_entries


def add_entry(ctx, catalogue_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    pop_item_if_none(kwargs, "tag")
    pop_item_if_none(kwargs, "short_description")
    pop_item_if_none(kwargs, "long_description")
    model = agilicus.CatalogueEntry(**kwargs)
    return apiclient.catalogues_api.create_catalogue_entry(catalogue_id, model).to_dict()


def show_entry(ctx, catalogue_id, entry_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    return apiclient.catalogues_api.get_catalogue_entry(catalogue_id, entry_id).to_dict()


def update_entry(ctx, catalogue_id, entry_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    catalogue_entry = apiclient.catalogues_api.get_catalogue_entry(
        catalogue_id, entry_id
    )
    catalogue_entry = build_updated_model(
        agilicus.CatalogueEntry, catalogue_entry, kwargs
    )
    return apiclient.catalogues_api.replace_catalogue_entry(
        catalogue_id, entry_id, catalogue_entry
    ).to_dict()


def delete_entry(ctx, catalogue_id, entry_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    return apiclient.catalogues_api.delete_catalogue_entry(catalogue_id, entry_id)
