from typing import List

from seeq.sdk import *
from seeq.spy import _common
from seeq.spy._session import Session
from seeq.spy.workbooks._item import Item
from seeq.spy.workbooks._user import ItemWithOwnerAndAcl

SHARED = '__Shared__'
CORPORATE = '__Corporate__'
ALL = '__All__'
USERS = '__Users__'
MY_FOLDER = '__My_Folder__'
PUBLIC = '__Public__'

SYNTHETIC_FOLDERS = [MY_FOLDER, SHARED, CORPORATE, ALL, USERS, PUBLIC]


def massage_ancestors(session: Session, item: Item):
    if not session.corporate_folder:
        return

    if len(item.definition['Ancestors']) > 0 and item.definition['Ancestors'][0] == session.corporate_folder.id:
        # Why replace the Corporate folder ID with the CORPORATE string token? The user doesn't want to have to
        # deal with the ID of the corporate folder, especially when importing/exporting workbooks from one server to
        # another.
        item.definition['Ancestors'][0] = CORPORATE


def synthetic_folder_to_content_filter(synthetic_folder):
    # If synthetic_folder is MY_FOLDER, the corresponding content_filter would be 'OWNER', otherwise,  it would be the
    #  synthetic_folder formatted for use by the Folders API
    content_filter = 'OWNER' if synthetic_folder == MY_FOLDER else synthetic_folder.replace('__', '').upper()
    return content_filter


class Folder(ItemWithOwnerAndAcl):
    def _pull(self, session: Session, item_id):
        folders_api = FoldersApi(session.client)
        folder_output = folders_api.get_folder(folder_id=item_id)  # type: FolderOutputV1
        self._pull_owner_and_acl(session, folder_output.owner)
        self._pull_ancestors(session, folder_output.ancestors)
        self.provenance = Item.PULL

    def _pull_ancestors(self, session: Session, ancestors: List[ItemPreviewV1]):
        super()._pull_ancestors(session, ancestors)
        massage_ancestors(session, self)

    def _find_by_name(self, session: Session, folder_id):
        folders_api = FoldersApi(session.client)

        if folder_id and folder_id != _common.PATH_ROOT:
            folders = folders_api.get_folders(filter='owner',
                                              folder_id=folder_id,
                                              limit=10000)  # type: WorkbenchItemOutputListV1
        else:
            folders = folders_api.get_folders(filter='owner',
                                              limit=10000)  # type: WorkbenchItemOutputListV1

        content_dict = {content.name.lower(): content for content in folders.content}
        if self.name.lower() in content_dict and content_dict[self.name.lower()].type == 'Folder':
            return content_dict[self.name.lower()]

        return None

    def push(self, session: Session, parent_folder_id, datasource_maps, datasource_output, item_map, *, owner=None,
             label=None, access_control=None):
        items_api = ItemsApi(session.client)
        folders_api = FoldersApi(session.client)
        folder_item = self.find_me(session, label, datasource_output)

        if folder_item is None and self.provenance == Item.CONSTRUCTOR:
            folder_item = self._find_by_name(session, parent_folder_id)

        if not folder_item:
            folder_input = FolderInputV1()
            folder_input.name = self['Name']
            if 'Description' in self:
                folder_input.description = self['Description']
            folder_input.owner_id = self.decide_owner(session, datasource_maps, item_map, owner=owner)
            folder_input.parent_folder_id = parent_folder_id if parent_folder_id != _common.PATH_ROOT else None

            folder_output = folders_api.create_folder(body=folder_input)

            items_api.set_properties(id=folder_output.id, body=[
                ScalarPropertyV1(name='Datasource Class', value=datasource_output.datasource_class),
                ScalarPropertyV1(name='Datasource ID', value=datasource_output.datasource_id),
                ScalarPropertyV1(name='Data ID', value=self._construct_data_id(label))])
        else:
            folder_output = folders_api.get_folder(folder_id=folder_item.id)  # type: FolderOutputV1

            props = [ScalarPropertyV1(name='Name', value=self['Name'])]
            if 'Description' in self:
                props.append(ScalarPropertyV1(name='Description', value=self['Description']))

            # If the folder happens to be archived, un-archive it. If you're pushing a new copy it seems likely
            # you're intending to revive it.
            props.append(ScalarPropertyV1(name='Archived', value=False))

            items_api.set_properties(id=folder_output.id, body=props)

            owner_id = self.decide_owner(session, datasource_maps, item_map, owner=owner,
                                         current_owner_id=folder_output.owner.id)

            self._push_owner_and_location(session, folder_output, owner_id, parent_folder_id)

        item_map[self.id.upper()] = folder_output.id.upper()

        if access_control:
            self._push_acl(session, folder_output.id, datasource_maps, item_map, access_control)

        return folder_output
