try:
    __import__('pkg_resources').declare_namespace(__name__)

except ImportError:

    from pkgutil import extend_path

    __path__ = extend_path(__path__, __name__)


"""
This is ususally imported only when logging is configured.
Our features depend on structlog which is not a dependency.
"""
try:
    pass
except ImportError as ex:
    ex.args += (
        'Hint: You have to add structlog to your packages.' '=> pip install structlog',
    )
    raise


# -- Setup for a stdlib logging free, getattr free use:
