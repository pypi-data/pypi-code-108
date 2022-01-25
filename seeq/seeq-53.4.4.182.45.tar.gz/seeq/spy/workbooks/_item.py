import hashlib
import json
import re
from typing import Optional, Dict

from seeq.sdk import *
from seeq.sdk.rest import ApiException
from seeq.spy import _common
from seeq.spy._errors import *
from seeq.spy._session import Session


class Item:
    _datasource: Optional[DatasourcePreviewV1]

    available_types = dict()

    CONSTRUCTOR = 'CONSTRUCTOR'
    PULL = 'PULL'
    LOAD = 'LOAD'

    def __init__(self, definition=None):
        _common.validate_argument_types([(definition, 'definition', dict)])

        self.definition = definition if definition else dict()

        if 'ID' not in self.definition:
            self.definition['ID'] = _common.new_placeholder_guid()

        if 'Type' not in self.definition:
            self.definition['Type'] = self.__class__.__name__

            # Reduce the derived classes down to their base class
            if self.definition['Type'] in ['Analysis', 'Topic']:
                self.definition['Type'] = 'Workbook'
            if 'Worksheet' in self.definition['Type']:
                self.definition['Type'] = 'Worksheet'
            if 'Workstep' in self.definition['Type']:
                self.definition['Type'] = 'Workstep'

        self.provenance = Item.CONSTRUCTOR
        self._datasource = None

    def __contains__(self, key):
        return _common.present(self.definition, key)

    def __getitem__(self, key):
        return _common.get(self.definition, key)

    def __setitem__(self, key, val):
        self.definition[key] = val

    def __delitem__(self, key):
        del self.definition[key]

    def __repr__(self):
        return '%s "%s" (%s)' % (self.type, self.name, self.id)

    @property
    def id(self):
        return _common.get(self.definition, 'ID')

    @property
    def name(self):
        return _common.get(self.definition, 'Name')

    @name.setter
    def name(self, value):
        self.definition['Name'] = value

    @property
    def type(self):
        return _common.get(self.definition, 'Type')

    @property
    def datasource(self) -> DatasourcePreviewV1:
        return self._datasource

    @property
    def definition_hash(self):
        return self.digest_hash(self.definition)

    @staticmethod
    def digest_hash(d):
        # We can't use Python's built-in hash() method as it produces non-deterministic hash values due to using a
        # random seed
        hashed = hashlib.md5()
        hashed.update(str(json.dumps(d, sort_keys=True, skipkeys=True)).encode('utf-8'))
        return hashed.hexdigest()

    def refresh_from(self, new_item, item_map):
        self.definition = new_item.definition
        self.provenance = new_item.provenance

    def apply_map(self, item_map):
        derived_class = self._get_derived_class(self.type)
        definition_str = _common.safe_json_dumps(self.definition)
        replaced_str = replace_items(definition_str, item_map)
        definition_dict = json.loads(replaced_str)
        return derived_class(**{'definition': definition_dict})

    def _construct_data_id(self, label):
        return '[%s] %s' % (label, self.id)

    def find_me(self, session: Session, label, datasource_output):
        # This is arguably the trickiest part of the spy.workbooks codebase: identifier management. This function is
        # a key piece to understanding how it works.
        #
        # When we push items to a server, we are trying our best not to create duplicates when the user doesn't
        # intend to. In other words, operations should be idempotent whenever it is expected that they should be.
        #
        # First, we look up an item by its identifier in case our in-memory object actually corresponds directly to
        # an existing item. This will happen whenever items are constructed by virtue of executing spy.workbooks.pull(),
        # or if the user does a spy.workbooks.push() without specifying refresh=False.
        #
        # If that method doesn't work, then we try to look up the item using a canonical Data ID format,
        # which incorporates the ID field from the in-memory object, which may have been generated (in the case where
        # self.provenance equals Item.CONSTRUCTOR) or may come from a different system (in the case where
        # self.provenance equals Item.PULL or Item.Load).
        #
        # If that doesn't work and the item was created by just constructing it in memory (i.e. self.provenance
        # equals Item.CONSTRUCTOR), then the item types will try to look it up by name.
        #
        # A label can be used to purposefully isolate or duplicate items. If a label is specified, then we never look
        # up an item directly by its ID, we fall through to the canonical Data ID format (which incorporates the
        # label). This allows many copies of a workbook to be created, for example during training scenarios.

        items_api = ItemsApi(session.client)

        if not label:
            try:
                item_output = items_api.get_item_and_all_properties(id=self.id)  # type: ItemOutputV1
                return item_output
            except ApiException:
                # Fall through to looking via Data ID
                pass

        data_id = self._construct_data_id(label)
        _filters = [
            'Datasource Class==%s && Datasource ID==%s && Data ID==%s' % (
                datasource_output.datasource_class, datasource_output.datasource_id, data_id),
            '@includeUnsearchable']

        search_results = items_api.search_items(
            filters=_filters,
            offset=0,
            limit=2)  # type: ItemSearchPreviewPaginatedListV1

        if len(search_results.items) == 0:
            return None

        if len(search_results.items) > 1:
            raise SPyRuntimeError('Multiple workbook/worksheet/workstep items found with Data ID of "%s"', data_id)

        return search_results.items[0]

    @staticmethod
    def _get_item_output(session: Session, item_id: str) -> ItemOutputV1:
        items_api = ItemsApi(session.client)
        return items_api.get_item_and_all_properties(id=item_id)

    @staticmethod
    def _dict_from_item_output(item_output: ItemOutputV1):
        def _parse(val):
            if val == 'true':
                return True
            elif val == 'false':
                return False
            else:
                return val

        definition = {prop.name: _parse(prop.value) for prop in item_output.properties}
        definition['Name'] = item_output.name
        definition['Type'] = item_output.type

        if 'UIConfig' in definition:
            definition['UIConfig'] = json.loads(definition['UIConfig'])

        # For some reason, these are coming back as lower case, which makes things inconsistent
        if 'Scoped To' in definition and isinstance(definition['Scoped To'], str):
            definition['Scoped To'] = definition['Scoped To'].upper()

        if item_output.ancillaries:
            definition['Ancillaries'] = list()
            for item_ancillary_output in item_output.ancillaries:  # type: ItemAncillaryOutputV1
                item_ancillary_dict = Item._dict_via_attribute_map(item_ancillary_output, {
                    'data_id': 'Data ID',
                    'datasource_class': 'Datasource Class',
                    'datasource_id': 'Datasource ID',
                    'description': 'Description',
                    'id': 'ID',
                    'name': 'Name',
                    'scoped_to': 'Scoped To',
                    'type': 'Type'
                })

                if item_ancillary_output.items:
                    item_ancillary_dict['Items'] = list()
                    for ancillary_item_output in item_ancillary_output.items:  # type: AncillaryItemOutputV1
                        ancillary_item_dict = Item._dict_via_attribute_map(ancillary_item_output, {
                            'id': 'ID',
                            'name': 'Name',
                            'order': 'Order',
                            'type': 'Type'
                        })
                        item_ancillary_dict['Items'].append(ancillary_item_dict)

                definition['Ancillaries'].append(item_ancillary_dict)

        return definition

    @staticmethod
    def _dict_via_attribute_map(item, attribute_map):
        d = dict()
        for attr, prop in attribute_map.items():
            if hasattr(item, attr):
                d[prop] = getattr(item, attr)

        return d

    @staticmethod
    def _dict_from_scalar_value_output(scalar_value_output):
        """
        :type scalar_value_output: ScalarValueOutputV1
        """
        d = dict()
        d['Value'] = scalar_value_output.value
        d['Unit Of Measure'] = scalar_value_output.uom
        return d

    @staticmethod
    def _str_from_scalar_value_dict(scalar_value_dict):
        if isinstance(scalar_value_dict['Value'], str):
            return '%s' % scalar_value_dict['Value']
        elif isinstance(scalar_value_dict['Value'], int):
            return '%d %s' % (scalar_value_dict['Value'], scalar_value_dict['Unit Of Measure'])
        else:
            return '%f %s' % (scalar_value_dict['Value'], scalar_value_dict['Unit Of Measure'])

    @staticmethod
    def _property_input_from_scalar_str(scalar_str):
        match = re.fullmatch(r'([+\-\d.]+)(.*)', scalar_str)
        if not match:
            return None

        uom = match.group(2) if match.group(2) else None
        return PropertyInputV1(unit_of_measure=uom, value=float(match.group(1)))

    @staticmethod
    def _property_output_from_item_output(item_output, property_name):
        props = [p for p in item_output.properties if p.name == property_name]
        return props[0] if len(props) == 1 else None

    @staticmethod
    def formula_string_from_list(formula_list):
        return '\n'.join(formula_list) if isinstance(formula_list, list) else str(formula_list)

    @staticmethod
    def formula_list_from_string(formula_string):
        return formula_string.split('\n') if '\n' in formula_string else formula_string

    @staticmethod
    def _get_derived_class(_type):
        if _type not in Item.available_types:
            raise SPyTypeError('Type "%s" not supported in this version of seeq module' % _type)

        return Item.available_types[_type]

    @staticmethod
    def pull(item_id, *, allowed_types=None, session: Session = None):
        session = Session.validate(session)
        item_output = Item._get_item_output(session, item_id)
        definition = Item._dict_from_item_output(item_output)
        if allowed_types and definition['Type'] not in allowed_types:
            return None

        derived_class = Item._get_derived_class(definition['Type'])
        item = derived_class(definition)  # type: Item
        item._pull(session, item_id)
        item._datasource = item_output.datasource
        return item

    def _pull(self, session: Session, item_id):
        self.provenance = Item.PULL

    @staticmethod
    def load(definition):
        derived_class = Item._get_derived_class(definition['Type'])
        item = derived_class(definition)
        item.provenance = Item.LOAD
        return item

    def _pull_formula_based_item(self, calculated_item):
        self.definition['Formula'] = Item.formula_list_from_string(self.definition['Formula'])
        self.definition['Formula Parameters'] = dict()
        for parameter in calculated_item.parameters:  # type: FormulaParameterOutputV1
            if parameter.item:
                self.definition['Formula Parameters'][parameter.name] = parameter.item.id
            else:
                self.definition['Formula Parameters'][parameter.name] = parameter.formula

    def _scrape_auth_datasources(self, session: Session) -> Dict[str, DatasourceOutputV1]:
        return dict()


class Reference:
    JOURNAL = 'Journal'
    DETAILS = 'Details'
    SCOPED = 'Scoped'
    DEPENDENCY = 'Dependency'
    ANCILLARY = 'Ancillary'
    EMBEDDED_CONTENT = 'Embedded Content'

    def __init__(self, _id, _provenance, worksheet=None):
        """
        :type _id: str
        :type _provenance: str
        :type worksheet: Worksheet
        """
        self.id = _id
        self.provenance = _provenance
        self.worksheet = worksheet

    def __repr__(self):
        if self.worksheet is not None:
            return '%s reference on "%s" (%s)' % (self.provenance, self.worksheet.name, self.id)
        else:
            return '%s (%s)' % (self.provenance, self.id)


def replace_items(document, item_map):
    if document is None:
        return

    new_report = document
    for _id, _replacement in item_map.items():
        matches = re.finditer(_id, document, flags=re.IGNORECASE)
        for match in matches:
            new_report = re.sub(re.escape(match.group(0)), _replacement, new_report, flags=re.IGNORECASE)

    return new_report


def get_canonical_server_url(session: Session):
    url = session.client.host.replace('/api', '').lower()  # type: str
    if url.startswith('http:') and url.endswith(':80'):
        url = url.replace(':80', '')
    if url.startswith('https:') and url.endswith(':443'):
        url = url.replace(':443', '')

    return url
