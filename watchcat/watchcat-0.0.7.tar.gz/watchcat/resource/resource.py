import time
from typing import List, Union
from watchcat.filter.filter import Filter
from watchcat.notifier.notifier import Notifier


class Resource:
    def __init__(
        self,
        resource_id: str,
        notifier: Notifier,
        enabled: bool = True,
        title: Union[str, None] = None,
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
        enabled : bool, optional
            通知するかどうか, by default True
        title : Union[str, None], optional
            通知に表示されるタイトル, by default None
        """
        self.resource_id = resource_id
        self.notifier = notifier
        self.enabled = enabled
        self.title = title
        self.filters = filters
        self.wait = wait

    def _get(self):
        raise NotImplementedError()

    def get(self):
        time.sleep(self.wait)
        snapshot = self._get()
        for filter in self.filters:
            snapshot.content = filter.filter(snapshot.content)
        return snapshot

    def description(self) -> str:
        raise NotImplementedError()
