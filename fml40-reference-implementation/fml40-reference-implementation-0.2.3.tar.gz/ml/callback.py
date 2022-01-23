import asyncio


class CallbackManager(object):
    """
    Global callback system, which is aimed at to be a single place to manage callbacks and process them
    """
    CALLBACK = 'callback'
    ONE_SHOT = 'one_shot'
    IS_ASYNC_CALLBACK = 'is_async_callback'
    ARGS = 'args'
    KWARGS = 'kwargs'

    def __init__(self):
        """
        Create an instance of the CallbackManager
        """
        self._stack = {}

    def add(self, prefix, callback, one_shot, is_async, *args, **kwargs):
        """
        Appends async callback function to dictionary
        :param prefix:
        :param callback:
        :param one_shot:
        :param is_async:
        :param args:
        :param kwargs:
        :return:
        """
        # prepare the stack
        if prefix not in self._stack:
            self._stack[prefix] = []

        if not isinstance(one_shot, bool):
            raise TypeError
        if not isinstance(is_async, bool):
            raise TypeError

        # create callback dictionary
        callback_dict = self.create_callback_dict(
            callback,
            one_shot,
            is_async,
            *args,
            **kwargs
        )

        # check for a duplicate
        if callback_dict in self._stack[prefix]:
            return prefix

        # append
        self._stack[prefix].append(callback_dict)
        return prefix

    def remove(self, prefix, callback_dict):
        if prefix not in self._stack:
            return False
        for callback in self._stack[prefix]:
            if callback == callback_dict:
                self._stack[prefix].remove(callback)
                return True
        return False

    def clear(self):
        if self._stack:
            self._stack = {}

    def process(self, prefix, loop=asyncio.get_event_loop()):
        if prefix not in self._stack:
            return False

        for callback_dict in self._stack[prefix]:
            method = callback_dict[self.CALLBACK]
            args = callback_dict[self.ARGS]
            kwargs = callback_dict[self.KWARGS]
            if callback_dict[self.IS_ASYNC_CALLBACK]:
                loop.create_task(method(*args, **kwargs))
            else:
                method(*args, **kwargs)

        for callback_dict in self._stack[prefix]:
            if callback_dict[self.ONE_SHOT]:
                self.remove(prefix, callback_dict)

        return True

    def create_callback_dict(self, callback, one_shot, is_async, *args, **kwargs):
        """
        Create and return callback dictionary

        :param method callback:
        :param bool one_shot:
        :param is_async:
        :return:
        """

        return {
            self.CALLBACK: callback,
            self.ONE_SHOT: one_shot,
            self.IS_ASYNC_CALLBACK: is_async,
            self.ARGS: args,
            self.KWARGS: kwargs
        }



