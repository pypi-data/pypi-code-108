import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
import xlsxwriter
from ipra.Model.Robot.baseRobot import BaseRobot
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading

class ChinaLifeRobot(BaseRobot):
    def __init__(self, policyList, frame, reportPath,inputPath):
        super().__init__(policyList, frame, reportPath,inputPath)
        self.logger.writeLogString('CHINALIFE-INIT','ROBOT INIT')
        self.maxPolicyListSize = len(policyList)
        self.workbook = xlsxwriter.Workbook(self.reportPath+'CHINALIFE_report.xlsx')
        self.worksheet = self.workbook.add_worksheet()
        self.worksheet.write(0, 0, "Policy No.")
        self.logger.writeLogString('CHINALIFE-INIT','maxPolicyListSize:'+str(self.maxPolicyListSize))

    def waitingLoginComplete(self):
        self.logger.writeLogString('CHINALIFE-LOGIN','START LOGIN')
        self.browser.get("https://onepartner.chinalife.com.hk/#/login")

        while not self.isLogin and not self.isStopped:
            try:
                self.browser.find_element_by_xpath(
                    "/html/body/div/div/div[1]/div[1]/div/ul/li[2]/div/span").click()
                time.sleep(0.5)
                self.browser.find_element_by_xpath(
                    "/html/body/div/div/div[1]/div[1]/div/ul/li[2]/ul/a[1]/li").click()
                time.sleep(0.5)
                self.isLogin = True
            except:
                time.sleep(3)
        else:
            pass

        if self.isLogin:
            self.frame.setStatusLableText("Logged in")
            self.logger.writeLogString('CHINALIFE-LOGIN','LOGIN COMPLETED')

    def scrapPolicy(self):
        for policy in self.policyList:
            if self.isStopped:
                return

            self.frame.setStatusLableText("Processing "+str(policy))
            self.logger.writeLogString('CHINALIFE','PROCESSING:'+str(policy))

            WebDriverWait(self.browser, 60).until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/div/div[2]/div[2]/div[1]/div[2]/div[2]/ul/li[1]/div[1]/input")))
            input_field = self.browser.find_element_by_xpath(
                "/html/body/div/div/div[2]/div[2]/div[1]/div[2]/div[2]/ul/li[1]/div[1]/input")
            input_field.click()
            input_field.clear()
            time.sleep(1)
            input_field.send_keys(str(policy))
            time.sleep(1)
            searchButton = self.browser.find_element_by_xpath("/html/body/div/div/div[2]/div[2]/div[1]/div[2]/div[2]/div/p[2]")
            searchButton.click()
            try:
                WebDriverWait(self.browser, 60).until(
                    EC.presence_of_element_located((By.XPATH, "//span[text()='{0}']".format(str(policy)))))
                input_field = self.browser.find_element_by_xpath(
                    "//span[text()='{0}']".format(str(policy)))
                input_field.click()
                time.sleep(5)
                soup = BeautifulSoup(self.browser.page_source, 'lxml')
                file1 = open(str(self.reportPath+policy)+".txt", "a",
                             encoding="utf-8")  # append mode
                file1.write(soup.prettify())
                file1.close()
            except Exception as e :
                print("Exception: "+str(e))
                print(policy+" is not in this A/C")
                self.frame.setStatusLableText(policy+" is not found")
            finally:
                self.frame.setStatusLableText(policy+" completed")
                self.frame.setStatusProgresValueByValue(1)
                self.buildReportQueue.append(policy)
                self.buildHeaderQueue.append(policy)
                self.browser.back()

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
        self.logger.writeLogString('CHINALIFE-HEADER','START BUILD HEADER FULLFLOW')
        policy_iteration = 0
        while policy_iteration < self.maxPolicyListSize:
            for policy in self.buildHeaderQueue:
                self.logger.writeLogString('CHINALIFE-HEADER','POLICY NO.:{0}'.format(str(policy)))
                if self.isStopped:
                    return
                try:
                    file = open(self.reportPath+policy+".txt",encoding="utf-8")#append mode 
                    #Full Html src
                    soup_all_src = BeautifulSoup(file.read(), 'lxml')
                    file.close()

                    soup_basic = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'basic-msg basic-msg-t')
                    soup_midman = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'midman-msg basic-msg')
                    soup_favman = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'favman-msg basic-msg')
                    soup_protection = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'safe-msg basic-msg')
                    soup_payment_info = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'e-pln basic-msg')
                    soup_acc = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'account_msg basic-msg')
                    #self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'paylist-msg basic-msg')
                    #self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'recvs-msg paylist-msg basic-msg')
                    soup_acc.find('i').decompose()
                    soup_acc.find("div", class_="el-popover el-popper el-popover--plain").decompose()

                    next_idx = 1
                    for strong_tag in soup_basic.find_all('span'):
                        #row_header.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        self.worksheet.write(0,next_idx,strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        next_idx = next_idx + 1
                    for strong_tag in soup_midman.find_all('span'):
                        #row_header.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        self.worksheet.write(0,next_idx,strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        next_idx = next_idx + 1

                    multiple = []
                    for strong_tag in soup_favman.find_all('span'):
                        #row_header.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        multiple.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    else:
                        multiple = multiple[0:2] * 4
                        for header in multiple:
                            self.worksheet.write(0,next_idx,header)
                            next_idx = next_idx + 1
                    multiple=[]

                    for strong_tag in soup_payment_info.find_all('span'):
                        #row_header.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        try:
                            if strong_tag['style'] == 'display: none;':
                                continue
                        except Exception as e:
                            self.worksheet.write(0,next_idx,strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                            next_idx = next_idx + 1
                    for strong_tag in soup_acc.find_all('span'):
                        tempHeader = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
                        if tempHeader != "":
                            self.worksheet.write(0,next_idx,tempHeader)
                            next_idx = next_idx + 1
                        else:
                            continue
                    #for strong_tag in soup_policy.find_all('th'):
                    #    #row_header.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    #    self.worksheet.write(0,next_idx,strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    #    next_idx = next_idx + 1
                    #for strong_tag in soup_payment.find_all('th'):
                    #    #row_header.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    #    self.worksheet.write(0,next_idx,strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    #    next_idx = next_idx + 1
                    #for col_num, data in enumerate(row_header):
                    #    self.worksheet.write(0, col_num+1, data)
                    
                    #No error when building the header,break all loop and then stop this thread
                    policy_iteration = self.maxPolicyListSize + 1
                    self.logger.writeLogString('CHINALIFE-HEADER','BUILD HEADER COMPLETED, BREAK LOOP')
                    break
                except FileNotFoundError:
                    self.logger.writeLogString('CHINALIFE-HEADER','FILE NOT FOUND')
                except Exception as ex:
                    self.logger.writeLogString('CHINALIFE-HEADER','EXCEPTION:'+str(ex))
                finally:
                    policy_iteration = policy_iteration + 1
                    if policy in self.buildHeaderQueue:
                        self.buildHeaderQueue.remove(policy)

    def __buildReportHeaderHalfFlow(self):
        self.logger.writeLogString('CHINALIFE-HEADER','START BUILD HEADER HALFFLOW')
        for policy in self.policyList:
            self.logger.writeLogString('CHINALIFE-HEADER','POLICY NO.:{0}'.format(str(policy)))
            if self.isStopped:
                return
            try:
                file = open(self.inputPath+policy+".txt",encoding="utf-8")#append mode 
                #Full Html src
                soup_all_src = BeautifulSoup(file.read(), 'lxml')
                file.close()

                soup_basic = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'basic-msg basic-msg-t')
                soup_midman = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'midman-msg basic-msg')
                soup_favman = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'favman-msg basic-msg')
                soup_protection = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'safe-msg basic-msg')
                soup_payment_info = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'e-pln basic-msg')
                soup_acc = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'account_msg basic-msg')
                #self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'paylist-msg basic-msg')
                #self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'recvs-msg paylist-msg basic-msg')
                soup_acc.find('i').decompose()
                soup_acc.find("div", class_="el-popover el-popper el-popover--plain").decompose()

                next_idx = 1
                for strong_tag in soup_basic.find_all('span'):
                    #row_header.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    self.worksheet.write(0,next_idx,strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    next_idx = next_idx + 1
                for strong_tag in soup_midman.find_all('span'):
                    #row_header.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    self.worksheet.write(0,next_idx,strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    next_idx = next_idx + 1
                
                multiple = []
                for strong_tag in soup_favman.find_all('span'):
                    #row_header.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    multiple.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))

                else:
                    multiple = multiple[0:2] * 4
                    for header in multiple:
                        self.worksheet.write(0,next_idx,header)
                        next_idx = next_idx + 1
                multiple=[]


                #multiple = []
                for strong_tag in soup_protection.find_all('span'):
                    try:
                        if strong_tag['class'][0] == 'title':
                            self.worksheet.write(0,next_idx,strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                            next_idx = next_idx + 1
                    except Exception as e:
                        pass
                soup_planHeader = soup_protection.find("div", class_="safe-msg-all clearfix")
                for strong_tag in soup_planHeader.find_all('li'):
                        self.worksheet.write(0,next_idx,strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        next_idx = next_idx + 1


                for strong_tag in soup_payment_info.find_all('span'):
                    #row_header.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    try:
                        if strong_tag['style'] == 'display: none;':
                            continue
                    except Exception as e:
                        self.worksheet.write(0,next_idx,strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        next_idx = next_idx + 1
                for strong_tag in soup_acc.find_all('span'):
                    tempHeader = strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' ')
                    if tempHeader != "":
                        self.worksheet.write(0,next_idx,tempHeader)
                        next_idx = next_idx + 1
                    else:
                        continue
                #for strong_tag in soup_policy.find_all('th'):
                #    #row_header.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                #    self.worksheet.write(0,next_idx,strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                #    next_idx = next_idx + 1
                #for strong_tag in soup_payment.find_all('th'):
                #    #row_header.append(strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                #    self.worksheet.write(0,next_idx,strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                #    next_idx = next_idx + 1
                #for col_num, data in enumerate(row_header):
                #    self.worksheet.write(0, col_num+1, data)
                    
                #No error when building the header,break all loop and then stop this thread
                self.logger.writeLogString('CHINALIFE-HEADER','BUILD HEADER COMPLETED, BREAK LOOP')
                break
            except FileNotFoundError as ex:
                self.logger.writeLogString('CHINALIFE-HEADER','FILE NOT FOUND')
            except Exception as ex:
                self.logger.writeLogString('CHINALIFE-HEADER','EXCEPTION:'+str(ex))
            
    def __buildReport(self):
        self.logger.writeLogString('CHINALIFE-CONTENT','START BUILD REPORT')
        policy_iteration = 0
        while policy_iteration < self.maxPolicyListSize:
            for policy in self.buildReportQueue:
                if self.isStopped:
                    return
                self.frame.setStatusLableText("Build Report "+str(policy))
                self.logger.writeLogString('CHINALIFE-CONTENT','POLICY NO.:{0}'.format(str(policy)))
                try:
                    self.worksheet.write(policy_iteration+1, 0, str(policy))
                    file = open(self.reportPath+policy+".txt", encoding="utf-8")  # append mode
                    # Full Html src
                    soup_all_src = BeautifulSoup(file.read(), 'html.parser')
                    file.close()

                    soup_basic = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'basic-msg basic-msg-t')
                    soup_midman = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'midman-msg basic-msg')
                    soup_favman = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'favman-msg basic-msg')
                    soup_protection = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'safe-msg basic-msg')
                    soup_payment_info = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'e-pln basic-msg')
                    soup_acc = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'account_msg basic-msg')
                    #self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'paylist-msg basic-msg')
                    #self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'recvs-msg paylist-msg basic-msg')
                    soup_acc.find('i').decompose()
                    soup_acc.find("div", class_="el-popover el-popper el-popover--plain").decompose()

                    #row_value = []
                    col_num = 0
                    for strong_tag in soup_basic.find_all('b'):
                        self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                        col_num = col_num + 1
                    for strong_tag in soup_midman.find_all('b'):
                        self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                        col_num = col_num + 1

                    multiple = []
                    for strong_tag in soup_favman.find_all('b'):
                        multiple.append(strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                    else:
                        favToAppendSpace = (4 - len(multiple) / 2) * 2
                        for value in multiple:
                            self.worksheet.write(policy_iteration+1, col_num+1,value)
                            col_num = col_num + 1
                        else:
                            for x in range(0,int(favToAppendSpace),1):
                                self.worksheet.write(policy_iteration+1, col_num+1,'')
                                col_num = col_num + 1
                    multiple = []

                    for strong_tag in soup_payment_info.find_all('b'):
                        try:
                            if strong_tag['style'] == 'display: none;':
                                continue
                            else:
                                self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                                col_num = col_num + 1
                        except Exception as e:
                            self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                            col_num = col_num + 1

                    for strong_tag in soup_acc.find_all('b'):
                        self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                        col_num = col_num + 1   

                    #for strong_tag in soup_insured.find_all('td'):
                    #    row_value.append(strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                    #for strong_tag in soup_policy.find_all('td'):
                    #    row_value.append(strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                    #for strong_tag in soup_payment.find_all('td'):
                    #    row_value.append(strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                    #for col_num, data in enumerate(row_value):
                    #    self.worksheet.write(policy_iteration+1, col_num+1, data)

                except FileNotFoundError:
                    self.worksheet.write(policy_iteration+1, 1, str(policy) +
                                    " not found in this A/C, please check other A/C")
                    self.frame.setStatusLableText(
                        "Build Report "+str(policy) + " Not Found")
                    self.logger.writeLogString('CHINALIFE-CONTENT','FILE NOT FOUND')
                except Exception as ex:
                    self.worksheet.write(policy_iteration+1, 1,
                                    "System Error ! Please contact IT Support!")
                    self.frame.setStatusLableText(
                        "Build Report "+str(policy) + " Failed")
                    self.logger.writeLogString('CHINALIFE-CONTENT','EXCEPTION:'+str(ex))
                finally:
                    self.frame.setStatusProgresValueByValue(1)
                    policy_iteration = policy_iteration + 1
                    if policy in self.buildReportQueue:
                        self.buildReportQueue.remove(policy)
                        
        self.buildHeaderThread.join()
        self.workbook.close()
        self.frame.setStatusLableText("Completed")
        self.logger.writeLogString('CHINALIFE-CONTENT','COPMLETED BUILD REPORT')

    def __buildReportOnly(self):
        self.logger.writeLogString('CHINALIFE-CONTENT','START BUILD REPORT OFFLINE MODE')
        for policy_iteration, policy in enumerate(self.policyList):
            if self.isStopped:
                return
            self.frame.setStatusLableText("Build Report "+str(policy))
            self.logger.writeLogString('CHINALIFE-CONTENT','POLICY NO.:{0}'.format(str(policy)))
            try:
                self.worksheet.write(policy_iteration+1, 0, str(policy))
                file = open(self.inputPath+policy+".txt", encoding="utf-8")  # append mode
                # Full Html src
                soup_all_src = BeautifulSoup(file.read(), 'html.parser')
                file.close()

                soup_basic = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'basic-msg basic-msg-t')
                soup_midman = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'midman-msg basic-msg')
                soup_favman = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'favman-msg basic-msg')
                soup_protection = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'safe-msg basic-msg')
                soup_payment_info = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'e-pln basic-msg')
                soup_acc = self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'account_msg basic-msg')
                soup_acc.find('i').decompose()
                soup_acc.find("div", class_="el-popover el-popper el-popover--plain").decompose()

                #self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'paylist-msg basic-msg')
                #self.SearchByHtmlTagValueKey(soup_all_src, 'div', 'class', 'recvs-msg paylist-msg basic-msg')
                
                #row_value = []
                col_num = 0
                for strong_tag in soup_basic.find_all('b'):
                    self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                    col_num = col_num + 1
                for strong_tag in soup_midman.find_all('b'):
                    self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                    col_num = col_num + 1

                multiple = []
                for strong_tag in soup_favman.find_all('b'):
                    multiple.append(strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                else:
                    favToAppendSpace = (4 - len(multiple) / 2) * 2
                    for value in multiple:
                        self.worksheet.write(policy_iteration+1, col_num+1,value)
                        col_num = col_num + 1
                    else:
                        for x in range(0,int(favToAppendSpace),1):
                            self.worksheet.write(policy_iteration+1, col_num+1,'')
                            col_num = col_num + 1
                multiple = []
                
                soup_date = soup_protection.find("div", class_="top-basic-date")
                for strong_tag in soup_date.find_all('span'):
                    try:
                        if strong_tag['class'][0] == 'content':
                            self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                            col_num = col_num + 1
                    except Exception as e:
                        pass

                soup_planValue = soup_protection.find("div", class_="basic_plan")
                soup_planValue.find('ul', style=lambda value: value and 'display: none' in value).decompose()

                for strong_tag in soup_planValue.find_all('li'):
                    self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                    col_num = col_num + 1

                for strong_tag in soup_payment_info.find_all('b'):
                    try:
                        if strong_tag['style'] == 'display: none;':
                            continue
                        else:
                            self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                            col_num = col_num + 1
                    except Exception as e:
                        self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                        col_num = col_num + 1

                for strong_tag in soup_acc.find_all('b'):
                    self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                    col_num = col_num + 1                
                #for strong_tag in soup_insured.find_all('td'):
                #    row_value.append(strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                #for strong_tag in soup_policy.find_all('td'):
                #    row_value.append(strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                #for strong_tag in soup_payment.find_all('td'):
                #    row_value.append(strong_tag.text.strip().replace('\t', '').replace('\n', '').replace(u'\xa0', u' '))
                #for col_num, data in enumerate(row_value):
                #    self.worksheet.write(policy_iteration+1, col_num+1, data)

            except FileNotFoundError:
                self.worksheet.write(policy_iteration+1, 1, str(policy) +
                                " not found in this A/C, please check other A/C")
                self.frame.setStatusLableText(
                    "Build Report "+str(policy) + " Not Found")
                self.logger.writeLogString('CHINALIFE-CONTENT','FILE NOT FOUND')
            except Exception as ex:
                self.worksheet.write(policy_iteration+1, 1,
                                "System Error ! Please contact IT Support!")
                self.frame.setStatusLableText(
                    "Build Report "+str(policy) + " Failed")
                self.logger.writeLogString('CHINALIFE-CONTENT','EXCEPTION:'+str(ex))
            finally:
                self.frame.setStatusProgresValueByValue(2)
                
        self.buildHeaderThread.join()
        self.workbook.close()
        self.frame.setStatusLableText("Copmleted")
        self.logger.writeLogString('CHINALIFE-CONTENT','COPMLETED BUILD REPORT OFFLINE MODE')
