# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2013 Rémi Pannequin, Centre de Recherche en Automatique de
# Nancy remi.pannequin@univ-lorraine.fr
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE
"""
This module contain classes related to the creation, management and displaying of
properties in emulica.
"""

import random
import logging

from emulica.core import emulation

logger = logging.getLogger('emulica.properties')

class Registry(dict):
    """
    Properties can be attached to every products and module (including models).
    They basically consist in a (name, value) pair. Moreover, a PropertyDisplay
    can also be used. If so the property is said to be "displayable";
    such properties can be presented in the user interface, and modified.
    Properties that don't have any PropertyDisplay object associated are not
    displayed by the PropertyWindow UI.

    Properties can be a direct value (a str, bool, int or float) a module (ie a
    pointer to a module), a string that can be evaluated (in a pythonic syntax),
    or complex object that contain other (sub)properties (setup or program
    tables).

    A property can be accessed from its owner using square braquets [], using
    its name.
    For example, create['destination'] returns the value of the 'destination'
    property of module 'create'. Shape1['program_table']['program1'] is the
    property 'program1' of the program_table object (which is in turn the
    property 'program_table' of module 'Shape1')... Properties can be get/set
    using the square braquet syntax, in the same way a python dictionary can be
    used.

    module['prop'] return the non evaluated value of the property. To evaluate
    the property string, the evaluate_property function must be used, or
    alternativelly, the property must be called. Therefore if module['prop'] is
    "product['mass'] + 5", module['prop'](context) is 12, in context wherethe
    current product has a property that evaluates to 7.

    Classes:
        Registry -- a dict of properties, with dsiplay information
        SetupMatrix -- Models setup (transtion between programs), and associated time
        Program -- Models actions done by actuators
        Display -- display information for properties
    """

    def __init__(self, owner, rng):
        """Create a new Registry, where properties can be stored.

        Arguments:
            owner -- the module that own this property registry
            parent -- the parent registry (used to get evaluation context and to
            notify owner of property modification)
        """
        dict.__init__(self)
        self.owner = owner
        self.rng = rng
        self.displays = dict()
        self.__ordered_display = list()
        self.auto_eval = set()

    def __getitem__(self, name):
        """Return the property (unevaluated), or the evaluated value
        if the property has been marqued.
        """
        if name in self.auto_eval:
            return self.evaluate(name)
        return dict.__getitem__(self, name)

    def __setitem__(self, name, value):
        """call the method of the underling dict, and trigger the modules
        property changed signal."""
        dict.__setitem__(self, name, value)
        self.notify_owner(name)

    def notify_owner(self, prop_name):
        """Notify owner or parent of property change"""
        if 'emit' in dir(self.owner):
            self.owner.emit(emulation.Module.PROPERTIES_CHANGE_SIGNAL, prop_name, self.owner)

    def set_auto_eval(self, name, auto_eval=True):
        """Mark the property 'name' to be automatically evaluated"""
        if auto_eval:
            self.auto_eval.add(name)
        else:
            self.auto_eval.remove(name)

    def add_with_display(self, name, display_type, value=None, display_name=None):
        """Add a new property and set its display. If value is not specified or None,
        it is instancied from the default_value dict in class Display. If display_name
        is not specified or None, it take avlue name.

        Arguments:
            name -- the property name
            display_type -- the display type (int, see properties.Display)

        Keyword arguments:
            value -- the property's value
            display_name -- the name to use in dialogs
        """
        if value is None:
            if 'program_keyword' in dir(self.owner):
                schema = self.owner.program_keyword
            else:
                schema = list()
            value = Display.default_value[display_type](self.owner.properties, name, schema)
        display_name = display_name or name
        self[name] = value
        display = Display(display_type, display_name)
        self.__ordered_display.append(name)
        self.displays[name] = display

    def set_display(self, name, display):
        """Set the display of the property designed by 'name'.

        Arguments:
            name -- the name of the property
            display -- the properties.Display to set
        """
        self.displays[name] = display
        if not display in self.__ordered_display:
            self.__ordered_display.append(name)

    def get_display(self, name):
        """Get the display of the property designed by name.

        Arguments:
            name -- the name of the property

        Returns:
            the associated Display object, or None if the property is not
            displayable
        """
        return self.displays[name]

    def displayables(self):
        """return a list of (name, value, display) tuple of all the properties
        that have a display set."""
        result = list()
        for name in self.__ordered_display:
            result.append((name, self[name], self.displays[name]))
        return result

    def get(self, name):
        """Return the value of the prop without evaluation"""
        return dict.__getitem__(self, name)

    def evaluate(self, name, product=None):
        """Resolve reference to other properties, and return the value.
        """
        return self.eval_expression(self.get(name), product)

    def eval_and_set(self, name, value, product=None):
        """Evaluate value in the context of product, and set the result as prop
        name.
        Exemple product.properties.eval_and_set('mass', 'self['mass'] / 2')
        """
        self[name] = self.eval_expression(value, product)

    def eval_expression(self, expr, product=None):
        """Evaluate expression expr"""
        if type(expr) == str:
            context = dict()
            context['rng'] = self.rng
            if self.owner and 'model' in dir(self.owner):
                context['model'] = self.owner.model
            for (name, value) in self.items():
                context[name] = value
            if not product is None:
                context['product'] = product
            result = eval(expr, globals(), context)
        else:
            result = expr
        return result


class SetupMatrix(object):
    """A Setup Matrix record setup times between programs.

    When requesting a setup time for a (initial -> final) transition
        * if it exists, that precise transition is used
        * else, if there is a default for that final, it is used
        * else, the default setup time is used

    Attributes:
        default_time -- default setup time when no setup data have been found
    """
    def __init__(self, prop_registry, default_time=0, parent_prop_name='setup'):
        """Create a new instance of SetupMatrix

        Arguments:
            default_time -- default setup time (default = 0)
        """
        self.registry = prop_registry
        assert type(parent_prop_name) == str
        assert 'notify_owner' in dir(self.registry)
        self.parent_prop_name = parent_prop_name
        self.default_time = default_time
        self.__dest_default = dict()
        self.__dest_prog = dict()

    def add(self, initial_prog, final_prog, setup_time):
        """Add a new element in the matrix.

        Arguments:
            initial_prog -- the program at the begining of the setup
            final_prog -- the program at the end of the setup
            setup_time -- the setup delay
        """
        if final_prog not in  self.__dest_prog:
            self.__dest_prog[final_prog] = dict()
        self.__dest_prog[final_prog][initial_prog] = setup_time
        self.registry.notify_owner(self.parent_prop_name)

    def add_final(self, final_prog, setup_time):
        """Add a new column in the setup matrix : ie a setup that
        depends only on the final program."""
        self.__dest_default[final_prog] = setup_time

    def remove(self, initial_prog, final_prog):
        """Remove an element in the setup matrix

        Attributes:
            initial_prog -- the program at the beginig of the setup
            final_prog -- the program at the end of the setup
        """
        del self.__dest_prog[final_prog][initial_prog]
        if self.__dest_prog[final_prog]:
            del self.__dest_prog[final_prog]
        self.registry.notify_owner(self.parent_prop_name)

    def modify(self, initial_prog, final_prog, new_initial=None, new_final=None, new_time=None):
        """Change an entry in the setup matrix. If the change create a conflict..."""
        #TODO: check for duplicate keys
        time = self.__dest_prog[final_prog][initial_prog]
        if (new_initial and (not new_initial == initial_prog)) or (new_final and (not new_final == final_prog)):
            initial = new_initial or initial_prog
            final = new_final or final_prog
            logger.debug(_("changing setup: ({initial}, {final}) -> ({new_init}, {new_final})").format(initial=initial_prog,
                                                                                                       final=final_prog,
                                                                                                       new_init=initial,
                                                                                                       new_final=final))
            self.remove(initial_prog, final_prog)
            self.add(initial, final, time)
        if new_time:
            logger.debug(_("changing setup time: {0:f}) -> {1:f}").format(time, new_time))
            self.__dest_prog[final_prog][initial_prog] = new_time
        self.registry.notify_owner(self.parent_prop_name)

    def get(self, initial_prog, final_prog):
        """Get setup time. if initial or final element desn't exist in
        the matrix, the default value is returned.

        Arguments:
            initial_prog -- the program at the beginig of the setup
            final_prog -- the program at the end of the setup

        Returns:
            the setup delay
        """
        if initial_prog == final_prog:
            return 0
        if final_prog in self.__dest_prog and initial_prog in self.__dest_prog[final_prog]:
            expr = self.__dest_prog[final_prog][initial_prog]
        elif final_prog in self.__dest_default:
            expr = self.__dest_default[final_prog]
        else:
            expr = self.default_time
        return self.registry.eval_expression(expr)

    def items(self):
        """Return a list of tuple of the form (initial, final, delay)
        """
        for (final, time_elt) in self.__dest_prog.items():
            for (initial, delay) in time_elt.items():
                yield (initial, final, delay)

    def __len__(self):
        """Return the number of elements in the matrix (ie the number of setups)"""
        result = 0
        for d in self.__dest_prog.values():
            result += len(d)
        return result


class XTable(dict):
    """A dictionary of Physical Changes, where the name is the attribute to
    change and value is the new attribute value. This class is the base for
    ProgramTable and ChangeTable"""

    def __init__(self, prop_registry, parent_prop_name):
        """Create a new Xtable.

        Arguments:
            prop_registry -- the parent property Registry
            parent_prop_name -- the name of the parent property (used to notify
            of value changes)
        """
        dict.__init__(self)
        self.registry = prop_registry
        assert 'notify_owner' in dir(self.registry)
        self.parent_prop_name = parent_prop_name

    def __setitem__(self, name, value):
        """Set a value in the table"""
        dict.__setitem__(self, name, value)
        self.registry.notify_owner(self.parent_prop_name)


class ChangeTable(XTable):
    """A dictionary of Physical Changes, where the name is the attribute to
    change and value is the new attribute value"""


class ProgramTable(XTable):
    """A dictionary of Programs, designed by their names."""

    def __init__(self, prop_registry, parent_prop_name, schema):
        """Set the structure of the program's transforms
        schema is a list of tuple of the form (key, display_type, display_name)
        """
        XTable.__init__(self, prop_registry, parent_prop_name)
        self.program_keyword = schema

    def add_program(self, name, delay, prog_transform=None, prog_resources=[]):
        """Add a program in the program Table."""
        prog = Program(self.registry, delay, prog_resources)
        #initialize transforms to default values
        for (transf_name, display) in self.program_keyword:
            prog.transform[transf_name] = Display.default_value[display.type](self.registry,
                                                                              self.parent_prop_name, [])
        if prog_transform and 'items' in dir(prog_transform):
            for (transf_name, transf_value) in prog_transform.items():
                if 'items' in dir(transf_value):
                    chg_table = ChangeTable(self.registry, self.parent_prop_name)
                    prog.transform[transf_name] = chg_table
                    for (chg_name, chg_value) in transf_value.items():
                        chg_table[chg_name] = chg_value
                else:
                    prog.transform[transf_name] = transf_value
        self[name] = prog


class Program(object):
    """A program represents a transformation to apply on a product,
    and a transformation time. time can be either a numeric value, or
    a string containing a python expression that evaluate to a time.
    This is usefull to model probability distribution such as function of the
    random module. These expressions should use the globally-defined random
    number generator called rng (e.g. 'rng.expovariate(lambda=2)')

    A program is a particular form of property registry

    Attributes:
        transform -- a dictionary of program parameters
        time_law -- a python expression used to evaluate the delay (may be
                    a float, int, or an expression calling random or rng)
    """
    def __init__(self, prop_registry, time=0.0, resources=[]):
        """Create a new instance of a Program

        Arguments:
            module -- the module the own the program.
            time -- the program duration (default = 0.0). It can be either a number, or an evaluable string.
            resources -- a list of resources that the program  execution require (default [])
        """
        self.registry = prop_registry
        self.time_law = time
        self.transform = XTable(self.registry, 'program_table')
        self.resources = resources

    def time(self, product=None):
        """Return the delay corresponding to this program. If time is a string
        expression, it is evaluated to a number.
        """
        return self.registry.eval_expression(self.time_law, product)

    def is_evaluable(self):
        """Return True if time_law is evaluable"""
        class DumbProduct(object):
            """used to test whether expression evauatio would work."""
            def __getitem__(self, value):
                return 1
        product = DumbProduct()
        try:
            eval_value = self.registry.eval_expression(self.time_law, product)
        except:
            logger.exception(_("could not evaluate expression {0}").format(self.time_law))
            return False
        if not type(eval_value) == str:
            return True
        return False


class Display(object):
    """
    display_name -- the localized name that should be used to display
                            this property
            lower_bound --
            upper_bound --
    """

    REFERENCE = 1
    """A module present in the model, represented by its name"""
    VALUE = 2
    """Any (string) value"""
    BOOL_VALUE = 3
    """A boolean value"""
    INT = 4
    """A numerical value (int)"""
    FLOAT = 5
    """A numerical value (int)"""
    REFERENCE_LIST = 6
    """A list of references"""
    PROGRAM_TABLE = 7
    """A dictionary (ProgramTable) of emulica.emulation.Program, where keys are program names"""
    SETUP = 8
    """A emulica.emulation.SetupMatrix"""
    EVALUABLE = 9
    """A string that can be evaluated (using python's 'eval' function) to a numeric"""
    PHYSICAL_PROPERTIES_LIST = 10
    """a set of physical properties, and the associated value"""

    type_names = {REFERENCE: _("Module"),
                  VALUE: _("String"),
                  BOOL_VALUE: _("Boolean"),
                  INT: _("Integer"),
                  FLOAT: _("Float"),
                  REFERENCE_LIST: _("List of modules"),
                  PROGRAM_TABLE: _("Program table"),
                  SETUP: _("Setup table"),
                  EVALUABLE: _("Evaluable string"),
                  PHYSICAL_PROPERTIES_LIST: _("List of physical properties")}

    default_value = {REFERENCE: lambda reg, name, schema: None,
                     VALUE: lambda reg, name, schema: str(),
                     BOOL_VALUE: lambda reg, name, schema: bool(),
                     INT: lambda reg, name, schema: int(),
                     FLOAT: lambda reg, name, schema: float(),
                     REFERENCE_LIST: lambda reg, name, schema: list(),
                     PROGRAM_TABLE: lambda reg, name, schema: ProgramTable(reg, name, schema),
                     SETUP: lambda reg, name, schema: SetupMatrix(reg, 0, name),
                     EVALUABLE: lambda reg, name, schema: str(),
                     PHYSICAL_PROPERTIES_LIST: lambda reg, name, schema: ChangeTable(reg, name)}

    def __init__(self, prop_type, display_name=None, lower_bound=0, upper_bound=2000000):
        """Create an new instance of a ModuleProperty

        Arguments:
            prop_type -- the type of the property : either one of the int
                         constant defined in this module, or a string that is
                         the name of the constant
            value -- the value of the property
            module -- the module tha this property belong to.
        """
        self.name = display_name
        if isinstance(prop_type, int):
            self.type = prop_type
        else:
            self.type = getattr(self, prop_type)
            #self.logger.warning("")
        self.lower = lower_bound
        self.upper = upper_bound

    def is_int(self):
        """Return true if property is an integer"""
        return self.type == self.INT
