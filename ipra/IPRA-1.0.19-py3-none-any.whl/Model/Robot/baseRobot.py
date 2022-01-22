from abc import abstractmethod
import tkinter as tk
from tkinter import *
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
#from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
from pandas import ExcelWriter
import xlsxwriter
import time
import pandas as pd
from ipra.Logger.logger import Logger


class BaseRobot:
    def __init__(self, policyList, frame, reportPath,inputPath):
        self.policyList = policyList
        self.frame = frame
        self.frame.resetProgress()
        self.isLogin = False
        self.isStopped = False
        self.buildReportQueue = []
        self.buildHeaderQueue = []
        self.buildReportThread = None
        self.reportPath = reportPath
        self.inputPath = inputPath
        self.logger = Logger()

    def SearchByIdValue(self, soup, key):
        result = soup.find_all(id=key)
        result_soup = BeautifulSoup(str(result), 'lxml')
        return result_soup

    def SearchByHtmlTagClassValue(self, soup, tag, class_key):
        result = soup.find_all(tag, attrs={'class': class_key})
        result_soup = BeautifulSoup(str(result), 'lxml')
        return result_soup

    def SearchByHtmlTagValueKey(self, soup, tag, key, value):
        result = soup.find_all(tag, attrs={key: value})
        result_soup = BeautifulSoup(str(result), 'lxml')
        return result_soup

    def DoClickUntilNoException(self,xPath):
        isWaiting = True
        while isWaiting:
            try:
                self.browser.find_element_by_xpath(xPath).click()
                isWaiting = False
            except:
                time.sleep(1)

    def setIsStopped(self, status):
        self.isStopped = status

    def getIsStopped(self):
        return self.isStopped

    def startBrowser(self):
        self.browser = webdriver.Chrome(r"C:\IPRA\chromedriver.exe")

    @abstractmethod
    def waitingLoginComplete(self):
        pass

    @abstractmethod
    def scrapPolicy(self):
        pass

    @abstractmethod
    def buildReport(self):
        pass

    @abstractmethod
    def buildReportOnly(self):
        pass
    
    @abstractmethod
    def buildReportHeaderFullFlow(self):
        pass
    
    @abstractmethod
    def buildReportHeaderHalfFlow(self):
        pass

    def execReport(self):
        self.buildReportOnly()
        
    def execRobot(self):
        self.startBrowser()
        self.waitingLoginComplete()
        self.buildReport()
        self.scrapPolicy()
        self.buildReportThread.join()
        self.browser.close()
