# This file is part of Sympathy for Data.
# Copyright (c) 2020, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import copy
import os.path
import logging

from . import library
from . import user_commands
from . import version as sy_version
from sympathy.platform import parameter_helper
from sympathy.platform.exceptions import sywarn
from sympathy.platform.migrations import (
    Migration, MigrationStatus, MigrationNotAvailableError, NodeMigration)
from sympathy.utils import port, prim, components


migr_logger = logging.getLogger('core.migrations')

# Copy platform version into this module to allow changing it in tests.
platform_version = max(sy_version.parsed_version,
                       sy_version.parsed_base_version)
del sy_version


def _port_enumerator(ports, sy_ports=True):
    """Yields pairs of (port_id, port)."""
    i = 0
    last_name = None
    for port_ in ports:
        name = port_.name
        if name != last_name:
            i = 0
        if name.startswith('__sy_') and not sy_ports:
            continue
        yield (name, i), port_
        last_name = name
        i = i + 1


def _get_port(ports, port_id):
    for port_id_, port_ in _port_enumerator(ports):
        if port_id_ == port_id:
            return port_
    return None


def _get_port_ids(ports, sy_ports=True):
    """Return a list of port_ids for all ports."""
    return [port_id for port_id, port_ in _port_enumerator(
        ports, sy_ports=sy_ports)]


def _get_parameters(parameter_model):
    """Get a ParameterRoot from a parameter model."""
    parameter_dict = copy.deepcopy(parameter_model.data_dict())
    parameters = parameter_helper.ParameterRoot(parameter_dict)
    return parameters


class MigrationContext:
    def __init__(self, node=None, overrides=None, macro_cmd=None):
        self._node = node
        self._overrides = overrides
        self._flow = node.flow
        self._macro_cmd = macro_cmd

    def push(self, cmd):
        self._macro_cmd.push(cmd)

    def _remove_input_connections(self, old_node, port_mapping):
        """
        Remove all the input connections to old_node.

        Return a dictionary mapping keys in port_mapping to the actual source
        ports that that port was connected to.
        """
        res = {}
        flow = old_node.flow
        for port_id, old_port in _port_enumerator(old_node.inputs):
            connection = flow.input_connection_to_port(old_port)
            if connection is not None:
                source_port = connection.source
                self.push(user_commands.RemoveElementCommand(connection))
                res[port_id] = source_port
        return res

    def _remove_output_connections(self, old_node, port_mapping):
        """
        Remove all the output connections to old_node.

        Return a dictionary mapping keys in port_mapping to the actual source
        ports that that port was connected to.
        """
        res = {}
        flow = old_node.flow
        for port_id, old_port in _port_enumerator(old_node.outputs):
            connections = flow.output_connections_from_port(old_port)
            for connection in connections:
                destination_port = connection.destination
                self.push(user_commands.RemoveElementCommand(connection))
                res.setdefault(port_id, []).append(destination_port)
        return res

    # TODO: This method copies a lot of logic from
    # library_creator.get_properties()
    def _get_library_node(self, node_def):
        def icon_dirs_path(icon, icon_dirs):
            for icon_dir in icon_dirs:
                icon_path = os.path.join(icon_dir, icon)
                if os.path.exists(icon_path):
                    return icon_path

        lib_node_def = {}

        # TODO: This part takes file and class info from current implementation
        # of target node. Should use a special api (perhaps just a flag?) to
        # allow finding deleted nodes too.
        quickfix_library_node = self._flow.app_core.library_node(
            node_def['nodeid'])
        lib_node_def['class'] = quickfix_library_node.class_name
        lib_node_def['file'] = quickfix_library_node.source_uri
        lib_node_def['validate'] = quickfix_library_node.needs_validate

        lib_node_def['label'] = node_def['name']
        lib_node_def['id'] = node_def['nodeid']
        lib_node_def['type'] = 'python2'

        lib_node_def['version'] = node_def['version']
        for field in ('author', 'copyright', 'description', 'file',
                      'icon', 'nodeid'):
            if field in node_def:
                lib_node_def[field] = node_def[field]
                if not isinstance(node_def[field], str):
                    print('[{}] field {} is not a string'.format(
                        node_def['nodeid'], field))

        lib_node_def['parameters'] = {}
        try:
            lib_node_def['ports'] = port.port_structures_to_dict(
                node_def.get('inputs'),
                node_def.get('outputs'))
        except Exception:
            pass

        if 'tags' in node_def:
            try:
                lib_node_def['tags'] = node_def['tags'].to_dict()
            except Exception:
                pass

        # Check if we have a resource directory where icons could reside.
        nodedir = prim.uri_to_path(os.path.dirname(lib_node_def['file']))
        icon = node_def.get('icon')
        if icon:
            icon_path = icon_dirs_path(
                icon, [os.path.join(nodedir, '_resources'), nodedir])
            if icon_path:
                lib_node_def['icon'] = prim.localuri(icon_path)
            else:
                sywarn("Couldn't find icon for node {}".format(
                    node_def['name']))

        library_node = self._flow.app_core.library_node_from_definition(
            node_def['nodeid'], lib_node_def)
        return library_node

    def replace_node(self, old_node, new_node_def,
                     input_port_mapping, output_port_mapping):
        # Automatically include ports added by the platform
        input_port_mapping = input_port_mapping.copy()
        input_port_mapping.update({
            ('__sy_conf__', 0): ('__sy_conf__', 0)})
        output_port_mapping = output_port_mapping.copy()
        sy_names = [
            '__sy_conf__',
            '__sy_out__',
            '__sy_err__',
            '__sy_both__',
        ]
        output_port_mapping.update(
            {(name, 0): (name, 0) for name in sy_names})

        # Store internal ports enabled on old node
        sy_input_ports = {port.name for port in old_node.inputs} & set(sy_names)
        sy_output_ports = {port.name for port in old_node.outputs} & set(sy_names)

        # Remove connections to old node (saving them for later)
        input_connections = self._remove_input_connections(
            old_node, input_port_mapping)
        output_connections = self._remove_output_connections(
            old_node, output_port_mapping)

        # Remove all old overrides (saving them for later)
        old_overrides = []
        for parent_flow in old_node.flow.parent_flows():
            if not parent_flow.is_root_flow():
                model = old_node.get_override_parameter_model(parent_flow)
                old_overrides.append((parent_flow, model))
                self.push(user_commands.EditNodeOverrideParameters(
                    parent_flow, old_node, new_params_model=None))

        # Remove old node
        cmd = user_commands.RemoveElementCommand(old_node)
        self.push(cmd)

        # Create new node
        library_node = self._get_library_node(new_node_def)
        cmd = user_commands.CreateLibraryElementCommand(
            uuid=old_node.uuid,
            flow=self._flow,
            node_id=new_node_def['nodeid'],
            library_node=library_node,
            version=new_node_def['version'],
            position=old_node.position)
        self.push(cmd)
        new_node = cmd.created_element()
        if old_node.exec_conf_only:
            self.push(user_commands.EditNodeExecutionConfig(new_node, True))

        # Create internal ports enabled on old node
        for port_name in sy_input_ports:
            self.push(user_commands.CreateNamedInputPortCommand(
                new_node, port_name))
        for port_name in sy_output_ports:
            self.push(user_commands.CreateNamedOutputPortCommand(
                new_node, port_name))

        # Restore removed connections
        for old_port_id, source_port in input_connections.items():
            new_port_id = input_port_mapping[old_port_id]
            if new_port_id is not None:
                new_port = _get_port(new_node.inputs, new_port_id)
                if new_port is None:
                    cmd = user_commands.CreateNamedInputPortCommand(
                        new_node, new_port_id[0])
                    self.push(cmd)
                    new_port = cmd.created_element()
                self.push(user_commands.CreateConnectionCommand(
                    source_port, new_port, self._flow))
        for old_port_id, destination_ports in output_connections.items():
            new_port_id = output_port_mapping[old_port_id]
            if new_port_id is not None:
                new_port = _get_port(new_node.outputs, new_port_id)
                if new_port is None:
                    cmd = user_commands.CreateNamedOutputPortCommand(
                        new_node, new_port_id[0])
                    self.push(cmd)
                    new_port = cmd.created_element()
                for destination_port in destination_ports:
                    self.push(user_commands.CreateConnectionCommand(
                        new_port, destination_port, self._flow))

        # Set original_nodeid
        # Overrides now store the nodeid and version for which they apply, but
        # older overrides don't have that information. In order to allow old
        # overrides to migrate past a NodeMigration, we need to store the
        # original nodeid that the node had at version "0.0" (i.e. before
        # migrations system).
        self.push(user_commands.ChangeNodeOriginalNodeID(
            new_node, old_node.identifier))

        # Set all existing overrides on the new node
        for flow, model in old_overrides:
            self.push(user_commands.EditNodeOverrideParameters(
                flow, new_node, model))

        return new_node

    def get_parameters(self):
        """Return a copy of node's base parameters."""
        if self._overrides is not None:
            parameter_model = self._overrides
        else:
            parameter_model = self._node.base_parameter_model
        return _get_parameters(parameter_model)

    def warning(self, msg, node=None):
        """Display a warning in the messages view."""
        node = node or self._node
        self._flow.app_core.display_custom_node_message(node, warning=msg)


class MigrationChain:
    """
    An unbroken chain of migrations from one version to another.

    Can be empty.

    May also include one or more NodeMigrations which replace the node with
    another.
    """
    def __init__(self, node):
        self._node = node
        self._flow = node.flow
        self._library_node = node.library_node
        self._from_version = node.version

        self._init_migration_classes(
            self._node.base_parameter_model,
            self._node.identifier,
        )

    def _init_migration_classes(self, parameter_model, current_nodeid,
                                target_version=None, target_nodeid=None):
        self._auto_migrations = []
        self._manual_migrations = []
        self._unavailable_migrations = []
        self._ignored_migrations = []
        self._auto_parameters = None
        self._auto_target_exists = True
        self._manual_target_exists = True

        try:
            current_parameters = _get_parameters(parameter_model)
        except Exception:
            # Building parameters should never fail, but if it does, there is
            # no need for migrations to fail too.
            import traceback
            migr_logger.error(
                "Ignoring all migrations for node %s due to error when "
                "building parameters:\n%s", self._node, traceback.format_exc())
            return
        self._auto_parameters = copy.deepcopy(current_parameters)

        # TODO: MigrationChains are instantiated for nodes that are not yet
        # added to a flow, which means that they have no access to app_core and
        # so we can not know what migration classes exist.
        if self._flow is None:
            return

        def get_migration_class(nodeid, from_version):
            try:
                library_node = self._flow.app_core.library_node(nodeid)
            except KeyError:
                return None
            migrations_for_nodeid = sorted(
                library_node.migrations,
                key=lambda migr: migr.from_version)
            for migration_cls in migrations_for_nodeid:
                if migration_cls.from_version == from_version:
                    return migration_cls
            return None

        def implementation_exists(nodeid, version):
            """Return True if nodeid has version in node library."""
            try:
                library_node = self._flow.app_core.library_node(nodeid)
            except KeyError:
                return False
            return library_node.version == version

        target_version = target_version or platform_version
        current = self._auto_migrations
        current_version = self._from_version

        while True:
            try:
                migration_cls = get_migration_class(
                    current_nodeid, current_version)
                if migration_cls is None:
                    break
                migr_logger.debug(
                    "Testing migration: %s", migration_cls.__name__)
                _migration_ctx, migration = self._init_migration(
                    None, migration_cls)

                # Update which list of migration classes is the current one
                if (migration_cls.to_version > target_version
                        or current_nodeid == target_nodeid
                        and issubclass(migration_cls, NodeMigration)):
                    # This migration would take us past target nodeid/version
                    current = self._ignored_migrations
                if current is self._auto_migrations and not self._is_auto(
                        migration, current_parameters):
                    current = self._manual_migrations
                if (current is self._manual_migrations
                        and not self._is_available(
                            migration, current_parameters)):
                    current = self._unavailable_migrations

                # Update current parameters and nodeid
                if (current is self._auto_migrations
                        or current is self._manual_migrations):
                    current_parameters = migration.forward_parameters(
                        current_parameters)
                current_version = migration_cls.to_version
                if issubclass(migration_cls, NodeMigration):
                    current_nodeid = migration.forward_node()['nodeid']
                current.append(migration_cls)

                # Update members describing the last auto/manual result
                impl_exists = implementation_exists(
                    current_nodeid, current_version)
                if current is self._auto_migrations:
                    self._auto_target_exists = impl_exists
                    self._auto_parameters = copy.deepcopy(current_parameters)
                else:
                    self._manual_target_exists = impl_exists
            except Exception:
                # TODO: Should this be a node message? It might print too often
                migr_logger.error(
                    "Error when dry-running migration: %s. Ignoring this "
                    "and following migrations.", migration_cls)
                import traceback
                migr_logger.error(traceback.format_exc())
                break

    def _is_auto(self, migration, parameters):
        """Return True if migration can be performed automatically."""
        if isinstance(migration, NodeMigration):
            return False
        return migration.forward_status() == MigrationStatus.Perfect

    def _is_available(self, migration, parameters):
        """Return True if migration is available for manual migration."""
        return migration.forward_status() != MigrationStatus.NotAvailable

    @property
    def auto_migrated_parameters(self):
        return library.ParameterModel.from_dict({
            'data': self._auto_parameters._parameter_dict,
            'type': 'json',
        })

    def auto_migrated_version(self):
        if not self._auto_migrations:
            return self._from_version
        return self._auto_migrations[-1].to_version

    def forward(self, macro_cmd, auto_only=False):
        """
        Full migration, including non-auto migrations.

        This function runs user code and so should always be called from inside
        a try...except block.
        """
        migration_classes = list(self._auto_migrations)
        if not auto_only:
            migration_classes += self._manual_migrations
        if not migration_classes:
            raise MigrationNotAvailableError("No migrations")

        for migration_cls in migration_classes:
            migration_ctx, migration = self._init_migration(
                macro_cmd, migration_cls)

            # Check migration status
            status = migration.forward_status()
            msg = None
            if isinstance(status, tuple):
                status, msg = status
            if status == MigrationStatus.NotAvailable:
                if msg is not None:
                    raise MigrationNotAvailableError(msg)
                else:
                    raise MigrationNotAvailableError()

            # Do the migration
            migr_logger.info(
                "Running migration: %s from version %s to %s",
                migration_cls, migration_cls.from_version,
                migration_cls.to_version)
            self._forward_single(migration, migration_ctx)

            # Warn if status was Imperfect
            if status == MigrationStatus.Imperfect:
                if msg is None:
                    msg = ("Node may not have been migrated correctly, "
                           "please check configuration and output.")
                migration_ctx.warning(msg, node=self._node)

    def _init_migration(self, macro_cmd, migration_cls):
        """Instantiate the migration class"""
        migration_ctx = MigrationContext(self._node, macro_cmd=macro_cmd)
        migration = migration_cls(migration_ctx)
        return migration_ctx, migration

    def _forward_single(self, migration, migration_ctx):
        """Run a single migration"""
        # Replace node in case of NodeMigration
        new_node = self._node
        if isinstance(migration, NodeMigration):
            new_node_def = migration.forward_node()
            new_node_def['version'] = migration.to_version
            old_input_port_ids = _get_port_ids(
                self._node.inputs, sy_ports=False)
            old_output_port_ids = _get_port_ids(
                self._node.outputs, sy_ports=False)
            new_input_port_ids, new_output_port_ids = migration.forward_ports(
                old_input_port_ids, old_output_port_ids)
            if len(new_input_port_ids) != len(old_input_port_ids):
                raise ValueError(
                    f"Not all input ports are mapped to new ports:\n"
                    f"  Old: {old_input_port_ids}\n"
                    f"  New: {new_input_port_ids}")
            if len(new_output_port_ids) != len(old_output_port_ids):
                raise ValueError(
                    f"Not all output ports are mapped to new ports:\n"
                    f"  Old: {old_output_port_ids}\n"
                    f"  New: {new_output_port_ids}")
            input_port_mapping = dict(zip(
                old_input_port_ids, new_input_port_ids))
            output_port_mapping = dict(zip(
                old_output_port_ids, new_output_port_ids))
            new_node = migration_ctx.replace_node(
                self._node,
                new_node_def,
                input_port_mapping,
                output_port_mapping,
            )
        self._node = new_node
        self._library_node = new_node.library_node

        # Update parameters
        old_parameters = migration_ctx.get_parameters()
        new_parameters = migration.forward_parameters(old_parameters)
        new_parameter_model = library.ParameterModel.from_dict({
            'data': new_parameters._parameter_dict,
            'type': 'json',
        })
        migration_ctx.push(user_commands.EditNodeBaseParameters(
            new_node, new_parameter_model, new_version=migration.to_version))
        self._from_version = migration.to_version

    def gui_status(self):  # -> Optional[str]:
        """Return the status of a whole chain of migrations."""
        if self._manual_migrations and self._manual_target_exists:
            return 'yellow'
        elif self._auto_migrations and self._auto_target_exists:
            return 'green'
        elif self._unavailable_migrations and not self._auto_target_exists:
            return 'red'
        else:
            return None

    def debug_dict(self):
        def migrations_list(migrations):
            return ['{v1} -> {v2}: {name}({type_})'.format(
                v1=cls.from_version,
                v2=cls.to_version,
                name=cls.__name__,
                type_='node' if issubclass(cls, NodeMigration) else 'basic',
            ) for cls in migrations]

        return {
            'node id': self._library_node.node_identifier,
            'node version': str(self._node.version),
            'node library version': str(self._library_node.version),
            'platform version': str(platform_version),
            'deprecated': self._library_node.deprecated,
            'gui status': self.gui_status(),
            'auto migrations': migrations_list(self._auto_migrations),
            'auto target exists': self._auto_target_exists,
            'manual migrations': migrations_list(self._manual_migrations),
            'manual target exists': self._manual_target_exists,
            'unavailable migrations': migrations_list(
                self._unavailable_migrations),
            'ignored migrations': migrations_list(self._ignored_migrations),
        }


class OverridesMigrationChain(MigrationChain):
    """
    MigrationChain operating on overrides instead of a node.
    """
    def __init__(self, node, overrides_model, subflow):
        self._node = node
        self._flow = subflow
        self._overrides = overrides_model
        self._from_version = self._overrides.get_version()
        self._library_node = self._flow.app_core.library_node(
            self._overrides.get_nodeid())

        self._init_migration_classes(
            overrides_model,
            self._overrides.get_nodeid(),
            target_nodeid=self._node.identifier,
            target_version=self._node.auto_migrated_base_version(),
        )

    def _init_migration(self, macro_cmd, migration_cls):
        """Instantiate the migration class"""
        migration_ctx = MigrationContext(
            self._node, macro_cmd=macro_cmd, overrides=self._overrides)
        migration = migration_cls(migration_ctx)
        return migration_ctx, migration

    def _forward_single(self, migration, migration_ctx):
        # Replace node in case of NodeMigration
        new_nodeid = self._node.identifier
        if isinstance(migration, NodeMigration):
            new_node_def = migration.forward_node()
            new_nodeid = new_node_def['nodeid']
        self._library_node = self._flow.app_core.library_node(new_nodeid)

        # Update parameters
        old_parameters = migration_ctx.get_parameters()
        new_parameters = migration.forward_parameters(old_parameters)
        new_overrides_model = library.OverridesModel.from_dict({
            'data': new_parameters._parameter_dict,
            'type': 'json',
            'version': str(migration.to_version),
            'nodeid': new_nodeid,
        })
        migration_ctx.push(user_commands.EditNodeOverrideParameters(
            self._flow, self._node, new_overrides_model))
        self._from_version = migration.to_version
        self._overrides = new_overrides_model

    def _is_auto(self, migration, parameters):
        """Return True if migration can be performed automatically."""
        return migration.forward_status() == MigrationStatus.Perfect

    def gui_status(self):  # -> Optional[str]:
        """Return the status of a whole chain of migrations."""
        same_node = self._node.identifier == self._library_node.node_identifier
        old = self._from_version < self._node.version
        if same_node and not old:
            return None
        return super().gui_status()

    def debug_dict(self):
        res = super().debug_dict()
        res['overrides_version'] = str(self._overrides.get_version())
        res['overrides_old'] = self._from_version < self._node.version
        res['overrides_same_node'] = (
            self._node.identifier == self._library_node.node_identifier)
        return res


def migrations_from_file(filename):
    migration_classes = components.get_subclasses_env(
        components.get_file_env(filename, no_raise=True),
        Migration).values()
    return [cls for cls in migration_classes
            if cls is not Migration]
