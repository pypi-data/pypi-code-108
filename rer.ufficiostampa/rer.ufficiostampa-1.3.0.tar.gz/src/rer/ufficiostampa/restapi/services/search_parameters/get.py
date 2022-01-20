# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service
from rer.ufficiostampa import _
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IVocabularyFactory


def getVocabularyTermsForForm(vocab_name, context):
    """
    Return the values of vocabulary
    """
    utility = getUtility(IVocabularyFactory, vocab_name)

    values = []

    vocab = utility(context)

    for entry in vocab:
        if entry.title != u"select_label":
            values.append({"value": entry.value, "label": entry.title})
    return values


def getTypesValues():
    res = [
        {"value": "ComunicatoStampa", "label": "Comunicato Stampa"},
        {"value": "InvitoStampa", "label": "Invito Stampa"},
    ]
    return res


def getTypesDefault():
    res = ["ComunicatoStampa"]
    if not api.user.is_anonymous():
        res.append("InvitoStampa")
    return res


def getSearchFields():
    request = getRequest()
    portal = api.portal.get()

    return [
        {
            "id": "SearchableText",
            "label": translate(
                _("comunicati_search_text_label", default=u"Search text"),
                context=request,
            ),
            "help": "",
            "type": "text",
        },
        {
            "id": "portal_type",
            "label": translate(
                _("label_portal_type", default="Type"), context=request,
            ),
            "help": "",
            "type": "checkbox",
            "options": getTypesValues(),
            "default": getTypesDefault(),
            "hidden": api.user.is_anonymous(),
        },
        {
            "id": "created",
            "label": translate(
                _("comunicati_search_created_label", default=u"Date"),
                context=request,
            ),
            "help": "",
            "type": "date",
        },
        {
            "id": "legislature",
            "label": translate(
                _("label_legislature", default="Legislature"), context=request,
            ),
            "help": "",
            "type": "select",
            "multivalued": True,
            "options": getVocabularyTermsForForm(
                context=portal,
                vocab_name="rer.ufficiostampa.vocabularies.legislatures",
            ),
        },
        {
            "id": "arguments",
            "label": translate(
                _("legislature_arguments_label", default="Arguments"),
                context=request,
            ),
            "help": "",
            "type": "select",
            "multivalued": True,
            "options": getVocabularyTermsForForm(
                context=portal,
                vocab_name="rer.ufficiostampa.vocabularies.all_arguments",
            ),
        },
    ]


@implementer(IPublishTraverse)
class SearchParametersGet(Service):
    def __init__(self, context, request):
        super(SearchParametersGet, self).__init__(context, request)

    def reply(self):
        return getSearchFields()
