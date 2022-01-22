#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk.utils import constants


class ChatAction(object):
	FIND_LOCATION = constants.CHAT_ACTION_FIND_LOCATION  # type: str
	RECORD_AUDIO = constants.CHAT_ACTION_RECORD_AUDIO  # type: str
	RECORD_VIDEO = constants.CHAT_ACTION_RECORD_VIDEO  # type: str
	RECORD_VIDEO_NOTE = constants.CHAT_ACTION_RECORD_VIDEO_NOTE  # type: str
	RECORD_VOICE = constants.CHAT_ACTION_RECORD_VOICE  # type: str
	TYPING = constants.CHAT_ACTION_TYPING  # type: str
	UPLOAD_AUDIO = constants.CHAT_ACTION_UPLOAD_AUDIO  # type: str
	UPLOAD_DOCUMENT = constants.CHAT_ACTION_UPLOAD_DOCUMENT  # type: str
	UPLOAD_PHOTO = constants.CHAT_ACTION_UPLOAD_PHOTO  # type: str
	UPLOAD_VIDEO = constants.CHAT_ACTION_UPLOAD_VIDEO  # type: str
	UPLOAD_VIDEO_NOTE = constants.CHAT_ACTION_UPLOAD_VIDEO_NOTE  # type: str
	UPLOAD_VOICE = constants.CHAT_ACTION_UPLOAD_VOICE  # type: str
