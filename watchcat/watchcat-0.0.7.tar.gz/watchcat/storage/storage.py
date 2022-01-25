from watchcat.snapshot import Snapshot


class Storage:
    def __init__(self, db_path: str):
        """init

        Parameters
        ----------
        db_path : str
            dbの保存場所
        """

    def __str__(self):
        raise NotImplementedError()

    def get(self, resource_id: str):
        raise NotImplementedError()

    def set(self, snapshot: Snapshot):
        raise NotImplementedError()
