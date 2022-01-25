import io
import json
import os
import shutil
from collections import OrderedDict
from pathlib import Path

from _pistar.pistar_pytest.models import ATTACHMENT_PATTERN
from _pistar.pistar_pytest.models import Attachment
from _pistar.pistar_pytest.utils import now, write_attr
from _pistar.utilities.constants import ENCODE
from _pistar.utilities.constants import FILE_MODE


class Reporter:
    def __init__(self, report_dir):
        self._report_base = report_dir
        self._report_dir = report_dir
        self._items = OrderedDict()
        self._finished = list()
        # current case uuid
        self._cur_case = None

    def set_file_finished(self, finish):
        write_attr(finish, self._report_dir, "finished.json")

    def update_file_output_path(self, folder_md5):
        self._report_dir = os.path.join(self._report_base, folder_md5)

        if os.path.exists(self._report_dir):
            shutil.rmtree(self._report_dir)
        os.makedirs(self._report_dir)

    def update_cur_file(self, cur_file):
        data = dict()
        data["cur_script"] = cur_file
        destination = os.path.join(self._report_base, "task_meta_info.json")
        with io.open(destination, mode=FILE_MODE.WRITE, encoding=ENCODE.UTF8) as json_file:
            json.dump(data, json_file, ensure_ascii=False)

    def _update_item(self, uuid, **kwargs):
        item = self._items[uuid] if uuid else self._items[next(reversed(self._items))]
        for key, value in kwargs.items():
            setattr(item, key, value)

    def schedule_test(self, uuid, test_case):
        self._cur_case = uuid
        self._items[uuid] = test_case

    def close_test(self, uuid):
        test_case = self._items.pop(uuid)
        self._cur_case = None
        self.report_item(test_case, uuid)

    def get_test(self, uuid: str):
        if uuid:
            return self.get_item(uuid)
        else:
            return self.get_item(self._cur_case)

    def get_item(self, uuid: str):
        return self._items.get(uuid)

    def _last_executable(self):

        return next(reversed(self._items))

    def start_before_fixture(self, uuid, fixture):
        self._items[uuid] = fixture

    def stop_before_fixture(self, uuid, **kwargs):
        self._update_item(uuid, **kwargs)
        self._items.pop(uuid)

    def start_after_fixture(self, uuid, fixture):
        self._items[uuid] = fixture

    def stop_after_fixture(self, uuid, **kwargs):
        self._update_item(uuid, **kwargs)
        fixture = self._items.pop(uuid)
        fixture.stop = now()

    def report_item(self, item, uuid):
        filename = item.file_pattern.format(prefix=uuid)
        write_attr(item, self._report_dir, filename)

    def attach_data(self, uuid, body, name=None, attachment_type=None):
        file_name = self._attach(uuid, name=name, attachment_type=attachment_type)
        self.report_attached_data(body=body, file_name=file_name)

    def _attach(self, uuid, name=None, attachment_type=None):

        extension = attachment_type.extension
        mime_type = attachment_type.mime_type

        file_name = ATTACHMENT_PATTERN.format(prefix=uuid, ext=extension)
        file_abs_name = os.path.join(self._report_dir, file_name)
        attachment = Attachment(path=file_abs_name, name=name, type=mime_type)
        last_uuid = self._last_executable()
        self._items[last_uuid].attachments.append(attachment)

        return file_name

    def report_attached_data(self, body, file_name):
        destination = Path(self._report_dir).joinpath(file_name)
        with destination.open(mode="wb") as f:
            f.write(body.encode("utf-8"))
