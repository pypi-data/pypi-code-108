from .config import logger
from random import choices
# from .config import yaml
import re
from typing import Tuple


from System.Windows.Media import Color


class classproperty(object):

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class SimultanComponent(object):

    def __init__(self, *args, **kwargs):
        self.data = list(kwargs.get('data'))
        self.component_list = set()
        self.typed_component_list = set()

        self.get_component_list(self.data, self.data[0])
        self.get_typed_component_list()

    def get_component_list(self, components, component):
        if component not in self.typed_component_list:
            self.component_list.add(component)

            component_list = component.Components
            for neighbour in component_list:
                self.get_component_list(component_list, neighbour)

    def get_typed_component_list(self):
        for component in self.component_list:
            for param in component.Parameters.Items:
                if param.Name == 'TYPE':
                    self.typed_component_list.add(component)

    #
    # def dfs(self, visited, components, component):
    #     if component not in visited:
    #         print(component)
    #         visited.add(component)
    #         component_list = component.ContainedComponentsAsList
    #         for neighbour in component_list:
    #             dfs(visited, component_list, neighbour)
    #
    # def visit_components_list(self, visited, components, component, typed_component_list=[]):
    #     if component not in visited:
    #         visited.add(component)
    #
    #         for neighbour in components:
    #             if neighbour.ContainedParameters:
    #                 print('PARAMS')
    #                 print(neighbour.ContainedParameters)
    #                 for el in component.ContainedParameters:
    #                     if el.Name == 'TYPE':
    #                         print('TYPE')
    #                         print(el)
    #                         typed_component_list.append(neighbour)
    #             if neighbour.ContainedComponentsAsList:
    #                 print('LIST')
    #                 print(neighbour.ContainedComponentsAsList)
    #                 visit_components_list(component.ContainedComponentsAsList, neighbour, typed_component_list)
    #
    # def get_flat_list(self, visited, component_list, component):
    #     if component not in visited:
    #         visited.add(component)
    #         component_list = component.ContainedComponentsAsList
    #         for neighbour in component_list:
    #             dfs(visited, component_list, neighbour)
    #
    #     if not component_list:
    #         return []
    #     for comp in component_list:
    #         flat_list.append(comp)
    #         return (get_flat_list((comp.ContainedComponentsAsList, flat_list)))


def create_example_template():

    from .template_tools import Template

    material_template = Template(template_name='Material',
                                 template_id='1',
                                 content=['c', 'w20', 'w80', 'lambda', 'mu', 'rho'],
                                 documentation='c: specific heat = capacity in J/kg*K; ',
                                 units={'c': 'J/kg K',
                                        'w20': 'g/m=C2=B3',
                                        'w80': 'g/m=C2=B3',
                                        'lambda': 'W/mK',
                                        'mu': '-',
                                        'rho': 'kg/m=C2=B3'},
                                 types={'c': 'float',
                                        'w20': 'float',
                                        'w80': 'float',
                                        'lambda': 'float',
                                        'mu': 'float',
                                        'rho': 'float'}
                                 )

    layer_template = Template(template_name='Layer',
                              template_id='2',
                              content=['d', 'Material'],
                              documentation="d: thickness of the layer = in m, Material: see Template 'Material'",
                              units={'d': 'm', 'Material': '-'},
                              types={'d': 'float'}
                              )

    layer_template2 = Template(inherits_from=layer_template,
                               template_name='Layer2',
                               template_id='2.1',
                               content=['d', 'Material'],
                               documentation="d: thickness of the = layer in m, Material: see Template 'Material'",
                               units={'d': 'm', 'Material': '-'},
                               types={'d': 'int'}
                               )

    construction_template = Template(template_name='Construction',
                                     template_id='3',
                                     content=['layers'],
                                     documentation="layers: list of = items with type 'Layer'",
                                     units={'layers': '-'}
                                     )

    return [material_template, layer_template, layer_template2, construction_template]


def create_example_template_bim_bestand_network():

    from .template_tools import Template

    component_template = Template(template_name='Component',
                                  template_id=1,
                                  content=['AKS-Id', 'Loss Factor'],
                                  documentation='c: specific heat = capacity in J/kg*K;',
                                  units={'AKS-Id': 'J/kg K',
                                         'Loss Factor': 'g/m=C2=B3'},
                                  types={'AKS-Id': 'int',
                                         'Loss Factor': 'float'}
                                  )

    material_template = Template(template_name='Material',
                                 template_id='1',
                                 content=['c', 'w20', 'w80', 'lambda', 'mu', 'rho'],
                                 documentation='c: specific heat = capacity in J/kg*K; ',
                                 units={'c': 'J/kg K',
                                        'w20': 'g/m=C2=B3',
                                        'w80': 'g/m=C2=B3',
                                        'lambda': 'W/mK',
                                        'mu': '-',
                                        'rho': 'kg/m=C2=B3'},
                                 types={'c': 'float',
                                        'w20': 'float',
                                        'w80': 'float',
                                        'lambda': 'float',
                                        'mu': 'float',
                                        'rho': 'float'}
                                 )

    edge_template = Template(inherits_from=component_template,
                             template_name='Edge',
                             template_id='2',
                             content=['Start-ID', 'End-ID', 'COMPONENT-ID', 'COMPONENT-TYPE', 'Length', 'Lambda', 'K'],
                             documentation="d: thickness of the layer = in m, Material: see Template 'Material'",
                             units={'d': 'm', 'Material': '-'},
                             types={'d': 'float'}
                             )

    confuser_diffuser_rectangular_template = Template(inherits_from=edge_template,
                                                      template_name='CONFUSERDIFFUSERRECTANGULAR',
                                                      template_id='2.1',
                                                      content=['EndHight', 'EndWidth', 'StartHight', 'StartWidth'],
                                                      documentation="d: thickness of the = layer in m, Material: see Template 'Material'",
                                                      units={'d': 'm', 'Material': '-'},
                                                      types={'d': 'int'}
                                                      )

    confuser_diffuser_round_template = Template(inherits_from=edge_template,
                                                template_name='CONFUSERDIFFUSERROUND',
                                                template_id='3',
                                                content=['EndDiameter', 'StartDiameter'],
                                                documentation="layers: list of = items with type 'Layer'",
                                                units={'layers': '-'}
                                                )

    return [component_template, material_template, edge_template, confuser_diffuser_rectangular_template, confuser_diffuser_round_template]


def class_type_simultan_components(components, template_classes):

    # collect component classes in a dictionary:
    component_classes = {}

    # loop trough all components:
    for component in components:
        # get the template-id
        template_name = None
        for comp_type in component.Parameters.Items:
            if comp_type.Name == 'TYPE':
                template_name = comp_type.TextValue

        # check if the component class already exists:
        if template_name in component_classes.keys():     # if it already = exists take it
            new_component_class_dict = component_classes[template_name]
        elif template_name in template_classes.keys():   # create new component class
            # find the python template class:
            template_class = template_classes[template_name]

            # init new instance
            new_instance = template_class(wrapped_obj=component)

            print(new_instance)


    return components


def create_example_simultan_components(templates, flat_list_components):

    simultan_components = []

    for template in templates:
        for component in flat_list_components:
            print(template)
            print(component)

    return simultan_components


def get_obj_by_id(cls, id):
    return cls._cls_instances_dict.get(id, None)


def sort_component_list(components):

    if components.__len__() == 0:
        return components

    slots = [x.Slot.SlotBase.Base for x in components]
    if not all(slots[0] == x for x in slots):
        raise TypeError(f'List elements do not have same slot')

    # slot_extensions = [int(re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", x.CurrentSlot)[-1]) for x in components]
    slot_extensions = [int(x.Slot.SlotExtension) for x in components]
    return slot_extensions


def sort_slots(slots):

    if slots.__len__() == 0:
        return slots

    if not all(slots[0].SlotBase == x.SlotBase for x in slots):
        raise TypeError(f'List elements do not have same slot')

    slot_extensions = [int(x.SlotExtension) for x in slots]
    return slot_extensions


def sort_references(references):

    if references.__len__() == 0:
        return references
    # check if same slot:
    slots = [x.Slot.SlotBase for x in references]

    if not all(slots[0] == x for x in slots):
        raise TypeError(f'List elements do not have same slot')

    slot_extensions = [int(x.Slot.SlotExtension) for x in references]
    return slot_extensions


def get_random_color():
    rgb = choices(range(256), k=3)
    return Color.FromArgb(rgb[0], rgb[1], rgb[2], 255)


def parse_slot(full_slot_name: str) -> Tuple[str, any]:
    """
    Parse the slot name. Returns slot_name and slot_extension
    :param full_slot_name:
    :return: (slot_name, slot_extension)
    """
    if full_slot_name.startswith('Undefined Slot'):
        slot_extension = full_slot_name.split('_')[-1]
        slot_name = 'Undefined Slot'
    else:
        slot_extension = full_slot_name.split()[-1]
        slot_name = ' '.join(full_slot_name.split()[0:-1])

    return slot_name, slot_extension
