# -*- coding: utf-8 -*-
from plone import api
from Products.Five import BrowserView


class View(BrowserView):
    def get_children(self):
        return [self.wrap_obj(x) for x in self.context.listFolderContents()]

    def wrap_obj(self, item):
        url = item.absolute_url()
        if item.portal_type == "File":
            file_obj = getattr(item, "file", None)
            if file_obj:
                url = "{}/@@download/file/{}".format(
                    url, file_obj.filename.encode("utf-8")
                )
        return {
            "url": url,
            "title": item.Title(),
            "description": item.Description() or item.Title(),
        }

    def can_see_links(self):
        current = api.user.get_current()
        return api.user.has_permission(
            "rer.ufficiostampa: Send", user=current, obj=self.context
        )

    def can_send(self):
        review_state = api.content.get_state(obj=self.context)
        if (
            self.context.portal_type == "ComunicatoStampa"
            and review_state == "published"  # noqa
        ):
            return True
        if self.context.portal_type == "InvitoStampa":
            return True
        return False
