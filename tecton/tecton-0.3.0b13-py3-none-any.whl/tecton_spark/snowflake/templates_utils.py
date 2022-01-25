from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import StrictUndefined

from tecton_proto.common import column_type_pb2
from tecton_spark.aggregation_utils import get_aggregation_function_name


def snowflake_function(value):
    fn = get_aggregation_function_name(value)
    if fn == "mean":
        return "avg"
    return fn


def load_template(name):
    env = Environment(
        loader=PackageLoader("tecton_spark"),
        autoescape=False,
        undefined=StrictUndefined,
    )
    env.globals["column_type_pb2"] = column_type_pb2
    env.filters["snowflake_function"] = snowflake_function
    return env.get_template(name)
