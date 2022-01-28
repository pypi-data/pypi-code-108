import functools
from dataclasses import dataclass
from textwrap import dedent

from tecton._internals.fco import Fco
from tecton.transformations.transformation import Transformation
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_spark.materialization_context import materialization_context


@dataclass
class BuiltinTransformation(Transformation):
    """
    Note that you SHOULD NOT change the code of any builtin transformations since it will cause
    errors to be thrown in MDS validation since we cannot allow destructive recreations.
    """

    docstring: str
    call_count: int = 0

    def _docstring(self):
        return self.docstring

    def _is_builtin(self):
        return True

    def __call__(self, *args, **kwargs) -> PipelineNode:
        # register the first time it's called
        if self.call_count == 0:
            Fco._register(self)
        self.call_count += 1
        return super().__call__(*args, **kwargs)

    def __hash__(self):
        return hash(self.name)


def builtin_transformation(mode: str, description: str, docstring: str):
    def decorator(user_function):
        transform_name = user_function.__name__
        transform = BuiltinTransformation(
            transform_name,
            mode,
            user_function,
            description,
            owner="tecton",
            family="tecton_builtins",
            tags={},
            docstring=dedent(docstring),
        )
        functools.update_wrapper(wrapper=transform, wrapped=user_function)
        return transform

    return decorator


@builtin_transformation(
    mode="pyspark",
    description="A transformation that adds a column to make sliding window aggregations easier.",
    docstring="""
        :param df: Spark DataFrame
        :param timestamp_key: The name of the timestamp columns for the event times in `df`
        :param window_size: How long each sliding window is, as a string in the format "[QUANTITY] [UNIT]".
            Ex: "2 days". See https://pypi.org/project/pytimeparse/ for more details.
        :param slide_interval: [optional] How often window is produced, as a string in the format "[QUANTITY] [UNIT]".
            Ex: "2 days". See https://pypi.org/project/pytimeparse/ for more details.
            Note this must be less than or equal to window_size, and window_size must be a multiple of slide_interval.
            If not provided, this defaults to the batch schedule of the FeatureView.
        :param window_column_name: [optional] The output column name for the timestamp of the end of each window
        :return: An exploded Spark DataFrame with an added column according to window_column_name.

        Ex:
            tecton_sliding_window(
                [
                    (user_id=1, timestamp = '2021-01-10 10:14:14'),
                    (user_id=2, timestamp = '2021-01-11 23:10:10'),
                    (user_id=3, timestamp = '2021-01-12 01:01:01')
                ],
                window_size = '2 days')
            with context(
                feature_start_time='2021-01-10 00:00:00',
                feature_end_time='2021-01-12 00:00:00',
                batch_schedule='1 day'
            )
            =>
            [
                (user_id=1, timestamp='2021-01-10 10:14:14', window_end='2021-01-10 23:59:59.999999'),
                (user_id=1, timestamp='2021-01-10 10:14:14', window_end='2021-01-11 23:59:59.999999'),
                (user_id=2, timestamp='2021-01-11 23:10:10', window_end='2021-01-11 23:59:59.999999')
            ]

            Note that each input row can produce from 0 to (window_size / slide_interval) output rows, depending on how many
            windows it is present in.

            To do an aggregation on these rows, you could write a query like below, which computes a count for each window.
            ```
            SELECT
                user_id,
                COUNT(1) as occurrences,
                window_end
            FROM {df}
            GROUP BY
                user_id,
                window_end
            ```
    """,
)
def tecton_sliding_window(
    df,
    timestamp_key,
    window_size,
    slide_interval=None,
    window_column_name="window_end",
    context=materialization_context(),
):
    from pyspark.sql import functions as F
    from tecton_spark.udfs import tecton_sliding_window_udf, _validate_sliding_window_duration

    slide_interval = slide_interval or f"{context.batch_schedule.total_seconds()} seconds"
    _validate_sliding_window_duration(window_size, slide_interval)

    return df.withColumn(
        window_column_name,
        F.explode(
            tecton_sliding_window_udf(
                F.col(timestamp_key),
                F.lit(window_size),
                F.lit(slide_interval),
                F.lit(context.feature_start_time),
                F.lit(context.feature_end_time),
            )
        ),
    )
