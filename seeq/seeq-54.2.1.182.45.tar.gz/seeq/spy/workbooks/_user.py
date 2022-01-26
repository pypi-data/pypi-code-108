from typing import List, Optional, Dict, Union

from seeq.sdk import *
from seeq.spy import _common
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy.workbooks._data import StoredItem
from seeq.spy.workbooks._item import Item

ORIGINAL_OWNER = '__original__'
FORCE_ME_AS_OWNER = '__me__'


class ItemWithOwnerAndAcl(Item):
    def decide_owner(self, session: Session, datasource_maps, item_map, *, owner=None, current_owner_id=None):
        requires_admin = True
        if _common.is_guid(owner):
            owner_id = owner
        elif owner is None:
            requires_admin = False
            if current_owner_id is None:
                owner_id = session.user.id
            else:
                owner_id = current_owner_id
        elif owner == ORIGINAL_OWNER:
            owner_id = Identity.find_identity(session, self['Owner'], datasource_maps=datasource_maps,
                                              item_map=item_map)
        elif owner == FORCE_ME_AS_OWNER:
            owner_id = session.user.id
        else:
            raise SPyValueError('Invalid owner: %s' % owner)

        if current_owner_id is None or current_owner_id == owner_id:
            requires_admin = False

        if requires_admin and not session.user.is_admin:
            raise SPyRuntimeError("Logged in user must be an admin as a result of owner='%s'" % owner)

        return owner_id

    def _pull_owner_and_acl(self, session: Session, owner: IdentityPreviewV1):
        items_api = ItemsApi(session.client)

        if not owner.is_redacted:
            self['Owner'] = User.pull(owner.id, session=session).definition
        else:
            self['Owner'] = {'ID': owner.id}

        self['Owner']['Redacted'] = owner.is_redacted

        acl_output = items_api.get_access_control(id=self['ID'])  # type: AclOutputV1
        access_control = list()

        for ace_output in acl_output.entries:  # type: AceOutputV1
            ace_dict = Item._dict_via_attribute_map(ace_output, {
                'created_at': 'Created At',
                'id': 'ID',
                'role': 'Role'
            })

            ace_dict['Origin'] = ace_output.origin.id if ace_output.origin is not None else None
            ace_dict['Permissions'] = ItemWithOwnerAndAcl._permissions_to_dict(ace_output.permissions)
            ace_dict['Redacted'] = ace_output.identity.is_redacted

            if not ace_output.identity.is_redacted:
                if ace_output.identity.type == 'User':
                    identity = User.pull(ace_output.identity.id, session=session)
                else:
                    identity = UserGroup.pull(ace_output.identity.id, session=session)

                ace_dict['Identity'] = identity.definition
            access_control.append(ace_dict)

        self.definition['Access Control'] = access_control

    def _push_owner_and_location(self, session: Session, item_output, owner_id, folder_id):
        items_api = ItemsApi(session.client)
        folders_api = FoldersApi(session.client)

        if item_output.owner.id != owner_id:
            items_api.change_owner(item_id=item_output.id, new_owner_id=owner_id)

        if folder_id:
            folders_api.move_item_to_folder(folder_id=folder_id, item_id=item_output.id)

    def _push_acl(self, session: Session, pushed_id, datasource_maps, item_map, access_control):
        replace = False
        strict = False
        if access_control:
            treatment_parts = access_control.split(',')
            for treatment_part in treatment_parts:
                if treatment_part == 'add':
                    replace = False
                elif treatment_part == 'replace':
                    replace = True
                elif treatment_part == 'loose':
                    strict = False
                elif treatment_part == 'strict':
                    strict = True
                else:
                    raise SPyValueError("access_control argument must be 'add' or 'replace' comma 'loose' or "
                                        "'strict'. For example: replace,strict")

        if 'Access Control' not in self:
            return

        items_api = ItemsApi(session.client)
        acl_output = items_api.get_access_control(id=pushed_id)  # type: AclOutputV1
        acl_inputs = list()
        for acl_to_push in self['Access Control']:
            found = False

            try:
                identity_id = Identity.find_identity(session, acl_to_push['Identity'], datasource_maps, item_map)
            except SPyDependencyNotFound:
                if strict:
                    raise

                continue

            # We sort so that the system-managed entries are found first, and item-specific entries will be removed
            # if they're already covered by the system-managed entries
            sorted_acl_entries = sorted(acl_output.entries, key=lambda e: e.role != 'OWNER' and e.origin is None)
            for existing_acl in sorted_acl_entries:  # type: AceOutputV1
                if ItemWithOwnerAndAcl._permissions_to_dict(existing_acl.permissions) == \
                        acl_to_push['Permissions'] and existing_acl.identity.id == identity_id:
                    found = True
                    setattr(existing_acl, 'used', True)
                    break

            if found:
                continue

            permissions = ItemWithOwnerAndAcl._dict_to_permissions(acl_to_push['Permissions'])
            acl_inputs.append((pushed_id, permissions, identity_id))

        if replace:
            # It's important to remove the entries that need to be removed before adding. Otherwise, if you try to
            # add an ACE that conflicts with an existing entry, it will be silently ignored.
            for existing_acl in acl_output.entries:  # type: AceOutputV1
                if existing_acl.role == 'OWNER' or existing_acl.origin is not None:
                    # You can't remove OWNER or inherited permissions
                    continue

                if hasattr(existing_acl, 'used') and getattr(existing_acl, 'used'):
                    continue

                items_api.remove_access_control_entry(id=pushed_id, ace_id=existing_acl.id)

        for pushed_id, permissions, identity_id in acl_inputs:
            items_api.add_access_control_entry(id=pushed_id,
                                               body=AceInputV1(permissions=permissions,
                                                               identity_id=identity_id))

    @staticmethod
    def _dict_to_permissions(d):
        return PermissionsV1(
            manage=_common.get(d, 'Manage', False),
            read=_common.get(d, 'Read', False),
            write=_common.get(d, 'Write', False)
        )

    @staticmethod
    def _permissions_to_dict(permissions):
        """
        :type permissions: PermissionsV1
        """
        return {
            'Read': permissions.read,
            'Write': permissions.write,
            'Manage': permissions.manage
        }

    def _pull_ancestors(self, session: Session, ancestors: List[ItemPreviewV1]):
        if ancestors is None:
            return

        self.definition['Ancestors'] = \
            [(ancestor.id.upper() if ancestor.id is not None else f'__{ancestor.name}__')
             for ancestor in ancestors]

    @staticmethod
    def _find_auth_provider(session: Session, datasource_class, datasource_id) -> Optional[DatasourceOutputV1]:
        for auth_provider in session.auth_providers:
            if auth_provider.datasource_class == datasource_class and auth_provider.datasource_id == datasource_id:
                return auth_provider

        return None

    def _scrape_auth_datasources(self, session: Session) -> Dict[str, DatasourceOutputV1]:
        referenced_datasources: Dict[str, DatasourceOutputV1] = dict()

        def _scrape_auth_datasource(d, key):
            if key in d and 'Datasource Class' in d[key] and 'Datasource ID' in d[key]:
                auth_provider = ItemWithOwnerAndAcl._find_auth_provider(
                    session, d[key]['Datasource Class'], d[key]['Datasource ID'])
                if auth_provider:
                    referenced_datasources[auth_provider.id] = auth_provider

        _scrape_auth_datasource(self, 'Owner')
        if 'Access Control' in self:
            for acl in self['Access Control']:
                _scrape_auth_datasource(acl, 'Identity')

        return referenced_datasources


class Identity(StoredItem):
    @staticmethod
    def find_identity(session: Session, identity_dict, datasource_maps, item_map) -> str:
        if identity_dict['ID'] in item_map:
            return item_map[identity_dict['ID']]

        if identity_dict['Type'] == 'User':
            identity = User(identity_dict)
        else:
            identity = UserGroup(identity_dict)

        pushed_identity = identity.push(session, datasource_maps=datasource_maps, datasource_output=None,
                                        item_map=item_map)

        return pushed_identity.id

    def pull_datasource(self, session: Session, identity: Union[UserOutputV1, UserGroupOutputV1]):
        # noinspection PyBroadException
        try:
            if identity.type == 'User':
                users_api = UsersApi(session.client)
                user_output = users_api.get_user(id=identity.id)  # type: UserOutputV1

                for auth_provider in session.auth_providers:  # type: DatasourceOutputV1
                    if auth_provider.name == user_output.datasource_name:
                        self['Datasource Class'] = auth_provider.datasource_class
                        self['Datasource ID'] = auth_provider.datasource_id
                        self['Datasource Name'] = auth_provider.name
                        break
            else:
                # In .45, groups will come from different datasources. For now, hard-code it.
                # user_groups_api = UserGroupsApi(session.client)
                # user_group_output = user_groups_api.get_user_group(id=identity.id)  # type: UserGroupOutputV1
                self['Datasource Class'] = 'Auth'
                self['Datasource ID'] = 'Seeq'
                self['Datasource Name'] = 'Seeq'
        except KeyboardInterrupt:
            raise
        except BaseException:
            # If we can't get extra data on the user, that's OK
            pass


class User(Identity):
    @staticmethod
    def pull(item_id, *, allowed_types=None, status=None, session: Optional[Session] = None):
        session = Session.validate(session)
        users_api = UsersApi(session.client)
        user_output = users_api.get_user(id=item_id)  # type: UserOutputV1

        item = User({
            'ID': user_output.id,
            'Type': user_output.type,
            'Name': user_output.name,
            'Username': user_output.username,
            'First Name': user_output.first_name,
            'Last Name': user_output.last_name,
            'Email': user_output.email,
            'Is Admin': user_output.is_admin
        })

        item.pull_datasource(session, user_output)
        return item


class UserGroup(Identity):
    @staticmethod
    def pull(item_id, *, allowed_types=None, status=None, session: Optional[Session] = None):
        session = Session.validate(session)
        usergroups_api = UserGroupsApi(session.client)
        usergroup_output = usergroups_api.get_user_group(user_group_id=item_id)  # type: UserGroupOutputV1

        item = UserGroup({
            'ID': usergroup_output.id,
            'Type': usergroup_output.type,
            'Name': usergroup_output.name
        })

        item.pull_datasource(session, usergroup_output)
        return item
