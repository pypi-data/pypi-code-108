from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from tecton import LoggingConfig
from tecton._internals.fco import Fco
from tecton._internals.feature_definition import FeatureDefinition
from tecton.basic_info import prepare_basic_info
from tecton.feature_services.feature_service_args import FeaturesConfig
from tecton.feature_services.feature_service_args import prepare_args
from tecton_proto.args.feature_service_pb2 import FeatureServiceArgs
from tecton_proto.args.repo_metadata_pb2 import SourceInfo
from tecton_proto.common.id_pb2 import Id
from tecton_spark.logger import get_logger

logger = get_logger("FeatureService")


class FeatureService(Fco):
    """
    Declare a FeatureService.

    In Tecton, a Feature Service exposes an API for accessing a set of FeatureViews.
    FeatureServices are implemented using the ``FeatureService`` class.

    Once deployed in production, each model has one associated Feature Service that
    serves the model its features. A Feature Service contains a list of the Feature
    Views associated with a model. It also includes user-provided metadata such as
    name, description, and owner that Tecton uses to organize feature data.
    """

    _args: FeatureServiceArgs
    _source_info: SourceInfo

    def __init__(
        self,
        *,
        name: str,
        description: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
        owner: str = "",
        online_serving_enabled: bool = True,
        features: List[Union[FeaturesConfig, FeatureDefinition]] = None,
        logging: Optional[LoggingConfig] = None,
    ):
        """
        Instantiates a new FeatureService.

        :param name: A unique name for the Feature Service.
        :param description: (Optional) description.
        :param family: (Optional) Family of this Feature Service, used to group Tecton Objects.
        :param tags: (Optional) Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
        :param owner: Owner name (typically the email of the primary maintainer).
        :param online_serving_enabled: (Optional, default True) If True, users can send realtime requests
            to this FeatureService, and only FeatureViews with online materialization enabled can be added
            to this FeatureService.
        :param features: The list of FeatureView or FeaturesConfig that this FeatureService will serve.
        :param logging: (Optional) A configuration for logging feature requests sent to this Feature Service.

        An example of Feature Service declaration

        .. code-block:: python

            from tecton import FeatureService, LoggingConfig
            # Import your feature views declared in your feature repo directory
            from feature_repo.features.feature_views import last_transaction_amount_sql, transaction_amount_is_high
            ...

            # Declare Feature Service
            fraud_detection_feature_service = FeatureService(
                name='fraud_detection_feature_service',
                description='A FeatureService providing features for a model that predicts if a transaction is fraudulent.',
                family='fraud',
                features=[
                    last_transaction_amount_sql,
                    transaction_amount_is_high,
                    ...
                ]
                logging=LoggingConfig(
                    sample_rate=0.5,
                    log_effective_time=False,
                )
                tags={'release': 'staging'},
            )
        """
        from tecton.cli.common import get_fco_source_info

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)

        self._source_info = get_fco_source_info()
        self._args = prepare_args(
            basic_info=basic_info,
            online_serving_enabled=online_serving_enabled,
            features=features or [],
            logging=logging,
        )

        Fco._register(self)

    def _id(self) -> Id:
        return self._args.feature_service_id

    @property
    def name(self) -> str:
        """
        Name of this FeatureService.
        """
        return self._args.info.name
