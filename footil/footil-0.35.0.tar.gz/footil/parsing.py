"""Parse arbitrary data using various helpers."""
import builtins


def get_globals_locals(cfg: dict) -> tuple:
    """Get globals and locals dicts that could be used for eval/exec.

    Args:
        cfg: configuration structure:
            {
                'all_builtins': bool,
                'excluded_builtins': list,
                'included_builtins': list,
                # priority:
                # all_builtins -> excluded_builtins -> included_builtins
                'globals': dict,
                'locals': dict
            }

    Returns:
        (_globals, _locals)

    """
    def filter_builtins(filter_func):
        for k, v in builtins.__dict__.items():
            if filter_func(k):
                _globals['__builtins__'][k] = v

    def set_builtins(
            all_builtins=False, excluded_builtins=(), included_builtins=()):
        if all_builtins:
            # Makes it include builtins, because it is required to
            # explicitly specify to not included it.
            del _globals['__builtins__']
        elif excluded_builtins:
            filter_builtins(lambda k: k not in excluded_builtins)
        elif included_builtins:
            filter_builtins(lambda k: k in included_builtins)

    _globals = cfg.get('globals', {})
    # builtins excluded explicitly.
    _globals['__builtins__'] = {}
    all_builtins = cfg.get('all_builtins', False)
    excluded_builtins = cfg.get('excluded_builtins', [])
    included_builtins = cfg.get('included_builtins', [])
    set_builtins(all_builtins, excluded_builtins, included_builtins)
    _locals = cfg.get('locals')
    # None means, that _globals will be used on _locals.
    if _locals is not None:
        # Calling second .get, because locals could be False.
        _locals = cfg.get('locals', {})
    return (_globals, _locals)


def eval_limited(source: str, cfg: dict = None):
    """Evaluate source with limited globals/locals.

    Can specify how to limit eval function, to not expose to more
    context than it is needed. On default no globals and locals are
    included.

    Args:
        source: source to evaluate.
        cfg: configuration to set globals/locals.
    """
    if not cfg:
        cfg = {}
    _globals, _locals = get_globals_locals(cfg)
    # evaluate source with given context if any.
    return eval(source, _globals, _locals)


def exec_limited(source: str, cfg: dict = None):
    """Execute source with limited globals/locals.

    Can specify how to limit exec function, to not expose to more
    context than it is needed. On default no globals and locals are
    included.

    Args:
        source: source to execute.
        cfg: configuration to set globals/locals.
    """
    if not cfg:
        cfg = {}
    _globals, _locals = get_globals_locals(cfg)
    # evaluate source with given context if any.
    return exec(source, _globals, _locals)
