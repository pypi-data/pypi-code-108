import os
import sys
import getpass
import time
import datetime
import shutil
import glob
import string
import re
import hashlib
import timeago
import zipfile
import fnmatch
import subprocess
import pathlib
import mimetypes
import traceback
import psutil

import kabaret.app.resources as resources
from kabaret import flow
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict
from kabaret.flow_entities.entities import Entity, EntityCollection, Property

from .maputils import SimpleCreateAction, ClearMapAction
from .site import SyncMap, Request, RequestAs, UploadRevision, DownloadRevision, SiteJobsPoolNames, ActiveSiteChoiceValue
from .runners import LaunchSessionWorker, CHOICES, CHOICES_ICONS
from .kitsu import KitsuTaskStatus
from .dependency import DependencyView

from ..resources.mark_sequence import fields
from ..utils.b3d import wrap_python_expr
from ..utils.kabaret.subprocess_manager.flow import RunAction
from ..utils.kabaret.jobs import jobs_flow
from ..utils.kabaret.flow_entities.entities import CustomEntityCollection, EntityView, GlobalEntityCollection
from ..utils.os import zip_folder, remove_folder_content, hash_folder
from ..utils.flow import keywords_from_format

pyversion = sys.version_info


class CreateWorkingCopyBaseAction(flow.Action):

    _file = flow.Parent()

    def allow_context(self, context):
        return context and self._file.editable()


class RevisionsChoiceValue(flow.values.ChoiceValue):

    STRICT_CHOICES = False

    _file = flow.Parent(2)

    def choices(self):
        return self._file.get_revision_names(sync_status='Available', published_only=True)

    def revert_to_default(self):
        if self._file.is_empty():
            self.set('')
            return

        revision = self._file.get_head_revision(sync_status='Available')
        revision_name = ''
        
        if revision is None:
            choices = self.choices()
            if choices:
                revision_name = choices[0]
        else:
            revision_name = revision.name()
        
        self.set(revision_name)
    
    def _fill_ui(self, ui):
        super(RevisionsChoiceValue, self)._fill_ui(ui)
        ui['hidden'] = self._file.is_empty(on_current_site=True)


class CreateWorkingCopyFromRevision(flow.Action):

    ICON = ('icons.libreflow', 'edit-blank')

    _revision = flow.Parent()

    def get_buttons(self):
        msg = "<h3>Create a working copy</h3>"

        if self._revision._file.has_working_copy(from_current_user=True):
            msg += "<font color=#D66700>WARNING: You already have a working copy to your name. \
                    Choosing to create a new one will overwrite your changes.</font>"
        self.message.set(msg)

        return ["Create", "Cancel"]

    def needs_dialog(self):
        return self._revision._file.has_working_copy(from_current_user=True)

    def allow_context(self, context):
        return (
            context
            and self._revision._file.editable()
            and not self._revision.is_working_copy()
        )

    def run(self, button):
        if button == "Cancel":
            return

        file = self._revision._file
        working_copy = file.create_working_copy(reference_name=self._revision.name())
        file.set_current_user_on_revision(working_copy.name())
        file.touch()
        file.get_revisions().touch()


class MakeCurrentRevisionAction(flow.Action):

    _revision = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        file = self._revision._file
        file.make_current(self._revision)
        file.get_revisions().touch()
        file.touch()


class GenericRunAction(RunAction):

    _file = flow.Parent()

    def runner_name_and_tags(self):
        ext = self._file.format.get()
        default_applications = self.root().project().admin.default_applications
        runner_name = default_applications[ext].runner_name.get()
        
        return runner_name, []
    
    def _check_env_priority(self, var_name):
        sys_env = os.environ
        usr_env = self.root().project().admin.user_environment
        name_site = self.root().project().admin.multisites.current_site_name.get()
        site_env = self.root().project().admin.multisites.working_sites[name_site].site_environment

        if (var_name in sys_env) and (len(sys_env[var_name]) > 0):
            # Highest priority: Already defined, we don't do anything
            pass

        elif (usr_env.has_mapped_name(var_name)) and (len(usr_env[var_name].get()) > 0):
            # Mid priority: We fill the environment
            sys_env[var_name] = usr_env[var_name].get()

        elif (site_env.has_mapped_name(var_name)) and (len(site_env[var_name].value.get()) > 0):
            # Lowest priority
            sys_env[var_name] = site_env[var_name].value.get()
        else:
            return False
        
        return True


    def check_runner_env_priority(self, runner_name, runner_version=None):
        session = self.root().session()

        if runner_version is not None:
            target_var = '%s_%s_EXEC_PATH' % (
                runner_name.upper(),
                runner_version.upper().replace('.', '_')
            )
        
            var_defined = self._check_env_priority(target_var)
        
            if var_defined:
                session.log_info('%s defined: %s' % (target_var, os.environ[target_var]))
                return
            
            session.log_info('%s undefined' % target_var)
        
        target_var = '%s_EXEC_PATH' % runner_name.upper()
        var_defined = self._check_env_priority(target_var)

        if var_defined:
            session.log_info('%s defined: %s' % (target_var, os.environ[target_var]))
        else:
            session.log_info('No executable path defined for %s %s in environment' % (runner_name, runner_version))
    
    def target_file_extension(self):
        return self._file.format.get()

    def extra_env(self):
        env = get_contextual_dict(self, "settings")
        env["USER_NAME"] = self.root().project().get_user_name()
        root_path = self.root().project().get_root()
        
        if root_path:
            env["ROOT_PATH"] = root_path

        return env

    def get_version(self, button):
        session = self.root().session()

        default_applications = self.root().project().admin.default_applications
        app = default_applications[self.target_file_extension()]
        runner_name = app.runner_name.get()

        env = get_contextual_dict(self, 'environment')
        version_var_name = '%s_VERSION' % app.runner_name.get().upper()

        if env and version_var_name in env:
            runner_version = str(env[version_var_name])
            session.log_info('%s selected version: %s (contextual override)' % (runner_name, runner_version))
        else:
            runner_version = app.runner_version.get()
            session.log_info('%s selected version: %s (default applications)' % (
                runner_name,
                runner_version
            ))

            if runner_version == 'default':
                runner_version = None

        return runner_version

    def get_buttons(self):
        ext = self._file.format.get()
        default_applications = self.root().project().admin.default_applications

        if not default_applications[ext].runner_name.get():
            self.message.set(
                "<h3>No default application for .%s file format.</h3>" % ext
            )
            return ["Cancel"]

        return super(GenericRunAction, self).get_buttons()

    def needs_dialog(self):
        ext = self._file.format.get()
        default_applications = self.root().project().admin.default_applications
        has_default_app = default_applications[ext].runner_name.get()

        return not has_default_app
    
    def run(self, button):
        '''
        Sets the environment variable which contains the runner executable path
        before launching the runner.
        '''
        name, tags = self.runner_name_and_tags()
        version = self.get_version(button)

        self.check_runner_env_priority(name, version)
        
        rid = self.root().session().cmds.SubprocessManager.run(
            runner_name=name,
            tags=tags,
            version=version,
            label=self.get_run_label(),
            extra_argv=self.extra_argv(),
            extra_env=self.extra_env(),
        )
        return self.get_result(runner_id=rid)


class OpenRevision(GenericRunAction):
    
    _file = flow.Parent(4)
    _revision = flow.Parent()
    
    def extra_argv(self):
        return [self._revision.get_path()]
    
    def allow_context(self, context):
        return context and self._revision.get_sync_status() == 'Available'
    
    def needs_dialog(self):
        return (
            self._revision.get_sync_status() != 'Available'
            or not self._revision.exists()
        )
    
    def get_buttons(self):
        if self._revision.get_sync_status() != 'Available':
            self.message.set((
                '<h2>Unavailable revision</h2>'
                'This revision is not available on the current site.'
            ))
            return ['Close']
        elif not self._revision.exists():
            self.message.set((
                '<h2>Missing revision</h2>'
                'This revision does not exist on the current site.'
            ))
            return ['Close']
        else:
            return super(OpenRevision, self).get_buttons()
    
    def run(self, button):
        if button == 'Close':
            return
        else:
            return super(OpenRevision, self).run(button)


class ComputeRevisionHash(LaunchSessionWorker):
    _revision = flow.Parent()

    def get_run_label(self):
        return 'Compute revision hash'

    def allow_context(self, context):
        return False

    def launcher_oid(self):
        return self._revision.oid()

    def launcher_exec_func_name(self):
        return "update_hash"


class CheckRevisionHash(flow.Action):
    _revision = flow.Parent()

    def get_buttons(self):
        self.message.revert_to_default()
        return ["Check", "Close"]
    
    def run(self, button):
        if button == "Close":
            return

        if self._revision.hash_is_valid():
            color = "029600"
            msg = "Hash is valid !"
        else:
            color = "D5000D"
            msg = "Invalid hash"

        self.message.set((
            f"<h3><font color=#{color}>"
            f"{msg}</font></h3>"
        ))

        return self.get_result(close=False)


class KeepEditingValue(flow.values.SessionValue):

    _action = flow.Parent()

    def check_default_value(self):
        user = self.root().project().get_user()

        if user.preferences.keep_editing.enabled.get():
            # Check if default value is defined in user preferences
            default = user.preferences.keep_editing.value.get()
            self.set(default)
        else:
            # No default value: do nothing
            pass

from .users import PresetValue, PresetSessionValue, PresetChoiceValue

class UploadAfterPublishValue(PresetValue):

    _action = flow.Parent()

    def check_default_value(self):
        preset = self.get_preset()

        if preset is not None:
            # Higher priority: preset defined in user preferences
            self.set(preset)
        elif self._action._file.to_upload_after_publish():
            # Lower priority: option enabled for this file in the project settings
            self.set(True)
        else:
            # No default value: do nothing
            pass

    def _fill_ui(self, ui):
        settings = self.root().project().admin.project_settings
        f = self._action._file

        for pattern in settings.get_hidden_upload_files():
            if fnmatch.fnmatch(f.display_name.get(), pattern):
                ui['hidden'] = True
                break


class PublishFileAction(LaunchSessionWorker):

    ICON = ("icons.libreflow", "publish")

    _file = flow.Parent()

    comment = flow.SessionParam("", PresetSessionValue)
    keep_editing = flow.SessionParam(True, PresetSessionValue).ui(
        editor='bool',
        tooltip='If disabled, delete your working copy after publication'
    )
    upload_after_publish = flow.Param(False, UploadAfterPublishValue).ui(editor='bool')

    def get_run_label(self):
        return 'Upload and save dependencies'
    
    def check_default_values(self):
        self.comment.apply_preset()
        self.keep_editing.apply_preset()
        self.upload_after_publish.check_default_value()
    
    def update_presets(self):
        self.comment.update_preset()
        self.keep_editing.update_preset()
        self.upload_after_publish.update_preset()

    def get_buttons(self):
        self.check_default_values()
        
        msg = "<h2>Publish</h2>"

        working_copies = self._file.get_working_copies()
        if working_copies:
            user_names = [wc.user.get() for wc in working_copies]
            user_names = ["<b>"+n+"</b>" for n in user_names]
            msg += (
                "<h3><font color=#D66500><br>"
                "This file is currently being edited by one or more users (%s)."
                "</font></h3>"
                % ', '.join(user_names)
            )

        self.message.set(msg)
        
        return ['Publish', 'Cancel']

    def allow_context(self, context):
        return context and self._file.editable() and self._file.has_working_copy(True)
    
    def launcher_oid(self):
        return self.oid()

    def launcher_exec_func_name(self):
        return "_process_revision"
    
    def _target_file(self):
        return self._file
    
    def _revision_to_process(self):
        return self._target_file().get_head_revision()
    
    def _process_revision(self):
        file = self._target_file()
        rev = self._revision_to_process()
        
        if self.upload_after_publish.get():
            self._upload(rev)
        
        if file.format.get() == 'blend':
            self._save_blend_dependencies(rev)
    
    def _upload(self, revision):
        current_site = self.root().project().get_current_site()

        upload_job = current_site.get_queue().submit_job(
            emitter_oid=revision.oid(),
            user=self.root().project().get_user_name(),
            studio=current_site.name(),
            job_type='Upload',
            init_status='WAITING'
        )
        sync_manager = self.root().project().get_sync_manager()
        sync_manager.process(upload_job)
    
    def _save_blend_dependencies(self, revision):
        from blender_asset_tracer import trace, bpathlib
        from pathlib import Path
        import collections

        path = Path(revision.get_path())
        report = collections.defaultdict(list)

        for usage in trace.deps(path):
            filepath = usage.block.bfile.filepath.absolute()
            asset_path = str(usage.asset_path).replace('//', '')
            report[str(filepath)].append(asset_path)
        
        revision.dependencies.set(dict(report))
    
    def publish_file(self, file, comment, keep_editing, upload_after_publish=None):
        file.lock()
        published_revision = file.publish(comment=comment, keep_editing=keep_editing)

        if not keep_editing:
            file.set_current_user_on_revision(published_revision.name())
            file.unlock()

        published_revision.make_current.run(None)
        file.touch()

        if upload_after_publish is not None:
            self.upload_after_publish.set(upload_after_publish)

        super(PublishFileAction, self).run(None)

    def allow_context(self, context):
        return (
            context and (
                self._file.has_working_copy(from_current_user=True)
                and (
                    not self._file.is_locked()
                    or self._file.is_locked(by_current_user=True)
                )
            )
        )

    def run(self, button):
        if button == "Cancel":
            return
        
        self.update_presets()
        
        target_file = self._target_file()
        self.publish_file(
            target_file,
            comment=self.comment.get(),
            keep_editing=self.keep_editing.get()
        )


class PublishFileFromWorkingCopy(flow.Action):

    _revision = flow.Parent()
    _file = flow.Parent(4)
    
    comment = flow.SessionParam('', PresetSessionValue)
    keep_editing = flow.SessionParam(True, PresetSessionValue).ui(
        editor='bool',
        tooltip='If disabled, delete your working copy after publication'
    )
    upload_after_publish = flow.Param(False, UploadAfterPublishValue).ui(editor='bool')

    def allow_context(self, context):
        return (
            context
            and self._revision.is_working_copy(from_current_user=True)
            and (
                not self._file.is_locked()
                or self._file.is_locked(by_current_user=True)
            )
        )
    
    def get_buttons(self):
        self.check_default_values()
        
        msg = "<h2>Publish</h2>"

        working_copies = self._file.get_working_copies()
        if working_copies:
            user_names = [wc.user.get() for wc in working_copies]
            user_names = ["<b>"+n+"</b>" for n in user_names]
            msg += (
                "<h3><font color=#D66500><br>"
                "This file is currently being edited by one or more users (%s)."
                "</font></h3>"
                % ', '.join(user_names)
            )

        self.message.set(msg)
        
        return ['Publish', 'Cancel']

    def check_default_values(self):
        self.comment.apply_preset()
        self.keep_editing.apply_preset()
        self.upload_after_publish.check_default_value()
    
    def update_presets(self):
        self.comment.update_preset()
        self.keep_editing.update_preset()
        self.upload_after_publish.update_preset()

    def run(self, button):
        if button == 'Cancel':
            return
        
        self.update_presets()

        publish_action = self._file.publish_action
        publish_action.publish_file(
            self._file,
            comment=self.comment.get(),
            keep_editing=self.keep_editing.get(),
            upload_after_publish=self.upload_after_publish.get()
        )


class SiteName(flow.values.ChoiceValue):
    
    def choices(self):
        sites = self.root().project().get_working_sites()
        return sites.mapped_names()
    
    def revert_to_default(self):
        site = self.root().project().get_current_site()
        self.set(site.name())


class RevisionActionDependencyView(DependencyView):
    
    _parent = flow.Parent(5)
    
    def get_site_name(self):
        return self._action.target_site.get()
    
    def get_revision_name(self):
        return self._action.revision.name()


class RequestRevisionDependencies(flow.Action):
    
    revision = flow.Parent().ui(hidden=True)
    target_site = flow.Param(None, ActiveSiteChoiceValue).watched()
    dependencies = flow.Child(RevisionActionDependencyView)
    predictive_only = flow.SessionParam(False).ui(editor='bool').watched()
    
    def child_value_changed(self, child_value):
        if child_value in [self.target_site, self.predictive_only]:
            self.update_dependencies()
    
    def update_dependencies(self):
        self.dependencies.update_dependencies_data()
        self.dependencies.touch()
    
    def get_buttons(self):
        choices = self.target_site.choices()
        
        if not choices:
            return ['Cancel']
        
        self.target_site.set(choices[0])
        
        return ['Proceed', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        target_site = self.target_site.get()
        
        for d in self.dependencies.mapped_items():
            revision_oid = d.revision_oid.get()
            if revision_oid is not None and d.in_breakdown.get():
                rev = self.root().get_object(revision_oid)
                status = rev.get_sync_status(site_name=target_site)
                
                if status == 'NotAvailable':
                    rev.request_as.sites.target_site.set(target_site)
                    rev.request_as.sites.source_site.set(d.source_site.get())
                    rev.request_as.run(None)
        
        return self.get_result(close=False)


class SyncStatus(Entity):

    status = Property().ui(editable=False)

    def get_default_value(self):
        return 'NotAvailable'


class SyncStatutes(EntityView):
    '''
    This class manages the synchronization statutes of a tracked file revision.
    '''

    _revision = flow.Parent()
    _history = flow.Parent(3)

    @classmethod
    def mapped_type(cls):
        return SyncStatus
    
    def set_status(self, site_name, status):
        if site_name not in self.mapped_names():
            s = self.add(site_name)
        else:
            s = self.get_mapped(site_name)
        
        s.status.set(status)
        
        self._document_cache = None # Reset map cache
        self._history.sync_statutes.touch() # Reset history status map cache

    def collection_name(self):
        return self.root().project().get_file_manager().sync_statutes.collection_name()


class Revision(Entity):

    _revisions = flow.Parent()
    _history = flow.Parent(2)
    _file = flow.Parent(3)

    user = Property().ui(editable=False)
    date = Property().ui(editable=False, editor='datetime')
    comment = Property().ui(editable=False)
    site = Property().ui(editable=False)
    hash = Property().ui(editable=False)
    ready_for_sync = Property().ui(editable=False, editor='bool')
    working_copy = Property().ui(editable=False, editor='bool')
    path = Property().ui(editable=False)

    sync_statutes = flow.Child(SyncStatutes).injectable()

    open = flow.Child(OpenRevision)
    make_current = flow.Child(MakeCurrentRevisionAction)
    publish = flow.Child(PublishFileFromWorkingCopy)
    create_working_copy = flow.Child(CreateWorkingCopyFromRevision)
    request = flow.Child(Request)
    request_as = flow.Child(RequestAs)
    request_dependencies = flow.Child(RequestRevisionDependencies)
    upload = flow.Child(UploadRevision)
    download = flow.Child(DownloadRevision)
    compute_hash_action = flow.Child(ComputeRevisionHash)
    check_hash = flow.Child(CheckRevisionHash)
    dependencies = flow.Param("").ui(editor='textarea', editable=False)

    @classmethod
    def get_property_names_and_labels(cls):
        return [
            ('name', 'Revision'), ('user', 'Creator'),
            ('date', 'Created on'), ('comment', 'Comment')
        ]
    
    def configure(self, creator_name, is_working_copy, site_name, status, comment, ready_for_sync):
        self.date.set(time.time())
        self.user.set(creator_name)
        self.working_copy.set(is_working_copy)
        self.site.set(site_name)
        self.set_sync_status(status)
        self.comment.set(comment)
        self.ready_for_sync.set(ready_for_sync)

    def get_path(self, relative=False):
        '''
        If relative is True, returns the path of this revision without the project
        root. Otherwise, returns the path of the revision on the current site.
        '''
        if relative:
            return self.path.get()
        
        return os.path.join(
            self.root().project().get_root(), self.path.get()
        )
    
    def update_path(self, path_format=None):
        '''
        Updates the relative path of this revision.

        If provided, `path_format` must be a format string from which the path
        will be computed with `compute_path()`. Otherwise, the path will defaults
        to the value returned by `get_default_path()`.
        '''
        if path_format is None:
            path = self.get_default_path()
        else:
            path = self._compute_path(path_format)
        
        self.path.set(path)
    
    def _get_default_suffix(self):
        '''
        Returns the default path suffix of this revision.

        The suffix should contain the revision underlying
        file name, possibly under one or more folders.
        Default is to return the revision's file complete
        name under a folder with the name of the revision
        (e.g., <revision_name>/<file_complete_name>.<file_extension>)
        '''
        file_name = '{file_name}.{extension}'.format(
            file_name=self._file.complete_name.get(),
            extension=self._file.format.get()
        )
        return os.path.join(self.name(), file_name)
    
    def get_default_path(self):
        '''
        Returns the default relative path of this revision.
        '''
        return os.path.join(
            self._file.get_default_path(), self._get_default_suffix()
        )
    
    def _compute_path(self, path_format):
        '''
        Computes a path given the format string `path_format`.
        
        By default, keywords in `path_format` are replaced with the values of the
        entries with the same names in the contextual settings of this revision.
        In case there is no match, a keyword is replaced by an empty string.
        '''
        kwords = keywords_from_format(path_format)
        settings = get_contextual_dict(self, 'settings')
        values = {}
        for kword in kwords:
            values[kword] = settings.get(kword, '')
        
        path = pathlib.Path(path_format.format(**values))
        
        return f'{path}.{self._file.format.get()}'

    def is_current(self):
        return self.name() == self._file.current_revision.get()

    def is_working_copy(self, from_current_user=False):
        return (
            self.working_copy.get()
            and (
                not from_current_user
                or self.name() == self.root().project().get_user_name()
            )
        )

    def get_sync_status(self, site_name=None, exchange=False):
        """
        Returns revision's status on the site identified
        by the given name, or the project's exchange site
        if `exchange` is True.

        If site_name is None, this method returns its status
        on the current site.
        """
        if exchange:
            site_name = self.root().project().admin.multisites.exchange_site_name.get()
        elif not site_name:
            site_name = self.root().project().admin.multisites.current_site_name.get()
        
        return self._history.sync_statutes.get_status(self.name(), site_name)

    def set_sync_status(self, status, site_name=None, exchange=False):
        """
        Sets revision's status on the site identified
        by the given name, or the project's exchange site
        if `exchange` is True, to the given status.

        If site_name is None, this method sets its status
        on the current site.
        """
        if exchange:
            site_name = self.root().project().admin.multisites.exchange_site_name.get()
        elif not site_name:
            site_name = self.root().project().admin.multisites.current_site_name.get()

        self.sync_statutes.set_status(site_name, status)

    def get_last_edit_time(self):
        if self.exists():
            return os.path.getmtime(self.get_path())
        
        return 0
    
    def exists(self):
        return os.path.exists(self.get_path())
    
    def compute_hash(self):
        path = self.get_path()
        
        if os.path.exists(path):
            with open(path, "rb") as f:
                content = f.read()

            return hashlib.md5(content).hexdigest()
    
    def update_hash(self):
        self.hash.set(self.compute_hash())
        self.hash.touch()
    
    def hash_is_valid(self):
        return self.hash.get() == self.compute_hash()

    def compute_child_value(self, child_value):
        if child_value is self.is_current:
            child_value.set(self.name() == self._file.current_revision.get())
        elif child_value is self.path:
            path = os.path.join(
                self.root().project().get_root("UNKNOWN_ROOT_DIR"),
                self._file.path.get(),
                self.name(),
            )
            child_value.set(path)
        elif child_value is self.playblast_path:
            child_value.set(
                os.path.join(
                    os.path.dirname(self._file.get_path()),
                    "preview",
                    "%s_%s-movie.mov" % (self._file.complete_name.get(), self.name()),
                )
            )
    
    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(revision=self.name())


class ToggleSyncStatuses(flow.Action):
    _revisions = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._revisions.show_sync_statuses.set(
            not self._revisions.show_sync_statuses.get()
        )
        self._revisions.touch()


class ToggleShortNames(flow.Action):
    _revisions = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._revisions.enable_short_names.set(
            not self._revisions.enable_short_names.get()
        )
        self._revisions.touch()


class TogglePublicationDateFormat(flow.Action):
    
    ICON = ('icons.libreflow', 'time_format')
    
    _revisions = flow.Parent()
    
    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return context and context.endswith('.inline')
    
    def run(self, button):
        enabled = self._revisions.time_ago_enabled.get()
        self._revisions.time_ago_enabled.set(not enabled)
        self._revisions.touch()


class ToggleActiveSites(flow.Action):

    ICON = ('icons.libreflow', 'active_site')

    _revisions = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        active_sites_only = self._revisions.active_sites_only
        active_sites_only.set(not active_sites_only.get())


class Revisions(EntityView):

    STYLE_BY_STATUS = {
        "Available":    ("#45cc3d", ("icons.libreflow", "checked-symbol-colored")),
        "Requested":    ("#cc3b3c", ("icons.libreflow", "exclamation-sign-colored")),
        "NotAvailable": ("#cc3b3c", ("icons.libreflow", "blank"))
    }

    _history = flow.Parent()
    _file = flow.Parent(2)
    _needs_update = flow.SessionParam(True).ui(editor='bool')

    show_sync_statuses = flow.SessionParam(True).ui(hidden=True, editor='bool')
    enable_short_names = flow.SessionParam(True).ui(hidden=True, editor='bool').watched()
    time_ago_enabled = flow.SessionParam(False).ui(hidden=True, editor='bool')
    active_sites_only = flow.SessionParam(True).ui(hidden=True, editor='bool').watched()

    toggle_sync_statuses = flow.Child(ToggleSyncStatuses)
    toggle_short_names = flow.Child(ToggleShortNames)
    toggle_date_format = flow.Child(TogglePublicationDateFormat)
    toggle_active_sites = flow.Child(ToggleActiveSites)

    def __init__(self, parent, name):
        super(Revisions, self).__init__(parent, name)
        self._site_names_cache = None
        self._file_cache = None
        self._file_cache_ttl = 5

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(Revision)

    def columns(self):
        columns = ['Revision', 'Creator', 'Created on']
        
        if self.show_sync_statuses.get():
            _, display_names = self._ensure_site_names()
            columns += display_names
        
        columns.append('Comment')

        return columns

    def collection_name(self):
        return self.root().project().get_file_manager().revisions.collection_name()

    def add(self, name=None, is_working_copy=False, comment="", ready_for_sync=True, path_format=None):
        if not name:
            publication_count = len([r for r in self.mapped_items() if not r.is_working_copy()])
            name = 'v%03i' % (publication_count + 1)

        r = super(Revisions, self).add(name)
        r.configure(
            creator_name=self.root().project().get_user_name(),
            is_working_copy=is_working_copy,
            site_name=self.root().project().admin.multisites.current_site_name.get(),
            status='Available',
            comment=comment,
            ready_for_sync=ready_for_sync
        )
        r.update_path(path_format)

        self._document_cache = None # Reset map cache
        
        return r
    
    def remove(self, name):
        r = self.get_mapped(name)
        r.sync_statutes.clear()
        super(Revisions, self).remove(name)
    
    def clear(self):
        for r in self.mapped_items():
            r.sync_statutes.clear()
        
        super(Revisions, self).clear()

    def _fill_row_cells(self, row, item):
        self.mapped_names()

        name = item.name()
        if self._document_cache[item.oid()]['working_copy']:
            name += " ("
            if item.name() == self.root().project().get_user_name():
                name += "your "
            name += "working copy)"
        
        if item.get_sync_status() == "Requested":
            name += " ⏳"
        
        row['Revision'] = name
        row['Creator'] = self._document_cache[item.oid()]['user']
        row['Comment'] = self._document_cache[item.oid()]['comment']
        create_datetime = datetime.datetime.fromtimestamp(self._document_cache[item.oid()]['date'])

        if self.time_ago_enabled.get():
            row['Created on'] = timeago.format(create_datetime, datetime.datetime.now())
        else:
            row['Created on'] = create_datetime.strftime('%Y-%m-%d %H:%M:%S')

        if self.show_sync_statuses.get():
            _, display_names = self._ensure_site_names()
            d = dict.fromkeys(display_names, '')
            row.update(d)

    def _fill_row_style(self, style, item, row):
        file_data = self._ensure_file_data()
        seen_name = file_data['active']
        
        if item.name() == file_data['current']:
            if item.name() == seen_name or seen_name == "current":
                style["icon"] = ('icons.libreflow', 'circular-shape-right-eye-silhouette')
            else:
                style["icon"] = ('icons.libreflow', 'circular-shape-silhouette')
        else:
            if item.name() == seen_name:
                style["icon"] = ('icons.libreflow', 'circle-shape-right-eye-outline')
            else:
                style["icon"] = ('icons.libreflow', 'circle-shape-outline')

        style['Revision_foreground-color'] = self.STYLE_BY_STATUS[item.get_sync_status()][0]

        if self.show_sync_statuses.get():
            names, display_names = self._ensure_site_names()
            
            for i in range(len(names)):
                style[display_names[i] + '_icon'] = self.STYLE_BY_STATUS[item.get_sync_status(names[i])][1]
        
        style["Revision_activate_oid"] = item.open.oid()
    
    def _get_site_names(self):
        sites_data = self.root().project().admin.multisites.sites_data.get()
        ordered_names = self.root().project().get_current_site().ordered_site_names.get()
        names = []
        display_names = []

        for name in ordered_names:
            if self.active_sites_only.get() and not sites_data[name]['is_active']:
                continue
            
            names.append(name)
        
        exchange_site = self.root().project().get_exchange_site()

        if self.enable_short_names.get():
            display_names = [exchange_site.short_name.get()]
            display_names += [sites_data[name]['short_name'] for name in names]
            names.insert(0, exchange_site.name())
        else:
            names.insert(0, exchange_site.name())
            display_names = names
        
        return names, display_names
    
    def _ensure_site_names(self):
        if self._site_names_cache is None or self._needs_update.get():
            self._site_names_cache = self._get_site_names()
            self._needs_update.set(False)
        
        return self._site_names_cache
    
    def _ensure_file_data(self):
        if (
            self._file_cache is None
            or self._file_cache_birth < time.time() - self._file_cache_ttl
        ):
            self._file_cache = {
                'active': self._file.current_user_sees.get(),
                'current': self._file.current_revision.get()
            }
            self._file_cache_birth = time.time()
        
        return self._file_cache

    def touch(self):
        self._file_cache = None
        super(Revisions, self).touch()

    def child_value_changed(self, child_value):
        if child_value in [self.enable_short_names, self.active_sites_only] and self.show_sync_statuses.get():
            self._needs_update.set(True)
            self.touch()


class HistorySyncStatutes(EntityCollection):
    '''
    This class caches all revisions statutes recorded
    in the revision store which belong to a given history.
    '''

    _history = flow.Parent()

    @classmethod
    def mapped_type(cls):
        return SyncStatus
    
    def mapped_names(self, page_num=0, page_size=None):
        cache_key = (page_num, page_size)
        if (
            self._document_cache is None
            or self._document_cache_key != cache_key
            or self._document_cache_birth < time.time() - self._document_cache_ttl
        ):
            cursor = (
                self.get_entity_store()
                .get_collection(self.collection_name())
                .find(self.query_filter())
            )
            if page_num is not None and page_size is not None:
                cursor.skip((page_num - 1) * page_size)
                cursor.limit(page_size)
            
            name_and_doc = []
            for i in cursor:
                _, revision, _, site = i['name'].rsplit('/', maxsplit=3)
                name_and_doc.append((f'{revision}_{site}', i))
            
            self._document_names_cache = [n for n, d in name_and_doc]
            self._document_cache = dict(name_and_doc)
            self._document_cache_birth = time.time()
            self._document_cache_key = cache_key
            self.ensure_indexes()
        
        return self._document_names_cache

    def set_property(self, entity_name, property_name, value):
        self.mapped_names()
        self.get_entity_store().get_collection(self.collection_name()).update_one(
            {"name": self._document_cache[entity_name]['name']},
            {"$set": {property_name: value}},
        )

    def get_property(self, entity_name, property_name):
        self.root().session().log_debug(f'===========> {self._history.revisions.oid()}/{entity_name} {property_name}')
        self.mapped_names()

        value = (
            self.get_entity_store()
            .get_collection(self.collection_name())
            .find_one(
                {"name": self._document_cache[entity_name]['name']},
                {property_name: 1},
            )
        )
        try:
            return value[property_name]
        except KeyError:
            default = getattr(self.mapped_type(), property_name).get_default_value()
            return default
    
    def get_status(self, revision_name, site_name):
        self.mapped_names()
        st = self._document_cache.get(
            f'{revision_name}_{site_name}',
            {'status': 'NotAvailable'}
        )
        return st['status']

    def collection_name(self):
        return self.root().project().get_file_manager().sync_statutes.collection_name()
    
    def query_filter(self):
        return {'name': {'$regex': f'^{self._history.revisions.oid()}/[^/]*'}}


class History(flow.Object):

    revisions = flow.Child(Revisions).injectable().ui(expanded=True)
    sync_statutes = flow.Child(HistorySyncStatutes).injectable().ui(hidden=True)
    department = flow.Parent(3)


class CreateWorkingCopyAction(flow.Action):

    ICON = ('icons.libreflow', 'edit-blank')

    _file = flow.Parent()

    from_revision = flow.Param(None, RevisionsChoiceValue).ui(label="Reference")

    def get_buttons(self):
        msg = "<h3>Create a working copy</h3>"

        if self._file.has_working_copy(from_current_user=True):
            msg += "<font color=#D66700>WARNING: You already have a working copy to your name. \
                    Choosing to create a new one will overwrite your changes.</font>"
        self.message.set(msg)

        self.from_revision.revert_to_default()

        return ["Create", "Create from scratch", "Cancel"]

    def needs_dialog(self):
        return not self._file.is_empty() or self._file.has_working_copy(
            from_current_user=True
        )

    def allow_context(self, context):
        return context and self._file.editable()

    def run(self, button):
        if button == "Cancel":
            return
        
        if button == "Create from scratch":
            working_copy = self._file.create_working_copy()
        else:
            ref_name = self.from_revision.get()

            if ref_name == "" or self._file.is_empty():
                ref_name = None
            elif not self._file.has_revision(ref_name):
                msg = self.message.get()
                msg += (
                    "<br><br><font color=#D5000D>There is no revision %s for this file.</font>"
                    % ref_name
                )
                self.message.set(msg)

                return self.get_result(close=False)

            working_copy = self._file.create_working_copy(reference_name=ref_name)

        self._file.set_current_user_on_revision(working_copy.name())
        self._file.touch()
        self._file.get_revisions().touch()


class SeeRevisionAction(flow.Action):

    ICON = ("icons.libreflow", "watch")

    _file = flow.Parent()
    revision_name = flow.Param(None, RevisionsChoiceValue).ui(label="Revision")

    def allow_context(self, context):
        return False

    def get_buttons(self):
        self.message.set("<h3>Choose a revision to open</h3>")

        if self._file.is_empty():
            self.message.set("<h3>This file has no revision</h3>")
            return ["Cancel"]

        seen_name = self._file.current_user_sees.get()
        if seen_name != "current" or self._file.has_current_revision():
            if seen_name == "current":
                seen_name = self._file.current_revision.get()
            self.revision_name.set(seen_name)
        else:
            self.revision_name.set(self._file.get_revisions().mapped_names[0])

        return ["See", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        name = self.revision_name.get()

        if self._file.get_revision(name).is_current():
            name = "current"

        self._file.set_current_user_on_revision(name)
        self._file.touch()


class OpenFileAction(GenericRunAction):

    ICON = ('icons.gui', 'open-folder')

    def extra_argv(self):
        return [self._file.get_path()]


class OpenTrackedFileAction(GenericRunAction):

    ICON = ('icons.gui', 'open-folder')

    _to_open = flow.Param("")
    revision_name = flow.Param(None, RevisionsChoiceValue).ui(label="Revision")

    def get_run_label(self):
        return 'Open file'

    def get_buttons(self):
        if super(OpenTrackedFileAction, self).needs_dialog():
            return super(OpenTrackedFileAction, self).get_buttons()

        self.revision_name.revert_to_default()

        # At least one existing revision
        buttons = ["Open revision", "Cancel"]
        user_sees = self._file.current_user_sees.get()

        # Check if user's working copy already exists
        if not self._file.has_working_copy(from_current_user=True) and self._file.editable():
            buttons.insert(1, "Create a working copy")

        if user_sees == "current":
            if not self._file.has_current_revision():
                msg = "<h3>No active revision</h3>"
                self.message.set(msg)

                return buttons

            user_sees = self._file.current_revision.get()

        # Current user is seeing a revision
        revision = self._file.get_revision(user_sees)

        if not revision.is_working_copy(from_current_user=True):
            msg = "<h3>Read-only mode</h3>"
            msg += "You're about to open this file in read-only mode. If you want to edit it, you can open your working copy or create one."
            self.message.set(msg)

        return buttons

    def needs_dialog(self):
        seen_name = self._file.current_user_sees.get()
        if seen_name == "current":
            seen = self._file.get_current_revision()
        else:
            seen = self._file.get_revision(seen_name)

        return not self._file.is_empty() and (
            seen is None or not seen.is_working_copy(from_current_user=True) or not self._file.editable()
        )

    def extra_argv(self):
        revision = self._file.get_revision(self._to_open.get())
        return [revision.get_path()]

    def run(self, button):
        if button == "Cancel":
            return

        if button == "Create a working copy" or self._file.is_empty():
            ref_name = None if self._file.is_empty() else self.revision_name.get()
            working_copy = self._file.create_working_copy(reference_name=ref_name)
            revision_name = working_copy.name()
        elif button == "Open revision":
            revision_name = self.revision_name.get()
        else:
            revision_name = self._file.current_user_sees.get()

        self._file.set_current_user_on_revision(revision_name)
        self._to_open.set(revision_name)
        result = super(OpenTrackedFileAction, self).run(button)

        self._file.touch()

        return result


class OpenWithDefaultApp(RunAction):

    def runner_name_and_tags(self):
        return "DefaultEditor", []

    def extra_env(self):
        env = get_contextual_dict(self, "settings")
        env["USER_NAME"] = self.root().project().get_user_name()
        root_path = self.root().project().get_root()

        if root_path:
            env["ROOT_PATH"] = root_path

        return env


class OpenWithAction(OpenTrackedFileAction):
    
    def runner_name_and_tags(self):
        raise NotImplementedError()

    def allow_context(self, context):
        return context and self._file.format.get() in self.supported_extensions()

    @classmethod
    def supported_extensions(cls):
        raise NotImplementedError()


class OpenWithBlenderAction(OpenWithAction):

    ICON = ("icons.libreflow", "blender")

    def runner_name_and_tags(self):
        return "Blender", []

    @classmethod
    def supported_extensions(cls):
        return ["blend"]


class OpenWithKritaAction(OpenWithAction):

    ICON = ("icons.libreflow", "krita")

    def runner_name_and_tags(self):
        return "Krita", []

    @classmethod
    def supported_extensions(cls):
        return ["kra", "png", "jpg"]


class OpenWithVSCodiumAction(OpenWithAction):

    ICON = ("icons.libreflow", "vscodium")

    def runner_name_and_tags(self):
        return "VSCodium", []

    @classmethod
    def supported_extensions(cls):
        return ["txt"]


class OpenWithNotepadPPAction(OpenWithAction):

    ICON = ("icons.flow", "notepad")

    def runner_name_and_tags(self):
        return "NotepadPP", []

    @classmethod
    def supported_extensions(cls):
        return ["txt"]


class MakeFileCurrentAction(flow.Action):

    _file = flow.Parent()

    def needs_dialog(self):
        return False

    def allow_context(self, context):
        head_revision = self._file.get_head_revision()
        return (
            context and head_revision is not None and not head_revision.is_current()
        )  # And user is admin ?

    def run(self, button):
        self.root().session().log_debug(
            "Make latest revision of file %s current" % self._file.name()
        )

        self._file.make_current(self._file.get_head_revision())
        self._file.touch()


class GotoHistory(flow.Action):

    ICON = ("icons.libreflow", "history")

    _file = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        return self.get_result(goto=self._file.history.oid())


class LockAction(flow.Action):

    ICON = ("icons.gui", "padlock")

    _file = flow.Parent()

    def allow_context(self, context):
        return context and not self._file.is_locked()
    
    def needs_dialog(self):
        return False

    def run(self, button):
        self._file.lock()
        self._file._map.touch()


class UnlockAction(flow.Action):

    ICON = ("icons.gui", "open-padlock-silhouette")

    _file = flow.Parent()

    def allow_context(self, context):
        return self._file.is_locked(by_current_user=True)
    
    def needs_dialog(self):
        return False

    def run(self, button):
        self._file.unlock()
        self._file._map.touch()


class UserSees(flow.values.Value):
    pass


class ActiveUsers(flow.Map):
    @classmethod
    def mapped_type(cls):
        return UserSees

    def columns(self):
        return ["User", "Revision"]

    def _fill_row_cells(self, row, item):
        row["User"] = item.name()
        row["Revision"] = item.get()


class RevealInExplorer(RunAction):

    ICON = ('icons.flow', 'explorer')

    _file = flow.Parent()

    def runner_name_and_tags(self):
        return "DefaultEditor", []

    def extra_argv(self):
        # TODO: find a way to get the real file path
        available_revisions = self._file.get_revision_names(
            sync_status='Available'
        )
        r = self._file.get_revision(available_revisions[0])
        
        return [os.path.dirname(r.get_path())]
    
    def allow_context(self, context):
        return not self._file.is_empty()

    def needs_dialog(self):
        return False


class FileSystemItem(Entity):

    _map = flow.Parent()

    format        = Property().ui(editable=False)
    complete_name = Property().ui(editable=False)
    display_name  = Property().ui(editable=False)

    settings = flow.Child(ContextualView).ui(hidden=True)
    path = flow.Computed(cached=True)

    def get_name(self):
        return self.name()

    def get_path(self):
        return os.path.join(
            self.root().project().get_root(),
            self.path.get()
        )

    def get_last_edit_time(self):
        path = self.get_path()
        if os.path.exists(path):
            return os.path.getmtime(path)
        
        return 0
    
    def compute_child_value(self, child_value):
        if child_value is self.path:
            self.path.set(os.path.join(
                self._map.get_parent_path(),
                self.get_name()
            ))
    
    def configure(self, format, complete_name, display_name):
        self.format.set(format)
        self.complete_name.set(complete_name)
        self.display_name.set(display_name)

    def create(self):
        raise NotImplementedError

    def remove(self):
        raise NotImplementedError
    
    def get_icon(self, extension=None):
        return ('icons.gui', 'text-file-1')
    
    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(file=self.complete_name.get())


class File(FileSystemItem):

    open = flow.Child(OpenFileAction)
    reveal = flow.Child(RevealInExplorer).ui(label="Reveal in explorer")

    def get_name(self):
        return "%s.%s" % (self.complete_name.get(), self.format.get())

    def get_template_path(self):
        try:
            return resources.get("file_templates", "template.%s" % self.format.get())
        except resources.NotFoundError:
            raise resources.NotFoundError(
                "No template file for '%s' format." % self.format.get()
            )

    def editable(self):
        settings = self.root().project().admin.project_settings
        patterns = settings.non_editable_files.get().split(",")

        for pattern in patterns:
            pattern = pattern.encode('unicode-escape').decode().replace(" ", "")
            if fnmatch.fnmatch(self.display_name.get(), pattern):
                return False
        
        return True

    def create(self):
        shutil.copyfile(self.get_template_path(), self.get_path())

    def remove(self):
        os.remove(self.get_path())
    
    def get_icon(self, extension=None):
        return CHOICES_ICONS.get(extension, ('icons.gui', 'text-file-1'))


class SearchExistingRevisions(flow.Action):

    _file = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        folders = [
            f for f in os.listdir(self._file.get_path()) if re.search(r"^v\d\d\d$", f)
        ]
        revisions = self._file.get_revisions()

        for name in folders:
            try:
                revisions.add(name)
            except ValueError:
                pass

        revisions.touch()


class LinkedJob(jobs_flow.Job):

    _children = flow.OrderedStringSetParam()

    def add_child(self, jid, index=0):
        self._children.add(jid, index)
    
    def notify_children(self):
        for jid in self._children.get():
            self.root().session().cmds.Jobs.set_job_paused(jid, False)

    def execute(self):
        print('----------------EXECUTING JOB', self.oid())
        self.touch()
        self.root().session().cmds.Jobs.set_job_in_progress(self.job_id.get())
        try:
            self._do_job()
        except Exception as err:
            self.on_error(traceback.format_exc())
        else:
            self.root().session().cmds.Jobs.set_job_done(self.job_id.get())
            self.status.touch()
            self.touch()
            self.notify_children()
        finally:
            self.touch()


class FileJob(LinkedJob):

    _file = flow.Parent(2)
    
    def get_log_filename(self):
        root = str(pathlib.Path.home()) + "/.libreflow/log/"
        dt = datetime.datetime.fromtimestamp(self.get_created_on())
        dt = dt.astimezone().strftime("%Y-%m-%dT%H-%M-%S%z")
        
        path = os.path.join(root, '%s_%s.log' % (self.__class__.__name__, dt))
        return path


class PlayblastJob(FileJob):

    revision = flow.Param().ui(editable=False)
    use_simplify = flow.BoolParam().ui(editable=False)
    reduce_textures = flow.BoolParam(False).ui(editable=False)
    target_texture_width = flow.IntParam(4096).ui(editable=False)

    def _do_job(self):
        # Job is to wait until the playblast is ended
        render_blender_playblast = self._file.render_blender_playblast
        render_blender_playblast.revision_name.set(self.revision.get())
        render_blender_playblast.use_simplify.set(self.use_simplify.get())
        render_blender_playblast.reduce_textures.set(self.reduce_textures.get())
        render_blender_playblast.target_texture_width.set(self.target_texture_width.get())
        
        result = render_blender_playblast.run('Render')
        rid = result['runner_id']

        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)

        while runner_info['is_running']:
            self.show_message("Waiting for runner %s to finish" % rid)
            time.sleep(1)
            
            runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message("Runner %s finished !" % rid)


class FileJobs(jobs_flow.Jobs):

    @classmethod
    def job_type(cls):
        return FileJob

    def create_job(self, job_type=None):
        name = '{}{:>05}'.format(self._get_job_prefix(), self._get_next_job_id())
        job = self.add(name, object_type=job_type)
        return job


class RenderBlenderPlayblast(OpenWithBlenderAction):

    _files = flow.Parent(2)
    revision_name = flow.Param("", RevisionsChoiceValue).watched()
    use_simplify = flow.SessionParam(False, PresetSessionValue).ui(
        tooltip="Use low-definition rigs",
        editor='bool',
        )
    reduce_textures = flow.SessionParam(False, PresetSessionValue).ui(
        tooltip="Reduce texture sizes before render, to reduce memory footprint",
        editor='bool',
    )
    target_texture_width = flow.SessionParam(4096, PresetSessionValue).ui(
        tooltip="Size to reduce textures to",
        editor='int',
    )

    def get_run_label(self):
        return 'Render playblast'

    def _sequence_number_from_name(self, sequence_name):
        tmp = re.findall(r"\d+", sequence_name)
        numbers = list(map(int, tmp))
        return numbers[0]
    
    def check_default_values(self):
        self.revision_name.revert_to_default()
        self.use_simplify.apply_preset()
        self.reduce_textures.apply_preset()
        self.target_texture_width.apply_preset()
    
    def update_presets(self):
        self.use_simplify.update_preset()
        self.reduce_textures.update_preset()
        self.target_texture_width.update_preset()

    def get_buttons(self):
        self.check_default_values()
        buttons = ['Render', 'Cancel']
        
        current_site = self.root().project().get_current_site()
        if current_site.site_type.get() == 'Studio':
            buttons.insert(1, 'Submit job')
        
        return buttons

    def needs_dialog(self):
        return True

    def allow_context(self, context):
        return (
            super(RenderBlenderPlayblast, self).allow_context(context)
            and not self._file.is_empty()
        )
    
    def playblast_infos_from_revision(self, revision_name):
        filepath = self._file.path.get()
        filename = "_".join(self._file.name().split("_")[:-1])

        playblast_filename = filename + "_movie"
        playblast_revision_filename = self._file.complete_name.get() + "_movie.mov"
        
        playblast_filepath = os.path.join(
            self.root().project().get_root(),
            os.path.dirname(filepath),
            playblast_filename + "_mov",
            revision_name,
            playblast_revision_filename
        )

        return playblast_filepath, playblast_filename

    def child_value_changed(self, child_value):
        if child_value is self.revision_name:
            msg = "<h2>Render playblast</h2>"
            playblast_path, _ = self.playblast_infos_from_revision(child_value.get())

            # Check if revision playblast exists
            if os.path.exists(playblast_path):
                msg += (
                    "<font color=#D50000>"
                    "Choosing to render a revision's playblast "
                    "will override the existing one."
                    "</font>"
                )

            self.message.set(msg)

    def extra_argv(self):
        file_settings = get_contextual_dict(
            self._file, "settings", ["sequence", "shot"]
        )
        project_name = self.root().project().name()
        revision = self._file.get_revision(self.revision_name.get())
        python_expr = """import bpy
bpy.ops.lfs.playblast(do_render=True, filepath='%s', studio='%s', project='%s', sequence='s%04i', scene='%s', do_simplify=%s, do_reduce_textures=%s, target_texture_width=%s, version='%s')""" % (
            self.output_path,
            self.root().project().get_current_site().name(),
            project_name,
            self._sequence_number_from_name(file_settings["sequence"]),
            file_settings["shot"],
            str(self.use_simplify.get()),
            str(self.reduce_textures.get()),
            str(self.target_texture_width.get()),
            self.revision_name.get(),
        )

        return [
            "-b",
            revision.get_path(),
            "--addons",
            "mark_sequence",
            "--python-expr",
            wrap_python_expr(python_expr),
        ]

    def run(self, button):
        if button == "Cancel":
            return
        elif button == "Submit job":
            self.update_presets()

            submit_action = self._file.submit_blender_playblast_job
            submit_action.revision_name.set(self.revision_name.get())
            submit_action.use_simplify.set(self.use_simplify.get())
            submit_action.reduce_textures.set(self.reduce_textures.get())
            submit_action.target_texture_width.set(self.target_texture_width.get())
            
            return self.get_result(
                next_action=submit_action.oid()
            )
        
        self.update_presets()

        revision_name = self.revision_name.get()
        playblast_path, playblast_name = self.playblast_infos_from_revision(
            revision_name
        )

        # Get or create playblast file
        if not self._files.has_mapped_name(playblast_name + "_mov"):
            playblast_file = self._files.add_file(
                name=playblast_name,
                extension="mov",
                base_name=self._file.complete_name.get() + "_movie",
                tracked=True
            )
        else:
            playblast_file = self._files[playblast_name + "_mov"]
        
        # Get or add playblast revision
        if playblast_file.has_revision(revision_name):
            playblast_revision = playblast_file.get_revision(
                revision_name
            )
        else:
            playblast_revision = playblast_file.get_revisions().add(
                name=revision_name
            )
        
        # Configure playblast revision
        revision = self._file.get_revision(revision_name)
        playblast_revision.comment.set(revision.comment.get())
        playblast_revision.set_sync_status("Available")

        # Store revision path as playblast output path
        self.output_path = playblast_revision.get_path().replace("\\", "/")
        
        # Ensure playblast revision folder exists and is empty
        if not os.path.exists(playblast_revision.path.get()):
            os.makedirs(playblast_revision.path.get())
        elif os.path.exists(self.output_path):
            os.remove(self.output_path)

        result = super(RenderBlenderPlayblast, self).run(button)
        self._files.touch()
        return result


class SubmitBlenderPlayblastJob(flow.Action):
    
    _file = flow.Parent()
    
    pool = flow.Param('default', SiteJobsPoolNames)
    priority = flow.SessionParam(10).ui(editor='int')
    
    revision_name = flow.Param().ui(hidden=True)
    use_simplify = flow.Param().ui(hidden=True)
    reduce_textures = flow.Param().ui(hidden=True)
    target_texture_width = flow.Param().ui(hidden=True)
    
    def get_buttons(self):
        self.message.set('<h2>Submit playblast to pool</h2>')
        self.pool.apply_preset()
        return ['Submit', 'Cancel']
    
    def allow_context(self, context):
        return False
    
    def _get_job_label(self):
        label = f'Render playblast - {self._file.display_name.get()}'
        
        settings = get_contextual_dict(self, 'settings')
        category = settings['file_category']
        
        if category == 'PROD':
            film = settings['film']
            seq = settings['sequence']
            shot = settings['shot']
            dept = settings['department']
            label += f' (from {film}/{seq}/{shot}/{dept})'
        elif category == 'LIB':
            type = settings['asset_type']
            family = settings['asset_family']
            asset = settings['asset_name']
            dept = settings['department']
            label += f' (from {type}/{family}/{asset}/{dept})'
        
        return label
    
    def run(self, button):
        if button == 'Cancel':
            return

        # Update pool preset
        self.pool.update_preset()

        job = self._file.jobs.create_job(job_type=PlayblastJob)
        job.revision.set(self.revision_name.get())
        job.use_simplify.set(self.use_simplify.get())
        job.reduce_textures.set(self.reduce_textures.get())
        job.target_texture_width.set(self.target_texture_width.get())
        site_name = self.root().project().get_current_site().name()        

        job.submit(
            pool=site_name + '_' + self.pool.get(),
            priority=self.priority.get(),
            label=self._get_job_label(),
            creator=self.root().project().get_user_name(),
            owner=self.root().project().get_user_name(),
            paused=False,
            show_console=False,
        )


class PublishAndRenderPlayblast(flow.Action):

    _file = flow.Parent()

    publish = flow.Label('<h2>Publish</h2>')
    comment = flow.SessionParam('', PresetSessionValue)
    keep_editing = flow.SessionParam(True, PresetSessionValue).ui(
        tooltip='Delete your working copy after publication if disabled',
        editor='bool'
    )
    upload_after_publish = flow.Param(False, UploadAfterPublishValue).ui(editor='bool')

    def allow_context(self, context):
        return context and self._file.publish_action.allow_context(context)
    
    def check_default_values(self):
        self.comment.apply_preset()
        self.keep_editing.apply_preset()
        self.upload_after_publish.check_default_value()
    
    def update_presets(self):
        self.comment.update_preset()
        self.keep_editing.update_preset()
        self.upload_after_publish.update_preset()
    
    def get_buttons(self):
        self.check_default_values()

        return ['Publish and render playblast', 'Cancel']
    
    def _configure_and_render(self, revision_name):
        '''
        May be overriden by subclasses to configure and launch playblast rendering
        of the revision `revision_name` of the selected file.
        '''
        pass

    def run(self, button):
        if button == 'Cancel':
            return
        
        # Update parameter presets
        self.update_presets()
        
        # Publish
        publish_action = self._file.publish_action
        publish_action.publish_file(
            self._file,
            comment=self.comment.get(),
            keep_editing=self.keep_editing.get(),
            upload_after_publish=self.upload_after_publish.get()
        )
        
        # Playblast
        ret = self._configure_and_render(self._file.get_head_revision().name())

        return ret


class PublishAndRenderBlenderPlayblast(PublishAndRenderPlayblast):

    render_blender_playblast = flow.Label('<h2>Playblast</h2>')
    use_simplify = flow.SessionParam(False, PresetSessionValue).ui(
        tooltip='Use low-definition rigs',
        editor='bool'
    )
    reduce_textures = flow.SessionParam(False, PresetSessionValue).ui(
        tooltip='Reduce texture sizes before render, to reduce memory footprint',
        editor='bool'
    )
    target_texture_width = flow.SessionParam(4096, PresetSessionValue).ui(
        tooltip="Size to reduce textures to",
        editor='int',
    )
    render_in_pool = flow.SessionParam(False, PresetSessionValue).ui(
        tooltip='Submit playblast rendering in a job pool',
        editor='bool'
    )

    def allow_context(self, context):
        allow_context = super(PublishAndRenderBlenderPlayblast, self).allow_context(context)
        return allow_context and self._file.render_blender_playblast.allow_context(context)

    def check_default_values(self):
        super(PublishAndRenderBlenderPlayblast, self).check_default_values()
        self.use_simplify.apply_preset()
        self.reduce_textures.apply_preset()
        self.target_texture_width.apply_preset()
        self.render_in_pool.apply_preset()
    
    def update_presets(self):
        super(PublishAndRenderBlenderPlayblast, self).update_presets()
        self.use_simplify.update_preset()
        self.reduce_textures.update_preset()
        self.target_texture_width.update_preset()
        self.render_in_pool.update_preset()

    def _configure_and_render(self, revision_name):
        self._file.render_blender_playblast.revision_name.set(revision_name)
        self._file.render_blender_playblast.use_simplify.set(self.use_simplify.get())
        self._file.render_blender_playblast.reduce_textures.set(self.reduce_textures.get())
        self._file.render_blender_playblast.target_texture_width.set(self.target_texture_width.get())
        render_button = 'Submit job' if self.render_in_pool.get() else 'Render'
        
        return self._file.render_blender_playblast.run(render_button)


class PublishAndRenderAEPlayblast(PublishAndRenderPlayblast):

    render_blender_playblast = flow.Label('<h2>Playblast</h2>')
    render_in_pool = flow.SessionParam(False, PresetSessionValue).ui(
        tooltip='Submit playblast rendering in a job pool',
        editor='bool'
    )

    def allow_context(self, context):
        allow_context = super(PublishAndRenderAEPlayblast, self).allow_context(context)
        return allow_context and self._file.select_ae_playblast_render_mode.allow_context(context)
    
    def check_default_values(self):
        super(PublishAndRenderAEPlayblast, self).check_default_values()
        self.render_in_pool.apply_preset()
    
    def update_presets(self):
        super(PublishAndRenderAEPlayblast, self).update_presets()
        self.render_in_pool.update_preset()

    def _configure_and_render(self, revision_name):
        render_select_mode = self._file.select_ae_playblast_render_mode
        render_select_mode.revision.set(revision_name)
        # Configure sequence marking to be done locally by default
        # render_select_mode.mark_image_sequence.render_in_pool.set(False)

        if self.render_in_pool.get():
            render_button = 'Submit job'
        else:
            render_button = 'Render'
        
        return render_select_mode.run(render_button)


class FileRevisionNameChoiceValue(flow.values.ChoiceValue):

    STRICT_CHOICES = False
    action = flow.Parent()

    def get_file(self):
        return self.action._file

    def choices(self):
        if self.get_file() is None:
            return []
        
        return self.get_file().get_revision_names(
            sync_status='Available',
            published_only=True
        )
    
    def revert_to_default(self):
        source_file = self.get_file()
        
        if not source_file:
            self.set(None)
            return
        
        revision = source_file.get_head_revision(sync_status="Available")
        self.set(revision.name() if revision else None)


class KitsuShotTaskType(PresetChoiceValue):

    DEFAULT_EDITOR = 'choice'
    _file = flow.Parent(2)
    
    def choices(self):
        site = self.root().project().get_current_site()

        if site.is_kitsu_admin.get():
            # Return shot types if current site is 
            kitsu_api = self.root().project().kitsu_api()
            return kitsu_api.get_shot_task_types()
        else:
            kitsu_bindings = self.root().project().kitsu_bindings()
            return kitsu_bindings.get_task_types(self._file.display_name.get())

    def revert_to_default(self):
        kitsu_bindings = self.root().project().kitsu_bindings()
        choices = kitsu_bindings.get_task_types(self._file.display_name.get())
        
        if choices:
            default_value = choices[0]
        else:
            default_value = ''
        
        self.set(default_value)


class UploadPlayblastToKitsu(flow.Action):
    
    ICON = ('icons.libreflow', 'kitsu')
    
    _file = flow.Parent()
    
    revision_name = flow.Param(None, FileRevisionNameChoiceValue)
    kitsu_settings = flow.Label('<h3>Kitsu settings</h3>').ui(icon=('icons.libreflow', 'kitsu'))
    current_task_status = flow.Computed()
    target_task_type = flow.Param(None, KitsuShotTaskType).watched()
    target_task_status = flow.Param('Work In Progress', KitsuTaskStatus)
    comment = flow.SessionParam('', PresetSessionValue).ui(editor='textarea')
    
    def __init__(self, parent, name):
        super(UploadPlayblastToKitsu, self).__init__(parent, name)
        self._kitsu_entity = None
    
    def _ensure_kitsu_entity(self):
        if self._kitsu_entity is None:
            kitsu_bindings = self.root().project().kitsu_bindings()
            file_settings = get_contextual_dict(self._file, 'settings')
            entity_data = kitsu_bindings.get_entity_data(file_settings)
            self._kitsu_entity = kitsu_bindings.get_kitsu_entity(entity_data)
        
        return self._kitsu_entity
    
    def allow_context(self, context):
        kitsu_config = self.root().project().kitsu_config()
        return (
            context
            and not self._file.is_empty(on_current_site=True)
            and kitsu_config.configured.get()
            and kitsu_config.is_uploadable(self._file.display_name.get())
        )
    
    def check_default_values(self):
        self.revision_name.revert_to_default()
        self.target_task_type.apply_preset()
        self.target_task_status.apply_preset()
        self.comment.apply_preset()
    
    def update_presets(self):
        self.target_task_type.update_preset()
        self.target_task_status.update_preset()
        self.comment.update_preset()
    
    def get_buttons(self):
        self.check_default_values()
        
        # message, buttons = self._get_message_and_buttons()
        # self.message.set(message)
        
        return ['Upload', 'Cancel']
    
    def _check_kitsu_params(self):
        # Check if the file is linked to a Kitsu entity
        task_type = self.target_task_type.get()
        kitsu_entity = self._ensure_kitsu_entity()
        
        msg = "<h2>Upload playblast to Kitsu</h2>"
        
        if kitsu_entity is None or task_type is None:
            msg += (
                "<h3><font color=#D5000D>The Kitsu entity %s belongs to "
                "couldn't be detected. Please contact the "
                "support on the chat.</font></h3>" % self._file.display_name.get()
            )
            self.message.set(msg)
            return False
        
        # Check if current user is assigned to a Kitsu task this file is made for
        kitsu_api = self.root().project().kitsu_api()
        user = kitsu_api.get_user_name()
        task = kitsu_api.get_task(kitsu_entity, task_type)
        
        if user is None:
            msg += (
                "<h3><font color=#D5000D>It seems you (%s) have no "
                "user profile on Kitsu. Please contact the "
                "support on the chat.</font></h3>" % self.root().project().get_user_name()
            )
            self.message.set(msg)
            return False
        
        if task is None:
            msg += (
                "<h3><font color=#D5000D>This file is not linked to any "
                "task on Kitsu.</font></h3>"
            )
            self.message.set(msg)
            return False
        
        # Check if user is assigned to the task or have sufficient rights
        is_assigned = kitsu_api.user_is_assigned(user, task)
        user_role = user.get('role', None)
        
        if not is_assigned:
            if not user_role in ['admin', 'manager']:
                msg += (
                    "<h3><font color=#D5000D>You (%s) are not assigned to "
                    "the task this file has been created for.</font></h3>"
                    % self.root().project().get_user_name()
                )
                self.message.set(msg)
                return False
            else:
                user_roles = {
                    'admin': 'studio manager',
                    'manager': 'supervisor'
                }
                msg += (
                    "<h3>As %s, you can upload a preview for this file.</h3>"
                    % user_roles[user_role]
                )

        self.message.set(msg)
        
        return True
    
    def child_value_changed(self, child_value):
        if child_value is self.target_task_type:
            self._check_kitsu_params()
            self.current_task_status.touch()
    
    def compute_child_value(self, child_value):
        kitsu_entity = self._ensure_kitsu_entity()
        
        if kitsu_entity is None:
            child_value.set(None)
            return
        
        kitsu_api = self.root().project().kitsu_api()
        
        if child_value is self.current_task_status:
            task_status = kitsu_api.get_task_current_status(
                kitsu_entity,
                self.target_task_type.get()
            )
            self.current_task_status.set(task_status)
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self.update_presets()

        if not self._check_kitsu_params():
            return self.get_result(close=False)
        
        kitsu_api = self.root().project().kitsu_api()
        kitsu_entity = self._ensure_kitsu_entity()
        
        if kitsu_entity is None:
            self.root().session().log_error('No Kitsu entity for file ' + self._file.oid())
            return self.get_result(close=False)
        
        revision = self._file.get_revision(self.revision_name.get())
        
        success = kitsu_api.upload_preview(
            kitsu_entity=kitsu_entity,
            task_type_name=self.target_task_type.get(),
            task_status_name=self.target_task_status.get(),
            file_path=revision.get_path(),
            comment=self.comment.get(),
        )
        
        if not success:
            self.message.set((
                "<h2>Upload playblast to Kitsu</h2>"
                "<font color=#D5000D>An error occured "
                "while uploading the preview.</font>"
            ))
            return self.get_result(close=False)
        
        if self.root().project().get_current_site().auto_upload_kitsu_playblasts.get():
            revision.upload.run('Confirm')


class RenderWithAfterEffect(GenericRunAction):
    
    ICON = ('icons.libreflow', 'afterfx')

    def get_buttons(self):
        return ["Render", "Cancel"]

    def runner_name_and_tags(self):
        return "AfterEffectsRender", []

    @classmethod
    def supported_extensions(cls):
        return ["aep"]
    
    def allow_context(self, context):
        return (
            context
            and self._file.format.get() in self.supported_extensions()
        )


class WaitProcess(LaunchSessionWorker):
    '''
    Launch a `SessionWorker` which waits for the process identified
    by the ID `pid` to end. It is up to the user of this action to set
    the latter param before the action runs.
    
    Since a `SessionWorker` runs in its own session, params of this class
    and its subclasses must be stored in the DB in order to remain
    accessible to the underlying subprocess.
    '''
    pid = flow.IntParam()
    
    def allow_context(self, context):
        return False
    
    def launcher_oid(self):
        return self.oid()
    
    def launcher_exec_func_name(self):
        return 'wait'
    
    def wait(self):
        pid = self.pid.get()
        
        if pid is None:
            raise Exception('A process ID must be explicitly set in the pid param.')
        
        # os.waitpid(pid, 0)
        while psutil.pid_exists(pid):
            time.sleep(1.0)
        
        # Reset pid for the next calls to this method
        self.pid.set(None)
        self._do_after_process_ends()
    
    def _do_after_process_ends(self):
        '''
        Subclasses may redefine this method to perform a particular
        processing after the subprocess ending.
        '''
        pass


class ZipFolder(WaitProcess):
    
    folder_path = flow.Param()
    output_path = flow.Param()
    
    def allow_context(self, context):
        return False
    
    def get_run_label(self):
        return 'Zip rendered images'
    
    def _do_after_process_ends(self):
        folder_path = self.folder_path.get()
        output_path = self.output_path.get()
        
        if os.path.exists(folder_path):
            zip_folder(self.folder_path.get(), self.output_path.get())


class MarkSequenceAfterRender(WaitProcess):
    
    folder_oid = flow.Param()
    revision_name = flow.Param()
    
    site_name = flow.Param().ui(hidden=True)
    user_name = flow.Param().ui(hidden=True)
    render_in_pool = flow.BoolParam(False).ui(hidden=True)
    pool = flow.Param().ui(hidden=True)
    
    def allow_context(self, context):
        return False
    
    def get_run_label(self):
        return 'Generate playblast'
    
    def _do_after_process_ends(self):
        folder = self.root().get_object(self.folder_oid.get())
        
        if self.render_in_pool.get():
            site_name = self.site_name.get()
            user_name = self.user_name.get()
            
            # Use the user and site of the current context if they have
            # not been set from elsewhere (e.g., another session)
            if site_name is None:
                site_name = self.root().project().get_current_site().name()
            if user_name is None:
                user_name = self.root().project().get_user_name()
            
            folder.submit_mark_sequence_job.revision_name.set(self.revision_name.get())
            folder.submit_mark_sequence_job.site_name.set(site_name)
            folder.submit_mark_sequence_job.user_name.set(user_name)
            folder.submit_mark_sequence_job.pool.set(self.pool.get())
            folder.submit_mark_sequence_job.run('Submit job')
        else:
            self.root().project().ensure_runners_loaded()
            folder.mark_image_sequence.revision_name.set(self.revision_name.get())
            folder.mark_image_sequence.run('Render')
        
        self.site_name.revert_to_default()
        self.user_name.revert_to_default()


def list_digits(s, _nsre=re.compile('([0-9]+)')):
    '''
    List all digits contained in a string
    '''
    return [int(text) for text in _nsre.split(s) if text.isdigit()]


class RenderImageSequence(RenderWithAfterEffect):

    _files = flow.Parent(2)
    revision = flow.Param(None, FileRevisionNameChoiceValue)

    def needs_dialog(self):
        return True

    def allow_context(self, context):
        return False
    
    def get_buttons(self):
        self.revision.revert_to_default()
        return ['Render', 'Cancel']
    
    def get_run_label(self):
        return 'Render image sequence'

    def extra_argv(self):
        settings = get_contextual_dict(self._file, 'settings')
        sequence_name = settings['sequence']
        shot_name = settings['shot']
        revision = self._file.get_revision(self.revision.get())
        
        project_path = revision.get_path()
        comp_name = sequence_name + '_' + shot_name
        output_name = comp_name + '.[####].exr'
        output_path = os.path.join(self._output_path, output_name)
        
        argv = [
            '-project', project_path,
            '-comp', comp_name,
            '-RStemplate', 'siren_compo_render',
            '-OMtemplate', 'siren_compo_output',
            '-output', output_path
        ]
        
        return argv
    
    def ensure_render_folder(self):
        folder_name = self._file.display_name.get().split('.')[0]
        folder_name += '_render'

        if not self._files.has_mapped_name(folder_name):
            self._files.create_folder.folder_name.set(folder_name)
            self._files.create_folder.run(None)
        
        return self._files[folder_name]
    
    def _ensure_render_folder_revision(self):
        folder = self.ensure_render_folder()
        revision_name = self.revision.get()
        revisions = folder.get_revisions()
        
        if not folder.has_revision(revision_name):
            revision = revisions.add(revision_name)
            revision.set_sync_status('Available')
            folder.set_current_user_on_revision(revision_name)
        else:
            revision = revisions[revision_name]
        
        self._files.touch()
        
        return revision
    
    def run(self, button):
        if button == 'Cancel':
            return

        revision = self._ensure_render_folder_revision()
        self._output_path = revision.path.get()
        
        # Ensure playblast revision folder exists and is empty
        if not os.path.exists(self._output_path):
            os.makedirs(self._output_path)
        else:
            remove_folder_content(self._output_path)

        return super(RenderImageSequence, self).run(button)


class MarkImageSequence(GenericRunAction):
    
    _folder = flow.Parent()
    _files = flow.Parent(2)
    _departments = flow.Parent(4)
    
    revision = flow.Param(None, FileRevisionNameChoiceValue)
    
    def runner_name_and_tags(self):
        return 'MarkSequenceRunner', []
    
    def get_run_label(self):
        return 'Generate playblast'
    
    def allow_context(self, context):
        return context and len(self._folder.get_revision_names(sync_status='Available')) > 0
    
    def needs_dialog(self):
        return True
    
    def get_buttons(self):
        self.revision.revert_to_default()
        return ['Render', 'Cancel']
    
    def extra_argv(self):
        argv = super(MarkImageSequence, self).extra_argv()
        
        settings = get_contextual_dict(self, 'settings')
        category = settings['file_category']
        
        if category != 'PROD':
            return argv
        
        argv += [
            '-o', self._extra_argv['video_output'],
            '-t', resources.get('mark_sequence.fields', 'compositing.json'),
            '--project', settings['film'],
            '--sequence', list_digits(settings['sequence'])[0],
            '--scene', settings['shot'],
            '--version', self.revision.get(),
            '--studio', self.root().project().get_current_site().name(),
            '--file-name', self._extra_argv['file_name'],
            '--frame_rate', 24.0,
            self._extra_argv['image_path']
        ]
        
        audio_path = self._extra_argv['audio_file']
        
        if audio_path is not None:
            argv += ['--audio-file', audio_path]
        
        return argv
    
    def _ensure_file_revision(self, name, extension, revision_name):
        mapped_name = name + '_' + extension
        
        if not self._files.has_mapped_name(mapped_name):
            self._files.create_file.file_name.set(name)
            self._files.create_file.file_format.set(extension)
            self._files.create_file.run(None)
        
        file = self._files[mapped_name]
        revisions = file.get_revisions()
        
        if not file.has_revision(revision_name):
            revision = revisions.add(revision_name)
            revision.set_sync_status('Available')
            file.set_current_user_on_revision(revision_name)
        else:
            revision = revisions[revision_name]
        
        return revision
    
    def _get_first_image_path(self, revision_name):
        revision = self._folder.get_revision(revision_name)
        img_folder_path = revision.path.get()
        
        for f in os.listdir(img_folder_path):
            file_path = os.path.join(img_folder_path, f)
            file_type = mimetypes.guess_type(file_path)[0].split('/')[0]
            
            if file_type == 'image':
                return file_path
        
        return None
    
    def _get_audio_path(self):
        audio_path = None

        if self._departments.misc.files.has_mapped_name('audio_wav'):
            audio_file = self._departments.misc.files['audio_wav']
            revision = audio_file.get_head_revision()
            
            if revision is not None:
                audio_path = revision.get_path()
        
        return audio_path
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        revision_name = self.revision.get()
        
        # Compute playblast prefix
        prefix = self._folder.name()
        prefix = prefix.replace('_render', '')
        
        source_revision = self._file.get_revision(revision_name)
        revision = self._ensure_file_revision(prefix + '_movie', 'mov', revision_name)
        revision.comment.set(source_revision.comment.get())
        
        # Get the path of the first image in folder
        img_path = self._get_first_image_path(revision_name)
        
        # Get original file name to print on frames
        if self._files.has_mapped_name(prefix + '_aep'):
            scene = self._files[prefix + '_aep']
            file_name = scene.complete_name.get() + '.' + scene.format.get()
        else:
            file_name = self._folder.complete_name.get()
        
        self._extra_argv = {
            'image_path': img_path,
            'video_output': revision.get_path(),
            'file_name': file_name,
            'audio_file': None
        }
        
        return super(MarkImageSequence, self).run(button)


class MarkImageSequenceWaiting(WaitProcess):

    _file = flow.Parent()
    _files = flow.Parent(2)
    
    folder_name = flow.Param()
    revision_name = flow.Param()

    def _do_after_process_ends(self):
        # Mark image sequence in provided folder
        self.root().project().ensure_runners_loaded()
        sequence_folder = self._files[self.folder_name.get()]
        sequence_folder.mark_image_sequence.revision.set(self.revision_name.get())
        sequence_folder.mark_image_sequence.run('Render')


class RenderImageSequenceJob(FileJob):

    _file = flow.Parent(2)
    revision_name = flow.Param()

    def _do_job(self):
        revision_name = self.revision_name.get()
        render_image_seq = self._file.render_image_sequence
        render_image_seq.revision.set(revision_name)
        ret = render_image_seq.run('Render')
        rid = ret['runner_id']

        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message('[RUNNER] Runner %s started...' % rid)
        self.show_message('[RUNNER] Description: %s - %s %s' % (runner_info['label'], self._file.oid(), revision_name))
        self.show_message('[RUNNER] Command: %s' % runner_info['command'])

        while runner_info['is_running']:
            time.sleep(1)
            runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message('[RUNNER] Runner %s finished' % rid)


class MarkImageSequenceJob(FileJob):

    _folder = flow.Parent(2)
    revision_name = flow.Param()

    def _do_job(self):
        revision_name = self.revision_name.get()
        mark_image_seq = self._folder.mark_image_sequence
        mark_image_seq.revision.set(revision_name)
        ret = mark_image_seq.run('Render')
        rid = ret['runner_id']

        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message('[RUNNER] Runner %s started...' % rid)
        self.show_message('[RUNNER] Description: %s - %s %s' % (runner_info['label'], self._file.oid(), revision_name))
        self.show_message('[RUNNER] Command: %s' % runner_info['command'])

        while runner_info['is_running']:
            time.sleep(1)
            runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message('[RUNNER] Runner %s finished' % rid)


class RenderAEPlayblast(flow.Action):

    ICON = ('icons.libreflow', 'afterfx')

    _file = flow.Parent()
    revision = flow.Param(None, FileRevisionNameChoiceValue)

    def get_buttons(self):
        self.revision.revert_to_default()
        return ['Render', 'Cancel']
    
    def allow_context(self, context):
        return False
    
    def _render_image_sequence(self, revision_name):
        render_image_seq = self._file.render_image_sequence
        render_image_seq.revision.set(revision_name)
        ret = render_image_seq.run('Render')

        return ret
    
    def _mark_image_sequence(self, folder_name, revision_name, wait_pid):
        mark_sequence_wait = self._file.mark_image_sequence_wait
        mark_sequence_wait.folder_name.set(folder_name)
        mark_sequence_wait.revision_name.set(revision_name)
        mark_sequence_wait.pid.set(wait_pid)
        mark_sequence_wait.run(None)
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        revision_name = self.revision.get()
        
        # Render image sequence
        ret = self._render_image_sequence(revision_name)
        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(ret['runner_id'])
        
        # Configure image sequence marking
        folder_name = self._file.name()[:-len(self._file.format.get())]
        folder_name += 'render'
        self._mark_image_sequence(folder_name, revision_name, runner_info['pid'])


class SubmitRenderAEPlayblast(flow.Action):

    ICON = ('icons.libreflow', 'afterfx')

    _file = flow.Parent()
    revision = flow.Param(None, FileRevisionNameChoiceValue)
    pool = flow.Param('default', SiteJobsPoolNames)

    def get_buttons(self):
        self.revision.revert_to_default()
        self.pool.apply_preset()

        return ['Submit', 'Cancel']
    
    def allow_context(self, context):
        return False
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        # Update pool preset
        self.pool.update_preset()

        # Create rendering and marking jobs
        revision_name = self.revision.get()
        render_job = self._file.jobs.create_job(job_type=RenderImageSequenceJob)
        render_job.revision_name.set(revision_name)

        # Ensure render folder exists to generate marking job
        render_folder = self._file.render_image_sequence.ensure_render_folder()
        mark_job = render_folder.jobs.create_job(job_type=MarkImageSequenceJob)
        mark_job.revision_name.set(revision_name)

        site_name = self.root().project().admin.multisites.current_site_name.get()
        user_name = self.root().project().get_user_name()

        render_job.submit(
            pool=site_name + '_' + self.pool.get(),
            priority=10,
            label='Render image sequence - %s (%s)' % (self._file.oid(), revision_name),
            creator=user_name,
            owner=user_name,
            paused=True,
            show_console=False,
        )

        mark_job.submit(
            pool=site_name + '_' + self.pool.get(),
            priority=10,
            label='Mark image sequence - %s (%s)' % (self._file.oid(), revision_name),
            creator=user_name,
            owner=user_name,
            paused=True,
            show_console=False,
        )

        # Configure render job to resume marking job when it finishes
        render_job.add_child(mark_job.job_id.get())
        # Resume render job
        self.root().session().cmds.Jobs.set_job_paused(render_job.job_id.get(), False)


class SelectAEPlayblastRenderMode(flow.Action):

    ICON = ('icons.libreflow', 'afterfx')

    _file = flow.Parent()
    revision = flow.Param(None, FileRevisionNameChoiceValue)

    def get_buttons(self):
        self.revision.revert_to_default()
        return ['Render', 'Submit job', 'Cancel']
    
    def allow_context(self, context):
        return context and self._file.format.get() == 'aep'
    
    def run(self, button):
        if button == 'Cancel':
            return
        elif button == 'Render':
            render_action = self._file.render_ae_playblast
            render_action.revision.set(self.revision.get())
            render_action.run('Render')
        else:
            submit_action = self._file.submit_ae_playblast
            submit_action.revision.set(self.revision.get())
            return self.get_result(next_action=submit_action.oid())


class RequestTrackedFileAction(flow.Action):

    _file = flow.Parent()
    _files = flow.Parent(2)

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return False
    
    def run(self, button):
        head = self._file.get_head_revision()
        exchange_site_name = self.root().project().get_exchange_site().name()

        if not head or head.get_sync_status() != "NotAvailable" or head.get_sync_status(site_name=exchange_site_name) != "Available":
            return
        
        head.request.sites.target_site.set(
            self.root().project().get_current_site().name()
        )
        head.request.run(None)
        self._files.touch()


class TrackedFile(File):

    ICON = ("icons.gui", "text-file-1")

    _map = flow.Parent()
    
    locked_by = Property().ui(editable=False)

    history = flow.Child(History)
    current_revision = flow.Param("").ui(editable=False)
    last_revision_oid = Property().ui(editable=False)

    active_users = flow.Child(ActiveUsers)
    current_user_sees = flow.Computed()

    jobs = flow.Child(FileJobs)

    show_history = flow.Child(GotoHistory)
    publish_action = flow.Child(PublishFileAction).injectable().ui(label="Publish")
    publish_and_playblast_blender = flow.Child(PublishAndRenderBlenderPlayblast).ui(label='Publish and playblast')
    publish_and_playblast_ae = flow.Child(PublishAndRenderAEPlayblast).ui(label='Publish and playblast')
    create_working_copy_action = flow.Child(CreateWorkingCopyAction).ui(
        label="Create working copy"
    )
    open = flow.Child(OpenTrackedFileAction)
    reveal = flow.Child(RevealInExplorer).ui(label="Reveal in explorer")
    request = flow.Child(RequestTrackedFileAction)
    upload_playblast = flow.Child(UploadPlayblastToKitsu).ui(label='Upload to Kitsu')

    with flow.group("Advanced"):
        create_working_copy_from_file = flow.Child(None).ui(label="Create working copy from another file")
        publish_into_file = flow.Child(None).ui(label="Publish to another file")

        # Blender
        render_blender_playblast = flow.Child(RenderBlenderPlayblast).ui(label='Render playblast')
        submit_blender_playblast_job = flow.Child(SubmitBlenderPlayblastJob)

        # AfterEffects
        select_ae_playblast_render_mode = flow.Child(SelectAEPlayblastRenderMode).ui(label='Render playblast')
        render_image_sequence = flow.Child(RenderImageSequence).ui(label='Render image sequence')

        # Options hidden by default
        render_ae_playblast = flow.Child(RenderAEPlayblast)
        submit_ae_playblast = flow.Child(SubmitRenderAEPlayblast)
        mark_image_sequence_wait = flow.Child(MarkImageSequenceWaiting)

    def get_name(self):
        return "%s_%s" % (self.complete_name.get(), self.format.get())
    
    def get_default_path(self):
        return os.path.join(
            self._map.get_parent_path(), self.name()
        )

    def create(self):
        os.makedirs(self.get_path())

    def remove(self):
        shutil.rmtree(self.get_path())
    
    def configure(self, format, complete_name, display_name):
        super(TrackedFile, self).configure(format, complete_name, display_name)
        self.locked_by.set(None)

    def is_locked(self, by_current_user=False):
        if by_current_user:
            return self.locked_by.get() == self.root().project().get_user_name()

        return self.locked_by.get() is not None

    def lock(self):
        self.locked_by.set(self.root().project().get_user_name())

    def unlock(self):
        self.locked_by.set(None)

    def has_working_copy(self, from_current_user=False):
        if from_current_user:
            user = self.root().project().get_user_name()
            return user in self.get_revisions().mapped_names()

        for revision in self.get_revisions().mapped_items():
            if revision.is_working_copy():
                return True

        return False

    def set_current_user_on_revision(self, revision_name):
        current_user = self.root().project().get_user_name()
        self.set_user_on_revision(current_user, revision_name)

    def set_user_on_revision(self, user_name, revision_name):
        if self.has_active_user(user_name):
            active_user = self.active_users[user_name]
        else:
            active_user = self.active_users.add(user_name)

        active_user.set(revision_name)
        self.get_revisions().touch()

    def remove_active_user(self, user_name):
        self.active_users.remove(user_name)

    def has_active_user(self, user_name):
        return user_name in self.active_users.mapped_names()

    def get_seen_revision(self):
        name = self.current_user_sees.get()

        if name == "current":
            if self.has_current_revision():
                return self.get_current_revision()
            else:
                return None
        else:
            return self.get_revision(name)

    def has_current_revision(self):
        return bool(self.current_revision.get())

    def get_revision(self, name):
        return self.history.revisions[name]

    def get_revisions(self):
        return self.history.revisions
    
    def get_working_copies(self, sync_status=None):
        working_copies = []
        
        for r in self.get_revisions().mapped_items():
            if not r.is_working_copy() or r.is_working_copy(from_current_user=True):
                continue
            
            if sync_status is None or r.get_sync_status() == sync_status:
                working_copies.append(r)
        
        return working_copies
    
    def get_revision_names(self, sync_status=None, published_only=False):
        if sync_status is None and not published_only:
            return self.get_revisions().mapped_names()

        revisions = self.get_revisions().mapped_items()

        if published_only:
            revisions = filter(lambda r: not r.is_working_copy(), revisions)

        if sync_status is not None:
            revisions = filter(lambda r: r.get_sync_status() == sync_status, revisions)
        
        return [r.name() for r in revisions]
    
    def get_revision_statuses(self, published_only=False):
        revisions = self.get_revisions().mapped_items()
        
        if published_only:
            revisions = filter(lambda r: not r.is_working_copy(), revisions)
        
        return [(r.name(), r.get_sync_status()) for r in revisions]

    def has_revision(self, name, sync_status=None):
        exists = (name in self.history.revisions.mapped_names())

        if exists and sync_status:
            exists = exists and (self.history.revisions[name].get_sync_status() == sync_status)
        
        return exists

    def is_empty(self, on_current_site=True):
        revisions = self.get_revisions()
        empty = not bool(revisions.mapped_names())
        
        if not on_current_site:
            return empty
        
        for r in revisions.mapped_items():
            if r.get_sync_status() == 'Available':
                return False
        
        return empty

    def get_last_edit_time(self):
        seen_name = self.current_user_sees.get()
        current = self.get_current_revision()

        if seen_name == "current":
            if current is None:
                if os.path.exists(self.get_path()):
                    return os.path.getmtime(self.get_path())
                else:
                    return 0
            else:
                return current.get_last_edit_time()
        else:
            seen = self.get_revision(seen_name)
            return seen.get_last_edit_time()

    def get_last_comment(self):
        seen_name = self.current_user_sees.get()
        current = self.get_current_revision()

        if seen_name == "current":
            if current is None:
                return "NO PUBLISH YET"
            else:
                return current.comment.get()
        else:
            seen = self.get_revision(seen_name)

            if seen.is_working_copy():
                return "WORKING COPY (%s)" % seen.user.get()
            else:
                return seen.comment.get()

    def create_working_copy(self, reference_name=None, source_path=None, user_name=None, path_format=None):
        if user_name is None:
            user_name = self.root().project().get_user_name()

        revisions = self.get_revisions()
        working_copy = self.get_working_copy()

        # Overwrite current working copy
        if working_copy is not None:
            if working_copy.exists():
                os.remove(working_copy.get_path())

            revisions.remove(working_copy.name())
        
        working_copy = revisions.add(
            user_name,
            is_working_copy=True,
            ready_for_sync=False,
            path_format=path_format
        )
        # Ensure parent folder exists
        os.makedirs(
            os.path.dirname(working_copy.get_path()),
            exist_ok=True
        )

        if source_path is None:
            source_path = self.get_template_path()

            if reference_name is not None:
                reference = self.get_revision(reference_name)

                if reference is None or reference.get_sync_status() != 'Available':
                    self.root().session().log_error(
                        f'Revision {reference_name} undefined or unavailable '
                        'on the current site. The created working copy will be empty.'
                    )
                else:
                    source_path = reference.get_path()

        shutil.copy2(source_path, working_copy.get_path())

        revisions.touch()
        self._map.touch()

        return working_copy

    def publish(self, revision_name=None, source_path=None, comment="", keep_editing=False, ready_for_sync=True, path_format=None):
        revisions = self.get_revisions()
        head_revision = revisions.add(
            revision_name,
            ready_for_sync=ready_for_sync,
            comment=comment,
            path_format=path_format
        )

        # Ensure parent folder exists
        os.makedirs(
            os.path.dirname(head_revision.get_path()),
            exist_ok=True
        )

        # If source path is given, ignore working copy
        if source_path is not None:
            if os.path.exists(source_path):
                shutil.copy2(source_path, head_revision.get_path())
            else:
                self.root().session().log_error(
                    f'Source file {source_path} does not exist.'
                )
        else:
            working_copy = self.get_working_copy()

            if keep_editing:
                shutil.copy2(
                    working_copy.get_path(),
                    head_revision.get_path()
                )
            else:
                shutil.move(
                    working_copy.get_path(),
                    head_revision.get_path()
                )
                # TODO: find a way to remove working copy's potential subdirectories
                revisions.remove(working_copy.name())

        # Compute published revision hash
        head_revision.compute_hash_action.run(None)
        self.last_revision_oid.set(head_revision.oid())

        revisions.touch()
        self._map.touch()

        return head_revision

    def make_current(self, revision):
        self.current_revision.set(revision.name())
        self.get_revisions().touch()

    def get_working_copy(self, user_name=None):
        if user_name is None:
            user_name = self.root().project().get_user_name()
        try:
            return self.get_revision(user_name)
        except flow.exceptions.MappedNameError:
            return None

    def get_head_revision(self, sync_status=None):
        revisions = self.get_revisions()

        for revision in reversed(revisions.mapped_items()):
            if not revision.is_working_copy() and (not sync_status or revision.get_sync_status() == sync_status):
                return revision

        return None

    def get_current_revision(self):
        try:
            return self.get_revision(self.current_revision.get())
        except flow.exceptions.MappedNameError:
            return None
    
    def to_upload_after_publish(self):
        auto_upload_files = self.root().project().admin.project_settings.get_auto_upload_files()

        for pattern in auto_upload_files:
            if fnmatch.fnmatch(self.display_name.get(), pattern):
                return True
        
        return False

    def compute_child_value(self, child_value):
        current_user = self.root().project().get_user_name()

        if child_value is self.current_user_sees:
            try:
                child_value.set(self.active_users[current_user].get())
            except flow.exceptions.MappedNameError:
                child_value.set("current")
        else:
            super(TrackedFile, self).compute_child_value(child_value)


class FileRefRevisionNameChoiceValue(FileRevisionNameChoiceValue):

    def get_file(self):
        return self.action.source_file.get()


class ResetRef(flow.Action):

    _ref = flow.Parent()

    def allow_context(self, context):
        return context and context.endswith(".inline")
    
    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._ref.set(None)
        return self.get_result(refresh=True)


class ResetableTrackedFileRef(flow.values.Ref):

    SOURCE_TYPE = TrackedFile
    reset = flow.Child(ResetRef)


class PublishIntoFile(PublishFileAction):

    source_file = flow.SessionParam("").ui(
        editable=False,
        tooltip="File to publish to.",
    )
    source_revision_name = flow.Param(None, FileRevisionNameChoiceValue).watched().ui(
        label="Source revision"
    )
    target_file = flow.Connection(ref_type=ResetableTrackedFileRef).watched()
    revision_name = flow.Param("").watched()
    comment = flow.Param("", PresetValue)
    keep_editing = flow.SessionParam(True, PresetSessionValue).ui(hidden=True)
    upload_after_publish = flow.Param(False, UploadAfterPublishValue).ui(editor='bool')

    def get_buttons(self):
        self.message.set("<h2>Publish from an existing file</h2>")
        self.target_file.set(None)
        self.source_file.set(self._file.display_name.get())
        self.source_revision_name.revert_to_default()

        self.check_default_values()

        return ["Publish", "Cancel"]

    def allow_context(self, context):
        return None

    def check_file(self, file):
        expected_format = self._file.format.get()
        msg = "<h2>Publish from an existing file</h2>"
        error_msg = ""

        if not file:
            error_msg = "A target file must be set."
        elif file.format.get() != expected_format:
            error_msg = f"Target file must be in {expected_format} format."
        elif not self.source_revision_name.choices():
            error_msg = f"Target file has no revision available on current site."
        
        if error_msg:
            self.message.set(
                f"{msg}<font color=#D5000D>{error_msg}</font>"
            )
            return False
        
        # Check if other users are editing the target file
        working_copies = file.get_working_copies()
        if working_copies:
            user_names = [wc.user.get() for wc in working_copies]
            user_names = ["<b>"+n+"</b>" for n in user_names]
            msg += (
                "<h3><font color=#D66500><br>"
                "Target file <b>%s</b> is currently being edited by one or more users (%s)."
                "</font></h3>"
                % (file.display_name.get(), ', '.join(user_names))
            )
        
        self.message.set(msg)
        return True
    
    def check_revision_name(self, name):
        msg = self.message.get()
        target_file = self.target_file.get()

        if not self.check_file(target_file):
            return False

        if target_file.has_revision(name):
            msg += (
                "<font color=#D5000D>"
                f"Target file already has a revision {name}."
                "</font>"
            )
            self.message.set(msg)

            return False
        
        self.message.set(msg)
        return True
    
    def _target_file(self):
        return self.target_file.get()
    
    def _revision_to_process(self):
        revision_name = self.revision_name.get()
        if not revision_name:
            revision_name = self.source_revision_name.get()

        return self._target_file().get_revision(revision_name)

    def child_value_changed(self, child_value):
        self.message.set("<h2>Publish from an existing file</h2>")

        if child_value is self.target_file:
            self.check_file(self.target_file.get())
            self.check_revision_name(self.source_revision_name.get())
        elif child_value is self.source_revision_name:
            value = self.source_revision_name.get()
            self.revision_name.set(value)
            self.comment.set("Created from %s (%s)" % (
                self._file.display_name.get(),
                value,
            ))
        elif child_value is self.revision_name:
            revision_name = self.revision_name.get()
            self.check_revision_name(revision_name)

    def run(self, button):
        if button == "Cancel":
            return

        target_file = self.target_file.get()

        # Check source file
        if not self.check_file(target_file):
            return self.get_result(close=False)
        
        revision_name = self.revision_name.get()
        if not revision_name:
            revision_name = self.source_revision_name.get()
        
        # Check choosen revision name
        if not self.check_revision_name(revision_name):
            return self.get_result(close=False)
        
        source_revision_name = self.source_revision_name.get()
        source_revision = self._file.get_revision(source_revision_name)
        
        # Publish in target file
        target_file.lock()

        publication = target_file.publish(
            revision_name=revision_name,
            source_path=source_revision.get_path(),
            comment=self.comment.get(),
        )
        target_file.make_current(publication)
        target_file.unlock()
        target_file._map.touch()

        if self.upload_after_publish.get():
            super(PublishFileAction, self).run(None)


class CreateWorkingCopyFromFile(flow.Action):

    ICON = ('icons.libreflow', 'edit-blank')

    _file = flow.Parent()
    source_file = flow.Connection(ref_type=ResetableTrackedFileRef).watched()
    source_revision_name = flow.Param(None, FileRefRevisionNameChoiceValue).ui(
        label="Source revision"
    )
    target_file = flow.SessionParam("").ui(
        editable=False,
        tooltip="File in which the working copy will be created.",
    )

    def get_buttons(self):
        msg = "<h2>Create working copy from another file</h2>"
        self.source_file.set(None)
        self.target_file.set(self._file.display_name.get())

        if self._file.has_working_copy(from_current_user=True):
            msg += (
                "<font color=#D66700>"
                "You already have a working copy on %s. "
                "Creating a working copy will overwrite the current one."
                "</font><br>" % self._file.display_name.get()
            )
        else:
            msg += "<br>"
        
        self.message.set(msg)

        return ["Create", "Cancel"]

    def allow_context(self, context):
        return context and self._file.editable()
    
    def child_value_changed(self, child_value):
        if child_value is self.source_file:
            self.check_file(self.source_file.get())

            self.source_revision_name.touch()
            self.source_revision_name.revert_to_default()

    def check_file(self, file):
        expected_format = self._file.format.get()
        msg = "<h2>Create working copy from another file</h2>"
        error_msg = ""

        if self._file.has_working_copy(from_current_user=True):
            msg += (
                "<font color=#D66700>"
                "You already have a working copy on %s. "
                "Creating a working copy will overwrite the current one."
                "</font><br>" % self._file.display_name.get()
            )
        else:
            msg += "<br>"

        if not file:
            error_msg = "A source file must be set."
        elif file.format.get() != expected_format:
            error_msg = f"Source file must be in {expected_format} format."
        elif not self.source_revision_name.choices():
            error_msg = f"Source file has no revision available on current site."
        
        if error_msg:
            self.message.set(
                f"{msg}<font color=#D5000D>{error_msg}</font>"
            )
            return False

        self.message.set(msg + "<br><br>")
        
        return True
    
    def run(self, button):
        if button == "Cancel":
            return

        source_file = self.source_file.get()

        if not self.check_file(source_file):
            return self.get_result(close=False)
        
        source_revision = source_file.get_revision(self.source_revision_name.get())
        working_copy = self._file.create_working_copy(source_path=source_revision.get_path())

        self._file.set_current_user_on_revision(working_copy.name())
        self._file.touch()
        self._file.get_revisions().touch()


TrackedFile.create_working_copy_from_file.set_related_type(CreateWorkingCopyFromFile)
TrackedFile.publish_into_file.set_related_type(PublishIntoFile)


class ClearFileSystemMapAction(ClearMapAction):
    def run(self, button):
        for item in self._map.mapped_items():
            if hasattr(item, "state") and hasattr(item, "current_user_sees"):
                item.get_revisions().clear()
                item.current_revision.set("")
                item.active_users.clear()

        super(ClearFileSystemMapAction, self).run(button)


class Folder(FileSystemItem):

    open = flow.Child(RevealInExplorer).ui(icon=('icons.gui', 'open-folder'))

    def create(self):
        os.makedirs(self.get_path())

    def remove(self):
        shutil.rmtree(self.get_path())
    
    def get_icon(self, extension=None):
        return ('icons.gui', 'folder-white-shape')


class OpenTrackedFolderRevision(RevealInExplorer):

    _revision = flow.Parent()

    def extra_argv(self):
        return [self._revision.get_path()]
    
    def allow_context(self, context):
        return context and self._revision.exists()
    
    def needs_dialog(self):
        return (
            self._revision.get_sync_status() != 'Available'
            or not self._revision.exists()
        )
    
    def get_buttons(self):
        if self._revision.get_sync_status() != 'Available':
            self.message.set((
                '<h2>Unavailable revision</h2>'
                'This revision is not available on the current site.'
            ))
        else:
            self.message.set((
                '<h2>Missing revision</h2>'
                'This revision does not exist on the current site.'
            ))
        return ['Close']
    
    def run(self, button):
        if button == 'Close':
            return
        
        super(OpenTrackedFolderRevision, self).run(button)


class TrackedFolderRevision(Revision):

    open = flow.Child(OpenTrackedFolderRevision)

    def _get_default_suffix(self):
        return self.name()
    
    def _compute_path(self, path_format):
        kwords = keywords_from_format(path_format)
        settings = get_contextual_dict(self, 'settings')
        values = {}
        for kword in kwords:
            values[kword] = settings.get(kword, '')
        
        return path_format.format(**values)
    
    def compute_hash(self):
        return hash_folder(self.get_path())


class TrackedFolderRevisions(Revisions):

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(TrackedFolderRevision)


class TrackedFolderHistory(History):

    revisions = flow.Child(TrackedFolderRevisions).injectable()


class OpenTrackedFolderAction(flow.Action):

    ICON = ('icons.gui', 'open-folder')

    _folder = flow.Parent()

    revision = flow.Param(None, RevisionsChoiceValue)
    
    def get_buttons(self):
        self.revision.revert_to_default()

        if not self._folder.editable():
            self.message.set('<h2>Read-only folder</h2>')
            buttons = ['Open revision', 'Cancel']
        elif self._folder.is_empty():
            self.message.set((
                '<h2>Empty folder</h2>'
                'This folder does not have any revision. '
                'You can create a working copy to start editing it.'
            ))
            buttons = ['Create a working copy', 'Cancel']
        elif self._folder.is_empty(on_current_site=True):
            self.message.set((
                '<h2>Unedited folder</h2>'
                'This folder has no revision available on the current site. '
                'You can create a working copy to start editing it.'
            ))
            buttons = ['Create a working copy', 'Cancel']
        elif not self._folder.has_working_copy(from_current_user=True):
            self.message.set((
                '<h2>Read-only mode</h2>'
                'You are about to open this folder in read-only mode. '
                'If you want to edit it, you can create one a working copy.'
            ))
            buttons = ['Open revision', 'Create a working copy', 'Cancel']
        else:
            buttons = ['Open revision', 'Create a working copy', 'Cancel']

        return buttons

    def needs_dialog(self):
        return (
            not self._folder.editable()
            or self._folder.is_empty(on_current_site=True)
            or not self._folder.has_working_copy(from_current_user=True)
        )
    
    def run(self, button):
        if button == 'Cancel':
            return
        elif button == 'Open revision':
            revision = self._folder.get_revision(self.revision.get())
            revision.open.run(None)
        elif button == 'Create a working copy':
            if self._folder.is_empty():
                working_copy = self._folder.create_working_copy()
            else:
                working_copy = self._folder.create_working_copy(
                    reference_name=self.revision.get()
                )
            working_copy.open.run(None)
        else: # Working copy exists
            working_copy = self._folder.get_working_copy()
            working_copy.open.run(None)


class FolderAvailableRevisionName(FileRevisionNameChoiceValue):

    action = flow.Parent()

    def get_file(self):
        return self.action._folder


class ResizeTrackedFolderImages(RunAction):
    '''
    Computes half-resized versions of all PNG images contained in a source tracked folder
    in another tracked folder suffixed with `_half`.
    '''
    _folder = flow.Parent()
    _files = flow.Parent(2)
    revision_name = flow.Param(None, FolderAvailableRevisionName).watched()
    publish_comment = flow.SessionParam("")

    def runner_name_and_tags(self):
        return 'ImageMagick', []
    
    def get_run_label(self):
        return 'Resize images'
    
    def extra_argv(self):
        in_pattern = '{}/*.png[{}]'.format(self._source_folder_path, self._resize_format)
        out_pattern = '{}/%[filename:base].png'.format(self._target_folder_path)
        return ['convert', in_pattern, '-set', 'filename:base', '%[basename]', out_pattern]
    
    def get_buttons(self):
        self.message.set((
            "<h2>Resize images in {0}</h2>"
            "Every PNG image included in this folder will have a resized version placed in the <b>{0}_half</b> folder.".format(
                self._folder.name()
            )
        ))
        self.revision_name.revert_to_default()

        return ['Resize images', 'Cancel']
    
    def child_value_changed(self, child_value):
        if child_value is self.revision_name:
            self.publish_comment.set(
                "Half-resized images from %s folder" % self._folder.name()
            )
    
    def _get_image_dimensions(self, img_path):
        exec_path = self.root().project().admin.user_environment['IMAGEMAGICK_EXEC_PATH'].get()
        
        dims = subprocess.check_output([exec_path, 'convert', img_path, '-format', '%wx%h', 'info:'])
        dims = dims.decode('UTF-8').split('x')

        return tuple(map(int, dims))
    
    def run(self, button):
        if button == 'Cancel':
            return

        # Setup target folder
        target_folder_name = self._folder.name() + '_half'
        
        if not self._files.has_mapped_name(target_folder_name):
            self._files.create_folder.folder_name.set(target_folder_name)
            self._files.create_folder.run(None)
        
        target_folder = self._files[target_folder_name]
        publication = target_folder.publish(
            revision_name=self.revision_name.get(),
            source_path=self._folder.get_revision(self.revision_name.get()).path.get(),
            comment=self.publish_comment.get()
        )

        # Cache source and target folder paths
        self._source_folder_path = self._folder.get_revision(self.revision_name.get()).path.get()
        self._target_folder_path = publication.path.get()
        
        # Get dimensions of the first image
        image_paths = glob.glob("%s/*.png" % self._source_folder_path)
        width, height = self._get_image_dimensions(image_paths[0])

        # Cache dimensions
        if height > width:
            self._resize_format = "x%s" % min(int(0.5 * height), 3840)
        else:
            self._resize_format = "%sx" % min(int(0.5 * width), 3840)
        
        super(ResizeTrackedFolderImages, self).run(button)

        self._files.touch()


class TrackedFolder(TrackedFile):

    open = flow.Child(OpenTrackedFolderAction)
    history = flow.Child(TrackedFolderHistory)
    resize_images = flow.Child(ResizeTrackedFolderImages).ui(group='Advanced')
    # mark_image_sequence = flow.Child(MarkSequence).ui(group='Advanced')
    mark_image_sequence = flow.Child(MarkImageSequence).ui(
        group='Advanced',
        label='Mark image sequence')
    # submit_mark_sequence_job = flow.Child(SubmitMarkSequenceJob).ui(group='Advanced', hidden=True)
    
    def get_name(self):
        return self.complete_name.get()
    
    def get_icon(self, extension=None):
        return ('icons.gui', 'folder-white-shape')
    
    def create_working_copy(self, reference_name=None, user_name=None, path_format=None):
        if user_name is None:
            user_name = self.root().project().get_user_name()

        revisions = self.get_revisions()
        working_copy = self.get_working_copy()

        # TODO: Don't use os.path.dirname
        # Required here since folders are identified as zip files for synchronisation
        if working_copy is not None:
            if working_copy.exists():
                shutil.rmtree(working_copy.get_path())
            
            revisions.remove(working_copy.name())
        
        working_copy = revisions.add(
            user_name,
            is_working_copy=True,
            ready_for_sync=False,
            path_format=path_format
        )
        wc_dir_path = working_copy.get_path()

        # Ensure parent folder exists
        os.makedirs(
            os.path.dirname(wc_dir_path),
            exist_ok=True
        )

        if reference_name is not None:
            reference = self.get_revision(reference_name)

            if reference is None or reference.get_sync_status() != 'Available':
                self.root().session().log_error(
                    f'Revision {reference_name} undefined or unavailable '
                    'on the current site. The created working copy will be empty.'
                )
            else:
                shutil.copytree(
                    reference.get_path(), wc_dir_path
                )
        else:
            # Create an empty working copy folder
            os.mkdir(wc_dir_path)
        
        revisions.touch()
        self._map.touch()

        return working_copy

    def publish(self, revision_name=None, source_path=None, comment="", keep_editing=False, ready_for_sync=True, path_format=None):
        revisions = self.get_revisions()
        head_revision = revisions.add(
            revision_name,
            ready_for_sync=ready_for_sync,
            comment=comment,
            path_format=path_format
        )

        if source_path is not None:
            if os.path.exists(source_path):
                shutil.copytree(
                    source_path, head_revision.get_path()
                )
            else:
                self.root().session().log_error(
                    f'Source file {source_path} does not exist.'
                )
        else:
            working_copy = self.get_working_copy()
            
            if keep_editing:
                shutil.copytree(
                    working_copy.get_path(),
                    head_revision.get_path()
                )
            else:
                shutil.move(
                    working_copy.get_path(),
                    head_revision.get_path()
                )
                revisions.remove(working_copy.name())

        # Compute published revision hash
        head_revision.compute_hash_action.run(None)
        self.last_revision_oid.set(head_revision.oid())

        revisions.touch()
        self._map.touch()

        return head_revision

    def make_current(self, revision):
        self.current_revision.set(revision.name())
        self.get_revisions().touch()
    
    def to_upload_after_publish(self):
        auto_upload_files = self.root().project().admin.project_settings.get_auto_upload_files()

        for pattern in auto_upload_files:
            if fnmatch.fnmatch(self.name(), pattern):
                return True
        
        return False

    def compute_child_value(self, child_value):
        if child_value is self.display_name:
            child_value.set(self.name())
        else:
            TrackedFile.compute_child_value(self, child_value)


mapping = {r.name: r.index for r in TrackedFile._relations}
for relation in TrackedFolder._relations:
    if relation.name in ["open", "history"]:
        relation.index = mapping.get(relation.name)
TrackedFolder._relations.sort(key=lambda r: r.index)


class FileFormat(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    def choices(self):
        return CHOICES


class CreateFileSystemItemAction(flow.Action):

    def get_buttons(self):
        self.message.set(self._title())
        return ['Create', 'Cancel']
    
    def _title(self):
        raise NotImplementedError
    
    def _warn(self, message):
        self.message.set((
            f'{self._title()}'
            f'<font color=#D66700>{message}</font>'
        ))


class CreateFileAction(CreateFileSystemItemAction):

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')

    _files = flow.Parent()

    file_name   = flow.SessionParam('').ui(label='Name')
    file_format = flow.SessionParam('blend', FileFormat).ui(label='Format', choice_icons=CHOICES_ICONS)
    tracked     = flow.SessionParam(True).ui(editor='bool', hidden=True)
    
    def _title(self):
        return '<h2>Create file</h2>'

    def run(self, button):
        if button == 'Cancel':
            return

        name, extension = self.file_name.get(), self.file_format.get()

        if self._files.has_file(name, extension):
            self._warn((
                f'File {name}.{extension} already exists. '
                'Please choose another name.'
            ))
            return self.get_result(close=False)
        
        self._files.add_file(
            name,
            extension=extension,
            base_name=name,
            display_name=f'{name}.{extension}',
            tracked=self.tracked.get()
        )
        self._files.touch()


class CreateFolderAction(CreateFileSystemItemAction):

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')

    _files = flow.Parent()

    folder_name = flow.SessionParam('').ui(label='Name')
    tracked     = flow.SessionParam(True).ui(editor='bool', hidden=True)

    def _title(self):
        return '<h2>Create folder</h2>'

    def run(self, button):
        if button == 'Cancel':
            return
        
        name = self.folder_name.get()

        if self._files.has_folder(name):
            self._warn((
                f'Folder {name} already exists. '
                'Please choose another name.'
            ))
            return self.get_result(close=False)
        
        self._files.add_folder(
            name,
            base_name=name,
            display_name=name,
            tracked=self.tracked.get()
        )
        self._files.touch()


class FileSystemMap(EntityView):

    _STYLE_BY_STATUS = {
        'unlocked': ('icons.libreflow', 'blank'),
        'locked': ('icons.libreflow', 'lock-green'),
        'locked-other': ('icons.libreflow', 'lock-red')
    }

    _department = flow.Parent()

    create_file_action   = flow.Child(CreateFileAction).ui(label='Create file').injectable()
    create_folder_action = flow.Child(CreateFolderAction).ui(label='Create folder').injectable()

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(FileSystemItem)
    
    def mapped_names(self, page_num=0, page_size=None):
        cache_key = (page_num, page_size)
        if (
            self._document_cache is None
            or self._document_cache_key != cache_key
            or self._document_cache_birth < time.time() - self._document_cache_ttl
        ):
            cursor = (
                self.get_entity_store()
                .get_collection(self.collection_name())
                .aggregate([
                    {
                        '$match': {'name': {'$regex': f'^{self.oid()}/[^/]*'}}
                    },
                    {
                        '$lookup': {
                            'from': self.revision_collection_name(),
                            'let': { 'pattern': { '$concat': ['^', '$name', '/.*']}},
                            'pipeline': [
                                {
                                    '$match': {
                                        '$expr': {
                                            '$regexMatch': {
                                                'input': '$name',
                                                'regex': '$$pattern'
                                            }
                                        },
                                        'working_copy': True
                                    }
                                }
                            ],
                            'as': 'working_copies'
                        }
                    },
                    {
                        '$lookup': {
                            'from': self.revision_collection_name(),
                            'localField': 'last_revision_oid',
                            'foreignField': 'name',
                            'as': 'last_revision'
                        }
                    },
                ])
            )
            if page_num is not None and page_size is not None:
                cursor.skip((page_num - 1) * page_size)
                cursor.limit(page_size)
            name_and_doc = [(i["name"], i) for i in cursor]
            for n, d in name_and_doc:
                d['working_copies'] = [
                    wc['name'].rsplit('/', maxsplit=1)[-1] for wc in d['working_copies']
                ]
            
            self._document_names_cache = [n for n, d in name_and_doc]
            self._document_cache = dict(name_and_doc)
            self._document_cache_birth = time.time()
            self._document_cache_key = cache_key
            self.ensure_indexes()
        
        return [oid.rsplit('/', maxsplit=1)[-1] for oid in self._document_names_cache]

    def collection_name(self):
        return self.root().project().get_file_manager().files.collection_name()
    
    def revision_collection_name(self):
        return self.root().project().get_file_manager().revisions.collection_name()

    def columns(self):
        return ['Name', 'Status']

    def _fill_row_cells(self, row, item):
        self.mapped_names()

        row['Status'] = ''
        row['Name'] = self._document_cache[item.oid()]['display_name']
        
        last_revision_data = self._document_cache[item.oid()]['last_revision']

        if last_revision_data:
            last_revision_data = last_revision_data[0]
            row['Status'] = '%s > %s' % (
                last_revision_data['name'].rsplit('/', maxsplit=1)[-1],
                last_revision_data['comment']
            )

    def _fill_row_style(self, style, item, row):
        style['Status_icon'] = self._get_status_icon(item)
        style['Name_icon'] = item.get_icon(extension=self._document_cache[item.oid()]['format'])

        style['Name_activate_oid'] = item.open.oid()
        style['Status_activate_oid'] = item.show_history.oid()

    def _get_status_icon(self, item):
        self.mapped_names()

        user_name = self.root().project().get_user_name()
        locked_by = self._document_cache[item.oid()].get('locked_by', None)

        if locked_by is None:
            lock_key = 'unlocked'
        elif locked_by == user_name:
            lock_key = 'locked'
        else:
            lock_key = 'locked-other'
        
        folder, icon_name = self._STYLE_BY_STATUS[lock_key]
        
        if user_name in self._document_cache[item.oid()]['working_copies']:
            icon_name = 'edit-' + icon_name
        
        return folder, icon_name
    
    def get_parent_path(self):
        '''
        Returns the parent path of files contained in this map.
        '''
        return self.oid()[1:]

    def add_file(self, name, extension, display_name=None, base_name=None, tracked=False):
        '''
        Create a file in this map.

        If provided, `base_name` define the name of the file in the file system,
        without its extension. Otherwise, it defaults to the provided `name`.
        '''
        if base_name is None:
            base_name = name
        if display_name is None:
            display_name = f'{name}.{extension}'
        
        f = self.add(
            self._get_item_mapped_name(name, extension),
            object_type=self._get_item_type(tracked, extension)
        )

        f.configure(extension, base_name, display_name)
        
        return f
    
    def add_folder(self, name, display_name=None, base_name=None, tracked=False):
        '''
        Create a folder in this map.

        If provided, `base_name` define the name of the file in the file system,
        without its extension. Otherwise, it defaults to the provided `name`.
        '''
        if base_name is None:
            base_name = name
        if display_name is None:
            display_name = name
        
        f = self.add(
            self._get_item_mapped_name(name),
            object_type=self._get_item_type(tracked)
        )
        
        f.configure(None, base_name, display_name)
        
        return f
    
    def has_file(self, name, extension):
        return self.has_mapped_name(
            self._get_item_mapped_name(name, extension)
        )
    
    def has_folder(self, name):
        return self.has_mapped_name(
            self._get_item_mapped_name(name)
        )

    def _get_item_mapped_name(self, name, extension=None):
        mapped_name = name
        if extension is not None:
            mapped_name += '_' + extension
        
        return mapped_name

    def _get_item_type(self, tracked, extension=None):
        mapped_type = File
        
        if tracked:
            if extension is None:
                mapped_type = TrackedFolder
            else:
                mapped_type = TrackedFile
        elif extension is None:
            mapped_type = Folder
        
        # Ensure type is injectable
        flow.injection.injectable(mapped_type)

        # Return resolved type
        return flow.injection.resolve(mapped_type, self)


class PageNumber(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    _manager = flow.Parent()

    def choices(self):
        c = self._get_collection().get_entity_store().get_collection(self._get_collection().collection_name())
        page_count = -1 * (- c.count_documents({}) // self._get_collection().page_size())
        return [str(i) for i in range(1, page_count + 1)]
    
    def _get_collection(self):
        raise NotImplementedError
    
    def update_page_num(self):
        self._get_collection().page_num.set(int(self.get()))
        self._get_collection().touch()


class FilePageNumber(PageNumber):

    def _get_collection(self):
        return self._manager.files


class RevisionPageNumber(PageNumber):

    def _get_collection(self):
        return self._manager.revisions


class SyncStatusPageNumber(PageNumber):

    def _get_collection(self):
        return self._manager.sync_statutes


class PaginatedGlobalCollection(GlobalEntityCollection):

    _page_size = flow.IntParam(50)
    page_num = flow.SessionParam(1).ui(editor='int')

    def page_size(self):
        return self._page_size.get()

    def current_page_num(self):
        return self.page_num.get()


class FileManager(flow.Object):

    files = flow.Child(PaginatedGlobalCollection).ui(expanded=True, show_filter=True)
    files_page_num = flow.SessionParam(1, FilePageNumber).ui(label='Page').watched()
    revisions = flow.Child(PaginatedGlobalCollection).ui(expanded=True, show_filter=True)
    revisions_page_num = flow.SessionParam(1, RevisionPageNumber).ui(label='Page').watched()
    sync_statutes = flow.Child(PaginatedGlobalCollection).ui(expanded=True, show_filter=True)
    sync_statutes_page_num = flow.SessionParam(1, SyncStatusPageNumber).ui(label='Page').watched()
    
    def child_value_changed(self, child_value):
        if child_value is self.files_page_num:
            self.files_page_num.update_page_num()
        elif child_value is self.revisions_page_num:
            self.revisions_page_num.update_page_num()
        elif child_value is self.sync_statutes_page_num:
            self.sync_statutes_page_num.update_page_num()
