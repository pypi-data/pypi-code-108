from os import write
import time
from bs4 import BeautifulSoup
import xlsxwriter
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from ipra.Model.Robot.baseRobot import BaseRobot
import threading

class SunLifeRobot(BaseRobot):
    def __init__(self, policyList, frame, reportPath, inputPath):
        super().__init__(policyList, frame, reportPath, inputPath)
        self.logger.writeLogString('SUNLIFE-INIT','ROBOT INIT')
        self.maxPolicyListSize = len(policyList)
        self.workbook = xlsxwriter.Workbook(self.reportPath+'SUNLIFE_report.xlsx')
        
        self.basicInfo_sheet = self.workbook.add_worksheet(name="General Information")
        self.basicInfo_sheet.write(0, 0, "Policy No.")

        self.scope_customerInfo = self.workbook.add_worksheet(name="Customer Information")
        self.scope_customerInfo.write(0, 0, "Policy No.")

        self.coverage_sheet = self.workbook.add_worksheet(name="Coverage Details")
        self.coverage_sheet.write(0, 0, "Policy No.")

        self.policyValue_sheet = self.workbook.add_worksheet(name="Policy Value")
        self.policyValue_sheet.write(0, 0, "Policy No.")

        self.logger.writeLogString('SUNLIFE-INIT','maxPolicyListSize:'+str(self.maxPolicyListSize))
        
    def waitingLoginComplete(self):
        self.logger.writeLogString('SUNLIFE-LOGIN','START LOGIN')
        self.browser.get("https://new.sunlife.com.hk/index.aspx?login_from=p")
        self.frame.setStatusLableText("Waiting Login")
        
        while not self.isLogin and not self.isStopped:
            try:
                self.browser.window_handles[1]
                time.sleep(1)
                self.browser.close()
                time.sleep(1)
                self.browser.switch_to.window(self.browser.window_handles[0])
                time.sleep(1)
                self.isLogin=True
                self.browser.find_element_by_link_text('Individual Life Policy Enquiry').click()
                time.sleep(1)
                downLine = Select(self.browser.find_element_by_id('Search_DropDownList2'))
                downLine.select_by_visible_text('Downline')
                time.sleep(1)
                downLineSelectValue = Select(self.browser.find_element_by_id('Search_select2'))
                downLineSelectValue.select_by_visible_text('Yes')
                time.sleep(1)
            except:
                time.sleep(2)
        else:
            pass

        if self.isLogin:
            self.frame.setStatusLableText("Logged in")
            self.logger.writeLogString('SUNLIFE-LOGIN','LOGIN COMPLETED')

    def scrapPolicy(self):
        for policy in self.policyList:
            if self.isStopped:
                return
            try:
                self.frame.setStatusLableText("Processing "+str(policy))
                self.logger.writeLogString('SUNLIFE','PROCESSING:'+str(policy))
                
                input = self.browser.find_element_by_id('Search_text1')
                input.clear()
                input.send_keys(str(policy))
                
                self.browser.find_element_by_id('Search_ImageButton1').click()
                self.browser.find_element_by_link_text(str(policy)).click()
                
                time.sleep(1)
                soup = BeautifulSoup(self.browser.page_source, 'lxml')
                file1 = open(str(self.reportPath+policy)+"_basic"+".txt","a",encoding="utf-8")#append mode 
                file1.write(soup.prettify()) 
                file1.close()
                
                self.browser.find_element_by_id('CUST_INFO').click()
                time.sleep(1)
                soup = BeautifulSoup(self.browser.page_source, 'lxml')
                file1 = open(str(self.reportPath+policy)+"_customerInfo"+".txt","a",encoding="utf-8")#append mode 
                file1.write(soup.prettify()) 
                file1.close()
                
                self.browser.find_element_by_id('COV_DTL').click()
                time.sleep(1)
                soup = BeautifulSoup(self.browser.page_source, 'lxml')
                file1 = open(str(self.reportPath+policy)+"_coverageDetails"+".txt","a",encoding="utf-8")#append mode 
                file1.write(soup.prettify()) 
                file1.close()
                
                self.browser.find_element_by_id('POL_VAL').click()
                time.sleep(1)
                soup = BeautifulSoup(self.browser.page_source, 'lxml')
                file1 = open(str(self.reportPath+policy)+"_polictValue"+".txt","a",encoding="utf-8")#append mode 
                file1.write(soup.prettify()) 
                file1.close()
                
                self.browser.find_element_by_xpath("/html/body/div/form/table/tbody/tr[4]/td/img").click()
            except:
                self.logger.writeLogString('SUNLIFE',str(policy)+" NOT FOUND")
                self.frame.setStatusLableText(policy+" is not found")
            finally:
                self.frame.setStatusLableText(policy+" completed")
                self.logger.writeLogString('SUNLIFE',str(policy)+" COPMLETED")
                self.frame.setStatusProgresValueByValue(1)
                self.buildReportQueue.append(policy)
                self.buildHeaderQueue.append(policy)
                
    def buildReport(self):
        self.buildReportThread = threading.Thread(target = self.__buildReport)
        self.buildReportThread.start()
        self.buildReportHeaderFullFlow()
        pass

    def buildReportOnly(self):
        self.buildReportThread = threading.Thread(target = self.__buildReportOnly)
        self.buildReportThread.start()
        self.buildReportHeaderHalfFlow()
        pass

    def buildReportHeaderFullFlow(self):
        self.buildHeaderThread = threading.Thread(target = self.__buildReportHeaderFullFlow)
        self.buildHeaderThread.start()
        pass
    
    def buildReportHeaderHalfFlow(self):
        self.buildHeaderThread = threading.Thread(target = self.__buildReportHeaderHalfFlow)
        self.buildHeaderThread.start()
        pass

    def __buildReportHeaderFullFlow(self):
        self.logger.writeLogString('SUNLIFE-HEADER','START BUILD HEADER FULLFLOW')
        policy_iteration = 0
        while policy_iteration < self.maxPolicyListSize:
            for policy in self.buildHeaderQueue:
                self.logger.writeLogString('MANU-HEADER','POLICY NO.:{0}'.format(str(policy)))
                if self.isStopped:
                    return
                try:

                    self.__formatBasicInfoHeader(policy,self.basicInfo_sheet,self.reportPath)
                    self.__formatCustomerInfoHeader(policy,self.scope_customerInfo,self.reportPath)
                    self.__formatCoverageHeader(policy,self.coverage_sheet,self.reportPath)
                    self.__formatPolicyValueHeader(policy,self.policyValue_sheet,self.reportPath)
                        
                    #No error when building the header,break all loop and then stop this thread
                    policy_iteration = self.maxPolicyListSize + 1
                    self.logger.writeLogString('SUNLIFE-HEADER','BUILD HEADER COMPLETED, BREAK LOOP')
                    break
                except FileNotFoundError:
                    self.logger.writeLogString('SUNLIFE-HEADER','FILE NOT FOUND')
                except Exception as ex:
                    self.logger.writeLogString('SUNLIFE-HEADER','EXCEPTION:'+str(ex))
                finally:
                    policy_iteration = policy_iteration + 1
                    if policy in self.buildHeaderQueue:
                        self.buildHeaderQueue.remove(policy)

    def __buildReportHeaderHalfFlow(self):
        self.logger.writeLogString('SUNLIFE-HEADER','START BUILD HEADER HALFFLOW')
        for policy in self.policyList:
            self.logger.writeLogString('SUNLIFE-HEADER','POLICY NO.:{0}'.format(str(policy)))
            if self.isStopped:
                return
            try:

                self.__formatBasicInfoHeader(policy,self.basicInfo_sheet,self.inputPath)
                self.__formatCustomerInfoHeader(policy,self.scope_customerInfo,self.inputPath)
                self.__formatCoverageHeader(policy,self.coverage_sheet,self.inputPath)
                self.__formatPolicyValueHeader(policy,self.policyValue_sheet,self.inputPath)
                    
                #No error when building the header,break all loop and then stop this thread
                self.logger.writeLogString('SUNLIFE-HEADER','BUILD HEADER COMPLETED, BREAK LOOP')
                break
            except FileNotFoundError as ex:
                self.logger.writeLogString('SUNLIFE-HEADER','FILE NOT FOUND')
            except Exception as ex:
                self.logger.writeLogString('SUNLIFE-HEADER','EXCEPTION:'+str(ex))

    def __buildReport(self):
        self.logger.writeLogString('SUNLIFE-CONTENT','START BUILD REPORT')
        policy_iteration = 0
        while policy_iteration < self.maxPolicyListSize:
            for policy in self.buildReportQueue:
                if self.isStopped:
                    return
                self.frame.setStatusLableText("Build Report "+str(policy))
                self.logger.writeLogString('SUNLIFE-CONTENT','POLICY NO.:{0}'.format(str(policy)))
                try:
                    self.basicInfo_sheet.write(policy_iteration+1,0,str(policy))
                    self.scope_customerInfo.write(policy_iteration+1,0,str(policy))
                    self.coverage_sheet.write(policy_iteration+1,0,str(policy))
                    self.policyValue_sheet.write(policy_iteration+1,0,str(policy))

                    thread_basicInfo = threading.Thread(target = self.__formatBasicInfo, args=[policy_iteration,policy,self.basicInfo_sheet,self.reportPath])
                    thread_basicInfo.start()

                    thread_scope = threading.Thread(target = self.__formatCustomerInfo, args=[policy_iteration,policy,self.scope_customerInfo,self.reportPath])
                    thread_scope.start()

                    thread_policyValue = threading.Thread(target = self.__formatCoverage, args=[policy_iteration,policy,self.coverage_sheet,self.reportPath])
                    thread_policyValue.start()
                    
                    thread_payment = threading.Thread(target = self.__formatPolicyValue, args=[policy_iteration,policy,self.policyValue_sheet,self.reportPath])
                    thread_payment.start()

                except FileNotFoundError:
                    self.basicInfo_sheet.write(policy_iteration+1,1,str(policy)+" not found in this A/C, please check other A/C")
                    self.frame.setStatusLableText("Build Report "+str(policy)+ " Not Found")
                    self.logger.writeLogString('SUNLIFE-CONTENT','FILE NOT FOUND')
                except Exception as ex:
                    self.basicInfo_sheet.write(policy_iteration+1,1,"System Error ! Please contact IT Support!"+str(ex))
                    self.frame.setStatusLableText("Build Report "+str(policy)+ " Failed")
                    self.logger.writeLogString('SUNLIFE-CONTENT','EXCEPTION:'+str(ex))
                finally:
                    thread_basicInfo.join()
                    thread_scope.join()
                    thread_policyValue.join()
                    thread_payment.join()
                    self.frame.setStatusProgresValueByValue(1)
                    policy_iteration = policy_iteration + 1
                    self.buildReportQueue.remove(policy)
        
        self.buildHeaderThread.join()
        self.workbook.close()
        self.frame.setStatusLableText("Completed")
        self.logger.writeLogString('SUNLIFE-CONTENT','COPMLETED BUILD REPORT')

    def __buildReportOnly(self):
        self.logger.writeLogString('SUNLIFE-CONTENT','START BUILD REPORT OFFLINE MODE')
        for policy_iteration,policy in enumerate(self.policyList):
            if self.isStopped:
                return
            self.frame.setStatusLableText("Build Report "+str(policy))
            self.logger.writeLogString('SUNLIFE-CONTENT','POLICY NO.:{0}'.format(str(policy)))
            try:
                self.basicInfo_sheet.write(policy_iteration+1,0,str(policy))
                self.scope_customerInfo.write(policy_iteration+1,0,str(policy))
                self.coverage_sheet.write(policy_iteration+1,0,str(policy))
                self.policyValue_sheet.write(policy_iteration+1,0,str(policy))
                
                thread_basicInfo = threading.Thread(target = self.__formatBasicInfo, args=[policy_iteration,policy,self.basicInfo_sheet,self.inputPath])
                thread_basicInfo.start()

                thread_scope = threading.Thread(target = self.__formatCustomerInfo, args=[policy_iteration,policy,self.scope_customerInfo,self.inputPath])
                thread_scope.start()

                thread_policyValue = threading.Thread(target = self.__formatCoverage, args=[policy_iteration,policy,self.coverage_sheet,self.inputPath])
                thread_policyValue.start()
                
                thread_payment = threading.Thread(target = self.__formatPolicyValue, args=[policy_iteration,policy,self.policyValue_sheet,self.inputPath])
                thread_payment.start()
                
            except FileNotFoundError:
                self.basicInfo_sheet.write(policy_iteration+1,1,str(policy)+" not found in this A/C, please check other A/C")
                self.frame.setStatusLableText("Build Report "+str(policy)+ " Not Found")
                self.logger.writeLogString('SUNLIFE-CONTENT','FILE NOT FOUND')
            except Exception as ex:
                self.basicInfo_sheet.write(policy_iteration+1,1,"System Error ! Please contact IT Support!"+str(ex))
                self.frame.setStatusLableText("Build Report "+str(policy)+ " Failed")
                self.logger.writeLogString('SUNLIFE-CONTENT','EXCEPTION:'+str(ex))
            finally:
                thread_basicInfo.join()
                thread_scope.join()
                thread_policyValue.join()
                thread_payment.join()
                self.frame.setStatusProgresValueByValue(2)

        self.buildHeaderThread.join()
        self.workbook.close()
        self.frame.setStatusLableText("Completed")
        self.logger.writeLogString('SUNLIFE-CONTENT','COPMLETED BUILD REPORT OFFLINE MODE')

    def __formatBasicInfo(self,policy_iteration,policy,worksheet,path):
        file = open(path+policy+"_basic.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'form','id','dynamic_search')   
         
        soup_basic =soup_basic.find('tbody')
        
        soup_genralInfo = soup_basic.find('table')
        
        idx = 0
        for strong_tag in soup_genralInfo.find_all('td',{'class':'channel_policy_pending_content'}):
            if len(strong_tag.attrs) == 1 or strong_tag.attrs['width'] == '28%':
                content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
                worksheet.write(policy_iteration+1, idx+1, content)
                idx = idx + 1
        
        
        soup_benefit = soup_basic.find('table',{'id':'tblBenefit'})
        
        tableValue = []
        for strong_tag in soup_benefit.find_all('td',{'class':'channel_policy_pending_content'}):
            tableValue.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
        
        appendPlan = 3 - len(tableValue) / 11
        tableValue.extend(['','','','','','','','','','','']*int(appendPlan))
        
        for value in tableValue:
            worksheet.write(policy_iteration+1,idx+1,value)
            idx = idx + 1
        
        soup_payment = soup_basic.find('table',{'id':'tblPayInfo'})
        for strong_tag in soup_payment.find_all('td',{'class':'channel_policy_pending_content'}):
            if len(strong_tag.attrs) == 1 or strong_tag.attrs['width'] == '28%':
                content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
                worksheet.write(policy_iteration+1, idx+1, content)
                idx = idx + 1
                
                
        soup_policyValue = soup_basic.find('table',{'id':'tblPolVal'})
        soup_policyValue.find('span',attrs={'id':'lblLabView'}).decompose()
        for strong_tag in soup_policyValue.find_all('td',{'class':'channel_policy_pending_content'}):
            if len(strong_tag.attrs) == 1 or strong_tag.attrs['width'] == '28%':
                content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
                if content != '':
                    worksheet.write(policy_iteration+1, idx+1, content)
                    idx = idx + 1

        soup_benefit = soup_basic.find('table',{'id':'tblBenef'})
        tableValue = []
        
        for strong_tag in soup_benefit.find_all('td',{'class':'channel_policy_pending_content'}):
            tableValue.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
        
        appendPlan = 3 - len(tableValue) / 8
        tableValue.extend(['','','','','','','','','','','']*int(appendPlan))
        
        for value in tableValue:
            worksheet.write(policy_iteration+1,idx+1,value)
            idx = idx + 1

        pass
    
    def __formatBasicInfoHeader(self,policy,worksheet,path):
        file = open(path+policy+"_basic.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'form','id','dynamic_search')
        
        soup_basic =soup_basic.find('tbody')
        
        soup_genralInfo = soup_basic.find('table')
        
        idx = 0
        for strong_tag in soup_genralInfo.find_all('td',{'class':'general_search_desc'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            worksheet.write(0, idx+1, content)
            idx = idx + 1

        soup_benefit = soup_basic.find('table',{'id':'tblBenefit'})
        
        tableHeader = []
        for strong_tag in soup_benefit.find_all('td',{'class':'general_contactus_tablehead'}):
            tableHeader.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
            
        tableHeader = tableHeader * 3
        for header in tableHeader:
            worksheet.write(0, idx+1, header)
            idx = idx + 1
        
        
        soup_payment = soup_basic.find('table',{'id':'tblPayInfo'})
        for strong_tag in soup_payment.find_all('td',{'class':'general_search_desc'}):
            if not strong_tag.has_attr('colspan'):
                content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
                worksheet.write(0, idx+1, content)
                idx = idx + 1
            
        soup_policyValue = soup_basic.find('table',{'id':'tblPolVal'})
        soup_policyValue.find('span',attrs={'id':'lblLabView'}).decompose()
        for strong_tag in soup_policyValue.find_all('td',{'class':'general_search_desc'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if content != '':
                worksheet.write(0, idx+1, content)
                idx = idx + 1
        
        
        soup_benefit = soup_basic.find('table',{'id':'tblBenef'})
        tableHeader = []
        
        for strong_tag in soup_benefit.find_all('td',{'class':'general_contactus_tablehead'}):
            tableHeader.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
            
        tableHeader = tableHeader * 3
        for header in tableHeader:
            worksheet.write(0, idx+1, header)
            idx = idx + 1
            
        
        pass
    
    def __formatCustomerInfo(self,policy_iteration,policy,worksheet,path):
        file = open(path+policy+"_customerInfo.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'form','id','Form1')   
         
        soup_basic =soup_basic.find('tbody')
        
        owner = soup_basic.find('span',attrs={'id':'lblValOwnNm'})
        

        valueList = []
        idx = 0
        valueList.append(owner.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
        for strong_tag in soup_basic.find_all('td',{'class':'channel_policy_pending_content'}):
            tempSoup = BeautifulSoup(str(strong_tag), 'lxml')
            value = ''
            for tag in tempSoup.find_all('span'):
                value = tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
                if idx <= 8 or idx >= 17:
                    valueList.append(value)
                    
                else:
                    if idx % 2 == 1:
                        valueList[8] = valueList[8] +' '+ value
                    else:
                        valueList.append(value)
                idx = idx + 1            
            
        idx = 0
        for value in valueList:
            worksheet.write(policy_iteration+1,idx+1,value)
            idx = idx + 1
            
        pass
    
    def __formatCustomerInfoHeader(self,policy,worksheet,path):
        file = open(path+policy+"_customerInfo.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'form','id','Form1')   
         
        soup_basic =soup_basic.find('tbody')
        
        soup_header = soup_basic.find('span',attrs={'id':'lblLabOwnNm'})
        
        idx = 0
        worksheet.write(0, idx+1, soup_header.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
        idx = idx + 1
        for strong_tag in soup_basic.find_all('td',{'class':'general_search_desc'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if content != '':
                worksheet.write(0, idx+1, content)
                idx = idx + 1

        pass
    
    def __formatCoverage(self,policy_iteration,policy,worksheet,path):
        file = open(path+policy+"_coverageDetails.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'form','id','policy_coverage')   
         
        soup_benfit =soup_basic.find('tbody')
        
        while soup_benfit.find('table',attrs={'id':'table2'}) != None:
            soup_benfit.find('table',attrs={'id':'table2'}).decompose()

        valueList = []
        idx = 0
        for strong_tag in soup_benfit.find_all('td',{'class':'channel_policy_pending_content'}):
            if not strong_tag.has_attr('colspan'):
                valueList.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))

        appendPlan = 3 - len(valueList) / 10
        valueList.extend(['','','','','','','','','','']*int(appendPlan))


        for value in valueList:
            worksheet.write(policy_iteration+1,idx+1,value)
            idx = idx + 1
            
        
        soup_basic.find('tbody').decompose()
        soup_pending = soup_basic.find('tbody')
        for strong_tag in soup_pending.find_all('td',{'class':'channel_policy_pending_content'}):
            worksheet.write(policy_iteration+1,idx+1,strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
            idx = idx + 1

        pass
    
    def __formatCoverageHeader(self,policy,worksheet,path):
        file = open(path+policy+"_coverageDetails.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'form','id','policy_coverage')   
         
        soup_benfit = soup_basic.find('tbody')    
        
        headerList = []
        for strong_tag in soup_benfit.find_all('td',{'class':'general_search_desc'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            headerList.append(content)
        
        headerList.append('') #match with data row
        headerList = headerList * 3
        
        idx = 0
        for header in headerList:
            worksheet.write(0, idx+1, header)
            idx = idx + 1
        
        soup_basic.find('tbody').decompose()
        soup_pending = soup_basic.find('tbody')
        
        for strong_tag in soup_pending.find_all('td',{'class':'general_search_desc'}):
            worksheet.write(0, idx+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
            idx = idx + 1

        pass

    def __formatPolicyValue(self,policy_iteration,policy,worksheet,path):
        file = open(path+policy+"_polictValue.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'form','id','policy_value')   
         
        soup_basic =soup_basic.find('tbody')
        
        soup_cash = soup_basic.find('table')
        
        idx = 0
        for strong_tag in soup_cash.find_all('td',{'class':'channel_policy_pending_content'}):
            if len(strong_tag.attrs) == 1 or strong_tag.attrs['width'] == '28%':
                content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
                worksheet.write(policy_iteration+1, idx+1, content)
                idx = idx + 1
        
        soup_basic.find('table').decompose()
        
        soup_loan = soup_basic.find('table')
        
        for strong_tag in soup_loan.find_all('td',{'class':'channel_policy_pending_content'}):
            if len(strong_tag.attrs) == 1 or strong_tag.attrs['width'] == '28%':
                content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
                worksheet.write(policy_iteration+1, idx+1, content)
                idx = idx + 1
        
        pass
    
    def __formatPolicyValueHeader(self,policy,worksheet,path):
        file = open(path+policy+"_polictValue.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'form','id','policy_value')
        
        soup_basic =soup_basic.find('tbody')
        
        soup_cash = soup_basic.find('table')
        
        idx = 0
        for strong_tag in soup_cash.find_all('td',{'class':'general_search_desc'}):
            if not strong_tag.has_attr('colspan'):
                content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
                worksheet.write(0, idx+1, content)
                idx = idx + 1
            
        soup_basic.find('table').decompose()
        
        soup_loan = soup_basic.find('table')

        for strong_tag in soup_loan.find_all('td',{'class':'general_search_desc'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            worksheet.write(0, idx+1, content)
            idx = idx + 1
        
        pass