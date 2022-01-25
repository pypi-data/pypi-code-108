import subprocess
import time
from typing import Dict, List, Union
from watchcat.filter.filter import Filter

from watchcat.notifier.notifier import Notifier
from watchcat.resource.errors import GetError
from watchcat.resource.resource import Resource
from watchcat.snapshot import Snapshot


class CommandResource(Resource):
    def __init__(
        self,
        resource_id: str,
        notifier: Notifier,
        cmd: str,
        enabled: bool = True,
        title: Union[str, None] = None,
        env: Dict[str, str] = dict(),
        filters: List[Filter] = [],
        wait: int = 1,
    ):
        """init

        Parameters
        ----------
        resource_id : str
            一意なid
        notifier : Notifier
            通知元
        cmd : str
            実行コマンド
        enabled : bool, optional
            実行するかどうか, by default True
        title : Union[str, None], optional
            通知に表示されるタイトル, by default None
        env : Dict[str, str], optional
            環境変数, by default dict()
        """
        super().__init__(resource_id, notifier, enabled, title or cmd, filters, wait)
        self.cmd = cmd
        self.env = env

    def __str__(self) -> str:
        if self.title:
            return f"<CommandResource(resource_id={self.resource_id}, notifier={self.notifier}, title{self.title}, enabled={self.enabled}, title={self.title})>"

    def _get(self) -> Snapshot:
        """コマンドを実行して返り値を取得

        Returns
        -------
        Snapshot
            スナップショット

        Raises
        ------
        GetError
            取得エラー
        """
        response = subprocess.run(self.cmd, shell=True, env=self.env, stdout=subprocess.PIPE)
        if response.returncode == 0:
            text = response.stdout.decode(encoding="utf-8")
            timestamp = time.time()
            snapshot = Snapshot(self.resource_id, timestamp, text)
            return snapshot
        else:
            raise GetError()

    def description(self) -> str:
        return self.cmd
