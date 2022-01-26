from .csr_export import csr_export
from .example import add
from .basic_export import basic_export

registry = {
    'add': add,
    'basic_export': basic_export,
    'csr_export': csr_export
}
