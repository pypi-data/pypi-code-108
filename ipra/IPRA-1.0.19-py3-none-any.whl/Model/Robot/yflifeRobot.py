from os import write
import time
from bs4 import BeautifulSoup
import xlsxwriter
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from ipra.Model.Robot.baseRobot import BaseRobot
import threading

class YFLifeRobot(BaseRobot):
    def __init__(self, policyList, frame, reportPath, inputPath):
        super().__init__(policyList, frame, reportPath, inputPath)
        self.logger.writeLogString('YFLIFE-INIT','ROBOT INIT')
        
        self.maxPolicyListSize = len(policyList)
        self.workbook = xlsxwriter.Workbook(self.reportPath+'YFLIFE_report.xlsx')

        self.basicInfo_sheet = self.workbook.add_worksheet(name="General Information")
        self.basicInfo_sheet.write(0, 0, "Policy No.")
        
        self.value_payment = self.workbook.add_worksheet(name="Payment Information")
        self.value_payment.write(0, 0, "Policy No.")
                
        self.related_person = self.workbook.add_worksheet(name="Related Person")
        self.related_person.write(0, 0, "Policy No.")

        self.policy_info = self.workbook.add_worksheet(name="Policy Info")
        self.policy_info.write(0, 0, "Policy No.")
     
        self.logger.writeLogString('YFLIFE-INIT','maxPolicyListSize:'+str(self.maxPolicyListSize))

    def waitingLoginComplete(self):
        self.frame.setStatusLableText("Waiting Login")
        self.logger.writeLogString('YFLIFE-LOGIN','START LOGIN')
        self.browser.get("https://app.yflife.com/AESWeb/zh-HK/")
        while not self.isLogin and not self.isStopped:
            try:
                self.browser.find_element_by_xpath("/html/body/div[5]/table/tbody/tr/td[5]/div/form/table/tbody/tr/td[2]/input[1]")
                time.sleep(1)
                self.isLogin=True
            except:
                time.sleep(1)
        else:
            pass
        
        if self.isLogin:
            self.frame.setStatusLableText("Logged in")
            self.logger.writeLogString('YFLIFE-LOGIN','LOGIN COMPLETED')
  
    def scrapPolicy(self):
        
        for policy in self.policyList:
            if self.isStopped:
                return
            try:
                self.frame.setStatusLableText("Processing "+str(policy))
                self.logger.writeLogString('YFLIFE','PROCESSING:'+str(policy))
                input = self.browser.find_element_by_xpath("/html/body/div[5]/table/tbody/tr/td[5]/div/form/table/tbody/tr/td[2]/input[1]")

                input.clear()
                input.send_keys(str(policy))
                self.browser.find_element_by_xpath("/html/body/div[5]/table/tbody/tr/td[5]/div/form/table/tbody/tr/td[3]/button").click()                
                time.sleep(2)
            
                soup = BeautifulSoup(self.browser.page_source, 'lxml')
                file1 = open(str(self.reportPath+policy)+".txt","a",encoding="utf-8")#append mode 
                file1.write(soup.prettify()) 
                file1.close()

            except Exception as ex:
                self.logger.writeLogString('YFLIFE','EXCEPTION:'+str(ex))
                self.frame.setStatusLableText(policy+" is not found")
            finally:
                self.frame.setStatusLableText(policy+" completed")
                self.logger.writeLogString('YFLIFE',str(policy)+" COPMLETED")
                self.frame.setStatusProgresValueByValue(1)
                self.buildReportQueue.append(policy)
                self.buildHeaderQueue.append(policy)
        pass

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
        self.logger.writeLogString('YFLIFE-HEADER','START BUILD HEADER FULLFLOW')
        policy_iteration = 0
        while policy_iteration < self.maxPolicyListSize:
            for policy in self.buildHeaderQueue:
                self.logger.writeLogString('YFLIFE-HEADER','POLICY NO.:{0}'.format(str(policy)))
                if self.isStopped:
                    return
                try:

                    self.__formatBasicInfoHeader(policy,self.basicInfo_sheet,self.reportPath)
                    self.__formatValueHeader(policy,self.value_payment,self.reportPath)
                    self.__formatRelatedPersonHeader(policy,self.related_person,self.reportPath)
                    self.__formatPolicyInfoHeader(policy,self.policy_info,self.reportPath)
                    
                    #No error when building the header,break all loop and then stop this thread
                    policy_iteration = self.maxPolicyListSize + 1
                    self.logger.writeLogString('YFLIFE-HEADER','BUILD HEADER COMPLETED, BREAK LOOP')
                    break
                except FileNotFoundError:
                    self.logger.writeLogString('YFLIFE-HEADER','FILE NOT FOUND')
                except Exception as ex:
                    self.logger.writeLogString('YFLIFE-HEADER','EXCEPTION:'+str(ex))
                finally:
                    policy_iteration = policy_iteration + 1
                    if policy in self.buildHeaderQueue:
                        self.buildHeaderQueue.remove(policy)

    def __buildReportHeaderHalfFlow(self):
        self.logger.writeLogString('YFLIFE-HEADER','START BUILD HEADER HALFFLOW')
        for policy in self.policyList:
            self.logger.writeLogString('YFLIFE-HEADER','POLICY NO.:{0}'.format(str(policy)))
            if self.isStopped:
                return
            try:

                self.__formatBasicInfoHeader(policy,self.basicInfo_sheet,self.inputPath)
                self.__formatValueHeader(policy,self.value_payment,self.inputPath)
                self.__formatRelatedPersonHeader(policy,self.related_person,self.inputPath)
                self.__formatPolicyInfoHeader(policy,self.policy_info,self.inputPath)

                #No error when building the header,break all loop and then stop this thread
                self.logger.writeLogString('YFLIFE-HEADER','BUILD HEADER COMPLETED, BREAK LOOP')
                break
            except FileNotFoundError as ex:
                self.logger.writeLogString('YFLIFE-HEADER','FILE NOT FOUND')
            except Exception as ex:
                self.logger.writeLogString('YFLIFE-HEADER','EXCEPTION:'+str(ex))

    def __buildReport(self):
        self.logger.writeLogString('YFLIFE-CONTENT','START BUILD REPORT')
        policy_iteration = 0
        while policy_iteration < self.maxPolicyListSize:
            for policy in self.buildReportQueue:
                if self.isStopped:
                    return
                self.frame.setStatusLableText("Build Report "+str(policy))
                self.logger.writeLogString('YFLIFE-CONTENT','POLICY NO.:{0}'.format(str(policy)))
                try:
                    self.basicInfo_sheet.write(policy_iteration+1,0,str(policy))
                    self.value_payment.write(policy_iteration+1,0,str(policy))
                    self.related_person.write(policy_iteration+1,0,str(policy))
                    self.policy_info.write(policy_iteration+1,0,str(policy))

                    thread_basicInfo = threading.Thread(target = self.__formatBasicInfo, args=[policy_iteration,policy,self.basicInfo_sheet,self.reportPath])
                    thread_basicInfo.start()

                    thread_value = threading.Thread(target = self.__formatValue, args=[policy_iteration,policy,self.value_payment,self.reportPath])
                    thread_value.start()

                    thread_relatedPerson = threading.Thread(target = self.__formatRelatedPerson, args=[policy_iteration,policy,self.related_person,self.reportPath])
                    thread_relatedPerson.start()

                    thread_policyInfo = threading.Thread(target = self.__formatPolicyInfo, args=[policy_iteration,policy,self.policy_info,self.reportPath])
                    thread_policyInfo.start()

                except FileNotFoundError:
                    self.basicInfo_sheet.write(policy_iteration+1,1,str(policy)+" not found in this A/C, please check other A/C")
                    self.frame.setStatusLableText("Build Report "+str(policy)+ " Not Found")
                    self.logger.writeLogString('YFLIFE-CONTENT','FILE NOT FOUND')
                except Exception as ex:
                    self.basicInfo_sheet.write(policy_iteration+1,1,"System Error ! Please contact IT Support!"+str(ex))
                    self.frame.setStatusLableText("Build Report "+str(policy)+ " Failed")
                    self.logger.writeLogString('YFLIFE-CONTENT','EXCEPTION:'+str(ex))
                finally:
                    thread_basicInfo.join()
                    thread_value.join()
                    thread_relatedPerson.join()
                    thread_policyInfo.join()
                    self.frame.setStatusProgresValueByValue(1)
                    policy_iteration = policy_iteration + 1
                    self.buildReportQueue.remove(policy)
        self.buildHeaderThread.join()
        self.workbook.close()
        self.frame.setStatusLableText("Completed")
        self.logger.writeLogString('YFLIFE-CONTENT','COPMLETED BUILD REPORT')

    def __buildReportOnly(self):
        self.logger.writeLogString('YFLIFE-CONTENT','START BUILD REPORT OFFLINE MODE')
        for policy_iteration,policy in enumerate(self.policyList):
            if self.isStopped:
                return
            self.frame.setStatusLableText("Build Report "+str(policy))
            self.logger.writeLogString('YFLIFE-CONTENT','POLICY NO.:{0}'.format(str(policy)))
            try:
                
                self.basicInfo_sheet.write(policy_iteration+1,0,str(policy))
                self.value_payment.write(policy_iteration+1,0,str(policy))
                self.related_person.write(policy_iteration+1,0,str(policy))
                self.policy_info.write(policy_iteration+1,0,str(policy))

                thread_basicInfo = threading.Thread(target = self.__formatBasicInfo, args=[policy_iteration,policy,self.basicInfo_sheet,self.inputPath])
                thread_basicInfo.start()

                thread_value = threading.Thread(target = self.__formatValue, args=[policy_iteration,policy,self.value_payment,self.inputPath])
                thread_value.start()

                thread_relatedPerson = threading.Thread(target = self.__formatRelatedPerson, args=[policy_iteration,policy,self.related_person,self.inputPath])
                thread_relatedPerson.start()

                thread_policyInfo = threading.Thread(target = self.__formatPolicyInfo, args=[policy_iteration,policy,self.policy_info,self.inputPath])
                thread_policyInfo.start()

            except FileNotFoundError:
                self.basicInfo_sheet.write(policy_iteration+1,1,str(policy)+" not found in this A/C, please check other A/C")
                self.frame.setStatusLableText("Build Report "+str(policy)+ " Not Found")
                self.logger.writeLogString('YFLIFE-CONTENT','FILE NOT FOUND')
            except Exception as ex:
                self.basicInfo_sheet.write(policy_iteration+1,1,"System Error ! Please contact IT Support!"+str(ex))
                self.frame.setStatusLableText("Build Report "+str(policy)+ " Failed")
                self.logger.writeLogString('YFLIFE-CONTENT','EXCEPTION:'+str(ex))
            finally:
                thread_basicInfo.join()
                thread_value.join()
                thread_relatedPerson.join()
                thread_policyInfo.join()
                self.frame.setStatusProgresValueByValue(2)

        self.buildHeaderThread.join()
        self.workbook.close()
        self.frame.setStatusLableText("Completed")
        self.logger.writeLogString('YFLIFE-CONTENT','COPMLETED BUILD REPORT OFFLINE MODE')
        
    def __formatBasicInfoHeader(self,policy,worksheet,path):
        file = open(path+policy+".txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'div','id','MainContent')
        soup_basic = self.SearchByHtmlTagValueKey(soup_basic,'form','id','formSearchPol')
        soup_basic = self.SearchByHtmlTagValueKey(soup_basic,'table','class','TableGrid')
        
        headerList = []
        for strong_tag in soup_basic.find_all('td',attrs={'class':'FieldName'}):
            header = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if header == '':
                continue
            else:
                headerList.append(header)
        
        
        #Only 12 and 13 need to insert, 14 or more now not required
        if len(headerList) == 11:
            headerList.insert(6,'年金發放年齡')
            headerList.insert(8,'繳付保費年期')
        elif len(headerList) == 12:
            headerList.insert(8,'繳付保費年期')
            
            
        soup_basic = self.SearchByHtmlTagValueKey(basic,'div','id','tabs-8')
        soup_upperGrid = soup_basic.find('table',attrs={'class':'TableGrid'})
        for strong_tag in soup_upperGrid.find_all('td',attrs={'class':'FieldName'}):
            header = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if header == '':
                continue
            else:
                headerList.append(header)
        
        if len(headerList) == 24:
            headerList.insert(20,'性別')
            headerList.insert(21,'出生日期')
        
        soup_basic.find('table',attrs={'class':'TableGrid'}).decompose()
        soup_lowerGrid = soup_basic.find('table',attrs={'class':'TableGrid'})
        for strong_tag in soup_lowerGrid.find_all('td',attrs={'class':'FieldName'}):
            header = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if header == '':
                continue
            else:
                headerList.append(header)
        
        if len(headerList) == 43:
            headerList.insert(41,'保障生效日期')
            
        soup_basic = self.SearchByHtmlTagValueKey(basic,'table','id','ps-benDtl-view2')
        for strong_tag in soup_basic.find_all('th'):
            header = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if header == '':
                continue
            else:
                headerList.append(header)
        
        for iteration , value in enumerate(headerList):
            worksheet.write(0, iteration+1, value)
    
    def __formatValueHeader(self,policy,worksheet,path):
        file = open(path+policy+".txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'div','id','tabs-2')
        
        soup_basic = soup_basic.find('table',attrs={'class':'TableGrid'})
        try:
            soup_basic.find('tr').decompose() #1st tr is empty line
        except:
            pass  
        
        for iteration,strong_tag in enumerate(soup_basic.find_all('td',attrs={'class':'FieldName'})):
            header = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if header == '':
                continue
            else:
                worksheet.write(0, iteration+1, header)

        pass
    
    def __formatRelatedPersonHeader(self,policy,worksheet,path):
        file = open(path+policy+".txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'div','id','tabs-6')
        
        soup_basic = soup_basic.find('table',attrs={'class':'TableGrid'})
        try:
            soup_basic.find('tr').decompose() #1st tr is empty line
        except:
            pass  
        
        for iteration,strong_tag in enumerate(soup_basic.find_all('td',attrs={'class':'FieldName'})):
            header = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if header == '':
                continue
            else:
                worksheet.write(0, iteration+1, header)
    
    def __formatPolicyInfoHeader(self,policy,worksheet,path):
        file = open(path+policy+".txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'div','id','PolicyDetailsTabs')
        soup_basic = self.SearchByHtmlTagValueKey(soup_basic,'table','id','benDtl-all')
        
        for iteration,strong_tag in enumerate(soup_basic.find_all('th')):
            header = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            worksheet.write(0, iteration+1, header)
        pass
            
    def __formatBasicInfo(self,policy_iteration,policy,worksheet,path):
        file = open(path+policy+".txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        #This default from file
        worksheet.write(policy_iteration+1, 0, str(policy))
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'div','id','MainContent')
        soup_basic = self.SearchByHtmlTagValueKey(soup_basic,'form','id','formSearchPol')
        soup_basic = self.SearchByHtmlTagValueKey(soup_basic,'table','class','TableGrid')
        
        try:
            while soup_basic.find('a') != None:
                soup_basic.find('a').decompose()
            while soup_basic.find('img') != None:
                soup_basic.find('img').decompose()             
        except:
            pass
        
        #This is from Soup
        valueList = []
        try:
            inputField = soup_basic.find('input',attrs={'id':'txtPolicyNo'})
            valueList.append(str(inputField['value']))
        except Exception as ex:
            valueList.append(str(policy))
        

        for strong_tag in soup_basic.find_all('td',attrs={'class':'FieldValue'}):
            value = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if value == '':
                continue
            else:
                valueList.append(value)
        
        
        #Only 12 and 13 need to insert, 14 or more now not required
        if len(valueList) == 11:
            valueList.insert(6,'N/A')
            valueList.insert(8,'N/A')
        elif len(valueList) == 12:
            valueList.insert(8,'N/A')
            
        soup_basic = self.SearchByHtmlTagValueKey(basic,'div','id','tabs-8')
        soup_upperGrid = soup_basic.find('table',attrs={'class':'TableGrid'})
        for strong_tag in soup_upperGrid.find_all('td',attrs={'class':'FieldValue'}):
            value = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if value == '':
                continue
            else:
                valueList.append(value)

        #insert address at 22, short at 20
        address = ''
        for strong_tag in soup_upperGrid.find_all('div',attrs={'style':'display:inline;'}):
            value = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if value == '':
                continue
            else:
                address = address + value
        
        if len(valueList) == 25:
            valueList.insert(23,address)
        elif len(valueList) == 23:
            valueList.insert(20,'N/A')
            valueList.insert(21,'N/A')
            valueList.insert(23,address)
            
        soup_basic.find('table',attrs={'class':'TableGrid'}).decompose()
        soup_loweGrid = soup_basic.find('table',attrs={'class':'TableGrid'})
        
        valueStartingLen  = len(valueList)
        
        for iteration, strong_tag in enumerate(soup_loweGrid.find_all('td',attrs={'class':'FieldValue'})):
            value = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if value == '':
                if iteration == 3:
                    iteration = iteration -1
                    #there is a empty line
                    pass
                elif iteration / 3 < 5:
                    if 3 - ((len(valueList) - valueStartingLen) % 3) > 0:
                        valueList.append('')
                else:
                    pass
            else:
                valueList.append(value)
            
        if len(valueList) == 43:
            valueList.insert(41,'')
            
        soup_basic = self.SearchByHtmlTagValueKey(basic,'table','id','ps-benDtl-view2')
        try:
            while soup_basic.find('td',attrs={'class':'SubCell'}) != None:
                soup_basic.find('td',attrs={'class':'SubCell'}).decompose()
        except:
            pass
        
        try:
            soup_basic.find('a').decompose()
        except:
            pass
        for strong_tag in soup_basic.find_all('td'):
            value = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if valueList == '':
                continue
            else:
                valueList.append(value)
            
        for iteration , value in enumerate(valueList):
            worksheet.write(policy_iteration+1, iteration+1, value)
    
    def __formatValue(self,policy_iteration,policy,worksheet,path):
        file = open(path+policy+".txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'div','id','tabs-2')
        
        soup_basic = soup_basic.find('table',attrs={'class':'TableGrid'})
        try:
            soup_basic.find('tr').decompose() #1st tr is empty line
        except:
            pass        
        for iteration,strong_tag in enumerate(soup_basic.find_all('td',attrs={'class':'FieldValue'})):
            value = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if value == '':
                continue
            else:
                worksheet.write(policy_iteration+1, iteration+1, value)
  
    def __formatRelatedPerson(self,policy_iteration,policy,worksheet,path):
        file = open(path+policy+".txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'div','id','tabs-6')
        
        soup_basic = soup_basic.find('table',attrs={'class':'TableGrid'})
        try:
            soup_basic.find('tr').decompose() #1st tr is empty line
        except:
            pass  
        valueList = []      
        for strong_tag in soup_basic.find_all('td',attrs={'class':'FieldValue'}):
            value = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            valueList.append(value)
        
        valueAddress = []
        for strong_tag in soup_basic.find_all('div',attrs={'style':'display:inline;'}):
            value = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if value != '':
                valueAddress.append(value)
        
        try:
            if valueList[7] == '':
                valueList[7] = valueAddress[0]
            if valueList[8] == '':
                valueList[8] = valueAddress[1]        
            if valueList[14] == '':
                valueList[14] = valueAddress[2]
            if valueList[15] == '':
                valueList[15] = valueAddress[3]
            
            if len(valueAddress) <= 2:
                valueList.append(valueAddress[0])
                valueList.append(valueAddress[1])
            else:
                valueList.append(valueAddress[4])
                valueList.append(valueAddress[5])

        except:
            pass 
        
        
        
        for iteration, value in enumerate(valueList):
            worksheet.write(policy_iteration+1, iteration+1, value)    
        
    def __formatPolicyInfo(self,policy_iteration,policy,worksheet,path):
        file = open(path+policy+".txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'div','id','PolicyDetailsTabs')
        soup_basic = self.SearchByHtmlTagValueKey(soup_basic,'table','id','benDtl-all')
        
        try:
            while soup_basic.find('td',attrs={'class':'SubCell'}) != None:
                soup_basic.find('td',attrs={'class':'SubCell'}).decompose()
        except:
            pass
        
        for iteration,strong_tag in enumerate(soup_basic.find_all('td')):
            value = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            worksheet.write(policy_iteration+1, iteration+1, value)
        pass