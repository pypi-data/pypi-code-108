try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

__all__ = ['gptools']

if 'GPTOOLS_ROOT' in os.environ:
    _gptools_pythonpath = os.path.abspath(os.environ['GPTOOLS_ROOT'])
    if _gptools_pythonpath not in [os.path.abspath(_path) for _path in sys.path]:
        sys.path.insert(1, _gptools_pythonpath)
        print('* Path to GPTOOLS python tools has been added: ' + _gptools_pythonpath)
    else:
        print('* Path to GPTOOLS python tools was found' + _gptools_pythonpath)
    if 'PYTHONPATH' in os.environ and os.environ['PYTHONPATH']:
        if _gptools_pythonpath not in os.environ['PYTHONPATH']:
            os.environ['PYTHONPATH'] = _gptools_pythonpath + ':' + os.environ['PYTHONPATH']
    else:
        os.environ['PYTHONPATH'] = _gptools_pythonpath

gptools = None
try:
    #'triangle' has been renamed to 'corner'
    import corner

    sys.modules['triangle'] = sys.modules['corner']

except ImportError:
    try:
        import triangle
    except ImportError:
        pass

except Exception as _excp:
    warnings.warn('No `gptools` support: ' + repr(_excp))

else:
    try:
        import gptools
    except Exception as _excp:
        warnings.warn('No `gptools` support (GPTOOLS_ROOT environment variable): ' + repr(_excp))
