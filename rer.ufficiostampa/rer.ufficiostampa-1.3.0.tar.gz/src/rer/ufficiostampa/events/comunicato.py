# -*- coding: utf-8 -*-
from rer.ufficiostampa.utils import get_next_comunicato_number
from plone import api


def setNumber(item, event):
    if item.portal_type != "ComunicatoStampa":
        return
    if event.action != "publish":
        return
    if getattr(item, "comunicato_number", ""):
        # already set
        return
    setattr(item, "comunicato_number", get_next_comunicato_number())


def setEmptyNumber(item, event):
    """
    Reset it when copy a comunicato
    """
    setattr(item, "comunicato_number", "")
    setattr(item, "message_sent", False)


def fixText(item, event):
    transform_tool = api.portal.get_tool(name="portal_transforms")
    item.title = transform_tool.convert(
        "html_to_web_intelligent_plain_text", item.title
    ).getData()
    item.description = transform_tool.convert(
        "html_to_web_intelligent_plain_text", item.description
    ).getData()
