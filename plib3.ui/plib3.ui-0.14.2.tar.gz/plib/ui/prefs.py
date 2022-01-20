#!/usr/bin/env python3
"""
Module PREFS -- UI Preferences Dialog
Sub-Package UI of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import collections

from plib.ui.defs import *
from plib.ui.widgets import *


class PPreferences(object):
    """Manage editing and saving of program preferences.
    """
    
    default_dialog_width = 480
    default_group_style = PANEL_SUNKEN
    default_label_bold = False
    default_group_label_bold = True
    
    dialog = None
    
    def __init__(self, app, caption):
        self.app = app
        self.caption = caption
        self.inifile, self.section_type, self.field_map = app.prefs_data
        self.dialog_enums = getattr(app, 'prefs_dialog_enums', {})
        self.dialog_groups = getattr(app, 'prefs_dialog_groups', {})
        self.dialog_width = getattr(app, 'prefs_dialog_width', self.default_dialog_width)
        self.group_style = getattr(app, 'prefs_group_style', self.default_group_style)
        self.label_bold = getattr(app, 'prefs_label_bold', self.default_label_bold)
        self.group_label_bold = getattr(app, 'prefs_group_label_bold', self.default_group_label_bold)
        self.prefs_client = self.get_client_spec()
    
    def unpack_option(self, sname, opt):
        attrname = getter = setter = None
        if len(opt) > 4:
            oname, otype, odefault, getter, setter = opt
        elif len(opt) > 3:
            oname, otype, odefault, attrname = opt
        elif len(opt) > 2:
            oname, otype, odefault = opt
        else:
            oname, odefault = opt
            otype = type(odefault)
        if attrname is None:
            attrname = '{}_{}'.format(sname, oname)
        return otype, odefault, attrname
    
    def get_widget(self, attrname, otype, odefault, caption, geometry=None):
        if otype is bool:
            # No enum possible for checkbox, no separate label
            return checkbox(attrname, caption, odefault)
        
        enum = self.dialog_enums.get(attrname)
        control = (
            (num_combo if otype is int else combo)(attrname, enum, odefault)
            if enum else
            (num_edit if otype is int else edit)(attrname, odefault, geometry=geometry)
        )
        
        return labeled(caption, control, label_bold=self.label_bold)
    
    def get_client_spec(self):
        geometry = (None, None, self.dialog_width, None)
        
        contents = []
        for sname, opts in self.inifile._optionlist:
            specs = collections.OrderedDict()
            for opt in opts:
                otype, odefault, attrname = self.unpack_option(sname, opt)
                caption = self.field_map.get(attrname, "<Unknown Setting>")
                specs[attrname] = (otype, odefault, caption)
            
            groups = self.dialog_groups.get(sname)
            if not groups:
                groups = [(key,) for key in specs]
            controls = []
            for group in groups:
                if len(group) == 1:
                    attrname = group[0]
                    otype, odefault, caption = specs[attrname]
                    widget = self.get_widget(attrname, otype, odefault, caption, geometry)
                else:
                    widget = panel(ALIGN_JUST, LAYOUT_HORIZONTAL, [
                        self.get_widget(attrname, *specs[attrname])
                        for attrname in group
                    ])
                controls.append(widget)
            
            group_caption = self.field_map.get(sname)
            contents.append((group_caption, controls))
        
        if self.section_type == SECTION_TAB:
            dialog_controls = tabwidget('prefsdialog', [
                (caption, tab(ALIGN_JUST, LAYOUT_VERTICAL, controls + [padding()]))
                for caption, controls in contents
            ])
        elif self.section_type == SECTION_GROUPBOX:
            dialog_controls = panel(ALIGN_JUST, LAYOUT_VERTICAL, [
                labelbox(caption, controls, align=ALIGN_TOP, style=self.group_style, label_bold=self.group_label_bold)
                for caption, controls in contents
            ])
        else:
            raise ValueError("Unknown dialog section type: {}".format(repr(section_type)))
        
        dialog_buttons = panel(ALIGN_BOTTOM, LAYOUT_HORIZONTAL, [
            padding(),
            action_button(ACTION_APPLY),
            action_button(ACTION_OK),
            action_button(ACTION_CANCEL),
        ])
        
        return frame(ALIGN_JUST, LAYOUT_VERTICAL, [
            dialog_controls,
            dialog_buttons,
        ])
    
    def iter_vars(self):
        for sname, opts in self.inifile._optionlist:
            for opt in opts:
                otype, odefault, attrname = self.unpack_option(sname, opt)
                yield otype, odefault, attrname
    
    def control_by_name(self, otype, attrname):
        return getattr(self, '{}_{}'.format(
            (
                'checkbox' if otype is bool else
                'combo' if attrname in self.dialog_enums else
                'edit'
            ),
            attrname
        ))
    
    def control_method(self, otype, attrname):
        return (
            'checked' if otype is bool else
            ('current_{}' if attrname in self.dialog_enums else "{}").format(
                'value' if otype is int else 'text'
            )
        )
    
    def control_set(self, otype, attrname, value):
        control = self.control_by_name(otype, attrname)
        method = 'set_{}'.format(self.control_method(otype, attrname))
        getattr(control, method)(value)
    
    def load_prefs(self):
        for otype, _, attrname in self.iter_vars():
            self.control_set(otype, attrname, getattr(self.inifile, attrname))
    
    def show_dialog(self):
        dialog_class = get_toolkit_class('dialog', "PDialog")
        dialog = dialog_class(self, self.app.main_window, self.caption, self.prefs_client)
        self.load_prefs()
        dialog.setup_notify(SIGNAL_FINISHED, self.dialog_done)
        dialog.display()
    
    def control_get(self, otype, attrname):
        control = self.control_by_name(otype, attrname)
        method = 'get_{}'.format(self.control_method(otype, attrname))
        return getattr(control, method)()
    
    def save_prefs(self):
        for otype, _, attrname in self.iter_vars():
            setattr(self.inifile, attrname, self.control_get(otype, attrname))
        self.inifile.writeini()
    
    def on_apply(self):
        self.save_prefs()
    
    def dialog_done(self, result):
        print("Dialog done, result:", repr(result))
        if result:  # NOTE: we assume a simple boolean check on result is enough
            self.save_prefs()
        self.dialog = None
