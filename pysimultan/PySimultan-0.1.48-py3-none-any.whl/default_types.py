from __future__ import annotations
from collections import UserList
from functools import lru_cache
import pandas as pd
import numpy as np
from weakref import WeakSet
import colorlog
import re

# from typing import List as TypeList
from typing import NewType, Union, Optional

# from System.Collections.Generic import List as CSList
# from System import Array, Double

from ParameterStructure.Values import SimMultiValueBigTable, SimMultiValueBigTableHeader, SimMultiValuePointer
from ParameterStructure.Instances import SimInstancePlacementGeometry, SimInstanceType
from ParameterStructure.Parameters import SimParameter
from ParameterStructure.Components import SimComponent, SimSlot, SimSlotBase, SimChildComponentEntry, ComponentUtils
from ParameterStructure.Algorithms.Components import ComponentManagement, ComponentMapping
from ParameterStructure.Assets import ContainedResourceFileEntry
from ParameterStructure.SimObjects import SimId

from .config import continue_on_error
from .utils import sort_references, sort_component_list, sort_slots, parse_slot
from .simultan_utils import create_parameter
from . import create_component
from .slots import SimSlotBase
from .data_model import data_models


SimMultiValueBigTableType = NewType('SimMultiValueBigTable', SimMultiValueBigTable)
ContainedResourceFileEntryType = NewType('ContainedResourceFileEntry', ContainedResourceFileEntry)
SimParameterType = NewType('SimParameter', SimParameter)
SimComponentType = NewType('SimComponent', SimComponent)


logger = colorlog.getLogger('PySimultan')


class classproperty(object):

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


def init_parameter(cls, comp, param_name, val, user, slot_parameter_variable=False):

    if val is None:
        return
    if isinstance(val, (int, float, str)):
        if param_name in cls._slots.keys():
            if not slot_parameter_variable:
                raise TypeError((f'Error initializing instance of {cls.__name__}:\n'
                                 f'{param_name} is associated with a slot.'
                                 f'Valid parameter values are SimComponent or SimultanObject.'
                                 f'but the value is of type {type(val)}.\n'
                                 f'If this is intentional, initialize with option slot_parameter_variable=True'))

        if hasattr(comp, param_name):
            setattr(comp, param_name, val)
        else:
            # create parameter:
            unit = str(cls._units.get(param_name, ''))
            if isinstance(val, str):
                param = create_parameter(name=param_name,
                                         value=0.0,
                                         unit=unit)
                param.set_TextValue(val)
            else:
                param = create_parameter(name=param_name,
                                         value=float(val),
                                         unit=unit)
                param.set_ValueCurrent(float(val))
            comp.Parameters.Add(param)
    elif isinstance(val, (SimComponent, SimultanObject)):
        # if the parameter is associated with a slot:
        if param_name in cls._slots.keys():
            # create sub component or reference
            full_slot_name = cls._slots[param_name]
            slot_name, slot_extension = parse_slot(full_slot_name)

            if isinstance(val, SimultanObject) or (val is None):
                slot = SimSlot(SimSlotBase(slot_name), str(slot_extension))
                ComponentManagement.AddReferencedComponentSlot(comp, slot, user)
                if val is not None:
                    ComponentManagement.AddReferencedComponent(comp, slot, val._wrapped_obj, user)
            elif isinstance(val, SimComponent):
                entry = SimChildComponentEntry(SimSlot(SimSlotBase(slot_name), str(slot_extension)), val)
                comp.Components.Add(entry)
            else:
                raise TypeError(
                    f'Error setting parameter {param_name}. Wrong type {type(val)}. This parameter is associated with a slot. The parameter value must be of type {SimultanObject} or {SimComponent}')
        else:
            raise TypeError(
                f'Error setting parameter {param_name}. Can not create sub-component or reference. There is no slot defined for this parameter')
    else:
        raise TypeError(
            f'Error setting parameter {param_name}. Wrong type {type(val)}. The value must be a instance of int, float, str, SimultanObject, SimultanObject')


def create_simultan_component_from_template(cls, **kwargs):
    """

    :param cls:
    :param kwargs:
    @keyword create_undefined_parameters: if True create parameters for also for undefined keys
    @keyword slot_parameter_variable: if True automatically choose to create parameters, sub-components or references
    depending on the content value although a slot is defined in the template for the content
    :return:
    """

    create_undefined_parameters = kwargs.get('create_undefined_parameters', False)
    slot_parameter_variable = kwargs.get('slot_parameter_variable', False)

    comp = create_component()

    # add TYPE parameter:
    type_param = SimParameter('TYPE', '', 0.0)
    type_param.set_TextValue(cls._template_name)
    comp.Parameters.Add(type_param)

    user = kwargs['data_model'].user

    # create parameters:
    for param_name in cls._content:

        val = kwargs.get(param_name, None)
        init_parameter(cls, comp, param_name, val, user, slot_parameter_variable)

        # if val is None:
        #     continue
        # if isinstance(val, (int, float, str)):
        #     if param_name in cls._slots.keys():
        #         if not slot_parameter_variable:
        #             raise TypeError((f'Error initializing instance of {cls.__name__}:\n'
        #                              f'{param_name} is associated with a slot.'
        #                              f'Valid parameter values are SimComponent or SimultanObject.'
        #                              f'but the value is of type {type(val)}.\n'
        #                              f'If this is intentional, initialize with option slot_parameter_variable=True'))
        #
        #     if hasattr(comp, param_name):
        #         setattr(comp, param_name, kwargs.get(param_name))
        #     else:
        #         # create parameter:
        #         unit = str(cls._units.get(param_name, ''))
        #         if isinstance(val, str):
        #             param = create_parameter(name=param_name,
        #                                      value=0.0,
        #                                      unit=unit)
        #             param.set_TextValue(val)
        #         else:
        #             param = create_parameter(name=param_name,
        #                                      value=float(val),
        #                                      unit=unit)
        #             param.set_ValueCurrent(float(val))
        #         comp.Parameters.Add(param)
        # elif isinstance(val, (SimComponent, SimultanObject)):
        #     # if the parameter is associated with a slot:
        #     if param_name in cls._slots.keys():
        #         # create sub component or reference
        #         full_slot_name = cls._slots[param_name]
        #         slot_name, slot_extension = parse_slot(full_slot_name)
        #
        #         if isinstance(val, SimultanObject) or (val is None):
        #             slot = SimSlot(SimSlotBase(slot_name), str(slot_extension))
        #             user = kwargs['data_model'].user
        #             ComponentManagement.AddReferencedComponentSlot(comp, slot, user)
        #             if val is not None:
        #                 ComponentManagement.AddReferencedComponent(comp, slot, val._wrapped_obj, user)
        #         elif isinstance(val, SimComponent):
        #             entry = SimChildComponentEntry(SimSlot(SimSlotBase(slot_name), str(slot_extension)), val)
        #             comp.Components.Add(entry)
        #         else:
        #             raise TypeError(f'Error setting parameter {param_name}. Wrong type {type(val)}. This parameter is associated with a slot. The parameter value must be of type {SimultanObject} or {SimComponent}')
        #     else:
        #         raise TypeError(
        #             f'Error setting parameter {param_name}. Can not create sub-component or reference. There is no slot defined for this parameter')
        # else:
        #     raise TypeError(f'Error setting parameter {param_name}. Wrong type {type(val)}. The value must be a instance of int, float, str, SimultanObject, SimultanObject')

    if create_undefined_parameters:
        logger.warning(f'Using option slot_parameter_variable. This is an experimental feature and may cause errors')
        undef_params = set(kwargs.keys()) - set(cls._content) - {'name',
                                                                 'current_slot',
                                                                 'create_undefined_parameters',
                                                                 'data_model'}

        for param_name in undef_params:
            val = kwargs.get(param_name, None)
            init_parameter(cls, comp, param_name, val, user, slot_parameter_variable)

    return comp


class SlotError(Exception):
    """Exception raised for errors concerning slot."""


class MetaMock(type):
    def __call__(cls, *args, **kwargs):
        """
        Metaclass to implement object initialization either with wrapped_obj or keywords.

        If a wrapped_obj is defined, create new SimultanObject which wraps a SIMULTAN component (wrapped_obj).

        If no 'wrapped_obj' is defined, a new SimComponent is created with the content defined in the template and the
        values are set to the values defined in kwargs.
        """

        obj = cls.__new__(cls, *args, **kwargs)

        wrapped_obj = kwargs.get('wrapped_obj', None)
        if wrapped_obj is None:

            data_model = kwargs.get('data_model', None)
            if data_model is None:
                if list(data_models.data).__len__() == 1:
                    data_model = list(data_models.data)[0]()
                    kwargs['data_model'] = data_model
                else:
                    raise TypeError((f'Error creating new instance of class {cls.__name__}:\n'
                                     f'Any data model was defined. Tried to use default data model but there are multiple datamodels.\n'
                                     f'Define the data model to use with the key: data_model'))

            wrapped_obj = create_simultan_component_from_template(cls, **kwargs)
            if 'name' in kwargs.keys():
                wrapped_obj.Name = kwargs.get('name')
            if 'current_slot' in kwargs.keys():
                value = kwargs.get('current_slot')
                if isinstance(value, str):
                    value = SimSlotBase(value)
                elif isinstance(value, SimSlotBase):
                    pass
                else:
                    raise TypeError('Current slot must be of type str or SimSlotBase')
            elif cls._default_slot is not None:
                value = SimSlotBase(cls._default_slot)
            wrapped_obj.set_CurrentSlot(value)

            data_model.add_component(wrapped_obj)

            init_dict = {}
            init_dict['data_model_id'] = data_model.id
            init_dict['template_parser'] = cls._template_parser
            init_dict['wrapped_obj'] = wrapped_obj
            obj.__init__(*args, **init_dict)
            # instance = cls(**init_dict)
        else:
            obj.__init__(*args, **kwargs)
        return obj


class SimultanObject(object, metaclass=MetaMock):

    # __metaclass__ = MetaMock

    _cls_instances = WeakSet()  # weak set with all created objects
    _create_all = False     # if true all properties are evaluated to create python objects when initialized
    _cls_instances_dict_cache = None

    @classproperty
    def _cls_instances_dict(cls):
        if cls._cls_instances_dict_cache is None:
            cls._cls_instances_dict_cache = dict(zip([x.id for x in cls._cls_instances], [x for x in cls._cls_instances]))
        return cls._cls_instances_dict_cache

    @classproperty
    def cls_instances(cls):
        return list(cls._cls_instances)

    def __new__(cls, *args, **kwargs):

        instance = super().__new__(cls)

        if "_cls_instances" not in cls.__dict__:
            cls._cls_instances = WeakSet()
        try:
            cls._cls_instances.add(instance)
            cls._cls_instances_dict_cache = None
        except Exception as e:
            logger.error(f'Error adding instance {instance} to _cls_instances: {e}')

        return instance

    def __init__(self, *args, **kwargs):
        """
        Initialize a SIMULTAN component from a template class

        There are two options to initialize a SimultanObject:

        1. with a 'wrapped_obj', 'template_parser' and 'data_model_id':
            if the keyword 'wrapped_obj' with a SimComponent is passed, a new SimultanObject is created, which wraps the
            passed SimComponent. Additionally the 'template_parser' and 'data_model_id' must be defined. This is mostly
            intended to be done by the template parser to create python objects.

            Example:
            new_instance = template_class(wrapped_obj=sim_component,
                                          template_parser=self,
                                          data_model_id=self._current_data_model.id)

        2. without a 'wrapped_obj' to create a new SimComponent:

            if no 'data_model' is passed, the default data model is used, which is the first loaded data model

            new_slot_comp_3 = SimultanObject(name='test_name',
                                             current_slot='Element',
                                             Param0='Test Text Value',
                                             Param1='Test Value',
                                             Param2=new_comp_1,
                                             Param3=new_comp_2,
                                             data_model=data_model)

        :param args:
        :param kwargs:

        To creat a new instance wrapping an existing SimComponent:
        @keyword wrapped_obj: SimComponent to be wrapped
        @keyword template_parser: Template parser instance
        @keyword data_model_id: Id of the data model the component belongs to

        If a new SimComponent is created:
        @keyword name: Name of the Component
        @keyword current_slot: Name of the Component's slot (for valid slots see SIMULTAN slot documentation)
        @keyword data_model: Id of the data model the component belongs to

        @keyword create_undefined_parameters: if True create parameters for also for undefined keys
        @keyword slot_parameter_variable: if True automatically choose to create parameters, sub-components or references
        """

        self._wrapped_obj = kwargs.get('wrapped_obj', None)
        self._contained_components = kwargs.get('contained_components', None)
        self._contained_parameters = kwargs.get('contained_parameters', None)
        self._flat_sub_comp_list = kwargs.get('flat_sub_comp_list', None)
        self._referenced_components = kwargs.get('referenced_components', None)
        self._template_parser = kwargs.get('template_parser', None)
        self._data_model_id = kwargs.get('data_model_id', None)

        self._slot_components = None

        # if self._create_all:
        #     _ = self.contained_components
        #     _ = self.contained_parameters
        #     _ = self.referenced_components

        # _ = self.slot_components

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except (KeyError, AttributeError):
            wrapped = object.__getattribute__(self, '_wrapped_obj')
            if wrapped is not None:
                return object.__getattribute__(wrapped, attr)
            else:
                raise KeyError

    def __setattr__(self, attr, value):
        if hasattr(self, '_wrapped_obj'):

            if hasattr(self._wrapped_obj, attr) and (self._wrapped_obj is not None):
                object.__setattr__(self._wrapped_obj, attr, value)
            else:
                object.__setattr__(self, attr, value)
        else:
            object.__setattr__(self, attr, value)

        # if (attr in self.__dict__) or (attr in ['_wrapped_obj',
        #                                         '_contained_components',
        #                                         '_contained_parameters',
        #                                         '_flat_sub_comp_list',
        #                                         '_referenced_components',
        #                                         '_template_parser',
        #                                         '_data_model_id']):
        #
        #     object.__setattr__(self, attr, value)
        # else:
        #     object.__setattr__(self._wrapped_obj, attr, value)

    def __getstate__(self):

        logger.warning(f'__getstate__ in experimental state')

        obj_dict = dict()
        for key in dir(self.__class__):
            if type(getattr(self.__class__, key)) is property:
                print(key)
                obj_dict[key] = getattr(self, key)

        return obj_dict

    def __setstate__(self, state):

        logger.warning(f'__setstate__ in experimental state')

        for key, value in state.items():
            try:
                setattr(self, key, value)
            except AttributeError as e:
                pass

    def __repr__(self):
        return f'{self.name}: ' + object.__repr__(self)

    def __del__(self):
        self.__class__._cls_instances_dict_cache = None

    @property
    def id(self):
        if self._wrapped_obj is not None:
            return self._wrapped_obj.Id

    @property
    def name(self):
        if self._wrapped_obj is not None:
            return self._wrapped_obj.Name

    @name.setter
    def name(self, value: str):
        if self._wrapped_obj is not None:
            self._wrapped_obj.Name = value

    @property
    def contained_components(self):
        if self._contained_components is None:
            if self._wrapped_obj is not None:
                self._contained_components = [self._template_parser.create_python_object(x.Component) for x in self._wrapped_obj.Components.Items]
        return self._contained_components

    @property
    def contained_parameters(self):
        if self._contained_parameters is None:
            if self._wrapped_obj is not None:
                self._contained_parameters = {x.Name: x.get_ValueCurrent() for x in self._wrapped_obj.Parameters.Items}
        return self._contained_parameters

    # @property
    # def flat_sub_comp_list(self):
    #     if self._flat_sub_comp_list is None:
    #         if self._wrapped_obj is not None:
    #             self._flat_sub_comp_list = [self._template_parser.create_python_object(x) for x in self._wrapped_obj.GetFlatSubCompList()]
    #     return self._flat_sub_comp_list

    @property
    def referenced_components(self):
        if self._referenced_components is None:
            if self._wrapped_obj is not None:
                self._referenced_components = [self._template_parser.create_python_object(x.Target) for x in self._wrapped_obj.ReferencedComponents.Items]
        return self._referenced_components

    @property
    def referenced_assets(self):
        return [x.Resource for x in self._wrapped_obj.ReferencedAssets.Items]

    @lru_cache()
    def get_param_index(self, param: str) -> int:
        """
        Return the index of the parameter with the name 'param' in self self._wrapped_obj.Parameters.Items
        :param param: str; Example: 'Area'
        :return: Index of the parameter
        """
        idx = next((i for i, x in enumerate(self._wrapped_obj.Parameters.Items) if x.Name == param), None)
        return idx

    def get_param(self, param: str) -> SimParameterType:
        """
        Return the parameter of the parameter with the name 'param' in self self._wrapped_obj.Parameters.Items
        :param param: str; Example: 'Area'
        :return: SimParameter
        """
        idx = self.get_param_index(param)
        if idx is None:
            raise AttributeError(f'{self} {self.name} {self.id} has no parameter {param}')
        return self._wrapped_obj.Parameters.Items[idx].get_ValueCurrent()

    def set_param(self, param: str, value: float):
        """
        Set the value of a param
        :param param: name of the parameter
        :param value: value of the parameter
        """
        idx = self.get_param_index(param)
        if idx is None:
            raise AttributeError(f'{self} {self.name} has no parameter {param}')
        self._wrapped_obj.Parameters.Items[idx].set_ValueCurrent(value)

    @property
    def current_slot(self):
        return self._wrapped_obj.CurrentSlot

    @current_slot.setter
    def current_slot(self, value):
        if isinstance(value, str):
            value = SimSlotBase(value)
        elif isinstance(value, SimSlotBase):
            pass
        else:
            raise TypeError('Current slot must be of type str or SimSlotBase')
        self._wrapped_obj.set_CurrentSlot(value)

    @property
    def fits_in_slot(self):
        return self._wrapped_obj.CurrentSlot

    @property
    def slot_extension(self):
        """
        Returns the slot extension of the component
        :param
        """
        try:
            return int(re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", self.current_slot)[-1])
        except Exception as e:
            return None

    @property
    def slot_components(self):
        if self._slot_components is None:
            self._slot_components = self.get_slot_components()
        return self._slot_components

    @slot_components.setter
    def slot_components(self, value):
        self._slot_components = value
        
    @property
    def parent(self):
        if not hasattr(self._wrapped_obj, 'Parent'):
            return None

        if self._wrapped_obj.Parent is not None:
            return self._template_parser.create_python_object(self._wrapped_obj.Parent)
        else:
            return None

    @property
    def referenced_by(self):
        return set([self._template_parser.create_python_object(x.Target) for x in self._wrapped_obj.ReferencedBy if not x.Target == self._wrapped_obj])

    def get_slot_components(self):
        """
        Return a DataFrame with the slot components.
        Dataframe columns: 'comp': component, 'slot': slot name, 'slot_extension': slot extension, 'comp_type': 0: subcomponent, 1: referenced component
        :return:
        """
        sc_df = pd.DataFrame(columns=['comp', 'slot', 'slot_extension', 'comp_type'])

        # subcomponents
        for comp in self._wrapped_obj.Components.Items:
            c_slot = comp.Slot.SlotBase.Base
            c_slot_extension = comp.Slot.SlotExtension

            sc_df = sc_df.append(
                pd.DataFrame(data={'comp': [self._template_parser.create_python_object(comp.Component)],
                                   'slot': [c_slot],
                                   'slot_extension': c_slot_extension,
                                   'comp_type': 0}),
                ignore_index=True)

        # referenced components
        for comp in self._wrapped_obj.ReferencedComponents.Items:
            c_slot = comp.Slot.SlotBase.Base
            c_slot_extension = comp.Slot.SlotExtension

            sc_df = sc_df.append(
                pd.DataFrame(data={'comp': [self._template_parser.create_python_object(comp.Target)],
                                   'slot': [c_slot],
                                   'slot_extension': c_slot_extension,
                                   'comp_type': 1}),
                ignore_index=True)

        return sc_df

    def add_sub_component(self,
                          component: Union[SimComponentType, SimultanObject],
                          slot_name: str,
                          slot_extension: Union[int, float, str],
                          alter_slot=False):
        """
        Add a sub-component to this component
        :param component: Component to add; Type: SimComponent or SimultanObject
        :param slot_name: name of the slot of the created sub-component
        :param slot_extension: slot extension
        :param alter_slot: if True change the slot of the component if it does not match the current slot of the component
        """

        sub_comp_slot = SimSlot(SimSlotBase(slot_name), str(slot_extension))

        if isinstance(component, SimultanObject):
            component = component._wrapped_obj

        if component.CurrentSlot is not None:
            if alter_slot:
                component.CurrentSlot = SimSlotBase(slot_name)
            else:
                raise SlotError(f'Component: {component.Name, component.Id.GlobalId} has already asigned slot:\n{component.CurrentSlot.Base}\nThis slot does not match template\'s slot:\n{slot_name}')
        else:
            component.CurrentSlot = SimSlotBase(slot_name)

        if not component.Id == SimId.Empty:
            component.Id = SimId.Empty

        entry = SimChildComponentEntry(sub_comp_slot, component)
        self._wrapped_obj.Components.Add(entry)

        self.slot_components = self.get_slot_components()

    def remove_sub_component(self,
                             component: Union[SimComponent, SimultanObject] = None,
                             slot_name: Optional[str] = None,
                             slot_extension: Optional[Union[int, float, str]] = None):
        """
        Removes a sub component; Sub component defined either by component or slot_name and slot_extension
        :param component: Sub component to remove
        :param slot_name: [Optional]: slot name
        :param slot_extension: Optional]: slot extension
        """
        entry = None

        if isinstance(component, SimultanObject):
            component = component._wrapped_obj

        if component is not None:
            entry = next((x for x in self._wrapped_obj.Components.Items if x.Component == component), None)

        if None not in [slot_name, slot_extension, entry]:
            entry = next((x for x in self._wrapped_obj.Components.Items
                          if all([x.Slot.SlotBase.Base == slot_name,
                                  x.Slot.SlotExtension == slot_extension])),
                         None)

        if entry is not None:
            self._wrapped_obj.Components.Remove(entry)
        else:
            logger.warning(f'Could not remove sub component. Entry not found')
            raise ValueError(f'Could not remove sub component. Entry not found')

        self.slot_components = self.get_slot_components()

    def add_component_reference(self,
                                component: Union[SimComponentType, SimultanObject],
                                slot_name: str,
                                slot_extension: Union[int, float, str]):
        """
        Add a reference of component to self
        :param component: Instance of PySimultan.default_types.SimultanObject, PySimultan.default_types.List, PySimultan.default_types.ReferenceList
        :param slot_name: Name of the slot
        :param slot_extension:
        """
        slot = SimSlot(SimSlotBase(slot_name), str(slot_extension))
        user = self._template_parser.current_data_model.user
        ComponentManagement.AddReferencedComponentSlot(self._wrapped_obj, slot, user)
        if isinstance(component, SimultanObject):
            component = component._wrapped_obj
        ComponentManagement.AddReferencedComponent(self._wrapped_obj, slot, component, user)

        self.slot_components = self.get_slot_components()

    def remove_component_reference(self, component: Union[SimComponentType, SimultanObject]):
        """
        Removes the reference to a component.
        :param component: Component which's reference to remove
        """
        if isinstance(component, SimultanObject):
            component = component._wrapped_obj
        ComponentManagement.RemoveReferencedComponent_Level0(self._wrapped_obj, component, True)

        self.slot_components = self.get_slot_components()

    def add_parameter(self, name: str, unit: str, value: Union[int, float], param_type: str = 'int'):
        """
        Add a parameter to this component. Additionally a property is added to access the parameter from this component.
        :param name: name of the parameter
        :param unit: unit of the parameter; Example: 'kg'
        :param value: value of the parameter: Example: 15.875
        :param param_type: type of the parameter; if param_type == 'str': param.get_TextValue()
               else: param.get_ValueCurrent() is returned
        """
        from .template_tools import add_properties

        new_param = SimParameter(name, unit, float(value))
        self._wrapped_obj.Parameters.Add(new_param)
        object.__setattr__(self, name, add_properties(name, param_type=param_type))

    def add_asset(self, resource: ContainedResourceFileEntryType):
        """
        Add a reference to a resource (file) to this component
        :param resource: Instance of ParameterStructure.Assets.ContainedResourceFileEntry
        """
        ComponentMapping.AddAsset(self._wrapped_obj, resource, '')

    def assign_table_to_parameter(self, param_name: str, table: SimMultiValueBigTableType):
        """
        set a prarameter's value to a SimMultiValueBigTable value
        :param param_name: name of the parameter
        :param table: ParameterStructure.Values.SimMultiValueBigTable
        """
        idx = self.get_param_index(param_name)
        param = self._wrapped_obj.Parameters.Items[idx]
        param.set_MultiValuePointer(table.DefaultPointer)

    def replace(self, key: str, new_component: Union[SimComponentType, SimultanObject]):
        """
        Replace a existing Component or reference associated with a attribute (parameter name) with a new component
        or reference.

        There are six different cases:

        1. The old component is a sub-component and the new component is a SimComponent:
            the old component is exchanged with the new component

        2. The old component is a sub-component and the new component is a SimultanObject:
            the old component deleted and a reference to the SimultanObject is created

        3. The old component is a reference and the new component is a SimComponent:
            the reference to the old component is deleted a new sub-component is created

        4. The old component is a reference and the new component is a SimultanObject:
            the reference to the old component updated to reference the new component

        5. There is no old component and the new component is a SimComponent:
            A new sub-component is created

        6. There is no old component and the new component is a SimultanObject:
            A new reference is created

        References of other components to the old component are updated to the new component.

        :param key: the name of the attribute (parameter name)
        :param new_component: the new component to replace the old component
        """
        full_slot_name = self._slots.get(key, None)
        slot_name, slot_extension = parse_slot(full_slot_name)

        component = getattr(self, key)

        if component is None:
            if new_component is None:
                pass
            if isinstance(new_component, SimultanObject):
                self.add_component_reference(component=new_component,
                                             slot_name=slot_name,
                                             slot_extension=slot_extension)
            elif isinstance(new_component, SimComponent):
                self.add_sub_component(component=new_component,
                                       slot_name=slot_name,
                                       slot_extension=slot_extension,
                                       alter_slot=True)

        # old component is not None:
        else:
            idx = self.slot_components.index[np.array([x.Id for x in self.slot_components['comp']]) == component.Id][0]

            references = []
            for ref_comp in set(component._wrapped_obj.ReferencedBy):
                ref = next((x for x in ref_comp.ReferencedComponents.Items if x.Target == component._wrapped_obj), None)
                references.append(ref)

            new_sim_component = new_component

            # old component is sub component
            if self.slot_components.iloc[idx].comp_type == 0:
                if isinstance(new_component, SimultanObject):
                    if new_component is not None:
                        new_sim_component = new_component._wrapped_obj
                        # add reference to component:
                        self.add_component_reference(component=new_component,
                                                     slot_name=slot_name,
                                                     slot_extension=slot_extension)
                    self.remove_sub_component(component)

                elif isinstance(new_component, SimComponent):
                    if new_component is not None:
                        comp_ref = next((x for x in self._wrapped_obj.Components.Items
                                    if ((x.Slot.SlotBase.Base == slot_name) & (x.Slot.SlotExtension == slot_extension)))
                                   , None)
                        new_component.CurrentSlot = comp_ref.Slot.SlotBase
                        comp_ref.Component = new_component

                elif new_component is None:
                    self.remove_sub_component(component)

            # old component is reference
            elif self.slot_components.iloc[idx].comp_type == 1:
                ref = next((x for x in self._wrapped_obj.ReferencedComponents.Items
                            if ((x.Slot.SlotBase.Base == slot_name) & (
                        x.Slot.SlotExtension == slot_extension))), None)
                if isinstance(new_component, SimultanObject):
                    new_sim_component = new_component._wrapped_obj
                    ref.Target = new_component._wrapped_obj
                elif isinstance(new_component, SimComponent):
                    self.remove_component_reference(component)
                    self.add_sub_component(new_component)
                elif new_component is None:
                    self.remove_component_reference(component)

            for ref in references:
                ref.Target = new_sim_component

        # clear the cache of the attributes getter:
        getattr(self.__class__, key).fget.cache_clear()

        # update the 'slot_components'
        self.slot_components = self.get_slot_components()


class List(UserList):

    _create_all = False     # if true all properties are evaluated to create python objects when initialized

    def __init__(self, *args, **kwargs):
        self._wrapped_obj = kwargs.get('wrapped_obj', None)
        self._contained_components = kwargs.get('contained_components', None)
        self._contained_parameters = kwargs.get('contained_parameters', None)
        self._template_parser = kwargs.get('template_parser', None)
        self._data_model_id = kwargs.get('data_model_id', None)

        # if self._create_all:
        #     _ = self.contained_components
        #     _ = self.contained_parameters

    @property
    def data(self):
        if self._wrapped_obj is None:
            return
        components = [x.Component for x in self._wrapped_obj.Components.Items]
        ref_components = [x.Target for x in self._wrapped_obj.ReferencedComponents.Items]
        all_components = [*components, *ref_components]

        slots = [*[x.Slot for x in self._wrapped_obj.Components.Items],
                 *[x.Slot for x in self._wrapped_obj.ReferencedComponents.Items]]

        try:
            indices = sort_slots(slots)
            return [x for _, x in sorted(zip(indices, all_components))]
        except TypeError as e:
            logger.warning(f'Could not sort list {all_components}:\n{e}')
            return all_components

    def __getitem__(self, i):
        if isinstance(i, slice):
            if self._template_parser is None:
                return self.__class__(self.data[i])
            return [self._template_parser.create_python_object(x) for x in self.__class__(self.data[i])]
        else:
            if self._template_parser is None:
                return self.data[i]
            return self._template_parser.create_python_object(self.data[i])

    def __repr__(self):
        return f'{self.name}: ' + repr(list(self.data))

    @property
    def contained_components(self):
        if self._contained_components is None:
            if self._wrapped_obj is not None:
                self._contained_components = [self._template_parser.create_python_object(x.Component) for x in self._wrapped_obj.Components.Items]
        return self._contained_components

    @property
    def contained_parameters(self):
        if self._contained_parameters is None:
            if self._wrapped_obj is not None:
                self._contained_parameters = {x.Name: x.get_ValueCurrent() for x in self._wrapped_obj.Parameters.Items}
        return self._contained_parameters

    @property
    def name(self):
        if self._wrapped_obj is not None:
            if hasattr(self._wrapped_obj, 'Name'):
                return self._wrapped_obj.Name

    @name.setter
    def name(self, value):
        if self._wrapped_obj is not None:
            self._wrapped_obj.Name = value

    @property
    def parent(self):
        if not hasattr(self._wrapped_obj, 'Parent'):
            return None

        if self._wrapped_obj.Parent is not None:
            return self._template_parser.create_python_object(self._wrapped_obj.Parent)
        else:
            return None

    @property
    def current_slot(self):
        return self._wrapped_obj.CurrentSlot

    @current_slot.setter
    def current_slot(self, value):
        if isinstance(value, str):
            value = SimSlotBase(value)
        elif isinstance(value, SimSlotBase):
            pass
        else:
            raise TypeError('Current slot must be of type str or SimSlotBase')
        self._wrapped_obj.set_CurrentSlot(value)

    @property
    def referenced_by(self):
        return set([self._template_parser.create_python_object(x.Target) for x in self._wrapped_obj.ReferencedBy if
                    not x.Target == self._wrapped_obj])


class ComponentList(UserList):

    _create_all = False  # if true all properties are evaluated to create python objects when initialized

    def __init__(self, *args, **kwargs):
        self._wrapped_obj = kwargs.get('wrapped_obj', None)
        self._contained_components = kwargs.get('contained_components', None)
        self._contained_parameters = kwargs.get('contained_parameters', None)
        self._template_parser = kwargs.get('template_parser', None)
        self._data_model_id = kwargs.get('data_model_id', None)

        # if self._create_all:
        #     _ = self.contained_components
        #     _ = self.contained_parameters

    @property
    def data(self):
        if self._wrapped_obj is None:
            return
        components = [x.Component for x in self._wrapped_obj.Components.Items]
        try:
            indices = sort_component_list(self._wrapped_obj.Components.Items)
            return [x for _, x in sorted(zip(indices, components))]
        except TypeError as e:
            logger.warning(f'Could not sort list {components}:\n{e}')
            return components

    def __getitem__(self, i):
        if isinstance(i, slice):
            if self._template_parser is None:
                return self.__class__(self.data[i])
            return [self._template_parser.create_python_object(x) for x in self.__class__(self.data[i])]
        else:
            if self._template_parser is None:
                return self.data[i]
            return self._template_parser.create_python_object(self.data[i])

    def __repr__(self):
        return f'{self.name}: ' + repr(list(self.data))

    @property
    def contained_components(self):
        if self._contained_components is None:
            if self._wrapped_obj is not None:
                self._contained_components = [self._template_parser.create_python_object(x.Component) for x in
                                              self._wrapped_obj.Components.Items]
        return self._contained_components

    @property
    def contained_parameters(self):
        if self._contained_parameters is None:
            if self._wrapped_obj is not None:
                self._contained_parameters = {x.Name: x.get_ValueCurrent() for x in self._wrapped_obj.Parameters.Items}
        return self._contained_parameters

    @property
    def name(self):
        if self._wrapped_obj is not None:
            if hasattr(self._wrapped_obj, 'Name'):
                return self._wrapped_obj.Name

    @name.setter
    def name(self, value):
        if self._wrapped_obj is not None:
            self._wrapped_obj.Name = value

    @property
    def parent(self):
        if not hasattr(self._wrapped_obj, 'Parent'):
            return None

        if self._wrapped_obj.Parent is not None:
            return self._template_parser.create_python_object(self._wrapped_obj.Parent)
        else:
            return None

    @property
    def current_slot(self):
        return self._wrapped_obj.CurrentSlot

    @current_slot.setter
    def current_slot(self, value):
        if isinstance(value, str):
            value = SimSlotBase(value)
        elif isinstance(value, SimSlotBase):
            pass
        else:
            raise TypeError('Current slot must be of type str or SimSlotBase')
        self._wrapped_obj.set_CurrentSlot(value)

    @property
    def referenced_by(self):
        return set([self._template_parser.create_python_object(x.Target) for x in self._wrapped_obj.ReferencedBy if
                    not x.Target == self._wrapped_obj])


class ReferenceList(UserList):

    def __init__(self, *args, **kwargs):
        self._wrapped_obj = kwargs.get('wrapped_obj', None)
        self._contained_components = kwargs.get('contained_components', None)
        self._contained_parameters = kwargs.get('contained_parameters', None)
        self._template_parser = kwargs.get('template_parser', None)
        self._data_model_id = kwargs.get('data_model_id', None)

    def __getitem__(self, i):
        if isinstance(i, slice):
            if self._template_parser is None:
                return self.__class__(self.data[i])
            return [self._template_parser.create_python_object(x) for x in self.__class__(self.data[i])]
        else:
            if self._template_parser is None:
                return self.data[i]
            return self._template_parser.create_python_object(self.data[i])

    def __repr__(self):
        return f'{self.name}: ' + repr(list(self.data))

    @property
    def data(self):
        if self._wrapped_obj is None:
            return

        ref_components = [x.Target for x in self._wrapped_obj.ReferencedComponents.Items]
        try:
            indices = sort_references(self._wrapped_obj.ReferencedComponents.Items)
            return [x for _, x in sorted(zip(indices, ref_components))]
        except TypeError as e:
            logger.warning(f'Could not sort list {ref_components}:\n{e}')
            return ref_components

    @property
    def contained_components(self):
        if self._contained_components is None:
            if self._wrapped_obj is not None:
                self._contained_components = [self._template_parser.create_python_object(x) for x in
                                              self._wrapped_obj.Components]
        return self._contained_components

    @property
    def contained_parameters(self):
        if self._contained_parameters is None:
            if self._wrapped_obj is not None:
                self._contained_parameters = {x.Name: x.get_ValueCurrent() for x in
                                              self._wrapped_obj.Parameters.Items}
        return self._contained_parameters

    @property
    def name(self):
        if self._wrapped_obj is not None:
            if hasattr(self._wrapped_obj, 'Name'):
                return self._wrapped_obj.Name

    @name.setter
    def name(self, value):
        if self._wrapped_obj is not None:
            self._wrapped_obj.Name = value

    @property
    def parent(self):
        if not hasattr(self._wrapped_obj, 'Parent'):
            return None

        if self._wrapped_obj.Parent is not None:
            return self._template_parser.create_python_object(self._wrapped_obj.Parent)
        else:
            return None

    @property
    def current_slot(self):
        return self._wrapped_obj.CurrentSlot

    @current_slot.setter
    def current_slot(self, value):
        if isinstance(value, str):
            value = SimSlotBase(value)
        elif isinstance(value, SimSlotBase):
            pass
        else:
            raise TypeError('Current slot must be of type str or SimSlotBase')
        self._wrapped_obj.set_CurrentSlot(value)

    @property
    def referenced_by(self):
        return set([self._template_parser.create_python_object(x.Target) for x in self._wrapped_obj.ReferencedBy if
                    not x.Target == self._wrapped_obj])


class ValueField(pd.DataFrame):

    _metadata = pd.DataFrame._metadata + ['_wrapped_obj', '_template_parser', '_data_model_id']

    def __init__(self, *args, **kwargs):

        # self._wrapped_obj = kwargs.get('wrapped_obj')
        value_field = kwargs.pop('wrapped_obj', None)
        if isinstance(value_field, SimMultiValuePointer):
            value_field = value_field.ValueField
        self._wrapped_obj = value_field
        self._template_parser = kwargs.get('template_parser', None)
        self._data_model_id = kwargs.get('data_model_id', None)

        row_headers = [x.Name for x in self._wrapped_obj.RowHeaders.Items]
        column_headers = [x.Name for x in self._wrapped_obj.ColumnHeaders.Items]
        values = self._wrapped_obj.Values

        super().__init__(dict(zip(column_headers, np.array(values).T)),  index=row_headers)

    @property
    def base_class_view(self):
        # use this to view the base class, needed for debugging in some IDEs.
        return pd.DataFrame(self)


class BuildInFace(SimultanObject):

    def __init__(self, *args, **kwargs):
        SimultanObject.__init__(self, *args, **kwargs)

        self._geo_instances = kwargs.get('geo_instances', None)
        self._boundaries = kwargs.get('boundaries', None)

    @property
    def geo_ids(self):
        if self.geo_instances is not None:
            return [x.Id for x in self.geo_instances]

    @property
    def area(self):
        # idx = next((i for i, x in enumerate(self._wrapped_obj.ContainedParameters.Items) if x.Name == 'A'), None)
        # param = self._wrapped_obj.ContainedParameters.Items[idx]
        # return param.get_ValueCurrent()
        return self.get_param('A')

    @property
    def geo_ids(self):
        geo_ids = []
        for item in self._wrapped_obj.Instances.Items:

            geom_placement = next(x for x in item.Placements.Items if isinstance(x, SimInstancePlacementGeometry))

            file_id = geom_placement.FileId
            geometry_id = geom_placement.GeometryId

            geo_ids.append({'FileId': file_id,
                           'GeometryId': geometry_id})
        return geo_ids

    @property
    def geo_instances(self):
        if self._geo_instances is None:
            self._geo_instances = self.get_geo_instances()
        return self._geo_instances

    @geo_instances.setter
    def geo_instances(self, value):
        self._geo_instances = value

    @property
    def boundaries(self):
        if self._boundaries is None:
            if self.geo_instances is not None:
                self._boundaries = [x.boundary for x in self.geo_instances]
        return self._boundaries

    @property
    def construction(self):
        obj = next((x.Target for x in self._wrapped_obj.ReferencedComponents.Items if x.ReferenceFunction.SlotFull == 'Aufbau_0AG0'), None)
        return self._template_parser.create_python_object(obj)

    def get_geo_instances(self):
        try:
            geo_instances = []

            for item in self._wrapped_obj.Instances.Items:

                if item.Placements.Items.__len__() == 0:
                    continue

                geom_placement = next(x for x in item.Placements.Items if isinstance(x, SimInstancePlacementGeometry))

                file_id = geom_placement.FileId
                geometry_id = geom_placement.GeometryId

                # geo_model = self._template_parser.data_models[self._data_model_id].get_typed_model_by_file_id(file_id)
                geo_model = self._template_parser.typed_geo_models[file_id]
                geo_instance = geo_model.get_face_by_id(geometry_id)

                # geo_instance = self._template_parser.data_models[self._data_model_id].typed_geo_models[file_id].get_face_by_id(geometry_id)

                geo_instances.append(geo_instance)

            return geo_instances
        except Exception as e:
            logger.error(f'BuildInFace {self.name}; {self.id}: Error while getting geo instances: {e}')
            return []

    def associate_with_geometry(self, face):

        try:
            self.InstanceType = SimInstanceType.Entity3D
        except Exception as e:
            raise e

        exch = face.geometry_model.template_parser.current_data_model.exch
        exch.Associate(self, face._wrapped_obj)


class BuildInVolume(SimultanObject):

    def __init__(self, *args, **kwargs):
        """
        Default python class for SIMULTAN 'Geometrische_Volumina' Slot
        Grundflächen und Rauminhalte nach DIN 277

        @keyword geo_instances: List of geometric volume instances of type geo_default_types.GeometricVolume
        @keyword surfaces: List of
        """
        SimultanObject.__init__(self, *args, **kwargs)

        self._geo_instances = kwargs.get('geo_instances', None)
        self._surfaces = kwargs.get('surfaces', None)
        self._volumes = kwargs.get('volumes', None)

    @property
    def volumes(self):
        return self.geo_instances

    @property
    def geo_faces(self):
        """
        Faces of the Geometry-Model
        :return: list with faces of type geo_defaut_types.GeometricFace
        """
        faces = []
        try:
            [faces.extend(x.faces) for x in self.geo_instances if x is not None]
        except AttributeError as e:
            raise e
        return faces

    @property
    def face_components(self):
        return None

    @property
    def geo_instances(self):
        if self._geo_instances is None:
            self._geo_instances = self.get_geo_instances()
        return self._geo_instances

    @geo_instances.setter
    def geo_instances(self, value):
        self._geo_instances = value

    @property
    @lru_cache(maxsize=None)
    def v_a(self):
        return next((x.ValueCurrent for x in self._wrapped_obj.Parameters.Items if x.Name == 'Vᴀ'), None)

    @property
    @lru_cache(maxsize=None)
    def v_nri(self):
        """
        Netto-Rauminhalt NRI: Anteil des Brutto-Rauminhalts (BRI), der das Volumen über der Netto-Raumfläche (NRF) umfasst; DIN 277
        :return:
        """
        return next((x.ValueCurrent for x in self._wrapped_obj.Parameters.Items if x.Name == 'Vɴʀɪ'), None)

    @property
    @lru_cache(maxsize=None)
    def v_bri(self):
        """
        Brutto-Rauminhalt BRI: gesamtes Volumen eines Bauwerks oder eines Geschosses, das sich in Netto-Rauminhalt (NRI) und
        Konstruktions-Rauminhalt (KRI) gliedert; DIN 277
        :return:
        """
        return next((x.ValueCurrent for x in self._wrapped_obj.Parameters.Items if x.Name == 'Vᴃʀɪ'), None)

    @property
    @lru_cache(maxsize=None)
    def a_bgf(self):
        """
        Brutto-Grundfläche; gesamte Grundfläche eines Bauwerks oder eines Geschosses, die sich in Netto-Raumfläche (NRF)
        und Konstruktions-Grundfläche (KGF) gliedert; DIN 277
        :return:
        """
        return next((x.ValueCurrent for x in self._wrapped_obj.Parameters.Items if x.Name == 'Aᴃɢꜰ'), None)

    @property
    @lru_cache(maxsize=None)
    def a_ngf(self):
        """
        Netto-Grundfläche; DIN 277
        :return:
        """
        return next((x.ValueCurrent for x in self._wrapped_obj.Parameters.Items if x.Name == 'Aɴɢꜰ'), None)

    def get_geo_instances(self):

        geo_instances = []

        for item in self._wrapped_obj.Instances.Items:

            try:
                geom_placement = next(x for x in item.Placements.Items if isinstance(x, SimInstancePlacementGeometry))
            except Exception as e:
                logger.error(f'{self.__class__.__name__} {self.name} {self.id}: Could not find Geometry Placement for GeometryInstance {item}')
                if continue_on_error:
                    continue
                else:
                    raise e

            file_id = geom_placement.FileId
            geometry_id = geom_placement.GeometryId

            # geo_model = self._template_parser.data_models[self._data_model_id].get_typed_model_by_file_id(file_id)
            geo_model = self._template_parser.typed_geo_models[file_id]
            geo_instance = geo_model.get_zone_by_id(geometry_id)

            if geo_instance is None:
                logger.error(f'{self.__class__.__name__} {self.name} {self.id}: Geometry Instance with file id: {file_id}, geometry id: {geometry_id} not found')
                if not continue_on_error:
                    raise KeyError(f'{self.__class__.__name__} {self.name} {self.id}: Geometry Instance with file id: {file_id}, geometry id: {geometry_id} not found')

            else:
                geo_instances.append(geo_instance)

        return geo_instances


class BuildInZone(SimultanObject):

    def __init__(self, *args, **kwargs):
        """

        """
        SimultanObject.__init__(self, *args, **kwargs)

    @property
    @lru_cache(maxsize=None)
    def volumes(self):
        return [x for x in self.contained_components if x._wrapped_obj.FitsInSlots[0] == 'Geometrische_Volumina']

    @property
    @lru_cache(maxsize=None)
    def faces(self):
        return [x for x in self.contained_components if x._wrapped_obj.FitsInSlots[0] == 'Geometrische_Flächen']


class BaseBuildInConstruction(SimultanObject):

    def __init__(self, *args, **kwargs):
        """
        Default implementation for a wall construction (InstanceType == InstanceType.ALIGNED_WITH).
        """
        SimultanObject.__init__(self, *args, **kwargs)
        self.check_type()

    @property
    def is_window(self):
        if self.get_param_index('gVergl') is None:
            return False
        else:
            return True

    def check_type(self):
        if self.is_window:
            object.__setattr__(self, '__class__', BuildInWindowConstruction)
        else:
            object.__setattr__(self, '__class__', BuildInWallConstruction)


class BuildInWallConstruction(BaseBuildInConstruction):

    def __init__(self, *args, **kwargs):
        """
        Default implementation for a wall construction (InstanceType == InstanceType.ALIGNED_WITH).
        """
        BaseBuildInConstruction.__init__(self, *args, **kwargs)

    @property
    def total_thickness(self):
        idx = self.get_param_index('DickeGes')
        # idx = next((i for i, x in enumerate(self._wrapped_obj.ContainedParameters.Items) if x.Name == 'DickeGes'), None)
        param = self._wrapped_obj.Parameters.Items[idx]
        return param.get_ValueCurrent()

    @property
    def layers(self):
        layers = [self._template_parser.create_python_object(x.Component, template_name='BuildInMaterialLayer') for x in self._wrapped_obj.Components.Items]

        # sort the layers by their slot_extension:
        # slot_extensions = [x.slot_extension for x in layers]
        slot_extensions = [int(x.Slot.SlotExtension) for x in self._wrapped_obj.Components.Items]
        # test with rotated
        # layers = layers[1:] + layers[:1]

        return [x for _, x in sorted(zip(slot_extensions, layers))]


class BuildInWindowConstruction(BaseBuildInConstruction):

    def __init__(self, *args, **kwargs):
        """
        Default implementation for a window construction (InstanceType == InstanceType.ALIGNED_WITH).
        """
        BaseBuildInConstruction.__init__(self, *args, **kwargs)

    @property
    def d(self):
        """
        layer thickness in m
        :param
        """
        try:
            return self.get_param('d')
        except AttributeError:
            return self.get_param('Dicke')

    @d.setter
    def d(self, value):
        # idx = self.get_param_index('d')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('d', value)

    @property
    def eps(self):
        """
        eps
        :param
        """
        return self.get_param('eps')

    @eps.setter
    def eps(self, value):
        # idx = self.get_param_index('eps')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('eps', value)

    @property
    def gVergl(self):
        """
        Gesamtenergiedurchlassgrad
        :param
        """
        return self.get_param('gVergl')

    @gVergl.setter
    def gVergl(self, value):
        # idx = self.get_param_index('gVergl')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('gVergl', value)

    @property
    def curtain_position(self):
        """

        :param
        """
        return self.get_param('LageBehang')

    @curtain_position.setter
    def curtain_position(self, value):
        # idx = self.get_param_index('LageBehang')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('LageBehang', value)

    @property
    def openability(self):
        """
        openability of a window; 1=vollständig  0.1=kippen
        :param
        """
        return self.get_param('Öffenbarkeit')

    @openability.setter
    def openability(self, value):
        # idx = self.get_param_index('Öffenbarkeit')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('Öffenbarkeit', value)

    @property
    def frame_width(self):
        """
        frame width in m
        :param
        """
        return self.get_param('Rahmenbreite')

    @frame_width.setter
    def frame_width(self, value):
        # idx = self.get_param_index('Rahmenbreite')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('Rahmenbreite', value)

    @property
    def u_f(self):
        """
        U-Wert Rahmen in W/m²K
        :param
        """
        return self.get_param('Uf')

    @u_f.setter
    def u_f(self, value):
        # idx = self.get_param_index('Uf')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('Uf', value)

    @property
    def u_g(self):
        """
        U-Wert Glas in W/m²K
        :param
        """
        return self.get_param('Ug')

    @u_g.setter
    def u_g(self, value):
        self.set_param('Ug', value)

    @property
    def alpha_curtain(self):
        """
        Absorption Behang
        :param
        """
        return self.get_param('αeB')

    @alpha_curtain.setter
    def alpha_curtain(self, value):
        self.set_param('αeB', value)

    @property
    def rho_curtain(self):
        """
        Reflexion Behang
        :param
        """
        return self.get_param('ρeB')

    @rho_curtain.setter
    def rho_curtain(self, value):
        self.set_param('ρeB', value)

    @property
    def tau_curtain(self):
        """
        Transmission Behang
        :param
        """
        return self.get_param('τeB')

    @tau_curtain.setter
    def tau_curtain(self, value):
        self.set_param('τeB', value)

    @property
    def psi(self):
        """
        Transmission Behang
        :param
        """
        return self.get_param('ψ')

    @psi.setter
    def psi(self, value):
        self.set_param('ψ', value)


class BuildInMaterialLayer(SimultanObject):

    def __init__(self, *args, **kwargs):
        """
        Default implementation for a material layer of a wall construction.
        """
        SimultanObject.__init__(self, *args, **kwargs)
        print('done')

    @property
    def absorption_rate(self):
        """
        absorption rate (accoustic?)
        :param
        """
        return self.get_param('aGr')

    @absorption_rate.setter
    def absorption_rate(self, value):
        # idx = self.get_param_index('aGr')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('aGr', value)

    @property
    def c(self):
        """
        specific heat capacity in J/kgK
        :param
        """
        return self.get_param('c')

    @c.setter
    def c(self, value):
        # idx = self.get_param_index('c')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('c', value)

    @property
    def d(self):
        """
        layer thickness in m
        :param
        """
        return self.get_param('d')

    @d.setter
    def d(self, value):
        # idx = self.get_param_index('d')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('d', value)

    @property
    def w20(self):
        """
        Ausgleichsfeuchte bei rli 20%
        :param
        """
        return self.get_param('w20')

    @w20.setter
    def w20(self, value):
        # idx = self.get_param_index('w20')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('w20', value)

    @property
    def w80(self):
        """
        Ausgleichsfeuchte bei rli 80%
        :param
        """
        return self.get_param('w80')

    @w80.setter
    def w80(self, value):
        # idx = self.get_param_index('w80')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('w80', value)

    @property
    def heat_conductivity(self):
        """
        heat conductivity in W/mK
        :param
        """
        return self.get_param('λ')

    @heat_conductivity.setter
    def heat_conductivity(self, value):
        # idx = self.get_param_index('λ')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('λ', value)

    @property
    def mu(self):
        """
        Wasserdampfdiffusionswiderstand
        :param
        """
        return self.get_param('μ')

    @mu.setter
    def mu(self, value):
        # idx = self.get_param_index('μ')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('μ', value)

    @property
    def rho(self):
        """
        Rohdichte in kg/m³
        :param
        """
        return self.get_param('ρ')

    @rho.setter
    def rho(self, value):
        # idx = self.get_param_index('ρ')
        # self._wrapped_obj.ContainedParameters.Items[idx].set_ValueCurrent(value)
        self.set_param('ρ', value)


def create_component(name=None, parameters=None, slot=ComponentUtils.COMP_SLOT_UNDEFINED):
    """
    Creates a new SIMULTAN Component, optional add parameters
    :param name: Name of the component
    :param parameters: dictionary with parameters: {<parameter_name>: [<value>, <unit>]};
    Example: {'length': [10, 'm'], 'weight': [13.0, 'kg']}
    :param slot: Component Slot, sting or ComponentUtils
    :return: SimComponent
    """
    new_comp = SimComponent()

    if name is not None:
        new_comp.Name = 'Test'

    # set parameters
    if parameters is not None:
        for key, value in parameters.items():
            new_comp.Parameters.Add(create_parameter(name=key,
                                                     value=value[0],
                                                     unit=value[1]))
    # set slot:
    new_comp.CurrentSlot = SimSlotBase(slot)
    return new_comp
