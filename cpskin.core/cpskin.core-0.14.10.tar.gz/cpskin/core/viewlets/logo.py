# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets.common import LogoViewlet
from zExceptions import NotFound


class CPSkinLogoViewlet(LogoViewlet):

    def update(self):
        super(CPSkinLogoViewlet, self).update()
        logoName = 'cpskinlogo.png'
        logoTitle = self.portal_state.portal_title()
        try:
            logo_custom = self.context.restrictedTraverse(logoName)
        except (AttributeError, KeyError, NotFound):
            # If no custom logo found, super() will handle default one
            pass
        else:
            try:
                self.logo_tag = logo_custom.tag(title=logoTitle, alt=logoTitle)
            except:
                scales = api.content.get_view(
                    name='images',
                    context=logo_custom,
                    request=self.request)
                self.logo_tag = scales.tag(title=logoTitle, alt=logoTitle)
