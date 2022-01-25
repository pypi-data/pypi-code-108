import attr

from tecton_proto.args.feature_service_pb2 import LoggingConfigArgs


@attr.s(auto_attribs=True)
class LoggingConfig(object):
    """
    Configuration used to describe feature and request logging for Feature Services.

    :param sample_rate: (Optional, default 1.0) The rate of logging features. Must be between (0, 1]
    :param log_effective_times: (Optional) Whether to log the timestamps of the last update of the logged feature values

    An example of LoggingConfig declaration as part of FeatureService

    .. code-block:: Python

        from tecton import FeatureService, LoggingConfig

        # LoggingConfig is normaly used as a named argument parameter to a FeatureService instance definition.
        my_feature_service = FeatureService(
            name="An example of Feature Service"
            # Other named arguments
            ...
            # A LoggingConfig instance
            logging=LoggingConfig(
                    sample_rate=0.5,
                    log_effective_time=False,
            )
            ...
        )
    """

    sample_rate: float = attr.ib(default=1.0, validator=attr.validators.instance_of((float, int)))
    log_effective_times: bool = attr.ib(default=False, validator=attr.validators.instance_of(bool))

    def _to_proto(self) -> LoggingConfigArgs:
        return LoggingConfigArgs(sample_rate=self.sample_rate, log_effective_times=self.log_effective_times)

    @classmethod
    def _from_proto(cls, logging_config_proto: LoggingConfigArgs) -> "LoggingConfig":
        return LoggingConfig(logging_config_proto.sample_rate, logging_config_proto.log_effective_times)
