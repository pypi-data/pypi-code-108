# -*- coding: utf-8 -*-

from plone import api
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest


def post_install(context):
    """Post install demo script"""
    portal = api.portal.get()
    request = getRequest()
    folder1 = api.content.create(
        container=portal,
        type="imio.smartweb.Folder",
        title="Folder 1",
    )
    api.content.transition(folder1, "publish")
    folder2 = api.content.create(
        container=portal,
        type="imio.smartweb.Folder",
        title="Folder 2",
    )
    api.content.transition(folder2, "publish")
    folder3 = api.content.create(
        container=portal,
        type="imio.smartweb.Folder",
        title="Folder 3",
    )
    api.content.transition(folder3, "publish")

    # Inside folder 1
    page1 = api.content.create(
        container=folder1,
        type="imio.smartweb.Page",
        title="Page 1",
    )
    api.content.transition(page1, "publish")
    api.content.create(
        container=page1,
        type="imio.smartweb.SectionText",
        title="My beautiful text section",
    )
    api.content.create(
        container=page1,
        type="imio.smartweb.SectionGallery",
        title="Squirel gallery",
    )

    # Inside folder 2
    page2 = api.content.create(
        container=folder2,
        type="imio.smartweb.Page",
        title="Page 2",
    )
    api.content.transition(page2, "publish")
    page3 = api.content.create(
        container=folder2,
        type="imio.smartweb.Page",
        title="Page 3",
    )
    api.content.transition(page3, "publish")

    # Inside folder 3
    subsite = api.content.create(
        container=folder3,
        type="imio.smartweb.Folder",
        title="Subsite",
    )
    api.content.transition(subsite, "publish")
    subsite_view = getMultiAdapter((subsite, request), name="subsite_settings")
    subsite_view.enable()
    page4 = api.content.create(
        container=subsite,
        type="imio.smartweb.Page",
        title="Page 4",
    )
    api.content.transition(page4, "publish")
    page5 = api.content.create(
        container=subsite,
        type="imio.smartweb.Page",
        title="Page 5",
    )
    api.content.transition(page5, "publish")
