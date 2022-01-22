#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/


from tgsdk.utils import constants


def test__constants():

	assert constants.PARSE_MODE_HTML == "HTML"
	assert constants.PARSE_MODE_MARKDOWN == "Markdown"
	assert constants.PARSE_MODE_MARKDOWN_V2 == "MarkdownV2"

	assert constants.CHAT_PRIVATE == "private"
	assert constants.CHAT_CHANNEL == "channel"
	assert constants.CHAT_GROUP == "group"
	assert constants.CHAT_SUPERGROUP == "supergroup"

	assert constants.CHAT_ACTION_TYPING == "typing"
	assert constants.CHAT_ACTION_UPLOAD_PHOTO == "upload_photo"
	assert constants.CHAT_ACTION_UPLOAD_VIDEO == "upload_video"
	assert constants.CHAT_ACTION_RECORD_AUDIO == "record_audio"
	assert constants.CHAT_ACTION_RECORD_VIDEO == "record_video"
	assert constants.CHAT_ACTION_UPLOAD_AUDIO == "upload_audio"
	assert constants.CHAT_ACTION_UPLOAD_DOCUMENT == "upload_document"
	assert constants.CHAT_ACTION_UPLOAD_VIDEO_NOTE == "upload_video_note"
	assert constants.CHAT_ACTION_RECORD_VIDEO_NOTE == "record_video_note"
	assert constants.CHAT_ACTION_FIND_LOCATION == "find_location"

	assert constants.CHAT_MEMBER_CREATOR == "creator"
	assert constants.CHAT_MEMBER_ADMINISTRATOR == "administrator"
	assert constants.CHAT_MEMBER_MEMBER == "member"
	assert constants.CHAT_MEMBER_LEFT == "left"
	assert constants.CHAT_MEMBER_KICKED == "kicked"
	assert constants.CHAT_MEMBER_RESTRICTED == "restricted"

	assert constants.MAX_MESSAGE_LENGTH == 4096
	assert constants.MAX_CAPTION_LENGTH == 1024

	assert constants.ALLOWED_TYPE_MESSAGE == "message"
	assert constants.ALLOWED_TYPE_EDITED_MESSAGE == "edited_message"
	assert constants.ALLOWED_TYPE_CHANNEL_POST == "channel_post"
	assert constants.ALLOWED_TYPE_EDITED_CHANNEL_POST == "edited_channel_post"
	assert constants.ALLOWED_TYPE_INLINE_QUERY == "inline_query"
	assert constants.ALLOWED_TYPE_CHOSEN_INLINE_RESULT == "chosen_inline_result"
	assert constants.ALLOWED_TYPE_CALLBACK_QUERY == "callback_query"
	assert constants.ALLOWED_TYPE_SHIPPING_QUERY == "shipping_query"
	assert constants.ALLOWED_TYPE_PRE_CHECKOUT_QUERY == "pre_checkout_query"
	assert constants.ALLOWED_TYPE_POLL == "poll"
	assert constants.ALLOWED_TYPE_POLL_ANSWER == "poll_answer"
