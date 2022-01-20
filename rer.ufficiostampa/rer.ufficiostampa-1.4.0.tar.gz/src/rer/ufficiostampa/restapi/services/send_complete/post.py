# -*- coding: utf-8 -*-
from datetime import datetime
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from rer.ufficiostampa.interfaces import ISendHistoryStore
from zope.component import getUtility
from zope.interface import alsoProvides

import logging

logger = logging.getLogger(__name__)


class SendCompletePost(Service):
    def reply(self):
        data = json_body(self.request)

        send_uid = data.get("send_uid", None)
        error = data.get("error", False)

        if not send_uid:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="BadRequest", message='Missing "send_uid" parameter'
                )
            )
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        tool = getUtility(ISendHistoryStore)
        try:
            tool = getUtility(ISendHistoryStore)
            res = tool.update(
                id=int(send_uid),
                data={
                    "completed_date": datetime.now(),
                    "status": error and "error" or "success",
                },
            )
        except Exception as e:
            logger.exception(e)
            self.request.response.setStatus(500)
            return dict(
                error=dict(type="InternalServerError", message=e.message)
            )
        if res and "error" in res:
            if res["error"] == "NotFound":
                self.request.response.setStatus(500)
                return dict(
                    error=dict(
                        type="InternalServerError",
                        message='Send history "{uid}" not found in "{title}".'.format(  # noqa
                            uid=send_uid, title=self.context.title
                        ),
                    )
                )
            else:
                self.request.response.setStatus(500)
                return dict(
                    error=dict(
                        type="InternalServerError",
                        message="Unable to update end date. See application log for more details",  # noqa
                    )
                )
        self.request.response.setStatus(204)
        return
