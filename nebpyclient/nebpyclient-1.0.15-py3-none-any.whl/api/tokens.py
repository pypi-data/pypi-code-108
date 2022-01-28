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

import requests
from .common import read_value
from .issues import Issues

TOKEN_TIMEOUT_SECONDS = 30
"""Timeout for token delivery"""


class MustSendTargetDNS:
    """Used in mutations for on-premises infrastructure via security triangle

    Represents a definition of SPUs that a security token needs to be sent to.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new MustSendTargetDNS object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__control_port_dns = read_value(
            "controlPortDNS", response, str, True)
        self.__data_port_dns = read_value(
            "dataPortDNS", response, str, True)

    @property
    def control_port_dns(self) -> str:
        """The DNS name of the SPU's control port"""
        return self.__control_port_dns

    @property
    def data_port_dns(self) -> [str]:
        """List of DNS names of the SPU's data ports"""
        return self.__data_port_dns

    @staticmethod
    def fields():
        return [
            "controlPortDNS",
            "dataPortDNS",
        ]


class TokenResponse:
    """Used in mutations for on-premises infrastructure via security triangle

    Represents a response for a mutation that alters the customers'
    on-premises infrastructure and requires the completion of the security
    triangle.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new TokenResponse object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__token = read_value(
            "token", response, str, True)
        self.__wait_on = read_value(
            "waitOn", response, str, True)
        self.__target_ips = read_value(
            "targetIPs", response, str, True)
        self.__data_target_ips = read_value(
            "dataTargetIPs", response, str, False)
        self.__must_send_target_dns = read_value(
            "mustSendTargetDNS", response, MustSendTargetDNS, False)
        self.__issues = read_value(
            "issues", response, Issues, False)

    @property
    def token(self) -> str:
        """Token that needs to be delivered to on-premises SPUs"""
        return self.__token

    @property
    def wait_on(self) -> str:
        """Unique identifier of the resource that is about to be created"""
        return self.__wait_on

    @property
    def target_ips(self) -> [str]:
        """List of control IP addresses of SPUs involved in the mutation"""
        return self.__target_ips

    @property
    def data_target_ips(self) -> [str]:
        """List of data IP addresses of SPUs involved in the mutation"""
        return self.__data_target_ips

    @property
    def must_send_target_dns(self) -> [MustSendTargetDNS]:
        """List of data IP addresses of SPUs involved in the mutation"""
        return self.__must_send_target_dns

    @property
    def issues(self) -> Issues:
        """List of errors and warnings associated with the mutation"""
        return self.__issues

    @staticmethod
    def fields():
        return [
            "token",
            "waitOn",
            "targetIPs",
            "dataTargetIPs",
            "mustSendTargetDNS{%s}" % ",".join(MustSendTargetDNS.fields()),
            "issues{%s}" % ",".join(Issues.fields()),
        ]

    def _issue_one_token(
            self,
            ip: str
    ) -> any:
        url = "https://%s" % ip
        try:
            response = requests.post(
                url=url,
                data=self.token,
                timeout=TOKEN_TIMEOUT_SECONDS
            )
            if 200 <= response.status_code < 300:
                response_text = response.text.strip()
                if response_text == "OK" or response_text == "\"OK\"":
                    return True
                return response.json()

            # if we got here, there was an error
            reason = response.text

        except requests.exceptions.ConnectTimeout:
            reason = "request timed out"

        print("Failed to deliver token to %s: %s" % (ip, reason))
        return False

    def deliver_token(self) -> any:
        """Delivers the token to SPUs

        For recipe engine v1 requests, a boolean value is returned that
        indicates if the request was successful. For recipe v2 requests a dict
        is returned that includes ``recipe_id_to_wait_on`` and
        ``pod_uuid_to_wait_on`` that can be used to query the status of the
        recipe and its completion.

        :raises Exception: When token delivery failed.

        :returns any: The response received from nebulon ON through the proxy
            services processing unit (SPU).
        """

        # first to must_send_target_dns - need to send to all of them
        if self.must_send_target_dns is not None:

            for cur in self.must_send_target_dns:

                # first send the token to the control port
                if self._issue_one_token(cur.control_port_dns):
                    continue

                # if this failed, send the token to the data ports
                delivery_success = False

                for dp in cur.data_port_dns:
                    if self._issue_one_token(dp):
                        delivery_success = True
                        break

                if not delivery_success:
                    raise Exception("Unable to deliver token to mandatory SPUs")

        # second, send the token to one of the remaining SPUs
        ips = self.target_ips
        if self.data_target_ips is not None:
            ips = ips + self.data_target_ips

        for ip in ips:
            result = self._issue_one_token(ip)

            if result:
                return result

        raise Exception("Unable to deliver token any SPU")


class PodTokenResponse:
    """Response from the server used for nPod related mutations

    __This object is deprecated__

    Represents a response for a nPod related mutation that alters the customers'
    on-premises infrastructure and requires the completion of the security
    triangle.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new PodTokenResponse object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__token_resp = read_value(
            "tokenResp", response, TokenResponse, False)
        self.__issues_res = read_value(
            "IssuesRes", response, Issues, False)

    @property
    def token(self) -> TokenResponse:
        """Token that needs to be delivered to on-premises SPUs"""
        return self.__token_resp

    @property
    def issues(self) -> Issues:
        """List of errors and warnings associated with the mutation"""
        return self.__issues_res

    @staticmethod
    def fields():
        return [
            "tokenResp{%s}" % ",".join(TokenResponse.fields()),
            "IssuesRes{%s}" % ",".join(Issues.fields()),
        ]
