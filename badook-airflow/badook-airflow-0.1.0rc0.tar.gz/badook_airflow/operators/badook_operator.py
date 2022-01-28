from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from badook_airflow.hooks import BadookTestsHook


class BadookTestOperator(BaseOperator):
    """
        an operator to run badook tests using the AirFlow.

        :param target_directory: The directory containing the test project, passed as the `-d` argument to the `bdk` command
        :type target_directory: str
        :param data_cluster_url: The base URL fro the badook runtime cluster
        :type data_cluster_url: str
        :param management_cluster_url: The base URL fro the badook management instance
        :type management_cluster_url: str
        :param client_id: The environments client_id
        :type client_id: str
        :param client_secret: The environments client_secret
        :type client_secret: str
        """

    def __init__(self,
                 target_directory: str = None,
                 data_cluster_url: str = None,
                 management_cluster_url: str = None,
                 client_id: str = None,
                 client_secret: str = None,
                 *args, **kwargs):
        super(BadookTestOperator, self).__init__(*args, **kwargs)

        self.target_directory = target_directory
        self.data_cluster_url = data_cluster_url
        self.management_cluster_url = management_cluster_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.create_hook()

    def create_hook(self):
        self.hook = BadookTestsHook(target_directory=self.target_directory,
                                    data_cluster_url=self.data_cluster_url,
                                    management_cluster_url=self.management_cluster_url,
                                    client_id=self.client_id,
                                    client_secret=self.client_secret
                                    )

    def execute(self, context):
        self.hook.run()
