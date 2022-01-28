import os
import sys
import gazu
import time
from datetime import datetime, timedelta
import subprocess
import platform
from minio import Minio
import zipfile
import fnmatch
import re
import traceback
import tempfile
import uuid
import pathlib

from kabaret import flow
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict
from kabaret.subprocess_manager.flow import RunAction
from kabaret.flow_entities.entities import EntityCollection, Entity, Property, PropertyValue

from ..utils.os import zip_folder, unzip_archive

from .dependency import get_dependencies
from .maputils import ItemMap, CreateGenericAction, ClearMapAction, RemoveGenericAction, SimpleCreateAction
from .runners import Runner, PythonRunner


class StaticSiteTypeChoices(flow.values.ChoiceValue):
    CHOICES = ['Studio', 'User']


class StaticSiteSyncStatusChoices(flow.values.ChoiceValue):
    CHOICES = ['NotAvailable', 'Requested', 'Available']


class StaticSiteSyncTransferStateChoices(flow.values.ChoiceValue):
    CHOICES = ['NC', 'UP_REQUESTED', 'DL_REQUESTED', 'UP_IN_PROGRESS', 'DL_IN_PROGRESS']


class LoadType(PropertyValue):

    DEFAULT_EDITOR = 'choice'
    CHOICES = ['Upload', 'Download']

    def choices(self):
        return self.CHOICES


class JobStatus(PropertyValue):

    DEFAULT_EDITOR = 'choice'
    CHOICES = ['WFA', 'WAITING', 'PROCESSED', 'ERROR', 'PAUSE', 'DONE']

    def choices(self):
        return self.CHOICES


class ResetJob(flow.Action):

    ICON = ('icons.libreflow', 'reset')

    _job = flow.Parent()
    _jobs = flow.Parent(2)

    def needs_dialog(self):
        o = self.root().get_object(self._job.emitter_oid.get())
        return self._job.type.get() == 'Upload' and o.get_sync_status(exchange=True) == 'Available'
    
    def allow_context(self, context):
        return context and self._job.status.get() == 'ERROR'
    
    def get_buttons(self):
        self.message.set((
            '<h3>Revision already available on exchange server</h3>'
            'Reset upload job anyway ?'
        ))
        return ['Confirm', 'Cancel']

    def run(self, button):
        if button == 'Cancel':
            return
        
        self._job.status.set('WAITING')
        self._job.log.set('?')
        self._jobs.incr_waiting_count()
        o = self.root().get_object(self._job.emitter_oid.get())
        o.set_sync_status('NotAvailable', exchange=True)


class ResetJobs(flow.Action):

    ICON = ('icons.libreflow', 'reset')

    _jobs = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        if button == 'Cancel':
            return
        
        for j in self._jobs.jobs(status='ERROR'):
            j.status.set('WAITING')
        
        self._jobs.touch()


class ShowRevisionInHistory(flow.Action):

    ICON = ("icons.gui", "ui-layout")

    _job = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        history_oid = self._job.emitter_oid.get() + '/../..'
        history_oid = self.root().session().cmds.Flow.resolve_path(history_oid)

        return self.get_result(goto=history_oid)


class Job(Entity):

    type                = Property(property_value_type=LoadType)
    status              = Property(property_value_type=JobStatus)
    priority            = Property().ui(editor='int')
    emitter_oid         = Property()
    local_path          = Property()
    server_path         = Property()
    date                = Property().ui(editor='datetime')
    date_end            = Property().ui(editor='datetime')
    is_archived         = Property().ui(editor='bool')
    requested_by_user   = Property()
    requested_by_studio = Property()
    log                 = Property().ui(editor='textarea')

    reset = flow.Child(ResetJob)
    show = flow.Child(ShowRevisionInHistory).ui(label='Show in history')

    def __repr__(self):
        job_repr = "%s(type=%s, status=%s, priority=%s, emitter=%s, date=%s, date_end=%s, is_archived=%s, requested_by_user=%s, requested_by_studio=%s)" % (
                self.__class__.__name__,
                self.type.get(),
                self.status.get(),
                self.priority.get(),
                self.emitter_oid.get(),
                self.date.get(),
                self.date_end.get(),
                self.is_archived.get(),
                self.requested_by_user.get(),
                self.requested_by_studio.get()
            )

        return job_repr
    
    def on_submitted(self):
        '''
        Computes the local and server paths of the job's
        requested object (identified by `emitter_oid`).

        If the oid does not refer to an existing revision
        object, the methods puts the job in error state.
        '''
        try:
            revision = self.root().get_object(
                self.emitter_oid.get()
            )
        except (ValueError, flow.exceptions.MissingRelationError):
            self.status.set('ERROR')
            self.log.set('Object does not exist')
            return
        
        try:
            ready_for_sync = revision.ready_for_sync.get()
            local_path = revision.get_path()
            server_path = revision.get_path(relative=True)
        except AttributeError:
            self.status.set('ERROR')
            self.log.set('Object is not a revision')
            return
        else:
            if not ready_for_sync:
                self.status.set('ERROR')
                self.log.set('Revision is not ready to be synced')
                return
        
        if os.path.splitext(server_path)[1] == '':
            server_path += '/' + os.path.basename(server_path) + '.zip'
        
        self.local_path.set(local_path)
        self.server_path.set(server_path.replace('\\', '/'))
    
    def on_processed(self):
        '''
        Method which may be called after this job has been
        processed.

        Default is to update the related revision's statutes,
        and update its UI and that of its parent map. The
        method assumes param `emitter_oid` references a valid
        revision object.
        '''
        if self.status.get() != 'PROCESSED':
            return
        
        revision = self.root().get_object(
            self.emitter_oid.get()
        )
        revision.set_sync_status(
            'Available',
            exchange=(self.type.get() == 'Upload')
        )
        revision.touch()
        revision._revisions.touch()


class JobQueue(EntityCollection):

    count_waiting = flow.IntParam(0)
    reset_jobs = flow.Child(ResetJobs).ui(label='Reset erroneous jobs')

    @classmethod
    def mapped_type(cls):
        return Job
    
    def get_next_waiting_job(self):
        for job in reversed(self.mapped_items()):
            if job.status.get() == "WAITING":
                return job
        
        return None
    
    def jobs(self, type=None, status=None):
        jobs = self.mapped_items()

        if type is not None:
            jobs = [j for j in jobs if j.type.get() == type]
        if status is not None:
            jobs = [j for j in jobs if j.status.get() == status]
        
        return jobs
    
    def count(self, type=None, status=None):
        job_filter = {}

        if type is not None:
            job_filter['type'] = type
        if status is not None:
            job_filter['status'] = status
        
        c = self.get_entity_store().get_collection(self.collection_name())

        return c.count_documents(job_filter)
    
    def update_waiting_count(self, count=None):
        if count is None:
            count = len(self.jobs(status='WAITING'))
        
        self.count_waiting.set(count)
    
    def incr_waiting_count(self, by=1):
        self.count_waiting.incr(by)

    def decr_waiting_count(self, by=1):
        self.count_waiting.decr(by)
    
    def submit_job(self,
            emitter_oid,
            user,
            studio,
            date_end=-1,
            job_type='Download',
            init_status='WAITING',
            priority=50
        ):
        
        name = '%s_%s_%s_%i' % (
            emitter_oid[1:].replace('/', '_'),
            studio,
            job_type,
            time.time()
        )
        self.ensure_exist([name])
        self._document_cache = None

        job = self.get_mapped(name)
        job.type.set(job_type)
        job.status.set(init_status)
        job.priority.set(priority)
        job.emitter_oid.set(emitter_oid)
        job.date.set(time.time())
        job.date_end.set(date_end)
        job.requested_by_user.set(user)
        job.requested_by_studio.set(studio)
        job.is_archived.set(False)
        job.log.set('?')

        job.on_submitted()

        self.incr_waiting_count()

        self.root().session().log_info("Submitted job %s" % job)

        self.touch()

        return job
    
    def columns(self):
        return [
            "Type",
            "Status",
            "Revision",
            "Emitted on",
            "By",
            "Site",
        ]
    
    def _fill_row_cells(self, row, item):
        self.mapped_names()
        item_data = self._document_cache[item.name()]

        row['Type']       = item_data['type']
        row['Status']     = item_data['status']
        row['Revision']   = item_data['emitter_oid']
        row['By']         = item_data['requested_by_user']
        row['Site']       = item_data['requested_by_studio']
        row['Emitted on'] = datetime.fromtimestamp(
            float(item_data['date'])
        ).ctime()


class ProcessJobs(flow.Action):

    def __init__(self, parent, name):
        super(ProcessJobs, self).__init__(parent, name)
        self._job_count = {}

    def needs_dialog(self):
        return False

    def process(self, job):
        raise NotImplementedError(
            "Must be implemented to process the given job"
        )
    
    def _get_jobs(self):
        current_site = self.root().project().get_current_site()
        return current_site.get_jobs()
    
    def _compute_job_count(self):
        count = dict.fromkeys(JobStatus.CHOICES, 0)

        for j in self.root().project().get_current_site().get_jobs():
            count[j.status.get()] += 1
        
        return count
    
    def run(self, button):
        self._job_count = self._compute_job_count()

        for job in self._get_jobs():
            self.root().session().log_info("Processing job %s" % job)
            
            self._job_count[job.status.get()] -= 1
            self.process(job)
            self._job_count[job.status.get()] += 1
        
        current_site = self.root().project().get_current_site()
        current_site.queue.job_list.update_waiting_count(self._job_count['WAITING'])

        # Refresh project's sync section UI
        self.root().project().synchronization.touch()


class MinioFileUploader(PythonRunner):
    
    def argv(self):
        args = ["%s/../scripts/minio_file_uploader.py" % (
            os.path.dirname(__file__)
        )]
        args += self.extra_argv
        return args


class MinioFileDownloader(PythonRunner):
    
    def argv(self):
        args = ["%s/../scripts/minio_file_downloader.py" % (
            os.path.dirname(__file__)
        )]
        args += self.extra_argv
        return args


class MinioUploadFile(flow.Object):

    def upload(self, local_path, server_path):
        self.root().session().log_info(
            "Uploading file %s -> %s" % (
                local_path,
                server_path
            )
        )
        exchange_site = self.root().project().get_exchange_site()
        minioClient = Minio(
            exchange_site.server_url.get(),
            access_key=exchange_site.server_login.get(),
            secret_key=exchange_site.server_password.get(),
            secure=True
        )

        minioClient.fput_object(
            exchange_site.bucket_name.get(),
            server_path,
            local_path
        )


class MinioDownloadFile(flow.Object):

    def download(self, server_path, local_path):
        self.root().session().log_info(
            "Downloading file %s -> %s" % (
                server_path,
                local_path
            )
        )
        exchange_site = self.root().project().get_exchange_site()
        minioClient = Minio(
            exchange_site.server_url.get(),
            access_key=exchange_site.server_login.get(),
            secret_key=exchange_site.server_password.get(),
            secure=True
        )
        
        tmp_path = self.root().project().get_temp_folder()

        if tmp_path is not None:
            tmp_name = os.path.splitext(os.path.basename(local_path))[0]
            tmp_path = os.path.join(tmp_path, tmp_name)

        minioClient.fget_object(
            exchange_site.bucket_name.get(),
            server_path,
            local_path,
            tmp_file_path=tmp_path
        )


class SyncManager(flow.Object):

    _exchange = flow.Parent()

    def __init__(self, parent, name):
        super(SyncManager, self).__init__(parent, name)
        self._client = None

    def upload(self, server_path, local_path):
        zipped_folder = self._is_zipped_folder(
            server_path, local_path
        )
        if zipped_folder:
            # Folder to be zipped before upload
            src_path = self._get_temp_zip(server_path)
            zip_folder(local_path, src_path)
        else:
            # File/folder uploaded as is
            src_path = local_path

        self.root().session().log_info(
            f'Upload file {local_path} -> {server_path}'
        )
        self._ensure_client().fput_object(
            self._exchange.bucket_name.get(),
            server_path,
            src_path
        )

        if zipped_folder:
            os.remove(src_path)

    def download(self, server_path, local_path):
        zipped_folder = self._is_zipped_folder(
            server_path, local_path
        )
        if zipped_folder:
            dst_path = self._get_temp_zip(server_path)
        else:
            dst_path = local_path
        
        self.root().session().log_info(
            f'Download file {server_path} -> {local_path}'
        )
        self._ensure_client().fget_object(
            self._exchange.bucket_name.get(),
            server_path,
            dst_path
        )

        if zipped_folder:
            unzip_archive(dst_path, local_path)
            os.remove(dst_path)
    
    def check_connection(self):
        try:
            self._ensure_client().list_buckets()
        except Exception as err:
            return str(err)
        else:
            return None

    def _ensure_client(self):
        if self._client is None:
            self._client = Minio(
                self._exchange.server_url.get(),
                access_key=self._exchange.server_login.get(),
                secret_key=self._exchange.server_password.get(),
                secure=self._exchange.enable_tls.get()
            )
        
        return self._client
    
    def _get_temp_zip(self, server_path):
        return os.path.join(
            self.root().project().get_temp_folder(),
            (
                pathlib.PurePath(server_path).stem
                + f'-{str(uuid.uuid4())}.zip'
            )
        )
    
    def _is_zipped_folder(self, server_path, local_path):
        return (
            os.path.splitext(local_path)[1] == ''
            and os.path.splitext(server_path)[1] == '.zip'
        )


class Synchronize(ProcessJobs):

    def _get_jobs(self):
        return self.root().project().get_current_site().get_jobs(
            status='WAITING'
        )

    def process(self, job):
        if job.status.get() != 'WAITING':
            self.root().session().log_warning(
                'Job %s in %s status: skipping' % (
                    job.name(),
                    job.status.get()
                )
            )
            return
        
        try:
            sync_manager = self.root().project().get_exchange_site().sync_manager
        
            if job.type.get() == 'Upload':
                sync_manager.upload(
                    job.server_path.get(),
                    job.local_path.get()
                )
            else:
                sync_manager.download(
                    job.server_path.get(),
                    job.local_path.get()
                )
        except Exception as e:
            job.status.set('ERROR')
            job.log.set(traceback.format_exc())
        else:
            job.status.set('PROCESSED')
            job.on_processed()


class ActiveSiteChoiceValue(flow.values.SessionValue):
    
    DEFAULT_EDITOR = 'choice'
    
    _choices = flow.SessionParam(None).ui(editor='set')

    def choices(self):
        if self._choices.get() is None:
            working_sites = self.root().project().get_working_sites()
            names = working_sites.get_site_names(use_custom_order=True, active_only=True)
            self._choices.set(names)
        
        return self._choices.get()


class ActiveSiteAutoSelectChoiceValue(ActiveSiteChoiceValue):
    
    def choices(self):
        choices = super(ActiveSiteAutoSelectChoiceValue, self).choices()
        choices = ['Auto select'] + choices.copy()
        
        return choices


class ActiveSitesMultichoiceValue(ActiveSiteChoiceValue):
    
    DEFAULT_EDITOR = 'multichoice'
    
    exclude_choice = flow.SessionParam()
    
    def choices(self):
        if self._choices.get() is None:
            working_sites = self.root().project().get_working_sites()
            names = working_sites.get_site_names(use_custom_order=True, active_only=True)
            self._choices.set(names)
        
        choices = self._choices.get().copy()
        exclude_choice = self.exclude_choice.get()
        
        if exclude_choice is not None:
            try:
                choices.remove(exclude_choice)
            except ValueError:
                pass
        
        return choices


class ActiveSiteRevisionAvailableChoiceValue(flow.values.ChoiceValue):
    
    DEFAULT_EDITOR = 'choice'
    
    _choices = flow.SessionParam(None).ui(editor='set')
    _revision = flow.Parent(2)
    
    exclude_choice = flow.SessionParam(None).ui(hidden=False)

    def choices(self):
        if self._choices.get() is None:
            working_sites = self.root().project().get_working_sites()
            choices = working_sites.get_site_names(use_custom_order=True, active_only=True)
            exclude_choice = self.exclude_choice.get()
            
            if exclude_choice is not None:
                try:
                    choices.remove(exclude_choice)
                except ValueError:
                    pass
            
            choices_available = []
            
            for site_name in choices:
                if self._revision.get_sync_status(site_name) == 'Available':
                    choices_available.append(site_name)
            
            self._choices.set(choices_available)
        
        return self._choices.get()


class SiteSelection(flow.Object):
    
    source_site = flow.Param(None, ActiveSiteChoiceValue).watched()
    target_site = flow.Param(None, ActiveSiteChoiceValue).watched()
    auto_select_enabled = flow.SessionParam(False).watched().ui(
        editor='bool',
        hidden=True)
    
    def child_value_changed(self, child_value):
        if child_value in (self.source_site, self.target_site, self.auto_select_enabled):
            self.touch()
    
    def summary(self):
        if self.source_site.get() == self.target_site.get() and not self.auto_select_enabled.get():
            return '⚠️ Source and target sites can\'t be the same !'
        else:
            return ''


class RequestAs(flow.Action):

    _revision = flow.Parent()
    sites = flow.Child(SiteSelection).ui(expanded=True)
    priority = flow.IntParam(50)
    include_dependencies = flow.SessionParam(True).ui(editor='bool')
    forced_upload = flow.SessionParam(False).ui(
        editor='bool',
        tooltip=('Ask the source site to upload the revision regardless'
                 ' of its status on the exchange site.'))
    
    def get_buttons(self):
        self.sites.source_site.set(self.root().project().get_current_site().name())
        target_site_choices = self.sites.target_site.choices()
        
        if not target_site_choices:
            msg = self.message.get()
            if msg is None:
                msg = ''
            
            msg += (
                '<h3><font color="#D5000D">Making requests is not possible since '
                'there is no other site defined for this project.</font></h3>'
            )
            self.message.set(msg)
            
            return ['Cancel']
        
        self.sites.target_site.set(target_site_choices[0])

        return ["Request", "Cancel"]
    
    def get_source_site_name(self):
        return self.sites.source_site.get()
    
    def get_target_site_name(self):
        return self.sites.target_site.get()
    
    def allow_context(self, context):
        return (
            context
            and not self._revision.is_working_copy()
            and self.root().project().get_current_site().request_files_from_anywhere.get()
        )

    def run(self, button):
        if button == "Cancel":
            return
        
        source_site_name = self.get_source_site_name()
        target_site_name = self.get_target_site_name()

        # Get requesting and requested sites
        sites = self.root().project().get_working_sites()
        target_site = sites[target_site_name]
        
        # Add a download job for the requesting site
        target_site.get_queue().submit_job(
            job_type="Download",
            init_status="WAITING",
            emitter_oid=self._revision.oid(),
            user=self.root().project().get_user_name(),
            studio=target_site_name,
            priority=self.priority.get(),
        )
        self._revision.set_sync_status("Requested", site_name=target_site_name)
        self._revision._revisions.touch()
        
        # Request dependencies if required
        if self.include_dependencies.get():
            request_deps = self._revision.request_dependencies
            request_deps.target_site.set(target_site_name)
            request_deps.predictive_only.set(False)
            request_deps.run(None)
        
        # Check if the version is not available on the exchange server
        exchange_site = self.root().project().get_exchange_site()
        revision_status = self._revision.get_sync_status(exchange=True)

        if revision_status == "Available" and not self.forced_upload.get():
            self.root().session().log_warning(
                "Revision already available on exchange server"
            )
            self.root().project().synchronization.touch()
            return self.get_result()
        
        # If enabled, automatically select source site
        if self.sites.auto_select_enabled.get():
            source_site_name = self._revision.site.get()
        
        source_site = sites[source_site_name]

        # Check if the source version upload is not already requested
        for job in source_site.get_jobs(type="Upload", status="WAITING"):
            if job.emitter_oid.get() == self._revision.oid():
                self.root().session().log_warning(
                    "Revision already requested for upload in source site"
                )
                self.root().project().synchronization.touch()
                return self.get_result()
        
        # Add an upload job for the requested site
        source_site.get_queue().submit_job(
            job_type="Upload",
            init_status="WAITING",
            emitter_oid=self._revision.oid(),
            user=self.root().project().get_user_name(),
            studio=target_site_name,
            priority=self.priority.get(),
        )

        # Refresh project's sync section UI
        self.root().project().synchronization.touch()


class Request(RequestAs):

    _revision = flow.Parent()
    priority = flow.IntParam(50)
    source_site = flow.Param(None, ActiveSiteRevisionAvailableChoiceValue)
    
    sites = flow.Child(SiteSelection).ui(hidden=True)

    def get_buttons(self):
        self.source_site.exclude_choice.set(self.root().project().get_current_site().name())
        source_site_choices = self.source_site.choices()
        
        if not source_site_choices:
            msg = self.message.get()
            if msg is None:
                msg = ''
            
            msg += (
                '<h3><font color="#D5000D">Making requests is not possible since '
                'the revision isn\'t available on any site.</font></h3>'
            )
            self.message.set(msg)
            
            return ['Cancel']
        
        self.source_site.set(source_site_choices[0])

        return ['Request', 'Cancel']
    
    def get_source_site_name(self):
        return self.source_site.get()
    
    def get_target_site_name(self):
        return self.root().project().get_current_site().name()
    
    def allow_context(self, context):
        return (
            context
            and not self._revision.is_working_copy()
            and self._revision.get_sync_status() != "Available"
            and self._revision.get_sync_status(exchange=True) != "Available"
        )


class SyncErrorCounter(flow.DynamicMap):

    _error_count = flow.Param([])

    def refresh_error_count(self):
        count = []
        sites = self.root().project().get_working_sites()
        site_names = sites.get_site_names(use_custom_order=True, active_only=True)

        for name in site_names:
            s = sites[name]
            count.append((s.name(), s.oid(), len(s.get_jobs(status='ERROR'))))
        
        self._error_count.set(count)
    
    def columns(self):
        return ['Site', 'Nb errors']

    def rows(self):
        count = self._error_count.get()
        rows = []

        for site_name, site_oid, nb_err in count:
            style = {'icon': ('icons.libreflow', 'blank')}
            oid = site_oid + '/queue'
            
            if nb_err > 0:
                style['foreground-color'] = '#D5000D'
                style['Nb errors_foreground-color'] = '#D5000D'
            
            rows.append((oid,
                {
                    'Site': site_name,
                    'Nb errors': nb_err,
                    'activate_oid': oid,
                    '_style': style
                }
            ))
        
        return rows


class ShowSiteSyncErrors(flow.Action):

    error_counter = flow.Child(SyncErrorCounter).ui(
        label='Errors',
        expanded=True)

    def get_buttons(self):
        self.message.set('<h2>Synchronization errors</h2>')
        return ['Refresh', 'Close']
    
    def run(self, button):
        if button == 'Close':
            return
        
        self.error_counter.refresh_error_count()
        self.error_counter.touch()
        return self.get_result(close=False)


class ResetJobStatuses(flow.Action):
    _site = flow.Parent()
    status = flow.Param("WAITING", JobStatus)

    def run(self, button):
        for job in self._site.get_jobs():
            job.status.set(self.status.get())
        
        self._site.get_queue().touch()


class CreateSite(flow.Action):

    ICON = ("icons.gui", "plus-sign-in-a-black-circle")

    _site_map = flow.Parent()
    site_name = flow.SessionParam("").ui(label="Name")

    def get_buttons(self):
        self.message.set("<h2>Create a site</h2>")
        return ["Create", "Cancel"]
    
    def run(self, button):
        if button == "Cancel":
            return
        
        site_name = self.site_name.get()

        if not site_name or self._site_map.has_mapped_name(site_name):
            if not site_name:
                msg = "Site name must not be empty."
            else:
                msg = f"Site {site_name} already exists."

            self.message.set((
                "<h2>Create a site</h2>"
                f"<font color=#D5000D>{msg}</font>"
            ))
            
            return self.get_result(close=False)

        site = self._site_map.add(site_name)
        self._site_map.touch()

        return self.get_result(next_action=site.configuration.oid())


class ConfigureSite(flow.Action):

    _site_map = flow.Parent(2)
    _site = flow.Parent()
    short_name = flow.SessionParam("").ui(label="Short name")
    description = flow.SessionParam("")

    def get_buttons(self):
        self.message.set(
            "<h2>Site <font color=#fff>%s</font></h2>" % self._site.name()
        )
        self._fill_action_fields()

        return ["Configure", "Cancel"]

    def _configure_site(self, site):
        '''
        This can be used by subclass to configure a mapped site.

        Default is to set site's short name and description.
        '''
        self._site.short_name.set(self.short_name.get())
        self._site.description.set(self.description.get())
    
    def _fill_action_fields(self):
        '''
        This can be used by subclass to fill action's parameters when
        dialog is displayed (e.g. to automatically show site parameters).

        Default is to fill site's short name and description.
        '''
        self.short_name.set(self._site.short_name.get())
        self.description.set(self._site.description.get())
    
    def allow_context(self, context):
        # Hide in map item submenus
        return False
    
    def run(self, button):
        if button == "Cancel":
            return
        
        self._configure_site(self._site)
        self._site.configured.touch()
        self._site_map.touch()


class ComputedBoolValue(flow.values.ComputedValue):

    DEFAULT_EDITOR = 'bool'


class Site(flow.Object):

    short_name = flow.Param("")
    description = flow.Param("")
    # Define conditions required for a site to be considered as correctly configured
    configured = flow.Computed().ui(editor='bool')
    configuration = flow.Child(ConfigureSite)

    is_active = flow.BoolParam(True)

    def compute_child_value(self, child_value):
        if child_value is self.configured:
            self.configured.set(True)


class SiteMap(flow.Map):

    create_site = flow.Child(CreateSite)

    _short_names = flow.HashParam()
    _active_site_names = flow.OrderedStringSetParam()

    @classmethod
    def mapped_type(cls):
        return Site

    def mapped_names(self, page_num=0, page_size=None):
        return ["default"] + super(SiteMap, self).mapped_names(page_num, page_size)
    
    def columns(self):
        return ["Site"]
    
    def short_names(self):
        short_names = []
        
        for name in self.mapped_names():
            short_names.append(self.get_short_name(name))
        
        return short_names
    
    def get_short_name(self, site_name):
        return self._short_names.get_key(site_name)
    
    def update_active_site_names(self):
        self._active_site_names.revert_to_default()
        i = 0

        for s in self.mapped_items():
            if s.is_active.get():
                self._active_site_names.add(s.name(), i)
            
            i += 1
    
    def update_site_short_names(self):
        self._short_names.revert_to_default()

        for s in self.mapped_items():
            self._short_names.set_key(s.name(), s.short_name.get())
    
    def get_site_names(self, use_custom_order=False, active_only=False, short_names=False):
        sites_data = self.root().project().admin.multisites.sites_data.get()
        
        if use_custom_order:
            current_site = self.root().project().get_current_site()
            names = current_site.ordered_site_names.get()
        else:
            names = self.mapped_names()

        site_names = []

        for name in names:
            data = sites_data[name]

            if active_only and not data['is_active']:
                continue
            
            if short_names:
                site_names.append(data['short_name'])
            else:
                site_names.append(name)
        
        return site_names
    
    def _get_mapped_item_type(self, mapped_name):
        if mapped_name == "default":
            return self.mapped_type()

        return super(SiteMap, self)._get_mapped_item_type(mapped_name)
    
    def _fill_row_cells(self, row, item):
        row["Site"] = item.name()
        if not item.configured.get():
            row["Site"] += " ⚠️"


class ConfigureWorkingSite(ConfigureSite):

    site_type = flow.Param("Studio", StaticSiteTypeChoices)

    root_windows_folder = flow.SessionParam("")
    root_linux_folder = flow.SessionParam("")
    root_darwin_folder = flow.SessionParam("")
    
    sync_dl_max_connections = flow.SessionParam(1)
    sync_up_max_connections = flow.SessionParam(1)
    
    def _fill_action_fields(self):
        super(ConfigureWorkingSite, self)._fill_action_fields()
        self.site_type.set(self._site.site_type.get())
        self.root_windows_folder.set(self._site.root_windows_folder.get())
        self.root_linux_folder.set(self._site.root_linux_folder.get())
        self.root_darwin_folder.set(self._site.root_darwin_folder.get())
        self.sync_dl_max_connections.set(self._site.sync_dl_max_connections.get())
        self.sync_up_max_connections.set(self._site.sync_up_max_connections.get())

    def _configure_site(self, site):
        super(ConfigureWorkingSite, self)._configure_site(site)
        site.site_type.set(self.site_type.get())
        site.root_windows_folder.set(self.root_windows_folder.get())
        site.root_linux_folder.set(self.root_linux_folder.get())
        site.root_darwin_folder.set(self.root_darwin_folder.get())
        site.sync_dl_max_connections.set(self.sync_dl_max_connections.get())
        site.sync_up_max_connections.set(self.sync_up_max_connections.get())


class Queue(flow.Object):

    job_list = flow.Child(JobQueue).ui(
        label="Jobs",
        expanded=True,
        show_filter=True)


class GotoQueue(flow.Action):

    _site = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        return self.get_result(goto=self._site.queue.oid())


class GotoCurrentSiteQueue(flow.Action):
    
    ICON = ('icons.flow', 'jobs')
    
    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return context and context.endswith('.details')
    
    def run(self, button):
        current_site = self.root().project().get_current_site()
        return self.get_result(goto=current_site.queue.oid())


class ClearQueueJobStatus(flow.values.ChoiceValue):

    CHOICES = JobStatus.CHOICES + ["All"]


class ClearQueueLoadType(flow.values.ChoiceValue):

    CHOICES = LoadType.CHOICES + ["All"]


class ClearQueueAction(flow.Action):

    _site = flow.Parent()
    status = flow.Param("PROCESSED", ClearQueueJobStatus)
    type = flow.Param("All", ClearQueueLoadType)
    emitted_before = flow.SessionParam((datetime.now() - timedelta(days=1)).timestamp()).ui(
        editor='datetime'
    )

    def get_buttons(self):
        self.message.set(
            "<h2>Clear %s jobs</h2>" % self._site.name()
        )
        return ["Clear", "Cancel"]
    
    def run(self, button):
        queue = self._site.get_queue()
        status = self.status.get()
        type = self.type.get()

        if status == "All" and type == "All":
            queue.clear()
        else:
            for job in queue.jobs(status=self.status.get()):
                if job.date.get() < self.emitted_before.get():
                    queue.remove(job.name())

        queue.touch()


class RemoveEnvironmentVariableAction(flow.Action):

    ICON = ('icons.gui', 'remove-symbol')

    _variable = flow.Parent().ui(hidden=True)
    _collection = flow.Parent(2).ui(hidden=True)

    def get_buttons(self):
        return ['Confirm', 'Cancel']

    def run(self, button):
        if button == 'Cancel':
            return

        collection = self._collection
        self._collection.remove(self._variable.name())
        collection.touch()


class EnvironmentVariable(flow.Object):

    site = flow.Parent(2)
    
    variable = flow.Param("")
    value_windows = flow.Param('')
    value_linux   = flow.Param('')
    value_darwin  = flow.Param('')
    value = flow.Computed(cached=True)

    remove_variable = flow.Child(RemoveEnvironmentVariableAction).ui(hidden=True)

    def compute_child_value(self, child_value):
        if child_value is self.value:
            value = None
            # Get the operative system
            _os = platform.system()
            if _os == "Linux":
                value = self.value_linux.get()
            elif _os == "Windows":
                value = self.value_windows.get()
            elif _os == "Darwin":
                value = self.value_darwin.get()
            else:
                self.root().session().log_error('Unrecognized operative system')
                value = None

            self.value.set(value)


class AddEnvironmentVariableAction(flow.Action):

    _vars_collection = flow.Parent().ui(hidden=True)
    variable = flow.SessionParam("")
    value_windows = flow.SessionParam('')
    value_linux   = flow.SessionParam('')
    value_darwin  = flow.SessionParam('')

    def get_buttons(self):
        return ['Create', 'Cancel']
    
    def revert_params_to_defaults(self):
        self.variable.revert_to_default()
        self.value_windows.revert_to_default()
        self.value_linux.revert_to_default()
        self.value_darwin.revert_to_default()

    def run(self, button):
        var_name = self.variable.get().replace(' ', '_').upper()
        value_windows = self.value_windows.get()
        value_linux = self.value_linux.get()
        value_darwin = self.value_darwin.get()

        if button == 'Cancel':
            self.revert_params_to_defaults()
            return

        elif (len(var_name) == 0) or (len(value_windows) == 0 and len(value_linux) == 0 and len(value_darwin) == 0) or (self._vars_collection.has_mapped_name(var_name)):
            self.revert_params_to_defaults()
            return

        else:
            new_var = self._vars_collection.add(var_name)
            
            new_var.variable.set(var_name)
            new_var.value_windows.set(value_windows)
            new_var.value_linux.set(value_linux)
            new_var.value_darwin.set(value_darwin)
            self.revert_params_to_defaults()
            self._vars_collection.touch()


class SiteEnvironment(flow.Map):
    
    add_environment_variable = flow.Child(AddEnvironmentVariableAction)

    @classmethod
    def mapped_type(cls):
        return EnvironmentVariable


    def columns(self):
        return ['Variable', 'Value']

    def _fill_row_cells(self, row, item):
        row['Variable'] = item.variable.get()
        row['Value'] = item.value.get()

from .users import PresetValue

class SiteJobsPoolNames(PresetValue):

    DEFAULT_EDITOR = 'choice'
    
    def choices(self):
        site = self.root().project().get_current_site()
        return ['default'] + site.pool_names.get()


class WorkingSite(Site):
    
    _site_map = flow.Parent()
    
    site_type = flow.Param("Studio", StaticSiteTypeChoices)
    request_files_from_anywhere = flow.BoolParam(False).ui(
        tooltip=(
            "Allow the site to request files for any other site. "
            "Temporary option as long as synchronisation is manual."
        )
    )
    is_kitsu_admin = flow.BoolParam(False)
    auto_upload_kitsu_playblasts = flow.BoolParam(True)

    root_folder = flow.Computed(cached=True)
    root_windows_folder = flow.Param()
    root_linux_folder = flow.Param()
    root_darwin_folder = flow.Param()
    
    ordered_site_names = flow.Computed(cached=True)
    custom_site_order = flow.Param('').watched().ui(
        label='Custom order',
        tooltip='Manage order in which sites are listed in the interface')
    
    sync_dl_max_connections = flow.IntParam(1)
    sync_up_max_connections = flow.IntParam(1)
    pool_names = flow.OrderedStringSetParam()

    queue = flow.Child(Queue)

    configuration = flow.Child(ConfigureWorkingSite)
    goto_queue = flow.Child(GotoQueue).ui(
        label="Show job queue"
    )
    clear_queue = flow.Child(ClearQueueAction)
    site_environment = flow.Child(SiteEnvironment)

    def compute_child_value(self, child_value):
        if child_value is self.root_folder:
            root_dir = None
            # Get the operative system
            _os = platform.system()
            if _os == "Linux":
                root_dir = self.root_linux_folder.get()
            elif _os == "Windows":
                root_dir = self.root_windows_folder.get()
            elif _os == "Darwin":
                root_dir = self.root_darwin_folder.get()
            else:
                print("ERROR: Unrecognized operative system ?")
            
            if not root_dir or not os.path.exists(root_dir):
                print("WARNING: ROOT_DIR path DOES NOT EXISTS")

            child_value.set(root_dir)

        elif child_value is self.configured:
            self.configured.set(bool(self.root_folder.get()))
        elif child_value is self.ordered_site_names:
            self.ordered_site_names.set(self._compute_ordered_site_names())
    
    def child_value_changed(self, child_value):
        if child_value is self.custom_site_order:
            self.ordered_site_names.touch()
    
    def _compute_ordered_site_names(self):
        names_as_string = self.custom_site_order.get()
        names = names_as_string.replace(' ','').split(',')
        
        if names and names[0] == '':
            names = []
        
        unordered_names = self._site_map.mapped_names()

        for n in names:
            unordered_names.remove(n)
        
        return names + unordered_names
    
    def get_queue(self):
        return self.queue.job_list
    
    def get_jobs(self, type=None, status=None):
        return self.get_queue().jobs(type=type, status=status)
    
    def count_jobs(self, type=None, status=None):
        return self.get_queue().count(type=type, status=status)


class ClearSiteQueues(flow.Action):

    ICON = ('icons.libreflow', 'clean')

    _sites = flow.Parent()
    emitted_since = flow.Param(0.0)

    def get_buttons(self):
        return ['Clear', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        for s in self._sites.mapped_items():
            for j in s.get_jobs(status='PROCESSED'):
                if time.time() - j.date.get() > self.emitted_since.get():
                    s.queue.job_list.remove(j.name())

        self.root().project().synchronization.touch()


class WorkingSites(SiteMap):

    ICON = ('icons.gui', 'home')

    clear_site_queues = flow.Child(ClearSiteQueues)

    @classmethod
    def mapped_type(cls):
        return WorkingSite

    def _configure_child(self, child):
        if child.name() == "default":
            child.short_name.set("dft")
            child.description.set("Default working site")
            child.site_type.set("Studio")
        else:
            super(WorkingSites, self)._configure_child(child)

    def _fill_row_style(self, style, item, row):
        super(WorkingSites, self)._fill_row_style(style, item, row)

        if item.site_type.get() == "User":
            style['icon'] = ('icons.gui', 'user')
        else:
            style['icon'] = ('icons.gui', 'home')


class ConfigureExchangeSite(ConfigureSite):

    server_url = flow.SessionParam("http://")
    server_login = flow.SessionParam("")
    server_password = flow.SessionParam("").ui(editor='password')
    bucket_name = flow.SessionParam('')

    def _fill_action_fields(self):
        super(ConfigureExchangeSite, self)._fill_action_fields()
        self.server_url.set(self._site.server_url.get())
        self.server_login.set(self._site.server_login.get())
        self.server_password.set(self._site.server_password.get())
        self.bucket_name.set(self._site.bucket_name.get())

    def _configure_site(self, site):
        super(ConfigureExchangeSite, self)._configure_site(site)
        site.server_url.set(self.server_url.get())
        site.server_login.set(self.server_login.get())
        site.server_password.set(self.server_password.get())
        site.bucket_name.set(self.bucket_name.get())


class TestConnectionAction(flow.Action):

    _exchange = flow.Parent()

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('Clik the button to test the connection.')
        return ['Test']

    def run(self, button):
        ret = self._exchange.sync_manager.check_connection()

        if ret is not None:
            self.message.set(
                '<font color=red>Connection error:</font><br>'
                f'<pre>{ret}</pre>'
            )
        else:
            self.message.set(
                'Connection looks <b>OK</b>'
            )
        return self.get_result(close=False)


class ExchangeSite(Site):

    ICON = ('icons.libreflow', 'exchange')

    server_url = flow.Param("")
    server_login = flow.Param("")
    server_password = flow.Param("").ui(editor='password')
    bucket_name = flow.Param('')
    enable_tls = flow.BoolParam(False)

    sync_manager = flow.Child(SyncManager).ui(hidden=True)

    configuration = flow.Child(ConfigureExchangeSite)
    test_connection = flow.Child(TestConnectionAction)

    def compute_child_value(self, child_value):
        if child_value is self.configured:
            self.configured.set(
                (
                    self.server_url.get()
                    and self.server_login.get()
                    and self.server_password.get()
                    and self.bucket_name.get()
                )
            )


class ExchangeSites(SiteMap):
    
    ICON = ('icons.libreflow', 'exchange')

    @classmethod
    def mapped_type(cls):
        return ExchangeSite

    def mapped_names(self, page_num=0, page_size=None):
        return ["default_exchange"] + super(SiteMap, self).mapped_names(page_num, page_size)

    def _configure_child(self, child):
        if child.name() == "default_exchange":
            child.short_name.set("dftx")
            child.description.set("Default exchange site")
        else:
            super(ExchangeSites, self)._configure_child(child)

    def _get_mapped_item_type(self, mapped_name):
        if mapped_name == "default_exchange":
            return self.mapped_type()

        return super(SiteMap, self)._get_mapped_item_type(mapped_name)


class SyncSiteStatus(flow.Object):
    status = flow.Param("NotAvailable", StaticSiteSyncStatusChoices)


class SyncMap(flow.DynamicMap):
    version = flow.Parent()

    @classmethod
    def mapped_type(cls):
        return SyncSiteStatus

    def mapped_names(self, page_num=0, page_size=None):
        sites_data = self.root().project().admin.multisites.sites_data.get()
        return sites_data.keys()

    def columns(self):
        return ['Name', 'Status']

    def _fill_row_cells(self, row, item):
        row['Status'] = item.status.get()
        name = item.name()

        if name == self.version.site.get():
            name += " (S)"
        
        row['Name'] = name


class RequestedRevisions(flow.DynamicMap):
    
    STYLE_BY_STATUS = {
        'Available': ('#45cc3d', ('icons.libreflow', 'blank')),
        'Requested': ('#b9c2c8', ('icons.libreflow', 'exclamation-sign-colored')),
        'NotAvailable': ('#cc3b3c', ('icons.libreflow', 'blank')),
        'Undefined': ('#cc3b3c', ('icons.libreflow', 'unavailable')),
    }
    
    request_action = flow.Parent()
    oids = flow.SessionParam([]).ui(editor='set')
    
    def mapped_names(self, page_num=0, page_size=None):
        return self.oids.get()
    
    def get_mapped(self, name):
        if not self.has_mapped_name(name):
            raise MappedNameError(self.oid(), name)

        try:
            obj = self._mng.get_object(name)
        except ValueError:
            raise

        return obj
    
    def columns(self):
        return ['Revision']
    
    def _fill_row_cells(self, row, item):
        row['Revision'] = item.oid()
    
    def _fill_row_style(self, style, item, row):
        status = 'Undefined'
        
        if hasattr(item, 'request_as'):
            status = item.get_sync_status(site_name=self.request_action.sites.target_site.get())
            
        style['Revision_foreground-color'] = self.STYLE_BY_STATUS[status][0]
        style['Revision_icon'] = self.STYLE_BY_STATUS[status][1]


class RequestRevisions(flow.Action):
    
    ICON = ('icons.gui', 'share-option')

    pattern = flow.SessionParam("").ui(
        placeholder="Revision oid pattern"
    )
    
    sites = flow.Child(SiteSelection).ui(expanded=True)
    revisions = flow.Child(RequestedRevisions).ui(expanded=True)
    
    def allow_context(self, context):
        current_site = self.root().project().get_current_site()
        return context and current_site.request_files_from_anywhere.get()
    
    def _get_oid(self, pattern_str):
        oids = []
        patterns = []
        
        for pattern in pattern_str.split(';'):
            patterns += self.resolve_pattern(pattern)
        
        for pattern in patterns:
            oids += self.glob(self.root().project().oid(), pattern, 0)
        
        return oids

    def get_buttons(self):
        self.sites.source_site.set(self.root().project().get_current_site().name())
        target_site_choices = self.sites.target_site.choices()
        
        if not target_site_choices:
            msg = self.message.get()
            if msg is None:
                msg = ''
            
            msg += (
                '<h3><font color="#D5000D">Making requests is not possible since '
                'there is no other site defined for this project.</font></h3>'
            )
            self.message.set(msg)
            
            return ['Close']
        
        self.sites.target_site.set(target_site_choices[0])

        return ["Request", "Refresh revision list", "Close"]
    
    def ls(self, root_oid):
        related_info, mapped_names = self.root().session().cmds.Flow.ls(root_oid)
        relation_oids = [rel_info[0] for rel_info in related_info]
        mapped_oids = ["%s/%s" % (root_oid, name) for name in mapped_names]
        
        return relation_oids + mapped_oids
    
    def get_last_publication(self, file_oid):
        o = self.root().get_object(file_oid)
        
        try:
            head = o.get_head_revision()
        except AttributeError:
            return None
        
        if not head:
            return None
        
        return head.name()
    
    def glob(self, root_oid, pattern, level):
        if level >= pattern.count("/") - 1:
            return [root_oid]

        matches = []
        level_pattern = "/".join(pattern.split("/")[:level + 3])

        if level_pattern.endswith("[last]"):
            file_oid = self.root().session().cmds.Flow.resolve_path(root_oid + "/../..")
            head_name = self.get_last_publication(file_oid)

            if not head_name:
                return []
            
            pattern = pattern.replace("[last]", head_name)
            level_pattern = level_pattern.replace("[last]", head_name)
        
        for oid in self.ls(root_oid):
            if fnmatch.fnmatch(oid, level_pattern):
                matches += self.glob(oid, pattern, level + 1)
        
        return matches
    
    def resolve_pattern(self, pattern_oid):
        '''
        Returns a list of patterns which correspond to all substitution combinations of `pattern_oid`.
        Substitute string are specified in `pattern_oid` between brackets and separated with comas (`{s0, s1, ...}`).
        '''
        match = re.search(r'{[^{}]+}', pattern_oid)

        if not match:
            return [pattern_oid]

        substitutes = match.group()[1:-1].split(',')
        substitutes = [sub.replace(' ', '') for sub in substitutes]

        sub_oids = [pattern_oid.replace(match.group(), sub, 1) for sub in substitutes]
        oids = []

        for sub_oid in sub_oids:
            oids += self.resolve_pattern(sub_oid)
        
        return oids
    
    def run(self, button):
        if button == "Close":
            return
        elif button == "Refresh revision list":
            self.revisions.oids.revert_to_default()
            oids = self._get_oid(self.pattern.get())
            self.revisions.oids.set(oids)
            self.revisions.touch()
            
            return self.get_result(close=False)
        
        source_site = self.sites.source_site.get()
        target_site = self.sites.target_site.get()
        
        for obj in self.revisions.mapped_items():
            # Skip objects which are not file revisions
            if not hasattr(obj, 'request_as'):
                continue
            # Skip revisions which are not available on selected source site
            if obj.get_sync_status(site_name=source_site) != 'Available':
                continue

            # Skip revisions which are already available on selected target site
            status = obj.get_sync_status(site_name=target_site)
            if status == 'Requested' or status == 'Available':
                continue
            
            obj.request_as.sites.source_site.set(source_site)
            obj.request_as.sites.target_site.set(target_site)
            obj.request_as.include_dependencies.set(False)
            obj.request_as.run(None)
        
        self.revisions.touch()

        return self.get_result(close=False)


class SiteMultiSelection(flow.Object):
    
    source_site = flow.Param('Auto select', ActiveSiteAutoSelectChoiceValue).watched()
    target_sites = flow.Param([], ActiveSitesMultichoiceValue)
    
    def child_value_changed(self, child_value):
        if child_value is self.source_site:
            source_site = self.source_site.get()
            
            if source_site == 'Auto select':
                self.target_sites.exclude_choice.set(None)
            else:
                self.target_sites.exclude_choice.set(self.source_site.get())
            
            self.target_sites.touch()


class MultiRequestedRevisions(RequestedRevisions):
    
    STYLE_BY_STATUS = {
        'Available': ('#45cc3d', ('icons.libreflow', 'checked-symbol-colored')),
        'Requested': ('#b9c2c8', ('icons.libreflow', 'exclamation-sign-colored')),
        'NotAvailable': ('#cc3b3c', ('icons.libreflow', 'blank')),
        'Undefined': ('#cc3b3c', ('icons.libreflow', 'unavailable')),
    }
    
    request_action = flow.Parent()
    source_sites = flow.SessionParam([]).ui(hidden=True)
    
    def columns(self):
        site_names = self.request_action.sites.target_sites.get() + self.source_sites.get()
        site_names = list(dict.fromkeys(site_names))

        return ['Revision'] + site_names
    
    def _fill_row_cells(self, row, item):
        row['Revision'] = item.oid()
        
        for col in self.columns()[1:]:
            row[col] = ''
    
    def _fill_row_style(self, style, item, row):
        style['Revision_icon'] = ('icons.libreflow', 'blank')
        
        if not hasattr(item, 'request_as'):
            style['Revision_icon'] = self.STYLE_BY_STATUS['Undefined'][1]
            return
        
        site_names = self.request_action.sites.target_sites.get() + self.source_sites.get()
        site_names = list(dict.fromkeys(site_names))

        for site_name in site_names:
            status = item.get_sync_status(site_name=site_name)
            style[site_name + '_icon'] = self.STYLE_BY_STATUS[status][1]


class MultiRequestRevisions(RequestRevisions):
    
    ICON = ('icons.libreflow', 'multi-share-option')
    
    sites = flow.Child(SiteMultiSelection).ui(expanded=True)
    revisions = flow.Child(MultiRequestedRevisions).ui(expanded=True)
    
    def get_buttons(self):
        self.sites.source_site.revert_to_default()
        target_sites_choices = self.sites.target_sites.choices()
        
        if not target_sites_choices:
            msg = self.message.get()
            if msg is None:
                msg = ''
            
            msg += (
                '<h3><font color="#D5000D">Making requests is not possible since '
                'there is no other site defined for this project.</font></h3>'
            )
            self.message.set(msg)
            
            return ['Close']

        return ['Request', 'Refresh revision list', 'Close']
    
    def run(self, button):
        if button == 'Close':
            return
        elif button == 'Refresh revision list':
            self.revisions.oids.revert_to_default()
            oids = self._get_oid(self.pattern.get())
            self.revisions.oids.set(oids)

            source_sites = []
            for oid in oids:
                site_name = self.root().session().cmds.Flow.get_value(oid + '/site')
                source_sites.append(site_name)
            
            self.revisions.source_sites.set(source_sites)
            self.revisions.touch()
            
            return self.get_result(close=False)
        
        source_site = self.sites.source_site.get()
        auto_select_enabled = (source_site == 'Auto select')
        
        for obj in self.revisions.mapped_items():
            # Skip objects which are not file revisions
            if not hasattr(obj, 'request_as'):
                continue
            # Skip revisions which are not available on selected source site
            if not auto_select_enabled and obj.get_sync_status(site_name=source_site) != 'Available':
                continue
            
            for target_site in self.sites.target_sites.get():
                # Skip revisions which are already available on selected target site
                status = obj.get_sync_status(site_name=target_site)
                if status == 'Requested' or status == 'Available':
                    continue
                
                if not auto_select_enabled:
                    obj.request_as.sites.source_site.set(source_site)
                
                obj.request_as.sites.target_site.set(target_site)
                obj.request_as.sites.auto_select_enabled.set(auto_select_enabled)
                obj.request_as.include_dependencies.set(False)
                obj.request_as.run(None)
        
        self.revisions.touch()

        return self.get_result(close=False)


class UploadRevision(flow.Action):
    
    _revision = flow.Parent()
    _revisions = flow.Parent(2)
    
    def needs_dialog(self):
        return self._revision.get_sync_status(exchange=True) == 'Available'
    
    def allow_context(self, context):
        return (
            context
            and not self._revision.is_working_copy()
            and self._revision.get_sync_status() == 'Available'
        )
    
    def get_buttons(self):  
        self.message.set((
            '<h3>Revision already available on exchange server</h3>'
            'Upload and overwrite it anyway ?'
        ))
        return ['Confirm', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return

        current_site = self.root().project().get_current_site()
        # Add an upload job for the current site
        job = current_site.get_queue().submit_job(
            job_type='Upload',
            init_status='WAITING',
            emitter_oid=self._revision.oid(),
            user=self.root().project().get_user_name(),
            studio=current_site.name(),
        )
        sync_manager = self.root().project().get_sync_manager()
        sync_manager.process(job)
        
        self._revisions.touch()


class DownloadRevision(flow.Action):
    
    _revision = flow.Parent()
    _revisions = flow.Parent(2)

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return context and self._revision.get_sync_status() != 'Available'
    
    def run(self, button):
        if button == 'Cancel':
            return

        current_site = self.root().project().get_current_site()
        # Add an upload job for the current site
        job = current_site.get_queue().submit_job(
            job_type='Download',
            init_status='WAITING',
            emitter_oid=self._revision.oid(),
            user=self.root().project().get_user_name(),
            studio=current_site.name(),
        )
        self._revision.set_sync_status('Requested', current_site.name())
        sync_manager = self.root().project().get_sync_manager()
        sync_manager.process(job)
        
        self._revisions.touch()
