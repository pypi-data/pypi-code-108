from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link
from mayan.apps.navigation.utils import factory_condition_queryset_access

from .icons import (
    icon_import_setup_action_delete, icon_import_setup_action_edit,
    icon_import_setup_action_list,
    icon_import_setup_action_backend_selection,
    icon_import_setup_backend_selection, icon_import_setup_delete,
    icon_import_setup_edit, icon_import_setup_log_list, icon_import_setup_process,
    icon_import_setup_item_delete, icon_import_setup_item_document_list,
    icon_import_setup_item_process, icon_import_setup_clear,
    icon_import_setup_items_list, icon_import_setup_list,
    icon_import_setup_populate, icon_model_filer_load, icon_model_filer_save
)
from .permissions import (
    permission_import_setup_create, permission_import_setup_delete,
    permission_import_setup_edit, permission_import_setup_process,
    permission_import_setup_view, permission_model_filer_load,
    permission_model_filer_save
)


def conditional_disable_import_has_items(context):
    return context['resolved_object'].items.count() == 0


# Import setup

link_import_setup_backend_selection = Link(
    icon=icon_import_setup_backend_selection,
    permissions=(permission_import_setup_create,),
    text=_('Create import setup'),
    view='importer:import_setup_backend_selection',
)
link_import_setup_delete = Link(
    args='resolved_object.pk',
    icon=icon_import_setup_delete,
    permissions=(permission_import_setup_delete,),
    tags='dangerous', text=_('Delete'), view='importer:import_setup_delete'
)
link_import_setup_edit = Link(
    args='resolved_object.pk',
    icon=icon_import_setup_edit,
    permissions=(permission_import_setup_edit,), text=_('Edit'),
    view='importer:import_setup_edit'
)
link_import_setup_list = Link(
    icon=icon_import_setup_list,
    text=_('Import setup list'),
    view='importer:import_setup_list'
)
link_import_setup_logs = Link(
    args=('resolved_object.pk',), icon=icon_import_setup_log_list,
    permissions=(permission_import_setup_view,), text=_('Logs'),
    view='importer:import_setup_log_list'
)
link_import_setup_setup = Link(
    condition=factory_condition_queryset_access(
        app_label='importer', model_name='ImportSetup',
        object_permission=permission_import_setup_view,
        view_permission=permission_import_setup_create,
    ), icon=icon_import_setup_list,
    text=_('Importer'),
    view='importer:import_setup_list'
)

# Import setup actions


link_import_setup_action_delete = Link(
    args='resolved_object.pk',
    icon=icon_import_setup_action_delete,
    permissions=(permission_import_setup_edit,),
    tags='dangerous', text=_('Delete'),
    view='importer:import_setup_action_delete',
)
link_import_setup_action_edit = Link(
    args='resolved_object.pk',
    icon=icon_import_setup_action_edit,
    permissions=(permission_import_setup_edit,),
    text=_('Edit'), view='importer:import_setup_action_edit',
)
link_import_setup_action_list = Link(
    args='resolved_object.pk',
    icon=icon_import_setup_action_list,
    permissions=(permission_import_setup_view,), text=_('Actions'),
    view='importer:import_setup_action_list'
)
link_import_setup_action_backend_selection = Link(
    args='resolved_object.pk',
    icon=icon_import_setup_action_backend_selection,
    permissions=(permission_import_setup_edit,), text=_('Create action'),
    view='importer:import_setup_action_backend_selection',
)

# Import setup item

link_import_setup_populate = Link(
    args='resolved_object.pk',
    icon=icon_import_setup_populate,
    permissions=(permission_import_setup_process,), text=_('Prepare'),
    view='importer:import_setup_populate'
)
link_import_setup_multiple_populate = Link(
    icon=icon_import_setup_populate, text=_('Prepare'),
    view='importer:import_setup_multiple_populate'
)
link_import_setup_process = Link(
    args='resolved_object.pk',
    conditional_disable=conditional_disable_import_has_items,
    icon=icon_import_setup_process,
    permissions=(permission_import_setup_process,), text=_('Process'),
    view='importer:import_setup_process'
)
link_import_setup_multiple_process = Link(
    icon=icon_import_setup_process, text=_('Process'),
    view='importer:import_setup_multiple_process'
)
link_import_setup_clear = Link(
    args='resolved_object.pk', conditional_disable=conditional_disable_import_has_items,
    icon=icon_import_setup_clear,
    permissions=(permission_import_setup_process,), text=_('Clear items'),
    view='importer:import_setup_clear'
)
link_import_setup_multiple_clear = Link(
    icon=icon_import_setup_clear, text=_('Clear items'),
    view='importer:import_setup_multiple_clear'
)
link_import_setup_item_document_list = Link(
    args='resolved_object.pk',
    icon=icon_import_setup_item_document_list,
    permissions=(permission_import_setup_view,), text=_('Documents'),
    view='importer:import_setup_item_document_list'
)
link_import_setup_items_list = Link(
    args='resolved_object.pk',
    icon=icon_import_setup_items_list,
    permissions=(permission_import_setup_view,), text=_('Items'),
    view='importer:import_setup_items_list'
)
link_import_setup_item_multiple_delete = Link(
    icon=icon_import_setup_item_delete,
    permissions=(permission_import_setup_edit,),
    tags='dangerous', text=_('Delete'),
    view='importer:import_setup_item_multiple_delete'
)
link_import_setup_item_multiple_process = Link(
    icon=icon_import_setup_item_process,
    permissions=(permission_import_setup_edit,),
    text=_('Process'), view='importer:import_setup_item_multiple_process'
)

# Model filer

link_model_filer_load = Link(
    args='resolved_object.pk', icon=icon_model_filer_load,
    permissions=(permission_model_filer_load,),
    text=_('Load'), view='importer:import_setup_load'
)
link_model_filer_save = Link(
    args='resolved_object.pk', icon=icon_model_filer_save,
    permissions=(permission_model_filer_save,),
    text=_('Save'), view='importer:import_setup_save'
)
