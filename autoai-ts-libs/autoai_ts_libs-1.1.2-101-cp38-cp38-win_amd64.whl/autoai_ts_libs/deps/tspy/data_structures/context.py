#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

from py4j.java_gateway import JavaGateway, CallbackServerParameters, GatewayParameters, launch_gateway

from autoai_ts_libs.deps.tspy.data_structures.observations.Segment import Segment

from autoai_ts_libs.deps.tspy.data_structures.forecasting import ForecastingModelFactory
from autoai_ts_libs.deps.tspy.data_structures.forecasting.AnomalyDetector import AnomalyDetector
from autoai_ts_libs.deps.tspy.data_structures.ml import MLFactory
from autoai_ts_libs.deps.tspy.data_structures.stream_multi_time_series import StreamMultiTimeSeriesFactory
from autoai_ts_libs.deps.tspy.data_structures.stream_time_series import StreamTimeSeriesFactory
from autoai_ts_libs.deps.tspy.data_structures.time_series import TimeSeriesFactory
from autoai_ts_libs.deps.tspy.data_structures.multi_time_series import MultiTimeseriesFactory
from autoai_ts_libs.deps.tspy.data_structures.observations import ObservationCollectionFactory
from autoai_ts_libs.deps.tspy.data_structures.observations.Observation import Observation
from autoai_ts_libs.deps.tspy.data_structures.transforms import MathReducerFactory, StatTransformerFactory, SegmentationTransformerFactory, \
    DuplicateTransformerFactory, StatReducerFactory, InterpolatorFactory, MathTransformerFactory, \
    DistanceReducerFactory, GeneralReducerFactory
from autoai_ts_libs.deps.tspy.functions import expressions
from autoai_ts_libs.deps.tspy.data_structures.utils import Record


def get_or_create():
    if TSContext._active == None:
        return TSContext(daemonize=True)
    else:
        return TSContext._active


class TSContext(object):
    """Manage TimeSeriesContext object - to communicate with Spark engine"""
    _active = None

    def __init__(self, gateway=None, jvm=None, always_on_caching=True, kill_gateway_on_exception=False, port=0, callback_server_port=0, daemonize=False):
        self._always_on_cache = always_on_caching
        self._kill_gateway_on_exception = kill_gateway_on_exception
        if (jvm is None) != (gateway is None):
            raise ValueError("Argument Unexpected: either provide both `jvm` and `gateway`, or both must be None")
        if jvm is None and gateway is None:
            import os
            if os.environ.get("PY4J_PATH") is None:
                jarpath = ""
            else:
                jarpath = os.environ['PY4J_PATH']

            if os.environ.get('TS_HOME') is None:
                import pkg_resources
                # TODO replace with dynamic version number
                classpath = pkg_resources.resource_filename("autoai_ts_libs.deps.tspy",
                                                            'deps/jars/time-series-assembly-python-2.2.3-jar-with-dependencies-small.jar')
            else:
                classpath = os.environ['TS_HOME']

            _port = launch_gateway(
                port=port,
                classpath=classpath,
                jarpath=jarpath,
                die_on_exit=True,javaopts=["-Xms1024m", "-Xmx4096m"]
            )

            self._gateway = JavaGateway(
                gateway_parameters=GatewayParameters(port=_port),
                callback_server_parameters=CallbackServerParameters(port=callback_server_port, daemonize=daemonize, daemonize_connections=daemonize),
                python_proxy_port=callback_server_port,
                start_callback_server=True
            )

            self._gateway.java_gateway_server.resetCallbackClient(
                self._gateway.java_gateway_server.getCallbackClient().getAddress(),
                self._gateway.get_callback_server().get_listening_port()
            )

            self._jvm = self._gateway.jvm
            self._port = _port
            self._callback_server_port = self._gateway.get_callback_server().get_listening_port()
        else:
            self._jvm = jvm
            self._gateway = gateway

            # added callback server to gateway which allows for lambdas on single machine
            if not hasattr(self._gateway.gateway_parameters, 'auth_token'):  # in 2.3 and below, there is no token
                self._gateway.start_callback_server(
                    CallbackServerParameters(port=callback_server_port, daemonize=daemonize,
                                             daemonize_connections=daemonize))
            else:  # in 2.4+ there is a token that must be included
                self._gateway.start_callback_server(
                    CallbackServerParameters(port=callback_server_port, daemonize=daemonize,
                                             daemonize_connections=daemonize,
                                             auth_token=self._gateway.gateway_parameters.auth_token))
            self._gateway.java_gateway_server.resetCallbackClient(
                self._gateway.java_gateway_server.getCallbackClient().getAddress(),
                self._gateway.get_callback_server().get_listening_port()
            )
            self._port = self._gateway._gateway_client.port
            self._callback_server_port = self._gateway.get_callback_server().get_listening_port()
        TSContext._active = self

    def stop(self):
        self._gateway.close_callback_server()
        self._gateway.close()
        self._gateway.shutdown_callback_server()
        self._gateway.shutdown()
        TSContext._active = None

    @property
    def jvm(self):
        return self._jvm

    @property
    def exp(self):
        return expressions

    def segment(self, observations, start=None, end=None):
        """
        NOTE: Use at own risk, this is mostly for use of development inside library
        :param observations:
        :param start:
        :param end:
        :return:
        """
        return Segment(self, observations._j_observations, start, end)

    def observation(self, timestamp=-1, value=None):
        return Observation(self, timestamp, value)

    def record(self, **kwargs):
        return Record(self, None, **kwargs)

    def second(self, duration, unit="s"):
        from autoai_ts_libs.deps.tspy.data_structures import utils
        return utils.second(self._jvm, duration, unit)

    def minute(self, duration, unit="s"):
        from autoai_ts_libs.deps.tspy.data_structures import utils
        return utils.minute(self._jvm, duration, unit)

    def hour(self, duration, unit="s"):
        from autoai_ts_libs.deps.tspy.data_structures import utils
        return utils.hour(self._jvm, duration, unit)

    def day(self, duration, unit="s"):
        from autoai_ts_libs.deps.tspy.data_structures import utils
        return utils.day(self._jvm, duration, unit)

    @property
    def stream_time_series(self):
        return StreamTimeSeriesFactory.Factory(self)

    @property
    def stream_multi_time_series(self):
        return StreamMultiTimeSeriesFactory.Factory(self)

    @property
    def ml(self):
        return MLFactory.Factory(self)

    @property
    def time_series(self):
        return TimeSeriesFactory.Factory(self)

    @property
    def multi_time_series(self):
        return MultiTimeseriesFactory.Factory(self)

    @property
    def observations(self):
        return ObservationCollectionFactory.Factory(self)

    @property
    def forecasters(self):
        return ForecastingModelFactory.Factory(self)

    def anomaly_detector(self, confidence):
        return AnomalyDetector(self._jvm, confidence)

    @property
    def math_transforms(self):
        return MathTransformerFactory.Factory(self._jvm)

    @property
    def math_reducers(self):
        return MathReducerFactory.Factory(self._jvm)

    @property
    def distance_reducers(self):
        return DistanceReducerFactory.Factory(self)

    @property
    def stat_transforms(self):
        return StatTransformerFactory.Factory(self._jvm)

    @property
    def stat_reducers(self):
        return StatReducerFactory.Factory(self._jvm)

    @property
    def general_reducers(self):
        return GeneralReducerFactory.Factory(self)

    @property
    def segment_transforms(self):
        return SegmentationTransformerFactory.Factory(self)

    @property
    def duplicate_transforms(self):
        return DuplicateTransformerFactory.Factory(self)

    @property
    def interpolators(self):
        return InterpolatorFactory.Factory(self)
