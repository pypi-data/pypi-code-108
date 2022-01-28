from typing import List
from typing import Optional
from typing import Union

import tecton
from tecton import conf
from tecton._internals import errors
from tecton._internals import metadata_service
from tecton._internals.display import Displayable
from tecton._internals.sdk_decorators import documented_by
from tecton._internals.sdk_decorators import sdk_public_method
from tecton._internals.utils import is_live_workspace
from tecton.interactive.dataset import Dataset
from tecton.interactive.feature_table import FeatureTable
from tecton.interactive.feature_view import FeatureView
from tecton.interactive.transformation import Transformation
from tecton_proto.metadataservice.metadata_service_pb2 import ListWorkspacesRequest


class Workspace:
    """
    Workspace class.

    This class represents a Workspace. The Workspace class is used to fetch Tecton Objects, which are stored in a Workspace.

    Examples of using the Workspace methods for accessing Tecton first class objects:

    .. code-block:: python

        import tecton


        WORKSPACE_NAME = "jsd_tecton_wksp"

        workspace = tecton.Workspace(WORKSPACE_NAME)

        # For a specified workspace, list high-level registered Objects
        print(f" Entities            : {workspace.list_entities()}")
        print(f" Feature Data Sources: {workspace.list_data_sources()}")
        print(f" Feature Views       : {workspace.list_feature_views()}")
        print(f" Feature Services    : {workspace.list_feature_services()}")
        print(f" Transformations     : {workspace.list_transformations()}")
        print(f" Feature Tables      : {workspace.list_feature_tables()}")
        print(f" List of Workspaces  : {tecton.list_workspaces()}")

    .. code-block:: Text

        The output:

        Entities            : ['ad', 'auction', 'content', 'ContentKeyword', 'ads_user', 'fraud_user']
        Feature Data Sources: ['ad_impressions_stream', 'ad_impressions_batch', 'transactions_stream', 'transactions_batch',
                                'users_batch', 'credit_scores_batch']
        Feature Views       : ['user_has_great_credit', 'user_age', 'transaction_amount_is_high',
                               'transaction_amount_is_higher_than_average', 'transaction_bucketing', 'user_ctr_7d_2',
                               ...
                               'user_ad_impression_counts', 'content_keyword_click_counts']
        Feature Services    : ['ad_ctr_feature_service', 'fraud_detection_feature_service',
                                'fraud_detection_feature_service:v2', 'minimal_fs', 'continuous_feature_service']
        Transformations     : ['content_keyword_click_counts', 'user_ad_impression_counts', 'user_click_counts',
                               'user_impression_counts', 'user_ctr_7d', 'user_ctr_7d_2', 'user_distinct_ad_count_7d',
                               ...
                               'weekend_transaction_count_n_days', 'user_has_good_credit_sql']
        Feature Tables      : ['user_login_counts', 'user_page_click_feature_table']
        List of Workspaces  : ['jsd_tecton_wksp, 'kafka_streaming_staging, 'kafka_streaming_production',
                               ...
                               'on_demand_streaming_aggregation_pipeline']

    """

    def __init__(self, workspace: str, _is_live: Optional[bool] = None, _validate: bool = True):
        """
        Fetch an existing :class:`Workspace` by name.

        :param workspace: Workspace name.
        """
        self.workspace = workspace

        if _is_live is None:
            self.is_live = is_live_workspace(self.workspace)
        else:
            self.is_live = _is_live

        if _validate:
            self._validate()

    def _validate(self):
        request = ListWorkspacesRequest()
        response = metadata_service.instance().ListWorkspaces(request)

        workspace_from_resp = None
        for ws in response.workspaces:
            if ws.name == self.workspace:
                workspace_from_resp = ws
                break

        if workspace_from_resp is None:
            raise errors.NONEXISTENT_WORKSPACE(workspace, workspaces)

        if ws.capabilities.materializable != self.is_live:
            raise errors.INCORRECT_MATERIALIZATION_ENABLED_FLAG(self.is_live, ws.capabilities.materializable)

    @classmethod
    @sdk_public_method
    def get_all(self) -> List["Workspace"]:
        """
        Returns a list of all registered Workspaces.

        :return: A list of Workspace objects.
        """
        request = ListWorkspacesRequest()
        response = metadata_service.instance().ListWorkspaces(request)
        workspaces = [
            Workspace(ws.name, _is_live=ws.capabilities.materializable, _validate=False) for ws in response.workspaces
        ]

        # Return live workspaces first (alphabetical), then development workspaces.
        return sorted(workspaces, key=lambda ws: (not ws.is_live, ws.workspace))

    def __enter__(self):
        self.previous_workspace = conf.get_or_none("TECTON_WORKSPACE")
        conf.set("TECTON_WORKSPACE", self.workspace)

    def __exit__(self, type, value, traceback):
        conf.set("TECTON_WORKSPACE", self.previous_workspace)

    def __repr__(self) -> str:
        capability_str = "Live" if self.is_live else "Development"
        return f"{self.workspace} ({capability_str})"

    @sdk_public_method
    def summary(self) -> Displayable:
        from texttable import Texttable

        items = [
            ("Workspace Name", self.workspace),
            ("Workspace Type", "Live" if self.is_live else "Development"),
        ]
        return Displayable.from_items(
            headings=["", ""], items=items, deco=(Texttable.BORDER | Texttable.VLINES | Texttable.HLINES)
        )

    @classmethod
    @sdk_public_method
    def get(cls, name) -> "Workspace":
        """
        Fetch an existing :class:`Workspace` by name.

        :param name: Workspace name.
        """
        return Workspace(name)

    @sdk_public_method
    def get_feature_view(self, name: str) -> FeatureView:
        """
        Returns a FeatureView within a workspace.

        :param name: FeatureView name
        :return: :class:`BatchFeatureView`, :class:`BatchWindowAggregateFeatureView`,
            :class:`StreamFeatureView`, :class:`StreamWindowAggregateFeatureView`,
            or :class:`OnDemandFeatureView`
        """
        return tecton.get_feature_view(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_feature_table(self, name: str) -> FeatureTable:
        """
        Returns a :class:`FeatureTable` within a workspace.

        :param name: FeatureTable name
        :return: the named FeatureTable
        """
        return tecton.get_feature_table(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_feature_service(self, name: str):
        """
        Returns a :class:`FeatureService` within a workspace.

        :param name: FeatureService name.
        :return: the named FeatureService
        """

        return tecton.get_feature_service(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_data_source(self, name: str):
        """
        Returns a :class:`BatchDataSource` or :class:`StreamDataSource` within a workspace.

        :param name: BatchDataSource or StreamDataSource name.
        :return: the named BatchDataSource or StreamDataSource
        """

        return tecton.get_data_source(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_entity(self, name: str):
        """
        Returns an :class:`Entity` within a workspace.

        :param name: Entity name.
        :return: the named Entity
        """

        return tecton.get_entity(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_transformation(self, name: str) -> Union[Transformation]:
        """
        Returns a :class:`Transformation` within a workspace.

        :param name: Transformation name.
        :return: the named Transformation
        """

        return tecton.get_transformation(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_dataset(self, name) -> Dataset:
        """
        Returns a :class:`Dataset` within a workspace.

        :param name: Dataset name.
        :return: the named Dataset
        """
        return tecton.get_dataset(name, workspace_name=self.workspace)

    @sdk_public_method
    def list_datasets(self) -> List[str]:
        """
        Returns a list of all registered Datasets within a workspace.

        :return: A list of strings.
        """
        return tecton.list_datasets(workspace_name=self.workspace)

    @sdk_public_method
    def list_feature_views(self) -> List[str]:
        """
        Returns a list of all registered FeatureViews within a workspace.

        :return: A list of strings.
        """
        return tecton.list_feature_views(workspace_name=self.workspace)

    @sdk_public_method
    def list_feature_services(self) -> List[str]:
        """
        Returns a list of all registered FeatureServices within a workspace.

        :return: A list of strings.
        """
        return tecton.list_feature_services(workspace_name=self.workspace)

    @sdk_public_method
    def list_transformations(self) -> List[str]:
        """
        Returns a list of all registered Transformations within a workspace.

        :return: A list of strings.
        """
        return tecton.list_transformations(workspace_name=self.workspace)

    @sdk_public_method
    def list_entities(self) -> List[str]:
        """
        Returns a list of all registered Entities within a workspace.

        :returns: A list of strings.
        """
        return tecton.list_entities(workspace_name=self.workspace)

    @sdk_public_method
    def list_data_sources(self) -> List[str]:
        """
        Returns a list of all registered DataSources within a workspace.

        :return: A list of strings.
        """
        return tecton.list_data_sources(workspace_name=self.workspace)

    @sdk_public_method
    def list_feature_tables(self) -> List[str]:
        """
        Returns a list of all registered FeatureTables within a workspace.

        :return: A list of strings.
        """
        return tecton.list_feature_tables(workspace_name=self.workspace)


@documented_by(Workspace.get)
@sdk_public_method
def get_workspace(name: str):
    return Workspace.get(name)
