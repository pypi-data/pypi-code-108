# -*- coding: utf-8 -*-
from rer.agidtheme.base.viewlets.social import SocialTagsViewlet as BaseViewlet
from plone.memoize.view import memoize


class SocialTagsViewlet(BaseViewlet):
    @memoize
    def _get_tags(self):
        """
        Add a static description when we are in comunicati-search
        """
        tags = super(SocialTagsViewlet, self)._get_tags()
        if "comunicati-search" not in self.request.steps:
            return tags
        for tag in tags:
            content = tag.get("content", "")
            itemprop = tag.get("itemprop", "")
            property = tag.get("property", "")
            if (
                itemprop == "description" or property == "og:description"
            ) and not content:  # noqa
                tag[
                    "content"
                ] = "Ricerca comunicati stampa della Regione Emilia-Romagna"
        return tags
