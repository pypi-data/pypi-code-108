"""Useful function decorators.

Provides:

* to_spark_col: to specify parameters to be converted to a spark_col
  before use.
* to_list: to specify parameters to be converted to a list before use.

"""
from .factories import args_kwargs_transformer_factory
from .pyspark.general import convert_to_spark_col
from .generic import list_convert


to_spark_col = args_kwargs_transformer_factory(convert_to_spark_col)
to_list = args_kwargs_transformer_factory(list_convert)
