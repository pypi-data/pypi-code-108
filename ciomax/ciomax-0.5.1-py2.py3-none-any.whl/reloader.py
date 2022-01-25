
from importlib import reload

from ciomax import store, const,  render_scope
from ciomax.sections import collapsible_section
from ciomax.components import widgets

from ciomax.components import text_field_grp
from ciomax.components import int_field_grp
from ciomax.components import text_grp
from ciomax.components import key_value_grp
from ciomax.components import combo_box_grp
from ciomax.components import software_combo_box_grp
from ciomax.components import checkbox_grp
from ciomax.components import notice_grp
from ciomax.components import buttoned_scroll_panel
from ciomax.sections import general_section
from ciomax.sections import software_section
from ciomax.sections import frames_section
from ciomax.sections import info_section
from ciomax.sections import advanced_section
from ciomax.sections import environment_section
from ciomax.sections import metadata_section
from ciomax.sections import extra_assets_section
from ciomax import main_tab
from ciomax import preview_tab
from ciomax import validation_tab
from ciomax import response_tab
from ciomax import validation
from ciomax import submit
 

# The order of the reloads is important. 
reload(const)
reload(render_scope)
reload(store)
reload(collapsible_section)
reload(widgets)
reload(text_field_grp)
reload(int_field_grp)
reload(text_grp)
reload(key_value_grp)
reload(combo_box_grp)
reload(software_combo_box_grp)
reload(checkbox_grp)
reload(notice_grp)
reload(buttoned_scroll_panel)
reload(general_section)
reload(software_section)
reload(frames_section)
reload(info_section)
reload(advanced_section)
reload(environment_section)
reload(metadata_section)
reload(extra_assets_section)
reload(main_tab)
reload(preview_tab)
reload(validation_tab)
reload(response_tab)
reload(validation)
reload(submit)
 