#
# rbfly - a library for RabbitMQ Streams using Python asyncio
#
# Copyright (C) 2021-2022 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import asyncio
import logging
import typing as tp
from collections.abc import Awaitable
from itertools import chain as concatv

logger = logging.getLogger(__name__)

T = tp.TypeVar('T')
P = tp.ParamSpec('P')
Predicate = tp.Callable[[Exception], bool]

def default_predicate(ex: Exception) -> bool:
    return True

def suppress(
        ex_cls: type[Exception],
        *,
        predicate: Predicate=default_predicate,
    ) -> tp.Callable[
        [tp.Callable[P, Awaitable[T]]],
        tp.Callable[P, Awaitable[T]]
    ]:
    """
    Suppress an exception of class `ex_cls`.

    The execution of decorated asynchronous coroutine is not repeated.

    An exception is suppressed only when predicate function returns true
    for the exception.

    :param ex_cls: Class of exception to suppress.
    :param predicate: Exception predicate.

    .. seealso:: retry
    """
    def wrapper(f: tp.Callable[P, Awaitable[T]]) -> tp.Callable[P, Awaitable[T]]:
        async def wrapper_exec(*args: P.args, **kw: P.kwargs) -> T:  # type: ignore
            try:
                result = await f(*args, **kw)
                return result
            except ex_cls as ex:
                if predicate(ex):
                    logger.warning('error suppressed: {}'.format(ex))
                else:
                    raise
        return wrapper_exec
    return wrapper

def retry(
        ex_cls: type[Exception],
        *,
        predicate: Predicate=default_predicate,
        retry_after: int=5
    ) -> tp.Callable[
        [tp.Callable[P, Awaitable[T]]],
        tp.Callable[P, Awaitable[T]]
    ]:
    """
    Suppress an exception of class `ex_cls` and retry execution of
    decorated asynchronous coroutine.

    An exception is suppressed only when predicate function returns true
    for the exception.

    Once exception is suppressed, the coroutine sleeps for `retry_after`
    seconds. The minimum is 1 second.

    :param ex_cls: Class of exception to suppress.
    :param predicate: Exception predicate.
    :param retry_after: Retry after specified amount of seconds.

    .. seealso:: suppress
    """
    def wrapper(f: tp.Callable[P, Awaitable[T]]) -> tp.Callable[P, Awaitable[T]]:
        assert retry_after >= 1
        async def wrapper_exec(*args: P.args, **kw: P.kwargs) -> T:
            while True:
                try:
                    result = await f(*args, **kw)
                    return result
                except ex_cls as ex:
                    if predicate(ex):
                        logger.warning(
                            'error suppressed, sleep for {}s: {}'.format(retry_after, ex)
                        )
                        await asyncio.sleep(retry_after)
                    else:
                        raise
        return wrapper_exec
    return wrapper

# vim: sw=4:et:ai
