#!/usr/bin/env python
#coding=utf8
import sys, os, socket
import time, threading
import collections
import simplejson as json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from lxml import html, etree

class Webpage(object):
    '''
    A base class for common linux devices.
    '''
    version = '0.10'

    def __init__(self, server = None, type = "chrome", **kwargs):
        """
        This is the constructor for Web
        [References]:
            [1] Selenium with Python, http://selenium-python.readthedocs.io/
            [2] 快速入门, http://selenium-python-zh.readthedocs.io/en/latest/getting-started.html
            [3] Python爬虫利器三之Xpath语法与lxml库的用法, https://cuiqingcai.com/2621.html
        """

        self.start_time = time.time()
        self.attributes = collections.OrderedDict()

        if type == "chrome":

            options = webdriver.ChromeOptions()
            prefs = {
                    "profile.managed_default_content_settings.images": 2,
                    "profile.managed_default_content_settings.plugins": 2,
                    }
            options.add_experimental_option("prefs", prefs)
            #options.add_argument('--headless')
            #options.add_argument('--ignore-certificate-errors')
            self.driver = webdriver.Chrome(chrome_options = options)

        if server:
            self.driver.get(server)
            print("current url: %s" %(self.driver.current_url))
            print("title: %s" %(self.driver.title))
            print("name: %s" %(self.driver.name))
        #driver = webdriver.Firefox()

    def __del__(self):
        '''
        Recycle resource when the object is destroied.
        '''
        self.driver.close()

    def get (self, server):
        '''
        Html get
        '''
        self.driver.get(server)
        print "current url: ", self.driver.current_url
        print "title: ", self.driver.title
        print "name", self.driver.name

    def element (self, timeout = 5, **kwargs):
        '''
        Wait for at most timeout or until get the element.
        '''
        t = max(int(timeout / 0.5), 1)
        for i in range(t):
            try:
                if "id" in kwargs.keys():
                    elem = self.driver.find_element_by_id(kwargs["id"])
                elif "name" in kwargs.keys():
                    print "name: ", kwargs["name"]
                    elem = self.driver.find_element_by_name(kwargs["name"])
                elif "xpath" in kwargs.keys():
                    elem = self.driver.find_element_by_xpath(kwargs["xpath"])
                elif "text" in kwargs.keys():
                    elem = self.driver.find_element_by_link_text(kwargs["text"])
                elif "partial_text" in kwargs.keys():
                    elem = self.driver.find_element_by_partial_link_text(kwargs["partial_text"])
                elif "tag" in kwargs.keys():
                    elem = self.driver.find_element_by_tag_name(kwargs["tag"])
                elif "class" in kwargs.keys():
                    elem = self.driver.find_element_by_class_name(kwargs["class"])
                elif "css" in kwargs.keys():
                    elem = self.driver.find_element_by_css_selector(kwargs["css"])
                else:
                    print 'not supported search attributes'
                    #raise Exception ('not supported search attributes')
                    return None
            except Exception as e:
                time.sleep(0.5)
                #print e
            else:
                #print "elem text: ", elem.text
                return elem

        return None

    def input (self, text, **kwargs):
        '''
        Find the element and enter the text and send ENTER.
        '''

        #print self.driver.page_source
        elem = self.element(**kwargs)
        if elem:
            elem.send_keys(text)
            elem.send_keys(Keys.RETURN)
            return True
        else:
            return False

    def click (self, **kwargs):
        '''
        Find the element and click the button.
        '''
        elem = self.element(**kwargs)
        if elem:
            elem.click()
            return True
        else:
            return False

    def alert (self, action = "accept", username = None, password = None,
            keys = None):
        '''
        Find the element and click the button.
        '''

        try:
            alert = self.driver.switch_to_alert()
            print "alert: ", alert.text
            print "action: ", action
        except Exception as e:
            print e
            return False
        else:
            if username and password:
                alert.authenticate(username, password)

            if keys:
                alert.send_keys(keys)

            if action == "accept":
                alert.accept()
            else:
                alert.dismiss()

            return True

    def string (self, xpath = None):
        '''
        Return the source code of the web page.
        '''
        if xpath:
            html = etree.HTML(self.driver.page_source)
            tmp = html.xpath(xpath)
            src = etree.tostring(tmp[0]).decode('utf-8')
        else:
            src = self.driver.page_source
        return src

    def elements (self, timeout = 5, **kwargs):
        '''
        Wait for at most timeout or until get the elements.
        '''
        t = max(int(timeout / 0.5), 1)
        for i in range(t):
            try:
                if "id" in kwargs.keys():
                    elem = self.driver.find_elements_by_id(kwargs["id"])
                elif "name" in kwargs.keys():
                    elem = self.driver.find_elements_by_name(kwargs["name"])
                elif "xpath" in kwargs.keys():
                    elem = self.driver.find_elements_by_xpath(kwargs["xpath"])
                elif "text" in kwargs.keys():
                    elem = self.driver.find_elements_by_link_text(kwargs["text"])
                elif "partial_text" in kwargs.keys():
                    elem = self.driver.find_elements_by_partial_link_text(kwargs["partial_text"])
                elif "tag" in kwargs.keys():
                    elem = self.driver.find_elements_by_tag_name(kwargs["tag"])
                elif "classname" in kwargs.keys():
                    elem = self.driver.find_elements_by_class_name(kwargs["classname"])
                elif "css" in kwargs.keys():
                    elem = self.driver.find_elements_by_css_selector(kwargs["css"])
                else:
                    print 'not supported search attributes'
                    #raise Exception ('not supported search attributes')
                    return []
            except Exception as e:
                time.sleep(0.5)
            else:
                return elem

        return None


    def strings (self, xpath = None):
        '''
        Return the source code of the web page.
        '''
        if xpath:
            html = etree.HTML(self.driver.page_source)
            tmp = html.xpath(xpath)
            src = map(etree.tostring, tmp)
            #src = map(str.decode('utf-8'), tmp)
        else:
            src = [self.driver.page_source]

        return src

    def src (self, xpath = None):
        '''
        Return the source code of the web page.
        '''
        if xpath:
            html = etree.HTML(web.driver.page_source)
            tmp = html.xpath(xpath)
            src = etree.tostring(tmp)[0]
        else:
            src = self.driver.page_source

        return src

    def page_source (self):
        '''
        Find the element and get the source
        '''
        return self.driver.page_source

if __name__ == '__main__':
    web = Webpage("https://pypi.python.org/pypi")
    web.input("netdevice", name = "term")
    table = web.string(xpath = '//table[@class="list"]')
    print table
    #df = pd.read_html(table, header=0)[0]
    #print df.ix[0, "Description"]
