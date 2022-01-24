# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from cpskin.core.testing import CPSKIN_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.namedfile.file import NamedBlobImage
from zope.component import queryMultiAdapter
from zope.viewlet.interfaces import IViewletManager

import os
import unittest


def dummy_content(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    return NamedBlobImage(
        data=open(file_path, 'r').read(),
        filename=file_path
    )


class TestBanners(unittest.TestCase):
    layer = CPSKIN_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        manager_name = 'plone.portaltop'
        view = BrowserView(self.portal, self.request)
        manager = queryMultiAdapter(
            (self.portal, self.request, view),
            IViewletManager,
            manager_name,
            default=None)
        manager.update()
        self.my_viewlet = [v for v in manager.viewlets
                           if v.__name__ == 'cpskin.banner'][0]

    def test_banner_without_folder(self):
        banner = self.my_viewlet.getBanner()
        url = banner.get('url')
        self.assertTrue(url.startswith('http://nohost/plone/banner.jpg'))
        self.assertEqual(banner.get('type'), 'image')

    def test_banner_with_folder_without_image(self):
        api.content.create(
            container=self.portal, type='Folder', id='banner')
        banner = self.my_viewlet.getBanner()
        url = banner.get('url')
        self.assertTrue(url.startswith('http://nohost/plone/banner.jpg'))
        self.assertEqual(banner.get('type'), 'image')

    def test_banner_with_folder_with_image(self):
        folder = api.content.create(
            container=self.portal, type='Folder', id='banner')
        image = api.content.create(
            container=folder, type='Image', id='img1.png')
        image.image = dummy_content(u'banner.png')
        banner = self.my_viewlet.getBanner()
        url = banner.get('url')
        self.assertTrue(url.startswith('http://nohost/plone/banner/img1.png'))
        self.assertEqual(banner.get('type'), 'image')
    
    def test_banner_with_folder_with_one_video(self):
        folder = api.content.create(
            container=self.portal, type='Folder', id='banner')
        image = api.content.create(
            container=folder, type='Image', id='img1.png')
        image.image = dummy_content(u'banner.png')
        video = api.content.create(
            container=folder, type='File', id='banner.mp4')
        video.file = dummy_content(u'banner.mp4')
        banner = self.my_viewlet.getBanner()
        url = banner.get('url')
        self.assertTrue(url.startswith('http://nohost/plone/banner/img1.png'))
        self.assertEqual(banner.get('type'), 'image')


    def test_banner_with_folder_with_two_video(self):
        folder = api.content.create(
            container=self.portal, type='Folder', id='banner')
        image = api.content.create(
            container=folder, type='Image', id='img1.png')
        image.image = dummy_content(u'banner.png')
        video = api.content.create(
            container=folder, type='File', id='banner.mp4')
        video.file = dummy_content(u'banner.mp4')
        video = api.content.create(
            container=folder, type='File', id='banner.webm')
        video.file = dummy_content(u'banner.webm')
        banner = self.my_viewlet.getBanner()
        url = banner.get('url')
        url_webm = banner.get('url_webm')
        self.assertTrue(url.startswith('http://nohost/plone/banner/banner.mp4'))
        self.assertTrue(url_webm.startswith('http://nohost/plone/banner/banner.webm'))
        self.assertEqual(banner.get('type'), 'video')
