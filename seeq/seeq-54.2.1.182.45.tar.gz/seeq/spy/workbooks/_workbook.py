import copy
import glob
import json
import os
from typing import Dict, List, Optional, Union

import numpy as np

from seeq.base import system
from seeq.base.seeq_names import SeeqNames
from seeq.sdk import *
from seeq.sdk.rest import ApiException
from seeq.spy import _common
from seeq.spy import _metadata
from seeq.spy import _url
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status
from seeq.spy.workbooks import _folder
from seeq.spy.workbooks import _item
from seeq.spy.workbooks import _render
from seeq.spy.workbooks import _search
from seeq.spy.workbooks._data import Datasource, StoredOrCalculatedItem
from seeq.spy.workbooks._folder import Folder
from seeq.spy.workbooks._item import Item, Reference
from seeq.spy.workbooks._user import ItemWithOwnerAndAcl
from seeq.spy.workbooks._worksheet import Worksheet, AnalysisWorksheet, TopicDocument


class ItemJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Item):
            return o.definition
        else:
            return o


class Workbook(ItemWithOwnerAndAcl):
    NULL_DATASOURCE_STRING = '__null__'

    def __new__(cls, *args, **kwargs):
        if cls is Workbook:
            raise SPyTypeError("Workbook may not be instantiated directly, create either Analysis or Topic")

        return object.__new__(cls)

    def __init__(self, definition=None, *, status=None):
        if isinstance(definition, str):
            definition = {'Name': definition}

        super().__init__(definition)

        self.status = Status.validate(status)
        self.item_inventory = dict()
        self.item_push_errors = set()
        self.item_pull_errors = set()
        self.worksheets: List[Union[AnalysisWorksheet, TopicDocument]] = list()
        self.datasource_maps = list()
        self.scoped_items = None
        self.datasource_inventory = dict()
        if 'Workbook Type' not in self.definition:
            self.definition['Workbook Type'] = self.__class__.__name__
        if 'Name' not in self.definition:
            self.definition['Name'] = _common.DEFAULT_WORKBOOK_NAME

    @property
    def url(self):
        # Note that 'URL' won't be filled in if a workbook/worksheet hasn't been pushed/pulled. That's because the
        # IDs may change from the placeholders that get generated.
        return self['URL']

    @property
    def path(self):
        if 'Ancestors' not in self:
            return ''

        parts = list()
        for folder_id in self['Ancestors']:
            if not _common.is_guid(folder_id):
                parts.append(folder_id)
                continue

            folder = self.item_inventory.get(folder_id)

            if folder is None:
                raise SPyRuntimeError(f'Folder ID "{folder_id}" not found in item inventory')

            # Don't include the user's home folder if it is the first item
            if len(parts) == 0 and folder.definition.get(SeeqNames.Properties.unmodifiable) and \
                    folder.definition.get(SeeqNames.Properties.unsearchable):
                continue

            parts.append(folder.name)

        return ' >> '.join(parts)

    @property
    def item_push_errors_str(self):
        return self._get_errors_str(self.item_push_errors)

    @property
    def items_pull_errors_str(self):
        return self._get_errors_str(self.item_pull_errors)

    def _get_errors_str(self, errors):
        return 'Errors encountered:\n' + \
               '\n----------------------------------------\n'.join(errors)

    def update_status(self, result, count_increment):
        if self.status.current_df_index is None and len(self.status.df) == 0:
            self.status.df.at[0, :] = None
            self.status.current_df_index = 0
        current_count = self.status.get('Count') if \
            'Count' in self.status.df and self.status.get('Count') is not None else 0
        self.status.put('Count', current_count + count_increment)
        self.status.put('Time', self.status.get_timer())
        self.status.put('Result', result)

        self.status.update('[%d/%d] Processing %s "%s"' %
                           (len(self.status.df[self.status.df['Result'] != 'Queued']),
                            len(self.status.df), self['Workbook Type'], self['Name']),
                           Status.RUNNING)

    def refresh_from(self, new_item, item_map):
        super().refresh_from(new_item, item_map)

        for worksheet in self.worksheets:
            new_worksheet_id = item_map[worksheet.id]
            new_worksheet_list = [w for w in new_item.worksheets if w.id == new_worksheet_id]
            if len(new_worksheet_list) == 1:
                worksheet.refresh_from(new_worksheet_list[0], item_map)

        new_inventory = new_item.item_inventory.copy()
        for inventory_item_id, inventory_item in self.item_inventory.copy().items():
            if inventory_item_id not in item_map:
                if inventory_item.type == 'Folder':
                    # Folders may not have been pushed (depending on spy.workbooks.push arguments) and therefore won't
                    # be in the map, so skip them.
                    continue

                raise SPyRuntimeError('Item "%s" not found in item_map' % inventory_item)

            new_inventory_item_id = item_map[inventory_item_id]

            if new_inventory_item_id not in new_inventory:
                # This can happen when something that is scoped to a workbook is not actually referenced by a
                # worksheet or calculated item in that workbook, and then you are pushing with a label to a different
                # location. The workbook in that new location will not have the item in its inventory, so we just remove
                # it during the refresh.
                del self.item_inventory[inventory_item_id]
            else:
                new_inventory_item = new_inventory[new_inventory_item_id]
                inventory_item.refresh_from(new_inventory_item, item_map)
                del self.item_inventory[inventory_item_id]
                self.item_inventory[new_inventory_item_id] = inventory_item

        # Transfer the remaining (new) inventory over. This often includes new folders.
        for new_inventory_item_id, new_inventory_item in new_inventory.items():
            if new_inventory_item_id not in self.item_inventory:
                self.item_inventory[new_inventory_item_id] = new_inventory_item

        self.datasource_inventory = new_item.datasource_inventory
        self.datasource_maps = new_item.datasource_maps

    @staticmethod
    def _instantiate(definition=None, status=None):
        if definition['Type'] == 'Workbook':
            if 'Data' not in definition or _common.get_workbook_type(definition['Data']) == 'Analysis':
                return Analysis(definition, status=status)
            else:
                return Topic(definition, status=status)
        elif definition['Type'] in ['Analysis', 'Topic']:
            # This is for backward compatibility with .49 and earlier, which used the same type (Workbook) for both
            # Analysis and Topic. Eventually we may want to deprecate "Workbook Type" and fold it into the "Type"
            # property.
            definition['Workbook Type'] = definition['Type']
            definition['Type'] = 'Workbook'

            if definition['Workbook Type'] == 'Analysis':
                return Analysis(definition, status=status)
            elif definition['Workbook Type'] == 'Topic':
                return Topic(definition, status=status)
        else:
            raise SPyValueError(f"Unrecognized workbook type: {definition['Type']}")

    @staticmethod
    def pull(item_id, *, status=None, extra_workstep_tuples=None, include_inventory=True, include_images=True,
             specific_worksheet_ids: Optional[List[str]] = None, session: Optional[Session] = None):
        session = Session.validate(session)
        definition = Item._dict_from_item_output(Item._get_item_output(session, item_id))
        workbook = Workbook._instantiate(definition, status)
        workbook._pull(session, workbook_id=workbook.id, extra_workstep_tuples=extra_workstep_tuples,
                       include_inventory=include_inventory, include_images=include_images,
                       specific_worksheet_ids=specific_worksheet_ids)
        return workbook

    def pull_rendered_content(self, session: Session, *, errors='raise', quiet=False, status: Status = None):
        pass

    def _pull(self, session: Session, *, workbook_id=None, extra_workstep_tuples=None, include_inventory=True,
              include_images=True, specific_worksheet_ids: Optional[List[str]] = None):
        if workbook_id is None:
            workbook_id = self.id
        workbooks_api = WorkbooksApi(session.client)
        workbook_output = workbooks_api.get_workbook(id=workbook_id)  # type: WorkbookOutputV1

        self.definition['Path'] = _common.path_list_to_string([a.name for a in workbook_output.ancestors])
        self.definition['Workbook Type'] = _common.get_workbook_type(workbook_output)

        self.provenance = Item.PULL

        self._pull_owner_and_acl(session, workbook_output.owner)
        self._pull_ancestors(session, workbook_output.ancestors)

        self.update_status('Pulling workbook', 1)

        if 'workbookState' in self.definition:
            self.definition['workbookState'] = json.loads(self.definition['workbookState'])

        self.definition['Original Server URL'] = _item.get_canonical_server_url(session)

        self.worksheets = list()

        if specific_worksheet_ids is not None:
            worksheet_ids = specific_worksheet_ids
        else:
            worksheet_ids = Workbook._pull_worksheet_ids(session, workbook_id,
                                                         get_archived_worksheets=workbook_output.is_archived)

        if extra_workstep_tuples:
            for workbook_id, worksheet_id, workstep_id in extra_workstep_tuples:
                if workbook_id == self.id and worksheet_id not in worksheet_ids:
                    worksheet_ids.append(worksheet_id)

        for worksheet_id in worksheet_ids:
            self.update_status('Pulling worksheets', 0)
            Worksheet.pull(worksheet_id, workbook=self, extra_workstep_tuples=extra_workstep_tuples,
                           include_images=include_images, session=session)
            self.update_status('Pulling worksheets', 1)

        self['URL'] = None
        if len(self.worksheets) > 0:
            link_url = _url.SeeqURL.parse(session.public_url)
            link_url.route = _url.Route.WORKBOOK_EDIT
            link_url.folder_id = self['Ancestors'][-1] if len(self['Ancestors']) > 0 else None
            link_url.workbook_id = self.id
            link_url.worksheet_id = self.worksheets[0].id
            self['URL'] = link_url.url

        self.item_inventory = dict()
        if include_inventory:
            self._scrape_item_inventory(session)
            self._scrape_datasource_inventory(session)
            self._construct_default_datasource_maps()
        else:
            # Need to at least scrape folders so we know what the path is
            self._scrape_folder_inventory(session)

    def _pull_ancestors(self, session: Session, ancestors: List[ItemPreviewV1]):
        super()._pull_ancestors(session, ancestors)
        _folder.massage_ancestors(session, self)

    @staticmethod
    def _pull_worksheet_ids(session: Session, workbook_id: str, *, get_archived_worksheets=False):
        workbooks_api = WorkbooksApi(session.client)

        offset = 0
        limit = 1000
        worksheet_ids = list()
        while True:
            worksheet_output_list = workbooks_api.get_worksheets(
                workbook_id=workbook_id,
                is_archived=get_archived_worksheets,
                offset=offset,
                limit=limit)  # type: WorksheetOutputListV1

            for worksheet_output in worksheet_output_list.worksheets:  # type: WorksheetOutputV1
                worksheet_ids.append(worksheet_output.id)

            if len(worksheet_output_list.worksheets) < limit:
                break

            offset = offset + limit

        return worksheet_ids

    @staticmethod
    def find_by_name(session: Session, workbook_name, workbook_type, folder_id) -> Optional[WorkbookOutputV1]:
        workbooks_api = WorkbooksApi(session.client)
        folders: WorkbenchItemOutputListV1
        if folder_id is not None and folder_id != _common.PATH_ROOT:
            folders = _search.get_folders(session, content_filter='owner', folder_id=folder_id)
        else:
            folders = _search.get_folders(session, content_filter='owner')

        for content in folders.content:  # type: WorkbenchSearchResultPreviewV1
            if content.name.lower() == workbook_name.lower() and content.type == workbook_type:
                return workbooks_api.get_workbook(id=content.id)

        return None

    def push(self, *, owner=None, folder_id=None, item_map=None, label=None, datasource=None,
             access_control=None, override_max_interp=False, include_inventory=True,
             scope_globals_to_workbook=False, status=None, session: Optional[Session] = None):
        session = Session.validate(session)
        self.status = Status.validate(status)
        self.item_push_errors = set()

        if len(self.worksheets) == 0:
            raise SPyValueError('Workbook %s must have at least one worksheet before pushing' % self)

        datasource_output = _metadata.create_datasource(session, datasource)

        workbook_item = self.find_me(session, label, datasource_output)

        if workbook_item is None and self.provenance == Item.CONSTRUCTOR:
            workbook_item = self.find_by_name(session, self.name, self.definition['Workbook Type'], folder_id)

        workbooks_api = WorkbooksApi(session.client)
        items_api = ItemsApi(session.client)

        props = list()
        existing_worksheet_identifiers = dict()

        if not workbook_item:
            workbook_input = WorkbookInputV1()
            workbook_input.name = self.definition['Name']
            workbook_input.description = _common.get(self.definition, 'Description')
            workbook_input.folder_id = folder_id if folder_id != _common.PATH_ROOT else None
            workbook_input.owner_id = self.decide_owner(session, self.datasource_maps, item_map, owner=owner)
            workbook_input.type = self['Workbook Type']
            workbook_input.branch_from = _common.get(self.definition, 'Branch From')
            workbook_output = workbooks_api.create_workbook(body=workbook_input)  # type: WorkbookOutputV1

            items_api.set_properties(id=workbook_output.id, body=[
                ScalarPropertyV1(name='Datasource Class', value=datasource_output.datasource_class),
                ScalarPropertyV1(name='Datasource ID', value=datasource_output.datasource_id),
                ScalarPropertyV1(name='Data ID', value=self._construct_data_id(label)),
                ScalarPropertyV1(name='workbookState', value=_common.DEFAULT_WORKBOOK_STATE)])

        else:
            workbook_output = workbooks_api.get_workbook(id=workbook_item.id)  # type: WorkbookOutputV1

            if workbook_output.is_archived:
                # If the workbook happens to be archived, un-archive it. If you're pushing a new copy it seems likely
                # you're intending to revive it.
                items_api.set_properties(id=workbook_output.id, body=[ScalarPropertyV1(name='Archived', value=False)])

            for is_archived in [False, True]:
                offset = 0
                limit = 1000
                while True:
                    worksheet_output_list = workbooks_api.get_worksheets(workbook_id=workbook_output.id,
                                                                         is_archived=is_archived,
                                                                         offset=offset,
                                                                         limit=limit)  # type: WorksheetOutputListV1

                    for worksheet_output in worksheet_output_list.worksheets:  # type: WorksheetOutputV1
                        item_output = items_api.get_item_and_all_properties(
                            id=worksheet_output.id)  # type: ItemOutputV1
                        data_id = [p.value for p in item_output.properties if p.name == 'Data ID']

                        existing_worksheet_identifiers[worksheet_output.id] = worksheet_output.id
                        existing_worksheet_identifiers[worksheet_output.name] = worksheet_output.id

                        # Worksheets not created by SPy will likely not have a Data ID
                        if len(data_id) != 0:
                            existing_worksheet_identifiers[data_id[0]] = worksheet_output.id

                    if len(worksheet_output_list.worksheets) < limit:
                        break

                    offset = offset + limit

            owner_id = self.decide_owner(session, self.datasource_maps, item_map, owner=owner,
                                         current_owner_id=workbook_output.owner.id)

            self._push_owner_and_location(session, workbook_output, owner_id, folder_id)

        self.status.put('Pushed Workbook ID', workbook_output.id)

        if item_map is None:
            item_map = dict()

        item_map[self.id.upper()] = workbook_output.id.upper()

        if access_control:
            self._push_acl(session, workbook_output.id, self.datasource_maps, item_map, access_control)

        if include_inventory:
            self._push_inventory(session, item_map, label, datasource_output, override_max_interp,
                                 scope_globals_to_workbook, workbook_output)

        props.append(ScalarPropertyV1(name='Name', value=self.definition['Name']))
        if _common.present(self.definition, 'Description'):
            props.append(ScalarPropertyV1(name='Description', value=self.definition['Description']))
        if _common.present(self.definition, 'workbookState'):
            props.append(ScalarPropertyV1(name='workbookState', value=json.dumps(self.definition['workbookState'])))

        items_api.set_properties(id=workbook_output.id, body=props)

        if len(set(self.worksheets)) != len(self.worksheets):
            raise SPyValueError('Worksheet list within Workbook "%s" is not unique: %s' % (self, self.worksheets))

        first_worksheet_id = None
        for worksheet in self.worksheets:  # type: Worksheet
            self.update_status('Pushing worksheet', 1)
            worksheet_output = worksheet.push(session, workbook_output.id, item_map, datasource_output,
                                              existing_worksheet_identifiers, include_inventory,
                                              label, self.item_push_errors)
            if first_worksheet_id is None:
                first_worksheet_id = worksheet_output.id

        # Pull the set of worksheets and re-order them
        remaining_pushed_worksheet_ids = Workbook._pull_worksheet_ids(session, workbook_output.id)
        next_worksheet_id = None
        for worksheet in reversed(self.worksheets):
            pushed_worksheet_id = item_map[worksheet.id]
            if next_worksheet_id is None:
                workbooks_api.move_worksheet(workbook_id=workbook_output.id, worksheet_id=pushed_worksheet_id)
            else:
                workbooks_api.move_worksheet(workbook_id=workbook_output.id, worksheet_id=pushed_worksheet_id,
                                             next_worksheet_id=item_map[next_worksheet_id])

            if pushed_worksheet_id in remaining_pushed_worksheet_ids:
                remaining_pushed_worksheet_ids.remove(pushed_worksheet_id)

            next_worksheet_id = worksheet.id

        # Archive any worksheets that are no longer active
        for remaining_pushed_worksheet_id in remaining_pushed_worksheet_ids:
            items_api.set_property(id=remaining_pushed_worksheet_id, property_name='Archived',
                                   body=PropertyInputV1(value=True))

        # Now go back through all the worksheets to see if any worksteps weren't resolved
        dependencies_not_found = set()
        for worksheet in self.worksheets:
            # Unresolved Report workstep dependencies will be found when pushing the associated document
            for workstep_tuple in worksheet.referenced_worksteps:
                referenced_workbook_id, referenced_worksheet_id, referenced_workstep_id = workstep_tuple
                if referenced_workstep_id not in item_map:
                    dependencies_not_found.add(
                        'Workbook %s, Worksheet %s, Workstep %s' % (
                            referenced_workbook_id, referenced_worksheet_id, referenced_workstep_id))

        if first_worksheet_id is not None:
            link_url = '%s/%sworkbook/%s/worksheet/%s' % (
                session.public_url,
                (folder_id + '/') if folder_id is not None else '',
                workbook_output.id,
                first_worksheet_id
            )
            self.status.put('URL', link_url)

        if len(dependencies_not_found) > 0:
            raise SPyDependencyNotFound('\n'.join(dependencies_not_found))

        self.status.update('Success', Status.SUCCESS)
        return workbook_output

    def _push_inventory(self, session: Session, item_map, label, datasource_output, override_max_interp,
                        scope_globals_to_workbook, workbook_output):
        remaining_inventory = dict(self.item_inventory)
        while len(remaining_inventory) > 0:
            at_least_one_thing_pushed = False
            dependencies_not_found = list()
            dict_iterator = dict(remaining_inventory)
            for item_id, item in dict_iterator.items():
                if item['Type'] in ['Folder']:
                    at_least_one_thing_pushed = True
                    del remaining_inventory[item_id]
                    continue

                # noinspection PyBroadException
                try:
                    item.push(session, self.datasource_maps, datasource_output, pushed_workbook_id=workbook_output.id,
                              item_map=item_map, label=label, override_max_interp=override_max_interp,
                              scope_globals_to_workbook=scope_globals_to_workbook)
                    self.update_status('Pushing item inventory', 1)
                    at_least_one_thing_pushed = True
                    del remaining_inventory[item_id]
                except _common.SPyDependencyNotFound as e:
                    dependencies_not_found.append(e)
                except KeyboardInterrupt:
                    raise
                except BaseException:
                    self.item_push_errors.add(f'Error processing {item}:\n{_common.format_exception()}')

            if not at_least_one_thing_pushed:
                for e in dependencies_not_found:
                    self.item_push_errors.add(str(e))
                break

    def push_containing_folders(self, session: Session, item_map, datasource_output, use_full_path, parent_folder_id,
                                owner, label, access_control):
        if 'Ancestors' not in self:
            return parent_folder_id

        keep_skipping = parent_folder_id in self['Ancestors']
        create_folders_now = False

        for ancestor_id in self['Ancestors']:
            if keep_skipping and parent_folder_id == ancestor_id:
                keep_skipping = False
                continue

            if use_full_path or 'Search Folder ID' not in self:
                create_folders_now = True

            if create_folders_now:
                if ancestor_id in self.item_inventory:
                    folder = self.item_inventory[ancestor_id]  # type: Folder

                    try:
                        is_unmodifiable = ItemsApi(session.client).get_property(
                            id=folder.id,
                            property_name='Unmodifiable').value == 'true'
                        if is_unmodifiable:
                            continue
                    except ApiException as e:
                        # it's okay if the item doesn't exist yet; it won't be unmodifiable
                        if e.status != 404:
                            raise e

                    parent_folder = folder.push(session, parent_folder_id, self.datasource_maps, datasource_output,
                                                item_map, owner=owner, label=label, access_control=access_control)
                    parent_folder_id = parent_folder.id
            elif self['Search Folder ID'] == ancestor_id:
                create_folders_now = True

        return parent_folder_id

    @property
    def referenced_items(self):
        referenced_items = list()
        for worksheet in self.worksheets:
            referenced_items.extend(worksheet.referenced_items)

        if self.scoped_items is not None:
            referenced_items.extend(self.scoped_items)

        return referenced_items

    @property
    def referenced_workbooks(self):
        references = dict()
        for worksheet in self.worksheets:
            for (workbook_id, worksheet_id, workstep_id) in worksheet.referenced_worksteps:
                if workbook_id not in references:
                    references[workbook_id] = set()

                references[workbook_id].add((workbook_id, worksheet_id, workstep_id))

        return references

    def find_workbook_links(self, session: Session):
        # This should only be called during a pull operation, because it requires a connection to the original
        # database in order to resolve the workbook in a view-only link. (See Annotation class.)
        links = dict()
        for worksheet in self.worksheets:
            links.update(worksheet.find_workbook_links(session))

        return links

    def push_fixed_up_workbook_links(self, session: Session, item_map, label, datasource_output):
        for worksheet in self.worksheets:
            worksheet.push_fixed_up_workbook_links(session, item_map, label, datasource_output)

    def _get_default_workbook_folder(self):
        return os.path.join(os.getcwd(), 'Workbook_%s' % self.id)

    @staticmethod
    def _get_workbook_json_file(workbook_folder):
        return os.path.join(workbook_folder, 'Workbook.json')

    @staticmethod
    def _get_items_json_file(workbook_folder):
        return os.path.join(workbook_folder, 'Items.json')

    @staticmethod
    def _get_datasources_json_file(workbook_folder):
        return os.path.join(workbook_folder, 'Datasources.json')

    @staticmethod
    def _get_datasource_map_json_file(workbook_folder, datasource_map):
        return os.path.join(
            workbook_folder, system.cleanse_filename(
                'Datasource_Map_%s_%s_%s.json' % (datasource_map['Datasource Class'],
                                                  datasource_map['Datasource ID'],
                                                  datasource_map['Datasource Name'])))

    def save(self, workbook_folder=None, *, overwrite=False, include_rendered_content=False,
             pretty_print_html=False):
        if not workbook_folder:
            workbook_folder = self._get_default_workbook_folder()

        if os.path.exists(workbook_folder):
            if overwrite:
                system.removetree(workbook_folder, keep_top_folder=True)
            else:
                raise SPyRuntimeError('"%s" folder exists. Use shutil.rmtree() to remove it, but be careful not to '
                                      'accidentally delete your work!' % workbook_folder)

        os.makedirs(workbook_folder, exist_ok=True)

        workbook_json_file = Workbook._get_workbook_json_file(workbook_folder)

        definition_dict = dict(self.definition)
        definition_dict['Worksheets'] = list()
        for worksheet in self.worksheets:
            worksheet.save(workbook_folder, include_rendered_content=include_rendered_content,
                           pretty_print_html=pretty_print_html)
            definition_dict['Worksheets'].append(worksheet.id)

        if include_rendered_content:
            _render.toc(self, workbook_folder)

        with open(workbook_json_file, 'w', encoding='utf-8') as f:
            json.dump(definition_dict, f, indent=4)

        items_json_file = Workbook._get_items_json_file(workbook_folder)
        with open(items_json_file, 'w', encoding='utf-8') as f:
            json.dump(self.item_inventory, f, indent=4, sort_keys=True, cls=ItemJSONEncoder)

        datasources_json_file = Workbook._get_datasources_json_file(workbook_folder)
        clean_datasource_inventory = {
            (Workbook.NULL_DATASOURCE_STRING if k is None else k): v for k, v in self.datasource_inventory.items()
        }
        with open(datasources_json_file, 'w', encoding='utf-8') as f:
            json.dump(clean_datasource_inventory, f, indent=4, sort_keys=True, cls=ItemJSONEncoder)

        for datasource_map in self.datasource_maps:
            datasource_map_file = Workbook._get_datasource_map_json_file(workbook_folder, datasource_map)
            with open(datasource_map_file, 'w', encoding='utf-8') as f:
                json.dump(datasource_map, f, indent=4)

    @staticmethod
    def load(workbook_folder):
        if not os.path.exists(workbook_folder):
            raise SPyRuntimeError('Workbook folder "%s" does not exist' % workbook_folder)

        workbook_json_file = Workbook._get_workbook_json_file(workbook_folder)
        if not os.path.exists(workbook_json_file):
            raise SPyRuntimeError('Workbook JSON file "%s" does not exist' % workbook_json_file)

        with open(workbook_json_file, 'r', encoding='utf-8') as f:
            definition = json.load(f)

        workbook = Workbook._instantiate(definition)
        workbook._load(workbook_folder)

        return workbook

    def _load(self, workbook_folder):
        self.provenance = Item.LOAD

        self.worksheets = list()
        for worksheet_id in self.definition['Worksheets']:
            Worksheet.load_from_workbook_folder(self, workbook_folder, worksheet_id)

        del self.definition['Worksheets']

        self.item_inventory = Workbook._load_inventory(Workbook._get_items_json_file(workbook_folder))
        for scope_item in self.item_inventory.values():
            scope_item.scoped_to = self

        self.datasource_inventory = Workbook._load_inventory(Workbook._get_datasources_json_file(workbook_folder))
        self.datasource_maps = Workbook.load_datasource_maps(workbook_folder)

    @staticmethod
    def load_datasource_maps(folder):
        if not os.path.exists(folder):
            raise SPyRuntimeError('Datasource map folder "%s" does not exist' % folder)

        datasource_map_files = glob.glob(os.path.join(folder, 'Datasource_Map_*.json'))
        datasource_maps = list()
        for datasource_map_file in datasource_map_files:
            with open(datasource_map_file, 'r', encoding='utf-8') as f:
                datasource_map = json.load(f)
                datasource_map['File'] = datasource_map_file
                datasource_maps.append(datasource_map)

        return datasource_maps

    @staticmethod
    def _load_inventory(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            loaded_inventory = json.load(f)

        inventory_dict = dict()
        for item_id, item_def in loaded_inventory.items():
            if item_id == Workbook.NULL_DATASOURCE_STRING:
                item_id = None
            inventory_dict[item_id] = Item.load(item_def)

        return inventory_dict

    def _scrape_datasource_inventory(self, session: Session):
        referenced_datasources: Dict[str, Union[DatasourceOutputV1, DatasourcePreviewV1]] = dict()
        referenced_datasources.update(self._scrape_auth_datasources(session))
        for item in self.item_inventory.values():  # type: Item
            referenced_datasources.update(item._scrape_auth_datasources(session))
            if item.datasource:
                referenced_datasources[item.datasource.id] = item.datasource

        self.datasource_inventory = dict()
        for datasource in referenced_datasources.values():
            self.datasource_inventory[datasource.id] = Datasource.from_datasource_output(datasource)

        return self.datasource_inventory

    def _construct_default_datasource_maps(self):
        self.datasource_maps = list()
        for _id, datasource in self.datasource_inventory.items():
            datasource_map = {
                'Datasource Class': datasource['Datasource Class'],
                'Datasource ID': datasource['Datasource ID'],
                'Datasource Name': datasource['Name'],
                _common.DATASOURCE_MAP_ITEM_LEVEL_MAP_FILES: list(),
                _common.DATASOURCE_MAP_REGEX_BASED_MAPS: [
                    {
                        'Old': {
                            'Type': r'(?<type>.*)',

                            'Datasource Class':
                                _common.escape_regex(datasource['Datasource Class']) if datasource[
                                    'Datasource Class'] else None,

                            'Datasource Name': _common.escape_regex(datasource['Name']) if datasource['Name'] else None
                        },
                        'New': {
                            'Type': '${type}',

                            # Why isn't datasource['Datasource Class'] re.escaped? Because in
                            # StoredOrCalculatedItem._lookup_in_regex_based_map() we use ItemsApi.search_items() to
                            # look up a Datasource by its name and Datasource Class is not a property that can accept
                            # a regex. See CRAB-21154 for more context on what led to this.
                            'Datasource Class': datasource['Datasource Class'],

                            'Datasource Name': _common.escape_regex(datasource['Name']) if datasource['Name'] else None
                        }
                    }
                ]
            }

            if datasource['Datasource Class'] in ['Auth', 'Windows Auth', 'LDAP', 'OAuth 2.0']:
                datasource_map['RegEx-Based Maps'].append(copy.deepcopy(datasource_map['RegEx-Based Maps'][0]))

                datasource_map['RegEx-Based Maps'][0]['Old']['Type'] = 'User'
                datasource_map['RegEx-Based Maps'][0]['Old']['Username'] = r'(?<username>.*)'
                datasource_map['RegEx-Based Maps'][0]['New']['Type'] = 'User'
                datasource_map['RegEx-Based Maps'][0]['New']['Username'] = '${username}'

                datasource_map['RegEx-Based Maps'][1]['Old']['Type'] = 'UserGroup'
                datasource_map['RegEx-Based Maps'][1]['Old']['Name'] = r'(?<name>.*)'
                datasource_map['RegEx-Based Maps'][1]['New']['Type'] = 'UserGroup'
                datasource_map['RegEx-Based Maps'][1]['New']['Name'] = '${name}'
            else:
                datasource_map['RegEx-Based Maps'][0]['Old']['Data ID'] = r'(?<data_id>.*)'
                datasource_map['RegEx-Based Maps'][0]['New']['Data ID'] = '${data_id}'

            self.datasource_maps.append(datasource_map)

    def _scrape_item_inventory(self, session: Session):
        self._scrape_references_from_scope(session)

        self._scrape_folder_inventory(session)

        for reference in self.referenced_items:
            self._scrape_inventory_from_item(session, reference.id)

        self._scrape_inventory_from_ancillaries(session)

    def _scrape_folder_inventory(self, session: Session):
        if 'Ancestors' not in self:
            return

        for ancestor_id in self['Ancestors']:
            self.update_status('Scraping folders', 0)

            if not _common.is_guid(ancestor_id):
                # This is a synthetic folder, analagous to "Users" and "Shared" in the Seeq Home Screen
                continue

            try:
                item = Item.pull(ancestor_id, allowed_types=['Folder'], session=session)
            except ApiException as e:
                if e.status == 404:
                    continue

                self.item_pull_errors.add(f'Error pulling folder {ancestor_id}: {_common.format_exception()}')
                continue

            if item is None:
                continue

            self.update_status('Scraping folders', 1)

            self.add_to_scope(item)

    def _scrape_inventory_from_item(self, session: Session, item_id):
        if item_id in self.item_inventory:
            return

        allowed_types = [
            'StoredSignal',
            'CalculatedSignal',
            'StoredCondition',
            'CalculatedCondition',
            'CalculatedScalar',
            'Chart',
            'ThresholdMetric',
            'TableDatasource'
        ]

        self.update_status('Scraping item inventory', 0)

        try:
            item = Item.pull(item_id, allowed_types=allowed_types, session=session)
        except ApiException as e:
            if e.status == 404:
                return

            self.item_pull_errors.add(f'Error pulling inventory from item {item_id}: {_common.format_exception()}')
            return

        if item is None:
            return

        if 'Is Generated' in item and item['Is Generated']:
            return

        self.update_status('Scraping item inventory', 1)

        self.add_to_scope(item)

        dependencies = self._scrape_references_from_dependencies(session, item_id)

        for dependency in dependencies:
            if dependency.id in self.item_inventory:
                continue

            self.update_status('Scraping item dependency', 0)

            try:
                dep_item = Item.pull(dependency.id, allowed_types=allowed_types, session=session)
            except ApiException as e:
                if e.status == 404:
                    continue

                self.item_pull_errors.add(f'Error pulling dependency {dependency.id}: {_common.format_exception()}')
                continue

            if dep_item is None:
                continue

            if 'Is Generated' in dep_item and dep_item['Is Generated']:
                continue

            self.update_status('Scraping item dependency', 1)

            self.add_to_scope(dep_item)

    def _scrape_references_from_scope(self, session: Session):
        items_api = ItemsApi(session.client)

        self.update_status('Scraping scope references', 0)

        self.scoped_items = list()
        offset = 0
        while True:
            # noinspection PyBroadException
            try:
                search_results = items_api.search_items(
                    filters=['', '@excludeGloballyScoped'],
                    scope=[self.id],
                    offset=offset,
                    limit=session.options.search_page_size,
                )  # type: ItemSearchPreviewPaginatedListV1
            except BaseException:
                self.item_pull_errors.add(f'Error scraping items scoped to workbook {self.id}: '
                                          f'{_common.format_exception()}')
                break

            self.scoped_items.extend([Reference(item.id, Reference.SCOPED) for item in search_results.items])

            if len(search_results.items) < search_results.limit:
                break

            offset += search_results.limit

    def _scrape_references_from_dependencies(self, session: Session, item_id):
        items_api = ItemsApi(session.client)
        referenced_items = list()

        self.update_status('Scraping dependencies', 0)

        try:
            dependencies = items_api.get_formula_dependencies(id=item_id)  # type: ItemDependencyOutputV1
        except ApiException as e:
            if e.status == 404:
                # For some reason, the item_id is unknown. We've seen this at Exxon, so just skip it.
                return referenced_items

            self.item_pull_errors.add(f'Error scraping dependencies for item {item_id}: {_common.format_exception()}')
            return referenced_items

        for dependency in dependencies.dependencies:  # type: ItemParameterOfOutputV1
            referenced_items.append(Reference(
                dependency.id,
                Reference.DEPENDENCY
            ))

        return referenced_items

    def _scrape_inventory_from_ancillaries(self, session: Session):
        self.update_status('Scraping ancillaries', 0)

        current_inventory = list(self.item_inventory.values())
        for item in current_inventory:
            if 'Ancillaries' not in item:
                continue

            for ancillary_dict in item['Ancillaries']:
                if 'Items' not in ancillary_dict:
                    continue

                # Only scrape ancillaries that are globally scoped or scoped to this workbook
                scoped_to = _common.get(ancillary_dict, 'Scoped To')
                if scoped_to is not None and scoped_to != self.id:
                    continue

                for ancillary_item_dict in ancillary_dict['Items']:
                    self._scrape_inventory_from_item(session, _common.get(ancillary_item_dict, 'ID'))

    def add_to_scope(self, item):
        if not isinstance(item, (StoredOrCalculatedItem, Folder)):
            raise SPyTypeError('Workbook.add_to_scope only accepts Stored or Calculated items. You tried to add:\n%s',
                               item)

        self.item_inventory[item.id] = item

        if not isinstance(item, Folder):
            item.scoped_to = self

    def _get_worksheet(self, name) -> Union[AnalysisWorksheet, TopicDocument, None]:
        for worksheet in self.worksheets:
            if worksheet.name == name:
                return worksheet

        return None


class Analysis(Workbook):
    def worksheet(self, name: str, create: bool = True) -> Optional[AnalysisWorksheet]:
        existing_worksheet = self._get_worksheet(name)
        if existing_worksheet:
            return existing_worksheet
        elif not create:
            return None

        return AnalysisWorksheet(self, {'Name': name})


class Topic(Workbook):
    def document(self, name: str, create: bool = True) -> Optional[TopicDocument]:
        existing_document = self._get_worksheet(name)
        if existing_document:
            return existing_document
        elif not create:
            return None

        return TopicDocument(self, {'Name': name})

    def pull_rendered_content(self, session: Session, *, errors='raise', quiet=False, status: Status = None):
        status = Status.validate(status, quiet)

        for worksheet in self.worksheets:
            timer = _common.timer_start()
            worksheet.pull_rendered_content(session, errors=errors, quiet=quiet,
                                            status=status.create_inner(
                                                f'Pull Embedded Content {worksheet}'))
            status.df.at[worksheet.id, 'Name'] = worksheet.name
            if worksheet.document.rendered_content_images is None:
                status.df.at[worksheet.id, 'Count'] = np.nan
            else:
                status.df.at[worksheet.id, 'Count'] = len(worksheet.document.rendered_content_images)
            status.df.at[worksheet.id, 'Time'] = _common.timer_elapsed(timer)
