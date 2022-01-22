from ipra.Model.Robot.baseRobot import BaseRobot
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import xlsxwriter
import threading

class CignaRobot(BaseRobot):
    def __init__(self, policyList, frame, reportPath,inputPath):
        super().__init__(policyList, frame, reportPath,inputPath)
        self.logger.writeLogString('CIGNA-INIT','ROBOT INIT')

        self.maxPolicyListSize = len(policyList)
        self.workbook = xlsxwriter.Workbook(self.reportPath+'CIGNA_report.xlsx')
        self.worksheet = self.workbook.add_worksheet(name="General Information")
        self.worksheet.write(0, 0, "Policy No.")
        
        self.payment = self.workbook.add_worksheet(name="Payment Information")
        self.payment.write(0, 0, "Policy No.")        
        
        self.logger.writeLogString('CIGNA-INIT','maxPolicyListSize:'+str(self.maxPolicyListSize))

        pass
    
    def waitingLoginComplete(self):
        self.frame.setStatusLableText("Waiting Login")
        self.logger.writeLogString('CIGNA-LOGIN','START LOGIN')
        self.browser.get("https://partner.cigna.com.hk/s/my-portfolio")
        
        while not self.isLogin and not self.isStopped:
            try:
                self.browser.switch_to.frame(0)
                select = Select(self.browser.find_element_by_xpath("/html/body/div/div[2]/span/form/div[1]/div[2]/div/div[1]/div/div[1]/select"))
                select.select_by_value('Pol_Policy_Number')
                time.sleep(1)
                self.isLogin=True
            except:
                time.sleep(3)
        else:
            pass

        if self.isLogin:
            self.frame.setStatusLableText("Logged in")
            self.logger.writeLogString('CIGNA-LOGIN','LOGIN COMPLETED')


    def scrapPolicy(self):
        for policy in self.policyList:
            if self.isStopped:
                return
            try:
                self.frame.setStatusLableText("Processing "+str(policy))
                self.logger.writeLogString('CIGNA','PROCESSING:'+str(policy))
                isWaiting = True
                while isWaiting:
                    try:
                        input = self.browser.find_element_by_xpath("/html/body/div/div[2]/span/form/div[1]/div[2]/div/div[1]/div/div[2]/input")
                        input.clear()
                        input.send_keys(str(policy))
                        self.browser.find_element_by_xpath("/html/body/div/div[2]/span/form/div[1]/div[2]/div/div[1]/div/div[2]/i").click()
                        time.sleep(3)
                        isWaiting = False
                    except:
                        time.sleep(3)
                    
                #Waiting
                isWaiting = True
                while isWaiting:
                    try:
                        self.browser.find_element_by_xpath("//div[contains(text(),'{0}')]".format(str(policy))).click()
                        isWaiting = False
                    except:
                        pass
                    finally:
                        time.sleep(5)
                         
                #The policy content is in a frame, need switch to default and then switch back to the 1st frame
                #Waiting
                isWaiting = True
                while isWaiting:
                    try:
                        self.browser.switch_to.default_content()
                        self.browser.switch_to.frame(0)
                        isWaiting = False
                    except:
                        pass
                    finally:
                        time.sleep(5)
                    
                isWaiting = True
                while isWaiting:
                    try:
                        self.browser.find_element_by_xpath("//div[contains(text(),'{0}')]".format(str(policy)))
                        isWaiting = False
                    except:
                        pass
                else:
                    time.sleep(10)
                
                isWaiting = True
                while isWaiting:
                    try:
                        self.browser.find_element_by_xpath('/html/body/div/div[1]/div[2]/span/div/form/div[1]/table/tbody/tr/td[4]').click()
                        isWaiting = False
                    except:
                        pass
                else:
                    time.sleep(5)
                
                
                isWaiting = True
                while isWaiting:
                    try:
                        self.browser.find_element_by_xpath('/html/body/div/div[1]/div[2]/span/div/form/div[1]/table/tbody/tr/td[1]').click()
                        isWaiting = False
                    except:
                        pass
                else:
                    time.sleep(8)
                    
                
                soup = BeautifulSoup(self.browser.page_source, 'lxml')
                file1 = open(str(self.reportPath+policy)+".txt","a",encoding="utf-8")#append mode 
                file1.write(soup.prettify())
                file1.close()
                
                self.browser.switch_to.default_content()
                self.browser.switch_to.frame(0)
                
                self.browser.find_element_by_xpath("/html/body/div/div[1]/div[2]/span/div/form/div[2]/div[1]/div").click()
                time.sleep(3)
                pass
            except:
                self.logger.writeLogString('CIGNA',str(policy)+" NOT FOUND")
                self.frame.setStatusLableText(policy+" is not found")
            finally:
                self.frame.setStatusLableText(policy+" completed")
                self.logger.writeLogString('CIGNA',str(policy)+" COPMLETED")
                self.frame.setStatusProgresValueByValue(1)
                self.browser.switch_to.default_content()
                self.buildReportQueue.append(policy)
                self.buildHeaderQueue.append(policy)
                self.browser.switch_to.default_content()
                self.browser.switch_to.frame(0)
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
        self.logger.writeLogString('CIGNA-HEADER','START BUILD HEADER FULLFLOW')
        policy_iteration = 0
        while policy_iteration < self.maxPolicyListSize:
            for policy in self.buildHeaderQueue:
                self.logger.writeLogString('CIGNA-HEADER','POLICY NO.:{0}'.format(str(policy)))
                if self.isStopped:
                    return
                try:
                    
                    file = open(self.reportPath+policy+".txt",encoding="utf-8")#append mode 
                    #Full Html src
                    soup_all_src = BeautifulSoup(file.read(), 'lxml')
                    file.close()
                    
                    idx = 0
                    soup_policyInformationPanel = soup_all_src.find('div',attrs={'id':'policyInformationPanel'})
                    
                    for tag in soup_policyInformationPanel.find_all('div',attrs={'class':'bs col-xs-6 col-sm-3 field-label'}):
                        self.worksheet.write(0, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        idx = idx + 1

                    soup_policyHolderInformationPanel = soup_all_src.find('div',attrs={'id':'policyHolderInformationPanel'})
                    
                    for tag in soup_policyHolderInformationPanel.find_all('div',attrs={'class':'bs col-xs-6 col-sm-3 field-label'}):
                        self.worksheet.write(0, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        idx = idx + 1
                    
                    soup_contactInformationPanel = soup_all_src.find('div',attrs={'id':'contactInformationPanel'})
                        
                    for tag in soup_contactInformationPanel.find_all('div',attrs={'class':'bs col-xs-6 col-sm-3 field-label'}):
                        self.worksheet.write(0, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        idx = idx + 1

                    soup_personInsuredPanel = soup_all_src.find('div',attrs={'id':'personInsuredPanel'})
                      
                    for tag in soup_personInsuredPanel.find_all('td',attrs={'class':'bs field-label'}):
                        self.worksheet.write(0, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        idx = idx + 1
                    
                    
                    #Switch another sheet
                    idx = 0
                    soup_PaymentInformation = soup_all_src.find('div',attrs={'id':'PaymentInformation'})

                    for tag in soup_PaymentInformation.find_all('div',attrs={'class':'bs col-xs-6 col-md-3 field-label'}):
                        self.payment.write(0, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        idx = idx + 1

  
                    #No error when building the header,break all loop and then stop this thread
                    policy_iteration = self.maxPolicyListSize + 1
                    self.logger.writeLogString('CIGNA-HEADER','BUILD HEADER COMPLETED, BREAK LOOP')
                    break
                except FileNotFoundError as ex:
                    self.logger.writeLogString('CIGNA-HEADER','FILE NOT FOUND')
                except Exception as ex:
                    self.logger.writeLogString('CIGNA-HEADER','EXCEPTION:'+str(ex))
                finally:
                    policy_iteration = policy_iteration + 1
                    if policy in self.buildHeaderQueue:
                        self.buildHeaderQueue.remove(policy)


    def __buildReportHeaderHalfFlow(self):
        self.logger.writeLogString('CIGNA-HEADER','START BUILD HEADER HALFFLOW')
        for policy in self.policyList:
            self.logger.writeLogString('CIGNA-HEADER','POLICY NO.:{0}'.format(str(policy)))
            if self.isStopped:
                return
            try:
                file = open(self.inputPath+policy+".txt",encoding="utf-8")#append mode 
                #Full Html src
                soup_all_src = BeautifulSoup(file.read(), 'lxml')
                file.close()
                idx = 0
                soup_policyInformationPanel = soup_all_src.find('div',attrs={'id':'policyInformationPanel'})
                
                for tag in soup_policyInformationPanel.find_all('div',attrs={'class':'bs col-xs-6 col-sm-3 field-label'}):
                    self.worksheet.write(0, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    idx = idx + 1

                soup_policyHolderInformationPanel = soup_all_src.find('div',attrs={'id':'policyHolderInformationPanel'})
                
                for tag in soup_policyHolderInformationPanel.find_all('div',attrs={'class':'bs col-xs-6 col-sm-3 field-label'}):
                    self.worksheet.write(0, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    idx = idx + 1

                soup_contactInformationPanel = soup_all_src.find('div',attrs={'id':'contactInformationPanel'})
                    
                for tag in soup_contactInformationPanel.find_all('div',attrs={'class':'bs col-xs-6 col-sm-3 field-label'}):
                    self.worksheet.write(0, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    idx = idx + 1
                    
                soup_personInsuredPanel = soup_all_src.find('div',attrs={'id':'personInsuredPanel'})
                    
                for tag in soup_personInsuredPanel.find_all('td',attrs={'class':'bs field-label'}):
                    self.worksheet.write(0, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    idx = idx + 1

                idx = 0
                soup_PaymentInformation = soup_all_src.find('div',attrs={'id':'PaymentInformation'})

                for tag in soup_PaymentInformation.find_all('div',attrs={'class':'bs col-xs-6 col-md-3 field-label'}):
                    self.payment.write(0, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    idx = idx + 1           
                
                #No error when building the header,break all loop and then stop this thread
                self.logger.writeLogString('CIGNA-HEADER','BUILD HEADER COMPLETED, BREAK LOOP')
                break
            except FileNotFoundError as ex:
                self.logger.writeLogString('CIGNA-HEADER','FILE NOT FOUND')
            except Exception as ex:
                self.logger.writeLogString('CIGNA-HEADER','EXCEPTION:'+str(ex))


    def __buildReport(self):
        self.logger.writeLogString('CIGNA-CONTENT','START BUILD REPORT')
        policy_iteration = 0
        while policy_iteration < self.maxPolicyListSize:
            for policy in self.buildReportQueue:
                if self.isStopped:
                    return
                self.frame.setStatusLableText("Build Report "+str(policy))
                self.logger.writeLogString('CIGNA-CONTENT','POLICY NO.:{0}'.format(str(policy)))
                try:
                    self.worksheet.write(policy_iteration+1,0,str(policy))
                    self.payment.write(policy_iteration+1,0,str(policy))
                    file = open(self.reportPath+policy+".txt",encoding="utf-8")#append mode 
                    #Full Html src
                    soup_all_src = BeautifulSoup(file.read(), 'lxml')
                    file.close()

                    idx = 0
                    soup_policyInformationPanel = soup_all_src.find('div',attrs={'id':'policyInformationPanel'})
                    
                    for tag in soup_policyInformationPanel.find_all('div',attrs={'class':'bs col-xs-6 col-sm-3 field-value'}):
                        self.worksheet.write(policy_iteration+1, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        idx = idx + 1
                        
                    soup_policyHolderInformationPanel = soup_all_src.find('div',attrs={'id':'policyHolderInformationPanel'})
                    
                    for tag in soup_policyHolderInformationPanel.find_all('div',attrs={'class':'bs col-xs-6 col-sm-3 field-value'}):
                        self.worksheet.write(policy_iteration+1, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        idx = idx + 1

                    soup_contactInformationPanel = soup_all_src.find('div',attrs={'id':'contactInformationPanel'})
                        
                    for tag in soup_contactInformationPanel.find_all('div',attrs={'class':'bs col-xs-6 col-sm-9 field-value'}):
                        self.worksheet.write(policy_iteration+1, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        idx = idx + 1
                        
                    soup_personInsuredPanel = soup_all_src.find('div',attrs={'id':'personInsuredPanel'})
                        
                    for tag in soup_personInsuredPanel.find_all('td',attrs={'class':'bs field-value'}):
                        self.worksheet.write(policy_iteration+1, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        idx = idx + 1                

                    idx = 0
                    soup_PaymentInformation = soup_all_src.find('div',attrs={'id':'PaymentInformation'})

                    for tag in soup_PaymentInformation.find_all('div',attrs={'class':'bs col-xs-6 col-md-3 field-value'}):
                        self.payment.write(policy_iteration+1, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        idx = idx + 1           

                        
                except FileNotFoundError:
                    self.worksheet.write(policy_iteration+1,1,str(policy)+" not found in this A/C, please check other A/C")
                    self.frame.setStatusLableText("Build Report "+str(policy)+ " Not Found")
                    self.logger.writeLogString('CIGNA-CONTENT','FILE NOT FOUND')
                except Exception as ex:
                    self.worksheet.write(policy_iteration+1,1,"System Error ! Please contact IT Support!")
                    self.frame.setStatusLableText("Build Report "+str(policy)+ " Failed")
                    self.logger.writeLogString('CIGNA-CONTENT','EXCEPTION:'+str(ex))
                finally:
                    self.frame.setStatusProgresValueByValue(1)
                    policy_iteration = policy_iteration + 1
                    if policy in self.buildReportQueue:
                        self.buildReportQueue.remove(policy)
        self.buildHeaderThread.join()
        self.workbook.close()
        self.frame.setStatusLableText("Completed")
        self.logger.writeLogString('CIGNA-CONTENT','COPMLETED BUILD REPORT')


    def __buildReportOnly(self):
        self.logger.writeLogString('CIGNA-CONTENT','START BUILD REPORT OFFLINE MODE')
        for policy_iteration,policy in enumerate(self.policyList):
            if self.isStopped:
                return
            self.frame.setStatusLableText("Build Report "+str(policy))
            self.logger.writeLogString('CIGNA-CONTENT','POLICY NO.:{0}'.format(str(policy)))
            try:
                self.worksheet.write(policy_iteration+1,0,str(policy))
                self.payment.write(policy_iteration+1,0,str(policy))
                file = open(self.inputPath+policy+".txt",encoding="utf-8")#append mode 
                #Full Html src
                soup_all_src = BeautifulSoup(file.read(), 'lxml')
                file.close()
                idx = 0
                soup_policyInformationPanel = soup_all_src.find('div',attrs={'id':'policyInformationPanel'})
                
                for tag in soup_policyInformationPanel.find_all('div',attrs={'class':'bs col-xs-6 col-sm-3 field-value'}):
                    self.worksheet.write(policy_iteration+1, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    idx = idx + 1
    
                soup_policyHolderInformationPanel = soup_all_src.find('div',attrs={'id':'policyHolderInformationPanel'})
                
                for tag in soup_policyHolderInformationPanel.find_all('div',attrs={'class':'bs col-xs-6 col-sm-3 field-value'}):
                    self.worksheet.write(policy_iteration+1, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    idx = idx + 1
                    
                soup_contactInformationPanel = soup_all_src.find('div',attrs={'id':'contactInformationPanel'})
                    
                for tag in soup_contactInformationPanel.find_all('div',attrs={'class':'bs col-xs-6 col-sm-9 field-value'}):
                    self.worksheet.write(policy_iteration+1, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    idx = idx + 1

                soup_personInsuredPanel = soup_all_src.find('div',attrs={'id':'personInsuredPanel'})
                    
                for tag in soup_personInsuredPanel.find_all('td',attrs={'class':'bs field-value'}):
                    self.worksheet.write(policy_iteration+1, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    idx = idx + 1    
                    
                idx = 0
                soup_PaymentInformation = soup_all_src.find('div',attrs={'id':'PaymentInformation'})

                for tag in soup_PaymentInformation.find_all('div',attrs={'class':'bs col-xs-6 col-md-3 field-value'}):
                    self.payment.write(policy_iteration+1, idx+1, tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    idx = idx + 1           
                         
                    
            except FileNotFoundError:
                self.worksheet.write(policy_iteration+1,1,str(policy)+" not found in this A/C, please check other A/C")
                self.frame.setStatusLableText("Build Report "+str(policy)+ " Not Found")
                self.logger.writeLogString('CIGNA-CONTENT','FILE NOT FOUND')
            except Exception as ex:
                self.worksheet.write(policy_iteration+1,1,"System Error ! Please contact IT Support!")
                self.frame.setStatusLableText("Build Report "+str(policy)+ " Failed")
                self.logger.writeLogString('CIGNA-CONTENT','EXCEPTION:'+str(ex))
            finally:
                self.frame.setStatusProgresValueByValue(2)
        
        self.buildHeaderThread.join()
        self.workbook.close()
        self.frame.setStatusLableText("Completed")
        self.logger.writeLogString('AXA-CONTENT','COPMLETED BUILD REPORT OFFLINE MODE')
