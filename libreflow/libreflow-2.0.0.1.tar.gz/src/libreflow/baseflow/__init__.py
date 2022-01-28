import os
import json
import gazu
import getpass
import pathlib
import fnmatch
import re

from kabaret import flow
from kabaret.app.ui.gui.widgets.flow.flow_view import (
    CustomPageWidget,
    QtWidgets,
    QtCore,
)
from kabaret.app.ui.gui.widgets.editors import editor_factory
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict
from kabaret.subprocess_manager.runners import Explorer
from kabaret.flow_entities.store import EntityStore

from .users import Users, UserEnvironment, UserBookmarks, UserProfile
from .film import Sequences
from .lib import Assets
from .runners import (
    Krita,
    Blender,
    AfterEffects,
    AfterEffectsRender,
    VSCodium,
    NotepadPP,
    MarkSequenceRunner,
    Firefox,
    SessionWorker,
    DefaultEditor,
    ImageMagick,
    RV,
    DefaultRunners,
)
from .site import (
    Synchronize, GotoCurrentSiteQueue, ShowSiteSyncErrors,
    WorkingSites, ExchangeSites,
    MinioFileUploader, MinioFileDownloader,
    RequestRevisions, MultiRequestRevisions,
)
from .file import TrackedFile, Revision, FileManager
from .kitsu import KitsuAPIWrapper, KitsuBindings
from .dependency import DependencyTemplates


class LoginPageWidget(CustomPageWidget):
    def build(self):
        # Get project root oid
        self.project_oid = self.session.cmds.Flow.split_oid(self.oid)[0][1]

        # Build UI
        self.label = QtWidgets.QLabel(self)
        self.label.setText("<h2>Connexion page</h2>")
        self.error_label = QtWidgets.QLabel(self)
        self.error_label.setText("")

        self.lineedit_kitsu_login = QtWidgets.QLineEdit()
        self.lineedit_kitsu_password = QtWidgets.QLineEdit()
        self.button_login = QtWidgets.QPushButton("Log in")
        self.button_login.setMinimumWidth(100)

        # Set kitsu_password field input mode
        self.lineedit_kitsu_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineedit_kitsu_password.setInputMethodHints(
            QtCore.Qt.ImhHiddenText
            | QtCore.Qt.ImhNoPredictiveText
            | QtCore.Qt.ImhNoAutoUppercase
        )

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(self.label, 0, 0)
        grid_layout.addWidget(self.lineedit_kitsu_login, 1, 0, 1, 2)
        grid_layout.addWidget(self.lineedit_kitsu_password, 2, 0, 1, 2)
        grid_layout.addWidget(self.error_label, 3, 0)
        grid_layout.addWidget(self.button_login, 3, 1)
        grid_layout.setColumnStretch(0, 1)

        self.setLayout(grid_layout)

        self.button_login.clicked.connect(self.on_connection_validated)
        self.lineedit_kitsu_login.returnPressed.connect(self.on_connection_validated)
        self.lineedit_kitsu_password.returnPressed.connect(self.on_connection_validated)

    def on_connection_validated(self):
        kitsu_login = self.lineedit_kitsu_login.text()
        kitsu_password = self.lineedit_kitsu_password.text()
        logged_in = self.session.cmds.Flow.call(
            self.project_oid,
            "log_in",
            args={},
            kwargs={"kitsu_login": kitsu_login, "kitsu_password": kitsu_password},
        )

        if logged_in:
            if logged_in == 1:
                text = "<font color=#C71B1F>Login failed... Check credentials !</font>"
            elif logged_in == 2:
                support = self.session.cmds.Flow.get_value(self.project_oid + "/admin/project_settings/support")
                text = "<font color=#D66700>A user with the same name but a different Kitsu ID is already registered for this project."
                if support:
                    text += f"<br>We invite you to contact the support of the project ({support}).</font>"
                else:
                    text += "</font>"
            
            self.error_label.setText(text)
            return

        self.error_label.setText("")
        self.page.refresh()


class LoginPage(flow.Object):

    kitsu_server_url = flow.Param("")



class SynchronizeFilesResult(flow.Action):

    def allow_context(self, context):
        return False

    def get_buttons(self):
        return ["Close"]
    
    def run(self, button):
        return


class SynchronizeFiles(Synchronize):
    
    ICON = ('icons.libreflow', 'sync')

    result = flow.Child(SynchronizeFilesResult)

    def needs_dialog(self):
        return True
    
    def get_buttons(self):
        exchange_site = self.root().project().get_exchange_site()
        
        if not exchange_site.configured.get():
            self.message.set((
                "<h3><font color=#D5000D>"
                "Exchange site not configured"
                "</font></h3>"
                "Please configure the exchange site of this project."
            ))
            return ['Configure exchange site', 'Cancel']
        
        self.message.set((
            "<h3><font color=#D66700>"
            "Synchronizing all requested files may freeze your session for a while."
            "</font></h3>"
        ))
        return ["Confirm", "Cancel"]

    def allow_context(self, context):
        return context and context.endswith(".details")
    
    def run(self, button):
        if button == "Cancel":
            return
        elif button == 'Configure exchange site':
            exchange_site = self.root().project().get_exchange_site()
            return self.get_result(next_action=exchange_site.configuration.oid())

        # Save initial job counts
        init_job_count = self._compute_job_count()

        # Process jobs
        super(SynchronizeFiles, self).run(button)

        # Print final counts
        nb_waiting_init = init_job_count['WAITING']
        nb_processed = self._job_count['PROCESSED'] - init_job_count['PROCESSED']
        nb_error_init = init_job_count['ERROR']
        nb_error = self._job_count['ERROR'] - nb_error_init

        if nb_processed == nb_waiting_init and nb_error == 0:
            msg = (
                "<h3><font color=#029600>"
                "Synchronization successful !"
                "</font></h3>"
            )
        else:
            msg = ''
            
            if nb_processed < nb_waiting_init:
                msg += (
                    '<h3><font color=#D66700>'
                    f'Synchronized files: {nb_processed}/{nb_waiting_init}'
                    '</font></h3>'
                )
            if nb_error > 0:
                msg += (
                    '<h3><font color=#D5000D>'
                    f'Errors: {nb_error}/{nb_waiting_init}'
                    '</font></h3>'
                )
        
        if nb_error_init > 0:
            msg += (
                '<h3><font color=#D5000D>'
                f'Other waiting errors: {nb_error_init}'
                '</font></h3>'
            )
            
        self.result.message.set(msg)
        
        return self.get_result(next_action=self.result.oid())


class GotoBookmarks(flow.Action):
    ICON = ("icons.gui", "star")

    def needs_dialog(self):
        return False
    
    def run(self, button):
        return self.get_result(
            goto=self.root().project().admin.bookmarks.oid()
        )


class WorkingSiteChoiceValue(flow.values.ChoiceValue):

    _parent = flow.Parent()

    def choices(self):
        return self.root().project().get_working_sites().mapped_names()


class CleanZipFiles(flow.Action):

    ICON = ('icons.libreflow', 'clean')

    def __init__(self, parent, name):
        super(CleanZipFiles, self).__init__(parent, name)
        self._paths = []

    def get_buttons(self):
        self.message.set('<h2>Remove ZIP files</h2>')
        return ['Confirm', 'Search', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        elif button == 'Search':
            root_project = self.root().project().get_root().replace('\\', '/')
            self._paths = []
            file_count = 0
            file_size = 0
            
            root_lib = os.path.join(root_project, 'lib').replace('\\', '/')
            root_film = os.path.join(root_project, 'siren').replace('\\', '/')
            
            for root_path in (root_lib, root_film):
                for root, _, files in os.walk(root_path):
                    norm_root = root.replace('\\', '/').replace(root_project, '')
                    
                    for f in files:
                        match = re.search('lib/(chars|props|sets)/.*/.*/.*/.*/v\d\d\d', norm_root)
                        match = match or re.search('/siren/sq\d\d/sc\d\d\d\d/.*/.*/v\d\d\d', norm_root)
                        
                        if match is not None and os.path.splitext(f)[1] == '.zip':
                            path = os.path.join(root, f)
                            file_count += 1
                            file_size += os.path.getsize(path)
                            self._paths.append(path)
            
            self.message.set((
                '<h2>Remove ZIP files</h2>'
                '<b>%i</b> ZIP files found in this project (~%03f Gb).'
                '<h3><font color="#D5000D">Remove all ?</font></h3>' % (file_count, file_size * 0.000000001)
            ))

            return self.get_result(close=False)
        else:
            for p in self._paths:
                try:
                    self.root().session().log_warning('Remove file %s' % p)
                    os.remove(p)
                except Exception:
                    self.root().session().log_warning('Failed to remove file %s' % p)


class Synchronization(flow.Object):

    ICON = ("icons.libreflow", "sync")
    
    _project = flow.Parent()
    synchronize_files = flow.Child(SynchronizeFiles)
    show_jobs = flow.Child(GotoCurrentSiteQueue)
    show_errors = flow.Child(ShowSiteSyncErrors)
    request_revisions = flow.Child(RequestRevisions)
    multi_request_revisions = flow.Child(MultiRequestRevisions)

    def __init__(self, parent, name):
        super(Synchronization, self).__init__(parent, name)
        self._initialized = False
    
    def _ensure_waiting_count(self):
        jobs = self._project.get_current_site().queue.job_list

        if not self._initialized:
            jobs.update_waiting_count()
            self._initialized = True
        
        return jobs.count_waiting.get()

    def summary(self):
        nb_waiting_jobs = self.root().project().get_current_site().count_jobs(
            status='WAITING'
        )
        
        if nb_waiting_jobs > 0:
            return (
                "<font color=#D5000D><b>"
                f"{nb_waiting_jobs} job(s) waiting"
                "</b></font>"
            )


class LogOut(flow.Action):

    ICON = ("icons.libreflow", "log_out")

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return context and context.endswith(".details")
    
    def run(self, button):
        project = self.root().project()
        kitsu_config = "%s/kitsu_config.json" % project.user_settings_folder()

        if os.path.exists(kitsu_config):
            os.remove(kitsu_config)

        project.log_out()
        
        return self.get_result(
            goto=project.oid(),
            refresh=True
        )


class KitsuConfig(flow.Object):

    ICON = ('icons.libreflow', 'kitsu')

    server_url = flow.Param().watched()
    project_name = flow.Param().watched()
    project_id = flow.Computed(
        cached=True
    )
    uploadable_files = flow.Param("")
    bindings = flow.Child(KitsuBindings)
    gazu_api = flow.Child(KitsuAPIWrapper).ui(
        hidden=True
    )
    configured = flow.Computed().ui(
        editor='bool',
        hidden=True
    )

    def child_value_changed(self, child_value):
        self.project_id.touch()

    def compute_child_value(self, child_value):
        if child_value is self.project_id:
            self.project_id.set(
                self.gazu_api.get_project_id()
            )
        elif child_value is self.configured:
            self.configured.set(
                self.project_id.get() is not None
            )
    
    def is_uploadable(self, file_name):
        patterns = self.uploadable_files.get().split(',')

        for pattern in patterns:
            pattern = pattern.replace(' ', '')
            if not fnmatch.fnmatch(file_name, pattern):
                return False
    
    def summary(self):
        if not self.configured.get():
            return (
                '<font color=#D5000D>'
                '<b>Server URL</b> and <b>project name</b> '
                'unset: Kitsu features won\'t be available'
            )


class DefaultFiles(flow.Object):

    file_names = flow.Param('')


class DefaultFilesMap(flow.Map):

    @classmethod
    def mapped_type(cls):
        return DefaultFiles


class ProjectSettings(flow.Object):

    ICON = ('icons.gui', 'settings')

    project_nice_name = flow.Param()
    project_thumbnail = flow.Param().ui(editor='textarea')
    support = flow.Param("")

    settings = flow.Child(ContextualView)
    default_files = flow.Child(DefaultFilesMap)
    non_editable_files = flow.Param("")
    auto_upload = flow.Param('').ui(
        tooltip='Enable <b>upload after publish</b> by default for all files matching the provided patterns')
    hide_upload_after_publish = flow.Param('')
    clean_zip_files = flow.Child(CleanZipFiles).ui(label='Clean ZIP files')

    def get_auto_upload_files(self):
        return self.auto_upload.get().replace(' ', '').split(',')
    
    def get_hidden_upload_files(self):
        return self.hide_upload_after_publish.get().replace(' ', '').split(',')


class ExchangeSiteChoiceValue(flow.values.ChoiceValue):

    def choices(self):
        return self.root().project().get_exchange_sites().mapped_names()


class MultisiteConfig(flow.Object):

    ICON = ('icons.gui', 'sitemap')

    current_site_name = flow.Computed(cached=True)
    root_dir = flow.Computed(cached=True)
    temp_dir = flow.Computed(cached=True)
    exchange_site_name = flow.Param("default_exchange", ExchangeSiteChoiceValue).watched().ui(
        editable=False
    )
    working_sites = flow.Child(WorkingSites).ui(label="Working sites")
    exchange_sites = flow.Child(ExchangeSites).ui(label="Exchange sites")
    sites_data = flow.Computed(cached=True).ui(hidden=True)

    def child_value_changed(self, child_value):
        if child_value is self.exchange_site_name:
            self.touch()

    def compute_child_value(self, child_value):
        if child_value is self.root_dir:
            '''
            TODO : Override by site on multisite !
            '''
            root_dir = None
            if "ROOT_DIR" in os.environ:
                print("WARNING: ROOT_DIR was defined by the environement !")
                root_dir = os.environ["ROOT_DIR"]
            else:
                # Otherwise, get current site's root dir
                root_dir = self.working_sites[self.current_site_name.get()].root_folder.get()
            
            child_value.set(root_dir)
        elif child_value is self.temp_dir:
            path = self.root_dir.get()

            if path is not None:
                path = os.path.join(path, '.tmp')

                if not os.path.exists(path):
                    os.makedirs(path)
            
            self.temp_dir.set(path)
        elif child_value is self.current_site_name:
            if "KABARET_SITE_NAME" in os.environ:
                site_name = os.environ["KABARET_SITE_NAME"]
            else:
                site_name = os.environ["KABARET_CLUSTER_NAME"]

            if not self.working_sites.has_mapped_name(site_name):
                self.root().session().log_warning((
                    f"Site {site_name} not found in project working sites. "
                    "Falling back to default."
                ))
                site_name = "default"

            child_value.set(site_name)
        elif child_value is self.sites_data:
            self.sites_data.set(self._compute_sites_data())
    
    def _compute_sites_data(self):
        data = {}

        for s in self.root().project().get_working_sites().mapped_items():
            data[s.name()] = {
                'is_default': True,
                'is_active': s.is_active.get(),
                'short_name': s.short_name.get()
            }
        for s in self.root().project().get_exchange_sites().mapped_items():
            data[s.name()] = {
                'is_default': True,
                'is_active': s.is_active.get(),
                'short_name': s.short_name.get()
            }
        
        return data

    def summary(self):
        current_site = self.working_sites[self.current_site_name.get()]
        exchange_site = self.exchange_sites[self.exchange_site_name.get()]

        if not current_site.configured.get():
            return (
                '<font color=#D5000D>'
                f'Current site <b>{current_site.name()}</b> '
                'needs to be configured</font>'
            )
        
        if not exchange_site.configured.get():
            return (
                '<font color=#D5000D>'
                f'Exchange site <b>{exchange_site.name()}</b> '
                'needs to be configured.</font>'
            )


class Admin(flow.Object):

    ICON = ("icons.gui", "team-admin")

    _project = flow.Parent()

    project_settings = flow.Child(ProjectSettings).injectable()
    users = flow.Child(Users).ui(show_filter=True)
    multisites = flow.Child(MultisiteConfig).ui(label='Sites')
    kitsu = flow.Child(KitsuConfig)

    dependency_templates = flow.Child(DependencyTemplates)
    
    user_environment = flow.Child(UserEnvironment).ui(
        expanded=False,
        label='Session environment')
    default_applications = flow.Child(DefaultRunners).ui(expanded=False).injectable()

    login_page = flow.Child(LoginPage).ui(hidden=True)

    file_manager = flow.Child(FileManager)
    store = flow.Child(EntityStore)


class Project(flow.Object):

    log_out_action = flow.Child(LogOut).ui(label="Log out")

    user = flow.Child(UserProfile)
    asset_lib = flow.Child(Assets).ui(expanded=True)
    sequences = flow.Child(Sequences).ui(expanded=True)
    admin = flow.Child(Admin)
    synchronization = flow.Child(Synchronization).ui(expanded=True)

    _RUNNERS_FACTORY = None

    def get_root(self, alternative=None):
        '''
        alternative can be used if root_dir.get() returns None
        '''
        root_dir = self.admin.multisites.root_dir.get()
        if root_dir is None and alternative != None:
            root_dir = alternative
        return root_dir
    
    def get_temp_folder(self):
        return self.admin.multisites.temp_dir.get()

    def set_user_name(self, username):
        '''
        Sets the name of the current user.
        '''
        project_settings_folder = self.project_settings_folder()

        if not os.path.exists(project_settings_folder):
            os.makedirs(project_settings_folder)

        user_file = os.path.join(project_settings_folder, "current_user.json")

        with open(user_file, "w+") as f:
            user_config = dict(username=username)
            json.dump(user_config, f)
        
        self.user.current_user_id.touch()

    def get_user_name(self):
        '''
        Returns the name of the current user.
        '''
        return self.user.current_user_id.get()

    def get_user(self, name=None):
        '''
        If provided, returns the user of this project with the
        given `name`. Return the project's current user otherwise.

        In any case, None is returned if no user is found.
        '''
        if name is None:
            name = self.get_user_name()
        
        if not self.admin.users.has_mapped_name(name):
            return None
        
        return self.admin.users[name]

    def get_current_site(self):
        """
        Returns the site within which the current
        session is beeing run.
        """
        return self.get_working_site(
            self.admin.multisites.current_site_name.get()
        )
    
    def get_working_site(self, name):
        """
        Returns the working site of the project
        with the given name.
        """
        return self.get_working_sites()[name]
    
    def get_exchange_site(self):
        """
        Returns the first exchange site found in
        project's registered site list.
        """
        return self.get_exchange_sites()[
            self.admin.multisites.exchange_site_name.get()
        ]

    def get_working_sites(self):
        return self.admin.multisites.working_sites

    def get_exchange_sites(self):
        return self.admin.multisites.exchange_sites
    
    def get_site_names(self, short_names=False):
        working_sites = self.get_working_sites()
        exchange_sites = self.get_exchange_sites()

        if short_names:
            return working_sites.short_names() + exchange_sites.short_names()

        return working_sites.mapped_names() + exchange_sites.mapped_names()

    def is_admin(self, username):
        try:
            return self.admin.users.is_admin(username)
        except flow.exceptions.MappedNameError:
            # Unregistered user not admin by default
            return False

    def show_login_page(self):
        kitsu_api = self.kitsu_api()
        valid_host = kitsu_api.host_is_valid()

        if not valid_host:
            logged_in = False
        else:
            logged_in = kitsu_api.current_user_logged_in()

        if not logged_in:
            try:
                f = open("%s/kitsu_config.json" % self.user_settings_folder(), "r")
            except IOError:
                logged_in = False
            else:
                kitsu_config = json.load(f)
                kitsu_api.set_host(kitsu_config["kitsu_host"])
                kitsu_api.set_tokens(kitsu_config["tokens"])

                logged_in = kitsu_api.current_user_logged_in()

        return not kitsu_api.host_is_valid() or not logged_in

    def update_kitsu_host(self, server_url):
        kitsu_api = self.kitsu_api()
        kitsu_api.set_server_url(server_url)
        kitsu_api.set_host(server_url + "/api")

        return kitsu_api.host_is_valid()

    def log_in(self, kitsu_login, kitsu_password):
        kitsu_api = self.kitsu_api()

        self.update_kitsu_host(self.admin.kitsu.server_url.get())
        kitsu_user_data = kitsu_api.log_in(kitsu_login, kitsu_password)

        if kitsu_user_data is None:
            return 1
        
        kitsu_id = kitsu_user_data['user']['id']

        # Set current user
        # user_name = self.admin.users.get_user_name(kitsu_login)
        user = self.admin.users.get_user_by_uid(kitsu_id)

        if user is None:
            # Create user profile if not registered
            user = self.admin.users.add_user(kitsu_id, kitsu_login)

            if user is None:
                return 2

            # user_name = user.name()
        
        self.set_user_name(user.name())

        # Create user folder at first login
        user_settings_folder = self.user_settings_folder()
        if not os.path.exists(user_settings_folder):
            os.makedirs(user_settings_folder)

        # Save authentification tokens
        tokens = kitsu_api.get_tokens()
        kitsu_config = {}
        kitsu_config["tokens"] = tokens
        kitsu_config["kitsu_host"] = kitsu_api.get_host()

        if user_settings_folder is not None:
            with open("%s/kitsu_config.json" % user_settings_folder, "w+") as f:
                json.dump(kitsu_config, f)

        return 0
    
    def log_out(self):
        self.kitsu_api().log_out()
    
    def kitsu_id(self):
        return self.admin.kitsu.project_id.get()

    def kitsu_name(self):
        return self.admin.kitsu.project_name.get()
    
    def kitsu_config(self):
        return self.admin.kitsu
    
    def kitsu_api(self):
        return self.admin.kitsu.gazu_api

    def kitsu_bindings(self):
        return self.admin.kitsu.bindings


    def get_contextual_view(self, context_name):
        if context_name == "settings":
            return self.admin.project_settings.settings

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(
                PROJECT=self.name(),
                default_shot_layout_files="{sequence}_{shot}_layout.blend, {sequence}_{shot}_layout-movie.mov",
                default_shot_animation_files="{sequence}_{shot}_animation.blend, {sequence}_{shot}_animation-movie.mov, {sequence}_{shot}_animation-export.abc",
                default_asset_model_files="{asset_name}_model.blend, {asset_name}_model-movie.mov, {asset_name}_model-export.abc",
                default_asset_rig_files="{asset_name}_rig.blend, {asset_name}_rig-turnaround.mov",
                project_thumbnail="{ROOT_DIR}TECH/{PROJECT}_thumbnail.png",
            )

    def project_settings_folder(self):
        return os.path.join(
            pathlib.Path.home(),
            ".libreflow",
            self.name()
        )

    def user_settings_folder(self):
        '''
        DEPRECATED ! TO DELETE ? 
        '''
        return os.path.join(
            self.project_settings_folder(),
            self.get_user_name()
        )

    def get_project_thumbnail2(self):
        image = self.admin.project_settings.project_thumbnail.get()
        return image
    def get_project_thumbnail(self):
        contextual_dict = get_contextual_dict(self, "settings")
        contextual_dict["ROOT_DIR"] = self.get_root()
        if "project_thumbnail" not in contextual_dict:
            return None
        path = None

        try:
            path = contextual_dict["project_thumbnail"].format(**contextual_dict)
        except KeyError:
            return None

        if path and os.path.exists(path):
            return path
        else:
            return None

    def update_user_environment(self):
        self.admin.user_environment.update()

    def _register_runners(self):
        self._RUNNERS_FACTORY.ensure_runner_type(Blender)
        self._RUNNERS_FACTORY.ensure_runner_type(Krita)
        self._RUNNERS_FACTORY.ensure_runner_type(AfterEffects)
        self._RUNNERS_FACTORY.ensure_runner_type(AfterEffectsRender)
        self._RUNNERS_FACTORY.ensure_runner_type(VSCodium)
        self._RUNNERS_FACTORY.ensure_runner_type(NotepadPP)
        self._RUNNERS_FACTORY.ensure_runner_type(MarkSequenceRunner)
        self._RUNNERS_FACTORY.ensure_runner_type(Firefox)
        self._RUNNERS_FACTORY.ensure_runner_type(Explorer)
        self._RUNNERS_FACTORY.ensure_runner_type(MinioFileUploader)
        self._RUNNERS_FACTORY.ensure_runner_type(MinioFileDownloader)
        self._RUNNERS_FACTORY.ensure_runner_type(SessionWorker)
        self._RUNNERS_FACTORY.ensure_runner_type(DefaultEditor)
        self._RUNNERS_FACTORY.ensure_runner_type(ImageMagick)
        self._RUNNERS_FACTORY.ensure_runner_type(RV)

    def ensure_runners_loaded(self):
        session = self.root().session()
        subprocess_manager = session.get_actor("SubprocessManager")

        if self._RUNNERS_FACTORY is None:
            self._RUNNERS_FACTORY = subprocess_manager.create_new_factory(
                "Libre Flow Tools"
            )
            self._register_runners()

        subprocess_manager.ensure_factory(self._RUNNERS_FACTORY)

    def get_factory(self):
        self.ensure_runners_loaded()
        return self._RUNNERS_FACTORY

    def get_entity_store(self):
        return self.admin.store
    
    def get_file_manager(self):
        return self.admin.file_manager
    
    def get_sync_manager(self):
        return self.synchronization.synchronize_files
    
    def touch(self):
        super(Project, self).touch()
        self.ensure_runners_loaded()
        self.update_user_environment()

    def _fill_ui(self, ui):
        if self._RUNNERS_FACTORY is None:
            self.ensure_runners_loaded()

        self.touch()

        if self.show_login_page():
            ui["custom_page"] = "libreflow.baseflow.LoginPageWidget"
