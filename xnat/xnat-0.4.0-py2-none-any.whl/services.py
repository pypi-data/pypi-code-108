# Copyright 2011-2015 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import unicode_literals
import datetime
import mimetypes
import collections
import os
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

import six
from six import BytesIO

from .core import XNATBaseObject
from .prearchive import PrearchiveSession
from .exceptions import XNATResponseError, XNATValueError
from .mixin import ProjectData, SubjectData, ExperimentData

TokenResult = collections.namedtuple('TokenResult', ('alias', 'secret'))


class DicomBoxImportRequest(object):
    def __init__(self, uri, xnat_session):
        self._xnat_session = xnat_session
        self._data = None
        self.uri = uri
        self._update_data()

    def _update_data(self):
        self._data = self._xnat_session.get_json(self.uri)

    @property
    def status(self):
        self._update_data()
        return self._data['status']

    @property
    def id(self):
        return self._data['id']

    @property
    def username(self):
        return self._data['username']

    @property
    def project_id(self):
        return self._data['parameters'].get('PROJECT_ID')

    @property
    def subject_id(self):
        return self._data['parameters'].get('SUBJECT_ID')

    @property
    def session_path(self):
        return self._data['sessionPath']

    @property
    def cleanup_after_import(self):
        return self._data['clenaupAfterImport']

    @property
    def enabled(self):
        return self._data['enabled']

    @property
    def created(self):
        return datetime.datetime.fromtimestamp(self._data['created'] / 1000.0)

    @property
    def timestamp(self):
        return datetime.datetime.fromtimestamp(self._data['timestamp'] / 1000.0)


class Services(object):
    """
    The class representing all service functions in XNAT found in the
    /data/services REST directory
    """
    def __init__(self, xnat_session):
        self._xnat_session = xnat_session

    @property
    def xnat_session(self):
        return self._xnat_session

    def guess_content_type(self, path):
        content_type, _ = mimetypes.guess_type(path)

        if content_type not in ['application/x-tar', 'application/zip']:
            if path.endswith('.zip'):
                self.xnat_session.logger.warning(
                    'Found unexpect content type, but assuming zip based on the extension'
                )
                content_type = 'application/zip'
            elif path.endswith('.tar.gz'):
                self.xnat_session.logger.warning(
                    'Found unexpect content type, but assuming tar based on the extension'
                )
                content_type = 'application/x-tar'
            else:
                self.xnat_session.logger.warning(
                    'Found unexpected content (found type {}), this could result in errors on import!'.format(content_type)
                )

        return content_type

    def dicom_dump(self, src, fields=None):
        """
        Retrieve a dicom dump as a JSON data structure
        See the XAPI documentation for more detailed information: `DICOM Dump Service <https://wiki.xnat.org/display/XAPI/DICOM+Dump+Service+API>`_

        :param str src: The url of the scan to generate the DICOM dump for
        :param list fields: Fields to filter for DICOM tags. It can either a tag name or tag number in the format GGGGEEEE (G = Group number, E = Element number)
        :return: JSON object (dict) representation of DICOM header
        :rtype: dict
        """
        query_string = {'src': src}
        if fields is not None:
            if not isinstance(fields, (list, str)):
                raise XNATValueError('The fields argument to .dicom_dump() should be list or a str and not {}'.format(type(fields)))
            query_string['field'] = fields

        return self.xnat_session.get_json('/data/services/dicomdump', query=query_string)['ResultSet']['Result']

    def import_(self, path, overwrite=None, quarantine=False, destination=None,
                trigger_pipelines=None, project=None, subject=None,
                experiment=None, content_type=None, import_handler=None):
        """
        Import a file into XNAT using the import service. See the
        `XNAT wiki <https://wiki.xnat.org/pages/viewpage.action?pageId=6226268>`_
        for a detailed explanation.

        :param str path: local path of the file to upload and import
        :param str overwrite: how the handle existing data (none, append, delete)
        :param bool quarantine: flag to indicate session should be quarantined
        :param bool trigger_pipelines: indicate that archiving should trigger pipelines
        :param str destination: the destination to upload the scan to
        :param str project: the project in the archive to assign the session to
                            (only accepts project ID, not a label)
        :param str subject: the subject in the archive to assign the session to
        :param str experiment: the experiment in the archive to assign the session content to
        :param str content_type: overwite the content_type (by default the mimetype will be
                                 guessed using the ``mimetypes`` package).
                                 This will often be ``application/zip``.
        :return:

        .. note::
            The project has to be given using the project ID and *NOT* the label.

        .. warning::
            On some systems the guessed mimetype of a zip file might not be ``application/zip``
            but be something like ``application/x-zip-compressed``. In that case you might have to
            set the ``content_type`` parameter to ``application/zip`` manually.

        """

        if not os.path.exists(path):
            raise FileNotFoundError("The file you are trying to import does not exist.")

        query = {}
        if overwrite is not None:
            if overwrite not in ['none', 'append', 'delete']:
                raise ValueError('Overwrite should be none, append or delete!')
            query['overwrite'] = overwrite

        if quarantine:
            query['quarantine'] = 'true'

        if trigger_pipelines is not None:
            if isinstance(trigger_pipelines, bool):
                if trigger_pipelines:
                    query['triggerPipelines'] = 'true'
                else:
                    query['triggerPipelines'] = 'false'
            else:
                raise TypeError('trigger_pipelines should be a boolean')

        if destination is not None:
            query['dest'] = destination

        if project is not None:
            if isinstance(project, ProjectData):
                project = project.id
            query['project'] = project

        if subject is not None:
            if isinstance(subject, SubjectData):
                subject = subject.label
            query['subject'] = subject

        if experiment is not None:
            if isinstance(experiment, ExperimentData):
                experiment = experiment.label
            query['session'] = experiment

        if import_handler is not None:
            query['import-handler'] = import_handler

        # Get mimetype of file
        if content_type is None and isinstance(path, six.string_types):
            content_type = self.guess_content_type(path)

        uri = '/data/services/import'
        response = self.xnat_session.upload(uri=uri, file_=path, query=query, content_type=content_type, method='post')

        if response.status_code != 200:
            raise XNATResponseError('The response for uploading was ({}) {}'.format(response.status_code, response.text))

        # Create object, the return text should be the url, but it will have a \r\n at the end that needs to be stripped
        response_text = response.text.strip()
        if response_text.startswith('/data/prearchive'):
            return PrearchiveSession(response_text, self.xnat_session)

        return self.xnat_session.create_object(response_text)

    def _zip_directory(self, directory, fh):
        """
        Zip a directory into a file(-like) obj given

        :param directory: directory to zip
        :param fh: output file handle
        """
        with ZipFile(fh, 'w', ZIP_DEFLATED) as zip_file:
            for dirpath, dirs, files in os.walk(directory):
                for f in files:
                    zip_file.write(os.path.join(dirpath, f),
                                   os.path.relpath(os.path.join(dirpath, f),
                                                   os.path.dirname(directory)))

    def import_dir(self, directory, overwrite=None, quarantine=False, destination=None,
                trigger_pipelines=None, project=None, subject=None,
                experiment=None, method='zip_file', import_handler=None):
        """
        Import a directory to an XNAT resource.

        :param str directory: local path of the directory to upload and import
        :param str overwrite: how the handle existing data (none, append, delete)
        :param bool quarantine: flag to indicate session should be quarantined
        :param bool trigger_pipelines: indicate that archiving should trigger pipelines
        :param str destination: the destination to upload the scan to
        :param str project: the project in the archive to assign the session to
                            (only accepts project ID, not a label)
        :param str subject: the subject in the archive to assign the session to
        :param str experiment: the experiment in the archive to assign the session content to


        The method has 2 options, default is zip_file:

        #. ``zip_file``: Create a temporary zip file and upload that
        #. ``zip_memory``: Create a temporary zip file in memory and upload it

        The considerations are that sometimes you can fit things in memory so
        you can save disk IO by putting it in memory.

        """
        # Make sure that a None or empty string is replaced by the default
        method = method or 'zip_file'

        content_type = 'application/zip'
        if method == 'zip_file':
            # Max-size is 256 MB
            fh = tempfile.SpooledTemporaryFile(max_size=268435456, mode='wb+')
            self._zip_directory(directory=directory, fh=fh)
        elif method == 'zip_memory':
            fh = BytesIO()
            self._zip_directory(directory=directory, fh=fh)
        else:
            message = 'Selected invalid import directory method: {}!'.format(method)
            self.xnat_session.logger.error(message)
            raise XNATValueError(message)

        fh.seek(0)
        session = self.import_(fh, overwrite, quarantine, destination,
                               trigger_pipelines, project, subject,
                               experiment, content_type, import_handler=import_handler)
        fh.close()
        return session

    def import_dicom_inbox(self, path, cleanup=False, project=None, subject=None, experiment=None):
        """
        Import a file into XNAT using the import service. See the
        `XNAT wiki <https://wiki.xnat.org/pages/viewpage.action?pageId=6226268>`_
        for a detailed explanation.

        :param str path: local path of the file to upload and import
        :param str cleanup: remove the files after importing them (default false)
        :param str project: the project in the archive to assign the session to
                            (only accepts project ID, not a label)
        :param str subject: the subject in the archive to assign the session to
        :param str experiment: the experiment in the archive to assign the session content to
        :return:

        .. note::
            The project and subject has to be given using the ID and *NOT* the label/name.
        """
        query = {
            'import-handler': 'inbox',
            'path': path,
        }

        if cleanup:
            query['cleanupAfterImport'] = 'true'
        else:
            query['cleanupAfterImport'] = 'false'

        if project is not None:
            if isinstance(project, ProjectData):
                project = project.id
            query['PROJECT_ID'] = project

        if subject is not None:
            if isinstance(subject, SubjectData):
                subject = subject.id
            query['SUBJECT_ID'] = subject

        if experiment is not None:
            if isinstance(experiment, ExperimentData):
                experiment = experiment.label
            query['EXPT_LABEL'] = experiment

        uri = '/data/services/import'
        response = self.xnat_session.post(uri, query=query)

        if response.status_code != 200:
            raise XNATResponseError('The response for uploading was ({}) {}'.format(response.status_code, response.text))

        # Create object, the return text should be the url, but it will have a \r\n at the end that needs to be stripped
        response_text = response.text.strip()
        if response_text.startswith('/data/prearchive'):
            return PrearchiveSession(response_text, self.xnat_session)

        return DicomBoxImportRequest(response_text, self._xnat_session)

    def issue_token(self, user=None):
        """
        Issue a login token, by default for the current logged in user. If
        username is given, for that user. To issue tokens for other users
        you must be an admin.

        :param str user: User to issue token for, default is current user
        :return: Token in a named tuple (alias, secret)
        """
        uri = '/data/services/tokens/issue'
        if user:
            uri += '/user/{}'.format(user)

        result = self.xnat_session.get_json(uri)

        return TokenResult(result['alias'], result['secret'])

    def refresh_catalog(self, resource, checksum=False, delete=False, append=False, populate_stats=False):
        """
        Call for a refresh of the catalog, see https://wiki.xnat.org/display/XAPI/Catalog+Refresh+API for
        details.

        Introduced with XNAT 1.6.2, the refresh catalog service is used to update catalog xmls that are out of
        sync with the file system.  This service can be used to store checksums for entries that are missing the,
        remove entries that no longer have valid files, or add new entries for files that have been manually
        added to the archive directory.

        When using this feature to add files that have been manually added to the archive directory, you must
        have placed the files in the appropriate archive directory (in the same directory as the generated
        catalog xml or a sub-directory).  The catalog xml should already exist before triggering this service.
        If you haven't generated the catalog yet, you can do so by doing a PUT to the resource URL
        (i.e. /data/archive/experiments/ID/resources/TEST).

        Extra parameters indicate operations to perform on the specified resource(s) during the refresh.
        If non are given, then the catalog will be reviewed and updated for validity, but nothing else.

        :param resource: XNATObject or uri indicating the resource to use
        :param bool checksum: generate checksums for any entries that are missing them
        :param bool delete: remove entries that do not reference valid files
        :param bool append: add entries for files in the catalog directory (or sub-directory)
        :param bool populate_stats: updates the statistics for the resource in the XNAT abstract resource table.
        :return:
        """
        if isinstance(resource, XNATBaseObject):
            resource = resource.fulluri

        options = []

        # Check which options to add
        if checksum:
            options.append('checksum')

        if delete:
            options.append('delete')

        if append:
            options.append('append')

        if populate_stats:
            options.append('populateStats')

        # Make query that only contains options if any are given
        query = {'resource': resource}

        if options:
            query['options'] = options

        self.xnat_session.post('/data/services/refresh/catalog', query=query)
