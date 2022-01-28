import os
import json
import time
import re
from collections import defaultdict

from kabaret import flow

from .maputils import SimpleCreateAction


class DependencyTemplate(flow.Object):

    dependencies = flow.Param('').ui(editor='textarea')
    defaults = flow.OrderedStringSetParam()

    def get_dependencies(self):
        return json.loads(self.dependencies.get())

    def get_default_dependency_names(self):
        return self.defaults.get()

    def get_dependency_files(self, name):
        deps = self.get_dependencies()[name]
        
        if 'files' in deps:
            return deps['files']
        
        return deps

    def get_asset_files(self, asset_name):
        kitsu_bindings = self.root().project().kitsu_bindings()
        asset = kitsu_bindings.get_asset_data(asset_name)

        return self.get_dependency_files('kitsu.'+asset['type'])


class DependencyTemplates(flow.Map):

    add_template = flow.Child(SimpleCreateAction)

    @classmethod
    def mapped_type(cls):
        return DependencyTemplate


class FileSystemItem:

    def __init__(self, entity_name, entity_oid, department, name, revision, project):
        self._entity_name = entity_name
        self._entity_oid = entity_oid
        self._department = department
        self._name = name
        self._project = project
        self._is_real = False
        self._path = None

        self._revision = self._get_revision_name(revision)

    @staticmethod
    def _get_shot_entity_name(department, file_name):
        '''
        Cheat function, for now, to get shot entity name based on file name.
        '''
        return file_name.split('.')[0]

    @classmethod
    def _get_name(cls, flow_name):
        raise NotImplementedError()

    @classmethod
    def _args_from_path(cls, path, project):
        entity_oid = project.oid()
        entity_name = 'undefined'
        shot_match = re.search("/(siren|siren_test)/sq\d\d/sc\d\d\d\d/.*/.*/v\d\d\d", path)

        if shot_match is not None:
            subpath = shot_match.group(0)[1:]
            (
                film,
                sequence,
                shot,
                department,
                name,
                revision,
            ) = subpath.split('/')

            name = cls._get_name(name)
            entity_name = cls._get_shot_entity_name(department, name)

            entity_oid += f"/films/{film}/sequences/{sequence}/shots/{shot}"
            return entity_name, entity_oid, department, name, revision

        asset_match = re.search("/lib/(chars|props|sets)/.*/.*/.*/.*/v\d\d\d", path)

        if asset_match is not None:
            subpath = asset_match.group(0)[5:]
            (
                asset_type,
                asset_family,
                asset_name,
                department,
                name,
                revision,
            ) = subpath.split('/')

            name = cls._get_name(name)

            entity_oid += f"/asset_lib/asset_types/{asset_type}/asset_families/{asset_family}/assets/{asset_name}"
            return asset_name, entity_oid, department, name, revision

        return entity_name, entity_oid, 'undefined', 'undefined', 'undefined'

    def _get_revision_name(self, revision):
        name = revision

        if revision == 'last':
            obj = self.related_object()
            name = None

            if obj is not None:
                revision_object = obj.get_head_revision()

                if revision_object is not None:
                    name = revision_object.name()

        return name

    @classmethod
    def create_from_path(cls, path, project):
        raise NotImplementedError()

    def exists(self):
        session = self._project.root().session()
        return session.cmds.Flow.exists(self.oid())

    def related_object(self):
        if not self.exists():
            return None
        return self._project.root().get_object(self.oid())

    def name(self):
        return self._name

    def flow_name(self):
        return self._name.replace('.', '_')

    def oid(self):
        return (
              self.entity_oid()
            + "/departments/"
            + self._department
            + "/files/"
            + self.flow_name()
        )

    def last_revision(self):
        return self._get_revision_name('last')

    def revision_exists(self):
        if self.revision_oid() is None:
            return False

        session = self._project.root().session()
        return session.cmds.Flow.exists(self.revision_oid())

    def related_revision_object(self, revision_name=None):
        if not self.revision_exists():
            return None

        if revision_name is None:
            revision_name = self.revision()

        return self._project.root().get_object(self.revision_oid())

    def revision(self):
        return self._revision

    def revision_oid(self):
        if self.revision() is None:
            return None

        return self.oid() + "/history/revisions/" + self.revision()

    def entity_name(self):
        return self._entity_name

    def entity_oid(self):
        return self._entity_oid

    def sync_status(self, revision, site_name=None, exchange=False):
        return revision.get_sync_status(site_name, exchange)

    def source_site(self):
        if not self.revision_exists():
            return None

        revision = self.related_revision_object()
        return revision.site.get()

    def status(self, site_name=None):
        if not self.revision_exists():
            return 'NotAvailable'

        revision = self.related_revision_object()

        if self.sync_status(revision, site_name=site_name) == 'Available':
            return 'Available'
        elif self.sync_status(revision, site_name=site_name) == 'Requested':
            return 'Requested'
        elif self.sync_status(revision, exchange=True) == 'Available':
            return 'Downloadable'
        else:
            return 'Requestable'

    def is_real(self):
        return self._is_real

    def path(self):
        return self._path


class File(FileSystemItem):

    @classmethod
    def create_from_path(cls, path, project):
        path = path.replace('\\', '/')
        entity_name, entity_oid, dept, name, rev = cls._args_from_path(path, project)

        file = cls(entity_name, entity_oid, dept, name, rev, project)
        file._is_real = True
        file._path = path

        return file

    @classmethod
    def _get_name(cls, flow_name):
        extension_index = flow_name.rfind('_')
        return flow_name[:extension_index] + '.' + flow_name[extension_index+1:]


class Folder(FileSystemItem):

    @classmethod
    def create_from_path(cls, path, project):
        path = path.replace('\\', '/')
        entity_name, entity_oid, dept, name, rev = cls._args_from_path(path, project)
        name = name.split('_')[-1]

        folder = cls(entity_name, entity_oid, dept, name, rev, project)
        folder._is_real = True
        folder._path = path

        return folder

    @classmethod
    def _get_name(cls, flow_name):
        return flow_name


def get_real_files(paths, flow_project):
    folders = defaultdict(list)
    real_files = []

    for path in paths:
        path = os.path.normpath(path)
        folders[os.path.dirname(path)].append(os.path.basename(path))

    for folder, files in folders.items():
        files = list(set(files))
        
        if len(files) > 1:
            item = Folder.create_from_path(folder, flow_project)
        else:
            item = File.create_from_path(folder, flow_project)
            
            if not item.exists():
                item = Folder.create_from_path(folder, flow_project)
            
        real_files.append(item)

    return real_files


def resolve_files(predictive_files, real_files=None, site_name=None):
    resolved_files = []

    if real_files is None:
        for f in predictive_files:
            resolved_files.append({
                'entity_name': f.entity_name(),
                'entity_oid': f.entity_oid(),
                'file_name': f.name(),
                'revision': f.revision(),
                'file_oid': f.oid(),
                'revision_oid': f.revision_oid(),
                'status': f.status(site_name=site_name),
                'in_breakdown': True,
                'source_site': f.source_site(),
                'last_revision': f.last_revision(),
                'is_alien': False,
                'is_real': False,
                'path': f.path(),
            })

        return resolved_files

    # Sort predictive and real files according to the file oid
    files = defaultdict(lambda: defaultdict(list))

    for pred_file in predictive_files:
        files[pred_file.oid()]['pred'].append(pred_file)

    for real_file in real_files:
        files[real_file.oid()]['real'].append(real_file)

    # Resolve predictive and real files
    for file_oid in files:
        pred_and_real = files[file_oid]
        pred_files = pred_and_real['pred'] # Only one predictive file here
        result_files = pred_and_real['real']
        in_breakdown = bool(pred_files)

        if not result_files:
            result_files = pred_files

        for f in result_files:
            resolved_files.append({
                'entity_name': f.entity_name(),
                'entity_oid': f.entity_oid(),
                'file_name': f.name(),
                'revision': f.revision(),
                'file_oid': file_oid,
                'revision_oid': f.revision_oid(),
                'status': f.status(site_name=site_name),
                'in_breakdown': in_breakdown,
                'source_site': f.source_site(),
                'last_revision': f.last_revision(),
                'is_alien': not in_breakdown and not f.exists(),
                'is_real': f.is_real(),
                'path': f.path(),
            })

    return resolved_files


def get_dependencies(leaf, site_name=None, predictive=False, real=False, revision_name=None):
    project = leaf.root().project()

    predictive_files = []
    real_files = None

    # Get object's real dependencies
    if real:
        try:
            dependency_getter = getattr(leaf, 'get_real_dependencies')
        except AttributeError:
            pass
        else:
            real_file_paths = dependency_getter(revision_name)
            real_files = get_real_files(real_file_paths, project)

    # Get object's dependency template
    if predictive:
        templates = project.admin.dependency_templates
        template_name = leaf.name()
        kitsu_casting = list()

        # Check if template name is explicitly provided
        try:
            template_getter = getattr(leaf, 'get_dependency_template')
        except AttributeError:
            pass
        else:
            template_name, entity_oid, kitsu_casting = template_getter()

        if not template_name or not templates.has_mapped_name(template_name):
            leaf.root().session().log_warning(
                f"No template named {template_name} in project dependency template"
            )
            return []

        template = templates[template_name]
        defaults = template.get_default_dependency_names()
        kitsu_bindings = project.kitsu_bindings()

        predictive_files = []

        for asset_name in kitsu_casting:
            asset_oid = kitsu_bindings.get_asset_oid(asset_name)
            asset_files = template.get_asset_files(asset_name)

            for name, data in asset_files.items():
                file_type = File if '.' in name else Folder
                pred_file = file_type(asset_name, asset_oid, data['department'], name, data['revision'], project)
                predictive_files.append(pred_file)

        for default in defaults:
            files = template.get_dependency_files(default)

            for name, data in files.items():
                file_type = File if '.' in name else Folder
                pred_file = file_type(default, entity_oid, data['department'], name, data['revision'], project)
                predictive_files.append(pred_file)

    return resolve_files(predictive_files, real_files, site_name)


class DependencyItem(flow.Object):

    ICON = ('icons.flow', 'expanded')

    _dependency_view = flow.Parent()
    dependency_name = flow.Computed(store_value=False)
    entity_name = flow.Computed(store_value=False)
    file_name = flow.Computed(store_value=False)
    revision = flow.Computed(store_value=False)
    revision_oid = flow.Computed(store_value=False)
    status = flow.Computed(store_value=False)
    source_site = flow.Computed(store_value=False)
    comment = flow.Computed(store_value=False)
    path = flow.Computed(store_value=False)
    in_breakdown = flow.Computed(store_value=False)
    is_alien = flow.Computed(store_value=False)

    def compute_child_value(self, child_value):
        if child_value is self.dependency_name:
            self.dependency_name.set(self.name())
        else:
            child_value.set('')

    def color(self):
        return '#444'


class DependencyItemFile(DependencyItem):

    ICON = ('icons.libreflow', 'blank')

    _parent = flow.Parent(3)

    def _get_comment(self, data):
        is_real = data['is_real']
        in_breakdown = data['in_breakdown']
        source_site = data['source_site']
        last_revision = data['last_revision']
        status = self.status.get()
        comment = ""
        
        parent_name = self._parent.name()
        if self.root().session().cmds.Flow.exists(self._parent.oid() + '/display_name'):
            parent_name = self._parent.display_name.get()

        if not self.is_alien.get():
            if not in_breakdown:
                comment = "Not in breakdown"
            elif not is_real:
                comment = "In breakdown but not used in " + parent_name
            elif status == 'Requested' or status == 'Requestable':
                comment = "From " + source_site
            elif self.revision.get() != last_revision:
                comment = "Update available (%s)" % last_revision
        else:
            comment = "In " + parent_name + " but out of pipeline"

        return comment

    def request(self, requesting_site_name=None):
        revision_oid = self.revision_oid.get()
        revision = self.root().get_object(revision_oid)

        if requesting_site_name is None:
            requesting_site_name = self.root().project().get_current_site().name()
        
        request_action = revision.request_as
        request_action.sites.target_site.set(requesting_site_name)
        request_action.sites.source_site.set(self.source_site.get())
        request_action.run(None)

    def compute_child_value(self, child_value):
        data = self._dependency_view.get_dependency_data(self.name())

        if child_value is self.dependency_name:
            self.dependency_name.set(self.file_name.get())
        elif child_value is self.entity_name:
            self.entity_name.set(data['entity_name'])
        elif child_value is self.file_name:
            if self.is_alien.get():
                self.file_name.set(data['path'])
            else:
                self.file_name.set(data['file_name'])
        elif child_value is self.revision:
            self.revision.set(data['revision'] or '-')
        elif child_value is self.revision_oid:
            self.revision_oid.set(data['revision_oid'])
        elif child_value is self.status:
            self.status.set(data['status'])
        elif child_value is self.source_site:
            self.source_site.set(data['source_site'])
        elif child_value is self.comment:
            self.comment.set(self._get_comment(data))
        elif child_value is self.path:
            self.path.set(data['path'])
        elif child_value is self.in_breakdown:
            self.in_breakdown.set(data['in_breakdown'])
        elif child_value is self.is_alien:
            self.is_alien.set(data['is_alien'])

    def color(self):
        return 'default'


class DependencyView(flow.DynamicMap):

    _action = flow.Parent()
    _parent = flow.Parent(2)
    _refresh_time = flow.SessionParam(60).ui(editor='int')
    
    _STATUS_ICONS = {
        'Available': ('icons.libreflow', 'available'),
        'Downloadable': ('icons.libreflow', 'downloadable'),
        'Requestable': ('icons.libreflow', 'requestable'),
        'Requested': ('icons.libreflow', 'waiting'),
        'NotAvailable': ('icons.libreflow', 'unavailable'),
    }

    def __init__(self, parent, name):
        super(DependencyView, self).__init__(parent, name)
        self._deps_time = time.time()
        self._deps_data = None

    @classmethod
    def mapped_type(cls):
        return DependencyItem
    
    def get_site_name(self):
        return self._action.requesting_site.get()
    
    def get_revision_name(self):
        return self._action.revision.get()

    def mapped_names(self, page_num=0, page_size=None):
        self._ensure_dependencies_data()
        mapped_names = []
        
        for entity_name, deps_names in self._entity_deps.items():
            mapped_names.append(entity_name)
            
            for dep_name in deps_names:
                mapped_names.append(dep_name)

        return mapped_names

    def _get_mapped_item_type(self, mapped_name):
        if re.match(r'.*_\d\d\d$', mapped_name):
            return DependencyItemFile
        else:
            return self.mapped_type()

    def columns(self):
        return ['Dependency', 'Revision', 'Comment']

    def get_dependency_data(self, name):
        self._ensure_dependencies_data()
        return self._deps_data[name]

    def update_dependencies_data(self):
        include_real = not self._action.predictive_only.get()
        deps = sorted(
            get_dependencies(
                self._parent,
                site_name=self.get_site_name(),
                revision_name=self.get_revision_name(),
                predictive=True,
                real=include_real,
            ),
            key=lambda d: d['is_alien']
        )
        
        files_data = defaultdict(list)
        self._deps_data = dict()
        self._entity_deps = defaultdict(list)
        
        for d in deps:
            files_data[d['entity_name']].append(d)
        
        for entity_name, data in files_data.items():
            for i, file_data in enumerate(data):
                dep_name = entity_name + '_%03i' % i
                self._entity_deps[entity_name].append(dep_name)
                self._deps_data[dep_name] = file_data

    def _ensure_dependencies_data(self):
        if not self._deps_data or time.time() - self._deps_time > self._refresh_time.get():
            self.update_dependencies_data()
            self._deps_time = time.time()

    def _fill_row_cells(self, row, item):
        row['Dependency'] = item.dependency_name.get()
        row['Revision'] = item.revision.get()
        row['Comment'] = item.comment.get()

    def _fill_row_style(self, style, item, row):
        color = item.color()
        if color != 'default':
            for col in self.columns():
                style['%s_background-color' % col] = color
        
        style['icon'] = self._STATUS_ICONS.get(item.status.get(), ('icons.flow', 'expanded'))


class WorkingSiteName(flow.values.ChoiceValue):
    
    STRICT_CHOICES = False
    
    def choices(self):
        return self.root().project().get_working_sites().mapped_names()
    
    def revert_to_default(self):
        self.set(self.root().project().get_current_site().name())


class RevisionName(flow.values.ChoiceValue):
    
    _parent = flow.Parent(2)
    STRICT_CHOICES = False
    
    def choices(self):
        try:
            revisions = self._parent.get_revision_names(published_only=True)
        except AttributeError:
            revisions = []
        
        return revisions
    
    def revert_to_default(self):
        try:
            last_revision = self._parent.get_head_revision().name()
        except AttributeError:
            last_revision = None
        
        self.set(last_revision)


class GetDependenciesAction(flow.Action):

    ICON = ('icons.libreflow', 'dependencies')

    requesting_site = flow.Param(None, WorkingSiteName).watched()
    revision = flow.Param(None, RevisionName).watched()
    dependencies = flow.Child(DependencyView).ui(expanded=True)
    predictive_only = flow.SessionParam(False).watched().ui(editor='bool')

    def child_value_changed(self, child_value):
        if child_value is self.predictive_only:
            self.dependencies.update_dependencies_data()
            self.dependencies.touch()
        elif child_value in [self.requesting_site, self.revision]:
            self.update_dependencies()
            
    def update_dependencies(self):
        self.dependencies.update_dependencies_data()
        self.dependencies.touch()

    def get_buttons(self):
        self.message.set("<h2>Get dependencies</h2>")
        self.requesting_site.revert_to_default()
        self.revision.revert_to_default()
        
        return ['Proceed', 'Cancel']

    def run(self, button):
        if button == 'Cancel':
            return
        
        for d in self.dependencies.mapped_items():
            if type(d) is DependencyItemFile:
                if d.status.get() in ['Requestable', 'Downloadable']:
                    d.request(self.requesting_site.get())

        self.update_dependencies()
        
        return self.get_result(close=False)


class DependencyStatus(flow.values.ChoiceValue):

    CHOICES = ['Available', 'Downloadable', 'Requestable', 'Unavailable']
    _COLORS = {
        'Available': '#45cc3d',
        'Downloadable': '#ffa800',
        'Requestable': '#aaa',
        'Unavailable': '#cc3b3c'
    }

    @classmethod
    def get_color(cls, status):
        return cls._COLORS[status]


class DependencyFile(flow.Object):

    _dependency = flow.Parent(3)
    department = flow.Computed(store_value=False)
    file_format = flow.Computed(store_value=False)
    revision = flow.Computed(store_value=False)
    status = flow.Computed(store_value=False)

    def get_name(self):
        dependency_files = self._dependency.get_dependency_files()
        name = '.'.join(self.name().rsplit('_', 1))

        if not name in dependency_files:
            name = self.name()

        return name

    def _get_root_oid(self):
        return self._dependency.dependency_oid.get() + '/departments/' + self.department.get() + '/files'

    def get_oid(self):
        return self._get_root_oid() + '/' + self.name()

    def get_file_data(self):
        dependency_files = self._dependency.get_dependency_files()
        return dependency_files[self.get_name()]

    def exists(self):
        return self.root().session().cmds.Flow.exists(self.get_oid())

    def _get_status(self):
        status = 'Unavailable'

        if self.exists():
            revision = self._get_revision()

            if revision:
                if revision.get_sync_status() == 'Available':
                    status = 'Available'
                elif revision.get_sync_status(exchange=True) == 'Available':
                    status = 'Downloadable'
                else:
                    status = 'Requestable'

        return status


    def _get_revision(self):
        revision = None

        if not self.exists():
            return revision

        revision_name = self.revision.get()
        tracked_file = self.root().get_object(self.get_oid())

        if revision_name == 'last':
            revision = tracked_file.get_head_revision()
        elif tracked_file.has_revision(revision_name):
            revision = tracked_file.get_revision(revision_name)

        return revision

    def compute_child_value(self, child_value):
        file_data = self.get_file_data()

        if child_value is self.department:
            self.department.set(file_data['department'])
        elif child_value is self.file_format:
            default_format = self.get_name().split('.')[-1]
            self.file_format.set(file_data.get('format', default_format))
        elif child_value is self.revision:
            self.revision.set(file_data['revision'])
        elif child_value is self.status:
            self.status.set(self._get_status())


class DependencyFileMap(flow.DynamicMap):

    _dependency = flow.Parent(2)

    @classmethod
    def mapped_type(cls):
        return DependencyFile

    def mapped_names(self, page_num=0, page_size=None):
        dependency_files = self._dependency.get_dependency_files()
        names = [name.replace('.', '_') for name in dependency_files]
        return names

    def _fill_row_cells(self, row, item):
        row['Name'] = item.get_name()

    def _fill_row_style(self, style, item, row):
        color = DependencyStatus.get_color(item.status.get())
        style['foreground-color'] = color


class ShowDependencyFiles(flow.Action):

    _dependency = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        return self.get_result(
            goto=self._dependency.files.oid()
        )


class DependencyFiles(flow.Object):

    file_map = flow.Child(DependencyFileMap).ui(
        label='Files',
        expanded=True
    )


class Dependency(flow.Object):

    _parent = flow.Parent()

    files = flow.Child(DependencyFiles)
    dependency_oid = flow.Computed(store_value=False)
    nb_occurrences = flow.Computed(store_value=False).ui(editor='int')
    available = flow.Computed(store_value=False).ui(editor='bool')

    show_files = flow.Child(ShowDependencyFiles)

    def get_dependency_data(self):
        return self._parent.get_asset_data(self.name())

    def get_dependency_files(self):
        dependency_data = self.get_dependency_data()
        return dependency_data['files']

    def get_files(self):
        return self.files.file_map.mapped_items()

    def get_file_count(self, status):
        file_statuses = [f.status.get() for f in self.get_files()]
        return file_statuses.count(status)

    def compute_child_value(self, child_value):
        dependency_data = self.get_dependency_data()

        if child_value is self.dependency_oid:
            self.dependency_oid.set(dependency_data['dependency_oid'])
        elif child_value is self.nb_occurrences:
            self.nb_occurrences.set(dependency_data['nb_occurrences'])
        elif child_value is self.available:
            available = (self.get_file_count('Available') == len(self.get_files()))
            self.available.set(available)


class Dependencies(flow.DynamicMap):

    _shot = flow.Parent()
    _sequence = flow.Parent(3)
    _updated = flow.BoolParam(False)
    _refresh_time = flow.SessionParam(30).ui(editor='int')

    def __init__(self, parent, name):
        super(Dependencies, self).__init__(parent, name)
        self._assets_data_time = time.time()
        self._assets_data = None

    def mapped_names(self, page_num=0, page_size=None):
        self._ensure_assets_data()
        return list(self._assets_data.keys())

    def _ensure_assets_data(self):
        if not self._assets_data or time.time() - self._assets_data_time > self._refresh_time.get():
            self._assets_data = self._get_dependencies_data()
            self._assets_data_time = time.time()

    def _get_dependencies_data(self):
        kitsu_api = self.root().project().kitsu_api()
        kitsu_casting = kitsu_api.get_shot_casting(self._shot.name(), self._sequence.name())
        kitsu_bindings = self.root().project().admin.kitsu.bindings
        assets_data = dict()

        dependency_template = self.root().project().admin.dependency_templates['shot']
        dependencies = dependency_template.get_dependencies()
        defaults = dependency_template.get_default_dependency_names()

        # Kitsu dependencies
        for asset in kitsu_casting:
            asset_name = asset['asset_name']
            asset_type = asset['asset_type_name']
            asset_oid = kitsu_bindings.get_asset_oid(asset_name)

            files = dependencies['kitsu.'+asset_type]

            assets_data[asset_name] = dict(
                dependency_oid=asset_oid,
                files=files,
                nb_occurrences=asset['nb_occurences'],
            )

        # Default dependencies
        for default in defaults:
            files = dependencies[default]

            assets_data[default] = dict(
                dependency_oid=self._shot.oid(),
                files=files,
                nb_occurrences=1,
            )

        return assets_data

    def get_asset_data(self, asset_name):
        self._ensure_assets_data()
        return self._assets_data[asset_name]

    @classmethod
    def mapped_type(cls):
        return Dependency

    def columns(self):
        return ['Name', 'Occurrences'] + DependencyStatus.CHOICES

    def _fill_row_cells(self, row, item):
        row['Name'] = item.name()
        row['Occurrences'] = item.nb_occurrences.get()

        for status in DependencyStatus.CHOICES:
            file_count = item.get_file_count(status)
            if file_count:
                row[status] = str(file_count)
            else:
                row[status] = ""

    def _fill_row_style(self, style, item, row):
        if item.available.get():
            style['foreground-color'] = '#45cc3d'
        else:
            style['foreground-color'] = '#cc3b3c'

        for status in DependencyStatus.CHOICES:
            color = DependencyStatus.get_color(status)
            style['%s_foreground-color' % status] = color
