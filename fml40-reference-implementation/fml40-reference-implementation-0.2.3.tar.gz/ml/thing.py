import asyncio

import s3i
from s3i.identity_provider import IdentityProvider, TokenType
from s3i.directory import Directory
from s3i.repository import Repository
# from s3i.broker import BrokerREST, Broker
from s3i.event_system import EventManager
from ml.s3i_tools import Broker, BrokerREST
from s3i.broker_message import GetValueReply, ServiceReply, SetValueReply, CustomEventReply, GetValueRequest, \
    ServiceRequest, SetValueRequest
from s3i.exception import raise_error_from_s3ib_msg, S3IBMessageError, S3IDittoError, S3IIdentityProviderError
from ml.app_logger import APP_LOGGER
from ml.tools import find_broker_endpoint
from ml.callback import CallbackManager
from ml.parameters import Parameters
from ast import literal_eval
import json
import uuid
import copy


class Thing:
    _ON_THING_START_OK = "_on_thing_start_ok"
    _ON_IDP_START_OK = "_on_idp_start_ok"
    _ON_DIRECTORY_START_OK = "_on_directory_start_ok"
    _ON_REPOSITORY_START_OK = "_on_repository_start_ok"
    _ON_BROKER_START_OK = "_on_broker_start_ok"

    def __init__(
            self,
            entry,
            oauth2_secret,
            grant_type,
            username=None,
            password=None,
            is_repository=False,
            is_broker=False,
            is_broker_rest=False,
            is_event_manager=False,
            parameters=Parameters(),
            loop=asyncio.get_event_loop()

    ):
        self.__entry = entry
        self.__secret = oauth2_secret
        self.__grant_type = grant_type
        self.__username = username
        self.__password = password
        self.__token = None
        self.__is_repository = is_repository
        self.__is_broker = is_broker
        self.__is_broker_rest = is_broker_rest
        self.__is_event_manager = is_event_manager
        self.loop = loop
        self.__resGetValue = []

        self.callbacks = CallbackManager()
        self.parameters = parameters

    @property
    def entry(self):
        return self.__entry

    @property
    def identifier(self):
        return self.__entry.identifier

    def run_forever(self):
        try:
            self.__setup_thing_json_sync()
            self.__connect_to_s3i()
            self.loop.run_forever()

        except KeyboardInterrupt:
            APP_LOGGER.info("[S3I]: Disconnect from S3I")
            self.loop.close()

    def add_on_thing_start_ok_callback(self, callback_func, one_shot, is_async, *args, **kwargs):
        self.callbacks.add(
            self._ON_THING_START_OK,
            callback_func,
            one_shot,
            is_async,
            *args,
            **kwargs
        )

    def add_on_idp_start_ok_callback(self, callback_func, one_shot, is_async, *args, **kwargs):
        self.callbacks.add(
            self._ON_IDP_START_OK,
            callback_func,
            one_shot,
            is_async,
            *args,
            **kwargs
        )

    def add_on_directory_start_ok_callback(self, callback_func, one_shot, is_async, *args, **kwargs):
        self.callbacks.add(
            self._ON_DIRECTORY_START_OK,
            callback_func,
            one_shot,
            is_async,
            *args,
            **kwargs
        )

    def add_on_repository_start_ok_callback(self, callback_func, one_shot, is_async, *args, **kwargs):
        self.callbacks.add(
            self._ON_REPOSITORY_START_OK,
            callback_func,
            one_shot,
            is_async,
            *args,
            **kwargs
        )

    def add_on_broker_start_ok_callback(self, callback_func, one_shot, is_async, *args, **kwargs):
        def _add_on_channel_open_callback(_thing, _callback, _one_shot, *_args, **_kwargs):
            _thing.broker.add_on_channel_open_callback(
                callback_func,
                one_shot,
                *args,
                **kwargs
            )
        self.callbacks.add(
            self._ON_BROKER_START_OK,
            _add_on_channel_open_callback,
            one_shot,
            is_async, # the following parameters are *args
            self,
            callback_func,
            one_shot,
            *args,
            **kwargs
        )

    def add_ml40_implementation(self, implementation_object, ml40_feature, *args, **kwargs):
        def _add_ml40_implementation(_thing, _implementation_object, _ml40_feature, *_args, **_kwargs):
            feature = _thing.entry.features.get(_ml40_feature, None)
            if feature is None:
                APP_LOGGER.critical(
                    "Functionality %s is not one of the build-in functionalities" % _ml40_feature
                )
            else:
                APP_LOGGER.info("Implementation object is added into the functionality %s" % _ml40_feature)
                impl_ins = _implementation_object(*_args, **_kwargs)
                impl_ins.class_name = _ml40_feature
                _thing.entry.features[_ml40_feature] = impl_ins

        self.add_on_thing_start_ok_callback(
            _add_ml40_implementation,
            True,
            False,
            self,
            implementation_object,
            ml40_feature,
            *args,
            **kwargs
        )

    def __connect_to_s3i(self):
        self.__setup_identity_provider()
        self.__setup_directory()
        if self.__is_repository:
            self.__setup_repository()
        if self.__is_broker:
            self.__setup__broker()
        if self.__is_event_manager:
            self.__setup_event_system()

    def __setup_identity_provider(self):
        APP_LOGGER.info("[S3I]: Connect to IdentityProvider")
        self.idp = IdentityProvider(
            grant_type=self.__grant_type,
            identity_provider_url=self.parameters.idp_url,
            realm=self.parameters.idp_realm,
            client_id=self.identifier,
            client_secret=self.__secret,
            username=self.__username,
            password=self.__password
        )
        try:
            self.__token = self.idp.get_token(TokenType.ACCESS_TOKEN)
        except S3IIdentityProviderError as err:
            APP_LOGGER.error("[S3I]: {}".format(err))
        else:
            APP_LOGGER.info("[S3I]: Access Token granted")
        self.loop.call_later(self.__get_remaining_time_to_refresh(),
                             self.__refresh_token_recur)
        self.callbacks.process(
            self._ON_IDP_START_OK,
            self.loop
        )

    def __refresh_token_recur(self):
        APP_LOGGER.info("[S3I]: Get refreshed access token from Identity Provider")
        self.idp._refresh_token(self.idp.get_token(TokenType.REFRESH_TOKEN))
        # Keycloak returns sometimes a invalid access token, even through it was gained via valid refresh token
        # Bug
        if self.idp._token_bundle["expires_in"] < 60:
            self.idp._authenticate(scope="openid")

        self.__token = self.idp._token_bundle["access_token"]

        # refresh s3i object
        APP_LOGGER.info("[S3I]: Refresh token to Directory")
        self.dir.pass_refreshed_token(self.__token)
        if self.__is_repository:
            APP_LOGGER.info("[S3I]: Refresh token to Repository")
            self.repo.pass_refreshed_token(self.__token)
        if self.__is_broker:
            self.broker.reconnect_token_expired(self.__token)
        self.loop.call_later(self.__get_remaining_time_to_refresh(),
                             self.__refresh_token_recur)

    def __get_remaining_time_to_refresh(self):
        remaining_time = self.idp._time_until_token_valid()
        safety_margin = 5
        return remaining_time - safety_margin

    def __setup_thing_json_sync(self):
        APP_LOGGER.info("[S3I]: Start the thing")
        self.__recursively_update_dt_json(frequency=self.parameters.thing_sync_freq)
        self.callbacks.process(
            prefix=self._ON_THING_START_OK,
            loop=self.loop
        )

    def __setup_directory(self):
        APP_LOGGER.info("[S3I]: Connect to Directory")
        self.dir = Directory(
            s3i_dir_url=self.parameters.dir_url,
            token=self.__token
        )
        self.__recursively_update_directory(frequency=self.parameters.dir_sync_freq)
        self.callbacks.process(
            self._ON_DIRECTORY_START_OK,
            self.loop
        )

    def __setup__broker(self):
        # TODO Bug: by network disconnect the connection to broker keeps still connected
        # TODO allow having more channels + consumers
        # TODO send via BrokerREST()
        endpoint = find_broker_endpoint(self.dir, self.identifier)
        APP_LOGGER.info("[S3I]: Connecting to Broker")
        if self.__is_broker_rest:
            self.broker = BrokerREST(token=self.__token)
        else:
            self.broker = Broker(
                token=self.__token,
                endpoint=endpoint,
                callback=self.on_broker_message_callback,
                loop=self.loop
            )
            self.broker.connect()
        self.callbacks.process(
            self._ON_BROKER_START_OK,
            self.loop
            )

    def __setup_repository(self):
        APP_LOGGER.info("[S3I]: Connect to Repository")
        self.repo = Repository(
            s3i_repo_url=self.parameters.repo_url,
            token=self.__token
        )
        self.__recursively_update_repository(frequency=self.parameters.repo_sync_freq)
        self.callbacks.process(
            self._ON_REPOSITORY_START_OK,
            self.loop
        )

    def __setup_event_system(self):
        # TODO implement event system
        self.event_manager = EventManager(
            json_entry=self.entry.dt_json
        )
        """
        self.event_manager = EventManager(
        )
        """

    def __recursively_update_directory(self, frequency):
        try:
            self.dir.updateThingIDBased(thingID=self.identifier, payload=self.__entry.refresh_directory_entry(
                current_dir_json=self.dir.queryThingIDBased(self.identifier)
            ))
        except S3IDittoError as err:
            APP_LOGGER.error("[S3I]: {}".format(err))
        if frequency != 0:
            self.loop.call_later(
                1 / frequency,
                self.__recursively_update_directory,
                frequency
            )

    def __recursively_update_repository(self, frequency):
        try:
            self.repo.updateThingIDBased(thingID=self.identifier, payload=self.__entry.refresh_repository_entry())
        except S3IDittoError as err:
            APP_LOGGER.error("[S3I]: {}".format(err))
        if frequency != 0:
            self.loop.call_later(
                1 / frequency,
                self.__recursively_update_repository,
                frequency
            )

    def __recursively_update_dt_json(self, frequency):
        self.__entry.refresh_dt_json()
        if frequency != 0:
            self.loop.call_later(
                1 / frequency,
                self.__recursively_update_dt_json,
                frequency
            )

    def on_broker_message_callback(self, ch, method, properties, body):
        """Parses body (content of a S3I-B message) and delegates the
        processing of the message to a separate method. The method is
        selected according to the message's type.

        :param body: S3I-B message

        """
        try:
            body = literal_eval(body.decode('utf-8'))
        except ValueError:
            body = json.loads(body)
        # Add S3I-B Message validate
        try:
            body = raise_error_from_s3ib_msg(body, S3IBMessageError)
        except S3IBMessageError as e:
            APP_LOGGER.error("[S3I]: {}".format(e))
        else:
            message_type = body.get("messageType")

            __log = "[S3I]: Received a S3I-B {}: {}".format(
                message_type, json.dumps(body, indent=2)
            )
            APP_LOGGER.info(__log)

            if message_type == "userMessage":
                self.on_user_message(body)
            elif message_type == "serviceRequest":
                self.loop.create_task(self.on_service_request(body))
            elif message_type == "getValueRequest":
                self.on_get_value_request(body)
            elif message_type == "setValueRequest":
                self.on_set_value_request(body)
            elif message_type == "eventSubscriptionRequest":
                self.on_event_subscription_request(body)
            else:
                pass

    def on_user_message(self, msg):
        """Handles incoming S³I-B UserMessages.

        :param msg: S³I-B UserMessages

        """
        pass

    def on_get_value_request(self, msg):
        """Handles incoming GetValueRequest message. Looks up the value specified in msg and
        sends a GetValueReply message back to the sender.

        :param msg: GetValueRequest

        """
        req = GetValueRequest(base_msg=msg)
        request_sender = req.base_msg.get("sender")
        request_msg_id = req.base_msg.get("identifier")
        request_sender_endpoint = req.base_msg.get("replyToEndpoint")
        attribute_path = req.base_msg.get("attributePath")
        reply_msg_uuid = "s3i:" + str(uuid.uuid4())

        try:
            __log = "[S3I]: Search the given attribute path: {}".format(attribute_path)
            APP_LOGGER.info(__log)
            value = self._uriToData(attribute_path)
        except KeyError:
            value = "Invalid attribute path"
            __log = "[S3I]: " + value
            APP_LOGGER.critical(__log)

        get_value_reply = GetValueReply()
        get_value_reply.fillGetValueReply(
            sender=self.identifier,
            receivers=[request_sender],
            message_id=reply_msg_uuid,
            replying_to_msg=request_msg_id,
            value=value
        )

        res = self.broker.send(
            endpoint=request_sender_endpoint,
            msg=get_value_reply.base_msg
        )
        if res:
            APP_LOGGER.info("[S3I]: Sending getValueReply back")
        else:
            APP_LOGGER.error("[S3I]: Sending getValueReply failed")

    def _uriToData(self, uri):
        """Returns a copy of the value found at uri.

        :param uri: Path to value
        :rtype: Feature

        """

        if uri == "":
            return self.__entry.dt_json
        else:
            uri_list = uri.split("/")
            if uri_list[0] == "features":
                try:
                    return self.__entry.dt_json[uri]
                except KeyError:
                    return "Invalid attribute path"

            try:
                self._getValue(self.__entry.dt_json, uri_list)
            except Exception:
                return "Invalid attribute path"
            if self.__resGetValue.__len__() == 0:
                return "Invalid attribute path"
            response = copy.deepcopy(self.__resGetValue)
            self.__resGetValue.clear()
            if response.__len__() == 1:
                return response[0]
            else:
                return response

    def _getValue(self, source, uri_list):
        """Searches for the value specified by uri_list in source and stores
        the result in __resGetValue.

        :param source: Object that is scanned
        :param uri_list: List containing path

        """

        # ??? What if the uri points to a Value object?
        # Shouldn't it be serialized?!
        value = source[uri_list[0]]
        if uri_list.__len__() == 1:
            # if is ditto-feature
            if isinstance(value, str):
                try:
                    stringValue_split = value.split(":")
                    if stringValue_split[0] == "ditto-feature":
                        value = self.__entry.dt_json["features"][stringValue_split[1]][
                            "properties"
                        ][uri_list[0]]
                except Exception:
                    pass
            self.__resGetValue.append(value)
            return
        if isinstance(value, dict):
            # ??? uri_list.pop(0) better?!
            del uri_list[0]
            self._getValue(value, uri_list)
        if isinstance(value, list):
            if isinstance(value[0], (str, int, float, bool, list)):
                return value
            if isinstance(value[0], dict):
                for item in value:
                    if item["class"] == "ml40::Thing":
                        for i in item["roles"]:
                            if self._findValue(i, uri_list[1]):
                                uri_list_1 = copy.deepcopy(uri_list)
                                del uri_list_1[:2]
                                self._getValue(item, uri_list_1)
                        _f = self._findValue({"identifier": item.get("identifier")}, uri_list[1]) or \
                             self._findValue({"name": item.get("name")}, uri_list[1])
                        if _f:
                            uri_list_1 = copy.deepcopy(uri_list)
                            del uri_list_1[:2]
                            self._getValue(item, uri_list_1)
                    else:
                        if self._findValue(item, uri_list[1]):
                            uri_list_1 = copy.deepcopy(uri_list)
                            del uri_list_1[:2]
                            if not uri_list_1:
                                self.__resGetValue.append(item)
                                return
                            else:
                                self._getValue(item, uri_list_1)
        if isinstance(value, (str, int, float, bool)):
            # if is ditto-feature
            if isinstance(value, str):
                try:
                    stringValue_split = value.split(":")
                    if stringValue_split[0] == "ditto-feature":
                        value = self.__entry.dt_json["features"][stringValue_split[1]][
                            "properties"
                        ][uri_list[0]]
                except Exception:
                    pass
            self.__resGetValue.append(value)

    def _findValue(self, dic, value):
        """Returns true if value has been found in json, otherwise returns false.

        :param dic: dictionary
        :param value:
        :returns:
        :rtype:

        """

        for val in dic.values():
            if val == value:
                return True
        return False

    async def on_service_request(self, body_json):
        """Handles S³I-B ServiceRequests. Executes the method of the
        functionality specified in serviceType and send a ServiceReply
        back to the sender.

        :param body_json: ServiceRequest

        """
        req = ServiceRequest(base_msg=body_json)
        service_type = req.base_msg.get("serviceType")
        parameters = req.base_msg.get("parameters")
        request_sender = req.base_msg.get("sender")
        request_id = req.base_msg.get("identifier")

        service_reply = ServiceReply()
        service_functionality = service_type.split('/')[0]
        service_functionality_obj = self.entry.features.get(service_functionality)
        if service_functionality_obj is None:
            APP_LOGGER.critical(
                "[S3I]: Functionality %s is not one of the built-in functionalities in %s!"
                % (service_functionality, self.entry.name)
            )
            service_reply.fillServiceReply(
                sender=self.identifier,
                receivers=[request_sender],
                service_type=service_type,
                results={"error": "invalid functionalities (serviceType) {}".format(service_functionality)},
                replying_to_msg=request_id,
                message_id="s3i:{}".format(uuid.uuid4())
            )
        else:
            # TODO: Call right functionality.
            try:
                method = getattr(service_functionality_obj, service_type.split('/')[1])
            except AttributeError:
                APP_LOGGER.critical(
                    "[S3I]: Method %s is not one of the built-in functionalities in %s!" % (
                        service_type.split('/')[1], self.entry.name)
                )
                service_reply.fillServiceReply(
                    sender=self.identifier,
                    receivers=[request_sender],
                    service_type=service_type,
                    replying_to_msg=request_id,
                    message_id="s3i:{}".format(uuid.uuid4()),
                    results={"error": "invalid method {}".format(service_type.split('/')[1])},
                )
            except IndexError:
                APP_LOGGER.critical(
                    "[S3I]: ServiceType consists of functionality and method name."
                )
                service_reply.fillServiceReply(
                    sender=self.identifier,
                    receivers=[request_sender],
                    service_type=service_type,
                    replying_to_msg=request_id,
                    results={"error": "method missing"},
                    message_id="s3i:{}".format(uuid.uuid4())
                )
            else:
                __log = "[S3I]: Execute the function {0} of the class {1}".format(service_type.split('/')[1],
                                                                                  service_type.split('/')[0])
                APP_LOGGER.info(__log)
                try:
                    result = await method(**parameters)
                except TypeError:
                    APP_LOGGER.critical("[S3I]: Invalid function arguments")
                    service_reply.fillServiceReply(
                        sender=self.identifier,
                        receivers=[request_sender],
                        service_type=service_type,
                        replying_to_msg=request_id,
                        results={"error": "invalid function arguments (parameters)"},
                        message_id="s3i:{}".format(uuid.uuid4())
                    )
                else:
                    if isinstance(result, bool):
                        result = {"ok": result}
                    elif result is None:
                        result = "None"
                    service_reply.fillServiceReply(
                        sender=self.identifier,
                        receivers=[request_sender],
                        service_type=service_type,
                        replying_to_msg=request_id,
                        results=result,
                        message_id="s3i:{}".format(uuid.uuid4())
                    )

        res = self.broker.send(
            endpoint=body_json.get("replyToEndpoint", None),
            msg=service_reply.base_msg)

        if res:
            APP_LOGGER.info("[S3I]: Sending serviceReply back")
        else:
            APP_LOGGER.error("[S3I]: Sending serviceReply failed")

    def on_set_value_request(self, msg):
        """Handles incoming S³I-B SetValueRequest. Prints the content of msg to stdout.

        :param msg: GetValueReply

        """
        set_value_reply = SetValueReply()

        req = SetValueRequest(base_msg=msg)

        request_sender = req.base_msg.get("sender")
        request_msg_id = req.base_msg.get("identifier")
        request_sender_endpoint = req.base_msg.get("replyToEndpoint")
        attribute_path = req.base_msg.get("attributePath")
        new_value = req.base_msg.get("newValue")
        reply_msg_uuid = "s3i:" + str(uuid.uuid4())

        try:
            __log = "[S3I]: Search for the given attribute path: {}".format(attribute_path)
            APP_LOGGER.info(__log)
            old_value = self._uriToData(attribute_path)
            ins = self._uriToIns(attribute_path)
            APP_LOGGER.info("[S3I]: Change value from {} to {}".format(old_value, new_value))
            result = self._set_value_req(ins, new_value, attribute_path)

        except Exception:
            __log = "[S3I]: Invalid attribute path"
            APP_LOGGER.critical(__log)
            result = False

        set_value_reply.fillSetValueReply(
            sender=self.identifier,
            receivers=[request_sender],
            ok=result,
            replying_to_msg=request_msg_id,
            message_id=reply_msg_uuid
        )
        res = self.broker.send(
            endpoint=request_sender_endpoint,
            msg=set_value_reply.base_msg
        )
        if res:
            APP_LOGGER.info("[S3I]: Sending setValueReply back")
        else:
            APP_LOGGER.error("[S3I]: Sending setValueReply failed")

    def _set_value_req(self, ins, new_value, attribute_path):
        if not isinstance(new_value, dict):
            attr_list = attribute_path.split("/")
            if attr_list.__len__() <= 2:
                APP_LOGGER.info("Not allowed to set attribute {}".format(attribute_path))
                return False
            else:
                if hasattr(ins, attr_list[attr_list.__len__() - 1]):
                    setattr(ins, attr_list[attr_list.__len__() - 1], new_value)
                    return True
                APP_LOGGER.info("{} is not one of the attributes".format(attr_list[attr_list.__len__() - 1]))
                return False
        else:
            for key in new_value.keys():
                if hasattr(ins, key):
                    setattr(ins, key, new_value[key])
                else:
                    APP_LOGGER.info("{} is not one of the attributes".format(key))
                    return False
            return True

    def _uriToIns(self, uri):
        if not uri:
            return None
        uri_list = uri.split("/")
        uri_list.pop(0)  # delete first element "attributes"
        return self._getInstance(self, uri_list)

    def _getInstance(self, source_obj, uri_list):
        if uri_list.__len__() == 0 or uri_list.__len__() == 1:
            ### the original uri was "attributes/features"
            return source_obj

        if "ml40" in uri_list[0]:
            _uri = uri_list[0]
            uri_list.pop(0)
            return self._getInstance(source_obj.features[_uri], uri_list)

        elif uri_list[0] == "features":
            uri_list.pop(0)
            return self._getInstance(source_obj, uri_list)

        elif uri_list[0] == "targets":
            uri_list.pop(0)
            for key in source_obj.targets.keys():
                subthing_dict = source_obj.targets[key].to_subthing_json()
                if subthing_dict.get("name", "") == uri_list[0] or subthing_dict.get("identifier", "") == uri_list[0] \
                        or subthing_dict.get("class", "") == uri_list[0]:
                    uri_list.pop(0)
                    return self._getInstance(source_obj.targets[key], uri_list)

        elif uri_list[0] == "subFeatures":
            uri_list.pop(0)
            for key in source_obj.subFeatures.keys():
                subfeature_dict = source_obj.subFeatures[key].to_json()
                if subfeature_dict.get("name", "") == uri_list[0] or subfeature_dict.get("identifier", "") == uri_list[
                    0] \
                        or subfeature_dict.get("class", "") == uri_list[0]:
                    uri_list.pop(0)
                    return self._getInstance(source_obj.subFeatures[key], uri_list)

    def on_event_subscription_request(self, msg):
        subscription_status, topic = self.event_manager.add_custom_event(
            rql_expression=msg.get("filter"),
            attribute_paths=msg.get("attributePaths")
        )
        __log = "[S3I][Broker]: Validation of RQL syntax: {}".format(subscription_status)
        APP_LOGGER.info(__log)
        event_sub_reply = CustomEventReply()
        event_sub_reply.fillCustomEventReply(
            sender=self.identifier,
            receivers=[msg.get("sender")],
            topic=topic,
            replying_to_msg=msg.get("identifier"),
            message_id="s3i:" + str(uuid.uuid4()),
            status="ok" if subscription_status else "invalid request"
        )
        res = self.broker.send(
            msg.get("replyToEndpoint"),
            msg=event_sub_reply.base_msg
        )
        if res:
            APP_LOGGER.info("[S3I]: Sending customEventReply back")
        else:
            APP_LOGGER.error("[S3I]: Sending customEventReply failed")
