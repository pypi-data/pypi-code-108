#
# Copyright 2020 Nebulon, Inc.
# All Rights Reserved.
#
# DISCLAIMER: THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
# OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

from os import path
from .api import *

# Version for the package
dir_name = path.dirname(__file__)
filename = path.join(dir_name, 'VERSION')

with open(filename, "r") as fh:
    __version__ = fh.read()


class NebPyClient(
    GraphQLClient,
    AlertsMixin,
    AuditingMixin,
    DatacentersMixin,
    HostsMixin,
    KeyValueMixin,
    LunsMixin,
    NPodGroupMixin,
    NPodsMixin,
    NPodTemplateMixin,
    PhysicalDriveMixin,
    RacksMixin,
    RBACMixin,
    RecipeMixin,
    RoomsMixin,
    RowMixin,
    SessionMixin,
    SnapshotMixin,
    SpuMixin,
    SupportCaseMixin,
    UpdatesMixin,
    UserGroupMixin,
    UsersMixin,
    VolumeMixin,
    VSphereCredentialsMixin,
    WebHookMixin
):
    """Nebulon connection"""

    def __init__(
            self,
            username: str,
            password: str,
            verbose: bool = False,
            client_name: str = None,
            client_version: str = None):
        """Constructs Nebulon Python client instance to interact with Nebulon ON

        :param username: nebulon ON username
        :type username: str
        :param password: nebulon ON password
        :type password: str
        :param verbose: If set to `True` the Python client will print verbose
            information to the console when interacting with nebulon ON. By
            default this option is turned off.
        :type verbose: bool, optional
        :param client_name: Allows setting the client application name which is
            used by the audit log as the client. Default value is `nebpyclient`.
        :type client_name: str, optional
        :param client_version: Allows setting the client application version
            which is used by the audit log as the client. Default value is
            derived from the nebpyclient version information.
        :type client_version: str, optional

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: When the login failed.
        """

        GraphQLClient.__init__(
            self,
            verbose=verbose,
            client_name=client_name,
            client_version=client_version,
        )

        login_result = self.login(
            username,
            password,
        )

        if not login_result.success:
            raise Exception("Login failed")
