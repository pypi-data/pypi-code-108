"""
  Copyright (c) 2016- 2021, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
import csv
from _collections import defaultdict
import requests
from wiliot.cloud_apis.api_client import Client, WiliotCloudError
import json
from enum import Enum


class TagNotFound(Exception):
    pass


class LabelNotFound(Exception):
    pass


class GatewayNotFound(Exception):
    pass


class HttpEndpoint:
    def __init__(self, url, headers, method='POST'):
        self.url = url
        if type(headers) != dict:
            raise TypeError('This class expects headers to be a dictionary')
        self.headers = headers
        self.method = method


class MqttEndpoint:
    def __init__(self, url, topic, username=None, password=None, certificate=None):
        self.url = url
        self.topic = topic
        self.username = username
        self.password = password
        self.certificate = certificate


class Event(Enum):
    HRTB_F = 'HRTB_F'
    HRTB_S = 'HRTB_S'
    TEMP_C = 'TEMP_C'
    GONE = 'GONE'
    HERE = 'HERE'
    BACK = 'BACK'
    AWAY = 'AWAY'
    NTWK = 'NTWK'


class EventFilter:
    def __init__(self, event, confidence=0.5):
        assert isinstance(event, Event), "EventFilter must be initialized with an Event object"
        self.event = event
        self.active = True
        self.confidence = confidence


class EventPolicy:
    def __init__(self, policy_name, filters=None):
        assert len([x for x in filters if not(isinstance(x, EventFilter))]) == 0, "filters must be a list of " \
                                                                                  "EventFilte objects "
        self.policy_name = policy_name
        self.filters = filters

    def as_dict(self):
        return {
                'policyName': self.policy_name,
                'eventName': "",
                'filters': {x.event.name: {"active": x.active, "confidence": x.confidence} for x in self.filters}
        }


class ManagementClient(Client):
    def __init__(self, oauth_username, oauth_password, owner_id, env='', log_file=None):
        self.client_path = "owner/{owner_id}/".format(owner_id=owner_id)
        self.owner_id = owner_id
        super().__init__(oauth_username, oauth_password, env, log_file)

    def get_applications(self):
        """
        Get an owner's cloud 2 cloud applications
        :return: A list of applications registered for the owner
        """
        path = "application"
        res = self._get(path)
        return res.get('data', [])

    def get_tags_associated_to_app(self, app_id):
        """
        Get a list of tags associated to an application
        :param app_id: Required. Application ID
        :return: List of tags
        """
        path = "application/{}/tag".format(app_id)
        res = self._get(path)
        return res.get('data', [])

    def create_application(self, app_id, app_name,
                           event_fields, event_document,
                           http_endpoint=None, mqtt_endpoint=None, event_policy=None):
        """
        Create a new application for pushing events from Wiliot's cloud to your own cloud. The caller must
        provide exactly one of: HttpEndpoint and MqttEndpoint
        :param app_id: String - A unique ID for the app
        :param app_name: String
        :param event_fields: List of Event objects
        :param event_document: String - The body to be sent in the request. Can use event fields in {{}}
        :param http_endpoint: An HttpEndpoint object
        :param mqtt_endpoint: An MqttEndpoint object
        :param event_policy: Optional - An Event Policy object which defines which events to send together with
        parameters where applicable
        :return: True if successful. Otherwise False
        """
        # Caller must provide exactly one of http_endpoint or mqtt_endpoint
        assert bool(http_endpoint) != bool(mqtt_endpoint), "Was expecting exactly one of http_endpoint or mqtt_endpoint"
        # event_fields should be a list of strings
        assert isinstance(event_fields, list), "Was expecting a list of strings for event_fields"
        # event_policy should be an object of type EventPolicy
        assert isinstance(event_policy, EventPolicy), "Was expecting an object of type EventPolicy for event_policy"
        # event_policy
        path = 'application'
        payload = {
            'id': app_id,
            'name': app_name,
            'endpointType': 'http' if bool(http_endpoint) else 'mqtt',
            'ownerId': self.owner_id,
            'eventFields': {x: x for x in event_fields},
            'eventDocument': event_document,
            'eventPolicy': {'policyName': "", "eventName": ""} if event_policy is None else event_policy.as_dict()
        }
        if http_endpoint is not None:
            payload['httpEndpoint'] = vars(http_endpoint)
        if mqtt_endpoint is not None:
            payload['mqttEndpoint'] = vars(mqtt_endpoint)
        try:
            res = self._put(path, payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to create application")
            raise e

    def delete_application(self, app_id):
        """
        Delete an application
        :param app_id: Required. String - the ID of the application to delete
        :return: True if successful. Otherwise the error message
        """
        path = "application/{}".format(app_id)
        try:
            res = self._delete(path, payload=None)
            if not res["data"]:
                return res["message"]
            else:
                return True
        except WiliotCloudError as e:
            print("Failed to delete application")
            raise e

    def get_tags(self):
        """
        Get an owner's tags
        :return: A list of tags owned by the owner
        """
        path = "tag"
        tags = []
        res = self._get(path)
        while True:
            if "data" in res:
                tags = tags + [t["id"] for t in res["data"]]
            else:
                return tags
            if 'next' in res.keys():
                res = self._get(path + "?next={}".format(res["next"]))
            else:
                break
        return tags

    def get_tag_details(self, tag_id):
        """
        Get a tag's details including the applications it's associated with
        :param tag_id:
        :return: A dictionary containing the information returned by the API
        """
        path = "tag/{}".format(tag_id)
        result = self._get(path)
        return result["data"]

    def get_associated_apps_to_tag(self, tag_id):
        """
        Get a list of applications a tag is associated with
        :param tag_id: The tag ID
        :return: a list of tag IDs. Empty list if no associated application
        """
        path = "tag/{}/application".format(tag_id)
        response = self._get(path)
        return response.get("data", [])

    def serialize_tag(self, tag_payload, tag_id, apps = None):
        """
        Assign an ID to a tag using a payload from the tag. Optionally also associate the tag with one
        or more applications
        :param tag_payload: A payload from a Wiliot tag (starts with 0005)
        :param tag_id: The ID to assign to the tag
        :param apps: (optional) a list of application IDs to associate the tag with
        :return: True if successful, the error message otherwise
        """
        path = "serialize"
        payload = [
                {
                    "payload": tag_payload,
                    "tagId": tag_id
                }
            ]
        if apps is not None:
            payload[0]["applications"] = apps
        res = self._post(path, payload)
        if res["data"][0]["isSuccess"]:
            return True
        else:
            return res["data"][0]["message"]

    def batch_serialize_tags(self, data):
        """
        Perform a batch serialization of multiple tags using payloads
        :param data: A list of dictionaries, each of the following  format:
            {
                "payload": <tag payload to use for serialization>,
                "tagId": <the ID to assign to the tag>,
                "applications": [
                    <application-id-1>,
                    <application_id-2>
                ]
            }
        :return: True if successful
        """
        assert isinstance(data, list), "data argument must be a list"
        path = "serialize"
        res = self._post(path, data)
        # Count the number of successes and compare to number of requests
        if len([r for r in res["data"] if r["isSuccess"]]) == len(data):
            return True
        else:
            return res["data"]

    def associate_tags(self, tags, applications):
        """
        Associate one or more tags with one or more applications. all tags will be associated
        with all applications
        :param tags: A list containing one or more tag IDs
        :param applications: a list of applications' IDs to associate with
        :return: True if successful
        """
        payload = {
            "applications": applications,
            "tags": tags
        }
        path = "tag/associate"
        try:
            res = self._post(path, payload)
            return res["data"][0]["success"]
        except WiliotCloudError as e:
            print("Failed to associate tag")
            raise WiliotCloudError("Failed to associate tag(s). Received the following error: {}".format(e.args[0]))

    def batch_associate_tags(self, tags_file_path):
        """
        Associate multiple tags with one or more applications. All tags will be associated with all applications.
        The input is a CSV file. Each line includes: tagId,applicationId

        Multiple associations for the same tag can be achieved by including multiple lines in the CSV with the
        same tagId
        """

        def assoc_init():
            return []

        associations = defaultdict(assoc_init)
        try:
            with open(tags_file_path, 'r') as tags_file:
                reader = csv.DictReader(tags_file)
                for row in reader:
                    # Build a dictionary of associations where each key is an applicationId and the value is a list
                    # of tags to be associated with the applicationId
                    associations[row["applicationId"]].append(row["tagId"].lower())
        except FileNotFoundError:
            print('Could not open {} for reading'.format(tags_file_path))
        except KeyError as e:
            print("The provided file is missing the {} field".format(e.args[0]))
        except Exception as e:
            raise e
        # Next - use the list to perform batch associations
        result = True
        for key, value in associations.items():
            result = result and self.associate_tags(tags=value, applications=[key])
        return result

    def disassociate_tags(self, tags, applications):
        """
        Disassociate one or more tags from one or more applications they are associated with
        :param tags: a list of Tag IDs to disassociate
        :param applications: A list of application IDs to disassociate the tags from
        :return: True if successful
        """
        payload = {
            "applications": applications,
            "tags": tags
        }
        path = "tag/disassociate"
        result = self._post(path, payload)
        return result.get("data").get("success")

    def batch_disassociate_tags(self, tags_file_path):
        """
        Disassociate multiple tags from multiple applications. Tags and applications are provided in a CSV file.
        The file needs to have, as a minimum the following columns: tagId, applicationId
        :param tags_file_path: A string representing the path to the CSV file
        :return: True if all disassociations were successful
        """

        def assoc_init():
            return []

        associations = defaultdict(assoc_init)
        try:
            with open(tags_file_path, 'r') as tags_file:
                reader = csv.DictReader(tags_file)
                for row in reader:
                    # Build a dictionary of associations where each key is an applicationId and the value is a list
                    # of tags to be associated with the applicationId
                    associations[row["applicationId"]].append(row["tagId"].lower())
        except FileNotFoundError:
            print('Could not open {} for reading'.format(tags_file_path))
        except KeyError as e:
            print("The provided file is missing the {} field".format(e.args[0]))
        except Exception as e:
            raise e
        # Next - use the list to perform batch disassociations
        result = True
        for key, value in associations.items():
            result = result and self.disassociate_tags(tags=value, applications=[key])
        return result

    def get_labels(self):
        """
        Get an owner's labels
        :return: A list of strings representing the labels
        """
        path = "label"
        labels = []
        res = self._get(path)
        while True:
            if "data" in res:
                labels = labels + res["data"]
            else:
                return labels
            if 'next' in res.keys():
                res = self._get(path + "?next={}".format(res["next"]))
            else:
                break
        return labels

    def get_label(self, label_id):
        """
        Get one label
        :param label_id: The label's ID to get the details for
        :return: The requested label's ID if successful
        :raises: LabelNotFound if the label ID doesn't exist
        """
        path = "label/{}".format(label_id)
        try:
            res = self._get(path)
            return res["data"]
        except WiliotCloudError as e:
            if e.args[0]['error'].lower().find('label does not exist') != -1:
                raise LabelNotFound
            else:
                raise

    def get_label_tags(self, label_id):
        """
        Get a list of tags belonging to a table
        :param label_id: The label ID to get the tags for
        :return: a list of tags belonging to the label
        :raises: LabelNotFound if the label doesn't exist
        """
        path = "label/{}/tag".format(label_id)
        try:
            res = self._get(path)
            return res["data"]
        except WiliotCloudError:
            raise

    def create_label(self, label_id, tag_ids=None):
        """
        Create a new label
        :param label_id: The ID to give the new label
        :param tag_ids: Optional. A list of tag IDs to add to the label
        :return: True if successful
        """
        path = "label"
        payload = {
            "label": label_id
        }
        res = self._put(path, payload)
        if res['data'] and tag_ids is not None:
            res = self.add_tags_to_label(label_id, tag_ids)
            return res
        return res['data']

    def add_tags_to_label(self, label_id, tag_ids):
        """
        Add one or more tags to a label
        :param label_id: The label ID to add the tags to
        :param tag_ids: A list of tag IDs to add
        :return: True if successful
        """
        path = "tag/label"
        payload = {
            "labels": [label_id],
            "tags": tag_ids
        }
        res = self._post(path, payload)
        return res["data"][0]["success"]

    def remove_tags_from_label(self, label_id, tag_ids):
        """
        Remove one or more tags from label
        :param label_id: The label to remove tags from
        :param tag_ids: The IDs of tags to remove from the label
        :return: True if successful
        """
        path = "tag/delabel"
        payload = {
            "labels": [label_id],
            "tags": tag_ids
        }
        res = self._post(path, payload)
        return res["data"]["success"]

    def delete_label(self, label_id):
        """
        Delete a label
        :param label_id: The ID of the label to delete
        :return: True if succesful
        :raise: LabelNotFound if the label doesn't exist
        """
        path = "label/{}".format(label_id)
        res = self._delete(path, payload={})
        return res["data"]

    def associate_labels(self, labels, applications):
        """
        Associate one or more tags with one or more applications. all tags will be associated
        with all applications
        :param labels: A list containing one or more label IDs
        :param applications: a list of applications' IDs to associate with
        :return: True if successful
        """
        payload = {
            "applications": applications,
            "labels": labels
        }
        path = "label/associate"
        try:
            res = self._post(path, payload)
            return res["data"][0]["success"]
        except WiliotCloudError as e:
            print("Failed to associate tag")
            raise WiliotCloudError("Failed to associate tag(s). Received the following error: {}".format(e.args[0]))

    def get_associated_apps_to_label(self, label_id):
        """
        Get a list of applications a label is associated with
        :param label_id: The tag ID
        :return: a list of tag IDs. Empty list if no associated application
        """
        path = "label/{}/application".format(label_id)
        response = self._get(path)
        res = response.get("data", [])
        return res

    def disassociate_labels(self, labels, applications):
        """
        Disassociate one or more tags from one or more applications they are associated with
        :param labels: a list of Tag IDs to disassociate
        :param applications: A list of application IDs to disassociate the tags from
        :return: True if successful
        """
        payload = {
            "applications": applications,
            "labels": labels
        }
        path = "label/disassociate"
        result = self._post(path, payload)
        return result.get("data").get("success")

    def get_gateways(self):
        """
        Get a list of gateways owned by the owner
        :return: A list of gateways
        """
        path = "gateway"
        response = self._get(path)
        res = response.get("data", [])
        return res

    def get_gateway_details(self, gateway_id):
        """
        Get a gateway's details including the applications it's associated with
        :param gateway_id:
        :return: A dictionary containing the information returned by the API
        """
        path = "gateway/{}".format(gateway_id)
        result = self._get(path)
        try:
            return result["data"]
        except KeyError:
            raise GatewayNotFound

    def register_gateway(self, gateways):
        """
        Register one or more Wiliot gateways
        :param gateways: list of gateway IDs to register
        :return: True if successful
        """
        assert isinstance(gateways, list), "gateways parameter must be a list of gateway IDs"
        payload = {
            "gateways": gateways
        }
        path = "gateway"
        response = self._put(path=path, payload=payload)
        return response["data"].lower() == "ok"

    def approve_gateway(self, gateway_id, user_code):
        """
        Approve a gateway. This endpoint must be called before a gateway can start pushing
        Wiliot packet payloads to the Wiliot cloud
        :param gateway_id: The ID of the gateway to approve
        :param user_code: The user code can be obtained by calling the get_gateway_details function. Note that
        the API will return a userCode only gateways in a 'registered' state
        :return: True if successful
        """
        path = "gateway/{}/approve".format(gateway_id)
        payload = {
            "userCode": user_code,
            "ownerId": self.owner_id,
            "gatewayId": gateway_id
        }
        response = self._post(path, payload)
        return response["data"].lower() == "ok"

    def delete_gateway(self, gateway_id):
        """
        Delete a gateway from the Wiliot cloud. This gateway will no longer be able to push Wiliot packet
        payloads to the Wiliot cloud
        :param gateway_id: The Id of the gateway to delete
        :return: True if successful
        """
        path = "gateway/{}".format(gateway_id)
        response = self._delete(path, payload={})
        return response['data'].lower().find("success") != -1

    def register_third_party_gateway(self, gateway_id, gateway_type, gateway_name):
        """
        Register a third-party (non-Wiliot) gateway and receive an access and refresh token
        to be used by the gateway for sending tag payloads to the Wiliot cloud
        :param gateway_id: String - A unique ID for the gateway
        :param gateway_type: String - Can be used to group gateways of the same type
        :param gateway_name: String - A human readable name for the gateway
        :return: A dictionary of the following format:
        {
            "data": {
                "access_token": "...",
                "expires_in": 43199,
                "refresh_token": "...",
                "token_type": "Bearer",
                "userId": "...",
                "ownerId": "wiliot"
            }
        }
        """
        path = "gateway/{}/mobile".format(gateway_id)
        payload = {
            "gatewayType": gateway_type,
            "gatewayName": gateway_name
        }
        response = self._post(path, payload=payload)
        return response

    def get_gateways_associated_to_app(self, app_id):
        """
        Get a list of gateways associated to an application
        :param app_id: Required. Application ID
        :return: List of gateways
        """
        path = "application/{}/gateway".format(app_id)
        res = self._get(path)
        return res.get('data', [])

    def associate_gateways(self, gateways, applications):
        """
        Associate one or more gateways with one or more applications. all gateways will be associated
        with all applications
        :param gateways: A list containing one or more gateway IDs
        :param applications: a list of applications' IDs to associate with
        :return: True if successful
        """
        payload = {
            "applications": applications,
            "gateways": gateways
        }
        path = "gateway/associate"
        try:
            res = self._post(path, payload)
            return False not in [r['success'] for r in res["data"]]
        except WiliotCloudError as e:
            print("Failed to associate gateway")
            raise WiliotCloudError("Failed to associate gateway(s). Received the following error: {}".format(e.args[0]))

    def disassociate_gateways(self, gateways, applications):
        """
        Disassociate one or more gateways from one or more applications. all gateways will be disassociated
        with all applications
        :param gateways: A list containing one or more gateway IDs
        :param applications: a list of applications' IDs to disassociate from
        :return: True if successful
        """
        payload = {
            "applications": applications,
            "gateways": gateways
        }
        path = "gateway/disassociate"
        try:
            res = self._post(path, payload)
            return res["data"]["success"]
        except WiliotCloudError as e:
            print("Failed to associate gateway")
            raise WiliotCloudError("Failed to associate gateway(s). Received the following error: {}".format(e.args[0]))

    # Bridge related functionality
    def get_bridges_connected_to_gateway(self, gateway):
        """
        Get a list of gateways connected (controlled by) a gateway
        :param gateway: String - A Gateway ID to query for
        :return: A list of dictionaries for all bridges
        """
        path = "gateway/{}/bridge".format(gateway)
        try:
            res = self._get(path)
            return res["data"]
        except WiliotCloudError as e:
            if e.args[0].lower().find("not found") != -1:
                raise WiliotCloudError("Gateway {} could not be found".format(gateway))
            else:
                raise

    def get_bridge(self, bridge_id):
        """
        Get information about a specific bridge
        :param bridge_id: String - the ID of the bridge to get information about
        :return: A dictionary containing bridge information
        :raises: WiliotCloudError if bridge cannot be found
        """
        path = "bridge/{}".format(bridge_id)
        try:
            res = self._get(path)
            return res["data"]
        except WiliotCloudError as e:
            raise

    def claim_bridge(self, bridge_id):
        """
        Claim bridge ownership
        :param bridge_id: String - The ID of the bridge to claim
        :return: True if successful
        """
        path = "bridge/{}/claim".format(bridge_id)
        try:
            res = self._post(path, None)
            return res["message"].lower().find("succesfully") != -1
        except WiliotCloudError as e:
            print("Failed to claim bridge")
            raise WiliotCloudError("Failed to claim bridge. Received the following error: {}".format(e.args[0]))

    def unclaim_bridge(self, bridge_id):
        """
        Release ownership of claimed bridge
        :param bridge_id: String - The ID of the bridge to release
        :return: True if successful
        """
        path = "bridge/{}/unclaim".format(bridge_id)
        try:
            res = self._post(path, None)
            return res["message"].lower().find("succesfully") != -1
        except WiliotCloudError as e:
            print("Failed to release bridge")
            raise WiliotCloudError("Failed to release claimed bridge. Received the following error: {}".format(e.args[0]))