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

class ManulifeRobot(BaseRobot):
    def __init__(self, policyList, frame, reportPath, inputPath):
        super().__init__(policyList, frame, reportPath, inputPath)
        self.logger.writeLogString('MANU-INIT','ROBOT INIT')
        self.maxPolicyListSize = len(policyList)
        self.workbook = xlsxwriter.Workbook(self.reportPath+'MANULIFE_report.xlsx')
        
        self.basicInfo_sheet = self.workbook.add_worksheet(name="General Information")
        self.basicInfo_sheet.write(0, 0, "Policy No.")
        
        self.coverage_sheet = self.workbook.add_worksheet(name="Coverage")
        self.coverage_sheet.write(0, 0, "Policy No.")
        
        self.policyValue_sheet = self.workbook.add_worksheet(name="Policy Value")
        self.policyValue_sheet.write(0, 0, "Policy No.")
        

        self.logger.writeLogString('MANU-INIT','maxPolicyListSize:'+str(self.maxPolicyListSize))
        
        
    def waitingLoginComplete(self):
        self.frame.setStatusLableText("Waiting Login")
        self.logger.writeLogString('MANU-LOGIN','START LOGIN')
        self.browser.get("https://www.manutouch.com.hk/wps/portal/login?agent_type=BROKER")
        mouseMovement = ActionChains(self.browser)
        #wait until below show
        while not self.isLogin and not self.isStopped:
            try:
                WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/div[4]/div/ul[1]/li[2]/a")))
                self.isLogin=True  
            except:
                time.sleep(3)
        else:
            time.sleep(1)

        #open a dropdown menu
        tab = self.browser.find_element_by_xpath("/html/body/div[1]/div[3]/div[4]/div/ul[1]/li[2]/a")
        time.sleep(1)
        mouseMovement.move_to_element(tab).perform()
        time.sleep(1)
        #click to enter search page
        self.browser.find_element_by_xpath("/html/body/div[1]/div[3]/div[4]/div/ul[1]/li[2]/div/div/div[1]/h3[1]/a").click()
        
        if self.isLogin:
            self.frame.setStatusLableText("Logged in")
            self.logger.writeLogString('MANU-LOGIN','LOGIN COMPLETED')
    
    def scrapPolicy(self):

        for policy in self.policyList:
            if self.isStopped:
                return
            
            try:
                #there is a frame wrapped the input field
                self.browser.switch_to.frame(0)
                time.sleep(1)
                self.frame.setStatusLableText("Processing "+str(policy))
                self.logger.writeLogString('MANU','PROCESSING:'+str(policy))
                
                try:
                    input = self.browser.find_element_by_xpath("/html/body/table/tbody/tr/td/div/form/div[2]/div/table/tbody/tr/td/div[2]/table/tbody/tr/td/table[3]/tbody/tr[2]/td[2]/table/tbody/tr[4]/td[4]/input")
                except:
                    input = self.browser.find_element_by_xpath("/html/body/table/tbody/tr/td/div/form/div[2]/div/table/tbody/tr/td/div[4]/table[1]/tbody/tr/td/table[3]/tbody/tr[2]/td[2]/table/tbody/tr[4]/td[4]/input")
                    
                input.clear()
                input.send_keys(str(policy).replace('-',''))
                
                try:
                    self.browser.find_element_by_xpath("/html/body/table/tbody/tr/td/div/form/div[2]/div/table/tbody/tr/td/div[2]/table/tbody/tr/td/table[1]/tbody/tr[1]/td[2]/a[1]/img").click()
                except:
                    self.browser.find_element_by_xpath("/html/body/table/tbody/tr/td/div/form/div[2]/div/table/tbody/tr/td/div[4]/table[1]/tbody/tr/td/table[1]/tbody/tr[1]/td[2]/a[1]/img").click()
                
                time.sleep(2)
                self.browser.find_element_by_link_text(str(policy).replace('-','')).click()
                time.sleep(2)
                
                self.browser.switch_to.window(self.browser.window_handles[1])
                
                #Basic Info
                soup = BeautifulSoup(self.browser.page_source, 'lxml')
                file1 = open(str(self.reportPath+policy)+"_basic"+".txt","a",encoding="utf-8")#append mode 
                file1.write(soup.prettify()) 
                file1.close()
                
                #Coverage
                self.browser.find_element_by_xpath("//b[contains(text(),\'Coverage')]").click()
                time.sleep(1)
                soup = BeautifulSoup(self.browser.page_source, 'lxml')
                file1 = open(str(self.reportPath+policy)+"_Coverage"+".txt","a",encoding="utf-8")#append mode 
                file1.write(soup.prettify()) 
                file1.close()
                
                
                #Policy Value
                self.browser.find_element_by_xpath("//b[contains(text(),\'Policy Value')]").click()
                time.sleep(1)
                soup = BeautifulSoup(self.browser.page_source, 'lxml')
                file1 = open(str(self.reportPath+policy)+"_PolicyValue"+".txt","a",encoding="utf-8")#append mode 
                file1.write(soup.prettify()) 
                file1.close()
                
                self.browser.close()
            except Exception as ex:
                self.logger.writeLogString('MANU','EXCEPTION:'+str(ex))
                self.frame.setStatusLableText(policy+" is not found")
            finally:
                self.frame.setStatusLableText(policy+" completed")
                self.logger.writeLogString('MANU',str(policy)+" COPMLETED")
                self.frame.setStatusProgresValueByValue(1)
                self.browser.switch_to.window(self.browser.window_handles[0])
                self.browser.switch_to.default_content()
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
        self.logger.writeLogString('MANU-HEADER','START BUILD HEADER FULLFLOW')
        policy_iteration = 0
        while policy_iteration < self.maxPolicyListSize:
            for policy in self.buildHeaderQueue:
                self.logger.writeLogString('MANU-HEADER','POLICY NO.:{0}'.format(str(policy)))
                if self.isStopped:
                    return
                try:

                    self.__formatBasicInfoHeader(policy,self.basicInfo_sheet,self.reportPath)
                    self.__formatCoverageHeader(policy,self.coverage_sheet,self.reportPath)
                    self.__formatPolicyValueHeader(policy,self.policyValue_sheet,self.reportPath)
                        
                    #No error when building the header,break all loop and then stop this thread
                    policy_iteration = self.maxPolicyListSize + 1
                    self.logger.writeLogString('MANU-HEADER','BUILD HEADER COMPLETED, BREAK LOOP')
                    break
                except FileNotFoundError:
                    self.logger.writeLogString('MANU-HEADER','FILE NOT FOUND')
                except Exception as ex:
                    self.logger.writeLogString('MANU-HEADER','EXCEPTION:'+str(ex))
                finally:
                    policy_iteration = policy_iteration + 1
                    if policy in self.buildHeaderQueue:
                        self.buildHeaderQueue.remove(policy)

    def __buildReportHeaderHalfFlow(self):
        self.logger.writeLogString('MANU-HEADER','START BUILD HEADER HALFFLOW')
        for policy in self.policyList:
            self.logger.writeLogString('MANU-HEADER','POLICY NO.:{0}'.format(str(policy)))
            if self.isStopped:
                return
            try:

                self.__formatBasicInfoHeader(policy,self.basicInfo_sheet,self.inputPath)
                self.__formatCoverageHeader(policy,self.coverage_sheet,self.inputPath)
                self.__formatPolicyValueHeader(policy,self.policyValue_sheet,self.inputPath)
                    
                #No error when building the header,break all loop and then stop this thread
                self.logger.writeLogString('MANU-HEADER','BUILD HEADER COMPLETED, BREAK LOOP')
                break
            except FileNotFoundError as ex:
                self.logger.writeLogString('MANU-HEADER','FILE NOT FOUND')
            except Exception as ex:
                self.logger.writeLogString('MANU-HEADER','EXCEPTION:'+str(ex))

    def __buildReport(self):
        self.logger.writeLogString('MANU-CONTENT','START BUILD REPORT')
        policy_iteration = 0
        while policy_iteration < self.maxPolicyListSize:
            for policy in self.buildReportQueue:
                if self.isStopped:
                    return
                self.frame.setStatusLableText("Build Report "+str(policy))
                self.logger.writeLogString('MANU-CONTENT','POLICY NO.:{0}'.format(str(policy)))
                try:
                    self.basicInfo_sheet.write(policy_iteration+1,0,str(policy))
                    self.coverage_sheet.write(policy_iteration+1,0,str(policy))
                    self.policyValue_sheet.write(policy_iteration+1,0,str(policy))

                    thread_basicInfo = threading.Thread(target = self.__formatBasicInfo, args=[policy_iteration,policy,self.basicInfo_sheet,self.reportPath])
                    thread_basicInfo.start()

                    thread_Coverage = threading.Thread(target = self.__formatCoverage, args=[policy_iteration,policy,self.coverage_sheet,self.reportPath])
                    thread_Coverage.start()

                    thread_policyValue = threading.Thread(target = self.__formatPolicyValue, args=[policy_iteration,policy,self.policyValue_sheet,self.reportPath])
                    thread_policyValue.start()

                except FileNotFoundError:
                    self.basicInfo_sheet.write(policy_iteration+1,1,str(policy)+" not found in this A/C, please check other A/C")
                    self.frame.setStatusLableText("Build Report "+str(policy)+ " Not Found")
                    self.logger.writeLogString('MANU-CONTENT','FILE NOT FOUND')
                except Exception as ex:
                    self.basicInfo_sheet.write(policy_iteration+1,1,"System Error ! Please contact IT Support!"+str(ex))
                    self.frame.setStatusLableText("Build Report "+str(policy)+ " Failed")
                    self.logger.writeLogString('MANU-CONTENT','EXCEPTION:'+str(ex))
                finally:
                    thread_basicInfo.join()
                    thread_Coverage.join()
                    thread_policyValue.join()
                    self.frame.setStatusProgresValueByValue(1)
                    policy_iteration = policy_iteration + 1
                    self.buildReportQueue.remove(policy)
        
        self.buildHeaderThread.join()
        self.workbook.close()
        self.frame.setStatusLableText("Completed")
        self.logger.writeLogString('MANU-CONTENT','COPMLETED BUILD REPORT')

    def __buildReportOnly(self):
        self.logger.writeLogString('MANU-CONTENT','START BUILD REPORT OFFLINE MODE')
        for policy_iteration,policy in enumerate(self.policyList):
            if self.isStopped:
                return
            self.frame.setStatusLableText("Build Report "+str(policy))
            self.logger.writeLogString('MANU-CONTENT','POLICY NO.:{0}'.format(str(policy)))
            try:
                self.basicInfo_sheet.write(policy_iteration+1,0,str(policy))
                self.coverage_sheet.write(policy_iteration+1,0,str(policy))
                self.policyValue_sheet.write(policy_iteration+1,0,str(policy))
                
                thread_basicInfo = threading.Thread(target = self.__formatBasicInfo, args=[policy_iteration,policy,self.basicInfo_sheet,self.inputPath])
                thread_basicInfo.start()
                
                thread_Coverage = threading.Thread(target = self.__formatCoverage, args=[policy_iteration,policy,self.coverage_sheet,self.inputPath])
                thread_Coverage.start()

                thread_policyValue = threading.Thread(target = self.__formatPolicyValue, args=[policy_iteration,policy,self.policyValue_sheet,self.inputPath])
                thread_policyValue.start()
                
            except FileNotFoundError:
                self.basicInfo_sheet.write(policy_iteration+1,1,str(policy)+" not found in this A/C, please check other A/C")
                self.frame.setStatusLableText("Build Report "+str(policy)+ " Not Found")
                self.logger.writeLogString('MANU-CONTENT','FILE NOT FOUND')
            except Exception as ex:
                self.basicInfo_sheet.write(policy_iteration+1,1,"System Error ! Please contact IT Support!"+str(ex))
                self.frame.setStatusLableText("Build Report "+str(policy)+ " Failed")
                self.logger.writeLogString('MANU-CONTENT','EXCEPTION:'+str(ex))
            finally:
                thread_basicInfo.join()
                thread_Coverage.join()
                thread_policyValue.join()
                self.frame.setStatusProgresValueByValue(2)

        self.buildHeaderThread.join()
        self.workbook.close()
        self.frame.setStatusLableText("Completed")
        self.logger.writeLogString('MANU-CONTENT','COPMLETED BUILD REPORT OFFLINE MODE')

    def __formatBasicInfo(self,policy_iteration,policy,worksheet,path):
        
        #Basic Upper <table border="0" width="660" wrap="auto">
        
        #General Part <table width="598">
        
        file = open(path+policy+"_basic.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'table','width','598')
        
        while soup_basic.find('font') != None:
            soup_basic.find('font').decompose()
        
        idx = 0
        for strong_tag in soup_basic.find_all('td',{'class':'type3'}):
            #Only get the tag with "type 3 and span 2", it will duplicate the report
            if len(strong_tag.attrs) <= 1:
                continue
            
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            #if content != None and content !='':
            worksheet.write(policy_iteration+1, idx+1, content)
            idx = idx + 1
            # else:
            #     continue
           
        soup_basic_details = basic.find_all('table', attrs={'border':'0', 'width':'660','wrap':'auto'})
        soup_basic_details = BeautifulSoup(str(soup_basic_details), 'lxml')
        
        
        #Special handling for the address
        address = ''
        address_idx = 0
        for iteration,strong_tag in enumerate(soup_basic_details.find_all('td',{'class':'type3'})):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ').replace(':','').replace(" ","")
            
            #Max address has 4 lines
            if iteration == 2 or iteration == 4 or iteration == 6 or iteration == 9:
                if iteration == 2:
                    address_idx = idx
                    address = content
                    idx= idx+1
                    continue
                else:
                    address = address + ' '+content
                    continue
            
            if iteration == 7:
                if len(content) <= 0:
                    content = 'N/A'
            
            if len(content) > 0 and iteration < 12:
                worksheet.write(policy_iteration+1, idx+1, content)
                idx = idx + 1
            elif iteration >= 12 and iteration <=25:
                if len(strong_tag.attrs) <= 2 or iteration == 24:
                    worksheet.write(policy_iteration+1, idx+1, content)
                    idx = idx + 1
        
        worksheet.write(policy_iteration+1, address_idx+1, address)
                    
        soup_basic_autopay = basic.find_all('table', attrs={'border':'0', 'width':'577'})
        soup_basic_autopay = BeautifulSoup(str(soup_basic_autopay), 'lxml')
        #Total 3 elements need to remove
        try:
            soup_basic_autopay.find('td',attrs={'colspan':'6'}).decompose()
            soup_basic_autopay.find('td',attrs={'colspan':'6'}).decompose()
            soup_basic_autopay.find('td',attrs={'colspan':'6'}).decompose()
            soup_basic_autopay.find('td',attrs={'colspan':'6'}).decompose()
            soup_basic_autopay.find('td',attrs={'colspan':'6'}).decompose()
        except:
            pass
        
        waitingToInsert = []
        for strong_tag in soup_basic_autopay.find_all('td',{'class':'type3'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ').replace(':','').replace(" ","")
            #worksheet.write(policy_iteration+1, idx+1, content)
            #idx = idx + 1
            if idx >= 37:
                waitingToInsert.append((idx,content))
            else:
                worksheet.write(policy_iteration+1, idx+1, content)
            idx = idx + 1
            
        if len(waitingToInsert) <= 1:
            worksheet.write(policy_iteration+1,waitingToInsert[0][0]+1,"")
            worksheet.write(policy_iteration+1,waitingToInsert[0][0]+2,waitingToInsert[0][1])
            idx = idx + 1
        else:
            worksheet.write(policy_iteration+1,waitingToInsert[0][0]+1,waitingToInsert[0][1])
            worksheet.write(policy_iteration+1,waitingToInsert[1][0]+2,waitingToInsert[1][1])
            
    

        soup_basic_contact = basic.find_all('table', attrs={'border':'0', 'width':'577','wrap':'auto'})
        soup_basic_contact = BeautifulSoup(str(soup_basic_contact), 'lxml')
        for iteration,strong_tag in enumerate(soup_basic_contact.find_all('font',{'class':'type1'})):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ').replace(':','').replace(" ","")
            worksheet.write(policy_iteration+1, idx+1, content)
            idx = idx + 1
               
    def __formatBasicInfoHeader(self,policy,worksheet,path):
        file = open(path+policy+"_basic.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = self.SearchByHtmlTagValueKey(basic,'table','width','598')
        
        idx = 0
        for strong_tag in soup_basic.find_all('td',{'class':'type6'}):
            worksheet.write(0, idx+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
            idx = idx + 1
        
        #soup_basic_details = self.SearchByHtmlTagValueKey(basic,'table','width','660')
        soup_basic_details = basic.find_all('table', attrs={'border':'0', 'width':'660','wrap':'auto'})
        soup_basic_details = BeautifulSoup(str(soup_basic_details), 'lxml')
        
        for strong_tag in soup_basic_details.find_all('td',{'class':'type6'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if content == '':
                continue
            worksheet.write(0, idx+1, content)
            idx = idx + 1
            
        soup_basic_autopay = basic.find_all('table', attrs={'border':'0', 'width':'577'})
        soup_basic_autopay = BeautifulSoup(str(soup_basic_autopay), 'lxml')
        #Total 3 elements need to remove
        try:
            soup_basic_autopay.find('td',attrs={'colspan':'6'}).decompose()
            soup_basic_autopay.find('td',attrs={'colspan':'6'}).decompose()
            soup_basic_autopay.find('td',attrs={'colspan':'6'}).decompose()
            soup_basic_autopay.find('td',attrs={'colspan':'6'}).decompose()
            soup_basic_autopay.find('td',attrs={'colspan':'6'}).decompose()
        except:
            pass
        
        waitingToInsert = []
        for strong_tag in  soup_basic_autopay.find_all('td',{'class':'type6'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if content == '':
                continue
            elif idx >= 37:
                waitingToInsert.append((idx,content))
            else:
                worksheet.write(0, idx+1, content)
            idx = idx + 1
        
        #Check required to insert a default header value
        if len(waitingToInsert) <= 1:
            worksheet.write(0,waitingToInsert[0][0]+1,"Autopay Suspend")
            worksheet.write(0,waitingToInsert[0][0]+2,waitingToInsert[0][1])
            idx = idx + 1
        else:
            worksheet.write(0,waitingToInsert[0][0]+1,waitingToInsert[0][1])
            worksheet.write(0,waitingToInsert[1][0]+2,waitingToInsert[1][1])

        #soup_basic_details = self.SearchByHtmlTagValueKey(basic,'table','width','660')
        soup_basic_contact = basic.find_all('table', attrs={'border':'0', 'width':'577','wrap':'auto'})
        soup_basic_contact = BeautifulSoup(str(soup_basic_contact), 'lxml')
        
        for strong_tag in soup_basic_contact.find_all('font',{'class':'type6'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
            if content == '':
                continue
            worksheet.write(0, idx+1, content)
            idx = idx + 1
             
    def __formatCoverageHeader(self,policy, worksheet,path):
        file = open(path+policy+"_Coverage.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = basic.find_all('table', attrs={'border':'0', 'width':'580'})
        soup_coverage = BeautifulSoup(str(soup_basic), 'lxml')

        headerList = []
        for strong_tag in soup_coverage.find_all('font',{'class':'type6'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ').replace(':','')
            headerList.append(content)
        
        headerList = headerList * 4
        
        for iteration, header in enumerate(headerList):
             worksheet.write(0, iteration+1, header)
             
        
        #Find border for 2 times
        soup_basic = basic.find_all('table', attrs={'border':'0'})
        for tag in soup_basic:
            if len(tag.attrs) == 1:
                soup_coverage = BeautifulSoup(str(tag), 'lxml')
                soup_coverage = soup_coverage.find_all('table', attrs={'border':'0'})
                for tag in soup_coverage:
                    if len(tag.attrs) == 1:
                        soup_coverage = BeautifulSoup(str(tag), 'lxml')
                        break;
        
        idx = 16
        for strong_tag in soup_coverage.find_all('font',{'class':'type6'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ').replace(':','')
            worksheet.write(0, idx+1, content)
            idx = idx + 1    
        worksheet.write(0, idx+1, "PLAN NAME")
        
 
        pass 
    
    def __formatCoverage(self,policy_iteration,policy, worksheet,path):
        file = open(path+policy+"_Coverage.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()
        
        soup_basic = basic.find_all('table', attrs={'border':'0', 'width':'580'})
        soup_coverage = BeautifulSoup(str(soup_basic), 'lxml')

        valueList = []
        for strong_tag in soup_coverage.find_all('font',{'class':'type3'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ').replace(':','')
            valueList.append(content)
        
        for x in range(0,16):
            if x < len(valueList):
                worksheet.write(policy_iteration+1, x+1, valueList[x])
            else:
                worksheet.write(policy_iteration+1, x+1, '')
        
        
        #Find border for 2 times
        soup_basic = basic.find_all('table', attrs={'border':'0'})
        for tag in soup_basic:
            if len(tag.attrs) == 1:
                soup_coverage = BeautifulSoup(str(tag), 'lxml')
                soup_coverage = soup_coverage.find_all('table', attrs={'border':'0'})
                for tag in soup_coverage:
                    if len(tag.attrs) == 1:
                        soup_coverage = BeautifulSoup(str(tag), 'lxml')
                        break;
        
        idx = 16
        for strong_tag in soup_coverage.find_all('font',{'class':'type3'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ').replace(':','')
            worksheet.write(policy_iteration+1, idx+1, content)
            idx = idx + 1        
        pass

    def __formatPolicyValueHeader(self,policy, worksheet,path):
        file = open(path+policy+"_PolicyValue.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()

        soup_basic = basic.find_all('table', attrs={'border':'0', 'width':'580'})
        soup_policyValue = BeautifulSoup(str(soup_basic), 'lxml')
        
        try:
            soup_policyValue.find('td',attrs={'colspan':'6'}).decompose()
            soup_policyValue.find('td',attrs={'colspan':'6'}).decompose()
            soup_policyValue.find('td',attrs={'colspan':'6'}).decompose()
            soup_policyValue.find('td',attrs={'colspan':'6'}).decompose()
        except:
            pass
        
        idx = 0
        for strong_tag in soup_policyValue.find_all('td',{'class':'type6'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ').replace(':','')
            if content == '':
                continue
            worksheet.write(0, idx+1, content)
            idx = idx + 1
        pass

    def __formatPolicyValue(self,policy_iteration,policy, worksheet,path):
        file = open(path+policy+"_PolicyValue.txt",encoding="utf-8")#append mode 
        #Full Html src
        basic = BeautifulSoup(file.read(), 'lxml')
        file.close()

        soup_basic = basic.find_all('table', attrs={'border':'0', 'width':'580'})
        soup_policyValue = BeautifulSoup(str(soup_basic), 'lxml')
        
        try:
            soup_policyValue.find('td',attrs={'colspan':'6'}).decompose()
            soup_policyValue.find('td',attrs={'colspan':'6'}).decompose()
            soup_policyValue.find('td',attrs={'colspan':'6'}).decompose()
            soup_policyValue.find('td',attrs={'colspan':'6'}).decompose()
        except:
            pass
        
        idx = 0
        for strong_tag in soup_policyValue.find_all('td',{'class':'type3'}):
            content = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ').replace(':','').replace(' ','')
            if content == '':
                continue
            worksheet.write(policy_iteration+1, idx+1, content)
            idx = idx + 1
        pass

