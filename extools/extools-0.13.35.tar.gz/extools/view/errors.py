from extools.errors import ExToolsError

try:
    from accpac import rotoid
except ImportError:
    pass

class ExViewError(ExToolsError):
    """Generic error raised by an ExView.

    :param rotoid: RotoID of the ExView that raised.
    :type rotoid: str
    :param action: ExView action that raised.
    :type action: string
    :param action_return: return code from the View call.
    :type action_return: int
    :param trigger_exc: the exception that triggered this one.
    :type trigger_exc: Exception
    """

    def __init__(self, rotoid, 
                 action="", action_return=None, 
                 fargs=[], fkwargs={}, 
                 trigger_exc=None):
        super().__init__(trigger_exc=trigger_exc)
        self.rotoid = rotoid
        self.action = action
        self.action_return= action_return
        self.fargs = fargs
        self.fkwargs = fkwargs

    def __str__(self):
        if self.action:
            s = "failed to {} view {}".format(self.action, self.rotoid)
        else:
            s = "error raised in view {}".format(self.rotoid)

        if self.action_return is not None:
            s += ", return code {}".format(self.action_return)

        if self.fargs:
            s += ". Call arguments: {}".format(self.fargs)
        
        if self.fkwargs:
            s += ". Call keywork arguments {}".format(self.fkwargs) 

        if self.trigger_exc:
            s+= ". Triggered by {}".format(self.trigger_exc)

        return s

class ExViewOpenError(ExViewError):
    """Error raised while opening ExView.

    :param rotoid: RotoID of the ExView that raised.
    :type rotoid: str
    :param action_return: return code from the View call.
    :type action_return: int
    :param trigger_exc: the exception that triggered this one.
    :type trigger_exc: Exception
    """
    def __init__(self, rotoid, action_return=None, trigger_exc=None):
        super().__init__(rotoid, action="open", action_return=action_return,
                         trigger_exc=trigger_exc)

class ExViewRecordDoesNotExist(ExViewError):
    """Error raised while opening ExView.

    :param rotoid: RotoID of the ExView that raised.
    :type rotoid: str
    :param action_return: return code from the View call.
    :type action_return: int
    :param trigger_exc: the exception that triggered this one.
    :type trigger_exc: Exception
    """
    def __init__(self, rotoid, action, action_return=None, trigger_exc=None):
        super().__init__(rotoid, action=action, action_return=action_return,
                         trigger_exc=trigger_exc)

class ExViewComposeError(ExViewError):
    """Error raised while composing ExViews.

    :param compose_list: list of rotoids the ExView is being composed with.
    :type compose_list: list(str)
    :param action_return: return code from the View call.
    :type action_return: int
    :param trigger_exc: the exception that triggered this one.
    :type trigger_exc: Exception
    """
    def __init__(self, rotoid, compose_list=[],
                 action_return=None, trigger_exc=None):
        super().__init__(rotoid, action="compose", action_return=action_return,
                         trigger_exc=trigger_exc)
        self.compose_list = compose_list

    def __str__(self):
        s = str(super())
        s += ". Composing with {}".format(self.compose_list)
        return s

class ExViewInvalidOrder(ExViewError):
    """Error raised while setting the index order.

    :param order: order requested.
    :type order: int
    :param action_return: return code from the View call.
    :type action_return: int
    :param trigger_exc: the exception that triggered this one.
    :type trigger_exc: Exception
    """
    def __init__(self, rotoid, order=None,
                 action_return=None, trigger_exc=None):
        super().__init__(rotoid, action="order", action_return=action_return,
                         trigger_exc=trigger_exc)
        self.order = order

class ExViewFieldDoesNotExist(ExViewError):
    """Error raised when a field does not exist in the view.

    :param field: field requested.
    :type field: str
    :param trigger_exc: the exception that triggered this one.
    :type trigger_exc: Exception
    """
    def __init__(self, rotoid, field=None, order=None, action=None,
                 action_return=None, trigger_exc=None):
        super().__init__(rotoid, action=action, action_return=action_return,
                         trigger_exc=trigger_exc)
        self.field = field

    def __str__(self):
        s = str(super())
        s += ", field {} not found".format(self.field)
        return s

class ExViewIndexError(ExViewError):
    """Error raised when an invalid index is provided.

    :param order: index order requested.
    :type order: int
    :param trigger_exc: the exception that triggered this one.
    :type trigger_exc: Exception
    """
    def __init__(self, rotoid, kwargs=None, action="order",
                 action_return=None, trigger_exc=None):
        super().__init__(rotoid, action=None, action_return=None,
                         trigger_exc=trigger_exc)
        self.kwargs = kwargs

    def __str__(self):
        s = str(super())
        s += ", index with fields {} is not valid".format(self.kwargs)
        return s

class ExViewInterpolationError(ExViewError):
    """Error raised when string interpolation using ExViews fails.

    :param rotoid: rotoid of the view failing interpolation.
    :type rotoid: str
    :param format_string: string being interpolated
    :type format_string: str
    :param root_view: the root view from which all fields can be found.
    :type root_view: str
    :param seek_to: seek to parameters for the first index of the root view.
    :type seek_to: dict
    """
    def __init__(self, rotoid, format_string, field, root_view, seek_to,
                 trigger_exc=None, **kwargs):
        super().__init__(rotoid, action=None, action_return=None,
                         trigger_exc=trigger_exc)
        self.rotoid = rotoid,
        self.format_string = format_string
        self.field = field
        self.root_view = root_view
        self.seek_to = seek_to
        self.kwargs = kwargs

    def __str__(self):
        s = str(super())
        s += ", failed to interpolate {} into {} from root view {} {}".format(
                self.field, self.format_string, self.root_view, self.seek_to)
        return s
