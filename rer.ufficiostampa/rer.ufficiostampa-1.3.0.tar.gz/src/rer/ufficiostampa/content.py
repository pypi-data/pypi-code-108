# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from rer.ufficiostampa.interfaces import IComunicatoStampa
from rer.ufficiostampa.interfaces import IInvitoStampa
from zope.interface import implementer


@implementer(IComunicatoStampa)
class ComunicatoStampa(Container):

    """
    """


@implementer(IInvitoStampa)
class InvitoStampa(Container):

    """
    """
