import tensorflow as _tf
from reverb.platform.default import load_op_library as _load_op_library

try:
  _reverb_gen_op = _tf.load_op_library(
    _tf.compat.v1.resource_loader.get_path_to_datafile("libgen_reverb_ops_gen_op.so"))
except _tf.errors.NotFoundError as e:
  _load_op_library.reraise_wrapped_error(e)
_locals = locals()
for k in dir(_reverb_gen_op):
  _locals[k] = getattr(_reverb_gen_op, k)
del _locals
