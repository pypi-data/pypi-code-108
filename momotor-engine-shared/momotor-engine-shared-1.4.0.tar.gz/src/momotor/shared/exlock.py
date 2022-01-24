import aiorwlock

import typing


class ExLock(aiorwlock.RWLock):
    """
    A subclass of `aiorwlock.RWLock <https://github.com/aio-libs/aiorwlock>`_

    An :py:class:`~momotor.shared.exlock.ExLock` maintains a pair of associated locks, one for read-only
    operations and one for writing. The read lock may be held simultaneously
    by multiple reader tasks, so long as there are no writers. The write
    lock is exclusive.
    """

    # noinspection PyProtectedMember
    def get(self, exclusive: bool) -> typing.Union[aiorwlock._ReaderLock, aiorwlock._WriterLock]:
        """ Get either the :py:attr:`reader` or :py:attr:`writer` lock, depending on the value of
        ``exclusive``

        :param exclusive: if ``False``, requests the :py:attr:`reader` lock, otherwise the :py:attr:`writer` lock
        :return: the requested lock
        """
        return self.writer if exclusive else self.reader
