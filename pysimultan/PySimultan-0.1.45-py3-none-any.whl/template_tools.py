from ruamel.yaml import YAML, yaml_object, add_representer
from .config import yaml
import io
import colorlog
from uuid import uuid4
import typing

from yamale.readers.yaml_reader import _parsers
import yamale


from collections import UserList
from .default_types import SimultanObject
from .default_types import List as SimultanList
from .default_types import ValueField, BuildInFace, BuildInVolume, BuildInZone, BaseBuildInConstruction, BuildInMaterialLayer, ReferenceList
from .geo_default_types import geometry_types
from .geometry import GeometryModel
from .utils import parse_slot

from functools import lru_cache

from System.Linq import Enumerable
from ParameterStructure.Values import SimMultiValuePointer
from .ParameterStructure.Components import SimComponent

from typing import List as TypeList
from typing import NewType, Union

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 importlib_resources.
    import importlib_resources as pkg_resources

from . import resources

with pkg_resources.path(resources, 'schema.yaml') as r_path:
    schema_file = str(r_path)


logger = colorlog.getLogger('PySimultan')


template_classes = {}


# create the class for the templates
@yaml_object(yaml)
class Template(object):

    yaml_tag = u'!Template:'

    def __init__(self, *args, **kwargs):
        """ Template class to define how SIMULTAN SimComponents are imported and parsed

        :param args:
        :param kwargs:

        @keyword template_name: Name of the Template. This name is the name of the created Python class and used for
        TYPE matching the SIMULTAN SimComponent
        @keyword template_id: ID of the template; int
        @keyword inherits_from: name of the python template or the template instance this template inherits from
        @keyword content: List of attribute names
        @keyword documentation: Entry to document the template; str
        @keyword units: units of the content. Dictionary
        @keyword types: Dictionary with the type of the content. if the type is 'str' get_TextValue() is returned, param.get_ValueCurrent() otherwise
        @keyword slots: Dictionary with the name of the content and the name of the slot where it is expected. The expected slot is a string
        @keyword default_slot: Default slot name for the Simultan component when new created
        with the slot name and the extension, seperated by a blank
        """

        self.template_name = kwargs.get('template_name', None)
        self.template_id = kwargs.get('template_id', None)

        self.inherits_from = kwargs.get('inherits_from', None)

        self.content = kwargs.get('content', [])
        self.documentation = kwargs.get('documentation', None)
        self.units = kwargs.get('units', {})
        self.types = kwargs.get('types', {})

        self.slots = kwargs.get('slots', {})
        self.synonyms = kwargs.get('synonyms', {})      # name of the attribute in the python class

        self.template_parser = kwargs.get('template_parser', None)
        self.template_class = kwargs.get('template_class', None)

        self.default_slot = kwargs.get('default_slot', 'Element')

    def write(self, filename: str = None):
        """
        write the template as .yml to a file
        :param filename: name and path of the file to save; Example: C:\SIMULTAN\my_template.yml
        :return: None
        """
        if filename is not None:
            yaml.dump([self], open(filename, mode='w'))
        else:
            f = io.StringIO()
            yaml.dump([self], f)
            return f.getvalue()

    def create_template_class(self, template_parser, template_classes):
        """
        Creates a template class for this template.
        :param template_parser: TemplateParser instance
        :param template_classes: list of template classes to inherit from (e.g. default classes)
        :return: TemplateClass
        """

        if (self.template_parser is template_parser) and (self.template_class is not None):
            return self.template_class

        self.template_parser = template_parser

        # for inheritance:
        # template classes must inherit from SimultanObject, UserList or ValueField

        if self.inherits_from is not None:
            if self.inherits_from in self.template_parser.bases.keys():
                base = template_classes[self.inherits_from]

                simultan_base_list = [SimultanObject, UserList, ValueField]

                if any([issubclass(base, x) for x in simultan_base_list]):
                    bases = (base, )
                else:
                    bases = (SimultanObject, ) + (base, )
                    # bases = (base, ) + (SimultanObject, )

                # if SimultanObject in base.__bases__:
                #     bases = (base, )
                # elif UserList in base.__bases__:
                #     bases = (base, )
                # elif ValueField in base.__bases__:
                #     bases = (base, )
                # else:
                #     bases = (SimultanObject, ) + (base, )
            else:
                base = template_classes[self.inherits_from.template_name]
                bases = (base, )

            def new_init(self, *args, **kwargs):

                for i in range(self.__class__.__bases__.__len__()):
                    self.__class__.__bases__[i].__init__(self, *args, **kwargs)

        else:
            bases = (SimultanObject, )
            # create the class from the template

            def new_init(self, *args, **kwargs):

                self.__class__.__bases__[0].__init__(self, *args, **kwargs)

        new_class_dict = {'__init__': new_init,
                          '_template_name': self.template_name,
                          '_template_id': self.template_id,
                          '_documentation': self.documentation,
                          '_content': [cont for cont in self.content],
                          '_types': self.types,
                          '_units': self.units,
                          '_base': bases,
                          '_template_parser': self.template_parser,
                          '_slots': self.slots,
                          '_synonyms': self.synonyms,
                          '_default_slot': self.default_slot}

        new_class_dict.update(self.get_properties())
        new_class = type(self.template_name, bases, new_class_dict)

        self.template_class = new_class

        return new_class

    def get_properties(self):

        prop_dict = {}

        for prop in self.content:

            if prop in self.slots.keys():
                slot = self.slots[prop]
            else:
                slot = None

            syn = self.synonyms.get('prop', prop)

            prop_dict[syn] = add_properties(prop, syn, param_type=self.types.get(prop, None), slot=slot)

        return prop_dict

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['template_parser']
        del state['template_class']
        return state

    def __setstate__(self, d):
        self.__dict__ = d
        self.template_parser = None
        self.template_class = None

    def __repr__(self):
        return f"Template '{self.template_name}': " + object.__repr__(self)


class TemplateParser(object):

    bases = {'Liste': SimultanList,
             'List': SimultanList,
             'ReferenceList': ReferenceList,
             'ValueField': ValueField,
             'Geometric Area': BuildInFace,
             'Geometrische_Flächen': BuildInFace,
             'Geometric Volume': BuildInVolume,
             'Geometrische_Volumina': BuildInVolume,
             'BuildInZone': BuildInZone,
             'BuildInConstruction': BaseBuildInConstruction,
             'BuildInMaterialLayer': BuildInMaterialLayer}

    geo_bases = {'base': geometry_types.base,
                 'layer': geometry_types.layer,
                 'vertex': geometry_types.vertex,
                 'edge': geometry_types.edge,
                 'edge_loop': geometry_types.edge_loop,
                 'face': geometry_types.face,
                 'volume': geometry_types.volume,
                 }

    _create_all = False

    def __init__(self, *args, **kwargs):

        """
        Class which handles templates. This class generates python objects from the SIMULTAN data model for templates.

        @keyword templates: list of templates; if templates is None and template_filepath is defined,
        templates are automatically loaded
        @keyword template_filepath: filepath to the template (*.yml)

        """

        self._current_data_model = None

        self.id = uuid4()

        self._templates = kwargs.get('templates', None)
        self.template_filepath = kwargs.get('template_filepath', None)

        self._template_classes = kwargs.get('template_classes', None)

        self.data_models = kwargs.get('data_models', {})

        self._typed_geo_models = None

        template_classes[self.id] = self._template_classes

        self.current_data_model = kwargs.get('current_data_model', None)

    @property
    def current_data_model(self):
        return self._current_data_model

    @current_data_model.setter
    def current_data_model(self, value):
        self._current_data_model = value
        if self._current_data_model is None:
            return

        if self._current_data_model not in self.data_models:
            self.data_models[self._current_data_model.id] = self._current_data_model

    @property
    def templates(self):
        if self.template_filepath is None:
            return None

        if self._templates is None:
            self._templates = self.load_templates_from_file()
        return self._templates

    @property
    def template_classes(self):
        if self._template_classes is None:
            self.create_template_classes()
        return self._template_classes

    @property
    def typed_geo_models(self):
        if self._typed_geo_models is None:
            self._typed_geo_models = self.get_typed_geo_models()
        return self._typed_geo_models

    def get_model_by_file_id(self, id):
        return self.current_data_model.models_dict[id]

    def get_typed_model_by_file_id(self, id):
        return self.typed_geo_models[id]

    def load_templates_from_file(self, filepath=None):
        """
        Load templates from file
        :param filepath: filepath of the file (str)
        :return: templates; list of templates
        """
        if filepath is None:
            filepath = self.template_filepath

        if filepath is None:
            templates = []
        else:
            with open(filepath, mode='r', encoding="utf-8") as f_obj:
                templates = yaml.load(f_obj)

        return templates

    def create_template_classes(self) -> typing.Dict[str, str]:

        logger.info('\n\nCreating template-classes:\n-------------------------------------')
        template_classes = {**self.bases}

        if self.templates is not None:
            logger.info(f'found {self.templates.__len__()} templates')

            for template in self.templates:

                new_class = template.create_template_class(self, template_classes)
                template_classes[template.template_name] = new_class

                logger.info(f'Created template class {template.template_name}. Inherits from {template.inherits_from}')

        else:
            logger.info(f'No template file defined')

        self._template_classes = template_classes
        logger.info('template-class creation finished\n\n')
        return self._template_classes

    @lru_cache(maxsize=None)
    def create_python_object(self, sim_component, template_name=None):

        # get the template or slot
        # template_name = None
        if hasattr(sim_component, 'Parameters'):
            t_name = next((x.TextValue for x in sim_component.Parameters.Items if x.Name == 'TYPE'), None)
            if t_name is not None:
                template_name = t_name

        if (template_name is None) and (hasattr(sim_component, 'get_CurrentSlot')):
            template_name = sim_component.CurrentSlot.Base

        # if no template and no slot could be found return the plain SimComponent

        if template_name is None:
            if isinstance(sim_component, SimMultiValuePointer):
                template_name = 'ValueField'

        if template_name is None:
            if self._create_all:
                if hasattr(SimComponent, 'ContainedSimComponentsAsList'):
                    _ = [self.create_python_object(x) for x in sim_component.Components]
                if hasattr(SimComponent, 'ReferencedSimComponents'):
                    _ = [self.create_python_object(x) for x in sim_component.ReferencedComponents.Items]
            return sim_component

        if template_name not in self.template_classes.keys():

            # create new class for the template / slot
            base = SimultanObject
            bases = (base, )

            def new__init(self, *args, **kwargs):
                self.__class__.__bases__[0].__init__(self, *args, **kwargs)

            new_class_dict = {'__init__': new__init,
                              '_template_name': template_name,
                              '_template_id': None,
                              '_documentation': None,
                              '_content': None,
                              '_types': None,
                              '_units': None,
                              '_base': bases,
                              '_template_parser': self,
                              '_slots': {}}

            new_class = type(template_name, bases, new_class_dict)
            self.template_classes[template_name] = new_class

        template_class = self.template_classes[template_name]

        # init new instance
        template_class._template_parser = self
        new_instance = template_class(wrapped_obj=sim_component,
                                      template_parser=self,
                                      data_model_id=self._current_data_model.id)

        # new_instance._template_parser = self
        return new_instance

    def get_typed_geo_models(self):
        typed_models_dict = {}
        for key, model in self.current_data_model.models_dict.items():
            if model is None:
                typed_models_dict[key] = None
                continue
            typed_models_dict[key] = GeometryModel(template_parser=self,
                                                   wrapped_obj=model,
                                                   geo_types=self.geo_bases)
            # models.append(GeometryModel(wrapped_obj=model))
        return typed_models_dict

    def add_new_geometry_model(self, file_name: str, model_name: str = None):

        model, resource = self.current_data_model.add_new_geometry_model(file_name, model_name, return_resource=True)

        return self.add_typed_geo_model(model, resource.Key)

    def add_typed_geo_model(self, model, key):
        """
        Add a geometry model as typed model
        :param model: ParameterStructure.Assets.ContainedResourceFileEntry
        :param key: resource key
        """
        if self._typed_geo_models is None:
            self._typed_geo_models = {}

        self._typed_geo_models[key] = GeometryModel(template_parser=self,
                                                    wrapped_obj=model,
                                                    geo_types=self.geo_bases)

        return self._typed_geo_models[key]

    def get_geo_components(self, geometry):
        return Enumerable.ToList[SimComponent](self.current_data_model.exch.GetComponents(geometry))

    def get_py_geo_components(self, geometry, template_name=None):
        components = Enumerable.ToList[SimComponent](self.current_data_model.exch.GetComponents(geometry))
        return [self.create_python_object(x, template_name=template_name) for x in components]


def add_properties(prop_name: str, syn_name: str, param_type: str, slot=None) -> property:
    """
    create property for a class
    :param prop_name: name of the property (str)
    :param prop_name: name of the synonym (str)
    :param param_type: type of the property; if type == 'str': param.get_TextValue(); else: param.get_ValueCurrent() is returned
    :param slot: slot; default is None
    :return: property
    """

    @lru_cache()
    def getx(self):
        obj = None

        idx = next((i for i, x in enumerate(self._wrapped_obj.Parameters.Items) if x.Name == prop_name), None)
        if idx is not None:
            param = self._wrapped_obj.Parameters.Items[idx]
            obj = param.get_MultiValuePointer()

            if obj is None:
                if param_type == 'str':
                    obj = param.get_TextValue()
                else:
                    obj = param.get_ValueCurrent()

        if obj is None:
            full_slot_name = self._slots.get(prop_name, None)
            slot_name, slot_extension = parse_slot(full_slot_name)

            if full_slot_name is not None:
                obj = next((x.Component for x in self._wrapped_obj.Components.Items
                            if (x.Slot.SlotBase.Base == slot_name) & (x.Slot.SlotExtension == slot_extension)),
                           None)

                if obj is None:
                    obj = next((x.Target for x in self._wrapped_obj.ReferencedComponents.Items
                                if ' '.join([str(x.Slot.SlotBase),
                                             x.Slot.SlotExtension]) == full_slot_name),
                               None)

        return self._template_parser.create_python_object(obj)

    def setx(self, value: Union[int, float, SimComponent, SimultanObject]):
        getx.cache_clear()
        idx = next((i for i, x in enumerate(self._wrapped_obj.Parameters.Items) if x.Name == prop_name), None)

        if isinstance(value, (SimComponent, SimultanObject)):
            # set reference or subcomponent

            if prop_name not in self._slots.keys():
                raise KeyError(f'{prop_name} not defined as slot for class {self.__class__.__name__}')

            full_slot_name = self._slots.get(prop_name, None)
            slot_name, slot_extension = parse_slot(full_slot_name)

            # check if slot exists:
            idx = self.slot_components.index[
                (self.slot_components.slot == slot_name) & (self.slot_components.slot_extension == slot_extension)]

            if idx.__len__() == 1:
                # if subcomponent:
                if self.slot_components.iloc[idx].comp_type.values == 0:
                    if isinstance(value, SimultanObject):
                        pass

                    ref = next((x for x in self._wrapped_obj.Components.Items
                                if ((x.Slot.SlotBase.Base == slot_name) & (
                                x.Slot.SlotExtension == slot_extension))), None)

                    if isinstance(value, SimComponent):
                        ref.Component = value
                    elif isinstance(value, SimultanObject):
                        ref.Component = value._wrapped_obj

                # if reference:
                elif self.slot_components.iloc[idx].comp_type.values == 1:
                    ref = next((x for x in self._wrapped_obj.ReferencedComponents.Items
                                if ((x.Slot.SlotBase.Base == slot_name) & (
                                x.Slot.SlotExtension == slot_extension))), None)

                    if isinstance(value, SimComponent):
                        # delete reference
                        self.remove_component_reference(ref.reference)
                        # add the SimComponent as sub-component
                        self.add_sub_component(component=value,
                                               slot_name=slot_name,
                                               slot_extension=slot_extension,
                                               alter_slot=True)
                    else:
                        ref.Target = value._wrapped_obj

            # index does not exist
            elif idx.__len__() == 0:
                if isinstance(value, SimultanObject):
                    self.add_component_reference(component=value._wrapped_obj,
                                                 slot_name=slot_name,
                                                 slot_extension=slot_extension)
                elif isinstance(value, SimComponent):
                    self.add_sub_component(component=value, slot_name=slot_name, slot_extension=slot_extension)

        elif param_type == 'str':
            #todo: implementation for referenced parameters
            if self._wrapped_obj.Parameters.Items[2].GetReferencedParameter() != self._wrapped_obj.Parameters.Items[idx]:
                raise NotImplementedError(f'{self.name}: Param {prop_name} is a referenced Parameter. Setting referenced parameters is not yet implemented')
            self._wrapped_obj.Parameters.Items[idx].set_TextValue(value)
        elif isinstance(value, (int, float)):
            # todo: implementation for referenced parameters
            if self._wrapped_obj.Parameters.Items[2].GetReferencedParameter() != self._wrapped_obj.Parameters.Items[idx]:
                raise NotImplementedError(f'{self.name}: Param {prop_name} is a referenced Parameter. Setting referenced parameters is not yet implemented')
            self._wrapped_obj.Parameters.Items[idx].set_ValueCurrent(float(value))
        else:
            raise TypeError(
                f'{self.name}: Error setting parameter {prop_name} to {type(value)}. Supported types are only: int float str SimComponent SimultanObject.')

    def delx(self):
        logger.warning('delete method not implemented')
        raise NotImplementedError

    return property(getx, setx, delx, f"automatic created property")


def _my_loader(f):
    import yaml

    description = []

    def any_constructor(loader, tag_suffix, node):
        if isinstance(node, yaml.MappingNode):
            return loader.construct_mapping(node)
        if isinstance(node, yaml.SequenceNode):
            return loader.construct_sequence(node)
        return loader.construct_scalar(node)

    yaml.add_multi_constructor('', any_constructor, Loader=yaml.SafeLoader)
    data = list(yaml.load_all(f, Loader=yaml.SafeLoader))
    return data


_parsers['_my_loader'] = _my_loader


class TemplateValidator(object):

    def __init__(self, *args, **kwargs):

        self.schema = yamale.make_schema(schema_file, parser='ruamel')

    def validate(self, yaml_file):
        data = yamale.make_data(yaml_file, parser='_my_loader')
        yamale.validate(self.schema, data)
