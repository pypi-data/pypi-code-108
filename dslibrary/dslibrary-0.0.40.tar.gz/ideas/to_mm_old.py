"""
An adapter for MMLibrary that simply delegates the calls to the existing (old) mmlibrary.
"""
import io
import json
import typing
from ..front import MMLibrary, MMException
from ..metadata import Metadata
# import the old mmlibrary
from .old_mm import *


class MMLibraryToOld(MMLibrary):
    def get_metadata(self, model_uri: str=None) -> Metadata:
        # TODO fill in model uri, at least
        # TODO fill in parameter metadata
        return Metadata()

    def get_arguments(self):
        raise MMException("not implemented")

    def get_argument(self, argument_name: str, default=None):
        try:
            get_argument(argument_name)
        except ValueError:
            return default

    def _open_reader_for_data(self, data: (str, bytes, bytearray), mode: str):
        if 'b' in mode:
            return io.BytesIO(data)
        else:
            return io.StringIO(data.decode("utf-8"))

    def _open_writer_with_save(self, save_binary, mode: str):
        if 'b' in mode:
            class WB(io.BytesIO):
                def close(self) -> None:
                    save_binary(self.getvalue())
            return WB()
        else:
            class WS(io.StringIO):
                def close(self) -> None:
                    save_binary(self.getvalue().encode("utf-8"))
            return WS()

    def open_resource(self, resource_name: str, mode: str='rb') -> io.IOBase:
        if 'r' in mode:
            bin = get_binary_from_resource(resource_name)
            return self._open_reader_for_data(bin, mode)
        else:
            return self._open_writer_with_save(lambda bin: save_binary_to_resource(resource_name, bin), mode)

    def open_run_data(self, filename: str, mode: str='rb') -> io.IOBase:
        if 'r' in mode:
            data = get_temporary_data()
            if isinstance(data, dict):
                part = data.get(filename)
                if not isinstance(part, (str, bytes, bytearray)):
                    part = json.dumps(part)
                return self._open_reader_for_data(part)
            return self._open_reader_for_data(b'', mode)
        data = get_temporary_data()
        if not isinstance(data, dict):
            data = {}
        def writer(part):
            data[filename] = json.loads(part)
            save_temporary_data(data)
        return self._open_writer_with_save(writer, mode)

    def open_model_binary(self, part: str=None, mode: str='rb') -> io.IOBase:
        return open(get_model(), mode=mode)

    def get_metrics(self, metric_name: str = None, uri: str = None, time_range: (list, tuple) = None, limit: int = None) -> typing.Iterable:
        raise MMException("not implemented")

    def save_metric(self, metric_name: str, metric_value) -> None:
        save_kpi(kpi_name=metric_name, kpi_value=metric_value)

    def get_last_metric(self, metric_name: str):
        return get_last_kpi(metric_name)

    def set_evaluation_result(self, success: bool, message: str = None) -> None:
        if not success:
            evaluation_result(message)

    def scoring_response(self, score) -> None:
        return_score(score)

    def is_scoring_mode(self):
        raise MMException("not implemented")

    def get_db_connection(self, connection_name: str, database: str = None):
        return get_db_connection(connection_name)

    def iter_scoring_requests(self, callback=None):
        raise MMException("not implemented")

    def run(self, code_uri: str, arguments: dict = None, callback=None):
        raise MMException("not implemented")
