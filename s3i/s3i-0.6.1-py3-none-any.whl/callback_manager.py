class CallbackManager(object):
    """
    Global callback system, which is aimed at to be a single place to manage callbacks and process them
    """
    CALLBACK = 'callback'
    ONE_SHOT = 'one_shot'
    ARGS = 'args'
    KWARGS = 'kwargs'

    def __init__(self):
        """
        Create an instance of the CallbackManager
        """
        self._stack = {}

    def add(self, prefix, callback, one_shot, *args, **kwargs):
        # prepare the stack
        if prefix not in self._stack:
            self._stack[prefix] = []

        # create callback dictionary
        callback_dict = self.create_callback_dict(
            callback,
            one_shot,
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

    def process(self, prefix):
        if prefix not in self._stack:
            return False
        for callback_dict in self._stack[prefix]:
            method = callback_dict[self.CALLBACK]
            args = callback_dict[self.ARGS]
            kwargs = callback_dict[self.KWARGS]
            method(*args, **kwargs)

        for callback_dict in self._stack[prefix]:
            if callback_dict[self.ONE_SHOT]:
                self.remove(prefix, callback_dict)
        return True

    def process_async_task(self, prefix, loop):
        if prefix not in self._stack:
            return False
        for callback_dict in self._stack[prefix]:
            method = callback_dict[self.CALLBACK]
            args = callback_dict[self.ARGS]
            kwargs = callback_dict[self.KWARGS]
            loop.create_task(method(*args, **kwargs))

        for callback_dict in self._stack[prefix]:
            if callback_dict[self.ONE_SHOT]:
                self.remove(prefix, callback_dict)
        return True

    def create_callback_dict(self, callback, one_shot, *args, **kwargs):
        """
        Create and return callback dictionary

        :param method callback:
        :param bool one_shot:
        :return:
        """

        return {
            self.CALLBACK: callback,
            self.ONE_SHOT: one_shot,
            self.ARGS: args,
            self.KWARGS: kwargs
        }



