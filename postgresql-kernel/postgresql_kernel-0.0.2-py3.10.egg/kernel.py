import os
from pydoc import Helper
import re
import sys
import json
import traceback
from pathlib import Path
from select import select

from traitlets import Dict as tDict
from metakernel import MetaKernel, ExceptionWrapper
# from IPython.display import Image, SVG

from tabulate import tabulate
import psycopg2
from psycopg2 import Error, OperationalError
from psycopg2.extensions import (
    QueryCanceledError, POLL_OK, POLL_READ, POLL_WRITE, STATUS_BEGIN
)
from typing import Any, List, Optional, TypedDict, Iterable, Sequence, Mapping, Union, Tuple, Dict
from . import __version__

KernelDictType = TypedDict(
    'KernelDictType',
    {
        "argv": List[str],
        "display_name": str,
        "mimetype": str,
        "language": str,
        "name": str
    },
    total=False)

HelpLinkDictType = TypedDict(
    'HelpLinkDictType',
    {
        "text": str,
        "url": str
    },
    total=False)

LanguageInfoDictType = TypedDict(
    'LanguageInfoDictType',
    {
        'mimetype': str,
        'name': str,
        'file_extension': str,
        'version': str,
        'help_links': List[HelpLinkDictType]
    },
    total=False)

version_pat = re.compile(r'^PostgreSQL (\d+(\.\d+)+)')
CONN_STRING_COMMENT = re.compile(r'--\s*connection:\s*(.*)\s*$')
AUTOCOMMIT_SWITCH_COMMENT = re.compile(r'--\s*autocommit:\s*(\w+)\s*$')

HELP_LINKS: List[HelpLinkDictType] = [
    {
        'text': "PostgreSQL",
        'url': "http://www.postgres.cn/docs/12/index.html",
    },
    {
        'text': "SQL",
        'url': "https://blog.hszofficial.site/TutorialForSQL/#/",
    },


] + MetaKernel.help_links


def get_kernel_json() -> KernelDictType:
    """Get the kernel json for the kernel."""
    here = Path(__file__)
    default_json_file = here.parent.joinpath('kernel.json')
    json_file = os.environ.get('POSTGRESQL_KERNEL_JSON', default_json_file)
    with open(json_file) as fid:
        data = json.load(fid)
    data['argv'][0] = sys.executable
    return data


def wait_select_inter(conn: "psycopg2.connection") -> None:
    """等待连接建立.

    Args:
        conn (psycopg2.connection): pg的连接

    Raises:
        conn.OperationalError: 连接报错
    """
    while 1:
        try:
            state = conn.poll()
            if state == POLL_OK:
                break
            elif state == POLL_READ:
                select([conn.fileno()], [], [])
            elif state == POLL_WRITE:
                select([], [conn.fileno()], [])
            else:
                raise conn.OperationalError(
                    "bad state from poll: %s" % state)
        except KeyboardInterrupt:
            conn.cancel()
            continue


class MissingConnection(Exception):
    """连接丢失异常."""
    pass


class RowsDisplay:
    def __init__(self, header: Union[str, Dict[str, str], Sequence[str]], rows: Union[Mapping[str, Iterable], Iterable[Iterable]]) -> None:
        self.header = header
        self.rows = rows

    def __repr__(self) -> str:
        return tabulate(self.rows, self.header, tablefmt='latex_booktabs')

    def _repr_html_(self) -> str:
        return tabulate(self.rows, self.header, tablefmt='html')

    def _repr_latex_(self) -> str:
        return tabulate(self.rows, self.header, tablefmt='latex_booktabs')


class PostgreSQLKernel(MetaKernel):

    app_name: str = 'postgresql_kernel'
    implementation: str = 'PostgreSQL Kernel'
    implementation_version: str = __version__
    language: str = 'sql'
    help_links: List[HelpLinkDictType] = HELP_LINKS
    kernel_json: tDict = tDict(get_kernel_json()).tag(config=True)
    _language_version: Optional[str] = None
    _banner: Optional[str] = None

    _conn_string: str
    _autocommit: bool
    _conn: Optional["psycopg2.connection"]

    @property
    def language_version(self) -> str:
        if self._language_version:
            return self._language_version
        if self.banner:
            m = version_pat.search(self.banner)
            if m:
                self._language_version = m.group(1)
                return self._language_version
            else:
                return "unknown"
        else:
            return "unknown"

    @property
    def banner(self) -> Optional[str]:
        if self._banner is None:
            if self._conn is None:
                return 'not yet connected to a database'
            res = self.fetchone('SELECT VERSION();')
            if res and len(res) >= 1 and isinstance(res[0], str):
                self._banner = res[0]
        return self._banner

    @property
    def language_info(self) -> LanguageInfoDictType:
        return {'mimetype': 'text/x-sql',
                'name': 'sql',
                'file_extension': '.sql',
                'version': self.language_version,
                'help_links': HELP_LINKS}

    def __init__(self, *args: Any, **kwargs: Any):
        super(PostgreSQLKernel, self).__init__(*args, **kwargs)
        psycopg2.extensions.set_wait_callback(wait_select_inter)
        self._conn_string = os.getenv('DATABASE_URL', '')
        self._autocommit = True
        self._conn = None
        if self._conn_string:
            self._start_connection()

    def _start_connection(self) -> None:
        """与pg建立连接."""
        self.log.info('starting connection')
        try:
            self._conn = psycopg2.connect(self._conn_string)
            self._conn.autocommit = self._autocommit
        except OperationalError:
            self.log.info(f'failed to connect to {self._conn_string}')
            message = f'''Failed to connect to a database at {self._conn_string}'''
            self.send_response(self.iopub_socket, 'stream',
                               {'name': 'stderr', 'text': message})

    def fetchone(self, query: str) -> Optional[Sequence[Union[str, bytes, int, float]]]:
        """拉取一行数据

        Args:
            query (str): 请求的sql语句

        Returns:
            Optional[Sequence[Union[str, bytes, int, float]]]: 获取的结果
        """
        if self._conn:
            self.log.info(f'fetching one from: \n{query}')
            with self._conn.cursor() as c:
                c.execute(query)
                one = c.fetchone()
                self.log.info(one)
                return one
        return None

    def fetchall(self, query: str) -> Tuple[Optional[List[str]], Optional[List[Sequence[Union[str, bytes, int, float]]]]]:
        """拉取多行数据.

        Args:
            query (str): 请求的sql

        Returns:
            [type]: [description]
        """
        if not self._conn:
            raise Exception("need to connect to pg first")
        else:
            self.log.info(f'fetching all from: \n{query}')
            with self._conn.cursor() as c:
                c.execute(query)
                desc = c.description
                if desc:
                    keys = [col[0] for col in desc]
                    return keys, c.fetchall()
                return None, None

    def change_connection(self, conn_string: str) -> None:
        """更换连接的库."""
        self._conn_string = conn_string
        self._start_connection()

    def switch_autocommit(self, switch_to: bool) -> bool:
        """切换是否要自动提交."""
        self._autocommit = switch_to
        committed = False
        if self._conn:
            if self._conn.get_transaction_status() == STATUS_BEGIN:
                committed = True
                self._conn.commit()
            self._conn.autocommit = switch_to
        else:
            self._start_connection()
        return committed

    def change_autocommit_mode(self, switch: str) -> None:
        """根据输入的字符串切换是否要自动提交.

        如果输入的字符串的全小写是true或者false则按指定的值设置,否则抛出错误.
        """
        parsed_switch = switch.strip().lower()
        if parsed_switch not in ['true', 'false']:
            self.send_response(
                self.iopub_socket, 'stream', {
                    'name': 'stderr',
                    'text': 'autocommit must be true or false.\n\n'
                }
            )

        switch_bool = (parsed_switch == 'true')
        committed = "True" if self.switch_autocommit(switch_bool) else ''
        message = f'committed current transaction & {committed} switched autocommit mode to {self._autocommit}'

        self.send_response(
            self.iopub_socket, 'stream', {
                'name': 'stderr',
                'text': message,
            }
        )

    def get_kernel_help_on(self, info: Mapping[str, str], level: int = 1, none_on_fail: bool = False) -> Optional[str]:
        self.log.warning("get kernel help")
        code = info['code'].strip()
        if not code or len(code.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ""
        shell_magic = self.line_magics['shell']
        return shell_magic.get_help_on(info, 1)

    def do_execute_meta(self, code: str) -> ExceptionWrapper:
        """
        Execute meta code in the kernel. This uses the execute infrastructure
        but allows JavaScript to talk directly to the kernel bypassing normal
        processing.
        When responding to the %%debug magic, the step and reset meta
        commands can answer with a string in the format:
        "highlight: [start_line, start_col, end_line, end_col]"
        for highlighting expressions in the frontend.
        """
        try:
            super(PostgreSQLKernel, self).do_execute_meta(code)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
            return ExceptionWrapper(ename=str(type(e)), evalue=str(e), traceback=tb)

    def do_execute_direct(self, code: str, silent: bool = False) -> Optional[Union[RowsDisplay, ExceptionWrapper]]:
        if code.strip().lower() in ['quit', 'quit()', 'exit', 'exit()']:
            self.do_shutdown(True)
            self.payload = [{"source": "ask_exit"}]
            return None
        try:
            connection_string = CONN_STRING_COMMENT.findall(code)
            autocommit_switch = AUTOCOMMIT_SWITCH_COMMENT.findall(code)
            if autocommit_switch:
                self.change_autocommit_mode(autocommit_switch[0])
            if connection_string:
                self.change_connection(connection_string[0])

            code = AUTOCOMMIT_SWITCH_COMMENT.sub('', CONN_STRING_COMMENT.sub('', code))
            if not code.strip():
                return None
            if self._conn is None:
                raise MissingConnection(f'''\
    Error: Unable to connect to a database at "{self._conn_string}".
    Perhaps you need to set a connection string with
    -- connection: <connection string here>''')

            try:
                header, rows = self.fetchall(code)
            except QueryCanceledError as qce:
                self._conn.rollback()
                raise qce
            except Error as e:
                self.send_response(self.iopub_socket, 'stream', {'name': 'stderr', 'text': str(e)})
                self._conn.rollback()
                raise e
            else:
                if rows is not None:
                    self.send_response(
                        self.iopub_socket, 'stream', {
                            'name': 'stdout',
                            'text': str(len(rows)) + " row(s) returned.\n"
                        })

                for notice in self._conn.notices:
                    self.send_response(
                        self.iopub_socket, 'stream', {
                            'name': 'stdout',
                            'text': str(notice)
                        })
                self._conn.notices = []
                if header is not None and rows and len(rows) > 0:
                    return RowsDisplay(header, rows)
                else:
                    return None
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
            return ExceptionWrapper(ename=str(type(e)), evalue=str(e), traceback=tb)
