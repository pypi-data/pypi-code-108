import glob
import os
import tempfile
import zipfile

from seeq.base import system
from seeq.spy import _common
from seeq.spy._errors import *
from seeq.spy._status import Status
from seeq.spy.workbooks._workbook import Workbook


def load(folder_or_zipfile):
    """
    Loads a list of workbooks from a folder on disk into Workbook objects in
    memory.

    Parameters
    ----------
    folder_or_zipfile : str
        A folder or zip file on disk containing workbooks to be loaded. Note
        that any subfolder structure will work -- this function will scan for
        any subfolders that contain a Workbook.json file and assume they should
        be loaded.
    """
    status = Status()

    _common.validate_argument_types([
        (folder_or_zipfile, 'folder_or_zipfile', str)
    ])

    folder_or_zipfile = system.cleanse_path(folder_or_zipfile)

    try:
        if not os.path.exists(folder_or_zipfile):
            raise SPyRuntimeError('Folder/zipfile "%s" does not exist' % folder_or_zipfile)

        if folder_or_zipfile.lower().endswith('.zip'):
            with tempfile.TemporaryDirectory() as temp:
                with zipfile.ZipFile(folder_or_zipfile, "r") as z:
                    status.update('Unzipping "%s"' % folder_or_zipfile, Status.RUNNING)
                    z.extractall(temp)

                status.update('Loading from "%s"' % temp, Status.RUNNING)
                workbooks = _load_from_folder(temp)
        else:
            status.update('Loading from "%s"' % folder_or_zipfile, Status.RUNNING)
            workbooks = _load_from_folder(folder_or_zipfile)

        status.update('Success', Status.SUCCESS)
        return workbooks

    except KeyboardInterrupt:
        status.update('Load canceled', Status.CANCELED)


def _load_from_folder(folder):
    workbook_json_files = glob.glob(os.path.join(folder, '**', 'Workbook.json'), recursive=True)

    workbooks = list()
    for workbook_json_file in workbook_json_files:
        workbooks.append(Workbook.load(os.path.dirname(workbook_json_file)))

    return workbooks
