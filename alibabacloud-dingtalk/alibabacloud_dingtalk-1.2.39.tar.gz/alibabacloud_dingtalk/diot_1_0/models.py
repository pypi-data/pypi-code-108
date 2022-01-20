# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from Tea.model import TeaModel
from typing import Dict, List, Any


class BatchDeleteDeviceHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class BatchDeleteDeviceRequest(TeaModel):
    def __init__(
        self,
        corp_id: str = None,
        device_ids: List[str] = None,
    ):
        # 钉钉物联组织ID, 第三方平台必填，企业内部系统忽略。
        self.corp_id = corp_id
        # 设备ID列表，最多500条。
        self.device_ids = device_ids

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.corp_id is not None:
            result['corpId'] = self.corp_id
        if self.device_ids is not None:
            result['deviceIds'] = self.device_ids
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('corpId') is not None:
            self.corp_id = m.get('corpId')
        if m.get('deviceIds') is not None:
            self.device_ids = m.get('deviceIds')
        return self


class BatchDeleteDeviceResponseBody(TeaModel):
    def __init__(
        self,
        device_ids: List[str] = None,
    ):
        # 成功删除设备ID列表。
        self.device_ids = device_ids

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.device_ids is not None:
            result['deviceIds'] = self.device_ids
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('deviceIds') is not None:
            self.device_ids = m.get('deviceIds')
        return self


class BatchDeleteDeviceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: BatchDeleteDeviceResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = BatchDeleteDeviceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class PushEventHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class PushEventRequest(TeaModel):
    def __init__(
        self,
        corp_id: str = None,
        event_id: str = None,
        event_type: str = None,
        event_name: str = None,
        occurrence_time: int = None,
        device_id: str = None,
        location: str = None,
        msg: str = None,
        pic_urls: List[str] = None,
        extra_data: Dict[str, Any] = None,
    ):
        # 钉钉物联组织ID, 第三方平台必填，企业内部系统忽略。
        self.corp_id = corp_id
        # 事件ID。
        self.event_id = event_id
        # 事件类型，最长20个字符。
        self.event_type = event_type
        # 事件名称，长度4-20个字符，一个中文汉字算2个字符。
        self.event_name = event_name
        # 事件发生事件，Unix时间戳，单位毫秒。
        self.occurrence_time = occurrence_time
        # 触发事件设备ID。
        self.device_id = device_id
        # 事件发生地点。
        self.location = location
        # 事件文字信息。
        self.msg = msg
        # 事件图片地址列表。
        self.pic_urls = pic_urls
        # 第三方平台定制参数，企业内部系统忽略。
        self.extra_data = extra_data

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.corp_id is not None:
            result['corpId'] = self.corp_id
        if self.event_id is not None:
            result['eventId'] = self.event_id
        if self.event_type is not None:
            result['eventType'] = self.event_type
        if self.event_name is not None:
            result['eventName'] = self.event_name
        if self.occurrence_time is not None:
            result['occurrenceTime'] = self.occurrence_time
        if self.device_id is not None:
            result['deviceId'] = self.device_id
        if self.location is not None:
            result['location'] = self.location
        if self.msg is not None:
            result['msg'] = self.msg
        if self.pic_urls is not None:
            result['picUrls'] = self.pic_urls
        if self.extra_data is not None:
            result['extraData'] = self.extra_data
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('corpId') is not None:
            self.corp_id = m.get('corpId')
        if m.get('eventId') is not None:
            self.event_id = m.get('eventId')
        if m.get('eventType') is not None:
            self.event_type = m.get('eventType')
        if m.get('eventName') is not None:
            self.event_name = m.get('eventName')
        if m.get('occurrenceTime') is not None:
            self.occurrence_time = m.get('occurrenceTime')
        if m.get('deviceId') is not None:
            self.device_id = m.get('deviceId')
        if m.get('location') is not None:
            self.location = m.get('location')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('picUrls') is not None:
            self.pic_urls = m.get('picUrls')
        if m.get('extraData') is not None:
            self.extra_data = m.get('extraData')
        return self


class PushEventResponseBody(TeaModel):
    def __init__(
        self,
        event_id: str = None,
    ):
        # 事件ID。
        self.event_id = event_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.event_id is not None:
            result['eventId'] = self.event_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('eventId') is not None:
            self.event_id = m.get('eventId')
        return self


class PushEventResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: PushEventResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = PushEventResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeviceConferenceHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class DeviceConferenceRequest(TeaModel):
    def __init__(
        self,
        conf_title: str = None,
        conference_id: str = None,
        conference_password: str = None,
        device_ids: List[str] = None,
    ):
        # 会议主题，最多不能超20个中文。
        self.conf_title = conf_title
        # 钉钉会议ID，加入已存在的会议必填。
        self.conference_id = conference_id
        # 钉钉会议密码，加入已存在的会议必填。
        self.conference_password = conference_password
        # 需要邀请的设备ID，最多5个。
        self.device_ids = device_ids

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.conf_title is not None:
            result['confTitle'] = self.conf_title
        if self.conference_id is not None:
            result['conferenceId'] = self.conference_id
        if self.conference_password is not None:
            result['conferencePassword'] = self.conference_password
        if self.device_ids is not None:
            result['deviceIds'] = self.device_ids
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('confTitle') is not None:
            self.conf_title = m.get('confTitle')
        if m.get('conferenceId') is not None:
            self.conference_id = m.get('conferenceId')
        if m.get('conferencePassword') is not None:
            self.conference_password = m.get('conferencePassword')
        if m.get('deviceIds') is not None:
            self.device_ids = m.get('deviceIds')
        return self


class DeviceConferenceResponseBody(TeaModel):
    def __init__(
        self,
        conference_id: str = None,
    ):
        # 会议ID
        self.conference_id = conference_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.conference_id is not None:
            result['conferenceId'] = self.conference_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('conferenceId') is not None:
            self.conference_id = m.get('conferenceId')
        return self


class DeviceConferenceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: DeviceConferenceResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = DeviceConferenceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class RegisterDeviceHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class RegisterDeviceRequest(TeaModel):
    def __init__(
        self,
        corp_id: str = None,
        id: str = None,
        device_name: str = None,
        nick_name: str = None,
        location: str = None,
        device_status: int = None,
        device_type: str = None,
        device_type_name: str = None,
        parent_id: str = None,
        product_type: str = None,
        live_url: str = None,
    ):
        # 钉钉组织id
        self.corp_id = corp_id
        # 设备id
        self.id = id
        # 设备名称
        self.device_name = device_name
        # 设备昵称
        self.nick_name = nick_name
        # 设备地址
        self.location = location
        # 设备状态 0:在线 1:离线
        self.device_status = device_status
        # 设备类型
        self.device_type = device_type
        # 设备类型名称
        self.device_type_name = device_type_name
        # 设备父节点id
        self.parent_id = parent_id
        # 设备类型 摄像头:CAMERA 其它:OTHERS
        self.product_type = product_type
        # 视频流地址
        self.live_url = live_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.corp_id is not None:
            result['corpId'] = self.corp_id
        if self.id is not None:
            result['id'] = self.id
        if self.device_name is not None:
            result['deviceName'] = self.device_name
        if self.nick_name is not None:
            result['nickName'] = self.nick_name
        if self.location is not None:
            result['location'] = self.location
        if self.device_status is not None:
            result['deviceStatus'] = self.device_status
        if self.device_type is not None:
            result['deviceType'] = self.device_type
        if self.device_type_name is not None:
            result['deviceTypeName'] = self.device_type_name
        if self.parent_id is not None:
            result['parentId'] = self.parent_id
        if self.product_type is not None:
            result['productType'] = self.product_type
        if self.live_url is not None:
            result['liveUrl'] = self.live_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('corpId') is not None:
            self.corp_id = m.get('corpId')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('deviceName') is not None:
            self.device_name = m.get('deviceName')
        if m.get('nickName') is not None:
            self.nick_name = m.get('nickName')
        if m.get('location') is not None:
            self.location = m.get('location')
        if m.get('deviceStatus') is not None:
            self.device_status = m.get('deviceStatus')
        if m.get('deviceType') is not None:
            self.device_type = m.get('deviceType')
        if m.get('deviceTypeName') is not None:
            self.device_type_name = m.get('deviceTypeName')
        if m.get('parentId') is not None:
            self.parent_id = m.get('parentId')
        if m.get('productType') is not None:
            self.product_type = m.get('productType')
        if m.get('liveUrl') is not None:
            self.live_url = m.get('liveUrl')
        return self


class RegisterDeviceResponseBody(TeaModel):
    def __init__(
        self,
        device_id: str = None,
    ):
        # 设备id
        self.device_id = device_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.device_id is not None:
            result['deviceId'] = self.device_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('deviceId') is not None:
            self.device_id = m.get('deviceId')
        return self


class RegisterDeviceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: RegisterDeviceResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = RegisterDeviceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class BatchRegisterDeviceHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class BatchRegisterDeviceRequestDevices(TeaModel):
    def __init__(
        self,
        device_id: str = None,
        device_name: str = None,
        device_status: int = None,
        device_type: str = None,
        device_type_name: str = None,
        product_type: str = None,
        live_url: str = None,
        parent_id: str = None,
        location: str = None,
        extra_data: Dict[str, Any] = None,
    ):
        # 设备ID。
        self.device_id = device_id
        # 设备名称。
        self.device_name = device_name
        # 设备状态  0:在线  1:离线
        self.device_status = device_status
        # 设备类型，自定义传入，最多128个字节。
        self.device_type = device_type
        # 设备类型名称，自定义传入，最多128个字节，与deviceType一一对应。
        self.device_type_name = device_type_name
        # 产品类型 CAMERA：摄像头，可看直播 OTHERS：非摄像头
        self.product_type = product_type
        # 视频流地址直播流地址，支持rtmp、flv、hls等格式，需要https协议。
        self.live_url = live_url
        # 父设备ID。
        self.parent_id = parent_id
        # 设备地址。
        self.location = location
        # 第三方平台定制参数，企业内部系统忽略。
        self.extra_data = extra_data

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.device_id is not None:
            result['deviceId'] = self.device_id
        if self.device_name is not None:
            result['deviceName'] = self.device_name
        if self.device_status is not None:
            result['deviceStatus'] = self.device_status
        if self.device_type is not None:
            result['deviceType'] = self.device_type
        if self.device_type_name is not None:
            result['deviceTypeName'] = self.device_type_name
        if self.product_type is not None:
            result['productType'] = self.product_type
        if self.live_url is not None:
            result['liveUrl'] = self.live_url
        if self.parent_id is not None:
            result['parentId'] = self.parent_id
        if self.location is not None:
            result['location'] = self.location
        if self.extra_data is not None:
            result['extraData'] = self.extra_data
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('deviceId') is not None:
            self.device_id = m.get('deviceId')
        if m.get('deviceName') is not None:
            self.device_name = m.get('deviceName')
        if m.get('deviceStatus') is not None:
            self.device_status = m.get('deviceStatus')
        if m.get('deviceType') is not None:
            self.device_type = m.get('deviceType')
        if m.get('deviceTypeName') is not None:
            self.device_type_name = m.get('deviceTypeName')
        if m.get('productType') is not None:
            self.product_type = m.get('productType')
        if m.get('liveUrl') is not None:
            self.live_url = m.get('liveUrl')
        if m.get('parentId') is not None:
            self.parent_id = m.get('parentId')
        if m.get('location') is not None:
            self.location = m.get('location')
        if m.get('extraData') is not None:
            self.extra_data = m.get('extraData')
        return self


class BatchRegisterDeviceRequest(TeaModel):
    def __init__(
        self,
        corp_id: str = None,
        devices: List[BatchRegisterDeviceRequestDevices] = None,
    ):
        # 钉钉物联组织ID, 第三方平台必填，企业内部系统忽略。
        self.corp_id = corp_id
        # 设备列表。
        self.devices = devices

    def validate(self):
        if self.devices:
            for k in self.devices:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.corp_id is not None:
            result['corpId'] = self.corp_id
        result['devices'] = []
        if self.devices is not None:
            for k in self.devices:
                result['devices'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('corpId') is not None:
            self.corp_id = m.get('corpId')
        self.devices = []
        if m.get('devices') is not None:
            for k in m.get('devices'):
                temp_model = BatchRegisterDeviceRequestDevices()
                self.devices.append(temp_model.from_map(k))
        return self


class BatchRegisterDeviceResponseBody(TeaModel):
    def __init__(
        self,
        device_ids: List[str] = None,
    ):
        # 注册成功的设备ID列表。
        self.device_ids = device_ids

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.device_ids is not None:
            result['deviceIds'] = self.device_ids
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('deviceIds') is not None:
            self.device_ids = m.get('deviceIds')
        return self


class BatchRegisterDeviceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: BatchRegisterDeviceResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = BatchRegisterDeviceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class BatchRegisterEventTypeHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class BatchRegisterEventTypeRequestEventTypes(TeaModel):
    def __init__(
        self,
        event_type: str = None,
        event_type_name: str = None,
    ):
        # 事件类型(唯一)，最长20个字符。
        self.event_type = event_type
        # 事件类型名称，长度4-20个字符，一个中文汉字算2个字符。
        self.event_type_name = event_type_name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.event_type is not None:
            result['eventType'] = self.event_type
        if self.event_type_name is not None:
            result['eventTypeName'] = self.event_type_name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('eventType') is not None:
            self.event_type = m.get('eventType')
        if m.get('eventTypeName') is not None:
            self.event_type_name = m.get('eventTypeName')
        return self


class BatchRegisterEventTypeRequest(TeaModel):
    def __init__(
        self,
        corp_id: str = None,
        event_types: List[BatchRegisterEventTypeRequestEventTypes] = None,
    ):
        # 钉钉物联组织ID, 第三方平台必填，企业内部系统忽略。
        self.corp_id = corp_id
        # 事件类型列表，最多支持添加500个。
        self.event_types = event_types

    def validate(self):
        if self.event_types:
            for k in self.event_types:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.corp_id is not None:
            result['corpId'] = self.corp_id
        result['eventTypes'] = []
        if self.event_types is not None:
            for k in self.event_types:
                result['eventTypes'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('corpId') is not None:
            self.corp_id = m.get('corpId')
        self.event_types = []
        if m.get('eventTypes') is not None:
            for k in m.get('eventTypes'):
                temp_model = BatchRegisterEventTypeRequestEventTypes()
                self.event_types.append(temp_model.from_map(k))
        return self


class BatchRegisterEventTypeResponseBody(TeaModel):
    def __init__(
        self,
        event_types: List[str] = None,
    ):
        # 注册成功的事件类型列表。
        self.event_types = event_types

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.event_types is not None:
            result['eventTypes'] = self.event_types
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('eventTypes') is not None:
            self.event_types = m.get('eventTypes')
        return self


class BatchRegisterEventTypeResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: BatchRegisterEventTypeResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = BatchRegisterEventTypeResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class BatchUpdateDeviceHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class BatchUpdateDeviceRequestDevices(TeaModel):
    def __init__(
        self,
        device_id: str = None,
        device_name: str = None,
        location: str = None,
        device_status: int = None,
        live_url: str = None,
        extra_data: Dict[str, Any] = None,
    ):
        # 设备ID。
        self.device_id = device_id
        # 设备名称。
        self.device_name = device_name
        # 设备地址。
        self.location = location
        # 设备状态 0:在线 1:离线
        self.device_status = device_status
        # 视频流地址直播流地址，支持rtmp、flv、hls等格式，需要https协议。
        self.live_url = live_url
        # 第三方平台定制参数，企业内部系统忽略。
        self.extra_data = extra_data

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.device_id is not None:
            result['deviceId'] = self.device_id
        if self.device_name is not None:
            result['deviceName'] = self.device_name
        if self.location is not None:
            result['location'] = self.location
        if self.device_status is not None:
            result['deviceStatus'] = self.device_status
        if self.live_url is not None:
            result['liveUrl'] = self.live_url
        if self.extra_data is not None:
            result['extraData'] = self.extra_data
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('deviceId') is not None:
            self.device_id = m.get('deviceId')
        if m.get('deviceName') is not None:
            self.device_name = m.get('deviceName')
        if m.get('location') is not None:
            self.location = m.get('location')
        if m.get('deviceStatus') is not None:
            self.device_status = m.get('deviceStatus')
        if m.get('liveUrl') is not None:
            self.live_url = m.get('liveUrl')
        if m.get('extraData') is not None:
            self.extra_data = m.get('extraData')
        return self


class BatchUpdateDeviceRequest(TeaModel):
    def __init__(
        self,
        corp_id: str = None,
        devices: List[BatchUpdateDeviceRequestDevices] = None,
    ):
        # 钉钉物联组织ID, 第三方平台必填，企业内部系统忽略。
        self.corp_id = corp_id
        # 设备列表。
        self.devices = devices

    def validate(self):
        if self.devices:
            for k in self.devices:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.corp_id is not None:
            result['corpId'] = self.corp_id
        result['devices'] = []
        if self.devices is not None:
            for k in self.devices:
                result['devices'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('corpId') is not None:
            self.corp_id = m.get('corpId')
        self.devices = []
        if m.get('devices') is not None:
            for k in m.get('devices'):
                temp_model = BatchUpdateDeviceRequestDevices()
                self.devices.append(temp_model.from_map(k))
        return self


class BatchUpdateDeviceResponseBody(TeaModel):
    def __init__(
        self,
        device_ids: List[str] = None,
    ):
        # 修改成功的设备ID列表。
        self.device_ids = device_ids

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.device_ids is not None:
            result['deviceIds'] = self.device_ids
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('deviceIds') is not None:
            self.device_ids = m.get('deviceIds')
        return self


class BatchUpdateDeviceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: BatchUpdateDeviceResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = BatchUpdateDeviceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class BindSystemHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class BindSystemRequest(TeaModel):
    def __init__(
        self,
        corp_id: str = None,
        auth_code: str = None,
        client_id: str = None,
        client_name: str = None,
        extra_data: Dict[str, Any] = None,
    ):
        # 三方平台的用户的钉钉物联组织ID。
        self.corp_id = corp_id
        # 与三方平台绑定验证的临时授权码。
        self.auth_code = auth_code
        # 三方平台的用户ID。
        self.client_id = client_id
        # 三方平台的用户名。
        self.client_name = client_name
        # 三方平台协定的其它参数。
        self.extra_data = extra_data

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.corp_id is not None:
            result['corpId'] = self.corp_id
        if self.auth_code is not None:
            result['authCode'] = self.auth_code
        if self.client_id is not None:
            result['clientId'] = self.client_id
        if self.client_name is not None:
            result['clientName'] = self.client_name
        if self.extra_data is not None:
            result['extraData'] = self.extra_data
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('corpId') is not None:
            self.corp_id = m.get('corpId')
        if m.get('authCode') is not None:
            self.auth_code = m.get('authCode')
        if m.get('clientId') is not None:
            self.client_id = m.get('clientId')
        if m.get('clientName') is not None:
            self.client_name = m.get('clientName')
        if m.get('extraData') is not None:
            self.extra_data = m.get('extraData')
        return self


class BindSystemResponseBody(TeaModel):
    def __init__(
        self,
        corp_id: str = None,
        client_id: str = None,
    ):
        # 钉钉物联组织ID。
        self.corp_id = corp_id
        # 三方平台的用户ID。
        self.client_id = client_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.corp_id is not None:
            result['corpId'] = self.corp_id
        if self.client_id is not None:
            result['clientId'] = self.client_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('corpId') is not None:
            self.corp_id = m.get('corpId')
        if m.get('clientId') is not None:
            self.client_id = m.get('clientId')
        return self


class BindSystemResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: BindSystemResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = BindSystemResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


