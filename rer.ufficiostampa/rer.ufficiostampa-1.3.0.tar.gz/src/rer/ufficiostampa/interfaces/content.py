# -*- coding: utf-8 -*-
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform import directives
from plone.supermodel import model
from rer.ufficiostampa import _
from rer.ufficiostampa.utils import defaultLegislature
from zope import schema


class IComunicatoStampa(model.Schema):
    arguments = schema.Tuple(
        title=_("arguments_label", default=u"Arguments"),
        description=_("arguments_help", default="Select one or more values."),
        value_type=schema.TextLine(),
        required=True,
        missing_value=(),
    )

    directives.widget(
        "arguments",
        AjaxSelectFieldWidget,
        vocabulary="rer.ufficiostampa.vocabularies.arguments",
        pattern_options={"allowNewItems": "false"},
    )

    legislature = schema.TextLine(
        title=_(u"label_legislature", default=u"Legislature"),
        description=u"",
        required=True,
        defaultFactory=defaultLegislature,
    )
    directives.mode(legislature="display")

    message_sent = schema.Bool(
        title=_(u"label_sent", default=u"Sent"),
        description=u"",
        required=False,
        default=False,
    )
    comunicato_number = schema.TextLine(title=u"", description=u"", required=False)
    directives.omitted("message_sent")
    directives.omitted("comunicato_number")


class IInvitoStampa(IComunicatoStampa):
    """ """
