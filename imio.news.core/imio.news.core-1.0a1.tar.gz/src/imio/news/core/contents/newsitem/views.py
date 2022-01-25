# -*- coding: utf-8 -*-

from embeddify import Embedder
from imio.smartweb.common.utils import translate_vocabulary_term
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.contenttypes.browser.folder import FolderView
from Products.CMFPlone.resources import add_bundle_on_request


class View(FolderView):
    def __call__(self):
        images = self.context.listFolderContents(contentFilter={"portal_type": "Image"})
        if len(images) > 0:
            add_bundle_on_request(self.request, "spotlightjs")
            add_bundle_on_request(self.request, "flexbin")
        return self.index()

    def files(self):
        return self.context.listFolderContents(contentFilter={"portal_type": "File"})

    def images(self):
        return self.context.listFolderContents(contentFilter={"portal_type": "Image"})

    def has_leadimage(self):
        if ILeadImage.providedBy(self.context) and getattr(
            self.context, "image", False
        ):
            return True
        return False

    def get_embed_video(self):
        embedder = Embedder(width=800, height=600)
        return embedder(self.context.video_url, params=dict(autoplay=False))

    def category(self):
        title = translate_vocabulary_term(
            "imio.news.vocabulary.NewsCategories", self.context.category
        )
        if title:
            return title

    def topics(self):
        topics = self.context.topics
        if topics is None:
            return
        items = []
        for item in topics:
            title = translate_vocabulary_term("imio.smartweb.vocabulary.Topics", item)
            items.append(title)
        return ", ".join(items)

    def iam(self):
        iam = self.context.iam
        if iam is None:
            return
        items = []
        for item in iam:
            title = translate_vocabulary_term("imio.smartweb.vocabulary.IAm", item)
            items.append(title)
        return ", ".join(items)

    def effective_date(self):
        if self.context.EffectiveDate() == "None":
            return
        return self.context.effective().strftime("%d/%m/%Y")

    def expiration_date(self):
        if self.context.ExpirationDate() == "None":
            return
        return self.context.expires().strftime("%d/%m/%Y")
